#!/usr/bin/env python3
"""
Permanently update transaction categories using Capital One categorization system
This will update the actual data in your Supabase database with 70% accuracy targeting
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict, Any

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(project_root)

from app.services.supabase_service import SupabaseService
from app.services.capital_one_categorization import CapitalOneCategorizationService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryUpdater:
    def __init__(self):
        self.db = SupabaseService()
        self.categorizer = CapitalOneCategorizationService()
        self.demo_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
    async def backup_current_categories(self) -> Dict[str, Any]:
        """Create a backup of current categories before updating"""
        
        print("📦 Creating backup of current categories...")
        
        # Get all transactions
        checking_transactions = await self.db.get_checking_transactions(self.demo_user_id)
        credit_transactions = await self.db.get_credit_transactions(self.demo_user_id)
        
        backup = {
            'timestamp': datetime.now().isoformat(),
            'checking_transactions': {},
            'credit_transactions': {},
            'total_transactions': len(checking_transactions) + len(credit_transactions)
        }
        
        # Store original categories
        for t in checking_transactions:
            backup['checking_transactions'][t['id']] = {
                'original_category': t.get('category', 'misc'),
                'description': t.get('description', '')
            }
            
        for t in credit_transactions:
            backup['credit_transactions'][t['id']] = {
                'original_category': t.get('category', 'misc'),
                'description': t.get('description', '')
            }
        
        # Save backup to file
        import json
        backup_file = f"category_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup, f, indent=2)
            
        print(f"✅ Backup saved to: {backup_file}")
        return backup
    
    async def update_transaction_categories(self, limit: int = None) -> Dict[str, Any]:
        """Update transaction categories using Capital One system"""
        
        print("🏦 Starting Capital One category updates...")
        print(f"🎯 Target accuracy: 70%")
        
        # Get all transactions
        print("📊 Fetching transactions from database...")
        checking_transactions = await self.db.get_checking_transactions(self.demo_user_id)
        credit_transactions = await self.db.get_credit_transactions(self.demo_user_id)
        
        all_transactions = checking_transactions + credit_transactions
        
        if limit:
            all_transactions = all_transactions[:limit]
            print(f"📝 Limited to first {limit} transactions for testing")
        
        print(f"📈 Total transactions to process: {len(all_transactions)}")
        
        # Filter transactions that need categorization (misc, empty, etc.)
        need_categorization = []
        for t in all_transactions:
            current_cat = t.get('category', '').lower()
            if current_cat in ['misc', 'miscellaneous', '', 'other', 'unknown']:
                need_categorization.append(t)
        
        print(f"🔧 Transactions needing categorization: {len(need_categorization)}")
        print(f"✅ Already categorized: {len(all_transactions) - len(need_categorization)}")
        
        if not need_categorization:
            print("🎉 All transactions already have categories!")
            return {'updated': 0, 'total': len(all_transactions)}
        
        # Batch categorize using Capital One system
        print("🤖 Running Capital One AI categorization...")
        categorization_results = self.categorizer.batch_categorize(need_categorization)
        
        # Update database
        updated_count = 0
        checking_updates = []
        credit_updates = []
        
        print("💾 Updating database...")
        for result in categorization_results:
            transaction_id = result['transaction_id']
            new_category = result['category']
            
            # Find original transaction to determine account type
            original_transaction = next(
                (t for t in need_categorization if t['id'] == transaction_id), 
                None
            )
            
            if not original_transaction:
                continue
                
            # Determine account type by checking which list it came from
            is_checking = any(t['id'] == transaction_id for t in checking_transactions)
            
            try:
                if is_checking:
                    # Update checking transaction
                    success = await self.db.update_checking_transaction_category(
                        str(transaction_id), new_category
                    )
                    if success:
                        checking_updates.append({
                            'id': transaction_id,
                            'old_category': original_transaction.get('category', 'misc'),
                            'new_category': new_category,
                            'description': original_transaction.get('description', '')[:50]
                        })
                        updated_count += 1
                else:
                    # Update credit transaction
                    success = await self.db.update_credit_transaction_category(
                        str(transaction_id), new_category
                    )
                    if success:
                        credit_updates.append({
                            'id': transaction_id,
                            'old_category': original_transaction.get('category', 'misc'),
                            'new_category': new_category,
                            'description': original_transaction.get('description', '')[:50]
                        })
                        updated_count += 1
                        
            except Exception as e:
                logger.error(f"Error updating transaction {transaction_id}: {e}")
        
        # Generate accuracy report
        accuracy_report = self.categorizer.get_accuracy_report(need_categorization)
        
        return {
            'total_transactions': len(all_transactions),
            'needed_categorization': len(need_categorization),
            'updated_count': updated_count,
            'checking_updates': len(checking_updates),
            'credit_updates': len(credit_updates),
            'accuracy_report': accuracy_report,
            'sample_updates': (checking_updates + credit_updates)[:10]  # Show first 10
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Print detailed results of the categorization update"""
        
        print("\n" + "="*60)
        print("🎉 CAPITAL ONE CATEGORIZATION UPDATE COMPLETE")
        print("="*60)
        
        print(f"📊 Total Transactions: {results['total_transactions']}")
        print(f"🔧 Needed Categorization: {results['needed_categorization']}")
        print(f"✅ Successfully Updated: {results['updated_count']}")
        print(f"🏦 Checking Account Updates: {results['checking_updates']}")
        print(f"💳 Credit Account Updates: {results['credit_updates']}")
        
        accuracy = results['accuracy_report']
        print(f"\n📈 AI Accuracy Report:")
        print(f"   • Target Accuracy: {accuracy['target_accuracy']}%")
        print(f"   • Actual Accuracy: {accuracy['accuracy_percentage']}%")
        print(f"   • Note: {accuracy['demo_note']}")
        
        print(f"\n🏷️  Category Breakdown:")
        for category, count in accuracy['category_breakdown'].items():
            try:
                from app.utils.category_formatter import format_category_for_api
                display_name = format_category_for_api(category)
            except:
                display_name = category.replace('_', ' ').title()
            print(f"   • {display_name}: {count}")
        
        print(f"\n📝 Sample Updates (first 10):")
        for update in results['sample_updates']:
            old_cat = update['old_category'] or 'misc'
            # Use the formatter for better display
            try:
                from app.utils.category_formatter import format_category_for_api
                new_cat = format_category_for_api(update['new_category'])
            except:
                new_cat = update['new_category'].replace('_', ' ').title()
            desc = update['description']
            print(f"   • {old_cat:<12} → {new_cat:<25} | {desc}")
        
        print(f"\n🚀 Your transactions now use Capital One categories!")
        print(f"💡 Visit your app to see the updated categorizations.")

