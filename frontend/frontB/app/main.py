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

def load_knowledge_graph(selected_genes=None, force_refresh=False):
    """
    Load the knowledge graph from the backend controller.
    
    This function calls the backend controller to create the knowledge graph,
    get the visualization, and retrieve node and edge data.
    
    Args:
        selected_genes: Optional list of gene symbols to filter the graph
        force_refresh: If True, forces a complete rebuild of the graph and visualization
    
    Returns:
        Tuple containing:
        - Plotly Figure
        - List of gene names
        - List of phenotype names
        - List of diagnostic names
        - Dictionary of 3D positions
        - NetworkX graph
        - Dictionary of graph statistics
        - Empty list (subgraphs generated on-demand)
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
        print(f"DEBUG - Force refresh: {force_refresh}")
        fig, community_0, community_1, community_2, spring_3D, G, graph_stats = create_knowledge_graph(
            selected_genes, 
            force_refresh=force_refresh
        )
        
        # Log performance info
        elapsed_time = time.time() - start_time
        
        # Return with empty subgraphs list (will be generated on-demand)
        return fig, community_0, community_1, community_2, spring_3D, G, graph_stats, [], elapsed_time
    except Exception as e:
        raise e

def load_data_with_animation(animation_placeholder: Any, selected_genes=None, force_refresh=False):
    """
    Load the knowledge graph data (animation removed).
    
    Args:
        animation_placeholder: Streamlit container (kept for backward compatibility)
        selected_genes: Optional list of gene symbols to filter the graph
        force_refresh: If True, forces a complete rebuild of the graph and visualization
        
    Returns:
        Tuple containing:
        - Plotly Figure
        - List of gene names
        - List of phenotype names
        - List of diagnostic names
        - Dictionary of 3D positions
        - NetworkX graph
        - Dictionary of graph statistics
        - Empty list (subgraphs generated on-demand)
        - Loading time (seconds)
        - Empty list (kept for backward compatibility)
        
    Used in:
    - frontend.frontB.app.main.run_app
    """
    # Display a simple loading spinner instead of the animation
    with st.spinner("Generating knowledge graph..."):
        # Call the function directly without animation or threading
        print(f"DEBUG - Selected genes in load_data_with_animation: {selected_genes if selected_genes else 'None'}")
        print(f"DEBUG - Force refresh in load_data_with_animation: {force_refresh}")
        result = load_knowledge_graph(selected_genes, force_refresh=force_refresh)
    
    # Get the result
    fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, subgraphs, elapsed_time = result
    
    # Show toast when loading completes
    st.toast(f"Graph loaded in {elapsed_time:.2f} seconds")
    
    # Return an empty list for frames to maintain backward compatibility
    frames = []
    
    return fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, subgraphs, elapsed_time, frames

def create_landing_page():
    """
    Create the landing page for gene selection.
    
    This function creates the UI for users to select genes through manual input
    and random selection, both always visible.
    
    Returns:
        List of selected gene symbols
    """
    
    st.write("Select genes to include in the knowledge graph.")
    
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
    
    # Create a container with consistent width for all controls
    with st.container():
        # Add custom CSS for consistent button and input width
        st.markdown("""
        <style>
        /* Make the number input similar width to buttons */
        [data-testid="stNumberInput"] {
            width: 100%;
        }
        
        /* Make all buttons full width */
        .stButton > button {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Number input for random genes - full width
        num_genes = st.number_input("Number of random genes:", 
                                  min_value=1, 
                                  max_value=total_genes, 
                                  value=5)
        
        # Generate button - placed below input, full width
        generate_clicked = st.button("Generate")
        
        if generate_clicked:
            # Set a flag to prevent double-clicking issues
            if 'generating_genes' in st.session_state and st.session_state.generating_genes:
                st.warning("Please wait for the current generation to finish.")
                return []  # Return early to prevent race conditions
                
            # Set flag to indicate we're generating
            st.session_state.generating_genes = True
            
            try:
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
                
                # We're done generating
                st.session_state.generating_genes = False
                
                # Add a small sleep to ensure database operations complete
                # This helps prevent the "UNIQUE constraint failed" error
                time.sleep(0.1)
                
                # Now it's safe to rerun
                st.rerun()
            except Exception as e:
                # Make sure we reset the flag if there's an error
                st.session_state.generating_genes = False
                st.error(f"Error generating genes: {str(e)}")
                raise e
    
    # Validate genes with exact matching against the uppercase list
    valid_genes = [g for g in input_genes if g in set(unique_gene_list)]
    invalid_genes = [g for g in input_genes if g not in set(unique_gene_list) and g.strip()]
    
    if invalid_genes:
        st.warning(f"Invalid genes (will be dropped): {', '.join(invalid_genes)}")
    
    selected_genes = valid_genes
    
    # Check if we had genes before but now have none (all genes were deleted)
    # This is a different case from removing some genes but keeping others
    if not selected_genes and st.session_state.has_generated_graph:
        previous_genes = set(st.session_state.previous_gene_selection)
        if previous_genes:  # We had genes before, but now have none
            print(f"DEBUG - All genes were removed. Previous: {len(previous_genes)}, Current: 0")
            # Clear the ontology
            from backend.backA.ontology.schema import clear_ontology
            clear_ontology()

            # Clear gene data from the database
            from backend.backA.data_storage.value_manager import clear_gene_data
            clear_gene_data(list(previous_genes))

            # Reset graph-related state
            st.session_state.selected_genes = []
            st.session_state.has_generated_graph = False
            st.session_state.graph_data = None
            st.session_state.needs_graph_update = False
            st.session_state.previous_gene_selection = []

            st.success("Gene selection cleared. Graph has been reset.")
            # No need to rerun here - the empty state will be handled correctly

    # Show selected genes if any
    if selected_genes:
        st.write(f"Selected genes ({len(selected_genes)}):")
        st.write(", ".join(selected_genes))

        # Store selected genes in session state to ensure they're used for graph building
        # Check if the selection has changed
        if set(selected_genes) != set(st.session_state.previous_gene_selection):
            # Check if any genes were deleted, regardless of whether new ones were added
            previous_genes = set(st.session_state.previous_gene_selection)
            current_genes = set(selected_genes)
            removed_genes = previous_genes - current_genes

            if removed_genes:
                # If any genes were deleted, clear the ontology to ensure the graph is completely rebuilt
                print(f"DEBUG - Genes were deleted. Previous: {len(previous_genes)}, Current: {len(current_genes)}")
                print(f"DEBUG - Removed genes: {removed_genes}")
                print(f"DEBUG - Added genes: {current_genes - previous_genes}")
                from backend.backA.ontology.schema import clear_ontology
                clear_ontology()

            st.session_state.selected_genes = selected_genes
            st.session_state.needs_graph_update = True
            st.session_state.previous_gene_selection = selected_genes.copy()
        else:
            st.session_state.selected_genes = selected_genes
    
    # Add a reset button at the bottom of the landing page with consistent width
    with st.container():
        if st.button("Reset All"):
            with st.spinner("Resetting application..."):
                # Clear the ontology
                clear_ontology()

                # Clear data for the selected genes from the database
                from backend.backA.data_storage.value_manager import clear_gene_data
                clear_gene_data(st.session_state.selected_genes)

                # Reset all gene selection related state
                st.session_state.gene_input_text = ""
                st.session_state.selected_genes = []
                st.session_state.previous_gene_selection = []
                st.session_state.has_generated_graph = False
                st.session_state.needs_graph_update = False
                st.session_state.generating_genes = False

                # Also reset application state
                reset_application_state()
                st.success("Application has been reset.")
                st.rerun()
    
    return selected_genes

def create_phenotype_list_page(phenotypes):
    """
    Create a page that displays a list of all phenotypes in the knowledge graph and
    allows users to input clinical features observed in the patient.
    
    Args:
        phenotypes: List of phenotype IDs
    """
    
    if not phenotypes or len(phenotypes) == 0:
        st.info("No phenotypes available. Please add genes in the Gene Selection tab first.")
        return
    
    # Load unique phenotypes with names - we'll need this for both sections
    try:
        from backend.backA.data_processing.loader import load_unique_phenotypes
        from backend.backA.data_storage.value_manager import set_node_value
        unique_phenotypes_df = load_unique_phenotypes()
    except Exception as e:
        st.error(f"Error loading phenotype data: {e}")
        return
    
    # Initialize session state for clinical features if not present
    if 'clinical_features' not in st.session_state:
        st.session_state.clinical_features = []
    
    # Section 1: Clinical features observed in the patient
    st.header("Clinical features observed in the patient")
    
    # Create a container for the search input and results
    with st.container():
        # Search input
        phenotype_search = st.text_input(
            "Search for clinical features (HPO terms)",
            key="phenotype_search",
            help="Enter a clinical feature to find matching HPO terms"
        )
        
        # Only perform search if there is input
        if phenotype_search and len(phenotype_search) > 2:
            # Simple fuzzy matching based on substring
            # Convert search term and phenotype names to lowercase for case-insensitive matching
            search_lower = phenotype_search.lower()
            matches = unique_phenotypes_df[
                unique_phenotypes_df['hpo_name'].str.lower().str.contains(search_lower, na=False)
            ]
            
            # If matches found, show them in a container with buttons
            if not matches.empty and len(matches) > 0:
                st.write(f"Found {len(matches)} potential matches:")
                
                # Create a container to hold the matches with buttons
                for idx, row in matches.head(5).iterrows():  # Limit to top 5 matches for simplicity
                    col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
                    
                    with col1:
                        st.write(f"{row['hpo_id']}: {row['hpo_name']}")
                    
                    # Create buttons for classification
                    with col2:
                        if st.button(f"Present", key=f"present_{row['hpo_id']}"):
                            add_clinical_feature(row['hpo_id'], row['hpo_name'], "Present", set_node_value)
                            st.rerun()
                    
                    with col3:
                        if st.button(f"Uncertain", key=f"uncertain_{row['hpo_id']}"):
                            add_clinical_feature(row['hpo_id'], row['hpo_name'], "Uncertain", set_node_value)
                            st.rerun()
                    
                    with col4:
                        if st.button(f"Absent", key=f"absent_{row['hpo_id']}"):
                            add_clinical_feature(row['hpo_id'], row['hpo_name'], "Absent", set_node_value)
                            st.rerun()
            else:
                st.info(f"No matches found for '{phenotype_search}'")
    
    # Display selected clinical features
    if st.session_state.clinical_features and len(st.session_state.clinical_features) > 0:
        st.subheader("Selected clinical features")
        
        # Create a DataFrame to display
        clinical_df = pd.DataFrame(st.session_state.clinical_features)
        
        # Add a "Remove" button column
        clinical_df_with_index = clinical_df.reset_index()
        
        # Display the table
        st.dataframe(
            clinical_df[["HPO ID", "Phenotype Name", "Classification"]],
            use_container_width=True
        )
        
        # Add buttons for clearing features and updating visualization
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear all clinical features"):
                st.session_state.clinical_features = []
                st.rerun()
                
        with col2:
            if st.button("Update graph visualization"):
                # Set flag to refresh graph visualization
                st.session_state.needs_visualization_update = True
                st.success("Graph visualization will update when you switch to the Knowledge Graph tab.")
                time.sleep(1)
    
    # Section 2: Theoretical phenotypic features from sequencing
    st.header("Theoretical phenotypic features according to sequencing results")
    st.write(f"Total phenotypes: {len(phenotypes)}")
    
    # Create a display DataFrame with IDs, names, and current values for theoretical features
    try:
        from backend.backA.data_storage.database import get_node_value
        from backend.backA.data_storage.value_manager import set_node_value as db_set_node_value
        
        display_data = []
        for phen_id in sorted(phenotypes):
            name = "Unknown"
            matches = unique_phenotypes_df[unique_phenotypes_df['hpo_id'] == phen_id]
            if not matches.empty:
                name = matches.iloc[0]['hpo_name']
            
            # Get current value from database
            try:
                value = get_node_value(phen_id, 'phenotype')
                # Convert value to a descriptive status
                if value >= 0.8:
                    status = "Present"
                elif value <= 0.2:
                    status = "Absent"
                else:
                    status = "Uncertain"
            except Exception as val_error:
                print(f"Error getting value for {phen_id}: {val_error}")
                value = 0.5
                status = "Unknown"
                
            display_data.append({
                "HPO ID": phen_id, 
                "Phenotype Name": name,
                "Value": f"{value:.2f}",
                "Status": status
            })
        
        df = pd.DataFrame(display_data)
    except Exception as e:
        # Fallback to just showing the IDs if there's an issue with the enhanced display
        print(f"Error loading phenotype names: {e}")
        df = pd.DataFrame({"HPO ID": sorted(phenotypes)})
    
    st.dataframe(df, use_container_width=True)
    
    # Add debugging controls to directly set values for troubleshooting
    with st.expander("Advanced: Direct Value Control"):
        st.warning("This is a debugging tool to directly set node values and test visualization updates.")
        
        # Input for phenotype ID
        phen_id = st.text_input("Phenotype ID (e.g., HP:0000252)")
        
        # Value selection
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Set to Present (1.0)"):
                if phen_id:
                    db_set_node_value(phen_id, 'phenotype', 1.0)
                    st.success(f"Set {phen_id} to Present (1.0)")
                    st.session_state.needs_visualization_update = True
        
        with col2:
            if st.button("Set to Uncertain (0.5)"):
                if phen_id:
                    db_set_node_value(phen_id, 'phenotype', 0.5)
                    st.success(f"Set {phen_id} to Uncertain (0.5)")
                    st.session_state.needs_visualization_update = True
        
        with col3:
            if st.button("Set to Absent (0.0)"):
                if phen_id:
                    db_set_node_value(phen_id, 'phenotype', 0.0)
                    st.success(f"Set {phen_id} to Absent (0.0)")
                    st.session_state.needs_visualization_update = True
        
        if st.button("Force Graph Rebuild"):
            st.session_state.needs_visualization_update = True
            st.success("Graph will be rebuilt when you switch to the Knowledge Graph tab.")
            st.info("After switching to the Knowledge Graph tab, wait for the graph to update, then refresh the page to see the changes.")
            time.sleep(1)

def add_clinical_feature(hpo_id, hpo_name, classification, set_node_value_func):
    """
    Add a clinical feature to the session state and update the node value in the database.
    
    Args:
        hpo_id: The HPO ID of the feature
        hpo_name: The name of the feature
        classification: The classification (Present, Uncertain, Absent)
        set_node_value_func: Function to set node value in the database
    """
    # Check if the feature already exists
    for feature in st.session_state.clinical_features:
        if feature["HPO ID"] == hpo_id:
            # Update the existing feature
            feature["Classification"] = classification
            
            # Update the node value
            update_node_value(hpo_id, classification, set_node_value_func)
            return
    
    # Add new feature
    st.session_state.clinical_features.append({
        "HPO ID": hpo_id,
        "Phenotype Name": hpo_name,
        "Classification": classification
    })
    
    # Update the node value
    update_node_value(hpo_id, classification, set_node_value_func)

def update_node_value(hpo_id, classification, set_node_value_func):
    """
    Update the node value in the database based on the classification.
    
    Args:
        hpo_id: The HPO ID of the feature
        classification: The classification (Present, Uncertain, Absent)
        set_node_value_func: Function to set node value in the database
    """
    # Set value based on classification
    if classification == "Present":
        value = 1.0
    elif classification == "Uncertain":
        value = 0.5
    elif classification == "Absent":
        value = 0.0
    else:
        value = 0.5  # Default
    
    # Update the node value in the database
    set_node_value_func(hpo_id, 'phenotype', value)
    
    # Debug output to verify the value was set
    from backend.backA.data_storage.database import get_node_value
    from backend.backA.data_storage.value_manager import create_opacity_buckets, get_bucket_for_value
    
    actual_value = get_node_value(hpo_id, 'phenotype')
    
    # Test bucketing for this node
    buckets = create_opacity_buckets(5)  # Same as in visualization
    bucket_idx = get_bucket_for_value(actual_value, buckets)
    
    print(f"DEBUG - Updated node value for {hpo_id}: classification={classification}, value={value}, stored={actual_value}")
    print(f"DEBUG - Node will appear in bucket {bucket_idx} with range {buckets[bucket_idx]}")
    
    # Set a flag to indicate that the graph needs to be updated
    # This will trigger a refresh of the visualization when the user switches tabs
    if 'needs_visualization_update' not in st.session_state:
        st.session_state.needs_visualization_update = True
    else:
        st.session_state.needs_visualization_update = True

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
        # Add session management to ensure we have a clean slate on page reload
        # Session state needs to be initialized with a session ID to detect refreshes

        # Generate a session ID if not present
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())

            # This indicates a new session or page reload
            # We need to clear existing selections and data
            print("New session detected, clearing previous selections")

            # Clear any previous gene selections
            st.session_state.gene_input_text = ""
            st.session_state.selected_genes = []
            st.session_state.previous_gene_selection = []
            st.session_state.has_generated_graph = False
            st.session_state.needs_graph_update = False

            # Reset the ontology to be safe
            from backend.backA.ontology.schema import clear_ontology
            clear_ontology()

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
        if 'generating_genes' not in st.session_state:
            st.session_state.generating_genes = False
            
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
                # Load data and generate the graph with the current selection
                # The placeholder is no longer used for animation but kept for API compatibility
                animation_placeholder = st.empty()

                # Check if we're rebuilding with any genes removed from the previous graph
                if (st.session_state.has_generated_graph and 'graph_data' in st.session_state):
                    previous_graph_genes = set(st.session_state.graph_data[1])  # Index 1 contains genes
                    current_genes = set(selected_genes)
                    removed_genes = previous_graph_genes - current_genes

                    if removed_genes:
                        # If any genes were removed, clear the graph data to ensure complete rebuild
                        print(f"DEBUG - Graph rebuild with removed genes:")
                        print(f"DEBUG - Current genes: {len(current_genes)}, Previous graph genes: {len(previous_graph_genes)}")
                        print(f"DEBUG - Removed genes: {removed_genes}")
                        print(f"DEBUG - Added genes: {current_genes - previous_graph_genes}")

                        from backend.backA.ontology.schema import clear_ontology
                        clear_ontology()
                        st.session_state.graph_data = None
                        print("DEBUG - Ontology cleared and graph_data reset to None")

                # Generate the graph with the current selection
                graph_data = load_data_with_animation(animation_placeholder, selected_genes, force_refresh=False)
                st.session_state.graph_data = graph_data
                st.session_state.has_generated_graph = True
                # Reset the update flag
                st.session_state.needs_graph_update = False
                # Initialize subgraph index
                st.session_state.current_subgraph_index = -1  # -1 means no subgraph (showing full graph)

                st.success("Knowledge graph generated. You can now navigate to the Knowledge Graph and Phenotypes tabs.")
                # This rerun is needed but only done once after graph generation
                st.rerun()  # Rerun to reflect the changes in tab state
        
        # Knowledge Graph Tab
        with graph_tab:
            if not has_genes:
                st.info("Please select genes in the Gene Selection tab first.")
                # Make sure we reset graph_data when there are no genes
                # This is a failsafe in case has_generated_graph wasn't properly reset
                if st.session_state.graph_data is not None:
                    st.session_state.graph_data = None
                    st.session_state.has_generated_graph = False
            elif not st.session_state.has_generated_graph:
                st.info("Please wait while the knowledge graph is being generated...")
            else:
                # Create animation placeholder
                animation_placeholder = st.empty()

                # Double-check to make sure graph_data exists
                if st.session_state.graph_data is None:
                    st.error("Graph data is missing. Please return to the Gene Selection tab and regenerate the graph.")
                    st.session_state.has_generated_graph = False
                else:
                    # Retrieve graph data from session state
                    (fig, genes, phenotypes, diagnostics, layout_3d, graph,
                     graph_stats, subgraphs, elapsed_time, animation_frames) = st.session_state.graph_data

                    # Check if we need to update the visualization due to node value changes
                    if 'needs_visualization_update' in st.session_state and st.session_state.needs_visualization_update:
                        # Reload the graph with existing gene selection
                        st.session_state.needs_visualization_update = False
                        print("DEBUG - Updating visualization due to node value changes")
                        with st.spinner("Updating graph visualization..."):
                            # Re-fetch data from nodes with updated values, forcing a complete refresh
                            print("DEBUG - About to refresh graph with force_refresh=True")
                            result = load_data_with_animation(animation_placeholder, st.session_state.selected_genes, force_refresh=True)
                            st.session_state.graph_data = result

                        # After updating graph data, get the new values
                        (fig, genes, phenotypes, diagnostics, layout_3d, graph,
                        graph_stats, subgraphs, elapsed_time, _) = st.session_state.graph_data
                        st.success("Graph visualization updated with new clinical feature values.")
                
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
                        "edge_limit": 1000,
                        "search_term": ""
                        # Removed opacity controls as they're now controlled by the database
                    }
                
                # Use the controls from session state
                controls = st.session_state.controls
                
                # Display visualization directly at the top level with full height
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
        
        # Phenotypes Tab
        with phenotypes_tab:
            if not has_genes:
                st.info("Please select genes in the Gene Selection tab first.")
                # Make sure we reset graph_data when there are no genes
                # This is a failsafe in case has_generated_graph wasn't properly reset
                if st.session_state.graph_data is not None:
                    st.session_state.graph_data = None
                    st.session_state.has_generated_graph = False
            elif not st.session_state.has_generated_graph:
                st.info("Please wait while the knowledge graph is being generated...")
            else:
                # Double-check to make sure graph_data exists
                if st.session_state.graph_data is None:
                    st.error("Graph data is missing. Please return to the Gene Selection tab and regenerate the graph.")
                    st.session_state.has_generated_graph = False
                else:
                    # Extract phenotypes from the graph data
                    phenotypes = st.session_state.graph_data[2]  # Index 2 contains phenotypes
                    create_phenotype_list_page(phenotypes)
                
        # Statistics Tab
        with stats_tab:
            if not has_genes:
                st.info("Please select genes in the Gene Selection tab first.")
                # Make sure we reset graph_data when there are no genes
                # This is a failsafe in case has_generated_graph wasn't properly reset
                if st.session_state.graph_data is not None:
                    st.session_state.graph_data = None
                    st.session_state.has_generated_graph = False
            elif not st.session_state.has_generated_graph:
                st.info("Please wait while the knowledge graph is being generated...")
            else:
                # Double-check to make sure graph_data exists
                if st.session_state.graph_data is None:
                    st.error("Graph data is missing. Please return to the Gene Selection tab and regenerate the graph.")
                    st.session_state.has_generated_graph = False
                else:
                    # Retrieve graph data from session state
                    (fig, genes, phenotypes, diagnostics, layout_3d, graph,
                     graph_stats, subgraphs, elapsed_time, animation_frames) = st.session_state.graph_data
                
                
                
                # Calculate statistics based on current control settings
                from frontend.frontB.display.chart import calculate_visibility_stats
                
                visibility_stats = calculate_visibility_stats(
                    st.session_state.controls, genes, phenotypes, diagnostics, graph_stats
                )
                
                # Display the statistics in sections separated by horizontal rules
                
                # Node statistics
                
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
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Displayed Nodes", visibility_stats["displayed_nodes"])
                with col2:
                    st.metric("Total Available Nodes", len(genes) + len(phenotypes) + len(diagnostics))
                with col3:
                    # Empty third column for alignment with the row above
                    st.empty()
                
                # Add a horizontal rule to separate sections
                st.markdown("<hr>", unsafe_allow_html=True)
                
                # Edge statistics
                st.subheader("Edge Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Gene-Phenotype Edges", visibility_stats["visible_gene_pheno_edges"])
                with col2:
                    st.metric("Phenotype-Diagnostic Edges", visibility_stats["visible_pheno_diag_edges"])
                with col3:
                    st.metric("Total Edges", visibility_stats["displayed_edges"])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Gene-Phenotype Density", f"{visibility_stats['visible_gene_pheno_edges'] / (visibility_stats['visible_genes'] * visibility_stats['visible_phenotypes']):.4f}" if visibility_stats['visible_genes'] > 0 and visibility_stats['visible_phenotypes'] > 0 else "N/A")
                with col2:
                    st.metric("Phenotype-Diagnostic Density", f"{visibility_stats['visible_pheno_diag_edges'] / (visibility_stats['visible_phenotypes'] * visibility_stats['visible_diagnostics']):.4f}" if visibility_stats['visible_phenotypes'] > 0 and visibility_stats['visible_diagnostics'] > 0 else "N/A")
                with col3:
                    # Empty third column for alignment
                    st.empty()
                
                # Add a horizontal rule to separate sections
                st.markdown("<hr>", unsafe_allow_html=True)
                
                # Performance statistics
                st.subheader("Performance Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Graph Generation Time", f"{elapsed_time:.2f} seconds")
                with col2:
                    st.metric("Nodes per Second", f"{(len(genes) + len(phenotypes) + len(diagnostics)) / elapsed_time:.2f}")
                with col3:
                    # Empty third column for alignment
                    st.empty()
                # End of statistics sections
        
    except Exception as e:
        st.error(f"Error loading knowledge graph: {str(e)}")
        st.write("Please check that the backend modules are correctly configured and all dependencies are installed.")
        st.code("""
        # Make sure these packages are installed:
        pip install streamlit plotly networkx owlready2 pandas numpy matplotlib
        """)