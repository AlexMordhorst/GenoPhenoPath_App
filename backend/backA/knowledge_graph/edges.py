"""
Edge creation for the GenoPhenoPath knowledge graph.

This module handles the creation of relationships between entities (Gene-Phenotype and 
Phenotype-Diagnostic) in the ontology based on the loaded data.

Functions in this module are used in:
- backend.backA.knowledge_graph.builder: For building the complete knowledge graph
"""

from typing import Any, Dict
import pandas as pd

def create_gene_phenotype_relations(onto: Any, gene_phenotype_data: pd.DataFrame) -> None:
    """
    Establish gene-to-phenotype relationships in the ontology.
    
    Args:
        onto: Ontology instance with defined classes and nodes
        gene_phenotype_data: DataFrame containing gene-phenotype mappings
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    # Group phenotypes by gene and establish connections
    gene_considered = gene_phenotype_data.iloc[0]["gene_symbol"]  # Start with first gene
    phen_list = []  # Initialize list to collect phenotypes for current gene
    
    for index, entry in gene_phenotype_data.iterrows():
        if gene_considered == entry["gene_symbol"]:
            # Add phenotype to the current gene's list
            phen_list.append(onto.Phenotype(entry["hpo_id"]))
        elif gene_considered is not entry["gene_symbol"]:
            # When we encounter a new gene, connect the previous gene to all its phenotypes
            onto.Gene(gene_considered).ConnectedTo = phen_list
            # Reset for next gene
            phen_list = []
            gene_considered = entry["gene_symbol"]
            phen_list.append(onto.Phenotype(entry["hpo_id"]))
    
    # Don't forget to connect the last gene to its phenotypes
    if phen_list:
        onto.Gene(gene_considered).ConnectedTo = phen_list

def create_phenotype_diagnostic_relations(onto: Any, diagnostic_data: pd.DataFrame) -> None:
    """
    Establish phenotype-to-diagnostic relationships in the ontology.
    
    Args:
        onto: Ontology instance with defined classes and nodes
        diagnostic_data: DataFrame containing phenotype-diagnostic mappings
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    # Group diagnostics by phenotype and establish connections
    phen_considered = diagnostic_data.iloc[0]["hpo_id"]  # Start with first phenotype
    diag_list = []  # Initialize list to collect diagnostics for current phenotype
    
    for index, entry in diagnostic_data.iterrows():
        if phen_considered == entry["hpo_id"]:
            # Add diagnostic to the current phenotype's list
            diag_list.append(onto.Diagnostic(entry["maxo_label"]))
        elif phen_considered is not entry["hpo_id"]:
            # When we encounter a new phenotype, connect the previous phenotype to all its diagnostics
            onto.Phenotype(phen_considered).ConnectedTo = diag_list
            # Reset for next phenotype
            diag_list = []
            phen_considered = entry["hpo_id"]
            diag_list.append(onto.Diagnostic(entry["maxo_label"]))
    
    # Don't forget to connect the last phenotype to its diagnostics
    if diag_list:
        onto.Phenotype(phen_considered).ConnectedTo = diag_list