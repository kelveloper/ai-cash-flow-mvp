from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from app.models.transaction import TransactionCreate, TransactionResponse, TransactionType, TransactionCategory, TransactionUpdate
from app.utils.data_loader import DataLoader
from app.services.db_service import DatabaseService
from app.services.keyword_categorization import KeywordCategorizationService
from app.models import TransactionStatus
import pandas as pd
import os
import logging
import csv
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from app.services.ml_categorization import MLCategorizationService
import tempfile
import matplotlib.pyplot as plt
from fpdf import FPDF
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cash Flow Dashboard with XAI")

# Define paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize services
data_loader = DataLoader()
db = DatabaseService()
keyword_categorizer = KeywordCategorizationService()

# Initialize ML categorizer with error handling
try:
    ml_categorizer = MLCategorizationService()
    logger.info("[DEBUG] ML Categorization service initialized successfully")
except Exception as e:
    logger.error(f"[DEBUG] Error initializing ML Categorization service: {str(e)}")
    ml_categorizer = None

class CategorizeRequest(BaseModel):
    description: str

class MonthRequest(BaseModel):
    month: str

class TransactionCategoryUpdate(BaseModel):
    transaction_id: int
    category: str

class BulkCategoryUpdate(BaseModel):
    updates: List[TransactionCategoryUpdate]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/checking-transactions", response_class=HTMLResponse)
async def view_checking_transactions(request: Request):
    """Render the checking account transactions page."""
    return templates.TemplateResponse("checking_transactions.html", {"request": request})

@app.get("/transactions", response_class=HTMLResponse)
async def view_transactions(request: Request):
    """Render the transactions page."""
    return templates.TemplateResponse("checking_transactions.html", {"request": request})

@app.get("/credit-transactions", response_class=HTMLResponse)
async def view_credit_transactions(request: Request):
    """Render the credit account transactions page."""
    return templates.TemplateResponse("credit_transactions.html", {"request": request})

@app.get("/ai-categorization", response_class=HTMLResponse)
async def view_ai_categorization(request: Request):
    """Render the AI categorization testing page."""
    return templates.TemplateResponse("ai_categorization.html", {"request": request})

