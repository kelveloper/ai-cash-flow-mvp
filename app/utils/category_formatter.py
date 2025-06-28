"""
Category formatting utilities for displaying human-readable category names
"""

def format_category_name(category: str) -> str:
    """
    Convert category enum values to human-readable format
    
    Examples:
    - 'dining_restaurants' -> 'Dining Restaurants'
    - 'merchandise_shopping' -> 'Merchandise Shopping'
    - 'gas_automotive' -> 'Gas Automotive'
    - 'phone_cable_utilities' -> 'Phone Cable Utilities'
    """
    if not category:
        return ''
    
    # Replace underscores with spaces and title case each word
    formatted = category.replace('_', ' ').title()
    
    # Handle special cases for better readability
    replacements = {
        'Dining Restaurants': 'Dining & Restaurants',
        'Gas Automotive': 'Gas & Automotive', 
        'Phone Cable Utilities': 'Phone, Cable & Utilities',
        'Bills Utilities': 'Bills & Utilities',
        'Home Rent Mortgage': 'Home & Rent/Mortgage',
        'Home Maintenance': 'Home Maintenance',
        'Merchandise Shopping': 'Shopping & Merchandise',
    }
    
    return replacements.get(formatted, formatted)

def get_category_display_map():
    """
    Get a mapping of enum values to display names for all Capital One categories
    """
    from app.models.transaction import TransactionCategory
    
    return {
        TransactionCategory.DINING_RESTAURANTS.value: format_category_name(TransactionCategory.DINING_RESTAURANTS.value),
        TransactionCategory.GROCERIES.value: format_category_name(TransactionCategory.GROCERIES.value),
        TransactionCategory.MERCHANDISE_SHOPPING.value: format_category_name(TransactionCategory.MERCHANDISE_SHOPPING.value),
        TransactionCategory.GAS_AUTOMOTIVE.value: format_category_name(TransactionCategory.GAS_AUTOMOTIVE.value),
        TransactionCategory.PHONE_CABLE_UTILITIES.value: format_category_name(TransactionCategory.PHONE_CABLE_UTILITIES.value),
        TransactionCategory.TRAVEL.value: format_category_name(TransactionCategory.TRAVEL.value),
        TransactionCategory.ENTERTAINMENT.value: format_category_name(TransactionCategory.ENTERTAINMENT.value),
        TransactionCategory.HOME.value: format_category_name(TransactionCategory.HOME.value),
        TransactionCategory.HEALTHCARE.value: format_category_name(TransactionCategory.HEALTHCARE.value),
        TransactionCategory.EDUCATION.value: format_category_name(TransactionCategory.EDUCATION.value),
        TransactionCategory.BILLS_UTILITIES.value: format_category_name(TransactionCategory.BILLS_UTILITIES.value),
        TransactionCategory.PERSONAL.value: format_category_name(TransactionCategory.PERSONAL.value),
        # Legacy categories
        'misc': 'Personal',
        'miscellaneous': 'Personal', 
        'other': 'Personal',
        'food': 'Dining & Restaurants',
        'coffee': 'Dining & Restaurants',
        'utilities': 'Bills & Utilities',
        'rent': 'Home & Rent/Mortgage',
        'maintenance': 'Home Maintenance',
        'supplies': 'Shopping & Merchandise',
        'merchandise': 'Shopping & Merchandise',
        'transportation': 'Gas & Automotive',
        'salary': 'Personal',
        'marketing': 'Personal',
    }

def format_category_for_api(category: str) -> str:
    """
    Format category for API responses with display-friendly names
    """
    display_map = get_category_display_map()
    return display_map.get(category, format_category_name(category)) 