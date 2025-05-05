#!/usr/bin/env python3
"""
Script to extract HPO names from genes_to_phenotype.txt and add them to unique_phenotypes.csv.
"""

import csv
import pandas as pd

def add_hpo_names():
    """
    Extract HPO names from genes_to_phenotype.txt and add them to unique_phenotypes.csv.
    
    This function reads both files, creates a mapping of HPO IDs to names, and then
    adds a new column to unique_phenotypes.csv with the corresponding names.
    """
    print("Reading genes_to_phenotype.txt...")
    
    # Create a dictionary to map HPO IDs to names
    hpo_id_to_name = {}
    
    # Read genes_to_phenotype.txt to extract HPO IDs and names
    with open('Data/archive/genes_to_phenotype.txt', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip header
        
        for row in reader:
            hpo_id = row[2]
            hpo_name = row[3]
            
            # Store the first occurrence of each HPO ID
            if hpo_id not in hpo_id_to_name:
                hpo_id_to_name[hpo_id] = hpo_name
    
    print(f"Extracted {len(hpo_id_to_name)} unique HPO IDs with names.")
    
    # Read unique_phenotypes.csv
    print("Reading unique_phenotypes.csv...")
    df = pd.read_csv('Data/unique_phenotypes.csv')
    
    # Add new column for HPO names
    df['hpo_name'] = df['hpo_id'].map(hpo_id_to_name)
    
    # Handle missing values
    missing_names = df['hpo_name'].isna().sum()
    if missing_names > 0:
        print(f"Warning: {missing_names} HPO IDs did not have corresponding names in genes_to_phenotype.txt")
    
    # Save updated file
    print("Saving updated unique_phenotypes.csv...")
    df.to_csv('Data/unique_phenotypes.csv', index=False)
    
    # Print sample of updated data
    print("\nSample of updated data:")
    print(df.head())
    
    print(f"\nSuccessfully updated unique_phenotypes.csv with HPO names.")

if __name__ == "__main__":
    add_hpo_names()