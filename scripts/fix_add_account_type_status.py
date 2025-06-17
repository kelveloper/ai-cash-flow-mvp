import csv

input_file = 'data/all_transactions.csv'
temp_file = 'data/all_transactions_temp.csv'

with open(input_file, 'r', newline='') as infile, open(temp_file, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    # Ensure both fields are present
    if 'account_type' not in fieldnames:
        fieldnames.append('account_type')
    if 'status' not in fieldnames:
        fieldnames.append('status')
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        row['account_type'] = row.get('account_type', 'Checking Account') or 'Checking Account'
        row['status'] = row.get('status', 'posted') or 'posted'
        writer.writerow(row)

import os
os.replace(temp_file, input_file)

print('Done! All transactions now have account_type and status.') 