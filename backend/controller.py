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

def create_knowledge_graph(selected_genes: Optional[List[str]] = None, max_edges: int = 1000, force_refresh: bool = False) -> Tuple[go.Figure, Dict[str, list], Dict[str, list], Dict[str, list], Dict[str, Any], nx.DiGraph, Dict[str, Any]]:
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

    # Return all necessary objects for the frontend
    return (
        fig,
        communities["genes"],
        communities["phenotypes"],
        communities["diagnostics"],
        positions_3d,
        G,
        graph_stats
    )