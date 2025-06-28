from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from app.models.transaction import TransactionCreate, TransactionResponse, TransactionType, TransactionCategory, TransactionUpdate
from app.services.supabase_service import SupabaseService
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

app = FastAPI(title="Cash Flow Dashboard with XAI - Supabase Edition")

# Define paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize services
try:
    db = SupabaseService()
    logger.info("✅ Supabase service initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing Supabase service: {str(e)}")
    db = None

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
    transaction_id: str  # UUID string for Supabase
    category: str

class BulkCategoryUpdate(BaseModel):
    updates: List[TransactionCategoryUpdate]

# Demo user ID - in production this would come from authentication
DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

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
    version = datetime.now().strftime("%Y%m%d%H%M%S")
    return templates.TemplateResponse("ai_categorization.html", {"request": request, "version": version})

@app.get("/api/account-summary")
async def get_account_summary():
    """Get account summary from Supabase."""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
            
        # Get account summaries from Supabase
        summaries = await db.get_account_summaries(DEMO_USER_ID)
        
        if not summaries:
            # If no summaries exist, calculate from transactions
            checking_transactions = await db.get_checking_transactions(DEMO_USER_ID)
            credit_transactions = await db.get_credit_transactions(DEMO_USER_ID)
            
            # Calculate checking balance
            checking_balance = sum(
                t['amount'] if t['type'] == 'income' else -t['amount']
                for t in checking_transactions
            )
            
            # Calculate credit balance  
            credit_balance = sum(
                t['amount'] if t['type'] == 'expense' else -t['amount']
                for t in credit_transactions
            )
            
            return {
                "current_balance": checking_balance,
                "available_balance": checking_balance,
                "credit_balance": credit_balance,
                "credit_available": 5000 - credit_balance if credit_balance > 0 else 5000,
                "credit_limit": 5000,
                "pending_transactions": []
            }
        
        # Use existing summaries
        checking_summary = next((s for s in summaries if s['account_type'] == 'checking'), {})
        credit_summary = next((s for s in summaries if s['account_type'] == 'credit'), {})
        
        return {
            "current_balance": checking_summary.get('current_balance', 0),
            "available_balance": checking_summary.get('available_balance', 0),
            "credit_balance": credit_summary.get('current_balance', 0),
            "credit_available": credit_summary.get('available_balance', 0),
            "credit_limit": credit_summary.get('credit_limit', 5000),
            "pending_transactions": []
        }
        
    except Exception as e:
        logger.error(f"Error in account summary endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions")
