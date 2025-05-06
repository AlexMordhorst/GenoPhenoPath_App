"""
Sidebar controls for the GenoPhenoPath application.

This module provides user interface controls for customizing the graph visualization
through the Streamlit sidebar.

Functions in this module are used in:
- frontend.frontB.app.main: For initializing the UI controls
- frontend.frontB.display.chart: For applying control changes to the visualization
"""

import streamlit as st
from typing import Dict, Any, Tuple

def create_sidebar_controls() -> Dict[str, Any]:
    """
    Create a sidebar with controls for customizing the visualization.
    
    This function provides controls for:
    - Node visibility
    - Edge visibility
    - Node size and opacity
    - Edge opacity
    - Performance settings
    - Search functionality
    - Graph regeneration
    
    Returns:
        Dictionary with control values:
        - show_genes: Boolean for gene nodes visibility
        - show_phenotypes: Boolean for phenotype nodes visibility
        - show_diagnostics: Boolean for diagnostic nodes visibility
        - show_gene_pheno_edges: Boolean for gene-phenotype edges visibility
        - show_pheno_diag_edges: Boolean for phenotype-diagnostic edges visibility
        - search_term: String with search query
        - gene_size: Float with gene node size
        - phenotype_size: Float with phenotype node size
        - diagnostic_size: Float with diagnostic node size
        - gene_opacity: Float with gene node opacity
        - phenotype_opacity: Float with phenotype node opacity
        - diagnostic_opacity: Float with diagnostic node opacity
        - gene_pheno_opacity: Float with gene-phenotype edge opacity
        - pheno_diag_opacity: Float with phenotype-diagnostic edge opacity
        - edge_limit: Int or string with edge limit setting
        
    Used in:
    - frontend.frontB.app.main.run_app
    - frontend.frontB.display.chart.update_visualization
    """
    controls = {}
    
    with st.sidebar:
        st.header("Display Controls")
        
        # Section for node visibility
        st.subheader("Show/Hide Nodes")
        
        # Node visibility checkboxes
        controls["show_genes"] = st.checkbox("Genes (blue)", value=True)
        controls["show_phenotypes"] = st.checkbox("Phenotypes (orange)", value=True)
        controls["show_diagnostics"] = st.checkbox("Diagnostic Measures (magenta)", value=True)
        
        # Section for edge visibility
        st.subheader("Show/Hide Connections")
        
        # Edge visibility checkboxes
        controls["show_gene_pheno_edges"] = st.checkbox("Gene-Phenotype Connections", value=True)
        controls["show_pheno_diag_edges"] = st.checkbox("Phenotype-Diagnostic Connections", value=True)
        
        # Add a search option
        st.subheader("Search")
        controls["search_term"] = st.text_input("🔍 Search for a node")
        
        # Size controls
        st.subheader("Node Size")
        controls["gene_size"] = st.slider("Gene Size", min_value=1, max_value=20, value=10)
        controls["phenotype_size"] = st.slider("Phenotype Size", min_value=1, max_value=10, value=3)
        controls["diagnostic_size"] = st.slider("Diagnostic Size", min_value=1, max_value=15, value=8)
        
        # Opacity controls
        st.subheader("Opacity")
        controls["gene_opacity"] = st.slider("Gene Opacity", min_value=0.1, max_value=1.0, value=0.9, step=0.1)
        controls["phenotype_opacity"] = st.slider("Phenotype Opacity", min_value=0.1, max_value=1.0, value=0.2, step=0.1)
        controls["diagnostic_opacity"] = st.slider("Diagnostic Opacity", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
        controls["gene_pheno_opacity"] = st.slider("Gene-Phenotype Connection Opacity", min_value=0.1, max_value=1.0, value=0.4, step=0.1)
        controls["pheno_diag_opacity"] = st.slider("Phenotype-Diagnostic Connection Opacity", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
        
        # Performance control
        st.subheader("Performance")
        controls["edge_limit"] = st.select_slider(
            "Edge Limit",
            options=[100, 250, 500, 750, 1000, "No Limit"],
            value=1000,
            help="Limit edges to improve performance"
        )
        
        # Action buttons
        st.subheader("Actions")
        if st.button("Regenerate Graph"):
            st.cache_data.clear()
        
        # Credit at the bottom
        st.markdown("---")
        st.caption("Built with Streamlit & Plotly")
    
    return controls

def check_controls_changed() -> bool:
    """
    Check if any visualization controls have changed.
    
    This function compares the current state of controls with their previous state
    to detect changes that require visualization updates.
    
    Returns:
        Boolean indicating if controls have changed
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    # Skip check if this is the first time we're running
    if 'last_controls' not in st.session_state:
        st.session_state.last_controls = {}
        # First run, so consider it changed
        return True
    
    # Get current controls
    current_controls = st.session_state.controls
    
    # Get last saved controls
    last_controls = st.session_state.last_controls
    
    # Check if any control has changed between the current and last state
    for key in current_controls:
        if key not in last_controls or current_controls[key] != last_controls[key]:
            return True
    
    # No changes detected
    return False

def update_control_state():
    """
    Update the stored state of controls in the session state.
    
    This function updates the remembered state of controls to reflect the current state,
    which helps detect future changes.
    
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    # Make a deep copy of the current controls
    st.session_state.last_controls = dict(st.session_state.controls)