-- Temporarily remove foreign key constraints for migration
-- Run this in Supabase SQL Editor before migration

-- Drop foreign key constraints
ALTER TABLE public.checking_transactions DROP CONSTRAINT IF EXISTS checking_transactions_user_id_fkey;
ALTER TABLE public.credit_transactions DROP CONSTRAINT IF EXISTS credit_transactions_user_id_fkey;
ALTER TABLE public.account_summaries DROP CONSTRAINT IF EXISTS account_summaries_user_id_fkey;

-- Also drop the users table reference if it exists
DROP TABLE IF EXISTS public.users CASCADE;

-- Confirm constraints are removed
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public' 
    AND tc.table_name IN ('checking_transactions', 'credit_transactions', 'account_summaries')
    AND tc.constraint_type = 'FOREIGN KEY'; 