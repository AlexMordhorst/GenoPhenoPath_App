"""
Knowledge graph builder for the GenoPhenoPath application.

This module orchestrates the creation of the complete knowledge graph by coordinating
data loading, ontology schema creation, and entity/relationship population.

Functions in this module are used in:
- backend.backA.network.generator: For creating the NetworkX graph from the ontology
"""

from typing import Any, Dict, Tuple
import owlready2 as owl

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

def build_knowledge_graph() -> Tuple[Any, Dict[str, list]]:
    """
    Build the complete knowledge graph from data sources.
    
    This function orchestrates the entire knowledge graph creation process:
    1. Load all necessary data directly from individual loaders
    2. Create ontology schema
    3. Populate nodes (genes, phenotypes, diagnostics)
    4. Establish relationships between nodes
    5. Extract node communities for visualization
    
    Returns:
        Tuple containing:
        - Populated ontology instance
        - Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Used in:
    - backend.backA.network.generator.create_networkx_graph
    """
    # Load data directly using individual loaders
    unique_genes = load_unique_genes()
    unique_phenotypes = load_unique_phenotypes()
    unique_diagnostics = load_unique_diagnostics()
    gene_phenotype_relations = load_gene_phenotype_relations()
    phenotype_diagnostic_relations = load_phenotype_diagnostic_relations()
    
    # Create ontology schema
    onto = create_ontology_schema()
    
    # Populate nodes
    create_gene_nodes(onto, unique_genes)
    create_phenotype_nodes(onto, unique_phenotypes)
    create_diagnostic_nodes(onto, unique_diagnostics)
    
    # Establish relationships
    create_gene_phenotype_relations(onto, gene_phenotype_relations)
    create_phenotype_diagnostic_relations(onto, phenotype_diagnostic_relations)
    
    # Extract node communities
    communities = extract_node_communities(onto)
    
    return onto, communities