import requests
import logging
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
        
        # API configurations (add your keys here)
        self.genify_api_key = None  # Get from environment
        self.salt_edge_app_id = None  # Get from environment
        self.salt_edge_secret = None  # Get from environment
        
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
        
        try:
            # Try Genify API first (example implementation)
            api_result = self._try_genify_api(description, amount)
            if api_result and api_result.get('confidence', 0) > 0.7:
                return {
                    'category': api_result['category'],
                    'confidence': api_result['confidence'],
                    'source': 'genify_api',
                    'merchant_name': api_result.get('clean_name'),
                    'merchant_logo': api_result.get('logo'),
                    'merchant_website': api_result.get('website')
                }
        except Exception as e:
            self.logger.warning(f"External API failed: {e}")
        
        # Fallback to your existing ML model
        if self.ml_service:
            try:
                ml_result = self.ml_service.categorize_descriptions([description])
                if ml_result and len(ml_result) > 0:
                    return {
                        'category': ml_result[0]['category'],
                        'confidence': ml_result[0].get('confidence', 0.6),
                        'source': 'local_ml',
                        'explanation': ml_result[0].get('explanation')
                    }
            except Exception as e:
                self.logger.warning(f"Local ML failed: {e}")
        
        # Final fallback to simple categorization
        return {
            'category': 'misc',
            'confidence': 0.3,
            'source': 'fallback',
            'explanation': 'No categorization method succeeded'
        }
    
    def _try_genify_api(self, description: str, amount: float = None) -> Optional[Dict]:
        """Try Genify API for categorization"""
        if not self.genify_api_key:
            return None
            
        try:
            # Example API call structure (adjust based on actual API)
            payload = {
                "transactions": [{
                    "description": description,
                    "amount": amount or 1.0,
                    "currency": "USD"
                }]
            }
            
            headers = {
                'Authorization': f'Bearer {self.genify_api_key}',
                'Content-Type': 'application/json'
            }
            
            # This is a placeholder URL - replace with actual Genify endpoint
            response = requests.post(
                'https://api.genify.ai/v1/categorize', 
                json=payload, 
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('data') and len(result['data']) > 0:
                    transaction_data = result['data'][0]
                    return {
                        'category': transaction_data.get('category_name', 'misc').lower(),
                        'confidence': 0.9,  # Genify typically has high confidence
                        'clean_name': transaction_data.get('clean_description'),
                        'logo': transaction_data.get('logo'),
                        'website': transaction_data.get('merchant_website')
                    }
        except Exception as e:
            self.logger.error(f"Genify API error: {e}")
            
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