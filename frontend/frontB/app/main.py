"""
Main application runner for the GenoPhenoPath application.

This module orchestrates the full application lifecycle including initialization,
data loading, UI setup, and visualization rendering.

Functions in this module are used in:
- app.py: The main entry point for the Streamlit application
"""

import streamlit as st
import threading
import time
import random
import pandas as pd
from typing import Any, Dict, List, Tuple

from frontend.frontA.stages.layout import configure_page_settings, apply_custom_css, create_layout_containers
from frontend.frontA.session.state import initialize_graph_statistics, initialize_ui_state, reset_application_state
from frontend.frontA.animations.dna_helix import generate_animation_frames, display_dna_animation
from frontend.frontB.interactions.controls import create_sidebar_controls
from frontend.frontB.display.chart import update_visualization
from backend.backA.data_processing.loader import load_unique_genes
from backend.backA.ontology.schema import clear_ontology

def load_knowledge_graph(selected_genes=None):
    """
    Load the knowledge graph from the backend controller.
    
    This function calls the backend controller to create the knowledge graph,
    get the visualization, and retrieve node and edge data.
    
    Args:
        selected_genes: Optional list of gene symbols to filter the graph
    
    Returns:
        Tuple containing:
        - Plotly Figure
        - List of gene names
        - List of phenotype names
        - List of diagnostic names
        - Dictionary of 3D positions
        - NetworkX graph
        - Dictionary of graph statistics
        - Elapsed time (seconds)
        
    Used in:
    - frontend.frontB.app.main.load_data_with_animation
    """
    try:
        import time
        start_time = time.time()
        
        # Import the function directly from the backend controller
        from backend.controller import create_knowledge_graph
        
        # Call the function to get all necessary data, passing selected genes if provided
        print(f"DEBUG - Selected genes in load_knowledge_graph: {selected_genes if selected_genes else 'None'}")
        fig, community_0, community_1, community_2, spring_3D, G, graph_stats = create_knowledge_graph(selected_genes)
        
        # Log performance info
        elapsed_time = time.time() - start_time
        
        return fig, community_0, community_1, community_2, spring_3D, G, graph_stats, elapsed_time
    except Exception as e:
        raise e

def load_data_with_animation(animation_placeholder: Any, selected_genes=None):
    """
    Load the knowledge graph data with an animation displayed during loading.
    
    Args:
        animation_placeholder: Streamlit container for the animation
        selected_genes: Optional list of gene symbols to filter the graph
        
    Returns:
        Tuple containing:
        - Plotly Figure
        - List of gene names
        - List of phenotype names
        - List of diagnostic names
        - Dictionary of 3D positions
        - NetworkX graph
        - Dictionary of graph statistics
        - Loading time (seconds)
        - List of animation frames (for transitions)
        
    Used in:
    - frontend.frontB.app.main.run_app
    """
    # Use a list to store the result since nonlocal isn't available
    result = [None]
    # Flag to indicate when loading is complete
    loading_complete = [False]
    
    def load_data_thread():
        # Call the non-cached function with selected genes if provided
        print(f"DEBUG - Selected genes in load_data_with_animation: {selected_genes if selected_genes else 'None'}")
        result[0] = load_knowledge_graph(selected_genes)
        loading_complete[0] = True
    
    # Start the loading in a separate thread
    loading_thread = threading.Thread(target=load_data_thread)
    loading_thread.start()
    
    # Generate animation frames
    animation_length = 100
    frames = generate_animation_frames(animation_length)
    frame_index = 0
    
    # Show DNA animation while loading
    with st.spinner(""):
        # Display the spinning DNA animation while loading
        while not loading_complete[0]:
            frame_index = display_dna_animation(
                animation_placeholder,
                frames,
                frame_index
            )
    
    # Clear the animation when done
    animation_placeholder.empty()
    
    # Get the result
    fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, elapsed_time = result[0]
    
    # Show toast when loading completes
    st.toast(f"Graph loaded in {elapsed_time:.2f} seconds")
    
    return fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, elapsed_time, frames

