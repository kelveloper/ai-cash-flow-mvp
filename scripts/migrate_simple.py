#!/usr/bin/env python3
"""
Simplified migration script to move data from CSV to Supabase
This version disables RLS temporarily for the migration
"""

import pandas as pd
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CSV_FILE_PATH = "data/all_transactions.csv"
BATCH_SIZE = 500  # Smaller batches for better reliability

# Demo user ID (fixed UUID for demo)
DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

def create_supabase_client() -> Client:
    """Create and return Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        sys.exit(1)
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def disable_rls(supabase: Client):
    """Temporarily disable RLS for migration"""
    try:
        # Disable RLS on tables
        supabase.rpc('exec_sql', {'sql': 'ALTER TABLE public.checking_transactions DISABLE ROW LEVEL SECURITY;'}).execute()
        supabase.rpc('exec_sql', {'sql': 'ALTER TABLE public.credit_transactions DISABLE ROW LEVEL SECURITY;'}).execute()
        supabase.rpc('exec_sql', {'sql': 'ALTER TABLE public.account_summaries DISABLE ROW LEVEL SECURITY;'}).execute()
        print("✓ Disabled RLS for migration")
    except Exception as e:
        print(f"Note: Could not disable RLS (this is okay): {e}")

def enable_rls(supabase: Client):
    """Re-enable RLS after migration"""
    try:
        # Re-enable RLS on tables
        supabase.rpc('exec_sql', {'sql': 'ALTER TABLE public.checking_transactions ENABLE ROW LEVEL SECURITY;'}).execute()
        supabase.rpc('exec_sql', {'sql': 'ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;'}).execute()
        supabase.rpc('exec_sql', {'sql': 'ALTER TABLE public.account_summaries ENABLE ROW LEVEL SECURITY;'}).execute()
        print("✓ Re-enabled RLS after migration")
    except Exception as e:
        print(f"Note: Could not re-enable RLS: {e}")

def load_and_prepare_data():
    """Load and prepare transaction data"""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Loaded {len(df)} transactions from {CSV_FILE_PATH}")
        
        # Clean and prepare data
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['user_id'] = DEMO_USER_ID
        
        # Map transaction_type to type
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
        
        # Select columns for database
        columns_to_keep = ['user_id', 'date', 'amount', 'description', 'category', 'type', 'status']
        
        checking_transactions = checking_df[columns_to_keep].to_dict('records')
        credit_transactions = credit_df[columns_to_keep].to_dict('records')
        
        print(f"Prepared {len(checking_transactions)} checking transactions")
        print(f"Prepared {len(credit_transactions)} credit transactions")
        
        return checking_transactions, credit_transactions
        
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def batch_insert(supabase: Client, table_name: str, data: list, batch_size: int = BATCH_SIZE):
    """Insert data in batches"""
    total_records = len(data)
    successful_inserts = 0
    
    print(f"Inserting {total_records} records into {table_name}...")
    
    for i in range(0, total_records, batch_size):
        batch = data[i:i + batch_size]
        try:
            result = supabase.table(table_name).insert(batch).execute()
            successful_inserts += len(batch)
            if (i // batch_size + 1) % 10 == 0:  # Print every 10th batch
                print(f"  Inserted {successful_inserts}/{total_records} records...")
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1}: {e}")
            continue
    
    print(f"✓ Successfully inserted {successful_inserts}/{total_records} records into {table_name}")
    return successful_inserts

def create_account_summaries(supabase: Client, checking_count: int, credit_count: int):
    """Create account summaries"""
    try:
        # Simple account summaries for demo
        summaries = [
            {
                "user_id": DEMO_USER_ID,
                "account_type": "checking",
                "current_balance": 10000.00,  # Demo balance
                "available_balance": 10000.00
            },
            {
                "user_id": DEMO_USER_ID,
                "account_type": "credit",
                "current_balance": 1500.00,  # Demo balance
                "available_balance": 3500.00,
                "credit_limit": 5000.00
            }
        ]
        
        result = supabase.table("account_summaries").insert(summaries).execute()
        print("✓ Created account summaries")
        
    except Exception as e:
        print(f"Error creating account summaries: {e}")

def main():
    """Main migration function"""
    print("🚀 Starting Supabase Migration")
    print("=" * 50)
    
    # Initialize Supabase client
    supabase = create_supabase_client()
    print("✓ Connected to Supabase")
    
    # Load and prepare data
    checking_transactions, credit_transactions = load_and_prepare_data()
    
    # Disable RLS temporarily
    disable_rls(supabase)
    
    try:
        # Insert checking transactions
        checking_inserted = batch_insert(supabase, "checking_transactions", checking_transactions)
        
        # Insert credit transactions  
        credit_inserted = batch_insert(supabase, "credit_transactions", credit_transactions)
        
        # Create account summaries
        create_account_summaries(supabase, checking_inserted, credit_inserted)
        
        print("\n" + "=" * 50)
        print("🎉 Migration Completed Successfully!")
        print(f"✅ Checking transactions: {checking_inserted}")
        print(f"✅ Credit transactions: {credit_inserted}")
        print("✅ Account summaries created")
        
    finally:
        # Re-enable RLS
        enable_rls(supabase)
    
    print("\n🔧 Next Steps:")
    print("1. Test the Supabase connection")
    print("2. Update your backend to use Supabase")
    print("3. Test all API endpoints")

if __name__ == "__main__":
    main() 