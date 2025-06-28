#!/usr/bin/env python3
"""
Test script for Enhanced Categorization APIs
Demonstrates the improvement over basic ML categorization
"""

import requests
import json
from datetime import datetime

# Test transaction descriptions
test_transactions = [
    "AMZN MKTP US*MT2QX3PX3 AMZN.COM/BILLWA",
    "SQ *THE CROISSANT CORNER BERKELEY CA",
    "SPOTIFY *SPOTIFY USA 877-7781161 NY",
    "UBER TRIP 4C7X2 HELP.UBER.COM CA",
    "TARGET T-1067 BERKELEY CA",
    "COSTCO WHSE #1006 FREMONT CA",
    "PACIFIC GAS & ELECTRIC COMPANY CA",
    "WELLS FARGO DES:ACH TRAN INDN:TRANSFER",
    "NETFLIX.COM LOS GATOS CA",
    "TST* PANDA EXPRESS #3092 BERKELEY CA"
]

def test_basic_categorization():
    """Test your existing categorization endpoint"""
    print("🔍 Testing Basic Categorization (Keyword-based)")
    print("=" * 60)
    
    for description in test_transactions:
        try:
            response = requests.post(
                "http://localhost:8000/api/categorize-transaction",
                json={"description": description}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {description[:40]:40} → {result.get('category', 'Unknown')}")
            else:
                print(f"❌ {description[:40]:40} → Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description[:40]:40} → Connection Error")
    
    print()

def test_enhanced_categorization():
    """Test the new enhanced categorization endpoint"""
    print("🚀 Testing Enhanced Categorization (ML + APIs)")
    print("=" * 60)
    
    for description in test_transactions:
        try:
            response = requests.post(
                "http://localhost:8000/api/categorize-transaction-enhanced",
                json={"description": description}
            )
            
            if response.status_code == 200:
                result = response.json()
                category = result.get('category', 'Unknown')
                confidence = result.get('confidence', 0)
                source = result.get('source', 'unknown')
                merchant_name = result.get('merchant_name', '')
                
                print(f"✅ {description[:30]:30} → {category:15} (conf: {confidence:.2f}, src: {source})")
                if merchant_name:
                    print(f"   Clean name: {merchant_name}")
                if result.get('demo_note'):
                    print(f"   ℹ️  {result['demo_note']}")
                elif result.get('source') == 'genify_api':
                    print(f"   ℹ️  🎬 Demo mode - simulating enhanced categorization")
                elif result.get('source') == 'fallback':
                    print(f"   ℹ️  Using keyword fallback - configure API keys for best results")
                print()
            else:
                print(f"❌ {description[:40]:40} → Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description[:40]:40} → Connection Error: {str(e)}")

def compare_categorizations():
    """Compare basic vs enhanced categorization side by side"""
    print("📊 Side-by-Side Comparison")
    print("=" * 80)
    print(f"{'Description':35} {'Basic':15} {'Enhanced':15} {'Improvement'}")
    print("-" * 80)
    
    for description in test_transactions[:5]:  # Test first 5 for quick comparison
        try:
            # Basic categorization
            basic_response = requests.post(
                "http://localhost:8000/api/categorize-transaction",
                json={"description": description}
            )
            basic_category = "Error"
            if basic_response.status_code == 200:
                basic_category = basic_response.json().get('category', 'Unknown')
            
            # Enhanced categorization
            enhanced_response = requests.post(
                "http://localhost:8000/api/categorize-transaction-enhanced",
                json={"description": description}
            )
            enhanced_category = "Error"
            enhanced_confidence = 0
            improvement = ""
            
            if enhanced_response.status_code == 200:
                enhanced_result = enhanced_response.json()
                enhanced_category = enhanced_result.get('category', 'Unknown')
                enhanced_confidence = enhanced_result.get('confidence', 0)
                
                if enhanced_result.get('merchant_name'):
                    improvement = f"+ Clean name"
                if enhanced_confidence > 0.8:
                    improvement += f" + High confidence"
            
            print(f"{description[:34]:35} {basic_category:15} {enhanced_category:15} {improvement}")
            
        except Exception as e:
            print(f"{description[:34]:35} {'Error':15} {'Error':15} Connection failed")

if __name__ == "__main__":
    print("🧪 Enhanced ML/AI Categorization API Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Make sure your FastAPI server is running on localhost:8000
    try:
        health_check = requests.get("http://localhost:8000/api/categories")
        if health_check.status_code != 200:
            print("❌ Server not responding. Make sure FastAPI is running on localhost:8000")
            exit(1)
    except:
        print("❌ Cannot connect to server. Make sure FastAPI is running on localhost:8000")
        print("   Run: python -m uvicorn app.main:app --reload")
        exit(1)
    
    test_basic_categorization()
    test_enhanced_categorization()
    compare_categorizations()
    
    print()
    print("💡 Next Steps:")
    print("1. Get API keys for Genify/Salt Edge for better accuracy")
    print("2. Configure environment variables for API access")
    print("3. Test with real transaction data")
    print("4. Monitor categorization accuracy improvements") 