def create_landing_page():
    """
    Create the landing page for gene selection.
    
    This function creates the UI for users to select genes either by manual input
    or random selection.
    
    Returns:
        List of selected gene symbols
    """
    st.title("GenoPhenoPath: Gene Selection")
    st.write("Select genes to include in the knowledge graph visualization.")
    
    # Load unique genes for validation
    unique_genes_df = load_unique_genes()
    unique_gene_list = unique_genes_df['gene_symbol'].tolist()
    total_genes = len(unique_gene_list)
    
    st.write(f"Available genes: {total_genes}")
    
    # Gene input methods
    input_method = st.radio("Select how to input genes:", 
                          ["Manual Entry", "Random Selection"])
    
    selected_genes = []
    
    if input_method == "Manual Entry":
        # Comma-separated gene input
        gene_input = st.text_area("Enter gene symbols (comma-separated):", 
                                height=150,
                                help="e.g., BRCA1, BRCA2, TP53")
        
        if gene_input:
            input_genes = [g.strip() for g in gene_input.split(',') if g.strip()]
            
            # Validate genes
            valid_genes = [g for g in input_genes if g in unique_gene_list]
            invalid_genes = [g for g in input_genes if g not in unique_gene_list and g.strip()]
            
            if invalid_genes:
                st.warning(f"Invalid genes (will be dropped): {', '.join(invalid_genes)}")
            
            selected_genes = valid_genes
    else:
        # Random gene selection
        col1, col2 = st.columns([3, 1])
        with col1:
            num_genes = st.number_input("Number of random genes:", 
                                      min_value=1, 
                                      max_value=total_genes, 
                                      value=10)
        with col2:
            if st.button("Generate"):
                # Ensure not selecting more genes than available
                max_genes = min(num_genes, total_genes)
                selected_genes = random.sample(unique_gene_list, max_genes)
    
    # Show selected genes
    if selected_genes:
        st.write(f"Selected genes ({len(selected_genes)}):")
        st.write(", ".join(selected_genes))
    
    # Add a reset button at the bottom of the landing page
    if st.button("Reset All"):
        with st.spinner("Resetting application..."):
            # Clear the ontology
            clear_ontology()
            st.success("Application has been reset.")
            
            # Also reset application state
            reset_application_state()
    
    return selected_genes

def create_phenotype_list_page(phenotypes):
    """
    Create a page that displays a list of all phenotypes in the knowledge graph.
    
    Args:
        phenotypes: List of phenotype names
    """
    st.title("GenoPhenoPath: Phenotypes")
    
    if not phenotypes or len(phenotypes) == 0:
        st.info("No phenotypes available. Please add genes in the Gene Selection tab first.")
        return
    
    st.write(f"Total phenotypes: {len(phenotypes)}")
    
    # Display phenotypes as a sortable dataframe
    df = pd.DataFrame({"Phenotype": sorted(phenotypes)})
    st.dataframe(df, use_container_width=True)

