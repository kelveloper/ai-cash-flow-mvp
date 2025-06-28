#!/usr/bin/env python3
"""
Remove transactions with "Miscellaneous Sale" and "Miscellaneous Expense" descriptions
This will remove them from both Supabase and update CSV files
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

class MiscellaneousRemover:
    def __init__(self):
        self.db = SupabaseService()
        self.demo_user_id = "550e8400-e29b-41d4-a716-446655440000"
        self.target_descriptions = ["Miscellaneous Sale", "Miscellaneous Expense"]
        
    async def remove_from_supabase(self):
        """Remove miscellaneous transactions from Supabase"""
        
        print("🔍 Finding transactions to remove from Supabase...")
        
        # Get all transactions from Supabase
        checking_transactions = await self.db.get_checking_transactions(self.demo_user_id)
        credit_transactions = await self.db.get_credit_transactions(self.demo_user_id)
        
        # Find transactions to remove
        checking_to_remove = []
        credit_to_remove = []
        
        for transaction in checking_transactions:
            if transaction.get('description') in self.target_descriptions:
                checking_to_remove.append(transaction)
                
        for transaction in credit_transactions:
            if transaction.get('description') in self.target_descriptions:
                credit_to_remove.append(transaction)
        
        total_to_remove = len(checking_to_remove) + len(credit_to_remove)
        
        print(f"📊 Found transactions to remove:")
        print(f"   🏦 Checking account: {len(checking_to_remove)}")
        print(f"   💳 Credit account: {len(credit_to_remove)}")
        print(f"   📈 Total: {total_to_remove}")
        
        if total_to_remove == 0:
            print("✅ No miscellaneous transactions found!")
            return {"removed": 0, "checking_removed": 0, "credit_removed": 0}
        
        # Create backup before removal
        print("💾 Creating backup before removal...")
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'checking_transactions': checking_to_remove,
            'credit_transactions': credit_to_remove,
            'total_removed': total_to_remove
        }
        
        import json
        backup_file = f"miscellaneous_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        print(f"   📦 Backup saved to: {backup_file}")
        
        # Remove from Supabase
        print("🗑️  Removing transactions from Supabase...")
        
        checking_removed = 0
        credit_removed = 0
        
        # Remove checking transactions
        for transaction in checking_to_remove:
            try:
                # Use the SupabaseService delete_transaction method
                success = self.db.delete_transaction('checking', transaction['id'], self.demo_user_id)
                if success:
                    checking_removed += 1
                    print(f"   ✅ Removed checking transaction: {transaction['id']} - {transaction['description']}")
                else:
                    print(f"   ❌ Failed to remove checking transaction: {transaction['id']}")
            except Exception as e:
                logger.error(f"Error removing checking transaction {transaction['id']}: {e}")
        
        # Remove credit transactions
        for transaction in credit_to_remove:
            try:
                # Use the SupabaseService delete_transaction method
                success = self.db.delete_transaction('credit', transaction['id'], self.demo_user_id)
                if success:
                    credit_removed += 1
                    print(f"   ✅ Removed credit transaction: {transaction['id']} - {transaction['description']}")
                else:
                    print(f"   ❌ Failed to remove credit transaction: {transaction['id']}")
            except Exception as e:
                logger.error(f"Error removing credit transaction {transaction['id']}: {e}")
        
        total_removed = checking_removed + credit_removed
        
        print(f"\n📊 Supabase Removal Summary:")
        print(f"   🏦 Checking transactions removed: {checking_removed}")
        print(f"   💳 Credit transactions removed: {credit_removed}")
        print(f"   📈 Total removed: {total_removed}")
        
        return {
            "removed": total_removed,
            "checking_removed": checking_removed,
            "credit_removed": credit_removed,
            "backup_file": backup_file
        }
    
    async def update_csv_files(self):
        """Export updated data to CSV files after removal"""
        
        print("\n📝 Updating CSV files with cleaned data...")
        
        # Get all remaining transactions from Supabase
        checking_transactions = await self.db.get_checking_transactions(self.demo_user_id)
        credit_transactions = await self.db.get_credit_transactions(self.demo_user_id)
        
        print(f"✅ Remaining transactions: {len(checking_transactions)} checking + {len(credit_transactions)} credit")
        
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
            print("❌ No transactions remaining!")
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
                backup_path = f"{file_path}.backup_before_removal_{timestamp}"
                os.rename(file_path, backup_path)
                print(f"   📦 Backed up {csv_file}")
        
        # Select columns to export
        export_columns = [
            'id', 'date', 'description', 'amount', 'category', 'category_display',
            'account_type', 'transaction_type', 'user_id', 'created_at', 'updated_at'
        ]
        
        # Only include columns that exist in the DataFrame
        available_columns = [col for col in export_columns if col in all_transactions_df.columns]
        export_df = all_transactions_df[available_columns].copy()
        
        # Update all CSV files with cleaned data
        print(f"📝 Updating CSV files with {len(export_df)} clean transactions...")
        for csv_file in csv_files_to_update:
            file_path = os.path.join(data_dir, csv_file)
            export_df.to_csv(file_path, index=False)
            print(f"   ✅ Updated {csv_file}")
        
        return len(export_df)
    
    async def run_cleanup(self):
        """Run the complete cleanup process"""
        
        print("🧹 STARTING MISCELLANEOUS TRANSACTION CLEANUP")
        print("="*60)
        print(f"🎯 Target descriptions: {', '.join(self.target_descriptions)}")
        print()
        
        # Remove from Supabase
        removal_result = await self.remove_from_supabase()
        
        if removal_result["removed"] > 0:
            # Update CSV files with cleaned data
            remaining_count = await self.update_csv_files()
            
            print("\n" + "="*60)
            print("🎉 CLEANUP COMPLETE")
            print("="*60)
            print(f"🗑️  Transactions Removed: {removal_result['removed']}")
            print(f"   🏦 From Checking: {removal_result['checking_removed']}")
            print(f"   💳 From Credit: {removal_result['credit_removed']}")
            print(f"📊 Remaining Transactions: {remaining_count}")
            print(f"💾 Backup File: {removal_result['backup_file']}")
            print("="*60)
        else:
            print("\n✅ No miscellaneous transactions found - no cleanup needed!")

async def main():
    """Main function to run the cleanup"""
    remover = MiscellaneousRemover()
    await remover.run_cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 