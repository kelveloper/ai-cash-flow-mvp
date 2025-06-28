"""
Capital One-style transaction categorization service
Implements their category system with 70% accuracy targeting for demo
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional
from app.models.transaction import TransactionCategory

class CapitalOneCategorizationService:
    """
    Capital One-style categorization service with targeted 70% accuracy for demo
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Category mapping from legacy to Capital One categories
        self.legacy_to_capital_one = {
            # Food & Dining
            'coffee': TransactionCategory.DINING_RESTAURANTS,
            'pastry': TransactionCategory.DINING_RESTAURANTS,
            'sandwich': TransactionCategory.DINING_RESTAURANTS,
            'catering': TransactionCategory.DINING_RESTAURANTS,
            'food': TransactionCategory.DINING_RESTAURANTS,
            
            # Existing groceries maps directly
            'groceries': TransactionCategory.GROCERIES,
            
            # Shopping & Merchandise
            'merchandise': TransactionCategory.MERCHANDISE_SHOPPING,
            'supplies': TransactionCategory.MERCHANDISE_SHOPPING,
            
            # Utilities & Bills
            'utilities': TransactionCategory.BILLS_UTILITIES,
            'bill': TransactionCategory.BILLS_UTILITIES,
            
            # Home & Maintenance
            'rent': TransactionCategory.HOME_RENT_MORTGAGE,
            'maintenance': TransactionCategory.HOME_MAINTENANCE,
            
            # Transportation becomes gas/automotive
            'transportation': TransactionCategory.GAS_AUTOMOTIVE,
            
            # Keep entertainment as is
            'entertainment': TransactionCategory.ENTERTAINMENT,
            
            # Keep healthcare as is
            'healthcare': TransactionCategory.HEALTHCARE,
            
            # Business categories map to personal for demo
            'marketing': TransactionCategory.PERSONAL,
            'salary': TransactionCategory.PERSONAL,
            
            # Catch-all
            'misc': TransactionCategory.PERSONAL,
            'other': TransactionCategory.PERSONAL,
        }
        
        # Enhanced categorization rules based on merchant patterns
        self.merchant_patterns = {
            # Dining & Restaurants
            TransactionCategory.DINING_RESTAURANTS: [
                r'starbucks|coffee|cafe|restaurant|dining|pizza|burger|taco|sushi|diner|bistro|grub|doordash|uber\s*eats|food',
                r'mcdonald|subway|kfc|chipotle|panera|wendy|dunkin|domino',
                r'bagel|danish|scone|muffin|pastry|sandwich|wrap|panini|salad|soup',
                r'catering|party\s*sale|event\s*sale|meeting\s*sale'
            ],
            
            # Groceries
            TransactionCategory.GROCERIES: [
                r'grocery|supermarket|whole\s*foods|trader\s*joe|safeway|kroger|publix',
                r'instacart|fresh\s*direct|amazon\s*fresh|grocery\s*delivery',
                r'food\s*market|organic|produce|deli'
            ],
            
            # Merchandise & Shopping
            TransactionCategory.MERCHANDISE_SHOPPING: [
                r'amazon|target|walmart|costco|best\s*buy|apple\s*store|etsy',
                r'shopping|retail|store|marketplace|mktplace|merchandise',
                r'clothing|electronics|books|toys|home\s*goods|decor',
                r'handmade|thermos|mug|hat|cups'
            ],
            
            # Gas & Automotive
            TransactionCategory.GAS_AUTOMOTIVE: [
                r'shell|exxon|bp|chevron|gas|fuel|automotive|car\s*wash',
                r'parking|toll|uber|lyft|taxi|rental\s*car|auto\s*repair'
            ],
            
            # Phone/Cable/Utilities
            TransactionCategory.PHONE_CABLE_UTILITIES: [
                r'verizon|att|t-mobile|sprint|comcast|spectrum|cable|internet',
                r'phone|cellular|wireless|broadband'
            ],
            
            # Bills & Utilities
            TransactionCategory.BILLS_UTILITIES: [
                r'electric|gas\s*bill|water|sewer|utility|coned|electric|power',
                r'spotify|netflix|hulu|disney|subscription|slack|adobe',
                r'insurance|health|cigna|united\s*health|wire\s*transfer'
            ],
            
            # Travel
            TransactionCategory.TRAVEL: [
                r'airline|flight|hotel|airbnb|booking|expedia|travel|vacation',
                r'airport|rental|cruise|resort'
            ],
            
            # Entertainment
            TransactionCategory.ENTERTAINMENT: [
                r'movie|theater|concert|game|sport|entertainment|gym|fitness',
                r'streaming|music|spotify|apple\s*music'
            ],
            
            # Home
            TransactionCategory.HOME: [
                r'home\s*depot|lowes|hardware|home\s*improvement|furniture',
                r'rent|mortgage|property|real\s*estate'
            ],
            
            # Healthcare
            TransactionCategory.HEALTHCARE: [
                r'hospital|doctor|medical|pharmacy|cvs|walgreens|health|dental',
                r'clinic|medicine|prescription|therapy'
            ],
            
            # Personal (catch-all)
            TransactionCategory.PERSONAL: [
                r'misc|personal|other|unknown|transfer|payment|refund',
                r'zelle|venmo|paypal|cash\s*app|wire|check'
            ]
        }
        
        # Demo accuracy control - we'll intentionally miscategorize 30% for demo
        self.target_accuracy = 0.70
        self.demo_errors = {
            TransactionCategory.DINING_RESTAURANTS: [TransactionCategory.GROCERIES, TransactionCategory.ENTERTAINMENT],
            TransactionCategory.GROCERIES: [TransactionCategory.DINING_RESTAURANTS, TransactionCategory.MERCHANDISE_SHOPPING],
            TransactionCategory.MERCHANDISE_SHOPPING: [TransactionCategory.PERSONAL, TransactionCategory.ENTERTAINMENT],
            TransactionCategory.BILLS_UTILITIES: [TransactionCategory.PHONE_CABLE_UTILITIES, TransactionCategory.HOME],
            TransactionCategory.GAS_AUTOMOTIVE: [TransactionCategory.MERCHANDISE_SHOPPING, TransactionCategory.PERSONAL]
        }
    
    def categorize_transaction(self, description: str, amount: float = None, original_category: str = None) -> Dict[str, Any]:
        """
        Categorize a transaction using Capital One-style categories
        with targeted 70% accuracy for demo purposes
        """
        
        # First, try to get the correct category
        correct_category = self._get_correct_category(description, original_category)
        
        # Apply demo accuracy targeting (30% intentional errors)
        final_category = self._apply_demo_accuracy(correct_category)
        
        # Calculate confidence based on whether we made an intentional error
        confidence = 0.85 if final_category == correct_category else 0.65
        
        # Import here to avoid circular imports
        from app.utils.category_formatter import format_category_for_api
        
        return {
            'category': final_category.value,
            'category_display': format_category_for_api(final_category.value),
            'confidence': confidence,
            'source': 'capital_one_ai',
            'explanation': self._get_explanation(description, final_category),
            'correct_category': correct_category.value,  # For demo purposes
            'was_intentional_error': final_category != correct_category
        }
    
    def _get_correct_category(self, description: str, original_category: str = None) -> TransactionCategory:
        """Get the correct category based on merchant patterns"""
        
        description_lower = description.lower()
        
        # Check each category's patterns
        for category, patterns in self.merchant_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
        
        # If no pattern matches, try legacy mapping
        if original_category and original_category.lower() in self.legacy_to_capital_one:
            return self.legacy_to_capital_one[original_category.lower()]
        
        # Default fallback
        return TransactionCategory.PERSONAL
    
    def _apply_demo_accuracy(self, correct_category: TransactionCategory) -> TransactionCategory:
        """Apply 70% accuracy by intentionally making some errors for demo"""
        
        # Set seed based on category name for consistent demo results
        random.seed(hash(correct_category.value) % 1000)
        
        # 70% of the time, return correct category
        if random.random() < self.target_accuracy:
            return correct_category
        
        # 30% of the time, return a plausible error
        possible_errors = self.demo_errors.get(correct_category, [TransactionCategory.PERSONAL])
        return random.choice(possible_errors) if possible_errors else TransactionCategory.PERSONAL
    
    def _get_explanation(self, description: str, category: TransactionCategory) -> str:
        """Generate explanation for the categorization"""
        
        explanations = {
            TransactionCategory.DINING_RESTAURANTS: f"Identified '{description}' as dining/restaurant based on merchant pattern",
            TransactionCategory.GROCERIES: f"Categorized '{description}' as groceries based on merchant type",
            TransactionCategory.MERCHANDISE_SHOPPING: f"Classified '{description}' as merchandise/shopping transaction",
            TransactionCategory.GAS_AUTOMOTIVE: f"Identified '{description}' as gas/automotive expense",
            TransactionCategory.BILLS_UTILITIES: f"Categorized '{description}' as utility bill payment",
            TransactionCategory.TRAVEL: f"Classified '{description}' as travel-related expense",
            TransactionCategory.ENTERTAINMENT: f"Identified '{description}' as entertainment expense",
            TransactionCategory.HOME: f"Categorized '{description}' as home-related expense",
            TransactionCategory.HEALTHCARE: f"Classified '{description}' as healthcare expense",
            TransactionCategory.PERSONAL: f"Categorized '{description}' as personal/miscellaneous"
        }
        
        return explanations.get(category, f"AI categorized '{description}' as {category.value}")
    
    def batch_categorize(self, transactions: List[Dict]) -> List[Dict]:
        """Batch categorize multiple transactions"""
        
        results = []
        for transaction in transactions:
            description = transaction.get('description', '')
            amount = transaction.get('amount')
            original_category = transaction.get('category')
            
            result = self.categorize_transaction(description, amount, original_category)
            result['transaction_id'] = transaction.get('id')
            results.append(result)
            
        return results
    
    def get_accuracy_report(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Generate accuracy report for demo purposes"""
        
        categorizations = self.batch_categorize(transactions)
        
        total = len(categorizations)
        correct = sum(1 for c in categorizations if not c.get('was_intentional_error', False))
        accuracy = correct / total if total > 0 else 0
        
        return {
            'total_transactions': total,
            'correct_predictions': correct,
            'accuracy_percentage': round(accuracy * 100, 1),
            'target_accuracy': round(self.target_accuracy * 100, 1),
            'demo_note': 'Accuracy intentionally limited to 70% for realistic demo',
            'category_breakdown': self._get_category_breakdown(categorizations)
        }
    
    def _get_category_breakdown(self, categorizations: List[Dict]) -> Dict[str, int]:
        """Get breakdown of categories used"""
        
        breakdown = {}
        for cat in categorizations:
            category = cat['category']
            breakdown[category] = breakdown.get(category, 0) + 1
            
        return breakdown

    def get_capital_one_categories(self) -> List[Dict[str, str]]:
        """Get list of Capital One categories for frontend"""
        
        return [
            {"value": "dining_restaurants", "label": "Dining/Restaurants"},
            {"value": "groceries", "label": "Groceries"},
            {"value": "merchandise_shopping", "label": "Merchandise/Shopping"},
            {"value": "gas_automotive", "label": "Gas/Automotive"},
            {"value": "phone_cable_utilities", "label": "Phone/Cable/Utilities"},
            {"value": "travel", "label": "Travel"},
            {"value": "travel_airlines", "label": "Travel - Airlines"},
            {"value": "travel_hotels", "label": "Travel - Hotels"},
            {"value": "travel_car_rentals", "label": "Travel - Car Rentals"},
            {"value": "entertainment", "label": "Entertainment"},
            {"value": "home", "label": "Home"},
            {"value": "home_rent_mortgage", "label": "Home - Rent/Mortgage"},
            {"value": "home_maintenance", "label": "Home - Maintenance"},
            {"value": "healthcare", "label": "Healthcare"},
            {"value": "education", "label": "Education"},
            {"value": "bills_utilities", "label": "Bills & Utilities"},
            {"value": "personal", "label": "Personal"}
        ] 