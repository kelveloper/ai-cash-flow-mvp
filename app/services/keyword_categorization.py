import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class KeywordCategorizationService:
    def __init__(self):
        """Initialize the keyword categorization service."""
        self.keyword_mappings = {
            'rent': ['rent', 'lease', 'housing'],
            'utilities': ['electric', 'water', 'gas', 'utility', 'utilities'],
            'groceries': ['grocery', 'supermarket', 'food', 'market'],
            'transportation': ['uber', 'lyft', 'taxi', 'transit', 'transport'],
            'entertainment': ['movie', 'theater', 'concert', 'ticket'],
            'healthcare': ['doctor', 'medical', 'pharmacy', 'health'],
            'subscriptions': ['netflix', 'spotify', 'subscription', 'membership'],
            'fees': ['fee', 'charge', 'service charge'],
            'taxes': ['tax', 'irs', 'withholding'],
            'insurance': ['insurance', 'coverage', 'policy'],
            'supplies': ['supply', 'equipment', 'material'],
            'merchandise': ['merchandise', 'product', 'item'],
            'food': ['restaurant', 'cafe', 'dining', 'meal'],
            'coffee': ['coffee', 'espresso', 'cafe'],
            'marketing': ['advertising', 'marketing', 'promotion'],
            'maintenance': ['maintenance', 'repair', 'service'],
            'pastry': ['pastry', 'bakery', 'bread', 'cake'],
            'sandwich': ['sandwich', 'sub', 'wrap'],
            'catering': ['catering', 'event', 'party'],
            'misc': ['misc', 'miscellaneous', 'other']
        }
        logger.info("[KeywordCategorization] Service initialized successfully")

    def categorize_description(self, description: str) -> str:
        """
        Categorize a transaction based on its description using keyword matching.
        
        Args:
            description (str): The transaction description to categorize
            
        Returns:
            str: The predicted category
        """
        description = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.keyword_mappings.items():
            if any(keyword in description for keyword in keywords):
                logger.info(f"[KeywordCategorization] Description: {description} | Predicted: {category}")
                return category
        
        # Default to misc if no matches found
        logger.info(f"[KeywordCategorization] Description: {description} | Predicted: misc (no matches)")
        return 'misc'

    def categorize_descriptions(self, descriptions: List[str], original_categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Categorize multiple transaction descriptions.
        
        Args:
            descriptions (List[str]): List of transaction descriptions
            original_categories (Optional[List[str]]): List of original categories
            
        Returns:
            List[Dict[str, Any]]: List of categorization results
        """
        results = []
        for i, desc in enumerate(descriptions):
            predicted = self.categorize_description(desc)
            result = {
                'predicted': predicted,
                'top': [(predicted, 1.0)],  # Simple confidence score for keyword matching
                'explanation': f'Matched keywords: {", ".join([k for k in self.keyword_mappings[predicted] if k in desc.lower()])}'
            }
            if original_categories:
                result['original_category'] = original_categories[i]
            results.append(result)
        return results 