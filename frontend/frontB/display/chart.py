"""
Graph visualization display for the GenoPhenoPath application.

This module handles the display and updating of the 3D graph visualization based on
user controls and application state.

Functions in this module are used in:
- frontend.frontB.app.main: For displaying the knowledge graph
"""

import streamlit as st
import plotly.graph_objects as go
import time
from typing import Dict, List, Any, Tuple

from frontend.frontA.animations.dna_helix import display_dna_animation
from frontend.frontA.session.state import update_graph_statistics
from frontend.frontB.interactions.controls import check_controls_changed, update_control_state
from frontend.frontB.interactions.search import handle_search

def update_figure_data(
    fig_data: List[go.Scatter3d], 
    controls: Dict[str, Any]
) -> List[go.Scatter3d]:
    """
    Update Plotly figure data based on control settings.
    
    Args:
        fig_data: List of Plotly trace objects
        controls: Dictionary with control values
        
    Returns:
        Updated list of Plotly trace objects
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    # Trace order:
    # 0: Gene-phenotype edges (trace_edges_gene_pheno)
    # 1: Phenotype-diagnostic edges (trace_edges_pheno_diag)
    # 2: Gene nodes (trace_nodes_gene)
    # 3: Phenotype nodes (trace_nodes_phenotype)
    # 4: Diagnostic nodes (trace_nodes_diagnostic)
    
    # Update gene-phenotype edge visibility and opacity (index 0)
    if not controls["show_gene_pheno_edges"] or not (controls["show_genes"] and controls["show_phenotypes"]):
        # Hide edges completely
        fig_data[0].opacity = 0
        fig_data[0].visible = "legendonly"
    else:
        fig_data[0].opacity = controls["gene_pheno_opacity"]
        fig_data[0].visible = True
    
    # Update phenotype-diagnostic edge visibility and opacity (index 1)
    if not controls["show_pheno_diag_edges"] or not (controls["show_phenotypes"] and controls["show_diagnostics"]):
        # Hide edges completely
        fig_data[1].opacity = 0
        fig_data[1].visible = "legendonly"
    else:
        fig_data[1].opacity = controls["pheno_diag_opacity"]
        fig_data[1].visible = True
        
    # Update gene nodes (index 2)
    if not controls["show_genes"]:
        # Hide gene nodes completely including hover text
        fig_data[2].opacity = 0
        fig_data[2].hoverinfo = "skip"
        fig_data[2].showlegend = False
        fig_data[2].visible = "legendonly"
    else:
        fig_data[2].marker.size = controls["gene_size"]
        fig_data[2].opacity = controls["gene_opacity"]
        fig_data[2].hoverinfo = "text"
        fig_data[2].visible = True
    
    # Update phenotype nodes (index 3)
    if not controls["show_phenotypes"]:
        # Hide phenotype nodes completely including hover text
        fig_data[3].opacity = 0
        fig_data[3].hoverinfo = "skip"
        fig_data[3].showlegend = False
        fig_data[3].visible = "legendonly"
    else:
        fig_data[3].marker.size = controls["phenotype_size"]
        fig_data[3].opacity = controls["phenotype_opacity"]
        fig_data[3].hoverinfo = "text"
        fig_data[3].visible = True
        
    # Update diagnostic nodes (index 4)
    if not controls["show_diagnostics"]:
        # Hide diagnostic nodes completely including hover text
        fig_data[4].opacity = 0
        fig_data[4].hoverinfo = "skip"
        fig_data[4].showlegend = False
        fig_data[4].visible = "legendonly"
    else:
        fig_data[4].marker.size = controls["diagnostic_size"]
        fig_data[4].opacity = controls["diagnostic_opacity"]
        fig_data[4].hoverinfo = "text"
        fig_data[4].visible = True
    
    return fig_data

def show_transition_animation(
    animation_placeholder: Any, 
    animation_frames: List[str], 
    frame_count: int = 5
):
    """
    Animation removed - this function now does nothing.
    Keeping the signature for backwards compatibility.
    
    Args:
        animation_placeholder: Streamlit container (not used)
        animation_frames: List of animation frame strings (not used)
        frame_count: Number of frames to display (not used)
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    # Animation has been removed
    pass

