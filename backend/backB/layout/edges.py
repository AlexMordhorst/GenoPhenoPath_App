"""
Edge coordinates preparation for the GenoPhenoPath visualization.

This module handles the extraction and preparation of edge coordinates for visualization,
organizing them by edge type (gene-phenotype and phenotype-diagnostic).

Functions in this module are used in:
- backend.backB.visualization.plotter: For creating the plotly visualization
"""

import networkx as nx
import random
from typing import Dict, List, Any, Tuple

def identify_edge_types(
    G: nx.Graph, 
    communities: Dict[str, List[str]], 
    max_edges: int = 1000
) -> Dict[str, List[Tuple[str, str]]]:
    """
    Identify and categorize edges by type with optional limiting.
    
    Args:
        G: NetworkX graph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        max_edges: Maximum number of edges to include (for performance)
        
    Returns:
        Dictionary with edge lists by type:
        - edge_list: All edges (limited if necessary)
        - gene_to_pheno_edges: Gene-to-phenotype edges
        - pheno_to_diag_edges: Phenotype-to-diagnostic edges
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Get edge list
    edge_list = list(G.edges())
    
    # Apply limiting if necessary
    original_edge_count = len(edge_list)
    if original_edge_count > max_edges:
        random.seed(42)  # For consistent results
        edge_list = random.sample(edge_list, max_edges)
    
    # Split edges by type
    gene_to_pheno_edges = []
    pheno_to_diag_edges = []
    
    for edge in edge_list:
        source, target = edge
        if source in communities["genes"] and target in communities["phenotypes"]:
            # Gene to phenotype edge
            gene_to_pheno_edges.append(edge)
        elif source in communities["phenotypes"] and target in communities["diagnostics"]:
            # Phenotype to diagnostic edge
            pheno_to_diag_edges.append(edge)
    
    return {
        "edge_list": edge_list,
        "gene_to_pheno_edges": gene_to_pheno_edges,
        "pheno_to_diag_edges": pheno_to_diag_edges
    }

def prepare_edge_coordinates(
    edge_types: Dict[str, List[Tuple[str, str]]],
    positions_3d: Dict[str, Any]
) -> Dict[str, List[float]]:
    """
    Prepare edge coordinates for visualization by type.
    
    Args:
        edge_types: Dictionary with edge lists by type
        positions_3d: Dictionary of 3D positions keyed by node
        
    Returns:
        Dictionary with edge coordinates by type:
        - gene_pheno_x, gene_pheno_y, gene_pheno_z: Gene-phenotype edge coordinates
        - pheno_diag_x, pheno_diag_y, pheno_diag_z: Phenotype-diagnostic edge coordinates
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Create coordinates for gene-to-phenotype edges
    gene_pheno_x = []
    gene_pheno_y = []
    gene_pheno_z = []
    
    for edge in edge_types["gene_to_pheno_edges"]:
        x_coords = [positions_3d[edge[0]][0], positions_3d[edge[1]][0], None]
        gene_pheno_x.extend(x_coords)
        
        y_coords = [positions_3d[edge[0]][1], positions_3d[edge[1]][1], None]
        gene_pheno_y.extend(y_coords)
        
        z_coords = [positions_3d[edge[0]][2], positions_3d[edge[1]][2], None]
        gene_pheno_z.extend(z_coords)
    
    # Create coordinates for phenotype-to-diagnostic edges
    pheno_diag_x = []
    pheno_diag_y = []
    pheno_diag_z = []
    
    for edge in edge_types["pheno_to_diag_edges"]:
        x_coords = [positions_3d[edge[0]][0], positions_3d[edge[1]][0], None]
        pheno_diag_x.extend(x_coords)
        
        y_coords = [positions_3d[edge[0]][1], positions_3d[edge[1]][1], None]
        pheno_diag_y.extend(y_coords)
        
        z_coords = [positions_3d[edge[0]][2], positions_3d[edge[1]][2], None]
        pheno_diag_z.extend(z_coords)
    
    return {
        "gene_pheno_x": gene_pheno_x,
        "gene_pheno_y": gene_pheno_y,
        "gene_pheno_z": gene_pheno_z,
        "pheno_diag_x": pheno_diag_x,
        "pheno_diag_y": pheno_diag_y,
        "pheno_diag_z": pheno_diag_z
    }