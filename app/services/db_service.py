from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from app.models import Base, Transaction, Forecast, Insight, TransactionType, TransactionStatus, TransactionCategory
import pandas as pd
from datetime import datetime, date
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///app/data/database/cash_flow.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseService:
    def __init__(self):
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def get_transactions(
        self,
        type: Optional[TransactionType] = None,
        category: Optional[str] = None
    ) -> List[Transaction]:
        """Get transactions with optional type and category filters."""
        query = self.db.query(Transaction)
        if type:
            query = query.filter(Transaction.type == type)
        if category:
            query = query.filter(Transaction.category == category)
        return query.all()

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a single transaction by ID."""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def create_transaction(self, transaction: Transaction) -> Transaction:
        """Create a new transaction."""
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update_transaction(self, transaction_id: int, **kwargs) -> Optional[Transaction]:
        """Update a transaction by ID."""
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            for key, value in kwargs.items():
                setattr(transaction, key, value)
            self.db.commit()
            self.db.refresh(transaction)
        return transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by ID."""
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
            return True
        return False

    def get_forecast(
        self,
        start_date: date,
        end_date: date,
        category: Optional[str] = None
    ) -> List[Forecast]:
        """Get forecast data with optional category filter."""
        logger.info(f"Querying forecasts from {start_date} to {end_date}, category: {category}")
        query = self.db.query(Forecast).filter(
            Forecast.date >= start_date,
            Forecast.date <= end_date
        )
        if category:
            query = query.filter(Forecast.category == category)
        forecasts = query.all()
        logger.info(f"Found {len(forecasts)} forecasts")
        for f in forecasts:
            logger.info(f"Forecast: date={f.date}, income={f.income}, expenses={f.expenses}, category={f.category}")
        return forecasts

    def get_insights(self, category: Optional[str] = None) -> List[Insight]:
        """Get insights with optional category filter."""
        query = self.db.query(Insight)
        if category:
            query = query.filter(Insight.category == category)
        return query.all()

    def import_from_csv(self, file_path: str):
        """Import data from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            df.columns = [c.strip() for c in df.columns]  # Normalize column names
            
            if "transactions" in file_path:
                for _, row in df.iterrows():
                    transaction = Transaction(
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        amount=float(row['amount']),
                        type=TransactionType[row['type'].strip().upper()],
                        category=TransactionCategory[row['category'].strip().upper()],
                        description=row['description'],
                        status=TransactionStatus[row['status'].strip().upper()],
                        account_type=row.get('account_type', None)
                    )
                    self.db.add(transaction)
            
            elif "forecast" in file_path:
                for _, row in df.iterrows():
                    forecast = Forecast(
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        income=float(row['income']),
                        expenses=float(row['expenses']),
                        category=row.get('category')
                    )
                    self.db.add(forecast)
            
            elif "insights" in file_path:
                for _, row in df.iterrows():
                    insight = Insight(
                        category=row['category'],
                        pattern=row['pattern'],
                        recommendation=row['recommendation'],
                        confidence=float(row['confidence'])
                    )
                    self.db.add(insight)
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def export_to_csv(self, file_path: str, data_type: str):
        """Export data to a CSV file."""
        try:
            if data_type == "transactions":
                data = self.get_transactions()
                df = pd.DataFrame([{
                    'date': t.date,
                    'amount': t.amount,
                    'type': t.type.value,
                    'category': t.category.value,
                    'description': t.description,
                    'status': t.status.value
                } for t in data])
            elif data_type == "forecast":
                data = self.get_forecast(date.today(), date.today())
                df = pd.DataFrame([{
                    'date': f.date,
                    'income': f.income,
                    'expenses': f.expenses,
                    'category': f.category
                } for f in data])
            elif data_type == "insights":
                data = self.get_insights()
                df = pd.DataFrame([{
                    'category': i.category,
                    'pattern': i.pattern,
                    'recommendation': i.recommendation,
                    'confidence': i.confidence
                } for i in data])
            
            df.to_csv(file_path, index=False)
        except Exception as e:
            raise e

    def get_transactions_paginated(self, limit=100, offset=0):
        return (
            self.db.query(Transaction)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_transactions_count(self):
        return self.db.query(Transaction).count() 