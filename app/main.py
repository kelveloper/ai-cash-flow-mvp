from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from app.models.transaction import TransactionCreate, TransactionResponse, TransactionType, TransactionCategory, TransactionUpdate
from app.utils.data_loader import DataLoader
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
from app.services.enhanced_categorization import EnhancedCategorizationService
from app.services.categorization_analytics import analytics
import tempfile
import matplotlib.pyplot as plt
from fpdf import FPDF
import seaborn as sns
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cash Flow Dashboard with XAI")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

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
try:
    db = SupabaseService()
    logger.info("✅ Supabase service initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing Supabase service: {str(e)}")
    # Fallback to None - we'll handle this in endpoints
    db = None
keyword_categorizer = KeywordCategorizationService()

# Demo user ID for Supabase
DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

# Initialize ML categorizer with error handling
try:
    ml_categorizer = MLCategorizationService()
    logger.info("[DEBUG] ML Categorization service initialized successfully")
except Exception as e:
    logger.error(f"[DEBUG] Error initializing ML Categorization service: {str(e)}")
    ml_categorizer = None

# Initialize Enhanced categorizer with error handling
try:
    enhanced_categorizer = EnhancedCategorizationService()
    logger.info("[DEBUG] Enhanced Categorization service initialized successfully")
except Exception as e:
    logger.error(f"[DEBUG] Error initializing Enhanced Categorization service: {str(e)}")
    enhanced_categorizer = None

# Global in-memory storage for temporary AI categorization changes
# This will reset when the app restarts, making all changes temporary
temporary_categorizations = {}  # Format: {transaction_id: new_category}

def apply_temporary_categorizations(transactions):
    """Apply temporary categorizations to transaction data"""
    global temporary_categorizations
    
    if not temporary_categorizations:
        return transactions
    
    # Apply temporary categorizations
    for transaction in transactions:
        transaction_id = transaction.get('id')
        if transaction_id in temporary_categorizations:
            original_category = transaction.get('category')
            new_category = temporary_categorizations[transaction_id]
            transaction['category'] = new_category
            print(f"[TEMP] Applied temporary categorization: {transaction_id} {original_category} -> {new_category}")
    
    return transactions

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
    version = datetime.now().strftime("%Y%m%d%H%M%S")
    return templates.TemplateResponse("ai_categorization.html", {"request": request, "version": version})

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
    """Get account summary from Supabase."""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
            
        # Get account summaries from Supabase
        summaries = await db.get_account_summaries(DEMO_USER_ID)
        
        if summaries:
            # Use existing summaries
            checking_summary = next((s for s in summaries if s['account_type'] == 'checking'), {})
            credit_summary = next((s for s in summaries if s['account_type'] == 'credit'), {})
            
            return {
                "current_balance": checking_summary.get('current_balance', 0),
                "available_balance": checking_summary.get('available_balance', 0),
                "credit_balance": credit_summary.get('current_balance', 0),
                "credit_available": credit_summary.get('available_balance', 0),
                "credit_limit": credit_summary.get('credit_limit', 5000),
                "pending_transactions": 0,
                "pending_amount": 0
            }
        else:
            # Calculate from transactions if no summaries exist
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
                "pending_transactions": 0,
                "pending_amount": 0
            }
        
    except Exception as e:
        logger.error(f"Error in account summary endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions")
