"""
Knowledge graph builder for the GenoPhenoPath application.

This module orchestrates the creation of the complete knowledge graph by coordinating
data loading, ontology schema creation, and entity/relationship population.

Functions in this module are used in:
- backend.backA.network.generator: For creating the NetworkX graph from the ontology
"""

from typing import Any, Dict, Tuple, List, Optional
import owlready2 as owl
import pandas as pd

from backend.backA.data_processing.loader import (
    load_unique_genes,
    load_unique_phenotypes,
    load_unique_diagnostics,
    load_gene_phenotype_relations,
    load_phenotype_diagnostic_relations
)
from backend.backA.ontology.schema import create_ontology_schema
from backend.backA.knowledge_graph.nodes import (
    create_gene_nodes, 
    create_phenotype_nodes, 
    create_diagnostic_nodes,
    extract_node_communities
)
from backend.backA.knowledge_graph.edges import (
    create_gene_phenotype_relations,
    create_phenotype_diagnostic_relations
)

def build_knowledge_graph(selected_genes: Optional[List[str]] = None) -> Tuple[Any, Dict[str, list]]:
    """
    Build the complete knowledge graph from data sources.
    
    This function orchestrates the entire knowledge graph creation process:
    1. Load all necessary data directly from individual loaders
    2. Filter data based on selected genes (if provided)
    3. Create ontology schema
    4. Populate nodes (genes, phenotypes, diagnostics)
    5. Establish relationships between nodes
    6. Extract node communities for visualization
    
    Args:
        selected_genes: Optional list of gene symbols to filter the graph
    
    Returns:
        Tuple containing:
        - Populated ontology instance
        - Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Used in:
    - backend.backA.network.generator.create_networkx_graph
    """
    # Debug print for selected genes
    print(f"DEBUG - Selected genes in build_knowledge_graph: {selected_genes if selected_genes else 'None'}")
    
    # Load data directly using individual loaders
    unique_genes = load_unique_genes()
    
    # Load all data first
    unique_phenotypes = load_unique_phenotypes()
    unique_diagnostics = load_unique_diagnostics()
    gene_phenotype_relations = load_gene_phenotype_relations()
    phenotype_diagnostic_relations = load_phenotype_diagnostic_relations()
    
    # Filter genes if a selection is provided
    if selected_genes and len(selected_genes) > 0:
        # Print sizes before filtering
        print(f"DEBUG - Before filtering: {len(unique_genes)} genes, {len(unique_phenotypes)} phenotypes, {len(unique_diagnostics)} diagnostics")
        
        # Filter to only include the selected genes
        unique_genes = unique_genes[unique_genes['gene_symbol'].isin(selected_genes)]
        print(f"DEBUG - After gene filtering: {len(unique_genes)} genes")
        
        # Filter to only include relations for selected genes
        gene_phenotype_relations = gene_phenotype_relations[
            gene_phenotype_relations['gene_symbol'].isin(selected_genes)
        ]
        print(f"DEBUG - After relation filtering: {len(gene_phenotype_relations)} gene-phenotype relations")
        
        # Get phenotypes related to selected genes
        related_phenotypes = gene_phenotype_relations['hpo_id'].unique().tolist()
        print(f"DEBUG - Related phenotypes: {len(related_phenotypes)}")
        
        # Filter phenotypes to only include related ones
        unique_phenotypes = unique_phenotypes[
            unique_phenotypes['hpo_id'].isin(related_phenotypes)
        ]
        print(f"DEBUG - After phenotype filtering: {len(unique_phenotypes)} phenotypes")
        
        # Filter phenotype-diagnostic relations
        phenotype_diagnostic_relations = phenotype_diagnostic_relations[
            phenotype_diagnostic_relations['hpo_id'].isin(related_phenotypes)
        ]
        print(f"DEBUG - After relation filtering: {len(phenotype_diagnostic_relations)} phenotype-diagnostic relations")
        
        # Get diagnostics related to the filtered phenotypes
        related_diagnostics = phenotype_diagnostic_relations['maxo_label'].unique().tolist()
        print(f"DEBUG - Related diagnostics: {len(related_diagnostics)}")
        
        # Filter diagnostics to only include related ones
        unique_diagnostics = unique_diagnostics[
            unique_diagnostics['maxo_label'].isin(related_diagnostics)
        ]
        print(f"DEBUG - After diagnostic filtering: {len(unique_diagnostics)} diagnostics")
    
    # Create ontology schema
    onto = create_ontology_schema()
    
    # Populate nodes
    print(f"DEBUG - Adding nodes to ontology: {len(unique_genes)} genes, {len(unique_phenotypes)} phenotypes, {len(unique_diagnostics)} diagnostics")
    create_gene_nodes(onto, unique_genes)
    create_phenotype_nodes(onto, unique_phenotypes)
    create_diagnostic_nodes(onto, unique_diagnostics)
    
    # Establish relationships
    print(f"DEBUG - Creating relationships: {len(gene_phenotype_relations)} gene-phenotype, {len(phenotype_diagnostic_relations)} phenotype-diagnostic")
    create_gene_phenotype_relations(onto, gene_phenotype_relations)
    create_phenotype_diagnostic_relations(onto, phenotype_diagnostic_relations)
    
    # Extract node communities
    communities = extract_node_communities(onto)
    
    return onto, communities