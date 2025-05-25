"""
Main controller for the GenoPhenoPath backend.

This module provides the main entry point for the frontend to access the backend
functionality, orchestrating the knowledge graph creation, layout generation, and
visualization preparation.

Functions in this module are used in:
- frontend.frontB.app.main: For loading the knowledge graph
- frontend.frontB.display.chart: For displaying the visualization
"""

from typing import Tuple, Dict, Any, List, Optional

import networkx as nx
import plotly.graph_objects as go

from backend.backA.knowledge_graph.builder import build_knowledge_graph
from backend.backA.network.generator import create_networkx_graph
from backend.backB.layout.positions import create_3d_layout, prepare_coordinates
from backend.backB.layout.edges import identify_edge_types
from backend.backB.visualization.plotter import create_visualization

def create_subgraph_visualization(subgraph: nx.DiGraph, positions: Dict[str, Any], 
                            communities: Dict[str, list]) -> go.Figure:
    """
    Create a visualization for a specific diagnostic subgraph.
    
    Args:
        subgraph: NetworkX subgraph containing nodes and edges
        positions: Dictionary of 3D positions for nodes in the subgraph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Returns:
        Plotly Figure object with the subgraph visualization
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    # Extract node lists for the subgraph by community
    subgraph_communities = {
        "genes": [],
        "phenotypes": [],
        "diagnostics": []
    }
    
    # Categorize nodes in the subgraph
    for node in subgraph.nodes():
        if node in communities["genes"]:
            subgraph_communities["genes"].append(node)
        elif node in communities["phenotypes"]:
            subgraph_communities["phenotypes"].append(node)
        elif node in communities["diagnostics"]:
            subgraph_communities["diagnostics"].append(node)
    
    # Prepare coordinates for visualization
    # We need to create a structure that matches what the plotter expects
    x_nodes_gene = []
    y_nodes_gene = []
    z_nodes_gene = []
    
    x_nodes_phenotype = []
    y_nodes_phenotype = []
    z_nodes_phenotype = []
    
    x_nodes_diagnostic = []
    y_nodes_diagnostic = []
    z_nodes_diagnostic = []
    
    # Get coordinates for each node in the subgraph by node type
    for node in subgraph_communities["genes"]:
        if node in positions:
            x_nodes_gene.append(positions[node][0])
            y_nodes_gene.append(positions[node][1])
            z_nodes_gene.append(positions[node][2])
    
    for node in subgraph_communities["phenotypes"]:
        if node in positions:
            x_nodes_phenotype.append(positions[node][0])
            y_nodes_phenotype.append(positions[node][1])
            z_nodes_phenotype.append(positions[node][2])
    
    for node in subgraph_communities["diagnostics"]:
        if node in positions:
            x_nodes_diagnostic.append(positions[node][0])
            y_nodes_diagnostic.append(positions[node][1])
            z_nodes_diagnostic.append(positions[node][2])
    
    # Create the node_coords dictionary expected by the plotter
    node_coords = {
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
    
    # Identify edge types
    edge_types = {
        "gene_to_pheno_edges": [],
        "pheno_to_diag_edges": []
    }
    
    for u, v in subgraph.edges():
        if u in subgraph_communities["genes"] and v in subgraph_communities["phenotypes"]:
            edge_types["gene_to_pheno_edges"].append((u, v))
        elif u in subgraph_communities["phenotypes"] and v in subgraph_communities["diagnostics"]:
            edge_types["pheno_to_diag_edges"].append((u, v))
    
    # Create graph stats for the subgraph
    graph_stats = {
        "gene_to_pheno_edges": len(edge_types["gene_to_pheno_edges"]),
        "pheno_to_diag_edges": len(edge_types["pheno_to_diag_edges"]),
        "total_edges": len(edge_types["gene_to_pheno_edges"]) + len(edge_types["pheno_to_diag_edges"])
    }
    
    # Create visualization
    fig, _ = create_visualization(subgraph, subgraph_communities, positions, edge_types, node_coords)
    
    return fig

def generate_diagnostic_subgraphs(G: nx.DiGraph, communities: Dict[str, list], positions_3d: Dict[str, Any]) -> List[Tuple[nx.DiGraph, Dict[str, Any], str]]:
    """
    Generate a subgraph for each diagnostic node in the knowledge graph.
    
    Each subgraph includes:
    1. A diagnostic node
    2. All phenotype nodes connected to the diagnostic node
    3. All gene nodes connected to those phenotype nodes
    4. All edges connecting these nodes
    
    Args:
        G: The complete NetworkX graph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        positions_3d: Dictionary of 3D positions for all nodes
        
    Returns:
        List of tuples, each containing:
        - A NetworkX subgraph
        - Dictionary of 3D positions for nodes in the subgraph
        - The diagnostic node name (for labeling)
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    subgraphs = []
    
    # For each diagnostic node, create a subgraph
    for diag_node in communities["diagnostics"]:
        # Create a new subgraph
        subgraph = nx.DiGraph()
        
        # Add the diagnostic node to the subgraph
        subgraph.add_node(diag_node, **G.nodes[diag_node])
        
        # Find all phenotype nodes connected to this diagnostic node
        phenotype_nodes = []
        for phen_node in communities["phenotypes"]:
            if G.has_edge(phen_node, diag_node):
                phenotype_nodes.append(phen_node)
                # Add the phenotype node to the subgraph
                subgraph.add_node(phen_node, **G.nodes[phen_node])
                # Add the edge connecting phenotype to diagnostic
                subgraph.add_edge(phen_node, diag_node, **G.edges[(phen_node, diag_node)])
        
        # Find all gene nodes connected to these phenotype nodes
        gene_nodes = []
        for gene_node in communities["genes"]:
            for phen_node in phenotype_nodes:
                if G.has_edge(gene_node, phen_node):
                    if gene_node not in gene_nodes:
                        gene_nodes.append(gene_node)
                        # Add the gene node to the subgraph
                        subgraph.add_node(gene_node, **G.nodes[gene_node])
                    # Add the edge connecting gene to phenotype
                    subgraph.add_edge(gene_node, phen_node, **G.edges[(gene_node, phen_node)])
        
        # Create a dictionary of positions for this subgraph
        subgraph_positions = {node: positions_3d[node] for node in subgraph.nodes()}
        
        # Only add subgraphs that have at least one phenotype and one gene node
        if len(phenotype_nodes) > 0 and len(gene_nodes) > 0:
            subgraphs.append((subgraph, subgraph_positions, diag_node))
    
    return subgraphs

