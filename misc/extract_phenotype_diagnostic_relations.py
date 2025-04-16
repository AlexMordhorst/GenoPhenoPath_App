#!/usr/bin/env python3
"""
Extract phenotype-diagnostic relationships from maxo_diagnostic_annotations.txt file
"""
import csv
import os

# Path to input file
input_file = os.path.join('Data', 'archive', 'maxo_diagnostic_annotations.txt')
output_file = 'phenotype_diagnostic_relations.csv'

# List to store phenotype-diagnostic relationships
relations = []

# Read the input file
with open(input_file, 'r', encoding='utf-8') as f:
    # Create a csv reader with tab delimiter
    reader = csv.reader(f, delimiter='\t')
    
    # Skip header row
    header = next(reader)
    
    # Extract HPO IDs (column index 0) and MAXO labels (column index 4)
    for row in reader:
        if len(row) > 4:
            hpo_id = row[0]
            maxo_label = row[4]
            relations.append((hpo_id, maxo_label))

# Write phenotype-diagnostic relations to CSV file
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['hpo_id', 'maxo_label'])  # Header
    for hpo, maxo in relations:
        writer.writerow([hpo, maxo])

print(f"Extracted {len(relations)} phenotype-diagnostic relationships to {output_file}")