"""
Knowledge graph builder for the GenoPhenoPath application.

This module orchestrates the creation of the complete knowledge graph by coordinating
data loading, ontology schema creation, and entity/relationship population.

Functions in this module are used in:
- backend.backA.network.generator: For creating the NetworkX graph from the ontology
"""

from typing import Any, Dict, Tuple
import owlready2 as owl

from backend.backA.data_processing.loader import load_all_data
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
    1. Load all necessary data
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
    # Load all required data
    data = load_all_data()
    
    # Create ontology schema
    onto = create_ontology_schema()
    
    # Populate nodes
    create_gene_nodes(onto, data["unique_genes"])
    create_phenotype_nodes(onto, data["unique_phenotypes"])
    create_diagnostic_nodes(onto, data["diagnostic_data"])
    
    # Establish relationships
    create_gene_phenotype_relations(onto, data["gene_phenotype"])
    create_phenotype_diagnostic_relations(onto, data["diagnostic_data"])
    
    # Extract node communities
    communities = extract_node_communities(onto)
    
    return onto, communities