#!/usr/bin/env python3
"""
Extract unique HPO IDs from gene_phenotype_relations.csv
"""
import csv
import os

# Path to input file
input_file = os.path.join('Data', 'gene_phenotype_relations.csv')
output_file = 'unique_phenotypes.csv'

# Set to store unique HPO IDs
unique_phenotypes = set()

# Read the input file
with open(input_file, 'r', encoding='utf-8') as f:
    # Create a csv reader
    reader = csv.reader(f)
    
    # Skip header row
    next(reader)
    
    # Extract HPO IDs (column index 1)
    for row in reader:
        if len(row) > 1:
            hpo_id = row[1]
            unique_phenotypes.add(hpo_id)

# Write unique HPO IDs to CSV file
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['hpo_id'])  # Header
    for hpo_id in sorted(unique_phenotypes):
        writer.writerow([hpo_id])

print(f"Extracted {len(unique_phenotypes)} unique phenotypes to {output_file}")