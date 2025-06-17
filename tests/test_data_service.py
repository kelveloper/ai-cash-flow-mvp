import pytest
from app.services.data_service import (
    get_transactions,
    get_forecast,
    get_insights,
    load_data
)
from datetime import datetime, timedelta

def test_get_transactions():
    transactions = get_transactions()
    assert isinstance(transactions, list)
    assert len(transactions) > 0
    
    # Test transaction structure
    transaction = transactions[0]
    assert "date" in transaction
    assert "amount" in transaction
    assert "type" in transaction
    assert "category" in transaction
    assert "description" in transaction
    
    # Test date format
    try:
        datetime.strptime(transaction["date"], "%Y-%m-%d")
    except ValueError:
        pytest.fail("Invalid date format")
    
    # Test amount format
    assert isinstance(transaction["amount"], str)
    assert transaction["amount"].startswith("$")
    
    # Test type values
    assert transaction["type"] in ["income", "expense"]

def test_get_forecast():
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    forecast = get_forecast(start_date, end_date)
    assert isinstance(forecast, dict)
    assert "labels" in forecast
    assert "income" in forecast
    assert "expenses" in forecast
    assert "net_cash_flow" in forecast
    
    # Test data consistency
    assert len(forecast["labels"]) > 0
    assert len(forecast["income"]) == len(forecast["labels"])
    assert len(forecast["expenses"]) == len(forecast["labels"])
    assert len(forecast["net_cash_flow"]) == len(forecast["labels"])
    
    # Test numeric values
    assert all(isinstance(x, (int, float)) for x in forecast["income"])
    assert all(isinstance(x, (int, float)) for x in forecast["expenses"])
    assert all(isinstance(x, (int, float)) for x in forecast["net_cash_flow"])

def test_get_insights():
    insights = get_insights()
    assert isinstance(insights, list)
    assert len(insights) > 0
    
    # Test insight structure
    insight = insights[0]
    assert "title" in insight
    assert "description" in insight
    assert "impact" in insight
    assert "confidence" in insight
    
    # Test impact values
    assert insight["impact"] in ["high", "medium", "low"]
    
    # Test confidence values
    assert 0 <= insight["confidence"] <= 1

def test_load_data():
    # Test loading default data
    data = load_data()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Test loading specific file
    data = load_data("seasonal_patterns.csv")
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Test invalid file
    with pytest.raises(FileNotFoundError):
        load_data("nonexistent.csv") 