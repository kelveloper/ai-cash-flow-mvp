from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from .models.transaction import TransactionCreate, TransactionResponse, TransactionType, TransactionCategory
from .utils.data_loader import DataLoader
import pandas as pd

app = FastAPI(title="Cash Flow Dashboard with XAI")

# Get the absolute path to the templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize data loader
data_loader = DataLoader()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/switch-data/{filename}")
async def switch_data_file(filename: str):
    """Switch to a different data file."""
    try:
        data_loader.switch_data_file(filename)
        return {"message": f"Switched to {filename}"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast")
async def get_forecast(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
):
    try:
        # Load transactions
        df = data_loader.load_transactions()
        
        # Convert dates to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Apply date range filter if provided
        if start_date and start_date.strip():
            start_date = pd.to_datetime(start_date)
            df = df[df['date'] >= start_date]
        if end_date and end_date.strip():
            end_date = pd.to_datetime(end_date)
            df = df[df['date'] <= end_date]
            
        # Apply category filter if provided
        if category and category.strip():
            df = df[df['category'] == category]
        
        if df.empty:
            return {
                "labels": [],
                "income": [],
                "expenses": [],
                "net_cash_flow": []
            }
        
        # Create monthly bins
        df['month'] = df['date'].dt.strftime('%Y-%m')
        
        # Calculate income and expenses separately
        income = df[df['transaction_type'] == TransactionType.INCOME.value].groupby('month')['amount'].sum()
        expenses = df[df['transaction_type'] == TransactionType.EXPENSE.value].groupby('month')['amount'].sum()
        
        # Create complete range of months
        first_date = df['date'].min()
        last_date = df['date'].max()
        all_months = pd.date_range(start=first_date, end=last_date, freq='ME').strftime('%Y-%m')
        
        # Reindex to include all months
        income = income.reindex(all_months, fill_value=0)
        expenses = expenses.reindex(all_months, fill_value=0)
        
        # Calculate net cash flow
        net_cash_flow = income - expenses
        
        return {
            "labels": all_months.tolist(),
            "income": income.tolist(),
            "expenses": expenses.tolist(),
            "net_cash_flow": net_cash_flow.tolist()
        }
            
    except Exception as e:
        print(f"Error in forecast endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights():
    """Get XAI insights for the forecast."""
    try:
        # Get patterns from the data
        patterns = data_loader.detect_patterns()
        
        insights = []
        
        # Process recurring transactions
        for recurring in patterns.get("recurring", []):
            insights.append({
                "type": "recurring",
                "title": f"Recurring {recurring['category']} Transaction",
                "description": f"Regular {recurring['category']} payment of ${recurring['amount']:.2f} every {recurring['frequency']} days",
                "data": recurring
            })
        
        # Process seasonal patterns
        for seasonal in patterns.get("seasonal", []):
            month_names = [datetime(2024, m, 1).strftime('%B') for m in seasonal['months']]
            insights.append({
                "type": "seasonal",
                "title": f"Seasonal Pattern in {seasonal['category']}",
                "description": f"Unusual spending in {', '.join(month_names)} for {seasonal['category']}",
                "data": seasonal
            })
        
        # Process anomalies
        for anomaly in patterns.get("anomalies", []):
            insights.append({
                "type": "anomaly",
                "title": f"Unusual {anomaly['category']} Transaction",
                "description": f"Transaction of ${anomaly['amount']:.2f} on {anomaly['date']} is outside normal range (${anomaly['expected_range'][0]:.2f} - ${anomaly['expected_range'][1]:.2f})",
                "data": anomaly
            })
        
        return insights
    except Exception as e:
        print(f"Error in insights endpoint: {str(e)}")
        return []

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

@app.get("/api/transactions")
async def get_transactions():
    """Get recent transactions."""
    try:
        df = data_loader.load_transactions()
        
        # Sort by date descending and get last 10 transactions
        df = df.sort_values('date', ascending=False).head(10)
        
        # Format the data for display
        transactions = []
        for _, row in df.iterrows():
            transactions.append({
                "date": row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], (datetime, date)) else str(row['date']),
                "amount": f"${float(row['amount']):.2f}",
                "type": row['transaction_type'],
                "category": row['category'],
                "description": str(row['description'])
            })
        
        return transactions
    except Exception as e:
        print(f"Error in transactions endpoint: {str(e)}")
        return [] 