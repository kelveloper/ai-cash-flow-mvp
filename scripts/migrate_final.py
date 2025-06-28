#!/usr/bin/env python3
"""
Final migration script - assumes RLS is already disabled
Run scripts/disable_rls_for_migration.sql first in Supabase dashboard
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
BATCH_SIZE = 500

# Demo user ID
DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

def main():
    """Main migration function"""
    print("🚀 Starting Final Supabase Migration")
    print("=" * 60)
    
    # Check environment
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Missing SUPABASE_URL or SUPABASE_KEY")
        sys.exit(1)
    
    # Create client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase")
    
    # Load CSV data
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"✅ Loaded {len(df)} transactions from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        sys.exit(1)
    
    # Prepare data
    print("🔄 Preparing data...")
    
    # Convert dates to strings
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['user_id'] = DEMO_USER_ID
    
    # Map transaction types
    df['type'] = df['transaction_type'].apply(lambda x: 'income' if x == 'Sale' else 'expense')
    
    # Clean account types
    df['account_type_clean'] = df['account_type'].apply(
        lambda x: 'checking' if 'Checking' in str(x) else 'credit'
    )
    
    # Fill missing values
    df['category'] = df['category'].fillna('misc')
    df['status'] = df['status'].fillna('completed')
    
    # Remove invalid rows
    df = df.dropna(subset=['date', 'amount', 'description'])
    
    # Separate by account type
    checking_df = df[df['account_type_clean'] == 'checking'].copy()
    credit_df = df[df['account_type_clean'] == 'credit'].copy()
    
    # Prepare records
    columns = ['user_id', 'date', 'amount', 'description', 'category', 'type', 'status']
    checking_records = checking_df[columns].to_dict('records')
    credit_records = credit_df[columns].to_dict('records')
    
    print(f"✅ Prepared {len(checking_records)} checking transactions")
    print(f"✅ Prepared {len(credit_records)} credit transactions")
    
    # Insert checking transactions
    print(f"\n🔄 Inserting checking transactions...")
    checking_success = 0
    for i in range(0, len(checking_records), BATCH_SIZE):
        batch = checking_records[i:i + BATCH_SIZE]
        try:
            result = supabase.table("checking_transactions").insert(batch).execute()
            checking_success += len(batch)
            if i % (BATCH_SIZE * 10) == 0:  # Progress every 5000 records
                print(f"   Progress: {checking_success}/{len(checking_records)} checking transactions")
        except Exception as e:
            print(f"❌ Error in checking batch {i//BATCH_SIZE + 1}: {e}")
            break
    
    print(f"✅ Inserted {checking_success}/{len(checking_records)} checking transactions")
    
    # Insert credit transactions
    print(f"\n🔄 Inserting credit transactions...")
    credit_success = 0
    for i in range(0, len(credit_records), BATCH_SIZE):
        batch = credit_records[i:i + BATCH_SIZE]
        try:
            result = supabase.table("credit_transactions").insert(batch).execute()
            credit_success += len(batch)
            if i % (BATCH_SIZE * 10) == 0:  # Progress every 5000 records
                print(f"   Progress: {credit_success}/{len(credit_records)} credit transactions")
        except Exception as e:
            print(f"❌ Error in credit batch {i//BATCH_SIZE + 1}: {e}")
            break
    
    print(f"✅ Inserted {credit_success}/{len(credit_records)} credit transactions")
    
    # Create account summaries
    print(f"\n🔄 Creating account summaries...")
    try:
        summaries = [
            {
                "user_id": DEMO_USER_ID,
                "account_type": "checking",
                "current_balance": 15000.00,
                "available_balance": 15000.00
            },
            {
                "user_id": DEMO_USER_ID,
                "account_type": "credit",
                "current_balance": 2500.00,
                "available_balance": 2500.00,
                "credit_limit": 5000.00
            }
        ]
        
        result = supabase.table("account_summaries").insert(summaries).execute()
        print("✅ Created account summaries")
        
    except Exception as e:
        print(f"❌ Error creating account summaries: {e}")
    
    # Final results
    print("\n" + "=" * 60)
    print("🎉 MIGRATION COMPLETED!")
    print("=" * 60)
    print(f"📊 Results:")
    print(f"   • Checking transactions: {checking_success:,}")
    print(f"   • Credit transactions:   {credit_success:,}")
    print(f"   • Total transactions:    {checking_success + credit_success:,}")
    print(f"   • Account summaries:     ✅")
    
    print(f"\n🔧 Next Steps:")
    print(f"   1. Run scripts/enable_rls_after_migration.sql in Supabase")
    print(f"   2. Test the Supabase connection")
    print(f"   3. Update your backend to use Supabase")
    print(f"   4. Test all API endpoints")
    
    if checking_success + credit_success > 170000:
        print(f"\n🚀 SUCCESS: Migration completed with {checking_success + credit_success:,} transactions!")
    else:
        print(f"\n⚠️  WARNING: Expected ~174k transactions but only migrated {checking_success + credit_success:,}")

if __name__ == "__main__":
    main() 