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
    
    # Step 2: Position phenotypes using hybrid clustering + spherical distribution
    alpha = 0.7  # Blending parameter: 0.7 = 70% clustering, 30% spherical distribution
    
    for i, phenotype in enumerate(phenotypes):
        # Calculate spherical distribution position (Fibonacci sphere)
        golden_ratio = (1 + 5**0.5) / 2
        phi = np.arccos(1 - 2 * (i + 0.5) / len(phenotypes))
        theta = 2 * np.pi * i / golden_ratio
        
        spherical_x = np.sin(phi) * np.cos(theta)
        spherical_y = np.sin(phi) * np.sin(theta)
        spherical_z = np.cos(phi)
        spherical_direction = np.array([spherical_x, spherical_y, spherical_z])
        
        # Find all diagnostics connected to this phenotype
        connected_diagnostics = []
        for diagnostic in diagnostics:
            if G.has_edge(phenotype, diagnostic):
                connected_diagnostics.append(diagnostic)
        
        if connected_diagnostics:
            # Calculate clustering direction (centroid of connected diagnostics)
            centroid = np.mean([temp_pos[diag] for diag in connected_diagnostics], axis=0)
            centroid_norm = np.linalg.norm(centroid)
            
            if centroid_norm > 0:
                clustering_direction = centroid / centroid_norm
                
                # Blend clustering and spherical directions
                final_direction = alpha * clustering_direction + (1 - alpha) * spherical_direction
                final_direction_norm = np.linalg.norm(final_direction)
                
                if final_direction_norm > 0:
                    final_direction = final_direction / final_direction_norm
                    temp_pos[phenotype] = final_direction * shell_radii[1]  # Middle shell
                else:
                    # Fallback to spherical if blend results in zero vector
                    temp_pos[phenotype] = spherical_direction * shell_radii[1]
            else:
                # Fallback to spherical if centroid is at origin
                temp_pos[phenotype] = spherical_direction * shell_radii[1]
        else:
            # No connected diagnostics - use pure spherical distribution
            temp_pos[phenotype] = spherical_direction * shell_radii[1]
    
    # Step 3: Position genes using hybrid clustering + spherical distribution with repulsion
    beta = 0.5  # Blending parameter: 0.5 = 50% clustering, 50% spherical distribution
    repulsion_distance = 8.0  # Minimum distance between genes (in terms of node radii)
    
    for i, gene in enumerate(genes):
        # Calculate spherical distribution position (Fibonacci sphere)
        golden_ratio = (1 + 5**0.5) / 2
        phi = np.arccos(1 - 2 * (i + 0.5) / len(genes))
        theta = 2 * np.pi * i / golden_ratio
        
        spherical_x = np.sin(phi) * np.cos(theta)
        spherical_y = np.sin(phi) * np.sin(theta)
        spherical_z = np.cos(phi)
        spherical_direction = np.array([spherical_x, spherical_y, spherical_z])
        
        # Find all phenotypes connected to this gene
        connected_phenotypes = []
        for phenotype in phenotypes:
            if G.has_edge(gene, phenotype):
                connected_phenotypes.append(phenotype)
        
        # Calculate initial position (clustering + spherical blend)
        if connected_phenotypes:
            # Calculate clustering direction (centroid of connected phenotypes)
            centroid = np.mean([temp_pos[phen] for phen in connected_phenotypes], axis=0)
            centroid_norm = np.linalg.norm(centroid)
            
            if centroid_norm > 0:
                clustering_direction = centroid / centroid_norm
                
                # Blend clustering and spherical directions
                initial_direction = beta * clustering_direction + (1 - beta) * spherical_direction
                initial_direction_norm = np.linalg.norm(initial_direction)
                
                if initial_direction_norm > 0:
                    initial_direction = initial_direction / initial_direction_norm
                else:
                    # Fallback to spherical if blend results in zero vector
                    initial_direction = spherical_direction
            else:
                # Fallback to spherical if centroid is at origin
                initial_direction = spherical_direction
        else:
            # No connected phenotypes - use pure spherical distribution
            initial_direction = spherical_direction
        
        # Apply repulsion constraint
        final_position = initial_direction * shell_radii[0]
        
        # Check for repulsion with already positioned genes
        max_iterations = 50  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            too_close = False
            repulsion_force = np.array([0.0, 0.0, 0.0])
            
            # Check distance to all previously positioned genes
            for positioned_gene in genes[:i]:  # Only check genes positioned before this one
                if positioned_gene in temp_pos:
                    other_pos = temp_pos[positioned_gene]
                    distance = np.linalg.norm(final_position - other_pos)
                    
                    # Convert repulsion distance to actual 3D distance
                    # Assume node radius is roughly 0.02 units (adjust based on your visualization)
                    node_radius = 0.02
                    min_distance = repulsion_distance * node_radius
                    
                    if distance < min_distance and distance > 0:
                        too_close = True
                        # Calculate repulsion vector (away from the other gene)
                        repulsion_vector = (final_position - other_pos) / distance
                        # Scale repulsion force inversely with distance
                        force_magnitude = (min_distance - distance) / min_distance
                        repulsion_force += repulsion_vector * force_magnitude
            
            if not too_close:
                break
                
            # Apply repulsion force and renormalize to sphere
            adjusted_direction = final_position + repulsion_force * 0.1  # Scale factor for adjustment
            adjusted_norm = np.linalg.norm(adjusted_direction)
            
            if adjusted_norm > 0:
                final_position = (adjusted_direction / adjusted_norm) * shell_radii[0]
            else:
                # If repulsion pushes to origin, use a random position
                random_phi = np.random.uniform(0, np.pi)
                random_theta = np.random.uniform(0, 2 * np.pi)
                final_position = np.array([
                    shell_radii[0] * np.sin(random_phi) * np.cos(random_theta),
                    shell_radii[0] * np.sin(random_phi) * np.sin(random_theta),
                    shell_radii[0] * np.cos(random_phi)
                ])
            
            iteration += 1
        
        temp_pos[gene] = final_position
    
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