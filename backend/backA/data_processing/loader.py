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

def load_genome_data(file_path: str = "./Data/vartest.tsv") -> pd.DataFrame:
    """
    Load and filter patient genome sequencing data.
    
    Args:
        file_path: Path to the TSV file containing genome data
        
    Returns:
        Filtered DataFrame with relevant columns and rows
    
    Used in:
    - backend.backA.knowledge_graph.nodes.create_gene_nodes
    """
    table = pd.read_csv(file_path, sep='\t')
    table2 = table.iloc[:, [0,1,2,3,6,8,22,24,25,26,40]].sort_values(
        "Pathogenicity Score", ascending=False
    ).loc[table["Pathogenicity Score"] >= 15]
    
    return table2

def load_diagnostic_annotations(file_path: str = "./Data/maxo_diagnostic_annotations2.txt") -> pd.DataFrame:
    """
    Load diagnostic annotations data that maps HPO terms to diagnostic procedures (MAXO terms).
    
    Args:
        file_path: Path to the TSV file containing diagnostic annotations
        
    Returns:
        DataFrame with HPO to MAXO mappings
    
    Used in:
    - backend.backA.knowledge_graph.nodes.create_diagnostic_nodes
    - backend.backA.knowledge_graph.edges.create_phenotype_diagnostic_relations
    """
    return pd.read_csv(file_path, sep='\t')

def load_gene_phenotype_mappings(
    file_path: str = "./Data/genes_to_phenotype.txt", 
    genome_data: pd.DataFrame = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load gene-to-phenotype mapping data and filter based on genes from genome data.
    
    Args:
        file_path: Path to the TSV file containing gene-phenotype mappings
        genome_data: DataFrame containing genome data to filter gene-phenotype mappings
        
    Returns:
        Tuple containing:
        - Filtered gene-phenotype DataFrame
        - Unique genes DataFrame
        - Unique phenotypes DataFrame
    
    Used in:
    - backend.backA.knowledge_graph.nodes.create_gene_nodes
    - backend.backA.knowledge_graph.nodes.create_phenotype_nodes
    - backend.backA.knowledge_graph.edges.create_gene_phenotype_relations
    """
    gene2phen = pd.read_csv(file_path, sep='\t')
    
    if genome_data is not None:
        gene2phen2 = gene2phen[gene2phen["gene_symbol"].isin(genome_data["Gene Symbol"])]
    else:
        gene2phen2 = gene2phen
    
    # Create deduplicated dataframes for unique genes and phenotypes
    gene2phen2sg = gene2phen2.drop_duplicates(subset=["gene_symbol"])  # One row per unique gene
    gene2phen2sp = gene2phen2.drop_duplicates(subset=["hpo_id"])       # One row per unique phenotype
    
    return gene2phen2, gene2phen2sg, gene2phen2sp

def load_all_data() -> Dict:
    """
    Load all required datasets and return them in a dictionary.
    
    Returns:
        Dictionary containing all loaded datasets:
        - genome_data: Filtered genome data
        - diagnostic_data: HPO to MAXO mappings
        - gene_phenotype: Filtered gene-phenotype mappings
        - unique_genes: DataFrame with unique genes
        - unique_phenotypes: DataFrame with unique phenotypes
    
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    genome_data = load_genome_data()
    diagnostic_data = load_diagnostic_annotations()
    gene_phenotype, unique_genes, unique_phenotypes = load_gene_phenotype_mappings(
        genome_data=genome_data
    )
    
    return {
        "genome_data": genome_data,
        "diagnostic_data": diagnostic_data,
        "gene_phenotype": gene_phenotype,
        "unique_genes": unique_genes,
        "unique_phenotypes": unique_phenotypes
    }