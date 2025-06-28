#!/usr/bin/env python3
"""
Export updated transaction data from Supabase back to CSV files
This will sync the Capital One categorization changes to the CSV files
"""

import os
import sys
import asyncio
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(project_root)

from app.services.supabase_service import SupabaseService
from app.utils.category_formatter import format_category_for_api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExporter:
    def __init__(self):
        self.db = SupabaseService()
        self.demo_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
    async def export_to_csv(self):
        """Export all transaction data from Supabase to CSV files"""
        
        print("📊 Exporting updated transaction data from Supabase to CSV...")
        
        # Get all transactions from Supabase
        print("🔍 Fetching all transactions from Supabase...")
        checking_transactions = await self.db.get_checking_transactions(self.demo_user_id)
        credit_transactions = await self.db.get_credit_transactions(self.demo_user_id)
        
        print(f"✅ Retrieved {len(checking_transactions)} checking transactions")
        print(f"✅ Retrieved {len(credit_transactions)} credit transactions")
        
        # Convert to DataFrames and add account_type column
        checking_df = pd.DataFrame(checking_transactions)
        if not checking_df.empty:
            checking_df['account_type'] = 'checking'
            
        credit_df = pd.DataFrame(credit_transactions)
        if not credit_df.empty:
            credit_df['account_type'] = 'credit'
        
        # Combine all transactions
        if not checking_df.empty and not credit_df.empty:
            all_transactions_df = pd.concat([checking_df, credit_df], ignore_index=True)
        elif not checking_df.empty:
            all_transactions_df = checking_df
        elif not credit_df.empty:
            all_transactions_df = credit_df
        else:
            print("❌ No transactions found!")
            return
        
        # Sort by date (newest first)
        all_transactions_df = all_transactions_df.sort_values('date', ascending=False)
        
        # Add formatted category for display
        all_transactions_df['category_display'] = all_transactions_df['category'].apply(
            lambda x: format_category_for_api(x) if x else x
        )
        
        # Create backup of existing CSV files
        data_dir = os.path.join(project_root, 'data')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        csv_files_to_update = [
            'all_transactions.csv',
            'all_transactions_demo.csv',
            'all_transactions_fixed.csv',
            'all_transactions_ready.csv'
        ]
        
        print(f"💾 Backing up existing CSV files...")
        for csv_file in csv_files_to_update:
            file_path = os.path.join(data_dir, csv_file)
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup_before_export_{timestamp}"
                os.rename(file_path, backup_path)
                print(f"   📦 Backed up {csv_file} to {os.path.basename(backup_path)}")
        
        # Select columns to export (match original CSV structure)
        export_columns = [
            'id', 'date', 'description', 'amount', 'category', 'category_display',
            'account_type', 'transaction_type', 'user_id', 'created_at', 'updated_at'
        ]
        
        # Only include columns that exist in the DataFrame
        available_columns = [col for col in export_columns if col in all_transactions_df.columns]
        export_df = all_transactions_df[available_columns].copy()
        
        # Update all CSV files with the latest data
        print(f"📝 Updating CSV files with {len(export_df)} transactions...")
        for csv_file in csv_files_to_update:
            file_path = os.path.join(data_dir, csv_file)
            export_df.to_csv(file_path, index=False)
            print(f"   ✅ Updated {csv_file}")
        
        # Generate summary report
        category_counts = export_df['category'].value_counts()
        
        print("\n" + "="*60)
        print("🎉 CSV EXPORT COMPLETE")
        print("="*60)
        print(f"📊 Total Transactions Exported: {len(export_df)}")
        print(f"🏦 Checking Account: {len(export_df[export_df['account_type'] == 'checking'])}")
        print(f"💳 Credit Account: {len(export_df[export_df['account_type'] == 'credit'])}")
        print(f"📁 Files Updated: {len(csv_files_to_update)}")
        
        print(f"\n🏷️  Category Distribution:")
        for category, count in category_counts.head(10).items():
            try:
                display_name = format_category_for_api(category)
                print(f"   • {display_name}: {count}")
            except:
                print(f"   • {category}: {count}")
        
        print(f"\n📂 Updated Files:")
        for csv_file in csv_files_to_update:
            print(f"   • data/{csv_file}")
            
        print(f"\n💡 Note: Original files backed up with timestamp {timestamp}")
        print("="*60)

async def main():
    """Main function to run the export"""
    exporter = DataExporter()
    await exporter.export_to_csv()

if __name__ == "__main__":
    asyncio.run(main()) 