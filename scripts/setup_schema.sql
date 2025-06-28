-- AI Cash Flow MVP - Supabase Schema Setup
-- Copy and paste this entire script into your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create checking transactions table
CREATE TABLE public.checking_transactions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID NOT NULL,
  date DATE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  description TEXT NOT NULL,
  category VARCHAR(50),
  type VARCHAR(20) CHECK (type IN ('income', 'expense')) NOT NULL,
  status VARCHAR(20) DEFAULT 'completed',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create credit transactions table
CREATE TABLE public.credit_transactions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID NOT NULL,
  date DATE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  description TEXT NOT NULL,
  category VARCHAR(50),
  type VARCHAR(20) CHECK (type IN ('income', 'expense')) NOT NULL,
  status VARCHAR(20) DEFAULT 'completed',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create account summaries table
CREATE TABLE public.account_summaries (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID NOT NULL,
  account_type VARCHAR(20) CHECK (account_type IN ('checking', 'credit')) NOT NULL,
  current_balance DECIMAL(12,2) NOT NULL DEFAULT 0,
  available_balance DECIMAL(12,2),
  credit_limit DECIMAL(12,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_checking_user_date ON public.checking_transactions(user_id, date DESC);
CREATE INDEX idx_credit_user_date ON public.credit_transactions(user_id, date DESC);
CREATE INDEX idx_account_summaries_user_type ON public.account_summaries(user_id, account_type);

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated; 