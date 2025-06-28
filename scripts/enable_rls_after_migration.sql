-- Re-enable RLS after migration
-- Run this in your Supabase SQL Editor AFTER the migration is complete

-- Re-enable RLS on all tables
ALTER TABLE public.checking_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.account_summaries ENABLE ROW LEVEL SECURITY;

-- Confirm RLS is enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('checking_transactions', 'credit_transactions', 'account_summaries');

-- This should show rowsecurity = true for all tables 