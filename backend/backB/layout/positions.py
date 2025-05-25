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

def clustered_shell_layout_3d(G: nx.Graph, communities: Dict[str, List[str]]) -> Dict[str, np.ndarray]:
    """
    Position nodes in concentric 3D shells with clustering based on connectivity.
    
    Optimization criteria:
    1. Minimize edge length to diagnostic nodes (primary)
    2. Minimize edge length to gene nodes (secondary)
    
    The algorithm positions nodes in computation order (diagnostics->phenotypes->genes)
    but returns them in visualization order (genes->phenotypes->diagnostics).
    
    Args:
        G: NetworkX graph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Returns:
        Dictionary of positions keyed by node in the order expected by prepare_coordinates:
        genes first, then phenotypes, then diagnostics
        
    Used in:
    - backend.backB.layout.positions.create_3d_layout
    """
    # Define radii for each shell
    shell_radii = {0: 0.5, 1: 1.0, 2: 1.5}  # genes, phenotypes, diagnostics
    temp_pos = {}  # Temporary storage for computing positions
    
    # Get node lists
    genes = communities["genes"]
    phenotypes = communities["phenotypes"]
    diagnostics = communities["diagnostics"]
    
    # Step 1: Position diagnostics evenly around outer sphere (computation step)
    n_diagnostics = len(diagnostics)
    
    for i, diagnostic in enumerate(diagnostics):
        # Use Fibonacci sphere for even distribution
        golden_ratio = (1 + 5**0.5) / 2
        phi = np.arccos(1 - 2 * (i + 0.5) / n_diagnostics)
        theta = 2 * np.pi * i / golden_ratio
        
        radius = shell_radii[2]  # Outer shell
        x = radius * np.sin(phi) * np.cos(theta)
        y = radius * np.sin(phi) * np.sin(theta)
        z = radius * np.cos(phi)
        
        temp_pos[diagnostic] = np.array([x, y, z])
    
    # Step 2: Position phenotypes based on connected diagnostics (computation step)
    for phenotype in phenotypes:
        # Find all diagnostics connected to this phenotype
        connected_diagnostics = []
        for diagnostic in diagnostics:
            if G.has_edge(phenotype, diagnostic):
                connected_diagnostics.append(diagnostic)
        
        if connected_diagnostics:
            # Calculate centroid of connected diagnostic positions
            centroid = np.mean([temp_pos[diag] for diag in connected_diagnostics], axis=0)
            
            # Normalize to project onto middle sphere
            centroid_norm = np.linalg.norm(centroid)
            if centroid_norm > 0:
                direction = centroid / centroid_norm
                temp_pos[phenotype] = direction * shell_radii[1]  # Middle shell
            else:
                # Fallback: random position if centroid is at origin
                phi = np.random.uniform(0, np.pi)
                theta = np.random.uniform(0, 2 * np.pi)
                radius = shell_radii[1]
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.sin(phi) * np.sin(theta)
                z = radius * np.cos(phi)
                temp_pos[phenotype] = np.array([x, y, z])
        else:
            # No connected diagnostics - use even distribution
            phen_index = phenotypes.index(phenotype)
            
            golden_ratio = (1 + 5**0.5) / 2
            phi = np.arccos(1 - 2 * (phen_index + 0.5) / len(phenotypes))
            theta = 2 * np.pi * phen_index / golden_ratio
            
            radius = shell_radii[1]
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            temp_pos[phenotype] = np.array([x, y, z])
    
    # Step 3: Position genes based on connected phenotypes (computation step)
    for gene in genes:
        # Find all phenotypes connected to this gene
        connected_phenotypes = []
        for phenotype in phenotypes:
            if G.has_edge(gene, phenotype):
                connected_phenotypes.append(phenotype)
        
        if connected_phenotypes:
            # Calculate centroid of connected phenotype positions
            centroid = np.mean([temp_pos[phen] for phen in connected_phenotypes], axis=0)
            
            # Normalize to project onto inner sphere
            centroid_norm = np.linalg.norm(centroid)
            if centroid_norm > 0:
                direction = centroid / centroid_norm
                temp_pos[gene] = direction * shell_radii[0]  # Inner shell
            else:
                # Fallback: random position if centroid is at origin
                phi = np.random.uniform(0, np.pi)
                theta = np.random.uniform(0, 2 * np.pi)
                radius = shell_radii[0]
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.sin(phi) * np.sin(theta)
                z = radius * np.cos(phi)
                temp_pos[gene] = np.array([x, y, z])
        else:
            # No connected phenotypes - use even distribution
            gene_index = genes.index(gene)
            
            golden_ratio = (1 + 5**0.5) / 2
            phi = np.arccos(1 - 2 * (gene_index + 0.5) / len(genes))
            theta = 2 * np.pi * gene_index / golden_ratio
            
            radius = shell_radii[0]
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            temp_pos[gene] = np.array([x, y, z])
    
    # Step 4: Create final position dictionary in the order expected by prepare_coordinates
    # Order must be: genes first, then phenotypes, then diagnostics
    pos = {}
    
    # Add genes first
    for gene in genes:
        pos[gene] = temp_pos[gene]
    
    # Add phenotypes second  
    for phenotype in phenotypes:
        pos[phenotype] = temp_pos[phenotype]
    
    # Add diagnostics last
    for diagnostic in diagnostics:
        pos[diagnostic] = temp_pos[diagnostic]
    
    return pos

def create_3d_layout(G: nx.Graph, communities: Dict[str, List[str]]) -> Dict[str, np.ndarray]:
    """
    Create a 3D layout for the knowledge graph nodes using clustered positioning.
    
    Args:
        G: NetworkX graph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Returns:
        Dictionary of 3D positions keyed by node
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Use the new clustered shell layout
    positions_3d = clustered_shell_layout_3d(G, communities)
    
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