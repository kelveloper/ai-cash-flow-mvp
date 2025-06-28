-- Supabase Database Schema for AI Cash Flow MVP
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table (if not already exists from auth)
CREATE TABLE IF NOT EXISTS public.users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create checking transactions table
CREATE TABLE public.checking_transactions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  description TEXT NOT NULL,
  category VARCHAR(50),
  type VARCHAR(20) CHECK (type IN ('income', 'expense')) NOT NULL,
  status VARCHAR(20) DEFAULT 'completed',
  ml_category VARCHAR(50),
  confidence_score DECIMAL(3,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create credit transactions table
CREATE TABLE public.credit_transactions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  description TEXT NOT NULL,
  category VARCHAR(50),
  type VARCHAR(20) CHECK (type IN ('income', 'expense')) NOT NULL,
  status VARCHAR(20) DEFAULT 'completed',
  ml_category VARCHAR(50),
  confidence_score DECIMAL(3,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create account summaries table
CREATE TABLE public.account_summaries (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  account_type VARCHAR(20) CHECK (account_type IN ('checking', 'credit')) NOT NULL,
  current_balance DECIMAL(12,2) NOT NULL DEFAULT 0,
  available_balance DECIMAL(12,2),
  credit_limit DECIMAL(12,2),
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_checking_user_date ON public.checking_transactions(user_id, date DESC);
CREATE INDEX idx_checking_date ON public.checking_transactions(date DESC);
CREATE INDEX idx_checking_category ON public.checking_transactions(category);
CREATE INDEX idx_checking_type ON public.checking_transactions(type);
CREATE INDEX idx_checking_status ON public.checking_transactions(status);

CREATE INDEX idx_credit_user_date ON public.credit_transactions(user_id, date DESC);
CREATE INDEX idx_credit_date ON public.credit_transactions(date DESC);
CREATE INDEX idx_credit_category ON public.credit_transactions(category);
CREATE INDEX idx_credit_type ON public.credit_transactions(type);
CREATE INDEX idx_credit_status ON public.credit_transactions(status);

CREATE INDEX idx_account_summaries_user_type ON public.account_summaries(user_id, account_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to update updated_at automatically
CREATE TRIGGER update_checking_transactions_updated_at 
  BEFORE UPDATE ON public.checking_transactions 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credit_transactions_updated_at 
  BEFORE UPDATE ON public.credit_transactions 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_account_summaries_updated_at 
  BEFORE UPDATE ON public.account_summaries 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checking_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.account_summaries ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Checking transactions policies
CREATE POLICY "Users can view own checking transactions" ON public.checking_transactions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own checking transactions" ON public.checking_transactions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own checking transactions" ON public.checking_transactions
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own checking transactions" ON public.checking_transactions
  FOR DELETE USING (auth.uid() = user_id);

-- Credit transactions policies
CREATE POLICY "Users can view own credit transactions" ON public.credit_transactions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own credit transactions" ON public.credit_transactions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own credit transactions" ON public.credit_transactions
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own credit transactions" ON public.credit_transactions
  FOR DELETE USING (auth.uid() = user_id);

-- Account summaries policies
CREATE POLICY "Users can view own account summaries" ON public.account_summaries
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own account summaries" ON public.account_summaries
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own account summaries" ON public.account_summaries
  FOR UPDATE USING (auth.uid() = user_id);

-- Create a function to calculate account balances
CREATE OR REPLACE FUNCTION calculate_account_balance(p_user_id UUID, p_account_type TEXT)
RETURNS DECIMAL AS $$
DECLARE
  balance DECIMAL(12,2) := 0;
BEGIN
  IF p_account_type = 'checking' THEN
    SELECT COALESCE(
      SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END), 0
    ) INTO balance
    FROM public.checking_transactions 
    WHERE user_id = p_user_id;
  ELSIF p_account_type = 'credit' THEN
    SELECT COALESCE(
      SUM(CASE WHEN type = 'expense' THEN amount ELSE -amount END), 0
    ) INTO balance
    FROM public.credit_transactions 
    WHERE user_id = p_user_id;
  END IF;
  
  RETURN balance;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to update account summaries
CREATE OR REPLACE FUNCTION update_account_summary(p_user_id UUID, p_account_type TEXT)
RETURNS VOID AS $$
DECLARE
  new_balance DECIMAL(12,2);
BEGIN
  new_balance := calculate_account_balance(p_user_id, p_account_type);
  
  INSERT INTO public.account_summaries (user_id, account_type, current_balance, last_updated)
  VALUES (p_user_id, p_account_type, new_balance, NOW())
  ON CONFLICT (user_id, account_type) 
  DO UPDATE SET 
    current_balance = new_balance,
    last_updated = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add unique constraint for user_id + account_type
ALTER TABLE public.account_summaries 
ADD CONSTRAINT unique_user_account_type UNIQUE (user_id, account_type);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated; 