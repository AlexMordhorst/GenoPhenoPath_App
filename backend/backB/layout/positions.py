"""
3D layout generation for the GenoPhenoPath knowledge graph.

This module handles the creation of 3D positions for nodes in the knowledge graph,
organizing them in concentric spheres based on node types.

Functions in this module are used in:
- backend.backB.visualization.plotter: For creating the plotly visualization
"""

import numpy as np
import random
import networkx as nx
from typing import Dict, List, Tuple, Any

def shell_layout_3d(G: nx.Graph, node_types: Dict[str, int]) -> Dict[str, np.ndarray]:
    """
    Position nodes in concentric 3D shells (spheres).
    
    Args:
        G: NetworkX graph
        node_types: Dictionary with node names as keys and node types as values.
            Node types should be integers representing the shell (0=innermost, 1=middle, 2=outermost)
    
    Returns:
        Dictionary of positions keyed by node
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Define radii for each shell - innermost has smallest radius
    shell_radii = {0: 0.5, 1: 1.0, 2: 1.5}  # These values can be adjusted
    
    # Initialize the position dictionary
    pos = {}
    
    # Group nodes by shell
    shells = {}
    for node, shell in node_types.items():
        if shell not in shells:
            shells[shell] = []
        shells[shell].append(node)
    
    # Distribute nodes in each shell
    for shell_number, nodes in shells.items():
        # Get radius for this shell
        radius = shell_radii[shell_number]
        
        # Number of nodes in this shell
        n_nodes = len(nodes)
        
        # Calculate positions for each node in this shell
        for i, node in enumerate(nodes):
            # For evenly spaced distribution on a sphere, we use the Fibonacci sphere algorithm
            golden_ratio = (1 + 5**0.5) / 2
            
            # Create a randomization offset for each node
            random_offset = random.uniform(-0.05, 0.05)
            
            # Calculate angles
            i_offset = i + random_offset  # Add a small random offset for variation
            phi = np.arccos(1 - 2 * (i_offset + 0.5) / n_nodes)
            theta = 2 * np.pi * i_offset / golden_ratio
            
            # Convert spherical to Cartesian coordinates
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            
            # Set position
            pos[node] = np.array([x, y, z])
    
    return pos

def create_3d_layout(G: nx.Graph, communities: Dict[str, List[str]]) -> Dict[str, np.ndarray]:
    """
    Create a 3D layout for the knowledge graph nodes.
    
    Args:
        G: NetworkX graph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Returns:
        Dictionary of 3D positions keyed by node
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Create a node type dictionary for the 3D shell layout
    node_types = {}
    
    # Genes in the innermost shell (0)
    for gene in communities["genes"]:
        node_types[gene] = 0
        
    # Phenotypes in the middle shell (1)
    for phenotype in communities["phenotypes"]:
        node_types[phenotype] = 1
        
    # Diagnostics in the outermost shell (2)
    for diagnostic in communities["diagnostics"]:
        node_types[diagnostic] = 2
    
    # Use our custom shell layout
    positions_3d = shell_layout_3d(G, node_types)
    
    return positions_3d

def prepare_coordinates(
    positions_3d: Dict[str, np.ndarray], 
    communities: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Prepare node and edge coordinates for visualization.
    
    Args:
        positions_3d: Dictionary of 3D positions keyed by node
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Returns:
        Dictionary containing separated coordinate lists for visualization:
        - x_nodes_gene, y_nodes_gene, z_nodes_gene: Gene node coordinates
        - x_nodes_phenotype, y_nodes_phenotype, z_nodes_phenotype: Phenotype node coordinates
        - x_nodes_diagnostic, y_nodes_diagnostic, z_nodes_diagnostic: Diagnostic node coordinates
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Get node counts
    n_genes = len(communities["genes"])
    n_pheno = len(communities["phenotypes"])
    n_diag = len(communities["diagnostics"])
    Num_nodes = n_genes + n_pheno + n_diag

    # Extract node coordinates from the 3D layout
    nodes_list = list(positions_3d.values())
    x_nodes = [nodes_list[i][0] for i in range(Num_nodes)]
    y_nodes = [nodes_list[i][1] for i in range(Num_nodes)]
    z_nodes = [nodes_list[i][2] for i in range(Num_nodes)]

    # Split node coordinates by entity type (gene, phenotype, diagnostic)
    # Fix the slicing to include all nodes
    x_nodes_gene = x_nodes[0:n_genes]
    x_nodes_phenotype = x_nodes[n_genes:(n_genes+n_pheno)]
    x_nodes_diagnostic = x_nodes[(n_genes+n_pheno):]

    y_nodes_gene = y_nodes[0:n_genes]
    y_nodes_phenotype = y_nodes[n_genes:(n_genes+n_pheno)]
    y_nodes_diagnostic = y_nodes[(n_genes+n_pheno):]

    z_nodes_gene = z_nodes[0:n_genes]
    z_nodes_phenotype = z_nodes[n_genes:(n_genes+n_pheno)]
    z_nodes_diagnostic = z_nodes[(n_genes+n_pheno):]
    
    return {
        "x_nodes_gene": x_nodes_gene,
        "y_nodes_gene": y_nodes_gene,
        "z_nodes_gene": z_nodes_gene,
        "x_nodes_phenotype": x_nodes_phenotype,
        "y_nodes_phenotype": y_nodes_phenotype,
        "z_nodes_phenotype": z_nodes_phenotype,
        "x_nodes_diagnostic": x_nodes_diagnostic,
        "y_nodes_diagnostic": y_nodes_diagnostic,
        "z_nodes_diagnostic": z_nodes_diagnostic
    }