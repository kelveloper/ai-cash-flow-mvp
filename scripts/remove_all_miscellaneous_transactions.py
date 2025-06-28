#!/usr/bin/env python3
"""
Remove ALL "Miscellaneous Sale" and "Miscellaneous Expense" transactions from entire Supabase database
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append('.')
from app.services.supabase_service import SupabaseService

async def remove_all_miscellaneous():
    db = SupabaseService()
    user_id = '550e8400-e29b-41d4-a716-446655440000'
    
    print('🧹 COMPREHENSIVE MISCELLANEOUS TRANSACTION CLEANUP')
    print('=' * 60)
    print('🎯 Target descriptions: "Miscellaneous Sale", "Miscellaneous Expense"')
    print('📅 Scope: ALL transactions (all dates)')
    print()
    
    try:
        # Get ALL transactions from both tables (no date filtering)
        print('🔍 Scanning entire database for miscellaneous transactions...')
        
        checking_transactions = await db.get_checking_transactions(user_id)
        credit_transactions = await db.get_credit_transactions(user_id)
        
        print(f'📊 Total transactions in database:')
        print(f'   🏦 Checking: {len(checking_transactions)}')
        print(f'   💳 Credit: {len(credit_transactions)}')
        print(f'   📈 Total: {len(checking_transactions) + len(credit_transactions)}')
        print()
        
        # Find exact matches for removal
        checking_to_remove = []
        credit_to_remove = []
        
        for t in checking_transactions:
            desc = t.get('description', '')
            if desc in ['Miscellaneous Sale', 'Miscellaneous Expense']:
                checking_to_remove.append(t)
        
        for t in credit_transactions:
            desc = t.get('description', '')
            if desc in ['Miscellaneous Sale', 'Miscellaneous Expense']:
                credit_to_remove.append(t)
        
        total_to_remove = len(checking_to_remove) + len(credit_to_remove)
        
        print(f'🎯 Found transactions to remove:')
        print(f'   🏦 Checking account: {len(checking_to_remove)}')
        print(f'   💳 Credit account: {len(credit_to_remove)}')
        print(f'   📈 Total: {total_to_remove}')
        print()
        
        if total_to_remove == 0:
            print('✅ No miscellaneous transactions found - database is already clean!')
            return
        
        # Show breakdown by description
        checking_sales = [t for t in checking_to_remove if t.get('description') == 'Miscellaneous Sale']
        checking_expenses = [t for t in checking_to_remove if t.get('description') == 'Miscellaneous Expense']
        credit_sales = [t for t in credit_to_remove if t.get('description') == 'Miscellaneous Sale']
        credit_expenses = [t for t in credit_to_remove if t.get('description') == 'Miscellaneous Expense']
        
        print(f'📋 Breakdown by type:')
        print(f'   🏦 Checking "Miscellaneous Sale": {len(checking_sales)}')
        print(f'   🏦 Checking "Miscellaneous Expense": {len(checking_expenses)}')
        print(f'   💳 Credit "Miscellaneous Sale": {len(credit_sales)}')
        print(f'   💳 Credit "Miscellaneous Expense": {len(credit_expenses)}')
        print()
        
        # Show date range of transactions to be removed
        all_to_remove = checking_to_remove + credit_to_remove
        if all_to_remove:
            dates = [t.get('date') for t in all_to_remove if t.get('date')]
            if dates:
                dates.sort()
                print(f'📅 Date range of transactions to remove: {dates[0]} to {dates[-1]}')
                print()
        
        # Create comprehensive backup
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'cleanup_scope': 'entire_database',
            'total_removed': total_to_remove,
            'breakdown': {
                'checking_miscellaneous_sale': len(checking_sales),
                'checking_miscellaneous_expense': len(checking_expenses),
                'credit_miscellaneous_sale': len(credit_sales),
                'credit_miscellaneous_expense': len(credit_expenses)
            },
            'checking_transactions_removed': checking_to_remove,
            'credit_transactions_removed': credit_to_remove
        }
        
        backup_file = f"all_miscellaneous_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        print(f'💾 Complete backup saved to: {backup_file}')
        print()
        
        # Confirm before proceeding
        print(f'⚠️  WARNING: This will permanently delete {total_to_remove} transactions!')
        response = input('🤔 Do you want to proceed? (yes/no): ').lower().strip()
        
        if response not in ['yes', 'y']:
            print('❌ Operation cancelled by user')
            return
        
        print()
        print(f'🗑️  Removing {total_to_remove} transactions...')
        
        # Remove checking transactions
        removed_checking = 0
        failed_checking = 0
        
        for t in checking_to_remove:
            try:
                success = db.delete_transaction('checking', t.get('id'), user_id)
                if success:
                    removed_checking += 1
                    print(f'   ✅ Removed checking: "{t.get("description")}" (ID: {t.get("id")}) - {t.get("date")}')
                else:
                    failed_checking += 1
                    print(f'   ❌ Failed checking: "{t.get("description")}" (ID: {t.get("id")})')
            except Exception as e:
                failed_checking += 1
                print(f'   ❌ Error removing checking transaction {t.get("id")}: {e}')
        
        # Remove credit transactions
        removed_credit = 0
        failed_credit = 0
        
        for t in credit_to_remove:
            try:
                success = db.delete_transaction('credit', t.get('id'), user_id)
                if success:
                    removed_credit += 1
                    print(f'   ✅ Removed credit: "{t.get("description")}" (ID: {t.get("id")}) - {t.get("date")}')
                else:
                    failed_credit += 1
                    print(f'   ❌ Failed credit: "{t.get("description")}" (ID: {t.get("id")})')
            except Exception as e:
                failed_credit += 1
                print(f'   ❌ Error removing credit transaction {t.get("id")}: {e}')
        
        print()
        print(f'📊 CLEANUP SUMMARY:')
        print(f'   🗑️  Successfully removed: {removed_checking + removed_credit}')
        print(f'   ❌ Failed to remove: {failed_checking + failed_credit}')
        print(f'   🏦 Checking removed: {removed_checking}/{len(checking_to_remove)}')
        print(f'   💳 Credit removed: {removed_credit}/{len(credit_to_remove)}')
        print(f'   💾 Backup file: {backup_file}')
        print()
        
        # Final verification
        print(f'🔍 Verifying cleanup...')
        remaining_checking = await db.get_checking_transactions(user_id)
        remaining_credit = await db.get_credit_transactions(user_id)
        
        # Check for any remaining miscellaneous transactions
        remaining_misc_checking = [t for t in remaining_checking if t.get('description') in ['Miscellaneous Sale', 'Miscellaneous Expense']]
        remaining_misc_credit = [t for t in remaining_credit if t.get('description') in ['Miscellaneous Sale', 'Miscellaneous Expense']]
        
        total_remaining_misc = len(remaining_misc_checking) + len(remaining_misc_credit)
        
        print(f'📊 Final database state:')
        print(f'   🏦 Total checking transactions: {len(remaining_checking)}')
        print(f'   💳 Total credit transactions: {len(remaining_credit)}')
        print(f'   📈 Total transactions: {len(remaining_checking) + len(remaining_credit)}')
        print(f'   🗑️  Remaining miscellaneous: {total_remaining_misc}')
        
        if total_remaining_misc == 0:
            print()
            print('🎉 SUCCESS! All "Miscellaneous Sale" and "Miscellaneous Expense" transactions have been removed!')
            print('✅ Database is now clean')
        else:
            print()
            print(f'⚠️  WARNING: {total_remaining_misc} miscellaneous transactions still remain:')
            for t in remaining_misc_checking + remaining_misc_credit:
                account_type = 'checking' if t in remaining_misc_checking else 'credit'
                print(f'   - {account_type}: "{t.get("description")}" (ID: {t.get("id")})')
        
    except Exception as e:
        print(f'❌ Error during cleanup: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(remove_all_miscellaneous()) 