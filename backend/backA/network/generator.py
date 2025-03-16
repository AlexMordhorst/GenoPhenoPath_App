"""
NetworkX graph generator for the GenoPhenoPath application.

This module converts the ontology-based knowledge graph into a NetworkX directed graph
for analysis and visualization.

Functions in this module are used in:
- backend.backB.layout.positions: For creating 3D layout with positioned nodes
- backend.backC.statistics.metrics: For calculating graph statistics
"""

import networkx as nx
from typing import Any, Dict, Tuple

def create_networkx_graph(onto: Any, communities: Dict[str, list]) -> Tuple[nx.DiGraph, Dict]:
    """
    Convert the ontology knowledge graph to a NetworkX directed graph.
    
    Args:
        onto: Populated ontology instance
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Returns:
        Tuple containing:
        - NetworkX directed graph
        - Dictionary with edge types and counts
        
    Used in:
    - backend.backB.layout.positions.create_3d_layout
    - backend.backC.statistics.metrics.calculate_graph_statistics
    """
    # Create directed graph to represent our knowledge graph
    G = nx.DiGraph()
    
    # Track edge counts for statistics
    edge_counts = {
        "gene_to_pheno_edges": 0,
        "pheno_to_diag_edges": 0
    }

    # Add all nodes and edges to the graph from our ontology
    # First, add diagnostic nodes
    for nodediag in onto.Diagnostic.instances():
        G.add_node(nodediag.name, label=nodediag.is_a[0].name)
        
    # Add phenotype nodes
    for nodephen in onto.Phenotype.instances():
        G.add_node(nodephen.name, label=nodephen.is_a[0].name)
        
    # Add gene nodes and gene->phenotype edges
    for nodegene in onto.Gene.instances():
        G.add_node(nodegene.name, label=nodegene.is_a[0].name)
        for genephenconnected in nodegene.ConnectedTo:
            G.add_edge(nodegene.name, genephenconnected.name)
            edge_counts["gene_to_pheno_edges"] += 1
            
    # Add phenotype->diagnostic edges
    for nodephen in onto.Phenotype.instances():
        for phendiagconnected in nodephen.ConnectedTo:
            G.add_edge(nodephen.name, phendiagconnected.name)
            edge_counts["pheno_to_diag_edges"] += 1
    
    # Calculate total edges
    edge_counts["total_edges"] = edge_counts["gene_to_pheno_edges"] + edge_counts["pheno_to_diag_edges"]
    
    return G, edge_counts