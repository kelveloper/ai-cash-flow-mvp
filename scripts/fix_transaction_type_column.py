import csv
from collections import Counter

input_file = 'data/all_transactions.csv'
output_file = 'data/all_transactions_ready.csv'

# Mapping for transaction_type to type
TYPE_MAP = {
    'Sale': 'income',
    'Expense': 'expense',
    'Refund': 'income',
}

# Mapping for category to allowed backend values
CATEGORY_MAP = {
    'Catering': 'groceries',
    'Coffee': 'groceries',
    'Pastry': 'groceries',
    'Sandwich': 'groceries',
    'Maintenance': 'utilities',
    'Utilities': 'utilities',
    'Marketing': 'entertainment',
    'Promotional Event': 'entertainment',
    'Merchandise': 'other',
    'Miscellaneous': 'other',
    'Supplies': 'other',
    'Payroll': 'salary',
    'Rent': 'rent',
}

ALLOWED_CATEGORIES = set([
    'salary', 'rent', 'utilities', 'groceries', 'transportation', 'entertainment', 'healthcare', 'other'
])

def main():
    with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = [fn if fn != 'transaction_type' else 'type' for fn in reader.fieldnames]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        type_counter = Counter()
        category_counter = Counter()
        for row in reader:
            # Fix type
            orig_type = row.get('transaction_type', '').strip()
            mapped_type = TYPE_MAP.get(orig_type, 'income' if orig_type.lower() in ['sale', 'refund'] else 'expense')
            row['type'] = mapped_type
            del row['transaction_type']
            type_counter[(orig_type, mapped_type)] += 1
            # Fix category
            orig_cat = row.get('category', '').strip()
            mapped_cat = CATEGORY_MAP.get(orig_cat, 'other')
            if mapped_cat not in ALLOWED_CATEGORIES:
                mapped_cat = 'other'
            row['category'] = mapped_cat
            category_counter[(orig_cat, mapped_cat)] += 1
            writer.writerow(row)
    print('Type mapping summary:')
    for (orig, mapped), count in type_counter.items():
        print(f"{orig} → {mapped}: {count}")
    print('Category mapping summary:')
    for (orig, mapped), count in category_counter.items():
        print(f"{orig} → {mapped}: {count}")
    print(f"Output written to {output_file}")

if __name__ == '__main__':
    main() 