"""
Data loading and preparation for the GenoPhenoPath application.

This module handles loading genomics data, diagnostic annotations, and gene-phenotype mappings
from various data sources.

Functions in this module are used in:
- backend.backA.knowledge_graph.nodes: For creating ontology node entities
- backend.backA.knowledge_graph.edges: For establishing relationships between entities
- backend.backA.network.generator: For creating the NetworkX graph
"""

import pandas as pd
from typing import Tuple, Dict
import os


def load_unique_genes(file_path: str = "./Data/unique_genes.csv") -> pd.DataFrame:
    """
    Load unique gene data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing unique genes
        
    Returns:
        DataFrame with unique genes
    """
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["gene_symbol"])

def load_unique_phenotypes(file_path: str = "./Data/unique_phenotypes.csv") -> pd.DataFrame:
    """
    Load unique phenotype data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing unique phenotypes
        
    Returns:
        DataFrame with unique phenotypes
    """
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["hpo_id"])

def load_unique_diagnostics(file_path: str = "./Data/unique_diagnostics.csv") -> pd.DataFrame:
    """
    Load unique diagnostic procedures data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing unique diagnostic procedures
        
    Returns:
        DataFrame with unique diagnostic procedures
    """
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["maxo_label"])

def load_gene_phenotype_relations(file_path: str = "./Data/gene_phenotype_relations.csv") -> pd.DataFrame:
    """
    Load gene-to-phenotype relation data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing gene-phenotype relations
        
    Returns:
        DataFrame with gene-phenotype relations
    """
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["gene_symbol", "hpo_id"])

def load_phenotype_diagnostic_relations(file_path: str = "./Data/phenotype_diagnostic_relations.csv") -> pd.DataFrame:
    """
    Load phenotype-to-diagnostic relation data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing phenotype-diagnostic relations
        
    Returns:
        DataFrame with phenotype-diagnostic relations
    """
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["hpo_id", "maxo_label"])
