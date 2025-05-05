#!/usr/bin/env python3
"""
Script to extract unique HPO IDs and names from genes_to_phenotype.txt and 
rebuild unique_phenotypes.csv with this data.
"""

import csv
import pandas as pd

def rebuild_unique_phenotypes():
    """
    Extract unique HPO IDs and names from genes_to_phenotype.txt and rebuild
    unique_phenotypes.csv with this data.
    """
    print("Reading genes_to_phenotype.txt to extract unique HPO entries...")
    
    # Dictionary to store HPO ID to name mappings
    hpo_mapping = {}
    
    # Read genes_to_phenotype.txt to extract HPO IDs and names
    with open('Data/archive/genes_to_phenotype.txt', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip header
        
        for row in reader:
            try:
                hpo_id = row[2]
                hpo_name = row[3]
                
                # Store the first occurrence of each HPO ID
                if hpo_id not in hpo_mapping:
                    hpo_mapping[hpo_id] = hpo_name
            except IndexError:
                continue  # Skip malformed rows
    
    print(f"Extracted {len(hpo_mapping)} unique HPO IDs with names.")
    
    # Create DataFrame from the mapping
    hpo_df = pd.DataFrame({
        'hpo_id': list(hpo_mapping.keys()),
        'hpo_name': list(hpo_mapping.values())
    })
    
    # Sort by HPO ID
    hpo_df = hpo_df.sort_values('hpo_id').reset_index(drop=True)
    
    # Save as the new unique_phenotypes.csv
    print("Saving new unique_phenotypes.csv...")
    hpo_df.to_csv('Data/unique_phenotypes.csv', index=False)
    
    # Print sample of the data
    print("\nSample of the new unique_phenotypes.csv:")
    print(hpo_df.head())
    
    print(f"\nSuccessfully rebuilt unique_phenotypes.csv with {len(hpo_df)} unique HPO entries.")

if __name__ == "__main__":
    rebuild_unique_phenotypes()