@app.post("/api/switch-data/{filename}")
async def switch_data(filename: str):
    """Switch to a different data file."""
    try:
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(current_dir, "data", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Data file not found: {filename}")
        
        db.import_from_csv(file_path)
        return {"message": f"Successfully switched to {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast")
async def get_forecast(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
):
    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime.now().date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else start + timedelta(days=30)
        
        logger.info(f"Fetching forecast for dates: {start} to {end}, category: {category}")
        
        forecasts = db.get_forecast(start_date=start, end_date=end, category=category)
        logger.info(f"Found {len(forecasts)} forecast records")
        
        response = {
            "labels": [f.date.isoformat() for f in forecasts],
            "income": [f.income for f in forecasts],
            "expenses": [f.expenses for f in forecasts],
            "net_cash_flow": [f.income - f.expenses for f in forecasts]
        }
        logger.info(f"Response data: {response}")
        
        return response
    except Exception as e:
        logger.error(f"Error in forecast endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights(category: str = None):
    """Get XAI insights for the forecast."""
    try:
        insights = db.get_insights(category=category)
        return [
            {
                "category": i.category,
                "pattern": i.pattern,
                "recommendation": i.recommendation,
                "confidence": i.confidence
            }
            for i in insights
        ]
    except Exception as e:
        print(f"Error in insights endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate):
    """Create a new transaction."""
    try:
        # Validate transaction
        if not data_loader.validate_transaction(transaction):
            raise HTTPException(status_code=400, detail="Duplicate transaction detected")
        
        # Save transaction
        data_loader.save_transaction(transaction)
        
        # Create response
        response = TransactionResponse(
            id=len(data_loader.load_transactions()),  # Simple ID generation
            **transaction.dict(),
            created_at=datetime.now()
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account-summary")
async def get_account_summary():
    """Get account summary including current balance, available balance, and pending transactions."""
    try:
        # Get all transactions
        transactions = db.get_transactions()
        
        # Calculate current balance (all posted transactions)
        current_balance = sum(
            t.amount if t.type == TransactionType.INCOME else -t.amount
            for t in transactions
            if t.status == TransactionStatus.POSTED
        )
        
        # Calculate pending transactions
        pending_transactions = [
            t for t in transactions
            if t.status == TransactionStatus.PENDING
        ]
        pending_amount = sum(
            t.amount if t.type == TransactionType.INCOME else -t.amount
            for t in pending_transactions
        )
        
        # Available balance = current balance + pending amount
        available_balance = current_balance + pending_amount
        
        # Get 30-day summary
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_transactions = [
            t for t in transactions
            if t.date >= thirty_days_ago
        ]
        
        # Calculate income and expenses for the last 30 days
        income_30d = sum(
            t.amount for t in recent_transactions
            if t.type == TransactionType.INCOME and t.status == TransactionStatus.POSTED
        )
        expenses_30d = sum(
            t.amount for t in recent_transactions
            if t.type == TransactionType.EXPENSE and t.status == TransactionStatus.POSTED
        )
        
        # Add pending transactions to the 30-day summary
        pending_income_30d = sum(
            t.amount for t in recent_transactions
            if t.type == TransactionType.INCOME and t.status == TransactionStatus.PENDING
        )
        pending_expenses_30d = sum(
            t.amount for t in recent_transactions
            if t.type == TransactionType.EXPENSE and t.status == TransactionStatus.PENDING
        )
        
        return {
            "current_balance": current_balance,
            "available_balance": available_balance,
            "pending_transactions": len(pending_transactions),
            "pending_amount": pending_amount,
            "thirty_day_summary": {
                "income": income_30d,
                "expenses": expenses_30d,
                "net": income_30d - expenses_30d,
                "pending_income": pending_income_30d,
                "pending_expenses": pending_expenses_30d,
                "total_net": (income_30d + pending_income_30d) - (expenses_30d + pending_expenses_30d)
            }
        }
    except Exception as e:
        logger.error(f"Error in account summary endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions")
def get_transactions():
    transactions = []
    file_path = "data/all_transactions_ready.csv"
    try:
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert amount to float, keep other fields as is
                try:
                    row["amount"] = float(row["amount"])
                except ValueError:
                    continue  # Skip this row if amount is invalid
                transactions.append(row)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Transactions file not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading transactions: {str(e)}")
    # Sort transactions by date descending
    transactions.sort(key=lambda x: x["date"], reverse=True)
    return {"transactions": transactions}

@app.get("/api/categories")
async def get_categories():
    """Get list of all transaction categories."""
    try:
        return [
            {
                "name": category.value,
                "type": "income" if category == TransactionCategory.SALARY else "expense"
            }
            for category in TransactionCategory
        ]
    except Exception as e:
        logger.error(f"Error in categories endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-data/{data_type}")
async def export_data(data_type: str):
    try:
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(current_dir, "data", f"export_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        db.export_to_csv(file_path, data_type=data_type)
        return {"message": f"Successfully exported {data_type} data to {file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, update: TransactionUpdate):
    """Update a transaction's category by ID."""
    transaction = db.update_transaction(transaction_id, category=update.category)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.post("/api/categorize-transaction")
async def categorize_transaction(request: CategorizeRequest):
    description = request.description
    try:
        # Get all possible categories from our enum
        categories = [category.value for category in TransactionCategory]
        # Use keyword-based categorization
        result = keyword_categorizer.categorize_transaction(description, categories)
        return result
    except Exception as e:
        logger.error(f"Error in transaction categorization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categorize-month")
async def categorize_month(request: Request):
    try:
        data = await request.json()
        month = data.get('month')
        
        if not month:
            raise HTTPException(status_code=400, detail="Month is required")
            
        # Load transactions from CSV
        try:
            transactions_df = pd.read_csv('data/all_transactions_ready.csv')
            logger.info(f"[DEBUG] Loaded {len(transactions_df)} transactions")
        except FileNotFoundError:
            logger.error("[DEBUG] Transactions file not found")
            raise HTTPException(status_code=500, detail="Transactions file not found")
        except Exception as e:
            logger.error(f"[DEBUG] Error reading transactions file: {str(e)}")
            raise HTTPException(status_code=500, detail="Error reading transactions file")
        
        # Convert date column to datetime
        try:
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        except Exception as e:
            logger.error(f"[DEBUG] Error converting dates: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing transaction dates")
        
        # Filter transactions for the specified month
        try:
            month_start = pd.to_datetime(month + '-01')
            month_end = (month_start + pd.offsets.MonthEnd(0))
            
            # Filter transactions for the current month only
            current_month_transactions = transactions_df[
                (transactions_df['date'] >= month_start) & 
                (transactions_df['date'] <= month_end)
            ]
            
            if current_month_transactions.empty:
                logger.info(f"[DEBUG] No transactions found for month: {month}")
                return []
                
            logger.info(f"[DEBUG] Found {len(current_month_transactions)} transactions for month: {month}")
            
            # Get descriptions and original categories for current month only
            descriptions = current_month_transactions['description'].tolist()
            original_categories = current_month_transactions['category'].tolist()
            
            # Categorize only current month transactions
            results = ml_categorizer.categorize_descriptions(descriptions, original_categories)
            
            # Add transaction details to results and convert numpy types to Python native types
            for i, result in enumerate(results):
                result['description'] = descriptions[i]
                result['original_category'] = original_categories[i]
                result['date'] = current_month_transactions.iloc[i]['date'].strftime('%Y-%m-%d')
                if 'amount' in current_month_transactions.columns:
                    # Convert numpy.float64 to Python float
                    result['amount'] = float(current_month_transactions.iloc[i]['amount'])
                # Convert numpy.int64 to Python int
                result['id'] = int(current_month_transactions.index[i])
                
                # Convert numpy types in top predictions
                if 'top' in result:
                    result['top'] = [(str(cat), float(prob)) for cat, prob in result['top']]
            
            # Filter results to only include transactions where AI suggestion differs from original
            filtered_results = [r for r in results if r['predicted'] != r['original_category']]
            
            if filtered_results:
                logger.info(f"[DEBUG] Categorization complete. First result: {filtered_results[0]}")
            else:
                logger.info("[DEBUG] No category changes suggested")
                
            return filtered_results
            
        except Exception as e:
            logger.error(f"[DEBUG] Error processing transactions: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing transactions: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DEBUG] Error in categorize_month: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-month-pdf")
async def generate_month_pdf(
    month: str = Body(...),
    transactions: Optional[List[Dict[str, Any]]] = Body(None),
    no_changes: Optional[bool] = Body(False)
):
    """Generate a PDF report for the given month with charts and insights. If transactions are provided, use them (with user categories) for the PDF."""
    import matplotlib.pyplot as plt
    import tempfile
    from fpdf import FPDF
    import pandas as pd
    import seaborn as sns
    
    if transactions:
        df_month = pd.DataFrame(transactions)
        if 'category' in df_month:
            df_month['predicted_category'] = df_month['category']
        else:
            df_month['predicted_category'] = 'unknown'
    else:
        df = pd.read_csv("data/all_transactions_ready.csv")
        df_month = df[df['date'].str.startswith(month)]
        descriptions = df_month['description'].astype(str).tolist()
        results = ml_categorizer.categorize_descriptions(descriptions)
        df_month['predicted_category'] = [r['predicted'] for r in results]

    # Create a figure with two subplots
    plt.figure(figsize=(12, 8))
    
    # 1. Category Distribution Pie Chart
    plt.subplot(1, 2, 1)
    cat_counts = df_month['predicted_category'].value_counts()
    plt.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Category Distribution')
    
    # 2. Category Changes Bar Chart
    plt.subplot(1, 2, 2)
    if 'original_category' in df_month.columns:
        changes = df_month[df_month['original_category'] != df_month['predicted_category']]
        if not changes.empty:
            change_counts = changes.groupby(['original_category', 'predicted_category']).size().reset_index(name='count')
            sns.barplot(data=change_counts, x='original_category', y='count', hue='predicted_category')
            plt.title('Category Changes')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
    
    # Save the combined chart
    chart_path = tempfile.mktemp(suffix='.png')
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    plt.close()

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Transaction Report for {month}', ln=True)

    # If no_changes flag is set, add a prominent message
    if no_changes:
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(220, 53, 69)  # Red color for emphasis
        pdf.cell(0, 12, 'No changes were made to any categories.', ln=True)
        pdf.set_text_color(0, 0, 0)  # Reset to black

    # Summary
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Total Transactions: {len(df_month)}', ln=True)
    
    # Add the combined chart
    pdf.image(chart_path, x=10, y=30, w=190)
    pdf.ln(100)  # Move down after the chart
    
    # Category Changes Summary
    if 'original_category' in df_month.columns:
        changes = df_month[df_month['original_category'] != df_month['predicted_category']]
        if not changes.empty:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Category Changes Summary:', ln=True)
            pdf.set_font('Arial', '', 12)
            
            # Group changes by original and new category
            change_groups = changes.groupby(['original_category', 'predicted_category'])
            for (orig, new), group in change_groups:
                pdf.cell(0, 10, f'• {orig} → {new}: {len(group)} transactions', ln=True)
                # Add example transactions
                examples = group.head(3)  # Show up to 3 examples
                for _, tx in examples.iterrows():
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 5, f'  - {tx["description"]}', ln=True)
                pdf.set_font('Arial', '', 12)
    
    # Top Categories
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Top Categories:', ln=True)
    pdf.set_font('Arial', '', 12)
    for cat, count in cat_counts.items():
        pdf.cell(0, 10, f'• {cat}: {count} transactions', ln=True)
    
    # Save PDF
    pdf_path = tempfile.mktemp(suffix='.pdf')
    pdf.output(pdf_path)
    
    return FileResponse(pdf_path, filename=f'{month}_report.pdf', media_type='application/pdf')

@app.post("/api/update-transaction-categories")
async def update_transaction_categories(request: BulkCategoryUpdate):
    """Update multiple transaction categories at once."""
    logger.info(f"[DEBUG] Updating {len(request.updates)} transaction categories")
    try:
        updated_transactions = []
        for update in request.updates:
            transaction = db.update_transaction(update.transaction_id, category=update.category)
            if transaction:
                updated_transactions.append(transaction)
            else:
                logger.warning(f"[DEBUG] Transaction {update.transaction_id} not found")
        
        logger.info(f"[DEBUG] Successfully updated {len(updated_transactions)} transactions")
        return {"message": f"Successfully updated {len(updated_transactions)} transactions", "updated": updated_transactions}
    except Exception as e:
        logger.error(f"[DEBUG] Error updating transaction categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 