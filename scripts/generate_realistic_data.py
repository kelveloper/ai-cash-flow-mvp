import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuration
START_DATE = datetime(2019, 1, 1)
END_DATE = datetime(2025, 6, 14)
MIN_TRANSACTIONS = 30000

# Business hours: 7 AM to 8 PM
OPEN_HOUR = 7
CLOSE_HOUR = 20

# Transaction types and their probabilities
TRANSACTION_TYPES = {
    'Sale': 0.7,
    'Refund': 0.05,
    'Expense': 0.25
}

# Transaction categories
CATEGORIES = {
    'Sale': ['Coffee', 'Pastry', 'Sandwich', 'Catering', 'Merchandise', 'Miscellaneous'],
    'Expense': ['Supplies', 'Marketing', 'Maintenance', 'Utilities', 'Payroll', 'Rent', 'Miscellaneous'],
    'Refund': ['Coffee', 'Pastry', 'Sandwich', 'Catering', 'Merchandise', 'Miscellaneous']
}

# Payment methods
PAYMENT_METHODS = ['Cash', 'Credit Card', 'Debit Card', 'Mobile Payment']

# Generate a realistic transaction amount based on category and type
def generate_amount(transaction_type, category):
    if transaction_type == 'Sale':
        if category == 'Coffee':
            return round(random.uniform(3.50, 6.00), 2)
        elif category == 'Pastry':
            return round(random.uniform(2.50, 5.00), 2)
        elif category == 'Sandwich':
            return round(random.uniform(8.00, 12.00), 2)
        elif category == 'Merchandise':
            return round(random.uniform(10.00, 25.00), 2)
        elif category == 'Catering':
            return round(random.uniform(100.00, 500.00), 2)
    elif transaction_type == 'Refund':
        return -round(random.uniform(3.50, 25.00), 2)
    elif transaction_type == 'Expense':
        if category == 'Rent':
            return -round(random.uniform(3000.00, 5000.00), 2)
        elif category == 'Utilities':
            return -round(random.uniform(200.00, 500.00), 2)
        elif category == 'Supplies':
            return -round(random.uniform(100.00, 300.00), 2)
        elif category == 'Payroll':
            return -round(random.uniform(2000.00, 4000.00), 2)
        elif category == 'Marketing':
            return -round(random.uniform(100.00, 500.00), 2)
        elif category == 'Maintenance':
            return -round(random.uniform(50.00, 200.00), 2)
    return 0.0

# Generate a realistic transaction date and time
def generate_datetime():
    date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
    hour = random.randint(OPEN_HOUR, CLOSE_HOUR)
    minute = random.randint(0, 59)
    return date.replace(hour=hour, minute=minute)

