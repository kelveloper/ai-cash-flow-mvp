#!/usr/bin/env python3
"""
Script to remove all transactions with description "Miscellaneous Expense" 
from both Supabase database and CSV files
"""

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

def create_supabase_client() -> Client:
    """Create and return Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        sys.exit(1)
    
    return create_client(supabase_url, supabase_key)

def remove_from_supabase():
    """Remove transactions with 'Miscellaneous Expense' description from Supabase"""
    print("🗑️  Removing 'Miscellaneous Expense' transactions from Supabase...")
    
    supabase = create_supabase_client()
    
    # Count transactions to be removed
    checking_count = supabase.table('checking_transactions').select('id').ilike('description', '%Miscellaneous Expense%').execute()
    credit_count = supabase.table('credit_transactions').select('id').ilike('description', '%Miscellaneous Expense%').execute()
    
    print(f"Found {len(checking_count.data)} checking transactions to remove")
    print(f"Found {len(credit_count.data)} credit transactions to remove")
    
    total_to_remove = len(checking_count.data) + len(credit_count.data)
    
    if total_to_remove == 0:
        print("✅ No 'Miscellaneous Expense' transactions found in Supabase")
        return 0
    
    # Remove from checking_transactions
    if len(checking_count.data) > 0:
        result = supabase.table('checking_transactions').delete().ilike('description', '%Miscellaneous Expense%').execute()
        print(f"✅ Removed {len(checking_count.data)} checking transactions")
    
    # Remove from credit_transactions
    if len(credit_count.data) > 0:
        result = supabase.table('credit_transactions').delete().ilike('description', '%Miscellaneous Expense%').execute()
        print(f"✅ Removed {len(credit_count.data)} credit transactions")
    
    print(f"✅ Total removed from Supabase: {total_to_remove} transactions")
    return total_to_remove

def remove_from_csv_files():
    """Remove transactions with 'Miscellaneous Expense' description from CSV files"""
    print("\n🗑️  Removing 'Miscellaneous Expense' transactions from CSV files...")
    
    csv_files = [
        "data/all_transactions.csv",
        "data/all_transactions_demo.csv", 
        "data/all_transactions_fixed.csv",
        "data/all_transactions_ready.csv"
    ]
    
    total_removed = 0
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"⚠️  File not found: {csv_file}")
            continue
            
        try:
            # Load CSV
            df = pd.read_csv(csv_file)
            original_count = len(df)
            
            # Remove rows with 'Miscellaneous Expense' in description
            df_cleaned = df[~df['description'].str.contains('Miscellaneous Expense', case=False, na=False)]
            new_count = len(df_cleaned)
            removed_count = original_count - new_count
            
            if removed_count > 0:
                # Create backup
                backup_file = f"{csv_file}.backup"
                df_original = pd.read_csv(csv_file)
                df_original.to_csv(backup_file, index=False)
                print(f"📁 Created backup: {backup_file}")
                
                # Save cleaned data
                df_cleaned.to_csv(csv_file, index=False)
                print(f"✅ {csv_file}: Removed {removed_count} transactions ({original_count} → {new_count})")
                total_removed += removed_count
            else:
                print(f"✅ {csv_file}: No 'Miscellaneous Expense' transactions found")
                
        except Exception as e:
            print(f"❌ Error processing {csv_file}: {e}")
    
    print(f"✅ Total removed from CSV files: {total_removed} transactions")
    return total_removed

def main():
    """Main function"""
    print("🧹 Removing 'Miscellaneous Expense' transactions")
    print("=" * 50)
    
    # Remove from Supabase
    supabase_removed = remove_from_supabase()
    
    # Remove from CSV files
    csv_removed = remove_from_csv_files()
    
    print("\n" + "=" * 50)
    print("✅ Cleanup completed successfully!")
    print(f"📊 Summary:")
    print(f"   - Supabase: {supabase_removed} transactions removed")
    print(f"   - CSV files: {csv_removed} transactions removed")
    print(f"   - Total: {supabase_removed + csv_removed} transactions removed")
    
    if supabase_removed > 0 or csv_removed > 0:
        print("\n💡 Note: Backup files were created for CSV files")
        print("🔄 You may want to restart your application to see changes")

if __name__ == "__main__":
    main() 