#!/usr/bin/env python3
"""
Remove ALL 2000 "Miscellaneous Sale" and "Miscellaneous Expense" transactions from entire database
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

async def remove_all_2000_misc_transactions():
    db = SupabaseService()
    user_id = '550e8400-e29b-41d4-a716-446655440000'
    
    print('🚨 COMPLETE DATABASE CLEANUP - REMOVING ALL MISCELLANEOUS TRANSACTIONS')
    print('=' * 75)
    print('🎯 Target: ALL "Miscellaneous Sale" and "Miscellaneous Expense" transactions')
    print('📅 Scope: ENTIRE DATABASE (all dates, all months)')
    print()
    
    try:
        # Use search method to find ALL miscellaneous transactions
        print('🔍 Finding ALL miscellaneous transactions using search method...')
        
        # Search for all transactions containing "misc" 
        all_checking_misc = await db.get_checking_transactions(
            user_id=user_id,
            search='misc'
        )
        all_credit_misc = await db.get_credit_transactions(
            user_id=user_id,
            search='misc'
        )
        
        total_transactions = len(all_checking_misc) + len(all_credit_misc)
        
        print(f'📊 Found transactions to remove:')
        print(f'   🏦 Checking: {len(all_checking_misc)}')
        print(f'   💳 Credit: {len(all_credit_misc)}')
        print(f'   📈 TOTAL: {total_transactions}')
        print()
        
        if total_transactions == 0:
            print('✅ No miscellaneous transactions found!')
            return
        
        # Verify these are all exact matches
        all_misc = all_checking_misc + all_credit_misc
        unique_descriptions = set(t.get('description', '') for t in all_misc)
        
        print(f'📋 Unique descriptions found:')
        for desc in sorted(unique_descriptions):
            count = len([t for t in all_misc if t.get('description') == desc])
            print(f'   - "{desc}": {count} transactions')
        
        # Confirm these are all exact "Miscellaneous Sale/Expense" matches
        exact_matches = [t for t in all_misc if t.get('description') in ['Miscellaneous Sale', 'Miscellaneous Expense']]
        
        print(f'\n🎯 EXACT "Miscellaneous Sale/Expense" matches: {len(exact_matches)} / {total_transactions}')
        
        if len(exact_matches) != total_transactions:
            print(f'⚠️  WARNING: Not all transactions are exact matches!')
            print(f'   Exact matches: {len(exact_matches)}')
            print(f'   Total found: {total_transactions}')
            print(f'   Difference: {total_transactions - len(exact_matches)}')
            
            # Show non-exact matches
            non_exact = [t for t in all_misc if t not in exact_matches]
            if non_exact:
                print(f'\n📝 Non-exact matches:')
                for t in non_exact[:10]:  # Show first 10
                    print(f'   - "{t.get("description")}"')
            
            response = input('\n🤔 Continue with removal of ALL found transactions? (yes/no): ').lower().strip()
            if response not in ['yes', 'y']:
                print('❌ Operation cancelled by user')
                return
        
        # Show monthly breakdown
        monthly_counts = {}
        for t in all_misc:
            date = t.get('date', '')
            if date:
                month = date[:7]  # YYYY-MM format
                if month not in monthly_counts:
                    monthly_counts[month] = 0
                monthly_counts[month] += 1
        
        print(f'\n📅 MONTHLY BREAKDOWN:')
        for month in sorted(monthly_counts.keys()):
            print(f'   {month}: {monthly_counts[month]} transactions')
        
        # Create comprehensive backup
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'cleanup_scope': 'entire_database_all_misc',
            'total_removed': total_transactions,
            'checking_count': len(all_checking_misc),
            'credit_count': len(all_credit_misc),
            'monthly_breakdown': monthly_counts,
            'unique_descriptions': list(unique_descriptions),
            'checking_transactions_removed': all_checking_misc,
            'credit_transactions_removed': all_credit_misc
        }
        
        backup_file = f"complete_database_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        print(f'💾 COMPLETE backup saved to: {backup_file}')
        print()
        
        # Final confirmation
        print(f'🚨 CRITICAL WARNING: This will delete ALL {total_transactions} transactions from your database!')
        print(f'🗃️  This will essentially EMPTY your entire transaction database!')
        print(f'💾 Backup file: {backup_file}')
        print()
        response = input('🤔 Are you ABSOLUTELY SURE you want to proceed? (type "DELETE ALL" to confirm): ').strip()
        
        if response != 'DELETE ALL':
            print('❌ Operation cancelled - confirmation not received')
            return
        
        print()
        print(f'🗑️  Starting deletion of {total_transactions} transactions...')
        print(f'⏳ This may take a while...')
        print()
        
        # Remove checking transactions
        removed_checking = 0
        failed_checking = 0
        
        print(f'🏦 Removing {len(all_checking_misc)} checking transactions...')
        for i, t in enumerate(all_checking_misc, 1):
            try:
                success = db.delete_transaction('checking', t.get('id'), user_id)
                if success:
                    removed_checking += 1
                    if i % 50 == 0:  # Progress update every 50 deletions
                        print(f'   ✅ Progress: {i}/{len(all_checking_misc)} checking transactions')
                else:
                    failed_checking += 1
                    print(f'   ❌ Failed checking: ID {t.get("id")}')
            except Exception as e:
                failed_checking += 1
                print(f'   ❌ Error removing checking transaction {t.get("id")}: {e}')
        
        print(f'✅ Checking transactions complete: {removed_checking} removed, {failed_checking} failed')
        print()
        
        # Remove credit transactions
        removed_credit = 0
        failed_credit = 0
        
        print(f'💳 Removing {len(all_credit_misc)} credit transactions...')
        for i, t in enumerate(all_credit_misc, 1):
            try:
                success = db.delete_transaction('credit', t.get('id'), user_id)
                if success:
                    removed_credit += 1
                    if i % 50 == 0:  # Progress update every 50 deletions
                        print(f'   ✅ Progress: {i}/{len(all_credit_misc)} credit transactions')
                else:
                    failed_credit += 1
                    print(f'   ❌ Failed credit: ID {t.get("id")}')
            except Exception as e:
                failed_credit += 1
                print(f'   ❌ Error removing credit transaction {t.get("id")}: {e}')
        
        print(f'✅ Credit transactions complete: {removed_credit} removed, {failed_credit} failed')
        print()
        
        total_removed = removed_checking + removed_credit
        total_failed = failed_checking + failed_credit
        
        print(f'📊 FINAL CLEANUP SUMMARY:')
        print(f'   🗑️  Successfully removed: {total_removed}/{total_transactions}')
        print(f'   ❌ Failed to remove: {total_failed}')
        print(f'   🏦 Checking: {removed_checking} removed, {failed_checking} failed')
        print(f'   💳 Credit: {removed_credit} removed, {failed_credit} failed')
        print(f'   💾 Backup file: {backup_file}')
        print()
        
        # Final verification
        print(f'🔍 Verifying complete cleanup...')
        
        remaining_checking = await db.get_checking_transactions(user_id)
        remaining_credit = await db.get_credit_transactions(user_id)
        
        remaining_total = len(remaining_checking) + len(remaining_credit)
        
        print(f'📊 Final database state:')
        print(f'   🏦 Remaining checking transactions: {len(remaining_checking)}')
        print(f'   💳 Remaining credit transactions: {len(remaining_credit)}')
        print(f'   📈 Total remaining transactions: {remaining_total}')
        
        if remaining_total == 0:
            print()
            print('🎉 SUCCESS! ALL transactions have been removed from the database!')
            print('✅ Database is now completely clean')
            print('💡 You can now import clean transaction data without any miscellaneous entries')
        else:
            print()
            print(f'📊 Database cleanup complete with {remaining_total} transactions remaining')
            
            # Check if any remaining are miscellaneous
            remaining_misc_checking = await db.get_checking_transactions(user_id, search='misc')
            remaining_misc_credit = await db.get_credit_transactions(user_id, search='misc')
            remaining_misc_total = len(remaining_misc_checking) + len(remaining_misc_credit)
            
            print(f'🔍 Remaining miscellaneous transactions: {remaining_misc_total}')
            
            if remaining_misc_total == 0:
                print('✅ No miscellaneous transactions remain!')
            else:
                print(f'⚠️  {remaining_misc_total} miscellaneous transactions still exist')
        
    except Exception as e:
        print(f'❌ Error during cleanup: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(remove_all_2000_misc_transactions()) 