#!/usr/bin/env python3
"""
Test script for Capital One categorization system
Demonstrates 70% accuracy targeting with your demo data
"""

import sys
import os
import pandas as pd

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.capital_one_categorization import CapitalOneCategorizationService

def test_capital_one_categorization():
    """Test the Capital One categorization system with demo data"""
    
    print("🏦 Capital One Categorization System Demo")
    print("="*50)
    
    # Initialize the service
    categorizer = CapitalOneCategorizationService()
    
    # Load demo data
    demo_file = "data/all_transactions_demo.csv"
    if not os.path.exists(demo_file):
        print(f"❌ Demo file not found: {demo_file}")
        return
    
    df = pd.read_csv(demo_file)
    transactions = df.to_dict('records')
    
    print(f"📊 Loaded {len(transactions)} demo transactions")
    print()
    
    # Test individual transaction categorization
    print("🔍 Individual Transaction Tests:")
    print("-" * 30)
    
    test_descriptions = [
        "Starbucks Coffee Seattle",
        "Amazon Marketplace Purchase", 
        "INSTACART Grocery Delivery",
        "Shell Gas Station",
        "Spotify Premium Subscription",
        "UBER Ride Service",
        "Target Shopping",
        "Electric Bill ConEd"
    ]
    
    for desc in test_descriptions:
        result = categorizer.categorize_transaction(desc)
        status = "✅ CORRECT" if not result['was_intentional_error'] else "❌ DEMO ERROR"
        print(f"{status} | {desc[:25]:<25} → {result['category']:<20} (conf: {result['confidence']:.2f})")
    
    print()
    
    # Test batch categorization with accuracy report
    print("📈 Batch Categorization Report:")
    print("-" * 30)
    
    accuracy_report = categorizer.get_accuracy_report(transactions[:20])  # Test first 20
    
    print(f"Total Transactions: {accuracy_report['total_transactions']}")
    print(f"Correct Predictions: {accuracy_report['correct_predictions']}")
    print(f"Accuracy: {accuracy_report['accuracy_percentage']}%")
    print(f"Target: {accuracy_report['target_accuracy']}%")
    print(f"Note: {accuracy_report['demo_note']}")
    print()
    
    # Show category breakdown
    print("📊 Category Breakdown:")
    print("-" * 20)
    for category, count in accuracy_report['category_breakdown'].items():
        print(f"{category.replace('_', ' ').title():<25}: {count}")
    
    print()
    
    # Show Capital One categories
    print("🏷️  Available Capital One Categories:")
    print("-" * 35)
    categories = categorizer.get_capital_one_categories()
    for cat in categories:
        print(f"• {cat['label']}")
    
    print()
    print("✅ Capital One categorization system ready!")
    print("🚀 Start your app and test the endpoints:")
    print("   • POST /api/categorize-transaction-capital-one")
    print("   • POST /api/categorize-month-capital-one") 
    print("   • GET /api/capital-one-categories")

if __name__ == "__main__":
    test_capital_one_categorization() 