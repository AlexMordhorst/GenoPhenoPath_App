#!/usr/bin/env python3
"""
Extract unique gene symbols from genes_to_phenotype.txt file
"""
import csv
import os

# Path to input file
input_file = os.path.join('Data', 'genes_to_phenotype.txt')
output_file = 'unique_genes.csv'

# Set to store unique gene symbols
unique_genes = set()

# Read the input file
with open(input_file, 'r', encoding='utf-8') as f:
    # Create a csv reader with tab delimiter
    reader = csv.reader(f, delimiter='\t')
    
    # Skip header row
    next(reader)
    
    # Extract gene symbols (column index 1)
    for row in reader:
        if len(row) > 1:
            gene_symbol = row[1]
            unique_genes.add(gene_symbol)

# Write unique genes to CSV file
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['gene_symbol'])  # Header
    for gene in sorted(unique_genes):
        writer.writerow([gene])

print(f"Extracted {len(unique_genes)} unique gene symbols to {output_file}")