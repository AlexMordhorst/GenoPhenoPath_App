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
from backend.backA.data_storage.value_manager import (
    get_node_opacity,
    get_edge_opacity,
    get_node_type,
    group_nodes_by_opacity,
    create_opacity_buckets,
    get_bucket_opacity
)

def create_node_traces(
    node_coords: Dict[str, List[float]], 
    communities: Dict[str, List[str]],
    default_sizes: Dict[str, float] = None,
    num_buckets: int = 5
) -> List[go.Scatter3d]:
    """
    Create Plotly traces for nodes by type and opacity bucket.
    
    Args:
        node_coords: Dictionary with node coordinates
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        default_sizes: Dictionary with default sizes for each node type
        num_buckets: Number of opacity buckets to use
        
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
    
    # Create the opacity buckets
    buckets = create_opacity_buckets(num_buckets)
    
    # Initialize list to hold all node traces
    all_traces = []
    
    # Create multiple traces for gene nodes based on opacity buckets
    gene_nodes_by_bucket = group_nodes_by_opacity(communities["genes"], "gene", num_buckets)
    
    for bucket_idx, node_ids in gene_nodes_by_bucket.items():
        # Get indices of these nodes in the coordinate arrays
        indices = [communities["genes"].index(node_id) for node_id in node_ids]
        
        # Extract coordinates for these nodes
        x_vals = [node_coords["x_nodes_gene"][i] for i in indices]
        y_vals = [node_coords["y_nodes_gene"][i] for i in indices]
        z_vals = [node_coords["z_nodes_gene"][i] for i in indices]
        
        # Get opacity for this bucket
        opacity = get_bucket_opacity(bucket_idx, buckets)
        
        # Create trace for this bucket of gene nodes
        trace = go.Scatter3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            mode='markers',
            marker=dict(
                symbol='circle',
                size=default_sizes["gene"],
                color="blue",
                line=dict(width=0)  # No border line
            ),
            hoverinfo='text',
            hovertext=node_ids,
            opacity=opacity,
            name=f'Genes (opacity {opacity:.2f})',
            showlegend=False  # Hide from legend to avoid clutter
        )
        
        all_traces.append(trace)
    
    # Create multiple traces for phenotype nodes based on opacity buckets
    phenotype_nodes_by_bucket = group_nodes_by_opacity(communities["phenotypes"], "phenotype", num_buckets)
    
    for bucket_idx, node_ids in phenotype_nodes_by_bucket.items():
        # Get indices of these nodes in the coordinate arrays
        indices = [communities["phenotypes"].index(node_id) for node_id in node_ids]
        
        # Extract coordinates for these nodes
        x_vals = [node_coords["x_nodes_phenotype"][i] for i in indices]
        y_vals = [node_coords["y_nodes_phenotype"][i] for i in indices]
        z_vals = [node_coords["z_nodes_phenotype"][i] for i in indices]
        
        # Get opacity for this bucket
        opacity = get_bucket_opacity(bucket_idx, buckets)
        
        # Create trace for this bucket of phenotype nodes
        trace = go.Scatter3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            mode='markers',
            marker=dict(
                symbol='circle',
                size=default_sizes["phenotype"],
                color="orange",
                line=dict(width=0)  # No border line
            ),
            hoverinfo='text',
            hovertext=node_ids,
            opacity=opacity,
            name=f'Phenotypes (opacity {opacity:.2f})',
            showlegend=False  # Hide from legend to avoid clutter
        )
        
        all_traces.append(trace)
    
    # Create multiple traces for diagnostic nodes based on opacity buckets
    diagnostic_nodes_by_bucket = group_nodes_by_opacity(communities["diagnostics"], "diagnostic", num_buckets)
    
    for bucket_idx, node_ids in diagnostic_nodes_by_bucket.items():
        # Get indices of these nodes in the coordinate arrays
        indices = [communities["diagnostics"].index(node_id) for node_id in node_ids]
        
        # Extract coordinates for these nodes
        x_vals = [node_coords["x_nodes_diagnostic"][i] for i in indices]
        y_vals = [node_coords["y_nodes_diagnostic"][i] for i in indices]
        z_vals = [node_coords["z_nodes_diagnostic"][i] for i in indices]
        
        # Get opacity for this bucket
        opacity = get_bucket_opacity(bucket_idx, buckets)
        
        # Create trace for this bucket of diagnostic nodes
        trace = go.Scatter3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            mode='markers',
            marker=dict(
                symbol='circle',
                size=default_sizes["diagnostic"],
                color="magenta",
                line=dict(width=0)  # No border line
            ),
            hoverinfo='text',
            hovertext=node_ids,
            opacity=opacity,
            name=f'Diagnostics (opacity {opacity:.2f})',
            showlegend=False  # Hide from legend to avoid clutter
        )
        
        all_traces.append(trace)
    
    # Add three main legend traces with opacity=0 (invisible but show in legend)
    # These are just for the legend - not for actual visualization
    
    # Gene legend trace
    legend_gene = go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(
            symbol='circle',
            size=default_sizes["gene"],
            color="blue",
            line=dict(width=0)
        ),
        opacity=0,  # Invisible
        name='Genes',
        showlegend=True
    )
    
    # Phenotype legend trace
    legend_phenotype = go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(
            symbol='circle',
            size=default_sizes["phenotype"],
            color="orange",
            line=dict(width=0)
        ),
        opacity=0,  # Invisible
        name='Phenotypes',
        showlegend=True
    )
    
    # Diagnostic legend trace
    legend_diagnostic = go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(
            symbol='circle',
            size=default_sizes["diagnostic"],
            color="magenta",
            line=dict(width=0)
        ),
        opacity=0,  # Invisible
        name='Diagnostic Measures',
        showlegend=True
    )
    
    # Add the legend traces to the beginning so they appear at the top of the legend
    all_traces = [legend_gene, legend_phenotype, legend_diagnostic] + all_traces
    
    return all_traces

def create_edge_traces(
    edge_coords: Dict[str, List[float]], 
    edge_types: Dict[str, List[Tuple[str, str]]],
    communities: Dict[str, List[str]]
) -> Tuple[List[go.Scatter3d], Dict[str, Any]]:
    """
    Create Plotly traces for edges by type, with opacity based on node values.
    
    Args:
        edge_coords: Dictionary with edge coordinates
        edge_types: Dictionary with edge lists by type
        communities: Dictionary with node communities (genes, phenotypes, diagnostics)
        
    Returns:
        Tuple containing:
        - List of Plotly Scatter3d traces for edges
        - Dictionary with edge statistics
        
    Used in:
    - backend.backB.visualization.plotter.create_visualization
    """
    # Calculate opacities for gene-phenotype edges
    gene_pheno_opacities = []
    for source, target in edge_types["gene_to_pheno_edges"]:
        source_type = get_node_type(source, communities)
        target_type = get_node_type(target, communities)
        opacity = get_edge_opacity(source, source_type, target, target_type)
        gene_pheno_opacities.append(opacity)
    
    # Calculate opacities for phenotype-diagnostic edges
    pheno_diag_opacities = []
    for source, target in edge_types["pheno_to_diag_edges"]:
        source_type = get_node_type(source, communities)
        target_type = get_node_type(target, communities)
        opacity = get_edge_opacity(source, source_type, target, target_type)
        pheno_diag_opacities.append(opacity)
    
    # Create gene-to-phenotype edges trace (blue lines)
    trace_edges_gene_pheno = go.Scatter3d(
        x=edge_coords["gene_pheno_x"],
        y=edge_coords["gene_pheno_y"],
        z=edge_coords["gene_pheno_z"],
        mode='lines',
        line=dict(
            color='blue', 
            width=0.26,  # 95% of 0.27
            # We can't set individual line opacities, so we use the trace opacity
        ),
        opacity=0.6,  # Base opacity which will be adjusted by UI controls
        hoverinfo='none',
        name='Gene-Phenotype Connections'
    )
    
    # Create phenotype-to-diagnostic edges trace (orange lines)
    trace_edges_pheno_diag = go.Scatter3d(
        x=edge_coords["pheno_diag_x"],
        y=edge_coords["pheno_diag_y"],
        z=edge_coords["pheno_diag_z"],
        mode='lines',
        line=dict(
            color='orange', 
            width=0.19,  # 95% of 0.2
            # We can't set individual line opacities, so we use the trace opacity
        ),
        opacity=0.5,  # Base opacity which will be adjusted by UI controls
        hoverinfo='none',
        name='Phenotype-Diagnostic Connections'
    )
    
    # Store opacities in the graph statistics for potential future use
    edge_stats = {
        "gene_pheno_opacities": gene_pheno_opacities,
        "pheno_diag_opacities": pheno_diag_opacities
    }
    
    return [trace_edges_gene_pheno, trace_edges_pheno_diag], edge_stats

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
    edge_traces, edge_opacity_stats = create_edge_traces(edge_coords, edge_types, communities)
    
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
    
    # Add edge opacity statistics
    graph_stats.update(edge_opacity_stats)
    
    # Combine all traces (edges first, then nodes)
    # This order is important for proper rendering (edges behind nodes)
    data = edge_traces + node_traces
    
    # Create the figure
    fig = go.Figure(data=data, layout=layout)
    
    return fig, graph_stats