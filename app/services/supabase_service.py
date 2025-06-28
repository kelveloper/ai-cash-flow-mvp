"""
Supabase service for AI Cash Flow MVP
Handles all database operations using Supabase PostgreSQL
"""

import os
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        # Try both possible environment variable names
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_KEY) environment variables are required")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase service initialized successfully")
    
    async def get_checking_transactions(
        self, 
        user_id: str = "550e8400-e29b-41d4-a716-446655440000",  # Demo user ID
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        month: Optional[str] = None, 
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """Get checking account transactions with filtering"""
        try:
            query = self.client.table('checking_transactions').select("*").eq('user_id', user_id)
            
            # Apply date filters - prioritize start_date/end_date over month
            if start_date and end_date:
                query = query.gte('date', start_date.isoformat()).lte('date', end_date.isoformat())
            elif month:
                start_date_str = f"{month}-01"
                # Handle month end date properly
                year, month_num = month.split('-')
                if month_num in ['01', '03', '05', '07', '08', '10', '12']:
                    end_date_str = f"{month}-31"
                elif month_num in ['04', '06', '09', '11']:
                    end_date_str = f"{month}-30"
                else:  # February
                    end_date_str = f"{month}-28"  # Simplified, doesn't handle leap years
                
                query = query.gte('date', start_date_str).lte('date', end_date_str)
            
            if category:
                query = query.eq('category', category)
            
            if status:
                query = query.eq('status', status)
            
            if search:
                query = query.ilike('description', f'%{search}%')
            
            if limit and limit > 0:
                query = query.limit(limit)
                logger.info(f"Applied limit of {limit} to checking transactions query")
            else:
                logger.info("No limit applied to checking transactions query - fetching all records")
            
            # Order by date descending
            query = query.order('date', desc=True)
            
            result = query.execute()
            
            # Convert date objects to strings for JSON serialization
            transactions = []
            for transaction in result.data:
                # Convert date to string if it's a date object
                if isinstance(transaction.get('date'), date):
                    transaction['date'] = transaction['date'].isoformat()
                transactions.append(transaction)
            
            logger.info(f"Retrieved {len(transactions)} checking transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"Error fetching checking transactions: {e}")
            return []
    
    async def get_credit_transactions(
        self, 
        user_id: str = "550e8400-e29b-41d4-a716-446655440000",  # Demo user ID
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        month: Optional[str] = None, 
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """Get credit account transactions with filtering"""
        try:
            query = self.client.table('credit_transactions').select("*").eq('user_id', user_id)
            
            # Apply date filters - prioritize start_date/end_date over month
            if start_date and end_date:
                query = query.gte('date', start_date.isoformat()).lte('date', end_date.isoformat())
            elif month:
                start_date_str = f"{month}-01"
                # Handle month end date properly
                year, month_num = month.split('-')
                if month_num in ['01', '03', '05', '07', '08', '10', '12']:
                    end_date_str = f"{month}-31"
                elif month_num in ['04', '06', '09', '11']:
                    end_date_str = f"{month}-30"
                else:  # February
                    end_date_str = f"{month}-28"  # Simplified, doesn't handle leap years
                
                query = query.gte('date', start_date_str).lte('date', end_date_str)
            
            if category:
                query = query.eq('category', category)
            
            if status:
                query = query.eq('status', status)
            
            if search:
                query = query.ilike('description', f'%{search}%')
            
            if limit and limit > 0:
                query = query.limit(limit)
                logger.info(f"Applied limit of {limit} to credit transactions query")
            else:
                logger.info("No limit applied to credit transactions query - fetching all records")
            
            # Order by date descending
            query = query.order('date', desc=True)
            
            result = query.execute()
            
            # Convert date objects to strings for JSON serialization
            transactions = []
            for transaction in result.data:
                # Convert date to string if it's a date object
                if isinstance(transaction.get('date'), date):
                    transaction['date'] = transaction['date'].isoformat()
                transactions.append(transaction)
            
            logger.info(f"Retrieved {len(transactions)} credit transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"Error fetching credit transactions: {e}")
            return []
    
    async def get_account_summaries(
        self, 
        user_id: str = "550e8400-e29b-41d4-a716-446655440000"  # Demo user ID
    ) -> List[Dict[str, Any]]:
        """Get account summaries for user"""
        try:
            result = self.client.table('account_summaries').select("*").eq('user_id', user_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching account summaries: {e}")
            return []

    async def update_checking_transaction_category(
        self,
        transaction_id: str,
        category: str
    ) -> bool:
        """Update the category of a checking transaction"""
        try:
            result = self.client.table('checking_transactions').update({
                'category': category
            }).eq('id', transaction_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating checking transaction category: {e}")
            return False

    async def update_credit_transaction_category(
        self,
        transaction_id: str,
        category: str
    ) -> bool:
        """Update the category of a credit transaction"""
        try:
            result = self.client.table('credit_transactions').update({
                'category': category
            }).eq('id', transaction_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating credit transaction category: {e}")
            return False

    def get_account_summary(
        self, 
        user_id: str = "550e8400-e29b-41d4-a716-446655440000"  # Demo user ID
    ) -> Dict[str, Any]:
        """Get account summary for both checking and credit accounts"""
        try:
            result = self.client.table('account_summaries').select("*").eq('user_id', user_id).execute()
            
            summary = {
                "current_balance": 0,
                "checking_balance": 0,
                "credit_balance": 0,
                "credit_limit": 5000,
                "available_credit": 5000
            }
            
            for account in result.data:
                if account['account_type'] == 'checking':
                    summary['checking_balance'] = float(account['current_balance'])
                    summary['current_balance'] = float(account['current_balance'])  # Main balance is checking
                elif account['account_type'] == 'credit':
                    summary['credit_balance'] = float(account['current_balance'])
                    summary['credit_limit'] = float(account.get('credit_limit', 5000))
                    summary['available_credit'] = summary['credit_limit'] - summary['credit_balance']
            
            logger.info("Retrieved account summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error fetching account summary: {e}")
            return {
                "current_balance": 0,
                "checking_balance": 0,
                "credit_balance": 0,
                "credit_limit": 5000,
                "available_credit": 5000
            }
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get unique categories from both transaction tables"""
        try:
            # Get categories from checking transactions
            checking_result = self.client.table('checking_transactions').select('category').execute()
            checking_categories = set()
            for row in checking_result.data:
                if row['category']:
                    checking_categories.add(row['category'])
            
            # Get categories from credit transactions
            credit_result = self.client.table('credit_transactions').select('category').execute()
            credit_categories = set()
            for row in credit_result.data:
                if row['category']:
                    credit_categories.add(row['category'])
            
            # Combine and format categories
            all_categories = checking_categories.union(credit_categories)
            categories = [{"name": cat} for cat in sorted(all_categories)]
            
            logger.info(f"Retrieved {len(categories)} categories")
            return categories
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    def add_transaction(
        self, 
        account_type: str, 
        transaction_data: Dict[str, Any],
        user_id: str = "550e8400-e29b-41d4-a716-446655440000"  # Demo user ID
    ) -> Dict[str, Any]:
        """Add a new transaction"""
        try:
            # Add user_id to transaction data
            transaction_data['user_id'] = user_id
            
            # Choose the correct table
            table_name = f"{account_type}_transactions"
            
            result = self.client.table(table_name).insert(transaction_data).execute()
            
            # Update account summary
            self.update_account_summary(user_id, account_type)
            
            logger.info(f"Added new {account_type} transaction")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            raise
    
    def update_transaction(
        self, 
        account_type: str, 
        transaction_id: str, 
        transaction_data: Dict[str, Any],
        user_id: str = "550e8400-e29b-41d4-a716-446655440000"  # Demo user ID
    ) -> Dict[str, Any]:
        """Update an existing transaction"""
        try:
            table_name = f"{account_type}_transactions"
            
            result = self.client.table(table_name).update(transaction_data).eq('id', transaction_id).eq('user_id', user_id).execute()
            
            # Update account summary
            self.update_account_summary(user_id, account_type)
            
            logger.info(f"Updated {account_type} transaction {transaction_id}")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            raise
    
    def delete_transaction(
        self, 
        account_type: str, 
        transaction_id: str,
        user_id: str = "550e8400-e29b-41d4-a716-446655440000"  # Demo user ID
    ) -> bool:
        """Delete a transaction"""
        try:
            table_name = f"{account_type}_transactions"
            
            result = self.client.table(table_name).delete().eq('id', transaction_id).eq('user_id', user_id).execute()
            
            # Update account summary
            self.update_account_summary(user_id, account_type)
            
            logger.info(f"Deleted {account_type} transaction {transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            return False
    
    def update_account_summary(
        self, 
        user_id: str, 
        account_type: str
    ) -> None:
        """Update account summary after transaction changes"""
        try:
            # Use the database function to calculate and update balance
            self.client.rpc('update_account_summary', {
                'p_user_id': user_id,
                'p_account_type': account_type
            }).execute()
            
            logger.info(f"Updated {account_type} account summary for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating account summary: {e}")
    
    def get_transaction_stats(
        self, 
        account_type: str,
        user_id: str = "550e8400-e29b-41d4-a716-446655440000"  # Demo user ID
    ) -> Dict[str, Any]:
        """Get transaction statistics for an account"""
        try:
            table_name = f"{account_type}_transactions"
            
            # Get all transactions for the user
            result = self.client.table(table_name).select("amount, type, category").eq('user_id', user_id).execute()
            
            total_income = 0
            total_expenses = 0
            category_totals = {}
            
            for transaction in result.data:
                amount = float(transaction['amount'])
                category = transaction.get('category', 'uncategorized')
                
                if transaction['type'] == 'income':
                    total_income += amount
                else:
                    total_expenses += amount
                
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount
            
            stats = {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_amount": total_income - total_expenses,
                "category_breakdown": category_totals,
                "transaction_count": len(result.data)
            }
            
            logger.info(f"Generated stats for {account_type} account")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating transaction stats: {e}")
            return {
                "total_income": 0,
                "total_expenses": 0,
                "net_amount": 0,
                "category_breakdown": {},
                "transaction_count": 0
            } 