import requests
import logging
import os
from typing import List, Dict, Any, Optional
from app.services.ml_categorization import MLCategorizationService

class EnhancedCategorizationService:
    """
    Enhanced categorization service that combines local ML with external APIs
    for improved accuracy and merchant enrichment
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize your existing ML service as fallback
        try:
            self.ml_service = MLCategorizationService()
            self.logger.info("ML categorization service loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load ML service: {e}")
            self.ml_service = None
        
        # API configurations - load from environment variables
        self.genify_api_key = os.environ.get('GENIFY_API_KEY')
        self.salt_edge_app_id = os.environ.get('SALT_EDGE_APP_ID')
        self.salt_edge_secret = os.environ.get('SALT_EDGE_SECRET')
        
        # Log API key status
        if self.genify_api_key:
            self.logger.info("✅ Genify API key configured")
        else:
            self.logger.warning("⚠️ Genify API key not found in environment")
        
    def categorize_transaction_enhanced(
        self, 
        description: str, 
        amount: float = None,
        original_category: str = None
    ) -> Dict[str, Any]:
        """
        Enhanced categorization with fallback strategy:
        1. Try external API for best accuracy
        2. Fallback to local ML model
        3. Fallback to keyword matching
        """
        
        # Log the attempt
        self.logger.info(f"🚀 [ENHANCED] Categorizing: '{description[:50]}...'")
        
        try:
            # Try Genify API first
            self.logger.info("🌐 [GENIFY] Attempting Genify API call...")
            api_result = self._try_genify_api(description, amount)
            if api_result and api_result.get('confidence', 0) > 0.7:
                self.logger.info(f"✅ [GENIFY] SUCCESS - Category: {api_result['category']} (confidence: {api_result['confidence']})")
                return {
                    'category': api_result['category'],
                    'confidence': api_result['confidence'],
                    'source': 'genify_api',
                    'merchant_name': api_result.get('clean_name'),
                    'merchant_logo': api_result.get('logo'),
                    'merchant_website': api_result.get('website')
                }
            else:
                self.logger.warning("⚠️ [GENIFY] API returned low confidence or no result")
                
        except Exception as e:
            self.logger.error(f"❌ [GENIFY] API failed: {e}")
        
        # Fallback to your existing ML model
        self.logger.info("🤖 [ML] Falling back to local ML model...")
        if self.ml_service:
            try:
                ml_result = self.ml_service.categorize_descriptions([description])
                if ml_result and len(ml_result) > 0:
                    predicted_category = ml_result[0].get('predicted', 'misc')
                    confidence = ml_result[0].get('confidence', 0.6)
                    self.logger.info(f"✅ [ML] SUCCESS - Category: {predicted_category} (confidence: {confidence:.2f})")
                    return {
                        'category': predicted_category,
                        'confidence': confidence,
                        'source': 'local_ml',
                        'explanation': ml_result[0].get('explanation', 'ML prediction')
                    }
            except Exception as e:
                self.logger.error(f"❌ [ML] Local ML failed: {e}")
        
        # Final fallback to simple categorization
        self.logger.warning("🔄 [FALLBACK] Using keyword fallback categorization")
        return {
            'category': 'misc',
            'confidence': 0.3,
            'source': 'fallback',
            'explanation': 'No categorization method succeeded'
        }
    
    def _try_genify_api(self, description: str, amount: float = None) -> Optional[Dict]:
        """Try Genify API for categorization"""
        if not self.genify_api_key:
            self.logger.warning("❌ [GENIFY] No API key configured")
            return None
        
        # Check if it's just a demo key
        if self.genify_api_key == "demo_key_for_testing":
            self.logger.warning("🧪 [GENIFY] Using demo key - API will not actually be called")
            return None
            
        try:
            # Genify API endpoint and payload based on their documentation
            self.logger.info(f"📡 [GENIFY] Calling API for: {description[:30]}...")
            
            # Genify API expects these query parameters
            params = {
                'description': description,
                'amount': amount or -10.0,  # Negative for expenses
                'country': 'US',  # Default to US
                'date': '2025-06-01',  # Use current date in production
                'currency': 'USD'
            }
            
            headers = {
                'Authorization': f'Bearer {self.genify_api_key}',
                'Username': 'your_username',  # Replace with actual username
                'Account_id': 'account_1',
                'Category': '1',  # Flag to activate categorizer
                'Content-Type': 'application/json'
            }
            
            # Actual Genify API endpoint
            response = requests.get(
                'https://pfm.genify.ai/api/v1.0/txn-data/', 
                params=params,
                headers=headers,
                timeout=10
            )
            
            self.logger.info(f"📨 [GENIFY] API Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"📦 [GENIFY] Raw response: {result}")
                
                if result:
                    category_name = result.get('Category Name', 'misc')
                    clean_description = result.get('Clean Description', result.get('Display Description', ''))
                    
                    self.logger.info(f"🎯 [GENIFY] Parsed category: {category_name}")
                    
                    return {
                        'category': category_name.lower().replace(' ', '_'),
                        'confidence': 0.95,  # Genify typically has high confidence
                        'clean_name': clean_description,
                        'logo': result.get('Logo'),
                        'website': result.get('Merchant Website')
                    }
            elif response.status_code == 401:
                self.logger.error("🔑 [GENIFY] Authentication failed - check API key")
            elif response.status_code == 400:
                self.logger.error(f"📝 [GENIFY] Bad request - check parameters: {response.text}")
            else:
                self.logger.error(f"🚨 [GENIFY] HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            self.logger.error("⏰ [GENIFY] API timeout (>10s)")
        except requests.exceptions.ConnectionError:
            self.logger.error("🌐 [GENIFY] Connection error - check internet")
        except Exception as e:
            self.logger.error(f"💥 [GENIFY] Unexpected error: {e}")
            
        return None
    
    def batch_categorize(self, transactions: List[Dict]) -> List[Dict]:
        """
        Batch categorization for multiple transactions
        """
        results = []
        
        for transaction in transactions:
            description = transaction.get('description', '')
            amount = transaction.get('amount')
            
            result = self.categorize_transaction_enhanced(description, amount)
            result['transaction_id'] = transaction.get('id')
            results.append(result)
            
        return results
    
    def learn_from_correction(
        self, 
        description: str, 
        correct_category: str,
        original_prediction: str = None
    ):
        """
        Learn from user corrections to improve future categorizations
        """
        self.logger.info(f"Learning: '{description}' -> {correct_category}")
        
        # You can implement learning logic here:
        # 1. Store corrections in database
        # 2. Send feedback to external APIs if they support it
        # 3. Retrain your local model periodically
        
        # Example: Store in database for later analysis
        correction_data = {
            'description': description,
            'correct_category': correct_category,
            'original_prediction': original_prediction,
            'timestamp': '2024-01-01'  # Use actual timestamp
        }
        
        # TODO: Store in your database
        self.logger.info(f"Correction logged: {correction_data}") 