async def get_transactions(
    account_type: Optional[str] = Query(None),
    month: Optional[str] = Query(None),
    limit: Optional[int] = Query(100),
    offset: Optional[int] = Query(0)
):
    """Get transactions from Supabase with filtering."""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        # Parse month filter
        start_date = None
        end_date = None
        if month:
            try:
                month_date = datetime.strptime(month, "%Y-%m")
                start_date = month_date.replace(day=1).date()
                # Get last day of month
                if month_date.month == 12:
                    end_date = month_date.replace(year=month_date.year + 1, month=1, day=1).date() - timedelta(days=1)
                else:
                    end_date = month_date.replace(month=month_date.month + 1, day=1).date() - timedelta(days=1)
            except ValueError:
                pass
        
        if account_type == "checking":
            transactions = await db.get_checking_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, limit=limit, offset=offset
            )
        elif account_type == "credit":
            transactions = await db.get_credit_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, limit=limit, offset=offset
            )
        else:
            # Get both types
            checking = await db.get_checking_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, limit=limit//2, offset=offset
            )
            credit = await db.get_credit_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, limit=limit//2, offset=offset
            )
            transactions = checking + credit
            # Sort by date descending
            transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Convert to expected format
        response_transactions = []
        for t in transactions:
            response_transactions.append({
                "id": t['id'],
                "date": t['date'],
                "amount": t['amount'],
                "description": t['description'],
                "category": t['category'],
                "type": t['type'],
                "status": t.get('status', 'completed'),
                "account_type": account_type or ('checking' if 'checking' in str(type(t)) else 'credit')
            })
        
        return response_transactions
        
    except Exception as e:
        logger.error(f"Error in get transactions endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get available transaction categories."""
    return [
        "Catering", "Coffee", "Maintenance", "Marketing", "Merchandise", 
        "Misc", "Pastry", "Rent", "Salary", "Sandwich", "Supplies", "Utilities"
    ]

@app.post("/api/categorize-transaction")
async def categorize_transaction(request: CategorizeRequest):
    """Categorize a single transaction using ML."""
    try:
        if not ml_categorizer:
            raise HTTPException(status_code=500, detail="ML categorization service not available")
        
        category, confidence = ml_categorizer.categorize_transaction(request.description)
        
        return {
            "category": category,
            "confidence": float(confidence),
            "description": request.description
        }
    except Exception as e:
        logger.error(f"Error in categorize transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categorize-month")
async def categorize_month(request: Request):
    """Categorize all uncategorized transactions for a specific month using ML."""
    try:
        if not db or not ml_categorizer:
            raise HTTPException(status_code=500, detail="Required services not available")
        
        data = await request.json()
        month = data.get("month")
        
        if not month:
            raise HTTPException(status_code=400, detail="Month is required")
        
        # Parse month
        try:
            month_date = datetime.strptime(month, "%Y-%m")
            start_date = month_date.replace(day=1).date()
            if month_date.month == 12:
                end_date = month_date.replace(year=month_date.year + 1, month=1, day=1).date() - timedelta(days=1)
            else:
                end_date = month_date.replace(month=month_date.month + 1, day=1).date() - timedelta(days=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
        
        # Get transactions for the month
        checking_transactions = await db.get_checking_transactions(
            DEMO_USER_ID, start_date=start_date, end_date=end_date
        )
        credit_transactions = await db.get_credit_transactions(
            DEMO_USER_ID, start_date=start_date, end_date=end_date
        )
        
        all_transactions = checking_transactions + credit_transactions
        
        # Filter uncategorized transactions (misc, empty, or None)
        uncategorized = [
            t for t in all_transactions 
            if not t.get('category') or t.get('category').lower() in ['misc', 'miscellaneous', '']
        ]
        
        categorized_count = 0
        updates = []
        
        # Categorize each transaction
        for transaction in uncategorized:
            try:
                category, confidence = ml_categorizer.categorize_transaction(transaction['description'])
                
                # Only update if confidence is reasonable
                if confidence >= 0.3:
                    updates.append({
                        'id': transaction['id'],
                        'category': category,
                        'confidence': confidence
                    })
                    categorized_count += 1
                    
            except Exception as e:
                logger.error(f"Error categorizing transaction {transaction['id']}: {str(e)}")
                continue
        
        # Update transactions in Supabase
        updated_count = 0
        for update in updates:
            try:
                # Determine if it's checking or credit transaction
                transaction_id = update['id']
                category = update['category']
                
                # Try updating checking transactions first
                success = await db.update_checking_transaction_category(transaction_id, category)
                if not success:
                    # Try credit transactions
                    success = await db.update_credit_transaction_category(transaction_id, category)
                
                if success:
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error updating transaction {update['id']}: {str(e)}")
                continue
        
        return {
            "total_transactions": len(all_transactions),
            "uncategorized_found": len(uncategorized),
            "categorized": categorized_count,
            "updated": updated_count,
            "month": month
        }
        
    except Exception as e:
        logger.error(f"Error in categorize month endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-transaction-categories")
async def update_transaction_categories(request: BulkCategoryUpdate):
    """Update multiple transaction categories."""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        updated_count = 0
        for update in request.updates:
            try:
                # Try updating checking transactions first
                success = await db.update_checking_transaction_category(update.transaction_id, update.category)
                if not success:
                    # Try credit transactions
                    success = await db.update_credit_transaction_category(update.transaction_id, update.category)
                
                if success:
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error updating transaction {update.transaction_id}: {str(e)}")
                continue
        
        return {
            "message": f"Updated {updated_count} out of {len(request.updates)} transactions",
            "updated_count": updated_count,
            "total_count": len(request.updates)
        }
        
    except Exception as e:
        logger.error(f"Error in bulk update endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast")
async def get_forecast(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
):
    """Generate forecast from Supabase transaction data."""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime.now().date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else start + timedelta(days=30)
        
        # Get historical transactions for forecasting
        checking_transactions = await db.get_checking_transactions(DEMO_USER_ID)
        credit_transactions = await db.get_credit_transactions(DEMO_USER_ID)
        
        all_transactions = checking_transactions + credit_transactions
        
        # Filter by category if specified
        if category:
            all_transactions = [t for t in all_transactions if t.get('category') == category]
        
        # Simple forecast - calculate averages from historical data
        df = pd.DataFrame(all_transactions)
        if df.empty:
            return {"labels": [], "income": [], "expenses": [], "net_cash_flow": []}
        
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Calculate daily averages
        daily_income = df[df['type'] == 'income']['amount'].mean() if not df[df['type'] == 'income'].empty else 0
        daily_expenses = df[df['type'] == 'expense']['amount'].mean() if not df[df['type'] == 'expense'].empty else 0
        
        # Generate forecast dates
        forecast_dates = []
        current_date = start
        while current_date <= end:
            forecast_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Simple forecast (could be enhanced with ML)
        income_forecast = [daily_income] * len(forecast_dates)
        expense_forecast = [daily_expenses] * len(forecast_dates)
        net_cash_flow = [daily_income - daily_expenses] * len(forecast_dates)
        
        return {
            "labels": [d.isoformat() for d in forecast_dates],
            "income": income_forecast,
            "expenses": expense_forecast,
            "net_cash_flow": net_cash_flow
        }
        
    except Exception as e:
        logger.error(f"Error in forecast endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights(category: str = None):
    """Get insights from Supabase transaction data."""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        # Get transactions
        checking_transactions = await db.get_checking_transactions(DEMO_USER_ID)
        credit_transactions = await db.get_credit_transactions(DEMO_USER_ID)
        
        all_transactions = checking_transactions + credit_transactions
        
        if category:
            all_transactions = [t for t in all_transactions if t.get('category') == category]
        
        df = pd.DataFrame(all_transactions)
        if df.empty:
            return []
        
        df['amount'] = pd.to_numeric(df['amount'])
        
        insights = []
        
        # Category spending insights
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        top_category = category_totals.index[0] if len(category_totals) > 0 else "Unknown"
        top_amount = category_totals.iloc[0] if len(category_totals) > 0 else 0
        
        insights.append({
            "category": top_category,
            "pattern": f"Highest spending category with ${top_amount:.2f}",
            "recommendation": f"Consider reviewing {top_category} expenses for potential savings",
            "confidence": 0.85
        })
        
        # Income vs expenses insight
        total_income = df[df['type'] == 'income']['amount'].sum()
        total_expenses = df[df['type'] == 'expense']['amount'].sum()
        net_flow = total_income - total_expenses
        
        if net_flow > 0:
            insights.append({
                "category": "Overall",
                "pattern": f"Positive cash flow of ${net_flow:.2f}",
                "recommendation": "Consider investing surplus funds",
                "confidence": 0.90
            })
        else:
            insights.append({
                "category": "Overall", 
                "pattern": f"Negative cash flow of ${abs(net_flow):.2f}",
                "recommendation": "Review expenses to improve cash flow",
                "confidence": 0.90
            })
        
        return insights
        
    except Exception as e:
        logger.error(f"Error in insights endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-data/{data_type}")
async def export_data(data_type: str):
    """Export data from Supabase."""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        if data_type == "transactions":
            checking = await db.get_checking_transactions(DEMO_USER_ID)
            credit = await db.get_credit_transactions(DEMO_USER_ID)
            all_transactions = checking + credit
            
            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(all_transactions)
            csv_path = "data/exported_transactions.csv"
            df.to_csv(csv_path, index=False)
            
            return FileResponse(
                path=csv_path,
                filename="transactions_export.csv",
                media_type="text/csv"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid export type")
            
    except Exception as e:
        logger.error(f"Error in export endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 