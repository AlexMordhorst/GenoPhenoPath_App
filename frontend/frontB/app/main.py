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
    
    # Add a button to reset the ontology (clear knowledge graph)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Maintenance")
    if st.sidebar.button("Reset Knowledge Graph"):
        with st.spinner("Resetting knowledge graph..."):
            # Clear the ontology
            clear_ontology()
            st.success("Knowledge graph has been reset.")
            
            # Also reset application state
            reset_application_state()
    
    # Add explanation for the reset button
    with st.sidebar.expander("What does Reset do?"):
        st.write("""
        The Reset button clears all entities from the knowledge graph. 
        Use this if you experience issues with gene selection or visualization.
        """)
    
    return selected_genes

def run_app():
    """
    Run the main GenoPhenoPath application.
    
    This function orchestrates the entire application flow:
    1. Configure page settings and styling
    2. Initialize session state
    3. Show landing page or visualization based on state
    4. Set up layout containers and visualization if needed
    
    Used in:
    - app.py: The main entry point for the Streamlit application
    """
    try:
        # Configure page settings and styling
        configure_page_settings()
        apply_custom_css()
        
        # Initialize session state
        initialize_graph_statistics()
        initialize_ui_state()
        
        # Initialize session state for gene selection and app state
        if 'selected_genes' not in st.session_state:
            st.session_state.selected_genes = []
        if 'show_visualization' not in st.session_state:
            st.session_state.show_visualization = False
        
        # Landing page
        if not st.session_state.show_visualization:
            selected_genes = create_landing_page()
            print(f"DEBUG - Selected genes from create_landing_page(): {selected_genes if selected_genes else 'None'}")
            
            # Store selected genes in session state immediately when they're returned
            if selected_genes:
                st.session_state.selected_genes = selected_genes
            
            # Button to generate visualization
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Visualize", type="primary", disabled=len(selected_genes) == 0):
                    print(f"DEBUG - Selected genes defined in run_app: {st.session_state.selected_genes if st.session_state.selected_genes else 'None'}")
                    st.session_state.show_visualization = True
                    st.rerun()
            with col1:
                if len(selected_genes) == 0:
                    st.info("Please select at least one gene to continue.")
        
        # Visualization page
        else:
            # Add a button to return to gene selection
            if st.button("← Back to Gene Selection"):
                # Clear the ontology to remove all gene entities
                clear_ontology()
                
                # Use comprehensive reset function to clear all application state
                reset_application_state()
                st.rerun()
            
            # Set up layout containers
            dropdown_container, animation_placeholder = create_layout_containers()
            print(f"DEBUG - Selected genes in run_app: {st.session_state.selected_genes if st.session_state.selected_genes else 'None'}")
            
            # Load data with animation, passing selected genes
            fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, elapsed_time, animation_frames = (
                load_data_with_animation(animation_placeholder, st.session_state.selected_genes)
            )
            
            # Create sidebar controls
            controls = create_sidebar_controls()
            
            # Store control values in session state for tracking changes
            for key, value in controls.items():
                st.session_state[key] = value
            
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
        
    except Exception as e:
        st.error(f"Error loading knowledge graph: {str(e)}")
        st.write("Please check that the backend modules are correctly configured and all dependencies are installed.")
        st.code("""
        # Make sure these packages are installed:
        pip install streamlit plotly networkx owlready2 pandas numpy matplotlib
        """)