# Generate a realistic transaction description
def generate_description(transaction_type, category):
    # 30% chance to use a weird description
    if random.random() < 0.30:
        weird_descriptions = {
            'Sale': [
                # Payment Processors
                'SQ *THE CROISSANT CORNER',
                'PAYPAL *JNSPLYCO 877-123-4567',
                'STRIPE* SUBSTACK 1A2B3C',
                'PP* JANE DOE 1234',
                'VENMO PMT - To Leo G.',
                'ZELLE PMT - From Maria R.',
                'CASH APP* JANE DOE',
                'APPLE PAY* JANE DOE',
                'GOOGLE PAY* JANE DOE',
                'TST* THE PERFECT CUP CAFE',
                # Online Retailers
                'AMZN Mktp US*AB123',
                'AMZN*MKTP US*AB123',
                'AMZN*MKTPLACE*AB123',
                'COSTCO WHSE #0321',
                'COSTCO.COM*AB123',
                'THE HOME DEPOT #0321',
                'HD.COM*AB123',
                'ETSY.COM*HandmadeDecor',
                'ETSY*HANDMADE*AB123',
                'TARGET.COM*AB123',
                'TGT*TARGET.COM*AB123',
                # Food Delivery
                'DD*DOORDASH*AB123',
                'UBER*EATS*AB123',
                'GRUB*GRUBHUB*AB123',
                'INST*INSTACART*AB123',
                # Subscription Services
                'NETFLIX.COM*AB123',
                'SPOTIFY*AB123',
                'HULU*AB123',
                'DISNEY+*AB123',
                # Other Services
                'LYFT*RIDE*AB123',
                'UBER*RIDE*AB123',
                'AIRBNB*AB123',
                'EXPEDIA*AB123'
            ],
            'Expense': [
                # Retail Stores
                'WMRL #0321 WM SUPERCENTER',
                'WMT*WALMART*AB123',
                'TGT*TARGET*AB123',
                'COSTCO WHSE #0321',
                'HD*HOME DEPOT*AB123',
                'LOWES*AB123',
                # Utilities & Services
                'CONED*ELECTRIC*AB123',
                'ATT*BILL PMT 800-123-4567',
                'VERIZON*WIRELESS*AB123',
                'TMOBILE*WIRELESS*AB123',
                'SPECTRUM*INTERNET*AB123',
                'COMCAST*INTERNET*AB123',
                'IRS USATAXPYMT',
                'NYC*PARKING*AB123',
                'NYC*DOF*AB123',
                # Vendors & Suppliers
                'TRI-STATE VENTURES LLC',
                'ARROWHEAD MNT SPG WTR',
                'OCEANIC CATERING GROUP',
                'SYSCO*FOOD*AB123',
                'US FOODS*AB123',
                'GORDON FOOD*AB123',
                # Financial
                'ACH PMT - CONEDISON-PYMT',
                'ACH RETURN - INSUFFICIENT FUNDS',
                'CHECK #1099',
                'WIRE TRANSFER*AB123',
                'FOREIGN CURRENCY CONVERSION FEE',
                'RETURNED ITEM - DEFECTIVE',
                # Insurance & Healthcare
                'AETNA*HEALTH*AB123',
                'BLUE CROSS*AB123',
                'UNITED HEALTH*AB123',
                'CIGNA*HEALTH*AB123',
                # Software & Tech
                'ADOBE*SUBSCRIPTION*AB123',
                'MICROSOFT*365*AB123',
                'GOOGLE*WORKSPACE*AB123',
                'ZOOM*SUBSCRIPTION*AB123',
                'SLACK*SUBSCRIPTION*AB123'
            ]
        }
        
        # For weird descriptions, use more appropriate categories
        if transaction_type == 'Sale':
            if any(processor in weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)] 
                  for processor in ['SQ *', 'PAYPAL *', 'STRIPE*', 'PP*', 'VENMO', 'ZELLE', 'CASH APP*', 'APPLE PAY*', 'GOOGLE PAY*']):
                return weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)], 'Miscellaneous'
            elif any(store in weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)] 
                    for store in ['AMZN', 'COSTCO', 'THE HOME DEPOT', 'ETSY', 'TARGET', 'HD.COM', 'TGT']):
                return weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)], 'Merchandise'
            elif any(delivery in weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)] 
                    for delivery in ['DD*', 'UBER*EATS', 'GRUB*', 'INST*']):
                return weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)], 'Miscellaneous'
            elif any(subscription in weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)] 
                    for subscription in ['NETFLIX', 'SPOTIFY', 'HULU', 'DISNEY+']):
                return weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)], 'Miscellaneous'
            else:
                return weird_descriptions['Sale'][random.randint(0, len(weird_descriptions['Sale'])-1)], 'Miscellaneous'
        else:  # Expense
            if any(utility in weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)] 
                  for utility in ['CONED', 'ATT*', 'VERIZON', 'TMOBILE', 'SPECTRUM', 'COMCAST', 'IRS']):
                return weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)], 'Utilities'
            elif any(store in weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)] 
                    for store in ['WMRL', 'WMT*', 'TGT*', 'COSTCO', 'HD*', 'LOWES*']):
                return weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)], 'Supplies'
            elif any(supplier in weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)] 
                    for supplier in ['SYSCO*', 'US FOODS*', 'GORDON FOOD*']):
                return weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)], 'Supplies'
            elif any(insurance in weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)] 
                    for insurance in ['AETNA*', 'BLUE CROSS*', 'UNITED HEALTH*', 'CIGNA*']):
                return weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)], 'Miscellaneous'
            elif any(software in weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)] 
                    for software in ['ADOBE*', 'MICROSOFT*', 'GOOGLE*', 'ZOOM*', 'SLACK*']):
                return weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)], 'Miscellaneous'
            elif any(fee in weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)] 
                    for fee in ['ACH RETURN', 'FOREIGN CURRENCY', 'RETURNED ITEM', 'WIRE TRANSFER*']):
                return weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)], 'Miscellaneous'
            else:
                return weird_descriptions['Expense'][random.randint(0, len(weird_descriptions['Expense'])-1)], 'Miscellaneous'
    
    # Standard descriptions for the remaining 70%
    if transaction_type == 'Sale':
        if category == 'Coffee':
            return random.choice([
                'Latte Sale',
                'Cappuccino Sale',
                'Cold Brew Sale',
                'Espresso Sale'
            ]), category
        elif category == 'Pastry':
            return random.choice([
                'Scone Sale',
                'Muffin Sale',
                'Danish Sale',
                'Bagel Sale'
            ]), category
        elif category == 'Sandwich':
            return random.choice([
                'BLT Sale',
                'Turkey Panini Sale',
                'Chicken Club Sale',
                'Grilled Cheese Sale',
                'Veggie Wrap Sale'
            ]), category
        elif category == 'Catering':
            return random.choice([
                'Birthday Party Sale',
                'Holiday Party Sale',
                'Corporate Event Sale',
                'Office Meeting Sale'
            ]), category
        elif category == 'Merchandise':
            return random.choice([
                'Mug Sale',
                'Hat Sale',
                'Thermos Sale'
            ]), category
        else:
            return 'Miscellaneous Sale', 'Miscellaneous'
    else:  # Expense or Refund
        if category == 'Supplies':
            return random.choice([
                'Coffee Beans',
                'Milk',
                'Cups',
                'Napkins'
            ]), category
        elif category == 'Marketing':
            return random.choice([
                'Promotional Event',
                'Email Campaign'
            ]), category
        elif category == 'Maintenance':
            return random.choice([
                'Electrical Work',
                'Plumbing Fix',
                'Equipment Repair',
                'General Maintenance'
            ]), category
        elif category == 'Utilities':
            return random.choice([
                'Electric Bill',
                'Internet Bill',
                'Water Bill',
                'Utility Payment'
            ]), category
        elif category == 'Payroll':
            return random.choice([
                'Wages',
                'Staff Payment'
            ]), category
        elif category == 'Rent':
            return random.choice([
                'Property Rent',
                'Store Rent',
                'Monthly Rent',
                'Lease Payment'
            ]), category
        elif category == 'Refund':
            return random.choice([
                'Order Error',
                'Cancellation'
            ]), category
        else:
            return 'Miscellaneous Expense', 'Miscellaneous'

