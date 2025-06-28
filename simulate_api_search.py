#!/usr/bin/env python3
"""
Simulate the exact same API search logic that frontend uses
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append('.')
from app.services.supabase_service import SupabaseService

async def simulate_api_search():
    db = SupabaseService()
    user_id = '550e8400-e29b-41d4-a716-446655440000'
    
    print('🔍 SIMULATING EXACT API SEARCH LOGIC')
    print('=' * 40)
    print('🎯 Using same search parameters as frontend API calls')
    print()
    
    try:
        # Simulate the exact API search for "misc" in May 2025 as seen in logs
        print('📊 Simulating API search for "misc" in May 2025...')
        
        # This mimics the API call: GET /api/transactions?search=misc&month=2025-05
        may_checking_misc = await db.get_checking_transactions(
            user_id=user_id,
            start_date=None,
            end_date=None,
            month='2025-05',
            search='misc'
        )
        
        may_credit_misc = await db.get_credit_transactions(
            user_id=user_id,
            start_date=None,
            end_date=None,
            month='2025-05',
            search='misc'
        )
        
        total_may_misc = len(may_checking_misc) + len(may_credit_misc)
        
        print(f'🎯 May 2025 "misc" search results:')
        print(f'   🏦 Checking: {len(may_checking_misc)}')
        print(f'   💳 Credit: {len(may_credit_misc)}')
        print(f'   📈 Total: {total_may_misc}')
        print()
        
        if total_may_misc > 0:
            print(f'🔍 Sample transactions found:')
            
            all_misc = may_checking_misc + may_credit_misc
            
            # Show unique descriptions
            unique_descriptions = set(t.get('description', '') for t in all_misc)
            print(f'📋 Unique descriptions containing "misc":')
            for desc in sorted(unique_descriptions):
                count = len([t for t in all_misc if t.get('description') == desc])
                print(f'   - "{desc}": {count} transactions')
            
            print()
            print(f'📝 Sample transaction details:')
            for i, t in enumerate(all_misc[:10], 1):  # Show first 10
                account_type = 'checking' if t in may_checking_misc else 'credit'
                print(f'  {i:2d}. [{account_type}] "{t.get("description")}" | {t.get("date")} | ${t.get("amount")} | ID: {t.get("id")}')
            
            if len(all_misc) > 10:
                print(f'      ... and {len(all_misc) - 10} more')
            
            # Check for exact "Miscellaneous Sale/Expense" matches
            exact_matches = [t for t in all_misc if t.get('description') in ['Miscellaneous Sale', 'Miscellaneous Expense']]
            
            print(f'\n🚨 EXACT "Miscellaneous Sale/Expense" matches: {len(exact_matches)}')
            
            if len(exact_matches) > 0:
                print(f'⚠️  Found {len(exact_matches)} exact matches that need removal!')
                for t in exact_matches:
                    account_type = 'checking' if t in may_checking_misc else 'credit'
                    print(f'   - [{account_type}] "{t.get("description")}" | {t.get("date")} | ID: {t.get("id")}')
            else:
                print(f'✅ No exact "Miscellaneous Sale/Expense" matches (these might be other transactions containing "misc")')
        
        # Also test with other months to see where the misc transactions are
        print(f'\n📅 Testing other months...')
        
        months_to_test = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-06', '2025-07']
        
        for month in months_to_test:
            month_checking = await db.get_checking_transactions(
                user_id=user_id,
                start_date=None,
                end_date=None,
                month=month,
                search='misc'
            )
            month_credit = await db.get_credit_transactions(
                user_id=user_id,
                start_date=None,
                end_date=None,
                month=month,
                search='misc'
            )
            
            month_total = len(month_checking) + len(month_credit)
            if month_total > 0:
                print(f'   {month}: {month_total} transactions ({len(month_checking)} checking, {len(month_credit)} credit)')
        
        # Test searching entire database without month filter
        print(f'\n🌐 Testing entire database search...')
        
        all_checking_misc = await db.get_checking_transactions(
            user_id=user_id,
            search='misc'
        )
        all_credit_misc = await db.get_credit_transactions(
            user_id=user_id,
            search='misc'
        )
        
        total_all_misc = len(all_checking_misc) + len(all_credit_misc)
        
        print(f'🎯 Entire database "misc" search results:')
        print(f'   🏦 Checking: {len(all_checking_misc)}')
        print(f'   💳 Credit: {len(all_credit_misc)}')
        print(f'   📈 Total: {total_all_misc}')
        
        print(f'\n📊 SEARCH COMPARISON:')
        print(f'   May 2025 only: {total_may_misc} transactions')
        print(f'   Entire database: {total_all_misc} transactions')
        
    except Exception as e:
        print(f'❌ Error during API simulation: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simulate_api_search()) 