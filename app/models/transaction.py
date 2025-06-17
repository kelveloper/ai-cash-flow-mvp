from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from decimal import Decimal

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"

class TransactionCategory(str, Enum):
    SALARY = "salary"
    RENT = "rent"
    UTILITIES = "utilities"
    GROCERIES = "groceries"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    SUBSCRIPTIONS = "subscriptions"
    FEES = "fees"
    TAXES = "taxes"
    INSURANCE = "insurance"
    SUPPLIES = "supplies"
    MERCHANDISE = "merchandise"
    FOOD = "food"
    COFFEE = "coffee"
    MARKETING = "marketing"
    MAINTENANCE = "maintenance"
    PASTRY = "pastry"
    SANDWICH = "sandwich"
    CATERING = "catering"
    BILL = "bill"
    MISC = "misc"
    OTHER = "other"

class TransactionStatus(str, Enum):
    POSTED = "posted"
    PENDING = "pending"

class TransactionBase(BaseModel):
    date: date
    amount: Decimal
    type: TransactionType
    category: TransactionCategory
    description: str
    status: TransactionStatus
    frequency: TransactionFrequency
    account_type: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class ForecastPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class Forecast(BaseModel):
    period: ForecastPeriod = Field(..., description="Forecast period")
    start_date: date = Field(..., description="Start date of the forecast")
    end_date: date = Field(..., description="End date of the forecast")
    predicted_amount: float = Field(..., description="Predicted amount")
    confidence_interval: Dict[str, float] = Field(..., description="Confidence interval for the prediction")
    factors: List[Dict[str, Any]] = Field(..., description="Factors influencing the forecast")

class InsightType(str, Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    PATTERN = "pattern"
    RECOMMENDATION = "recommendation"

class Insight(BaseModel):
    type: InsightType = Field(..., description="Type of insight")
    title: str = Field(..., description="Title of the insight")
    description: str = Field(..., description="Detailed description of the insight")
    impact: float = Field(..., description="Impact score of the insight")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the insight")
    related_transactions: List[int] = Field(..., description="IDs of related transactions")
    created_at: datetime = Field(default_factory=datetime.now, description="When the insight was created")

# Example: Budget Models
class BudgetCategory(str, Enum):
    HOUSING = "housing"
    FOOD = "food"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    SAVINGS = "savings"
    OTHER = "other"

class Budget(BaseModel):
    category: BudgetCategory = Field(..., description="Budget category")
    amount: float = Field(..., gt=0, description="Budget amount")
    period: TransactionFrequency = Field(..., description="Budget period")
    start_date: date = Field(..., description="Start date of the budget period")
    end_date: date = Field(..., description="End date of the budget period")

# Example: Cash Flow Analysis Models
class CashFlowMetric(str, Enum):
    NET_CASH_FLOW = "net_cash_flow"
    OPERATING_CASH_FLOW = "operating_cash_flow"
    INVESTING_CASH_FLOW = "investing_cash_flow"
    FINANCING_CASH_FLOW = "financing_cash_flow"

class CashFlowAnalysis(BaseModel):
    metric: CashFlowMetric = Field(..., description="Type of cash flow metric")
    value: float = Field(..., description="Value of the metric")
    period: TransactionFrequency = Field(..., description="Analysis period")
    trend: float = Field(..., description="Trend value (positive or negative)")
    comparison: Dict[str, float] = Field(..., description="Comparison with previous periods")

# Example: Financial Health Models
class FinancialHealthIndicator(str, Enum):
    LIQUIDITY = "liquidity"
    SOLVENCY = "solvency"
    PROFITABILITY = "profitability"
    EFFICIENCY = "efficiency"

class FinancialHealth(BaseModel):
    indicator: FinancialHealthIndicator = Field(..., description="Type of financial health indicator")
    score: float = Field(..., ge=0, le=100, description="Health score (0-100)")
    status: str = Field(..., description="Status description")
    recommendations: List[str] = Field(..., description="List of recommendations")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class TransactionUpdate(BaseModel):
    category: TransactionCategory 