import csv

input_file = 'data/all_transactions.csv'
output_file = 'data/all_transactions_cleaned.csv'

# Track (year, month) for Monthly Rent in description (case-insensitive, trimmed)
rent_seen = set()

with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        desc_clean = row['description'].strip().lower()
        if desc_clean == 'monthly rent':
            year_month = row['date'][:7]  # 'YYYY-MM'
            if year_month in rent_seen:
                continue  # Skip additional Monthly Rent for this month
            rent_seen.add(year_month)
        writer.writerow(row)

print('Done! Cleaned file saved as:', output_file) 