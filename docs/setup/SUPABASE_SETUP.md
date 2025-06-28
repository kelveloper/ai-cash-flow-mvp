# Supabase Setup Guide for AI Cash Flow MVP

This guide will help you migrate from SQLite to Supabase for better performance and scalability.

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login and create a new project
3. Choose a project name: `ai-cash-flow-mvp`
4. Set a strong database password
5. Choose a region close to your users
6. Wait for project creation (2-3 minutes)

## Step 2: Get Your Credentials

1. Go to your project dashboard
2. Click on **Settings** → **API**
3. Copy the following values:
   - **Project URL** (starts with `https://`)
   - **Anon public key** (starts with `eyJ`)
   - **Service role key** (starts with `eyJ`) - **Keep this secret!**

## Step 3: Set Up Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `scripts/supabase_schema.sql`
3. Paste it into the SQL Editor and click **Run**
4. This will create:
   - `checking_transactions` table
   - `credit_transactions` table
   - `account_summaries` table
   - Proper indexes for performance
   - Row Level Security (RLS) policies
   - Helper functions for balance calculations

## Step 4: Configure Environment Variables

1. Copy `supabase.env.example` to `.env` (or update your existing `.env`)
2. Replace the placeholder values with your actual Supabase credentials:

```bash
# Replace these with your actual values
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Step 5: Migrate Your Data

1. Make sure your environment variables are set:
   ```bash
   export SUPABASE_URL="https://your-project-id.supabase.co"
   export SUPABASE_SERVICE_KEY="your-service-key-here"
   ```

2. Run the migration script:
   ```bash
   python scripts/migrate_to_supabase.py
   ```

3. The script will:
   - Load data from `data/all_transactions.csv`
   - Separate transactions by account type
   - Insert data in batches (1000 records at a time)
   - Create account summaries with calculated balances
   - Show progress and success statistics

## Step 6: Update Your Backend

The Supabase service is already created at `app/services/supabase_service.py`. 

To integrate it into your existing API, you have two options:

### Option A: Gradual Migration (Recommended)
Keep both SQLite and Supabase running, gradually switch endpoints:

1. Update one endpoint at a time
2. Test thoroughly
3. Switch remaining endpoints
4. Remove SQLite code

### Option B: Complete Switch
Replace all database calls with Supabase at once.

## Step 7: Test the Migration

1. Start your backend:
   ```bash
   npm run dev:backend
   ```

2. Test the API endpoints:
   ```bash
   # Test account summary
   curl http://localhost:8000/api/account-summary
   
   # Test checking transactions
   curl "http://localhost:8000/api/transactions?account_type=checking&month=2025-06"
   
   # Test credit transactions
   curl "http://localhost:8000/api/transactions?account_type=credit&month=2025-06"
   
   # Test categories
   curl http://localhost:8000/api/categories
   ```

## Benefits After Migration

### Performance Improvements
- **Faster queries**: PostgreSQL with proper indexing
- **Better filtering**: Server-side filtering reduces data transfer
- **Concurrent users**: PostgreSQL handles multiple users better
- **Real-time updates**: Supabase real-time subscriptions

### Scalability
- **Automatic backups**: Supabase handles backups
- **Connection pooling**: Better resource management
- **Horizontal scaling**: Easy to scale as you grow
- **CDN**: Built-in CDN for faster global access

### Security
- **Row Level Security**: Users can only see their own data
- **Built-in auth**: Ready for user authentication
- **SSL encryption**: All data encrypted in transit
- **Audit logs**: Track all database changes

### Developer Experience
- **Dashboard**: Visual database management
- **API auto-generation**: REST API generated automatically
- **Real-time subscriptions**: Live data updates
- **SQL editor**: Run queries directly in the dashboard

## Data Structure Changes

### Before (SQLite - Single Table)
```
transactions
├── id
├── date
├── amount
├── description
├── category
├── type
├── status
└── account_type  # 'checking' or 'credit'
```

### After (Supabase - Separate Tables)
```
checking_transactions
├── id (UUID)
├── user_id (UUID)
├── date
├── amount
├── description
├── category
├── type
├── status
├── ml_category
├── confidence_score
├── created_at
└── updated_at

credit_transactions
├── id (UUID)
├── user_id (UUID)
├── date
├── amount
├── description
├── category
├── type
├── status
├── ml_category
├── confidence_score
├── created_at
└── updated_at

account_summaries
├── id (UUID)
├── user_id (UUID)
├── account_type
├── current_balance
├── available_balance
├── credit_limit
├── last_updated
└── created_at
```

## Performance Comparison

| Metric | SQLite (Before) | Supabase (After) |
|--------|----------------|------------------|
| Query time (filtered) | 2-5 seconds | 100-300ms |
| Data transfer | Full dataset | Filtered results only |
| Concurrent users | 1 | Unlimited |
| Backup strategy | Manual | Automatic |
| Scaling | Vertical only | Horizontal + Vertical |

## Troubleshooting

### Common Issues

1. **Connection Error**: Check your SUPABASE_URL and keys
2. **Permission Denied**: Make sure you're using the service key for migration
3. **Data Not Showing**: Check RLS policies are correctly set
4. **Slow Queries**: Verify indexes are created properly

### Getting Help

- **Supabase Docs**: [docs.supabase.com](https://docs.supabase.com)
- **Community**: [github.com/supabase/supabase/discussions](https://github.com/supabase/supabase/discussions)
- **Discord**: [discord.supabase.com](https://discord.supabase.com)

## Next Steps

1. Set up user authentication with Supabase Auth
2. Implement real-time updates for live transaction feeds
3. Add database triggers for automatic ML categorization
4. Set up automated backups and monitoring
5. Implement advanced analytics with PostgreSQL functions

## Cost Considerations

- **Free tier**: 500MB database, 2GB bandwidth/month
- **Pro tier**: $25/month for larger projects
- **Current usage**: ~174k transactions ≈ 50-100MB
- **Recommendation**: Start with free tier, upgrade as needed 