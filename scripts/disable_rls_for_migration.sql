-- Temporarily disable RLS for migration
-- Run this in your Supabase SQL Editor BEFORE running the migration

-- Disable RLS on all tables
ALTER TABLE public.checking_transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.account_summaries DISABLE ROW LEVEL SECURITY;

-- Confirm RLS is disabled
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('checking_transactions', 'credit_transactions', 'account_summaries');

-- This should show rowsecurity = false for all tables 