async def main():
    """Main execution function"""
    
    print("🏦 Capital One Transaction Category Updater")
    print("="*50)
    
    updater = CategoryUpdater()
    
    try:
        # Create backup first
        backup = await updater.backup_current_categories()
        
        # Ask for confirmation
        print(f"\n⚠️  This will permanently update {backup['total_transactions']} transactions")
        print("📦 Backup created - you can restore if needed")
        
        response = input("\n🔄 Proceed with permanent category updates? (y/N): ")
        
        if response.lower() not in ['y', 'yes']:
            print("❌ Update cancelled")
            return
        
        # Test with limited transactions first
        print("\n🧪 Running test update on first 50 transactions...")
        test_results = await updater.update_transaction_categories(limit=50)
        
        print(f"\n✅ Test completed: {test_results['updated_count']} transactions updated")
        
        # Ask if they want to continue with all
        response = input("\n🚀 Test successful! Update all remaining transactions? (y/N): ")
        
        if response.lower() in ['y', 'yes']:
            print("\n🔄 Updating all transactions...")
            final_results = await updater.update_transaction_categories()
            updater.print_results(final_results)
        else:
            print("✅ Test update complete. Your first 50 transactions have been updated.")
            updater.print_results(test_results)
            
    except Exception as e:
        logger.error(f"Error during category update: {e}")
        print(f"❌ Error: {e}")
        print("📦 Your data is safe - check the backup file if needed")

if __name__ == "__main__":
    asyncio.run(main()) 