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
    
    This function creates the UI for users to select genes through manual input
    and random selection, both always visible.
    
    Returns:
        List of selected gene symbols
    """
    st.title("GenoPhenoPath: Gene Selection")
    st.write("Select genes to include in the knowledge graph visualization.")
    
    # Load unique genes for validation
    unique_genes_df = load_unique_genes()
    unique_gene_list = [gene.upper() for gene in unique_genes_df['gene_symbol'].tolist()]  # Convert to uppercase
    total_genes = len(unique_gene_list)
    
    st.write(f"Available genes: {total_genes}")
    
    # Initialize the key for the text area in session state if not present
    if 'gene_input_text' not in st.session_state:
        st.session_state.gene_input_text = ""
    
    # Comma-separated gene input - Always visible
    gene_input = st.text_area("Enter gene symbols (comma-separated):", 
                            value=st.session_state.gene_input_text,
                            height=150,
                            help="e.g., BRCA1, BRCA2, TP53",
                            key="gene_input")
    
    # Process manual input
    input_genes = []
    if gene_input:
        # Convert to uppercase before processing
        input_genes = [g.strip().upper() for g in gene_input.split(',') if g.strip()]
        
    # Random gene selection - Always visible
    st.write("Add random genes:")
    col1, col2 = st.columns([3, 1])
    with col1:
        num_genes = st.number_input("Number of random genes:", 
                                  min_value=1, 
                                  max_value=total_genes, 
                                  value=5)
    with col2:
        generate_clicked = st.button("Generate")
        if generate_clicked:
            # Ensure not selecting more genes than available
            max_genes = min(num_genes, total_genes)
            random_genes = random.sample(unique_gene_list, max_genes)
            
            # Append random genes to any existing manually entered genes
            new_gene_list = input_genes.copy() if input_genes else []
            
            # Add random genes that aren't already in the list
            for gene in random_genes:
                if gene not in new_gene_list:
                    new_gene_list.append(gene)
            
            # Update the text area with the combined list
            st.session_state.gene_input_text = ", ".join(new_gene_list)
            st.rerun()
    
    # Validate genes against the uppercase list
    valid_genes = [g for g in input_genes if g in unique_gene_list]
    invalid_genes = [g for g in input_genes if g not in unique_gene_list and g.strip()]
    
    if invalid_genes:
        st.warning(f"Invalid genes (will be dropped): {', '.join(invalid_genes)}")
    
    selected_genes = valid_genes
    
    # Show selected genes
    if selected_genes:
        st.write(f"Selected genes ({len(selected_genes)}):")
        st.write(", ".join(selected_genes))
        
        # Store selected genes in session state to ensure they're used for graph building
        # Check if the selection has changed
        if set(selected_genes) != set(st.session_state.previous_gene_selection):
            st.session_state.selected_genes = selected_genes
            st.session_state.needs_graph_update = True
            st.session_state.previous_gene_selection = selected_genes.copy()
        else:
            st.session_state.selected_genes = selected_genes
    
    # Add a reset button at the bottom of the landing page
    if st.button("Reset All"):
        with st.spinner("Resetting application..."):
            # Clear the ontology
            clear_ontology()
            
            # Reset all gene selection related state
            st.session_state.gene_input_text = ""
            st.session_state.selected_genes = []
            st.session_state.previous_gene_selection = []
            st.session_state.has_generated_graph = False
            st.session_state.needs_graph_update = False
            
            # Also reset application state
            reset_application_state()
            st.success("Application has been reset.")
            st.rerun()
    
    return selected_genes

def create_phenotype_list_page(phenotypes):
    """
    Create a page that displays a list of all phenotypes in the knowledge graph.
    
    Args:
        phenotypes: List of phenotype IDs
    """
    st.title("GenoPhenoPath: Phenotypes")
    
    if not phenotypes or len(phenotypes) == 0:
        st.info("No phenotypes available. Please add genes in the Gene Selection tab first.")
        return
    
    st.write(f"Total phenotypes: {len(phenotypes)}")
    
    # Load unique phenotypes with names
    try:
        from backend.backA.data_processing.loader import load_unique_phenotypes
        unique_phenotypes_df = load_unique_phenotypes()
        
        # Create a display DataFrame with both IDs and names
        display_data = []
        for phen_id in sorted(phenotypes):
            name = "Unknown"
            matches = unique_phenotypes_df[unique_phenotypes_df['hpo_id'] == phen_id]
            if not matches.empty:
                name = matches.iloc[0]['hpo_name']
            display_data.append({"HPO ID": phen_id, "Phenotype Name": name})
        
        df = pd.DataFrame(display_data)
    except Exception as e:
        # Fallback to just showing the IDs if there's an issue with the enhanced display
        print(f"Error loading phenotype names: {e}")
        df = pd.DataFrame({"HPO ID": sorted(phenotypes)})
    
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
        
        # Add HTML viewport meta tag to ensure proper scaling on all devices and remove ALL margins
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
                
                /* EXTREMELY aggressive removal of ALL top margins and padding */
                .element-container, 
                div[data-testid="block-container"], 
                div[data-testid="stVerticalBlock"],
                div.stTabs,
                div.stTabs > div,
                div.stTabs > div > div,
                div.stTabs > div > div > div,
                [data-testid="stDecoration"],
                header,
                section[data-testid="stHeader"],
                div[data-testid="stToolbar"],
                div.main,
                div.main div,
                .stMarkdown,
                .stMarkdown div,
                .stMarkdown div p,
                .streamlit-container,
                .streamlit-container div,
                .streamlit-container div > div,
                .stApp,
                [data-testid="stAppViewContainer"],
                [data-testid="stAppViewContainer"] > div {
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                }
                
                /* Specifically target the streamlit header which often adds space */
                div[data-testid="stHeader"] {
                    display: none !important;
                    height: 0 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    visibility: hidden !important;
                }
                
                /* Move everything to the very top */
                .stApp {
                    margin-top: -10px !important;
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
        if 'needs_graph_update' not in st.session_state:
            st.session_state.needs_graph_update = False
        if 'previous_gene_selection' not in st.session_state:
            st.session_state.previous_gene_selection = []
            
        # Create tabs
        tab_titles = ["Gene Selection", "Knowledge Graph", "Phenotypes", "Statistics"]
        
        # Determine if other tabs should be enabled
        has_genes = len(st.session_state.selected_genes) > 0
        
        # Create the tabs
        genes_tab, graph_tab, phenotypes_tab, stats_tab = st.tabs(tab_titles)
        
        # Gene Selection Tab
        with genes_tab:
            selected_genes = create_landing_page()
            
            # Check if we need to generate/update the graph
            # This happens when:
            # 1. Genes are selected AND
            # 2. Either the graph hasn't been generated yet OR the gene selection has changed
            if selected_genes and (not st.session_state.has_generated_graph or st.session_state.needs_graph_update):
                # Set up a placeholder for animation while generating graph
                animation_placeholder = st.empty()
                
                # Generate the graph with the current selection
                with st.spinner("Generating knowledge graph..."):
                    # Load data with animation, passing selected genes
                    graph_data = load_data_with_animation(animation_placeholder, selected_genes)
                    st.session_state.graph_data = graph_data
                    st.session_state.has_generated_graph = True
                    # Reset the update flag
                    st.session_state.needs_graph_update = False
                
                st.success("Knowledge graph generated. You can now navigate to the Knowledge Graph and Phenotypes tabs.")
                # This rerun is needed but only done once after graph generation
                st.rerun()  # Rerun to reflect the changes in tab state
        
        # Knowledge Graph Tab
        with graph_tab:
            if not has_genes:
                st.info("Please select genes in the Gene Selection tab first.")
            elif not st.session_state.has_generated_graph:
                st.info("Please wait while the knowledge graph is being generated...")
            else:
                # Create animation placeholder
                animation_placeholder = st.empty()
                
                # Retrieve graph data from session state
                (fig, genes, phenotypes, diagnostics, layout_3d, graph, 
                 graph_stats, elapsed_time, animation_frames) = st.session_state.graph_data
                
                # Initialize controls with default values
                if 'controls' not in st.session_state:
                    # Default control values
                    st.session_state.controls = {
                        "show_genes": True,
                        "show_phenotypes": True, 
                        "show_diagnostics": True,
                        "show_gene_pheno_edges": True,
                        "show_pheno_diag_edges": True,
                        "gene_size": 10,
                        "phenotype_size": 3,
                        "diagnostic_size": 8,
                        "gene_opacity": 0.9,
                        "phenotype_opacity": 0.2,
                        "diagnostic_opacity": 0.7,
                        "gene_pheno_opacity": 0.4,
                        "pheno_diag_opacity": 0.3,
                        "edge_limit": 1000,
                        "search_term": ""
                    }
                
                # Use the controls from session state
                controls = st.session_state.controls
                
                # Update and display visualization with full height
                st.markdown("""
                <style>
                    /* Make the visualization container take maximum height */
                    .graph-container {
                        height: 104vh !important; /* Increased by factor of 1.3 (80vh * 1.3 = 104vh) */
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
                    # No rerun needed here - it will refresh naturally when the button is clicked
        
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
                
        # Statistics Tab
        with stats_tab:
            if not has_genes:
                st.info("Please select genes in the Gene Selection tab first.")
            elif not st.session_state.has_generated_graph:
                st.info("Please wait while the knowledge graph is being generated...")
            else:
                # Retrieve graph data from session state
                (fig, genes, phenotypes, diagnostics, layout_3d, graph, 
                 graph_stats, elapsed_time, animation_frames) = st.session_state.graph_data
                
                st.title("Knowledge Graph Statistics")
                
                # Calculate statistics based on current control settings
                from frontend.frontB.display.chart import calculate_visibility_stats
                
                visibility_stats = calculate_visibility_stats(
                    st.session_state.controls, genes, phenotypes, diagnostics, graph_stats
                )
                
                # Display the statistics in a nice layout
                st.markdown("""
                <style>
                .stats-container {
                    background-color: #000000;
                    border-radius: 5px;
                    border: 1px solid rgba(139, 233, 253, 0.2);
                    padding: 20px;
                    margin-bottom: 20px;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Node statistics
                st.markdown("<div class='stats-container'>", unsafe_allow_html=True)
                st.subheader("Node Statistics")
                
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
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Displayed Nodes", visibility_stats["displayed_nodes"])
                with col2:
                    st.metric("Total Available Nodes", len(genes) + len(phenotypes) + len(diagnostics))
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Edge statistics
                st.markdown("<div class='stats-container'>", unsafe_allow_html=True)
                st.subheader("Edge Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Gene-Phenotype Edges", visibility_stats["visible_gene_pheno_edges"])
                with col2:
                    st.metric("Phenotype-Diagnostic Edges", visibility_stats["visible_pheno_diag_edges"])
                with col3:
                    st.metric("Total Edges", visibility_stats["displayed_edges"])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Gene-Phenotype Density", f"{visibility_stats['visible_gene_pheno_edges'] / (visibility_stats['visible_genes'] * visibility_stats['visible_phenotypes']):.4f}" if visibility_stats['visible_genes'] > 0 and visibility_stats['visible_phenotypes'] > 0 else "N/A")
                with col2:
                    st.metric("Phenotype-Diagnostic Density", f"{visibility_stats['visible_pheno_diag_edges'] / (visibility_stats['visible_phenotypes'] * visibility_stats['visible_diagnostics']):.4f}" if visibility_stats['visible_phenotypes'] > 0 and visibility_stats['visible_diagnostics'] > 0 else "N/A")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Performance statistics
                st.markdown("<div class='stats-container'>", unsafe_allow_html=True)
                st.subheader("Performance Statistics")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Graph Generation Time", f"{elapsed_time:.2f} seconds")
                with col2:
                    st.metric("Nodes per Second", f"{(len(genes) + len(phenotypes) + len(diagnostics)) / elapsed_time:.2f}")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading knowledge graph: {str(e)}")
        st.write("Please check that the backend modules are correctly configured and all dependencies are installed.")
        st.code("""
        # Make sure these packages are installed:
        pip install streamlit plotly networkx owlready2 pandas numpy matplotlib
        """)