def run_app():
    """
    Run the main GenoPhenoPath application.
    
    This function orchestrates the entire application flow using a tabbed interface:
    1. Configure page settings and styling
    2. Initialize session state
    3. Set up the tab interface as the main navigation
    4. Display appropriate content based on the selected tab
    
    Used in:
    - app.py: The main entry point for the Streamlit application
    """
    try:
        # Configure page settings and styling
        configure_page_settings()
        apply_custom_css()
        
        # Add HTML viewport meta tag to ensure proper scaling on all devices
        st.markdown("""
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <style>
                html, body {
                    height: 100vh;
                    width: 100vw;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
            </style>
        </head>
        """, unsafe_allow_html=True)
        
        # Initialize session state
        initialize_graph_statistics()
        initialize_ui_state()
        
        # Initialize session state for gene selection, visualization and phenotypes
        if 'selected_genes' not in st.session_state:
            st.session_state.selected_genes = []
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = "Gene Selection"
        if 'graph_data' not in st.session_state:
            st.session_state.graph_data = None
        if 'has_generated_graph' not in st.session_state:
            st.session_state.has_generated_graph = False
            
        # Create tabs
        tab_titles = ["Gene Selection", "Knowledge Graph", "Phenotypes"]
        
        # Determine if other tabs should be enabled
        has_genes = len(st.session_state.selected_genes) > 0
        
        # Create the tabs
        genes_tab, graph_tab, phenotypes_tab = st.tabs(tab_titles)
        
        # Gene Selection Tab
        with genes_tab:
            selected_genes = create_landing_page()
            
            # Store selected genes in session state immediately when they're returned
            if selected_genes:
                st.session_state.selected_genes = selected_genes
                
                # Generate graph automatically if genes were selected and graph hasn't been generated yet
                if not st.session_state.has_generated_graph:
                    # Set up a placeholder for animation while generating graph
                    animation_placeholder = st.empty()
                    
                    with st.spinner("Generating knowledge graph..."):
                        # Load data with animation, passing selected genes
                        graph_data = load_data_with_animation(animation_placeholder, selected_genes)
                        st.session_state.graph_data = graph_data
                        st.session_state.has_generated_graph = True
                    
                    st.success("Knowledge graph generated. You can now navigate to the Knowledge Graph and Phenotypes tabs.")
                    st.rerun()  # Rerun to reflect the changes in tab state
        
        # Knowledge Graph Tab
        with graph_tab:
            if not has_genes:
                st.info("Please select genes in the Gene Selection tab first.")
            elif not st.session_state.has_generated_graph:
                st.info("Please wait while the knowledge graph is being generated...")
            else:
                # Set up layout containers
                dropdown_container, animation_placeholder = create_layout_containers()
                
                # Retrieve graph data from session state
                (fig, genes, phenotypes, diagnostics, layout_3d, graph, 
                 graph_stats, elapsed_time, animation_frames) = st.session_state.graph_data
                
                # Create controls without using sidebar
                controls_col1, controls_col2 = st.columns(2)
                
                with controls_col1:
                    show_genes = st.checkbox("Show Genes", value=True)
                    show_phenotypes = st.checkbox("Show Phenotypes", value=True)
                    show_diagnostics = st.checkbox("Show Diagnostics", value=True)
                
                with controls_col2:
                    show_gene_pheno_edges = st.checkbox("Show Gene-Phenotype Edges", value=True)
                    show_pheno_diag_edges = st.checkbox("Show Phenotype-Diagnostic Edges", value=True)
                
                controls = {
                    "show_genes": show_genes,
                    "show_phenotypes": show_phenotypes, 
                    "show_diagnostics": show_diagnostics,
                    "show_gene_pheno_edges": show_gene_pheno_edges,
                    "show_pheno_diag_edges": show_pheno_diag_edges
                }
                
                # Store control values in session state for tracking changes
                for key, value in controls.items():
                    st.session_state[key] = value
                
                # Update and display visualization with full height
                st.markdown("""
                <style>
                    /* Make the visualization container take maximum height */
                    .graph-container {
                        height: 80vh !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # Create a container with specific class for styling
                with st.container():
                    # Update and display visualization
                    updated_fig = update_visualization(
                        fig,
                        controls,
                        animation_placeholder,
                        animation_frames,
                        dropdown_container,
                        genes,
                        phenotypes,
                        diagnostics,
                        graph_stats
                    )
                
                # Button to regenerate graph with updated gene selection
                if st.button("Regenerate Knowledge Graph"):
                    # Clear the ontology to remove all gene entities
                    clear_ontology()
                    
                    # Set up a placeholder for animation
                    animation_placeholder = st.empty()
                    
                    with st.spinner("Regenerating knowledge graph..."):
                        # Load data with animation, passing selected genes
                        graph_data = load_data_with_animation(animation_placeholder, st.session_state.selected_genes)
                        st.session_state.graph_data = graph_data
                    
                    st.success("Knowledge graph regenerated.")
                    st.rerun()
        
        # Phenotypes Tab
        with phenotypes_tab:
            if not has_genes:
                st.info("Please select genes in the Gene Selection tab first.")
            elif not st.session_state.has_generated_graph:
                st.info("Please wait while the knowledge graph is being generated...")
            else:
                # Extract phenotypes from the graph data
                phenotypes = st.session_state.graph_data[2]  # Index 2 contains phenotypes
                create_phenotype_list_page(phenotypes)
        
    except Exception as e:
        st.error(f"Error loading knowledge graph: {str(e)}")
        st.write("Please check that the backend modules are correctly configured and all dependencies are installed.")
        st.code("""
        # Make sure these packages are installed:
        pip install streamlit plotly networkx owlready2 pandas numpy matplotlib
        """)