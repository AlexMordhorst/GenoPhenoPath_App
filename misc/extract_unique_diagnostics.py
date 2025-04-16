#!/usr/bin/env python3
"""
Extract unique MAXO labels from phenotype_diagnostic_relations.csv
"""
import csv
import os

# Path to input file
input_file = os.path.join('Data', 'phenotype_diagnostic_relations.csv')
output_file = 'unique_diagnostics.csv'

# Set to store unique MAXO labels
unique_diagnostics = set()

# Read the input file
with open(input_file, 'r', encoding='utf-8') as f:
    # Create a csv reader
    reader = csv.reader(f)
    
    # Skip header row
    next(reader)
    
    # Extract MAXO labels (column index 1)
    for row in reader:
        if len(row) > 1:
            maxo_label = row[1]
            unique_diagnostics.add(maxo_label)

# Write unique MAXO labels to CSV file
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['maxo_label'])  # Header
    for maxo_label in sorted(unique_diagnostics):
        writer.writerow([maxo_label])

print(f"Extracted {len(unique_diagnostics)} unique diagnostic labels to {output_file}")