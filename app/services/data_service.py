def get_transactions():
    transactions = [
        {
            "date": "2024-12-20",
            "amount": "$300.00",
            "type": "expense",
            "category": "entertainment",
            "description": "Holiday Gifts and Parties",
            "status": "posted"
        },
        {
            "date": "2024-12-15",
            "amount": "$5000.00",
            "type": "income",
            "category": "salary",
            "description": "Monthly Salary",
            "status": "posted"
        },
        {
            "date": "2024-12-10",
            "amount": "$150.00",
            "type": "expense",
            "category": "utilities",
            "description": "Electric Bill",
            "status": "pending"
        },
        {
            "date": "2024-12-01",
            "amount": "$2000.00",
            "type": "expense",
            "category": "rent",
            "description": "Monthly Rent",
            "status": "posted"
        },
        {
            "date": "2024-11-15",
            "amount": "$5000.00",
            "type": "income",
            "category": "salary",
            "description": "Monthly Salary",
            "status": "posted"
        },
        {
            "date": "2024-11-10",
            "amount": "$75.00",
            "type": "expense",
            "category": "entertainment",
            "description": "Regular Entertainment",
            "status": "posted"
        },
        {
            "date": "2024-11-01",
            "amount": "$2000.00",
            "type": "expense",
            "category": "rent",
            "description": "Monthly Rent",
            "status": "posted"
        }
    ]
    return transactions

def get_forecast(start_date, end_date, category=None):
    # Generate monthly labels
    labels = []
    current_date = start_date
    while current_date <= end_date:
        labels.append(current_date.strftime("%Y-%m"))
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    
    # Generate forecast data
    income = [5000] * len(labels)  # Monthly salary
    expenses = [2000] * len(labels)  # Monthly rent
    expenses = [x + 300 for x in expenses]  # Add utilities
    expenses = [x + 150 for x in expenses]  # Add entertainment
    
    # Calculate net cash flow
    net_cash_flow = [i - e for i, e in zip(income, expenses)]
    
    return {
        "labels": labels,
        "income": income,
        "expenses": expenses,
        "net_cash_flow": net_cash_flow
    } 