import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from app.models.transaction import TransactionCreate, TransactionType, TransactionCategory, TransactionFrequency

class DataLoader:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.transactions_file = self.data_dir / "transactions2023.csv"
        self.current_file = "transactions2023.csv"
        
        # Define validation rules
        self.validation_rules = {
            TransactionCategory.RENT: {"min_amount": 500, "max_amount": 5000},
            TransactionCategory.UTILITIES: {"min_amount": 50, "max_amount": 500},
            TransactionCategory.GROCERIES: {"min_amount": 20, "max_amount": 1000},
            TransactionCategory.TRANSPORTATION: {"min_amount": 10, "max_amount": 500},
            TransactionCategory.ENTERTAINMENT: {"min_amount": 5, "max_amount": 300},
            TransactionCategory.HEALTHCARE: {"min_amount": 0, "max_amount": 2000},
        }

    def switch_data_file(self, filename: str) -> None:
        """Switch to a different data file."""
        new_file = self.data_dir / filename
        if not new_file.exists():
            raise FileNotFoundError(f"Data file not found: {filename}")
        self.current_file = filename
        self.transactions_file = new_file

    def load_transactions(self) -> pd.DataFrame:
        """Load transactions from CSV file."""
        if not self.transactions_file.exists():
            raise FileNotFoundError(f"Transactions file not found at {self.transactions_file}")
        
        df = pd.read_csv(self.transactions_file)
        return self._preprocess_dataframe(df)

    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the dataframe to ensure correct data types and formats."""
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure amount is float
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Rename 'type' column to 'transaction_type' if it exists
        if 'type' in df.columns:
            df = df.rename(columns={'type': 'transaction_type'})
        
        # Convert transaction types to uppercase
        df['transaction_type'] = df['transaction_type'].str.upper()
        
        # Validate transaction types
        valid_types = [t.value for t in TransactionType]
        df['transaction_type'] = df['transaction_type'].apply(
            lambda x: x if x in valid_types else TransactionType.INCOME.value
        )
        
        # Convert categories to uppercase
        df['category'] = df['category'].str.upper()
        
        # Map categories to valid ones if they don't match exactly
        category_mapping = {
            'SALARY': TransactionCategory.SALARY.value,
            'RENT': TransactionCategory.RENT.value,
            'UTILITIES': TransactionCategory.UTILITIES.value,
            'GROCERIES': TransactionCategory.GROCERIES.value,
            'ENTERTAINMENT': TransactionCategory.ENTERTAINMENT.value,
            'HEALTHCARE': TransactionCategory.HEALTHCARE.value,
            'TRANSPORTATION': TransactionCategory.TRANSPORTATION.value,
            'BILL': TransactionCategory.BILL.value,
            'OTHER': TransactionCategory.OTHER.value
        }
        
        # Apply category mapping
        df['category'] = df['category'].apply(
            lambda x: category_mapping.get(x, TransactionCategory.OTHER.value)
        )
        
        # Convert frequencies to uppercase if the column exists
        if 'frequency' in df.columns:
            df['frequency'] = df['frequency'].str.upper()
            
            # Validate frequencies
            valid_frequencies = [f.value for f in TransactionFrequency]
            df['frequency'] = df['frequency'].apply(
                lambda x: x if x in valid_frequencies else TransactionFrequency.ONE_TIME.value
            )
        else:
            # Add default frequency if not present
            df['frequency'] = TransactionFrequency.ONE_TIME.value
        
        # Apply amount validation based on category
        df['amount'] = df.apply(
            lambda row: self._validate_amount(row['amount'], row['category'], row['transaction_type']),
            axis=1
        )
        
        return df

    def _validate_amount(self, amount: float, category: str, transaction_type: str) -> float:
        """Validate amount based on category and transaction type."""
        if pd.isna(amount):
            return 0.0
            
        # Convert category string to enum
        try:
            category_enum = TransactionCategory(category)
        except ValueError:
            return amount
            
        # Get validation rules for category
        rules = self.validation_rules.get(category_enum, {"min_amount": 0, "max_amount": float('inf')})
        
        # Adjust amount based on transaction type
        if transaction_type == TransactionType.EXPENSE.value:
            amount = abs(amount)  # Ensure expenses are positive
        elif transaction_type == TransactionType.INCOME.value:
            amount = abs(amount)  # Ensure income is positive
            
        # Apply category-specific limits
        amount = max(rules["min_amount"], min(amount, rules["max_amount"]))
        
        return amount

    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Get transactions within a date range."""
        df = self.load_transactions()
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        return df[mask]

    def get_transactions_by_category(self, category: TransactionCategory) -> pd.DataFrame:
        """Get transactions for a specific category."""
        df = self.load_transactions()
        return df[df['category'] == category.value]

    def get_transactions_by_type(self, transaction_type: TransactionType) -> pd.DataFrame:
        """Get transactions of a specific type (income/expense)."""
        df = self.load_transactions()
        return df[df['transaction_type'] == transaction_type.value]

    def get_monthly_summary(self) -> pd.DataFrame:
        """Get monthly summary of transactions."""
        df = self.load_transactions()
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        
        summary = df.groupby(['month', 'transaction_type']).agg({
            'amount': 'sum',
            'category': 'count'
        }).reset_index()
        
        return summary

    def detect_patterns(self) -> Dict[str, Any]:
        """Detect patterns in transaction data."""
        df = self.load_transactions()
        patterns = {
            "recurring": self._detect_recurring_transactions(df),
            "seasonal": self._detect_seasonal_patterns(df),
            "anomalies": self._detect_anomalies(df)
        }
        return patterns

    def _detect_recurring_transactions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect recurring transactions based on amount and category."""
        recurring = []
        
        # Group by category and amount
        grouped = df.groupby(['category', 'amount'])
        
        for (category, amount), group in grouped:
            if len(group) >= 3:  # At least 3 occurrences
                dates = sorted(group['date'].tolist())
                intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                
                if len(set(intervals)) == 1:  # Same interval between all occurrences
                    recurring.append({
                        "category": category,
                        "amount": amount,
                        "frequency": intervals[0],
                        "dates": dates
                    })
        
        return recurring

    def _detect_seasonal_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect seasonal patterns in transactions."""
        seasonal = []
        
        # Group by month and category
        df['month'] = pd.to_datetime(df['date']).dt.month
        monthly_avg = df.groupby(['month', 'category'])['amount'].mean().reset_index()
        
        # Calculate standard deviation for each category
        category_std = df.groupby('category')['amount'].std()
        
        for category in df['category'].unique():
            category_data = monthly_avg[monthly_avg['category'] == category]
            if len(category_data) >= 3:  # Need at least 3 months of data
                # Check if any month's amount is significantly different
                threshold = category_std[category] * 1.5
                seasonal_months = category_data[
                    abs(category_data['amount'] - category_data['amount'].mean()) > threshold
                ]
                
                if not seasonal_months.empty:
                    seasonal.append({
                        "category": category,
                        "months": seasonal_months['month'].tolist(),
                        "average_amount": category_data['amount'].mean()
                    })
        
        return seasonal

    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalous transactions."""
        anomalies = []
        
        # Group by category
        for category in df['category'].unique():
            category_data = df[df['category'] == category]
            
            # Calculate mean and standard deviation
            mean = category_data['amount'].mean()
            std = category_data['amount'].std()
            
            # Find transactions more than 2 standard deviations from mean
            threshold = 2 * std
            anomalous = category_data[abs(category_data['amount'] - mean) > threshold]
            
            if not anomalous.empty:
                for _, row in anomalous.iterrows():
                    anomalies.append({
                        "date": row['date'],
                        "category": category,
                        "amount": row['amount'],
                        "expected_range": (mean - threshold, mean + threshold)
                    })
        
        return anomalies

    def validate_transaction(self, transaction: TransactionCreate) -> bool:
        """Validate a new transaction against existing data."""
        df = self.load_transactions()
        
        # Check for duplicate transactions
        duplicate = df[
            (df['date'] == transaction.date) &
            (df['amount'] == transaction.amount) &
            (df['transaction_type'] == transaction.transaction_type) &
            (df['category'] == transaction.category)
        ]
        
        # Validate amount based on category
        try:
            category_enum = TransactionCategory(transaction.category)
            rules = self.validation_rules.get(category_enum, {"min_amount": 0, "max_amount": float('inf')})
            
            if not (rules["min_amount"] <= abs(transaction.amount) <= rules["max_amount"]):
                return False
        except ValueError:
            pass
        
        return len(duplicate) == 0

    def save_transaction(self, transaction: TransactionCreate) -> None:
        """Save a new transaction to the CSV file."""
        df = self.load_transactions()
        
        new_row = {
            'date': transaction.date,
            'amount': transaction.amount,
            'transaction_type': transaction.transaction_type,
            'category': transaction.category,
            'description': transaction.description,
            'frequency': transaction.frequency
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.transactions_file, index=False) 