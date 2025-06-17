from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .transaction import TransactionType, TransactionStatus, TransactionCategory

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    category = Column(SQLEnum(TransactionCategory), nullable=False)
    description = Column(String, nullable=False)
    status = Column(SQLEnum(TransactionStatus), nullable=False)
    account_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    income = Column(Float, nullable=False)
    expenses = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    pattern = Column(String, nullable=False)
    recommendation = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 