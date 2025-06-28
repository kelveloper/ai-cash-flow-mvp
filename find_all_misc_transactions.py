#!/usr/bin/env python3
"""
Find ALL transactions containing "misc" anywhere in description across entire database
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

async def find_all_misc_transactions():
    db = SupabaseService()
    user_id = '550e8400-e29b-41d4-a716-446655440000'
    
    print('🔍 COMPREHENSIVE SEARCH FOR ALL TRANSACTIONS CONTAINING "MISC"')
    print('=' * 65)
    print('🎯 Searching entire database for ANY transaction containing "misc"')
    print()
    
    try:
        # Get ALL transactions from entire database (no date filtering)
        print('📊 Getting all transactions from entire database...')
        
        all_checking = await db.get_checking_transactions(user_id)
        all_credit = await db.get_credit_transactions(user_id)
        
        print(f'Total database: {len(all_checking)} checking + {len(all_credit)} credit = {len(all_checking) + len(all_credit)} transactions')
        print()
        
        # Find ALL transactions containing "misc" (case-insensitive)
        misc_checking = [t for t in all_checking if 'misc' in t.get('description', '').lower()]
        misc_credit = [t for t in all_credit if 'misc' in t.get('description', '').lower()]
        
        total_misc = len(misc_checking) + len(misc_credit)
        
        print(f'🎯 FOUND {total_misc} transactions containing "misc":')
        print(f'   🏦 Checking: {len(misc_checking)}')
        print(f'   💳 Credit: {len(misc_credit)}')
        print()
        
        if total_misc == 0:
            print('✅ No transactions containing "misc" found!')
            return
        
        # Group by exact description to see what we're dealing with
        all_misc = misc_checking + misc_credit
        descriptions = {}
        
        for t in all_misc:
            desc = t.get('description', '')
            if desc not in descriptions:
                descriptions[desc] = {'checking': 0, 'credit': 0, 'transactions': []}
            
            if t in misc_checking:
                descriptions[desc]['checking'] += 1
            else:
                descriptions[desc]['credit'] += 1
            
            descriptions[desc]['transactions'].append(t)
        
        print(f'📋 BREAKDOWN BY DESCRIPTION:')
        print(f'=' * 50)
        
        for desc, data in sorted(descriptions.items()):
            total_count = data['checking'] + data['credit']
            print(f'"{desc}": {total_count} total ({data["checking"]} checking, {data["credit"]} credit)')
            
            # Show sample transaction IDs and dates
            sample_transactions = data['transactions'][:3]  # Show first 3
            for t in sample_transactions:
                account_type = 'checking' if t in misc_checking else 'credit'
                print(f'   - [{account_type}] ID: {t.get("id")} | Date: {t.get("date")} | Amount: {t.get("amount")}')
            
            if len(data['transactions']) > 3:
                print(f'   ... and {len(data["transactions"]) - 3} more')
            print()
        
        # Find exact "Miscellaneous Sale" and "Miscellaneous Expense" matches
        exact_matches = []
        for desc in descriptions.keys():
            if desc in ['Miscellaneous Sale', 'Miscellaneous Expense']:
                exact_matches.extend(descriptions[desc]['transactions'])
        
        print(f'🚨 EXACT "Miscellaneous Sale/Expense" matches: {len(exact_matches)}')
        
        if len(exact_matches) > 0:
            print(f'⚠️  These need to be removed!')
            
            # Create removal script for exact matches
            print(f'\n📝 Creating removal list...')
            
            checking_to_remove = [t for t in exact_matches if t in misc_checking]
            credit_to_remove = [t for t in exact_matches if t in misc_credit]
            
            removal_data = {
                'timestamp': datetime.now().isoformat(),
                'total_to_remove': len(exact_matches),
                'checking_count': len(checking_to_remove),
                'credit_count': len(credit_to_remove),
                'checking_transactions': checking_to_remove,
                'credit_transactions': credit_to_remove
            }
            
            removal_file = f"misc_removal_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(removal_file, 'w') as f:
                json.dump(removal_data, f, indent=2, default=str)
            
            print(f'💾 Removal list saved to: {removal_file}')
            print(f'🔥 Ready to remove {len(exact_matches)} exact matches!')
        else:
            print(f'✅ No exact "Miscellaneous Sale/Expense" matches found')
        
        # Show monthly distribution
        print(f'\n📅 MONTHLY DISTRIBUTION:')
        print(f'=' * 30)
        
        monthly_counts = {}
        for t in all_misc:
            date = t.get('date', '')
            if date:
                month = date[:7]  # YYYY-MM format
                if month not in monthly_counts:
                    monthly_counts[month] = 0
                monthly_counts[month] += 1
        
        for month in sorted(monthly_counts.keys()):
            print(f'{month}: {monthly_counts[month]} transactions')
        
        print(f'\n📊 SUMMARY:')
        print(f'   🔍 Total database transactions: {len(all_checking) + len(all_credit)}')
        print(f'   📝 Transactions containing "misc": {total_misc}')
        print(f'   🎯 Exact "Sale/Expense" matches: {len(exact_matches)}')
        print(f'   📋 Unique descriptions found: {len(descriptions)}')
        
        if total_misc > len(exact_matches):
            other_misc = total_misc - len(exact_matches)
            print(f'   💡 Other "misc" transactions: {other_misc} (not exact matches)')
        
    except Exception as e:
        print(f'❌ Error during search: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_all_misc_transactions()) 