#!/usr/bin/env python3
"""
Migration script to move data from CSV to Supabase
Run this after setting up your Supabase project and running the schema
"""

import pandas as pd
import os
from supabase import create_client, Client
from datetime import datetime
import uuid
from typing import List, Dict
import sys

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Use anon key for operations
CSV_FILE_PATH = "data/all_transactions.csv"
BATCH_SIZE = 1000

# Demo user ID (you can change this or make it configurable)
DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440000"  # Fixed UUID for demo

def create_supabase_client() -> Client:
    """Create and return Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        print("You can find these in your Supabase project settings")
        sys.exit(1)
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_transaction_data() -> pd.DataFrame:
    """Load transaction data from CSV"""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Loaded {len(df)} transactions from {CSV_FILE_PATH}")
        return df
    except FileNotFoundError:
        print(f"Error: Could not find {CSV_FILE_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)

def prepare_transaction_data(df: pd.DataFrame) -> tuple:
    """Prepare and separate transaction data by account type"""
    
    # Clean and prepare data
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')  # Convert to string format
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['user_id'] = DEMO_USER_ID
    
    # Map transaction_type to type and convert to income/expense
    df['type'] = df['transaction_type'].apply(lambda x: 'income' if x == 'Sale' else 'expense')
    
    # Clean account_type values
    df['account_type_clean'] = df['account_type'].apply(lambda x: 'checking' if 'Checking' in str(x) else 'credit')
    
    # Fill missing values
    df['category'] = df['category'].fillna('misc')
    df['status'] = df['status'].fillna('completed')
    
    # Remove rows with invalid data
    df = df.dropna(subset=['date', 'amount', 'description'])
    
    # Separate by account type
    checking_df = df[df['account_type_clean'] == 'checking'].copy()
    credit_df = df[df['account_type_clean'] == 'credit'].copy()
    
    # Select and rename columns for database
    columns_to_keep = [
        'user_id', 'date', 'amount', 'description', 
        'category', 'type', 'status'
    ]
    
    checking_transactions = checking_df[columns_to_keep].to_dict('records')
    credit_transactions = credit_df[columns_to_keep].to_dict('records')
    
    print(f"Prepared {len(checking_transactions)} checking transactions")
    print(f"Prepared {len(credit_transactions)} credit transactions")
    
    return checking_transactions, credit_transactions

def batch_insert(supabase: Client, table_name: str, data: List[Dict], batch_size: int = BATCH_SIZE):
    """Insert data in batches to avoid timeout"""
    total_records = len(data)
    successful_inserts = 0
    
    for i in range(0, total_records, batch_size):
        batch = data[i:i + batch_size]
        try:
            result = supabase.table(table_name).insert(batch).execute()
            successful_inserts += len(batch)
            print(f"Inserted batch {i//batch_size + 1}: {len(batch)} records into {table_name}")
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1} into {table_name}: {e}")
            # Continue with next batch instead of failing completely
            continue
    
    print(f"Successfully inserted {successful_inserts}/{total_records} records into {table_name}")
    return successful_inserts

def create_demo_user(supabase: Client):
    """Create demo user entry"""
    try:
        user_data = {
            "id": DEMO_USER_ID,
            "email": "demo@example.com"
        }
        result = supabase.table("users").insert(user_data).execute()
        print("Created demo user")
    except Exception as e:
        print(f"Demo user might already exist or error: {e}")

def calculate_and_insert_account_summaries(supabase: Client):
    """Calculate account balances and insert summaries"""
    try:
        # Calculate checking account balance
        checking_result = supabase.table("checking_transactions").select("amount, type").eq("user_id", DEMO_USER_ID).execute()
        checking_balance = 0
        for transaction in checking_result.data:
            if transaction['type'] == 'income':
                checking_balance += float(transaction['amount'])
            else:
                checking_balance -= float(transaction['amount'])
        
        # Calculate credit account balance
        credit_result = supabase.table("credit_transactions").select("amount, type").eq("user_id", DEMO_USER_ID).execute()
        credit_balance = 0
        for transaction in credit_result.data:
            if transaction['type'] == 'expense':
                credit_balance += float(transaction['amount'])
            else:
                credit_balance -= float(transaction['amount'])
        
        # Insert account summaries
        summaries = [
            {
                "user_id": DEMO_USER_ID,
                "account_type": "checking",
                "current_balance": checking_balance,
                "available_balance": checking_balance,
                "credit_limit": None
            },
            {
                "user_id": DEMO_USER_ID,
                "account_type": "credit",
                "current_balance": credit_balance,
                "available_balance": 5000 - credit_balance if credit_balance > 0 else 5000,
                "credit_limit": 5000
            }
        ]
        
        result = supabase.table("account_summaries").insert(summaries).execute()
        print(f"Created account summaries - Checking: ${checking_balance:.2f}, Credit: ${credit_balance:.2f}")
        
    except Exception as e:
        print(f"Error creating account summaries: {e}")

def main():
    """Main migration function"""
    print("Starting migration to Supabase...")
    print("=" * 50)
    
    # Initialize Supabase client
    supabase = create_supabase_client()
    print("✓ Connected to Supabase")
    
    # Load data
    df = load_transaction_data()
    print("✓ Loaded transaction data")
    
    # Prepare data
    checking_transactions, credit_transactions = prepare_transaction_data(df)
    print("✓ Prepared transaction data")
    
    # Create demo user
    create_demo_user(supabase)
    print("✓ Created demo user")
    
    # Insert checking transactions
    print("\nInserting checking transactions...")
    checking_inserted = batch_insert(supabase, "checking_transactions", checking_transactions)
    
    # Insert credit transactions
    print("\nInserting credit transactions...")
    credit_inserted = batch_insert(supabase, "credit_transactions", credit_transactions)
    
    # Create account summaries
    print("\nCreating account summaries...")
    calculate_and_insert_account_summaries(supabase)
    
    print("\n" + "=" * 50)
    print("Migration completed!")
    print(f"✓ Checking transactions: {checking_inserted}")
    print(f"✓ Credit transactions: {credit_inserted}")
    print("✓ Account summaries created")
    print("\nNext steps:")
    print("1. Update your .env file with Supabase credentials")
    print("2. Update your backend to use Supabase instead of SQLite")
    print("3. Test the API endpoints")

if __name__ == "__main__":
    main() 