#!/usr/bin/env python3
"""
Extract unique HPO IDs from gene_phenotype_relations.csv and add HPO names from genes_to_phenotype.txt
"""
import csv
import os
import pandas as pd

# Path to input files
input_file = os.path.join('Data', 'gene_phenotype_relations.csv')
genes_to_phenotype_file = os.path.join('Data', 'archive', 'genes_to_phenotype.txt')
output_file = os.path.join('Data', 'unique_phenotypes.csv')

# Set to store unique HPO IDs
unique_phenotypes = set()

# Read the input file to get unique HPO IDs
print("Reading gene_phenotype_relations.csv for unique HPO IDs...")
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

print(f"Found {len(unique_phenotypes)} unique HPO IDs.")

# Create a dictionary to map HPO IDs to names
print(f"Reading {genes_to_phenotype_file} to extract HPO names...")
hpo_id_to_name = {}

# Read genes_to_phenotype.txt to extract HPO names
with open(genes_to_phenotype_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)  # Skip header
    
    for row in reader:
        try:
            hpo_id = row[2]
            hpo_name = row[3]
            
            # Store the first occurrence of each HPO ID
            if hpo_id not in hpo_id_to_name:
                hpo_id_to_name[hpo_id] = hpo_name
        except IndexError:
            continue  # Skip malformed rows

print(f"Extracted {len(hpo_id_to_name)} unique HPO ID-name mappings.")

# Write unique HPO IDs with names to CSV file
print(f"Writing to {output_file}...")
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['hpo_id', 'hpo_name'])  # Updated header
    
    # Count HPO IDs with names
    match_count = 0
    
    for hpo_id in sorted(unique_phenotypes):
        hpo_name = hpo_id_to_name.get(hpo_id, "Unknown")
        writer.writerow([hpo_id, hpo_name])
        if hpo_name != "Unknown":
            match_count += 1

print(f"Extracted {len(unique_phenotypes)} unique phenotypes to {output_file}")
print(f"Found names for {match_count}/{len(unique_phenotypes)} HPO IDs ({match_count/len(unique_phenotypes)*100:.1f}%)")