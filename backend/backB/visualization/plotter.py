"""
Plotly visualization generation for the GenoPhenoPath knowledge graph.

This module handles the creation of the interactive 3D visualization using Plotly Graph Objects,
with customizable node and edge properties.

Functions in this module are used in:
- backend.controller: For preparing the visualization for the frontend
- frontend.frontB.display.chart: For displaying the visualization
"""

import plotly.graph_objects as go
from typing import Dict, List, Any, Tuple

from backend.backB.layout.edges import prepare_edge_coordinates
from backend.backC.statistics.metrics import calculate_graph_statistics

def create_node_traces(
    node_coords: Dict[str, List[float]], 
    communities: Dict[str, List[str]],
    default_sizes: Dict[str, float] = None
) -> List[go.Scatter3d]:
    """
    Create Plotly traces for nodes by type.
    
    Args:
        node_coords: Dictionary with node coordinates
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        default_sizes: Dictionary with default sizes for each node type
        
    Returns:
        List of Plotly Scatter3d traces for nodes
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    if default_sizes is None:
        default_sizes = {
            "gene": 6.37,  # 95% of 6.7
            "phenotype": 1.9,  # 95% of 2
            "diagnostic": 5.13  # 95% of 5.4
        }
    
    # Create gene nodes trace (blue color)
    trace_nodes_gene = go.Scatter3d(
        x=node_coords["x_nodes_gene"],
        y=node_coords["y_nodes_gene"],
        z=node_coords["z_nodes_gene"],
        mode='markers',
        marker=dict(
            symbol='circle',
            size=default_sizes["gene"],
            color="blue",
            line=dict(width=0)  # No border line
        ),
        hoverinfo='text', 
        hovertext=communities["genes"], 
        opacity=0.9,
        name='Genes'
    )

    # Create phenotype nodes trace (orange color)
    trace_nodes_phenotype = go.Scatter3d(
        x=node_coords["x_nodes_phenotype"],
        y=node_coords["y_nodes_phenotype"],
        z=node_coords["z_nodes_phenotype"],
        mode='markers',
        marker=dict(
            symbol='circle',
            size=default_sizes["phenotype"],
            color="orange",
            line=dict(width=0)  # No border line
        ),
        hoverinfo='text', 
        hovertext=communities["phenotypes"],
        opacity=0.2,  # Lower opacity for phenotypes
        name='Phenotypes'
    )

    # Create diagnostic nodes trace (magenta color)
    trace_nodes_diagnostic = go.Scatter3d(
        x=node_coords["x_nodes_diagnostic"],
        y=node_coords["y_nodes_diagnostic"],
        z=node_coords["z_nodes_diagnostic"],
        mode='markers',
        marker=dict(
            symbol='circle',
            size=default_sizes["diagnostic"],
            color="magenta",
            line=dict(width=0)  # No border line
        ),
        hoverinfo='text', 
        hovertext=communities["diagnostics"],
        opacity=0.7,
        name='Diagnostic Measures'
    )
    
    return [trace_nodes_gene, trace_nodes_phenotype, trace_nodes_diagnostic]

def create_edge_traces(edge_coords: Dict[str, List[float]]) -> List[go.Scatter3d]:
    """
    Create Plotly traces for edges by type.
    
    Args:
        edge_coords: Dictionary with edge coordinates
        
    Returns:
        List of Plotly Scatter3d traces for edges
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Create gene-to-phenotype edges trace (blue lines)
    trace_edges_gene_pheno = go.Scatter3d(
        x=edge_coords["gene_pheno_x"],
        y=edge_coords["gene_pheno_y"],
        z=edge_coords["gene_pheno_z"],
        mode='lines',
        line=dict(color='blue', width=0.26),  # 95% of 0.27
        opacity=0.4,
        hoverinfo='none',
        name='Gene-Phenotype Connections'
    )
    
    # Create phenotype-to-diagnostic edges trace (orange lines)
    trace_edges_pheno_diag = go.Scatter3d(
        x=edge_coords["pheno_diag_x"],
        y=edge_coords["pheno_diag_y"],
        z=edge_coords["pheno_diag_z"],
        mode='lines',
        line=dict(color='orange', width=0.19),  # 95% of 0.2
        opacity=0.3,
        hoverinfo='none',
        name='Phenotype-Diagnostic Connections'
    )
    
    return [trace_edges_gene_pheno, trace_edges_pheno_diag]

