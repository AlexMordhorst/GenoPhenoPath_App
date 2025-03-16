"""
Graph statistics calculation for the GenoPhenoPath knowledge graph.

This module handles the calculation of various graph metrics and statistics for
displaying information about the knowledge graph structure.

Functions in this module are used in:
- backend.backB.visualization.plotter: For enriching visualization with statistics
- frontend.frontA.session.state: For initializing session state with graph statistics
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any

def calculate_graph_statistics(
    G: nx.Graph, 
    communities: Dict[str, List[str]], 
    edge_counts: Dict[str, int]
) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics about the knowledge graph.
    
    Args:
        G: NetworkX graph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        edge_counts: Dictionary with edge counts by type
        
    Returns:
        Dictionary with graph statistics:
        - Basic counts (nodes, edges, etc.)
        - Node degree statistics by type
        - Connectivity metrics
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    - frontend.frontA.session.state.initialize_session_state
    """
    # Basic counts
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    avg_node_degree = round(np.mean([j for i, j in G.degree()]), 2)
    
    # Gene-specific statistics
    avg_node_degree_gene = round(np.mean([j for i, j in G.degree(communities["genes"])]), 2)
    gene_degrees = [j for i, j in G.degree(communities["genes"])]
    if gene_degrees:
        max_node_degree_gene = np.max(gene_degrees)
        max_node_name_gene = str([tup[0] for tup in G.degree(communities["genes"]) 
                              if tup[1] == max_node_degree_gene]).replace("'","").replace("[","").replace("]","")
        
        non_zero_degrees = [j for j in gene_degrees if j != 0]
        if non_zero_degrees:
            min_node_degree_gene = np.min(non_zero_degrees)
            min_node_name_gene = str([tup[0] for tup in G.degree(communities["genes"]) 
                                  if tup[1] == min_node_degree_gene]).replace("'","").replace("[","").replace("]","")
        else:
            min_node_degree_gene = 0
            min_node_name_gene = "N/A"
        
        gene_nophenotype = str([tup[0] for tup in G.degree(communities["genes"]) 
                            if tup[1] == 0]).replace("'","").replace("[","").replace("]","")
    else:
        max_node_degree_gene = 0
        max_node_name_gene = "N/A"
        min_node_degree_gene = 0
        min_node_name_gene = "N/A"
        gene_nophenotype = "N/A"
    
    # Diagnostic-specific statistics
    diag_degrees = [j for i, j in G.degree(communities["diagnostics"])]
    if diag_degrees:
        avg_node_degree_diagnostic = round(np.mean(diag_degrees), 2)
        max_node_degree_diagnostic = np.max(diag_degrees)
        max_node_name_diagnostic = str([tup[0] for tup in G.degree(communities["diagnostics"]) 
                                    if tup[1] == max_node_degree_diagnostic]).replace("'","").replace("[","").replace("]","")
        min_node_degree_diagnostic = np.min(diag_degrees)
        min_node_name_diagnostic = str([tup[0] for tup in G.degree(communities["diagnostics"]) 
                                    if tup[1] == min_node_degree_diagnostic]).replace("'","").replace("[","").replace("]","")
    else:
        avg_node_degree_diagnostic = 0
        max_node_degree_diagnostic = 0
        max_node_name_diagnostic = "N/A"
        min_node_degree_diagnostic = 0
        min_node_name_diagnostic = "N/A"
    
    # Store graph statistics as a dictionary
    graph_stats = {
        "total_nodes": n_nodes,
        "total_edges": n_edges,
        "gene_count": len(communities["genes"]),
        "phenotype_count": len(communities["phenotypes"]),
        "diagnostic_count": len(communities["diagnostics"]),
        "gene_to_pheno_edges": edge_counts["gene_to_pheno_edges"],
        "pheno_to_diag_edges": edge_counts["pheno_to_diag_edges"],
        "avg_node_degree": avg_node_degree,
        "avg_gene_phenotypes": avg_node_degree_gene,
        "max_phenotype_gene": max_node_name_gene,
        "max_phenotype_count": max_node_degree_gene,
        "min_phenotype_gene": min_node_name_gene,
        "min_phenotype_count": min_node_degree_gene,
        "genes_no_phenotype": gene_nophenotype,
        "avg_diagnostic_coverage": avg_node_degree_diagnostic,
        "max_coverage_diagnostic": max_node_name_diagnostic,
        "max_coverage_count": max_node_degree_diagnostic,
        "min_coverage_diagnostic": min_node_name_diagnostic,
        "min_coverage_count": min_node_degree_diagnostic
    }
    
    return graph_stats