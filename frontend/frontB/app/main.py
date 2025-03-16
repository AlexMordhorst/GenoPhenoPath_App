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
from typing import Any, Dict, List, Tuple

from frontend.frontA.stages.layout import configure_page_settings, apply_custom_css, create_layout_containers
from frontend.frontA.session.state import initialize_graph_statistics, initialize_ui_state
from frontend.frontA.animations.dna_helix import generate_animation_frames, display_dna_animation
from frontend.frontB.interactions.controls import create_sidebar_controls
from frontend.frontB.display.chart import update_visualization

def load_knowledge_graph():
    """
    Load the knowledge graph from the backend controller.
    
    This function calls the backend controller to create the knowledge graph,
    get the visualization, and retrieve node and edge data.
    
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
        
        # Call the function to get all necessary data
        fig, community_0, community_1, community_2, spring_3D, G, graph_stats = create_knowledge_graph()
        
        # Log performance info
        elapsed_time = time.time() - start_time
        
        return fig, community_0, community_1, community_2, spring_3D, G, graph_stats, elapsed_time
    except Exception as e:
        raise e

def load_data_with_animation(animation_placeholder: Any):
    """
    Load the knowledge graph data with an animation displayed during loading.
    
    Args:
        animation_placeholder: Streamlit container for the animation
        
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
        # Call the non-cached function
        result[0] = load_knowledge_graph()
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

def run_app():
    """
    Run the main GenoPhenoPath application.
    
    This function orchestrates the entire application flow:
    1. Configure page settings and styling
    2. Initialize session state
    3. Set up layout containers
    4. Load data with animation
    5. Create sidebar controls
    6. Update and display visualization
    
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
        
        # Set up layout containers
        dropdown_container, animation_placeholder = create_layout_containers()
        
        # Load data with animation
        fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, elapsed_time, animation_frames = (
            load_data_with_animation(animation_placeholder)
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