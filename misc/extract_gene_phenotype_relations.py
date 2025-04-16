#!/usr/bin/env python3
"""
Extract gene-phenotype relationships from genes_to_phenotype.txt file
"""
import csv
import os

# Path to input file
input_file = os.path.join('Data', 'genes_to_phenotype.txt')
output_file = 'gene_phenotype_relations.csv'

# List to store gene-phenotype relationships
relations = []

# Read the input file
with open(input_file, 'r', encoding='utf-8') as f:
    # Create a csv reader with tab delimiter
    reader = csv.reader(f, delimiter='\t')
    
    # Skip header row
    header = next(reader)
    
    # Extract gene symbols (column index 1) and HPO IDs (column index 2)
    for row in reader:
        if len(row) > 2:
            gene_symbol = row[1]
            hpo_id = row[2]
            relations.append((gene_symbol, hpo_id))

# Write gene-phenotype relations to CSV file
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['gene_symbol', 'hpo_id'])  # Header
    for gene, hpo in relations:
        writer.writerow([gene, hpo])

print(f"Extracted {len(relations)} gene-phenotype relationships to {output_file}")