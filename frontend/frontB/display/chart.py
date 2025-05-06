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
from typing import Dict, List, Any, Tuple, Callable

from frontend.frontA.session.state import update_graph_statistics
from frontend.frontB.interactions.search import handle_search

# Helper functions to make controls more responsive
def synchronize_control_to_state(control_name: str):
    """Callback function that syncs control widget value to session state"""
    if 'controls' in st.session_state:
        if f"cb_{control_name}" in st.session_state:
            # Update from checkbox
            st.session_state.controls[control_name] = st.session_state[f"cb_{control_name}"]
            # Set a flag to indicate the need for a rerun
            st.session_state.need_rerun = True
        elif f"sl_{control_name}" in st.session_state:
            # Update from slider
            st.session_state.controls[control_name] = st.session_state[f"sl_{control_name}"]
            # Set a flag to indicate the need for a rerun
            st.session_state.need_rerun = True

def create_checkbox(label: str, control_name: str, col=None):
    """Create a checkbox with automatic state management"""
    container = col if col else st
    current_value = st.session_state.controls.get(control_name, True)
    
    return container.checkbox(
        label,
        value=current_value,
        key=f"cb_{control_name}",
        on_change=synchronize_control_to_state,
        args=(control_name,)
    )
    
def create_slider(label: str, control_name: str, min_val: float, max_val: float, 
                  step: float, col=None):
    """Create a slider with automatic state management"""
    container = col if col else st
    current_value = st.session_state.controls.get(control_name, (min_val + max_val) / 2)
    
    return container.slider(
        label,
        min_value=min_val,
        max_value=max_val,
        value=current_value,
        step=step,
        key=f"sl_{control_name}",
        on_change=synchronize_control_to_state,
        args=(control_name,)
    )

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
    
    Note: 
    This function now uses a flag-based approach to handle control changes
    without using st.rerun() inside callbacks.
    """
    # Initialize the rerun flag if it doesn't exist
    if 'need_rerun' not in st.session_state:
        st.session_state.need_rerun = False
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
        
        # Clear the placeholder (no longer used for animation)
        animation_placeholder.empty()
        
        # Check if we need to rerun based on control changes
        if st.session_state.need_rerun:
            # Reset the flag
            st.session_state.need_rerun = False
            # Trigger the rerun from here (outside of any callback)
            st.rerun()
        
        # Apply targeted CSS to fix the canvas/container height mismatch
        st.markdown("""
        <style>
        /* Target the specific Plotly container-canvas gap */
        .js-plotly-plot, .plot-container.plotly {
            height: auto !important;
        }
        
        /* Force the main SVG to be the same height as the canvas */
        .main-svg {
            height: auto !important;
        }
        
        /* Force the container not to add extra space */
        .svg-container {
            padding-bottom: 0 !important;
        }
        
        /* Target the modebar to not create extra space */
        .modebar-container {
            transform: translateY(0) !important;
            height: 0 !important;
        }
        
        /* Fix plot dimensions and reduce its height */
        .plot-container {
            height: auto !important;
            max-height: none !important;
            min-height: 0 !important;
        }
        
        /* Place description immediately after the canvas */
        .js-plotly-plot + div {
            margin-top: -184px !important; /* Exactly the gap size you found */
        }
        
        /* Make sure description is visible above the gap */
        .legend-box {
            position: relative;
            background-color: rgba(0,0,0,0.8);
            z-index: 1000;
            margin-top: 0;
            padding: 10px;
            border-radius: 5px;
        }
        
        /* Override any colored styling in controls */
        .stSlider div[data-baseweb="slider"] div {
            background-color: rgba(50, 50, 50, 0.8) !important;
        }
        
        /* Style slider thumb/handle */
        .stSlider [role="slider"] {
            background-color: #aaaaaa !important;
            border-color: #cccccc !important;
        }
        
        /* Style checkboxes with neutral colors */
        .stCheckbox > div[role="checkbox"] > div:first-child {
            background-color: rgba(50, 50, 50, 0.8) !important;
            border-color: rgba(100, 100, 100, 0.3) !important;
        }
        
        /* Style checkbox checked state */
        .stCheckbox > div[role="checkbox"][data-checked="true"] > div:first-child {
            background-color: rgba(70, 70, 70, 0.9) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # CORE APPROACH: Use st.columns to force vertical stacking without spacing
        col1 = st.container()
        
        # 1. Visualization in the first slot
        with col1:
            # Display the plot with minimal height
            st.plotly_chart(
                updated_fig, 
                use_container_width=True,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'responsive': True,
                    'scrollZoom': True
                },
                height=650  # Further reduced height
            )
        
        # 2. Add the legend that will overlap with the gap between canvas and container
        st.markdown("""
        <div class="legend-box" style="margin-top: -184px;">
            <span>This visualization maps the relationships between:</span>
            <ul style="margin-top: 0; margin-bottom: 0; padding-top: 0; padding-bottom: 0; list-style-position: inside;">
                <li><span style='color: #8be9fd; font-weight: bold;'>Genes</span> (blue nodes in the inner sphere)</li>
                <li><span style='color: #ffb86c; font-weight: bold;'>Phenotypes</span> (orange nodes in the middle sphere)</li>
                <li><span style='color: #ff79c6; font-weight: bold;'>Diagnostic measures</span> (magenta nodes in the outer sphere)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Add controls header with minimal spacing
        st.markdown("<hr style='margin: 5px 0; border-color: #333;'><h4 style='margin: 5px 0;'>Controls</h4>", unsafe_allow_html=True)
        
        with st.container():
            # Create two columns for visibility controls
            visibility_col1, visibility_col2 = st.columns(2)
            
            # Node visibility controls in first column
            with visibility_col1:
                st.markdown('<p style="margin: 0; padding: 0;"><b>Show Nodes:</b></p>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                create_checkbox("Genes", "show_genes", col1)
                create_checkbox("Phenotypes", "show_phenotypes", col2)
                create_checkbox("Diagnostics", "show_diagnostics", col3)
            
            # Edge visibility controls in second column
            with visibility_col2:
                st.markdown('<p style="margin: 0; padding: 0;"><b>Show Connections:</b></p>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                create_checkbox("Gene-Phenotype", "show_gene_pheno_edges", col1)
                create_checkbox("Phenotype-Diagnostic", "show_pheno_diag_edges", col2)
                
            # Add a small spacer
            st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)
            
            # Create two columns for opacity controls
            opacity_col1, opacity_col2 = st.columns(2)
            
            # Node opacity controls
            with opacity_col1:
                st.markdown('<p style="margin: 0; padding: 0;"><b>Node Opacity:</b></p>', unsafe_allow_html=True)
                create_slider("Gene Opacity", "gene_opacity", 0.1, 1.0, 0.1, opacity_col1)
                create_slider("Phenotype Opacity", "phenotype_opacity", 0.1, 1.0, 0.1, opacity_col1)
                create_slider("Diagnostic Opacity", "diagnostic_opacity", 0.1, 1.0, 0.1, opacity_col1)
            
            # Edge opacity controls
            with opacity_col2:
                st.markdown('<p style="margin: 0; padding: 0;"><b>Connection Opacity:</b></p>', unsafe_allow_html=True)
                create_slider("Gene-Phenotype Opacity", "gene_pheno_opacity", 0.1, 1.0, 0.1, opacity_col2)
                create_slider("Phenotype-Diagnostic Opacity", "pheno_diag_opacity", 0.1, 1.0, 0.1, opacity_col2)
        
        # Statistics are now displayed in their own tab
        
        return updated_fig
        
    except Exception as e:
        st.error(f"Error updating graph visualization: {str(e)}")
        # Try to show the original figure as fallback
        try:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
                This visualization maps the relationships between:
                <ul>
                    <li><span style='color: #8be9fd; font-weight: bold;'>Genes</span> (blue nodes in the inner sphere)</li>
                    <li><span style='color: #ffb86c; font-weight: bold;'>Phenotypes</span> (orange nodes in the middle sphere)</li>
                    <li><span style='color: #ff79c6; font-weight: bold;'>Diagnostic measures</span> (magenta nodes in the outer sphere)</li>
                </ul>
            """, unsafe_allow_html=True)
        except Exception as fallback_error:
            st.error(f"Unable to display graph visualization: {str(fallback_error)}. The dataset may be too large.")
        
        return fig