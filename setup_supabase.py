#!/usr/bin/env python3
"""
Supabase Setup and Migration Script
This script helps you set up your Supabase environment and migrate your data.
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import supabase
        print("✅ Supabase Python client is installed")
    except ImportError:
        print("❌ Supabase Python client not found")
        print("Please install it with: pip install supabase")
        return False
    
    try:
        import pandas
        print("✅ Pandas is installed")
    except ImportError:
        print("❌ Pandas not found")
        print("Please install it with: pip install pandas")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create a .env file based on supabase.env.example")
        return False
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please add them to your .env file")
        return False
    
    print("✅ .env file is properly configured")
    return True

def check_csv_data():
    """Check if CSV data file exists."""
    csv_file = Path('data/all_transactions_ready.csv')
    if not csv_file.exists():
        print("❌ Transaction data file not found: data/all_transactions_ready.csv")
        return False
    
    print("✅ Transaction data file found")
    return True

def run_migration():
    """Run the Supabase migration script."""
    print("\n🚀 Starting Supabase migration...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/migrate_to_supabase.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            print(result.stdout)
        else:
            print("❌ Migration failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running migration: {str(e)}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🔧 Supabase Setup and Migration Script")
    print("=====================================\n")
    
    # Step 1: Check requirements
    print("Step 1: Checking requirements...")
    if not check_requirements():
        print("\nPlease install missing packages and run this script again.")
        sys.exit(1)
    
    # Step 2: Check environment file
    print("\nStep 2: Checking environment configuration...")
    if not check_env_file():
        print("\nPlease configure your .env file and run this script again.")
        print("\nTo get your Supabase credentials:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to Settings > API")
        print("4. Copy the URL and anon key")
        sys.exit(1)
    
    # Step 3: Check CSV data
    print("\nStep 3: Checking transaction data...")
    if not check_csv_data():
        print("\nPlease ensure your transaction data is available and run this script again.")
        sys.exit(1)
    
    # Step 4: Run migration
    print("\nStep 4: Running migration...")
    if not run_migration():
        print("\nMigration failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start your backend: python -m app.main")
    print("2. Start your frontend: npm run dev:frontend")
    print("3. Visit http://localhost:3000 to see your dashboard")

if __name__ == "__main__":
    main() 