def calculate_visibility_stats(
    controls: Dict[str, Any],
    genes: List[str],
    phenotypes: List[str],
    diagnostics: List[str],
    graph_stats: Dict[str, Any]
) -> Dict[str, int]:
    """
    Calculate statistics about visible nodes and edges.
    
    Args:
        controls: Dictionary with control values
        genes: List of gene names
        phenotypes: List of phenotype IDs
        diagnostics: List of diagnostic labels
        graph_stats: Dictionary with graph statistics
        
    Returns:
        Dictionary with visibility statistics:
        - visible_genes: Number of visible gene nodes
        - visible_phenotypes: Number of visible phenotype nodes
        - visible_diagnostics: Number of visible diagnostic nodes
        - visible_gene_pheno_edges: Number of visible gene-phenotype edges
        - visible_pheno_diag_edges: Number of visible phenotype-diagnostic edges
        - displayed_nodes: Total number of displayed nodes
        - displayed_edges: Total number of displayed edges
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    stats = {}
    
    # Calculate visible nodes
    stats["visible_genes"] = len(genes) if controls["show_genes"] else 0
    stats["visible_phenotypes"] = len(phenotypes) if controls["show_phenotypes"] else 0
    stats["visible_diagnostics"] = len(diagnostics) if controls["show_diagnostics"] else 0
    
    # Calculate total displayed nodes
    stats["displayed_nodes"] = stats["visible_genes"] + stats["visible_phenotypes"] + stats["visible_diagnostics"]
    
    # Calculate visible edges
    stats["visible_gene_pheno_edges"] = graph_stats["gene_to_pheno_edges"] if controls["show_gene_pheno_edges"] and controls["show_genes"] and controls["show_phenotypes"] else 0
    stats["visible_pheno_diag_edges"] = graph_stats["pheno_to_diag_edges"] if controls["show_pheno_diag_edges"] and controls["show_phenotypes"] and controls["show_diagnostics"] else 0
    
    # Calculate total displayed edges
    stats["displayed_edges"] = stats["visible_gene_pheno_edges"] + stats["visible_pheno_diag_edges"]
    
    return stats

def display_statistics_dropdown(
    dropdown_container: Any,
    visibility_stats: Dict[str, int],
    genes: List[str],
    phenotypes: List[str],
    diagnostics: List[str]
):
    """
    Display graph statistics in an expandable dropdown.
    
    Args:
        dropdown_container: Streamlit container for the dropdown
        visibility_stats: Dictionary with visibility statistics
        genes: List of all gene names
        phenotypes: List of all phenotype IDs
        diagnostics: List of all diagnostic labels
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    with dropdown_container:
        with st.expander("🧬 DNA Genopath - Statistics 🧬", expanded=False):
            # Create columns for a nice layout of statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Genes", visibility_stats["visible_genes"], 
                         delta=f"{visibility_stats['visible_genes']}/{len(genes)}" 
                         if visibility_stats["visible_genes"] < len(genes) else None)
            with col2:
                st.metric("Phenotypes", visibility_stats["visible_phenotypes"],
                         delta=f"{visibility_stats['visible_phenotypes']}/{len(phenotypes)}" 
                         if visibility_stats["visible_phenotypes"] < len(phenotypes) else None)
            with col3:
                st.metric("Diagnostic Measures", visibility_stats["visible_diagnostics"],
                         delta=f"{visibility_stats['visible_diagnostics']}/{len(diagnostics)}" 
                         if visibility_stats["visible_diagnostics"] < len(diagnostics) else None)
                
            # Add a small vertical space
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Second row for edges
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gene-Phenotype Edges", visibility_stats["visible_gene_pheno_edges"])
            with col2:
                st.metric("Phenotype-Diagnostic Edges", visibility_stats["visible_pheno_diag_edges"])
            with col3:
                st.metric("Total Edges", visibility_stats["displayed_edges"])

