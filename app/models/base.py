from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionStatus(enum.Enum):
    POSTED = "posted"
    PENDING = "pending"

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False)

class Forecast(Base):
    __tablename__ = 'forecasts'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    income = Column(Float, nullable=False)
    expenses = Column(Float, nullable=False)
    category = Column(String, nullable=True)

class Insight(Base):
    __tablename__ = 'insights'
    
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    pattern = Column(String, nullable=False)
    recommendation = Column(String, nullable=False)
    confidence = Column(Float, nullable=False) 