def configure_layout(width: int = 637, height: int = 509) -> go.Layout:
    """
    Configure Plotly layout for the 3D visualization.
    
    Args:
        width: Figure width
        height: Figure height
        
    Returns:
        Plotly Layout object
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Configure axis settings for the 3D plot (completely remove all axes elements)
    axis = dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                showaxeslabels=False,
                visible=False,
                title='')
    
    # Create a dark spacey layout for the 3D graph
    layout = go.Layout(
        # No title
        title_text = "",
        width=width,  # 95% of 670
        height=height,  # 95% of 536
        showlegend=False,  # Hide legend
        legend=dict(
            font=dict(color="#f8f8f2"),
            bgcolor="rgba(15, 22, 36, 0.5)"
        ),
        scene=dict(
            xaxis=dict(axis,
                      gridcolor="rgba(0,0,0,0)", 
                      zerolinecolor="rgba(0,0,0,0)"),
            yaxis=dict(axis,
                      gridcolor="rgba(0,0,0,0)", 
                      zerolinecolor="rgba(0,0,0,0)"),
            zaxis=dict(axis,
                      gridcolor="rgba(0,0,0,0)", 
                      zerolinecolor="rgba(0,0,0,0)"),
            bgcolor="#000000",  # Pure black to match website background
            # Add camera settings to increase zoom
            camera=dict(
                eye=dict(x=0.90, y=0.90, z=0.90)  # Reduced eye distance for more zoom
            ),
            aspectmode='cube'  # Enforce equal scaling on all axes
        ),
        paper_bgcolor="#000000",  # Pure black paper bg to match website background
        plot_bgcolor="#000000",   # Pure black plot bg
        margin=dict(t=32, l=0, r=0, b=0),  # 95% of 34
        hovermode='closest'
    )
    
    return layout

def create_visualization(
    G: Any, 
    communities: Dict[str, List[str]], 
    positions_3d: Dict[str, Any],
    edge_types: Dict[str, List[Tuple[str, str]]],
    node_coords: Dict[str, List[float]],
    width: int = 637, 
    height: int = 509
) -> Tuple[go.Figure, Dict[str, Any]]:
    """
    Create the complete 3D interactive visualization.
    
    Args:
        G: NetworkX graph
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        positions_3d: Dictionary of 3D positions keyed by node
        edge_types: Dictionary with edge lists by type
        node_coords: Dictionary with node coordinates
        width: Figure width
        height: Figure height
        
    Returns:
        Tuple containing:
        - Plotly Figure object
        - Dictionary with graph statistics
        
    Used in:
    - backend.controller.create_knowledge_graph
    """
    # Prepare edge coordinates
    edge_coords = prepare_edge_coordinates(edge_types, positions_3d)
    
    # Create node traces
    node_traces = create_node_traces(node_coords, communities)
    
    # Create edge traces
    edge_traces = create_edge_traces(edge_coords)
    
    # Configure layout
    layout = configure_layout(width, height)
    
    # Calculate graph statistics
    graph_stats = calculate_graph_statistics(
        G, 
        communities, 
        {
            "gene_to_pheno_edges": len(edge_types["gene_to_pheno_edges"]),
            "pheno_to_diag_edges": len(edge_types["pheno_to_diag_edges"])
        }
    )
    
    # Combine all traces (edges first, then nodes)
    # This order is important for proper rendering (edges behind nodes)
    data = edge_traces + node_traces
    
    # Create the figure
    fig = go.Figure(data=data, layout=layout)
    
    return fig, graph_stats