def display_graph_description():
    """
    Display a description of the graph visualization below the chart.
    This function is kept for backward compatibility but is no longer used directly.
    The info box is now placed using a placeholder for better positioning.
    
    Used in:
    - frontend.frontB.display.chart.update_visualization (legacy)
    """
    # Note: This function is kept for backwards compatibility but is no longer used directly
    st.markdown("""
    <div style='background-color: #000000; padding: 15px; border-radius: 5px; border: 1px solid rgba(139, 233, 253, 0.2);'>
        This visualization maps the relationships between:
        <ul>
            <li><span style='color: #8be9fd; font-weight: bold;'>Genes</span> (blue nodes in the inner sphere)</li>
            <li><span style='color: #ffb86c; font-weight: bold;'>Phenotypes</span> (orange nodes in the middle sphere)</li>
            <li><span style='color: #ff79c6; font-weight: bold;'>Diagnostic measures</span> (magenta nodes in the outer sphere)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def update_visualization(
    fig: go.Figure,
    controls: Dict[str, Any],
    animation_placeholder: Any,
    animation_frames: List[str],
    genes: List[str],
    phenotypes: List[str],
    diagnostics: List[str],
    graph_stats: Dict[str, Any]
) -> go.Figure:
    """
    Update the graph visualization based on control settings.
    
    Args:
        fig: Plotly Figure object
        controls: Dictionary with control values
        animation_placeholder: Streamlit container for the animation
        animation_frames: List of animation frame strings
        genes: List of gene names
        phenotypes: List of phenotype IDs
        diagnostics: List of diagnostic labels
        graph_stats: Dictionary with graph statistics
        
    Returns:
        Updated Plotly Figure object
        
    Used in:
    - frontend.frontB.app.main.run_app
    """
    try:
        # Handle search
        matching_nodes = handle_search(
            controls.get("search_term", ""),
            genes,
            phenotypes,
            diagnostics
        )
        
        # Update figure data based on controls
        fig_data = list(fig.data)
        updated_data = update_figure_data(fig_data, controls)
        
        # Create a new figure with the updated data
        updated_fig = go.Figure(data=updated_data, layout=fig.layout)
        
        # Set the figure size to be responsive and expand to full available space
        updated_fig.update_layout(
            autosize=True,
            showlegend=False,
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            margin=dict(t=0, l=0, r=0, b=0),  # Remove all margins around the plot
            uirevision='constant'  # Keep camera position on updates
        )
        
        # Completely remove all axis elements and grid
        # Update scene settings based on visibility
        updated_fig.update_layout(
            scene=dict(
                xaxis=dict(
                    showticklabels=False,
                    showspikes=False,
                    showgrid=False,
                    showline=False,
                    zeroline=False,
                    showaxeslabels=False,
                    visible=False,
                    backgroundcolor="#000000",
                    gridcolor="rgba(0,0,0,0)",
                    zerolinecolor="rgba(0,0,0,0)"
                ),
                yaxis=dict(
                    showticklabels=False,
                    showspikes=False,
                    showgrid=False,
                    showline=False,
                    zeroline=False,
                    showaxeslabels=False,
                    visible=False,
                    backgroundcolor="#000000",
                    gridcolor="rgba(0,0,0,0)",
                    zerolinecolor="rgba(0,0,0,0)"
                ),
                zaxis=dict(
                    showticklabels=False,
                    showspikes=False,
                    showgrid=False,
                    showline=False,
                    zeroline=False,
                    showaxeslabels=False,
                    visible=False,
                    backgroundcolor="#000000",
                    gridcolor="rgba(0,0,0,0)",
                    zerolinecolor="rgba(0,0,0,0)"
                ),
                bgcolor="#000000",  # Pure black to match website background
                # Increase zoom
                camera=dict(
                    eye=dict(x=0.90, y=0.90, z=0.90)  # Reducing eye distance for more zoom
                ),
                aspectmode='cube'  # Enforce equal scaling on all axes
            )
        )
        
        # Calculate visibility statistics
        visibility_stats = calculate_visibility_stats(
            controls, genes, phenotypes, diagnostics, graph_stats
        )
        
        # Update session state with current statistics
        update_graph_statistics(
            visibility_stats["visible_genes"],
            visibility_stats["visible_phenotypes"],
            visibility_stats["visible_diagnostics"],
            visibility_stats["visible_gene_pheno_edges"],
            visibility_stats["visible_pheno_diag_edges"],
            visibility_stats["displayed_edges"],
            graph_stats
        )
        
        # Check if visualization settings changed
        if check_controls_changed():
            # Update stored control state (animation has been removed)
            update_control_state()
        
        # Clear the placeholder (no longer used for animation)
        animation_placeholder.empty()
        
        # Create a container for the 3D graph with zero margins
        st.markdown("""
        <style>
        /* Zero margins between plot and info box */
        .js-plotly-plot, .plot-container, .svg-container {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create placeholders for controls and info box
        controls_placeholder = st.empty()
        info_box_placeholder = st.empty()
        
        # Display the interactive 3D graph with maximum size
        st.plotly_chart(
            updated_fig, 
            use_container_width=True,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'responsive': True,
                'scrollZoom': True
            },
            height=910  # Increased height by factor of 1.3 (700 * 1.3 = 910)
        )
        
        # Add controls between the graph and info box
        with controls_placeholder.container():
            st.markdown("<style>.control-container { background-color: #000000; padding: 10px; border-radius: 5px; border: 1px solid rgba(139, 233, 253, 0.2); margin-bottom: 10px; }</style>", unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="control-container">', unsafe_allow_html=True)
                
                # Create two columns for visibility controls
                visibility_col1, visibility_col2 = st.columns(2)
                
                # Node visibility controls in first column
                with visibility_col1:
                    st.write("**Show Nodes:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.session_state.controls["show_genes"] = st.checkbox("Genes", value=st.session_state.controls["show_genes"])
                    with col2:
                        st.session_state.controls["show_phenotypes"] = st.checkbox("Phenotypes", value=st.session_state.controls["show_phenotypes"])
                    with col3:
                        st.session_state.controls["show_diagnostics"] = st.checkbox("Diagnostics", value=st.session_state.controls["show_diagnostics"])
                
                # Edge visibility controls in second column
                with visibility_col2:
                    st.write("**Show Connections:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.session_state.controls["show_gene_pheno_edges"] = st.checkbox("Gene-Phenotype", value=st.session_state.controls["show_gene_pheno_edges"])
                    with col2:
                        st.session_state.controls["show_pheno_diag_edges"] = st.checkbox("Phenotype-Diagnostic", value=st.session_state.controls["show_pheno_diag_edges"])
                
                # Create two columns for opacity controls
                opacity_col1, opacity_col2 = st.columns(2)
                
                # Node opacity controls
                with opacity_col1:
                    st.write("**Node Opacity:**")
                    st.session_state.controls["gene_opacity"] = st.slider("Gene Opacity", min_value=0.1, max_value=1.0, value=st.session_state.controls["gene_opacity"], step=0.1)
                    st.session_state.controls["phenotype_opacity"] = st.slider("Phenotype Opacity", min_value=0.1, max_value=1.0, value=st.session_state.controls["phenotype_opacity"], step=0.1)
                    st.session_state.controls["diagnostic_opacity"] = st.slider("Diagnostic Opacity", min_value=0.1, max_value=1.0, value=st.session_state.controls["diagnostic_opacity"], step=0.1)
                
                # Edge opacity controls
                with opacity_col2:
                    st.write("**Connection Opacity:**")
                    st.session_state.controls["gene_pheno_opacity"] = st.slider("Gene-Phenotype Opacity", min_value=0.1, max_value=1.0, value=st.session_state.controls["gene_pheno_opacity"], step=0.1)
                    st.session_state.controls["pheno_diag_opacity"] = st.slider("Phenotype-Diagnostic Opacity", min_value=0.1, max_value=1.0, value=st.session_state.controls["pheno_diag_opacity"], step=0.1)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Add the explanation text below the controls using the placeholder
        info_box_placeholder.markdown("""
        <style>
        /* Info box styling */
        .info-box {
            background-color: #000000; 
            padding: 15px; 
            border-radius: 5px; 
            border: 1px solid rgba(139, 233, 253, 0.2);
            margin-top: 10px;
        }
        </style>
        <div class="info-box">
            This visualization maps the relationships between:
            <ul>
                <li><span style='color: #8be9fd; font-weight: bold;'>Genes</span> (blue nodes in the inner sphere)</li>
                <li><span style='color: #ffb86c; font-weight: bold;'>Phenotypes</span> (orange nodes in the middle sphere)</li>
                <li><span style='color: #ff79c6; font-weight: bold;'>Diagnostic measures</span> (magenta nodes in the outer sphere)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistics are now displayed in their own tab
        
        return updated_fig
        
    except Exception as e:
        st.error(f"Error updating graph visualization: {str(e)}")
        # Try to show the original figure as fallback
        try:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
            <div style='background-color: #000000; padding: 15px; border-radius: 5px; border: 1px solid rgba(139, 233, 253, 0.2);'>
                This visualization maps the relationships between:
                <ul>
                    <li><span style='color: #8be9fd; font-weight: bold;'>Genes</span> (blue nodes in the inner sphere)</li>
                    <li><span style='color: #ffb86c; font-weight: bold;'>Phenotypes</span> (orange nodes in the middle sphere)</li>
                    <li><span style='color: #ff79c6; font-weight: bold;'>Diagnostic measures</span> (magenta nodes in the outer sphere)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        except Exception as fallback_error:
            st.error(f"Unable to display graph visualization: {str(fallback_error)}. The dataset may be too large.")
        
        return fig