"""
Node creation for the GenoPhenoPath knowledge graph.

This module handles the creation of node entities (Gene, Phenotype, Diagnostic) in the ontology
based on the data loaded from various sources.

Functions in this module are used in:
- backend.backA.knowledge_graph.builder: For building the complete knowledge graph
"""

from typing import Any, List, Dict
import pandas as pd

def create_gene_nodes(onto: Any, gene_data: pd.DataFrame) -> List[str]:
    """
    Create Gene instances in the ontology from gene data.
    
    Args:
        onto: Ontology instance with defined classes
        gene_data: DataFrame containing unique gene symbols
        
    Returns:
        List of gene names created in the ontology
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    gene_names = []
    for gene in gene_data["gene_symbol"]:
        # Create a new gene instance in the ontology
        my_new_gene = onto.Gene(gene)
        gene_names.append(gene)
    
    return gene_names

def create_phenotype_nodes(onto: Any, phenotype_data: pd.DataFrame) -> List[str]:
    """
    Create Phenotype instances in the ontology from phenotype data.
    
    Args:
        onto: Ontology instance with defined classes
        phenotype_data: DataFrame containing unique phenotype IDs (HPO terms)
        
    Returns:
        List of phenotype IDs created in the ontology
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    phenotype_ids = []
    for phen in phenotype_data["hpo_id"]:
        # Create a new phenotype instance in the ontology
        my_new_phen = onto.Phenotype(phen)
        phenotype_ids.append(phen)
    
    return phenotype_ids

def create_diagnostic_nodes(onto: Any, diagnostic_data: pd.DataFrame) -> List[str]:
    """
    Create Diagnostic instances in the ontology from diagnostic data.
    
    Args:
        onto: Ontology instance with defined classes
        diagnostic_data: DataFrame containing diagnostic procedure labels (MAXO terms)
        
    Returns:
        List of diagnostic labels created in the ontology
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    diagnostic_labels = []
    for diag in diagnostic_data["maxo_label"]:
        # Create a new diagnostic instance in the ontology
        my_new_diag = onto.Diagnostic(diag)
        diagnostic_labels.append(diag)
    
    return diagnostic_labels

def extract_node_communities(onto: Any) -> Dict[str, List[str]]:
    """
    Extract node communities (genes, phenotypes, diagnostics) from the ontology.
    
    Args:
        onto: Ontology instance with populated nodes
        
    Returns:
        Dictionary containing lists of node names by community:
        - genes: List of gene names
        - phenotypes: List of phenotype IDs
        - diagnostics: List of diagnostic labels
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    - backend.backA.network.generator.create_networkx_graph
    """
    community_0 = []  # Genes
    community_1 = []  # Phenotypes
    community_2 = []  # Diagnostics

    # Extract gene names from ontology and remove prefix
    for i in onto.Gene.instances():
        community_0.append(str(i).removeprefix("onto."))

    # Extract phenotype IDs from ontology and remove prefix
    for i in onto.Phenotype.instances():
        community_1.append(str(i).removeprefix("onto."))

    # Extract diagnostic names from ontology and remove prefix
    for i in onto.Diagnostic.instances():
        community_2.append(str(i).removeprefix("onto."))
    
    # Print the number of nodes in each community for debugging
    print(f"DEBUG - Extracted communities: {len(community_0)} genes, {len(community_1)} phenotypes, {len(community_2)} diagnostics")
        
    return {
        "genes": community_0,
        "phenotypes": community_1,
        "diagnostics": community_2
    }