# Determine account type based on payment method
def get_account_type(payment_method):
    if payment_method in ['Debit Card', 'Mobile Payment']:
        return 'Checking Account'
    elif payment_method == 'Credit Card':
        return 'Credit Account'
    else:
        return 'Cash Account'

# Generate transactions
transactions = []
current_date = START_DATE
while current_date <= END_DATE:
    # Generate a random number of transactions for the current day
    num_transactions = random.randint(50, 100)  # Adjust as needed to meet the minimum
    for _ in range(num_transactions):
        transaction_type = random.choices(list(TRANSACTION_TYPES.keys()), list(TRANSACTION_TYPES.values()))[0]
        if transaction_type in ['Sale', 'Refund']:
            category = random.choice(CATEGORIES[transaction_type])
        else:
            category = random.choice(CATEGORIES['Expense'])
        amount = generate_amount(transaction_type, category)
        date_time = generate_datetime()
        description, category = generate_description(transaction_type, category)
        payment_method = random.choice(PAYMENT_METHODS)
        account_type = get_account_type(payment_method)
        transactions.append({
            'date': date_time.strftime('%Y-%m-%d'),
            'time': date_time.strftime('%H:%M:%S'),
            'description': description,
            'amount': amount,
            'category': category,
            'transaction_type': transaction_type,
            'payment_method': payment_method,
            'account_type': account_type
        })
    current_date += timedelta(days=1)

# Ensure at least 30,000 transactions
if len(transactions) < MIN_TRANSACTIONS:
    additional_transactions = MIN_TRANSACTIONS - len(transactions)
    for _ in range(additional_transactions):
        transaction_type = random.choices(list(TRANSACTION_TYPES.keys()), list(TRANSACTION_TYPES.values()))[0]
        if transaction_type in ['Sale', 'Refund']:
            category = random.choice(CATEGORIES[transaction_type])
        else:
            category = random.choice(CATEGORIES['Expense'])
        amount = generate_amount(transaction_type, category)
        date_time = generate_datetime()
        description, category = generate_description(transaction_type, category)
        payment_method = random.choice(PAYMENT_METHODS)
        account_type = get_account_type(payment_method)
        transactions.append({
            'date': date_time.strftime('%Y-%m-%d'),
            'time': date_time.strftime('%H:%M:%S'),
            'description': description,
            'amount': amount,
            'category': category,
            'transaction_type': transaction_type,
            'payment_method': payment_method,
            'account_type': account_type
        })

# Convert to DataFrame and save to CSV
df = pd.DataFrame(transactions)
df = df.sort_values(by=['date', 'time'])
df.to_csv('data/all_transactions.csv', index=False)

print(f"Generated {len(transactions)} realistic transactions over 5 years.") 