async def get_transactions(
    account_type: Optional[str] = Query(None),
    month: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    minAmount: Optional[float] = Query(None),
    maxAmount: Optional[float] = Query(None),
    limit: Optional[int] = Query(100),  # Default limit to improve performance
    offset: Optional[int] = Query(0)
):
    """Get transactions from Supabase with filtering - optimized for performance."""
    try:
        print(f"[TRANSACTIONS] Starting request: account_type={account_type}, month={month}, limit={limit}")
        
        if not db:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        # Parse date filters - prioritize custom date range over month
        start_date = None
        end_date = None
        
        if date and ',' in date:
            # Custom date range format: "YYYY-MM-DD,YYYY-MM-DD"
            try:
                date_parts = date.split(',')
                if len(date_parts) == 2:
                    start_date = datetime.strptime(date_parts[0].strip(), "%Y-%m-%d").date()
                    end_date = datetime.strptime(date_parts[1].strip(), "%Y-%m-%d").date()
                    print(f"[TRANSACTIONS] Custom date range: {start_date} to {end_date}")
            except ValueError:
                pass
        elif month:
            # Month filter format: "YYYY-MM"
            try:
                month_date = datetime.strptime(month, "%Y-%m")
                start_date = month_date.replace(day=1).date()
                # Get last day of month
                if month_date.month == 12:
                    end_date = month_date.replace(year=month_date.year + 1, month=1, day=1).date() - timedelta(days=1)
                else:
                    end_date = month_date.replace(month=month_date.month + 1, day=1).date() - timedelta(days=1)
                print(f"[TRANSACTIONS] Month filter: {start_date} to {end_date}")
            except ValueError:
                pass
        
        # Apply reasonable limits to prevent timeouts
        # For month/date queries, allow unlimited transactions; otherwise use provided limit
        if month or date:
            effective_limit = None  # No limit for month/date queries - show all transactions
        else:
            effective_limit = limit or 100  # Default 100 for general queries
            
        print(f"[TRANSACTIONS] Using effective_limit: {effective_limit or 'unlimited'}")
        
        transactions = []
        
        if account_type == "checking":
            print(f"[TRANSACTIONS] Fetching checking transactions...")
            transactions = await db.get_checking_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, 
                category=category, search=search, limit=effective_limit, offset=offset
            )
            # Add account_type field
            for t in transactions:
                t['account_type'] = 'checking'
                
        elif account_type == "credit":
            print(f"[TRANSACTIONS] Fetching credit transactions...")
            transactions = await db.get_credit_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, 
                category=category, search=search, limit=effective_limit, offset=offset
            )
            # Add account_type field
            for t in transactions:
                t['account_type'] = 'credit'
                
        else:
            # Get both types but handle unlimited properly
            if effective_limit is None:
                # No limit - get all transactions
                checking_limit = None
                credit_limit = None
            else:
                # Split the limit between account types
                checking_limit = effective_limit // 2
                credit_limit = effective_limit // 2
            
            print(f"[TRANSACTIONS] Fetching both account types (checking: {checking_limit or 'unlimited'}, credit: {credit_limit or 'unlimited'})...")
            
            checking = await db.get_checking_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, 
                category=category, search=search, limit=checking_limit, offset=offset
            )
            credit = await db.get_credit_transactions(
                DEMO_USER_ID, start_date=start_date, end_date=end_date, 
                category=category, search=search, limit=credit_limit, offset=offset
            )
            
            # Add account_type field to distinguish them
            for t in checking:
                t['account_type'] = 'checking'
            for t in credit:
                t['account_type'] = 'credit'
                
            transactions = checking + credit
            # Sort by date descending
            transactions.sort(key=lambda x: x['date'], reverse=True)
            
            # Apply final limit after combining (only if we have a limit)
            if effective_limit is not None and len(transactions) > effective_limit:
                transactions = transactions[:effective_limit]
        
        print(f"[TRANSACTIONS] Retrieved {len(transactions)} transactions")
        
        # Convert to expected format and apply amount filtering (optimized)
        response_transactions = []
        for t in transactions:
            # Apply amount filtering first (before creating dict - faster)
            amount = abs(t['amount'])  # Use absolute value for amount filtering
            if minAmount is not None and amount < minAmount:
                continue
            if maxAmount is not None and amount > maxAmount:
                continue
            
            transaction_data = {
                "id": t['id'],
                "date": t['date'],
                "amount": t['amount'],
                "description": t['description'],
                "category": t['category'],
                "type": t['type'],
                "status": t.get('status', 'completed'),
                "account_type": t.get('account_type', account_type or 'unknown')
            }
                
            response_transactions.append(transaction_data)
        
        # Apply temporary categorizations before returning
        response_transactions = apply_temporary_categorizations(response_transactions)
        
        print(f"[TRANSACTIONS] Returning {len(response_transactions)} transactions after filtering")
        return {"transactions": response_transactions}
        
    except Exception as e:
        print(f"[TRANSACTIONS] Error: {str(e)}")
        logger.error(f"Error in get transactions endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.put("/api/transactions/{transaction_id}")
async def update_transaction(transaction_id: int, update: Dict[str, Any]):
    """Update a transaction's category temporarily (in-memory only - resets on app restart)."""
    global temporary_categorizations
    
    try:
        # Get the new category from the update (only category updates supported for temporary edits)
        new_category = update.get('category')
        if not new_category:
            raise HTTPException(status_code=400, detail="Category is required")
        
        # Store the temporary categorization
        temporary_categorizations[transaction_id] = new_category
        
        print(f"[TEMP] Manual edit: Transaction {transaction_id} category -> {new_category}")
        print(f"[TEMP] Total temporary categorizations: {len(temporary_categorizations)}")
        
        # Return success response
        return {
            "id": transaction_id,
            "category": new_category,
            "message": "Category updated temporarily (will reset on app restart)",
            "temporary": True
        }
        
    except Exception as e:
        logger.error(f"Error updating transaction category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/api/categorize-transaction-enhanced")
async def categorize_transaction_enhanced(request: CategorizeRequest):
    """Enhanced categorization using external APIs with fallback to local ML"""
    description = request.description
    try:
        if not enhanced_categorizer:
            # Fallback to regular categorization if enhanced service not available
            logger.warning("Enhanced categorizer not available, falling back to keyword categorization")
            categories = [category.value for category in TransactionCategory]
            result = keyword_categorizer.categorize_transaction(description, categories)
            result['source'] = 'keyword_fallback'
            return result
        
        # Use the enhanced categorization service
        result = enhanced_categorizer.categorize_transaction_enhanced(description)
        
        # Add demo data if we're using fallback methods
        if result.get('source') == 'local_ml':
            result['demo_note'] = "Using local ML model - would be much more accurate with API keys configured"
        elif result.get('source') == 'fallback':
            result['demo_note'] = "Using keyword fallback - configure API keys for best results"
        elif result.get('source') == 'genify_api':
            result['demo_note'] = "Using Genify API - premium accuracy with merchant enrichment"
            
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced transaction categorization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categorize-month")
async def categorize_month(request: Request):
    """Categorize all uncategorized transactions for a specific month using ML."""
    try:
        if not db or not ml_categorizer:
            raise HTTPException(status_code=500, detail="Required services not available")
        
        data = await request.json()
        month = data.get("month")
        
        print(f"🔍 [DEBUG] Starting categorization for month: {month}")
        
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
        
        print(f"🔍 [DEBUG] Date range: {start_date} to {end_date}")
        
        # Get transactions for the month
        checking_transactions = await db.get_checking_transactions(
            DEMO_USER_ID, start_date=start_date, end_date=end_date
        )
        credit_transactions = await db.get_credit_transactions(
            DEMO_USER_ID, start_date=start_date, end_date=end_date
        )
        
        all_transactions = checking_transactions + credit_transactions
        print(f"🔍 [DEBUG] Total transactions found: {len(all_transactions)}")
        print(f"🔍 [DEBUG] Checking: {len(checking_transactions)}, Credit: {len(credit_transactions)}")
        
        # Filter uncategorized transactions (misc, empty, or None)
        uncategorized = [
            t for t in all_transactions 
            if not t.get('category') or t.get('category').lower() in ['misc', 'miscellaneous', '']
        ]
        
        print(f"🔍 [DEBUG] Uncategorized transactions found: {len(uncategorized)}")
        
        # Show first few uncategorized examples
        if uncategorized:
            print("🔍 [DEBUG] First 5 uncategorized transactions:")
            for i, t in enumerate(uncategorized[:5]):
                print(f"  {i+1}. ID: {t.get('id')}, Category: '{t.get('category')}', Description: '{t.get('description')[:50]}...'")
        
        categorized_count = 0
        updates = []
        
        # Categorize transactions using the ML service
        if uncategorized:
            descriptions = [t['description'] for t in uncategorized]
            print(f"🔍 [DEBUG] Sending {len(descriptions)} descriptions to ML categorizer")
            
            try:
                results = ml_categorizer.categorize_descriptions(descriptions)
                print(f"🔍 [DEBUG] ML categorizer returned {len(results)} results")
                
                # Show first few predictions
                print("🔍 [DEBUG] First 5 ML predictions:")
                for i, result in enumerate(results[:5]):
                    print(f"  {i+1}. Predicted: '{result.get('predicted')}', Confidence: {result.get('confidence'):.3f}")
                
                for i, result in enumerate(results):
                    predicted_category = result.get('predicted')
                    confidence = result.get('confidence', 0)
                    
                    print(f"🔍 [DEBUG] Transaction {i+1}: '{uncategorized[i]['description'][:30]}' -> '{predicted_category}' (confidence: {confidence:.3f})")
                    
                    if predicted_category and confidence >= 0.3:
                        updates.append({
                            'id': uncategorized[i]['id'],
                            'category': predicted_category,
                            'confidence': confidence,
                            'original_category': uncategorized[i].get('category', 'Misc')
                        })
                        categorized_count += 1
                        print(f"✅ [DEBUG] Added to updates: {predicted_category}")
                    else:
                        print(f"❌ [DEBUG] Skipped - low confidence or no prediction")
                        
            except Exception as e:
                logger.error(f"Error categorizing transactions: {str(e)}")
                print(f"🔍 [DEBUG] ML categorization error: {str(e)}")
                return {
                    "total_transactions": len(all_transactions),
                    "uncategorized_found": len(uncategorized),
                    "categorized_count": 0,
                    "updated_count": 0,
                    "month": month,
                    "error": f"ML categorization failed: {str(e)}"
                }
        
        print(f"🔍 [DEBUG] Final results: {categorized_count} transactions categorized with {len(updates)} updates")
        
        # Return categorization suggestions without updating database
        # This allows for temporary/preview categorization
        return {
            "total_transactions": len(all_transactions),
            "uncategorized_found": len(uncategorized),
            "categorized_count": categorized_count,
            "suggestions": updates,  # Return the suggested categorizations
            "month": month,
            "message": "Categorization suggestions generated (not applied to database)"
        }
        
    except Exception as e:
        logger.error(f"Error in categorize month endpoint: {str(e)}")
        print(f"🔍 [DEBUG] Endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/apply-categorizations")
async def apply_categorizations(request: Request):
    """Apply categorization suggestions temporarily (in-memory only - resets on app restart)."""
    try:
        global temporary_categorizations
        
        data = await request.json()
        suggestions = data.get("suggestions", [])
        
        if not suggestions:
            raise HTTPException(status_code=400, detail="No suggestions provided")
        
        updated_count = 0
        
        # Store changes in memory instead of database
        for suggestion in suggestions:
            try:
                transaction_id = suggestion['id']
                category = suggestion['category']
                
                # Store the temporary categorization
                temporary_categorizations[transaction_id] = category
                updated_count += 1
                
                print(f"[TEMP] Stored temporary categorization: {transaction_id} -> {category}")
                    
            except Exception as e:
                error_msg = f"Error storing temporary categorization {suggestion['id']}: {str(e)}"
                logger.error(error_msg)
        
        print(f"[TEMP] Total temporary categorizations stored: {len(temporary_categorizations)}")
        
        return {
            "total_suggestions": len(suggestions),
            "updated_count": updated_count,
            "errors": [],
            "message": f"Applied {updated_count} categorizations temporarily (will reset on app restart)"
        }
        
    except Exception as e:
        logger.error(f"Error in apply categorizations endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-temporary-categorizations")
async def clear_temporary_categorizations():
    """Clear all temporary categorizations (reset to database state)"""
    global temporary_categorizations
    
    count = len(temporary_categorizations)
    temporary_categorizations.clear()
    
    print(f"[TEMP] Cleared {count} temporary categorizations")
    
    return {
        "cleared_count": count,
        "message": f"Cleared {count} temporary categorizations. Data reset to database state."
    }

@app.get("/api/temporary-categorizations-status")
async def get_temporary_categorizations_status():
    """Get status of temporary categorizations with detailed transaction information"""
    global temporary_categorizations
    
    if not temporary_categorizations:
        return {
            "active_count": 0,
            "temporary_categorizations": {},
            "detailed_changes": [],
            "message": "No temporary categorizations active."
        }
    
    # Get detailed information for each temporary categorization
    detailed_changes = []
    try:
        # Get all transactions that have temporary changes
        for transaction_id, new_category in temporary_categorizations.items():
            # Try to find the transaction in both checking and credit tables
            transaction_found = False
            
            # Check checking transactions first
            try:
                checking_transactions = await db.get_checking_transactions(
                    DEMO_USER_ID, 
                    limit=None  # Get all to find the specific transaction
                )
                for tx in checking_transactions:
                    if tx.get('id') == transaction_id:
                        detailed_changes.append({
                            "transaction_id": transaction_id,
                            "description": tx.get('description', ''),
                            "amount": tx.get('amount', 0),
                            "date": tx.get('date', ''),
                            "account_type": "checking",
                            "original_category": tx.get('category', 'uncategorized'),
                            "new_category": new_category
                        })
                        transaction_found = True
                        break
            except Exception as e:
                logger.error(f"Error fetching checking transaction {transaction_id}: {e}")
            
            # If not found in checking, try credit
            if not transaction_found:
                try:
                    credit_transactions = await db.get_credit_transactions(
                        DEMO_USER_ID,
                        limit=None  # Get all to find the specific transaction
                    )
                    for tx in credit_transactions:
                        if tx.get('id') == transaction_id:
                            detailed_changes.append({
                                "transaction_id": transaction_id,
                                "description": tx.get('description', ''),
                                "amount": tx.get('amount', 0),
                                "date": tx.get('date', ''),
                                "account_type": "credit",
                                "original_category": tx.get('category', 'uncategorized'),
                                "new_category": new_category
                            })
                            transaction_found = True
                            break
                except Exception as e:
                    logger.error(f"Error fetching credit transaction {transaction_id}: {e}")
            
            # If still not found, add basic info
            if not transaction_found:
                detailed_changes.append({
                    "transaction_id": transaction_id,
                    "description": "Transaction not found",
                    "amount": 0,
                    "date": "",
                    "account_type": "unknown",
                    "original_category": "unknown",
                    "new_category": new_category
                })
                
    except Exception as e:
        logger.error(f"Error getting detailed changes: {e}")
    
    return {
        "active_count": len(temporary_categorizations),
        "temporary_categorizations": temporary_categorizations,
        "detailed_changes": detailed_changes,
        "message": f"Currently {len(temporary_categorizations)} temporary categorizations active. These will reset when the app restarts."
    }

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
                pdf.cell(0, 10, f'- {orig} -> {new}: {len(group)} transactions', ln=True)
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
                    pdf.cell(0, 10, f'- {cat}: {count} transactions', ln=True)
    
    # Save PDF
    pdf_path = tempfile.mktemp(suffix='.pdf')
    pdf.output(pdf_path)
    
    return FileResponse(pdf_path, filename=f'{month}_report.pdf', media_type='application/pdf')

@app.post("/api/generate-categorization-pdf")
async def generate_categorization_pdf(request: Request):
    """Fast PDF generation with essential categorization insights."""
    try:
        data = await request.json()
        month = data.get("month")
        account_type = data.get("accountType", "all")
        with_changes = data.get("withChanges", False)
        categorize_result = data.get("categorizeResult")
        current_transactions = data.get("currentTransactions", [])
        
        print(f"[PDF] Generating PDF for month={month}, account_type={account_type}, with_changes={with_changes}")
        
        if not month:
            raise HTTPException(status_code=400, detail="Month is required")
            
        # Parse month for date range
        month_date = datetime.strptime(month, "%Y-%m")
        start_date = month_date.replace(day=1).date()
        if month_date.month == 12:
            end_date = month_date.replace(year=month_date.year + 1, month=1, day=1).date() - timedelta(days=1)
        else:
            end_date = month_date.replace(month=month_date.month + 1, day=1).date() - timedelta(days=1)
        
        print(f"[PDF] Date range: {start_date} to {end_date}")
        
        # Get transactions from database if not provided - ENSURE MONTH FILTERING
        if not current_transactions:
            print(f"[PDF] Fetching transactions from database...")
            if account_type == "checking":
                current_transactions = await db.get_checking_transactions(DEMO_USER_ID, start_date=start_date, end_date=end_date)
            elif account_type == "credit":
                current_transactions = await db.get_credit_transactions(DEMO_USER_ID, start_date=start_date, end_date=end_date)
            else:
                checking_transactions = await db.get_checking_transactions(DEMO_USER_ID, start_date=start_date, end_date=end_date)
                credit_transactions = await db.get_credit_transactions(DEMO_USER_ID, start_date=start_date, end_date=end_date)
                current_transactions = checking_transactions + credit_transactions
        
        print(f"[PDF] Processing {len(current_transactions)} transactions")
        
        # Apply temporary categorizations to the fetched data
        current_transactions = apply_temporary_categorizations(current_transactions)
        
        # Convert to DataFrame and ensure month filtering
        import pandas as pd
        df = pd.DataFrame(current_transactions)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transactions found for the specified period")
        
        # CRITICAL: Double-check month filtering
        if 'date' in df.columns:
            df['date_parsed'] = pd.to_datetime(df['date'])
            # Filter to ensure only transactions from the specified month
            df = df[(df['date_parsed'].dt.date >= start_date) & (df['date_parsed'].dt.date <= end_date)]
            print(f"[PDF] After date filtering: {len(df)} transactions")
        
        # Quick analysis (no complex visualizations)
        category_counts = df['category'].fillna('uncategorized').value_counts()
        total_transactions = len(df)
        total_amount = df['amount'].abs().sum() if 'amount' in df.columns else 0
        avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
        top_category = category_counts.index[0] if len(category_counts) > 0 else 'Unknown'
        
        # Calculate uncategorized count using same logic as AI categorization
        # Count transactions that would be processed by AI categorization
        uncategorized_count = 0
        for _, row in df.iterrows():
            category = row.get('category')
            if not category or str(category).lower() in ['misc', 'miscellaneous', 'uncategorized', '']:
                uncategorized_count += 1
        
        print(f"[PDF] Analysis complete: {total_transactions} transactions, ${total_amount:.2f} total")
        print(f"[PDF] Uncategorized transactions (AI-categorizable): {uncategorized_count}")
        
        # If this is a preview (no changes applied), run AI categorization to get potential changes
        potential_categorizations = 0
        if not with_changes and uncategorized_count > 0:
            try:
                print(f"[PDF] Running AI categorization preview to get potential changes...")
                
                # Get uncategorized transactions
                uncategorized_transactions = []
                for _, row in df.iterrows():
                    category = row.get('category')
                    if not category or str(category).lower() in ['misc', 'miscellaneous', 'uncategorized', '']:
                        uncategorized_transactions.append(row.to_dict())
                
                if uncategorized_transactions and ml_categorizer:
                    descriptions = [t['description'] for t in uncategorized_transactions]
                    results = ml_categorizer.categorize_descriptions(descriptions)
                    
                    # Count how many would actually be categorized (confidence >= 0.3)
                    for result in results:
                        confidence = result.get('confidence', 0)
                        predicted_category = result.get('predicted')
                        if predicted_category and confidence >= 0.3:
                            potential_categorizations += 1
                    
                    print(f"[PDF] AI would categorize {potential_categorizations} out of {uncategorized_count} uncategorized transactions")
                    
            except Exception as e:
                print(f"[PDF] Error running AI categorization preview: {e}")
        
        # Generate simple PDF with FPDF only (no matplotlib to save time)
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title and Header
        pdf.set_font('Arial', 'B', 18)
        formatted_month = month_date.strftime('%B %Y')
        pdf.cell(0, 12, f'Transaction Categorization Report', ln=True, align='C')

        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 8, f'{formatted_month} - {account_type.capitalize()} Account', ln=True, align='C')
        
        pdf.ln(5)
        
        # Status Banner
        if with_changes:
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(0, 150, 0)  # Green
            pdf.cell(0, 8, 'AI CATEGORIZATION APPLIED', ln=True, align='C')
            pdf.set_text_color(0, 0, 0)  # Reset to black
        else:
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(0, 100, 200)  # Blue
            pdf.cell(0, 8, 'CURRENT CATEGORIZATION ANALYSIS', ln=True, align='C')
            pdf.set_text_color(0, 0, 0)  # Reset to black
        
        pdf.ln(10)
        
        # Generate category distribution chart
        import matplotlib.pyplot as plt
        import tempfile
        import os
        
        # If AI categorization has been applied, update the DataFrame with new categories
        chart_df = df.copy()
        if with_changes and categorize_result and categorize_result.get('suggestions'):
            print(f"[PDF] Applying AI categorization changes to chart data...")
            suggestions = categorize_result['suggestions']
            
            # Create a mapping of transaction IDs to new categories
            id_to_new_category = {}
            for suggestion in suggestions:
                id_to_new_category[suggestion['id']] = suggestion['category']
            
            # Apply the new categories to the chart DataFrame
            for index, row in chart_df.iterrows():
                transaction_id = row.get('id')
                if transaction_id in id_to_new_category:
                    chart_df.loc[index, 'category'] = id_to_new_category[transaction_id]
            
            print(f"[PDF] Applied {len(id_to_new_category)} category changes to chart data")
        
        # Generate category counts for the chart (using updated data if changes were applied)
        chart_category_counts = chart_df['category'].fillna('uncategorized').value_counts()
        
        # If we have AI categorization changes, prioritize showing those categories
        if with_changes and categorize_result and categorize_result.get('suggestions'):
            # Get categories that were changed by AI
            changed_categories = set()
            for suggestion in categorize_result['suggestions']:
                changed_categories.add(suggestion.get('category', 'Unknown'))
                changed_categories.add(suggestion.get('original_category', 'Uncategorized'))
            
            # Ensure changed categories are in the chart
            priority_categories = []
            remaining_categories = []
            
            for category, count in chart_category_counts.items():
                if category in changed_categories:
                    priority_categories.append((category, count))
                else:
                    remaining_categories.append((category, count))
            
            # Combine priority categories with top remaining categories
            chart_items = priority_categories + remaining_categories
            # Show more categories when we have changes to display
            chart_data = pd.Series(dict(chart_items[:12]))  # Show up to 12 categories
        else:
            # For "before" charts, show top 10 categories without "Other"
            chart_data = chart_category_counts.head(10)
        
        # Create the chart
        plt.figure(figsize=(10, 8))  # Larger size to accommodate more categories
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD', 
                 '#FF8C42', '#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#E17055', '#74B9FF', '#00B894']
        wedges, texts, autotexts = plt.pie(chart_data.values, labels=chart_data.index, autopct='%1.1f%%', 
                                          colors=colors[:len(chart_data)], startangle=90)
        
        # Improve text formatting
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        for text in texts:
            text.set_fontsize(9)
        
        # Update chart title to reflect if changes were applied
        chart_title = f'Category Distribution - {formatted_month}'
        if with_changes:
            chart_title += ' (After AI Categorization)'
        else:
            chart_title += ' (Current State)'
            
        plt.title(chart_title, fontsize=14, fontweight='bold', pad=20)
        plt.axis('equal')
        
        # Save chart as image
        chart_path = tempfile.mktemp(suffix='.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Add chart to PDF
        pdf.set_font('Arial', 'B', 14)
        if with_changes:
            pdf.cell(0, 8, 'Updated Category Distribution Chart', ln=True)
        else:
            pdf.cell(0, 8, 'Category Distribution Chart', ln=True)
        pdf.ln(5)
        
        # Insert the chart image
        try:
            pdf.image(chart_path, x=15, y=pdf.get_y(), w=180)
            pdf.ln(120)  # Move down past the chart
        except Exception as chart_error:
            print(f"[PDF] Error adding chart: {chart_error}")
            pdf.cell(0, 8, 'Chart generation failed - see category breakdown below', ln=True)
            pdf.ln(10)
        finally:
            # Clean up the temporary chart file
            try:
                os.unlink(chart_path)
            except:
                pass
        
        # Quick Summary Box
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Summary', ln=True)
        pdf.set_font('Arial', '', 11)
        
        # Use updated category counts if changes were applied, otherwise use original
        summary_category_counts = chart_category_counts if with_changes and categorize_result else category_counts
        summary_top_category = summary_category_counts.index[0] if len(summary_category_counts) > 0 else 'Unknown'
        
        pdf.cell(0, 6, f'Total Transactions: {total_transactions:,}', ln=True)
        pdf.cell(0, 6, f'Total Amount: ${total_amount:,.2f}', ln=True)
        pdf.cell(0, 6, f'Average per Transaction: ${avg_transaction:.2f}', ln=True)
        pdf.cell(0, 6, f'Top Category: {summary_top_category} ({summary_category_counts.iloc[0]} transactions)', ln=True)
        
        # Show different information based on whether changes were applied
        if with_changes and categorize_result:
            categorized_count = categorize_result.get('categorized_count', 0)
            pdf.cell(0, 6, f'Already categorized: {total_transactions - uncategorized_count} transactions', ln=True)
            pdf.cell(0, 6, f'AI Categorized: {categorized_count} transactions', ln=True)
        else:
            # Show current state and potential for AI categorization
            pdf.cell(0, 6, f'Already categorized: {total_transactions - uncategorized_count} transactions', ln=True)
            if potential_categorizations > 0:
                pdf.cell(0, 6, f'Can be AI categorized: {potential_categorizations} transactions', ln=True)
                remaining_uncategorized = uncategorized_count - potential_categorizations
                if remaining_uncategorized > 0:
                    pdf.cell(0, 6, f'Will remain uncategorized: {remaining_uncategorized} transactions', ln=True)
            else:
                pdf.cell(0, 6, f'Uncategorized: {uncategorized_count} transactions', ln=True)
        
        pdf.ln(10)
        
        # Category Breakdown
        pdf.set_font('Arial', 'B', 14)
        if with_changes:
            pdf.cell(0, 8, 'Updated Category Breakdown', ln=True)
        else:
            pdf.cell(0, 8, 'Category Breakdown', ln=True)
        pdf.ln(3)
        
        pdf.set_font('Arial', '', 10)
        # Use updated category counts for breakdown as well
        breakdown_category_counts = summary_category_counts
        breakdown_df = chart_df if with_changes and categorize_result else df
        
        for i, (category, count) in enumerate(breakdown_category_counts.head(10).items()):  # Top 10 only
            percentage = (count / total_transactions) * 100
            amount_for_cat = breakdown_df[breakdown_df['category'].fillna('uncategorized') == category]['amount'].abs().sum() if 'amount' in breakdown_df.columns else 0
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, f'{i+1}. {category.upper()}', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f'   Transactions: {count} ({percentage:.1f}%)', ln=True)
            if 'amount' in breakdown_df.columns:
                pdf.cell(0, 5, f'   Total Amount: ${amount_for_cat:,.2f}', ln=True)
            pdf.ln(2)
        
        # Changes Applied (if applicable) - detailed breakdown
        if with_changes and categorize_result and categorize_result.get('suggestions'):
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'AI CATEGORIZATION CHANGES APPLIED', ln=True, align='C')
            pdf.ln(5)
            
            suggestions = categorize_result['suggestions']
            changes_summary = {}
            
            # Group changes by type
            for suggestion in suggestions:
                orig_cat = suggestion.get('original_category', 'Uncategorized')
                new_cat = suggestion.get('category', 'Unknown')
                key = f"{orig_cat} -> {new_cat}"
                if key not in changes_summary:
                    changes_summary[key] = []
                changes_summary[key].append(suggestion)
            
            # Summary of changes
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 8, f'SUMMARY: {len(suggestions)} transactions categorized', ln=True)
            pdf.ln(3)
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 6, 'Changes by Category Type:', ln=True)
            pdf.set_font('Arial', '', 11)
            
            for change_type, change_list in sorted(changes_summary.items(), key=lambda x: len(x[1]), reverse=True):
                count = len(change_list)
                pdf.cell(0, 6, f'- {change_type}: {count} transaction{"s" if count != 1 else ""}', ln=True)
            
            pdf.ln(8)
            
            # Detailed changes section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 8, 'DETAILED CHANGES', ln=True)
            pdf.ln(5)
            
            # Show each change type with transaction details
            for change_type, change_list in sorted(changes_summary.items(), key=lambda x: len(x[1]), reverse=True):
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 7, f'{change_type} ({len(change_list)} transactions)', ln=True)
                pdf.ln(2)
                
                # Find the actual transactions for these changes
                pdf.set_font('Arial', '', 9)
                for i, suggestion in enumerate(change_list[:10]):  # Show max 10 per category to save space
                    transaction_id = suggestion.get('id')
                    confidence = suggestion.get('confidence', 0)
                    
                    # Find the transaction details
                    transaction_details = None
                    for _, row in df.iterrows():
                        if str(row.get('id')) == str(transaction_id):
                            transaction_details = row
                            break
                    
                    if transaction_details is not None:
                        description = str(transaction_details.get('description', 'Unknown'))[:45]
                        amount = transaction_details.get('amount', 0)
                        date = str(transaction_details.get('date', 'Unknown'))[:10]
                        
                        pdf.cell(0, 4, f'  {i+1}. {description}...', ln=True)
                        pdf.cell(0, 4, f'      Date: {date} | Amount: ${amount:,.2f} | Confidence: {confidence:.1%}', ln=True)
                        pdf.ln(1)
                
                if len(change_list) > 10:
                    pdf.set_font('Arial', 'I', 9)
                    pdf.cell(0, 4, f'      ... and {len(change_list) - 10} more transactions', ln=True)
                    pdf.set_font('Arial', '', 9)
                
                pdf.ln(5)
                
                # Add page break if getting too long
                if pdf.get_y() > 250:
                    pdf.add_page()
        
        # For "No Changes" PDF, show what WOULD be changed
        elif not with_changes and potential_categorizations > 0:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'AI CATEGORIZATION PREVIEW', ln=True, align='C')
            pdf.ln(5)
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 8, f'POTENTIAL CHANGES: {potential_categorizations} transactions could be categorized', ln=True)
            pdf.ln(5)
            
            # Show sample transactions that would be changed
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 6, 'Sample Transactions That Would Be Categorized:', ln=True)
            pdf.ln(3)
            
            # Get some uncategorized transactions as examples
            uncategorized_examples = []
            for _, row in df.iterrows():
                category = row.get('category')
                if not category or str(category).lower() in ['misc', 'miscellaneous', 'uncategorized', '']:
                    uncategorized_examples.append(row)
                    if len(uncategorized_examples) >= 15:  # Show max 15 examples
                        break
            
            pdf.set_font('Arial', '', 9)
            for i, transaction in enumerate(uncategorized_examples):
                description = str(transaction.get('description', 'Unknown'))[:50]
                amount = transaction.get('amount', 0)
                date = str(transaction.get('date', 'Unknown'))[:10]
                current_cat = transaction.get('category', 'Uncategorized')
                
                pdf.cell(0, 4, f'{i+1}. {description}...', ln=True)
                pdf.cell(0, 4, f'    Date: {date} | Amount: ${amount:,.2f} | Current: {current_cat}', ln=True)
                pdf.ln(1)
            
            if len(uncategorized_examples) < potential_categorizations:
                pdf.set_font('Arial', 'I', 9)
                pdf.cell(0, 4, f'... and {potential_categorizations - len(uncategorized_examples)} more transactions', ln=True)
            
            pdf.ln(8)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 6, 'Click "Yes" in the AI dialog to categorize these transactions!', ln=True)
        
        # Simple recommendations
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Insights & Recommendations', ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        
        recommendations = []
        
        if uncategorized_count > 0:
            recommendations.append(f"Consider using AI categorization for {uncategorized_count} uncategorized transactions.")
        
        if len(category_counts) > 10:
            recommendations.append("Consider consolidating similar categories for cleaner reporting.")
        
        if with_changes:
            recommendations.append("AI categorization has been applied. Review the changes for accuracy.")
        else:
            recommendations.append("Use AI categorization to automatically organize your transactions.")
        
        for i, rec in enumerate(recommendations, 1):
            pdf.cell(0, 6, f'{i}. {rec}', ln=True)
            pdf.ln(2)
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 4, f'Report generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}', ln=True, align='C')
        pdf.cell(0, 4, f'Period: {start_date} to {end_date}', ln=True, align='C')
        
        # Save PDF
        import tempfile
        pdf_path = tempfile.mktemp(suffix='.pdf')
        pdf.output(pdf_path)
        
        print(f"[PDF] PDF generated successfully: {pdf_path}")
        
        filename = f'{month}_{account_type}_categorization_report.pdf'
        from fastapi.responses import FileResponse
        return FileResponse(pdf_path, filename=filename, media_type='application/pdf')
        
    except Exception as e:
        print(f"[PDF] Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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

# Enhanced Categorization Analytics Endpoints

@app.get("/api/analytics/accuracy-report")
async def get_accuracy_report(days: int = 7):
    """Get accuracy analytics for enhanced categorization"""
    try:
        report = analytics.get_accuracy_report(days)
        return report
    except Exception as e:
        logger.error(f"Error generating accuracy report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/performance-report")
async def get_performance_report(days: int = 7):
    """Get performance analytics for enhanced categorization"""
    try:
        report = analytics.get_performance_report(days)
        return report
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/business-impact-report")
async def get_business_impact_report(days: int = 30):
    """Get business impact analytics for enhanced categorization"""
    try:
        report = analytics.get_business_impact_report(days)
        return report
    except Exception as e:
        logger.error(f"Error generating business impact report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/track-correction")
async def track_user_correction(
    description: str = Body(...),
    ai_prediction: str = Body(...),
    user_correction: str = Body(...),
    confidence: float = Body(...),
    source: str = Body(...)
):
    """Track when a user corrects an AI categorization"""
    try:
        analytics.track_user_correction(
            original_description=description,
            ai_prediction=ai_prediction,
            user_correction=user_correction,
            confidence=confidence,
            source=source
        )
        return {"message": "User correction tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking user correction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/export")
async def export_analytics_data():
    """Export all analytics data to JSON file"""
    try:
        file_path = analytics.export_analytics_data()
        return FileResponse(file_path, filename=f"categorization_analytics_{datetime.now().strftime('%Y%m%d')}.json")
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 