"""
Main controller for the GenoPhenoPath backend.

This module provides the main entry point for the frontend to access the backend
functionality, orchestrating the knowledge graph creation, layout generation, and
visualization preparation.

Functions in this module are used in:
- frontend.frontB.app.main: For loading the knowledge graph
- frontend.frontB.display.chart: For displaying the visualization
"""

from typing import Tuple, Dict, Any

import networkx as nx
import plotly.graph_objects as go

from backend.backA.knowledge_graph.builder import build_knowledge_graph
from backend.backA.network.generator import create_networkx_graph
from backend.backB.layout.positions import create_3d_layout, prepare_coordinates
from backend.backB.layout.edges import identify_edge_types
from backend.backB.visualization.plotter import create_visualization

def create_knowledge_graph(max_edges: int = 1000) -> Tuple[go.Figure, Dict[str, list], Dict[str, list], Dict[str, list], Dict[str, Any], nx.DiGraph, Dict[str, Any]]:
    """
    Create the complete knowledge graph and visualization.
    
    This function orchestrates the entire process:
    1. Build the ontology-based knowledge graph
    2. Convert to NetworkX for analysis
    3. Create 3D layout for visualization
    4. Generate the interactive Plotly visualization
    
    Args:
        max_edges: Maximum number of edges to include in visualization (for performance)
        
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
    # Build knowledge graph from ontology
    onto, communities = build_knowledge_graph()
    
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