def create_knowledge_graph(selected_genes: Optional[List[str]] = None, max_edges: int = 1000, force_refresh: bool = False) -> Tuple[go.Figure, Dict[str, list], Dict[str, list], Dict[str, list], Dict[str, Any], nx.DiGraph, Dict[str, Any], List[Tuple[nx.DiGraph, Dict[str, Any], str]]]:
    """
    Create the complete knowledge graph and visualization.

    This function orchestrates the entire process:
    1. Build the ontology-based knowledge graph
    2. Convert to NetworkX for analysis
    3. Create 3D layout for visualization
    4. Generate the interactive Plotly visualization

    Args:
        selected_genes: Optional list of gene symbols to filter the graph
        max_edges: Maximum number of edges to include in visualization (for performance)
        force_refresh: If True, forces a complete rebuild of the graph and visualization

    Returns:
        Tuple containing:
        - Plotly Figure
        - List of gene names
        - List of phenotype names
        - List of diagnostic names
        - Dictionary of 3D positions
        - NetworkX graph
        - Dictionary of graph statistics
        - List of diagnostic subgraphs (each containing a NetworkX graph, positions, and diagnostic name)

    Used in:
    - frontend.frontB.app.main.load_knowledge_graph
    """
    # If force_refresh is True, clear the ontology first to ensure everything is rebuilt
    if force_refresh:
        from backend.backA.ontology.schema import clear_ontology
        print("DEBUG - Forcing complete graph rebuild")
        clear_ontology()

    # Build knowledge graph from ontology with optional gene filtering
    print(f"DEBUG - Selected genes in create_knowledge_graph: {selected_genes if selected_genes else 'None'}")
    print(f"DEBUG - Force refresh: {force_refresh}")

    # Hack to access backA directly to modify behavior based on force_refresh
    from backend.backA.knowledge_graph.builder import build_knowledge_graph as raw_build_knowledge_graph
    from backend.backA.ontology.schema import create_ontology_schema
    from backend.backA.knowledge_graph.nodes import extract_node_communities
    from backend.backA.data_storage.value_manager import initialize_node_values

    # Get existing values for phenotypes before building the graph
    # This allows us to restore them after the graph is built
    from backend.backA.data_storage.database import get_node_value, set_node_value

    # Store any custom phenotype values
    custom_phenotype_values = {}
    if force_refresh:
        print("DEBUG - Force refresh is true, capturing custom phenotype values")
        try:
            # We need to find all phenotype nodes that might be in the database
            # For this, we can use the phenotype loader
            from backend.backA.data_processing.loader import load_unique_phenotypes
            all_phenotypes = load_unique_phenotypes()

            for _, row in all_phenotypes.iterrows():
                phenotype_id = row['hpo_id']
                try:
                    # Get the current value
                    current_value = get_node_value(phenotype_id, 'phenotype')

                    # If value is significantly different from 0.5, it's a custom value
                    if abs(current_value - 0.5) > 0.1:  # Values different from default
                        print(f"DEBUG - Captured phenotype {phenotype_id} with custom value = {current_value}")
                        custom_phenotype_values[phenotype_id] = current_value
                except Exception as e:
                    # This is expected for phenotypes not in the database yet
                    pass
        except Exception as e:
            print(f"DEBUG - Error capturing phenotype values: {e}")

    # Build the graph using the normal flow
    onto, communities = raw_build_knowledge_graph(selected_genes)

    # If we captured any custom values, restore them
    if force_refresh and custom_phenotype_values:
        print(f"DEBUG - Restoring {len(custom_phenotype_values)} custom phenotype values")

        # Only restore values for phenotypes that are in the current graph
        phenotype_ids = communities.get('phenotypes', [])
        for phenotype_id in phenotype_ids:
            if phenotype_id in custom_phenotype_values:
                value = custom_phenotype_values[phenotype_id]
                print(f"DEBUG - Restoring phenotype {phenotype_id} value = {value}")
                set_node_value(phenotype_id, 'phenotype', value)
    else:
        # New session, debug what values are set
        print("DEBUG - Using default node values")

    # Convert to NetworkX
    G, edge_counts = create_networkx_graph(onto, communities)

    # Create 3D layout
    positions_3d = create_3d_layout(G, communities)

    # Prepare node coordinates
    node_coords = prepare_coordinates(positions_3d, communities)

    # Identify edge types (with optional limiting)
    edge_types = identify_edge_types(G, communities, max_edges)

    # Create visualization
    fig, graph_stats = create_visualization(G, communities, positions_3d, edge_types, node_coords)

    # Generate diagnostic subgraphs
    diagnostic_subgraphs = generate_diagnostic_subgraphs(G, communities, positions_3d)
    
    # Return all necessary objects for the frontend
    return (
        fig,
        communities["genes"],
        communities["phenotypes"],
        communities["diagnostics"],
        positions_3d,
        G,
        graph_stats,
        diagnostic_subgraphs
    )