"""
Session state management for the GenoPhenoPath application.

This module handles the initialization and management of Streamlit session state variables
used for tracking graph statistics and UI state throughout the application.

Functions in this module are used in:
- frontend.frontB.app.main: For initializing the application state
- frontend.frontB.interactions.controls: For tracking UI state changes
"""

import streamlit as st
from typing import Dict, Any

def initialize_graph_statistics():
    """
    Initialize graph statistics in the session state.
    
    This function creates a container in the session state to store graph statistics
    including node counts, edge counts, and visibility state.
    
    Used in:
    - frontend.frontB.app.main.run_app
    """
    if 'graph_statistics' not in st.session_state:
        st.session_state.graph_statistics = {
            'gene_count': 0,
            'phenotype_count': 0,
            'diagnostic_count': 0,
            'gene_pheno_edges': 0,
            'pheno_diag_edges': 0,
            'total_edges': 0,
            'visible_genes': 0,
            'visible_phenotypes': 0,
            'visible_diagnostics': 0,
            'visible_gene_pheno_edges': 0,
            'visible_pheno_diag_edges': 0,
            'visible_total_edges': 0
        }

def initialize_ui_state():
    """
    Initialize UI state tracking variables in the session state.
    
    This function creates variables to track changes in UI controls 
    (like checkboxes and sliders) to trigger dynamic UI updates.
    
    Used in:
    - frontend.frontB.app.main.run_app
    - frontend.frontB.interactions.controls.create_sidebar_controls
    """
    # Create session state variables to track changes
    if 'last_gene_state' not in st.session_state:
        st.session_state.last_gene_state = True
    if 'last_phenotype_state' not in st.session_state:
        st.session_state.last_phenotype_state = True
    if 'last_diagnostic_state' not in st.session_state:
        st.session_state.last_diagnostic_state = True
    if 'last_gene_pheno_edges_state' not in st.session_state:
        st.session_state.last_gene_pheno_edges_state = True
    if 'last_pheno_diag_edges_state' not in st.session_state:
        st.session_state.last_pheno_diag_edges_state = True

def update_graph_statistics(
    visible_genes: int,
    visible_phenotypes: int,
    visible_diagnostics: int,
    visible_gene_pheno_edges: int,
    visible_pheno_diag_edges: int,
    displayed_edges: int,
    stats: Dict[str, Any]
):
    """
    Update graph statistics in the session state.
    
    Args:
        visible_genes: Number of visible gene nodes
        visible_phenotypes: Number of visible phenotype nodes
        visible_diagnostics: Number of visible diagnostic nodes
        visible_gene_pheno_edges: Number of visible gene-phenotype edges
        visible_pheno_diag_edges: Number of visible phenotype-diagnostic edges
        displayed_edges: Total number of displayed edges
        stats: Dictionary with full graph statistics
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    # Store the total statistics in session_state
    st.session_state.graph_statistics = {
        'gene_count': len(stats.get("genes", [])),
        'phenotype_count': len(stats.get("phenotypes", [])),
        'diagnostic_count': len(stats.get("diagnostics", [])),
        'gene_pheno_edges': stats.get("gene_to_pheno_edges", 0),
        'pheno_diag_edges': stats.get("pheno_to_diag_edges", 0),
        'total_edges': stats.get("total_edges", 0),
        'visible_genes': visible_genes,
        'visible_phenotypes': visible_phenotypes,
        'visible_diagnostics': visible_diagnostics,
        'visible_gene_pheno_edges': visible_gene_pheno_edges,
        'visible_pheno_diag_edges': visible_pheno_diag_edges,
        'visible_total_edges': displayed_edges
    }