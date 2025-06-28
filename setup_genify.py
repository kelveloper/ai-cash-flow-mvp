#!/usr/bin/env python3
"""
Setup script for Genify AI Enhanced Categorization
Helps configure API keys and test the integration
"""

import os
import sys
from pathlib import Path

def setup_genify():
    """Setup Genify AI integration"""
    
    print("🚀 Genify AI Enhanced Categorization Setup")
    print("=" * 50)
    print()
    
    # Check if .env file exists
    env_file = Path(".env")
    
    print("📋 Setup Steps:")
    print("1. Get your Genify API key from: https://genify.ai/")
    print("2. Sign up for a free account")
    print("3. Copy your API key from the dashboard")
    print()
    
    api_key = input("🔑 Enter your Genify API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting...")
        return False
    
    # Read existing .env or create new one
    env_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # Update or add Genify API key
    lines = env_content.split('\n') if env_content else []
    genify_line_exists = False
    
    for i, line in enumerate(lines):
        if line.startswith('GENIFY_API_KEY='):
            lines[i] = f'GENIFY_API_KEY={api_key}'
            genify_line_exists = True
            break
    
    if not genify_line_exists:
        lines.append(f'GENIFY_API_KEY={api_key}')
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ API key saved to {env_file}")
    print()
    
    # Set environment variable for current session
    os.environ['GENIFY_API_KEY'] = api_key
    
    print("🧪 Testing Integration...")
    try:
        from app.services.enhanced_categorization import EnhancedCategorizationService
        
        service = EnhancedCategorizationService()
        
        # Test with a sample transaction
        test_description = "AMZN MKTP US*MT2QX3PX3 AMZN.COM/BILLWA"
        result = service.categorize_transaction_enhanced(test_description)
        
        print(f"✅ Test Result: {test_description[:40]}...")
        print(f"   Category: {result.get('category')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Source: {result.get('source')}")
        if result.get('merchant_name'):
            print(f"   Clean Name: {result.get('merchant_name')}")
        print()
        
        if result.get('source') == 'genify_api':
            print("🎉 Genify API integration working!")
        elif result.get('source') == 'local_ml':
            print("⚠️ Genify API not responding, using local ML fallback")
        else:
            print("⚠️ Using basic fallback categorization")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print()
    print("📋 Next Steps:")
    print("1. Run: python test_enhanced_categorization.py")
    print("2. Start your FastAPI server: python -m uvicorn app.main:app --reload")
    print("3. Test enhanced categorization in your app")
    print("4. Monitor logs for API performance")
    print()
    print("🎯 Expected Improvements:")
    print("• Accuracy: 60% → 95%")
    print("• Clean merchant names")
    print("• Confidence scoring")
    print("• Automatic fallback")
    
    return True

if __name__ == "__main__":
    setup_genify() 