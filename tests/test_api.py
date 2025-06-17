from fastapi.testclient import TestClient
from app.main import app
import pytest
from datetime import datetime, timedelta

client = TestClient(app)

def test_get_transactions():
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("date" in item for item in data)
    assert all("amount" in item for item in data)
    assert all("type" in item for item in data)
    assert all("category" in item for item in data)

def test_get_transactions_with_filters():
    response = client.get("/api/transactions?type=income&category=salary")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(item["type"] == "income" for item in data)
    assert all(item["category"] == "salary" for item in data)

def test_get_forecast():
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    response = client.get(f"/api/forecast?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "income" in data
    assert "expenses" in data
    assert "net_cash_flow" in data
    assert len(data["labels"]) > 0
    assert len(data["income"]) == len(data["labels"])
    assert len(data["expenses"]) == len(data["labels"])
    assert len(data["net_cash_flow"]) == len(data["labels"])

def test_get_insights():
    response = client.get("/api/insights")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("title" in item for item in data)
    assert all("description" in item for item in data)
    assert all("impact" in item for item in data)

def test_switch_data():
    response = client.post("/api/switch-data/seasonal_patterns.csv")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "seasonal_patterns.csv" in data["message"] 