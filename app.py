import streamlit as st
import plotly.graph_objects as go
import sys
import os

# Set page config to make the app wider with dark mode
st.set_page_config(
    page_title="GenoPhenoPath 3D Knowledge Graph",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom CSS for dark spacey theme
st.markdown("""
<style>
    /* Pure black background */
    .stApp {
        background: #000000;
    }
    
    /* Title styling */
    h1 {
        color: #8be9fd !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 10px rgba(139, 233, 253, 0.7);
    }
    
    /* Make text and labels more visible on dark background */
    p, .stMarkdown, .css-10trblm, .css-1yeedl6 {
        color: #f8f8f2 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid rgba(139, 233, 253, 0.2);
    }
    
    /* Button styling */
    .stButton button {
        background-color: #483d8b !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #272733 !important;
        color: #8be9fd !important;
        border-radius: 4px !important;
    }
    
    /* Slider styling */
    .stSlider div[data-baseweb="slider"] div {
        background-color: #483d8b !important;
    }
    
    /* Make metric labels more visible */
    [data-testid="stMetricLabel"] {
        color: #f8f8f2 !important;
    }
    
    /* Make metric values more visible */
    [data-testid="stMetricValue"] {
        color: #8be9fd !important;
        font-size: 1.4rem !important;
    }
    
    /* Info box styling */
    .stAlert {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(139, 233, 253, 0.2) !important;
    }
    
    /* Make plotly background match app background */
    .js-plotly-plot, .plotly, .plot-container {
        background: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Create title with cosmic effect
st.markdown("""
<div style='text-align: center;'>
    <h1>🧬 GenoPhenoPath 3D Knowledge Graph 🧬</h1>
    <p style='font-size: 1.2rem; color: #bd93f9 !important; margin-top: -10px;'>
        Exploring the connections between genes, phenotypes, and diagnostics in 3D space
    </p>
</div>
""", unsafe_allow_html=True)

# Description will be moved below the plotly figure

# Create sidebar with dropdown sections for easier navigation
with st.sidebar:
    st.header("GenoPhenoPath Controls")
    
    # Main visibility section - always visible for quick toggling
    st.write("##### Quick Display Controls")
    col1, col2, col3 = st.columns(3)
    with col1:
        show_genes = st.checkbox("Genes", value=True)
    with col2:
        show_phenotypes = st.checkbox("Phenotypes", value=True)
    with col3:
        show_diagnostics = st.checkbox("Diagnostics", value=True)
    
    # Search - always visible at the top level
    search_term = st.text_input("🔍 Search for a node")
    
    # Gene settings in a collapsible section
    with st.expander("Gene Settings 🧬", expanded=False):
        gene_size = st.slider("Size", min_value=1, max_value=20, value=10)
        gene_opacity = st.slider("Opacity", min_value=0.1, max_value=1.0, value=0.9, step=0.1)
        show_gene_pheno_edges = st.checkbox("Show connections to phenotypes", value=True)
        gene_pheno_opacity = st.slider("Connection opacity", min_value=0.1, max_value=1.0, value=0.4, step=0.1)
    
    # Phenotype settings in a collapsible section
    with st.expander("Phenotype Settings 🔶", expanded=False):
        phenotype_size = st.slider("Size", min_value=1, max_value=10, value=3)
        phenotype_opacity = st.slider("Opacity", min_value=0.1, max_value=1.0, value=0.2, step=0.1)
        show_pheno_diag_edges = st.checkbox("Show connections to diagnostics", value=True)
        pheno_diag_opacity = st.slider("Connection opacity", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
    
    # Diagnostic measures settings in a collapsible section
    with st.expander("Diagnostic Settings 🔬", expanded=False):
        diagnostic_size = st.slider("Size", min_value=1, max_value=15, value=8)
        diagnostic_opacity = st.slider("Opacity", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
    
    # Advanced settings in a collapsible section
    with st.expander("Advanced Settings ⚙️", expanded=False):
        st.write("##### Rendering Controls")
        # Add a button to regenerate the graph
        if st.button("Regenerate Graph"):
            st.cache_data.clear()
        
        # Add a button to download current view
        if st.button("Download Current View"):
            st.info("Click the camera icon in the graph toolbar to save the current view")
        
        # Performance settings
        st.write("##### Performance Settings")
        st.write("Use these settings if the graph is slow to load")
        st.select_slider(
            "Edge Limit",
            options=[100, 250, 500, 750, 1000, "No Limit"],
            value=1000,
            key="edge_limit",
            help="Limit the number of edges to improve performance"
        )
    
    # Add attribution at the bottom
    st.markdown("---")
    st.caption("GenoPhenoPath by [Niklas Winnewisser](https://github.com/niklaswinner)")
    st.caption("Built with Streamlit & Plotly")

# Function to load the knowledge graph from prototype.py - removed st.cache_data
def load_knowledge_graph():
    try:
        import time
        start_time = time.time()
        
        # Import the function directly from the prototype module
        from prototype import create_knowledge_graph
        
        # Call the function to get all necessary data
        fig, community_0, community_1, community_2, spring_3D, G, graph_stats = create_knowledge_graph()
        
        # Log performance info
        elapsed_time = time.time() - start_time
        
        return fig, community_0, community_1, community_2, spring_3D, G, graph_stats, elapsed_time
    except Exception as e:
        raise e

# Try to load the graph data
try:
    # Create DNA animation frames
    dna_frames = [
        """
        ```
          A------T
         /        \\
        G          C
       |            |
       |            |
        G          C
         \\        /
          T------A
        ```
        """,
        """
        ```
         A--------T
         /        \\
        |          |
        G          C
        |          |
         \\        /
          T------A
        ```
        """,
        """
        ```
           A---T
          /     \\
         /       \\
        G         C
        |         |
        |         |
         \\       /
          T-----A
        ```
        """,
        """
        ```
              A
            /   \\
           /     \\
          G       T
         /|       |\\
        | |       | |
        | |       | |
         \\|       |/
          C       A
           \\     /
            \\   /
              G
        ```
        """,
        """
        ```
              T
             / \\
            C   A
           /|   |\\
          / |   | \\
          | |   | |
          \\ |   | /
           \\|   |/
            G   T
             \\ /
              A
        ```
        """,
        """
        ```
           T---A
          /     \\
         /       \\
        C         G
        |         |
        |         |
         \\       /
          A-----T
        ```
        """,
        """
        ```
         T--------A
         /        \\
        |          |
        C          G
        |          |
         \\        /
          A------T
        ```
        """,
        """
        ```
          T------A
         /        \\
        C          G
       |            |
       |            |
        C          G
         \\        /
          A------T
        ```
        """
    ]
    
    # Show DNA animation while loading
    with st.spinner(""):
        # Create a placeholder for the DNA animation
        dna_placeholder = st.empty()
        
        # Start loading in background
        import threading
        import time
        
        result = [None]  # Use a list to store the result since nonlocal isn't available
        loading_complete = [False]  # Flag to indicate when loading is complete
        
        def load_data():
            # Call the non-cached function
            result[0] = load_knowledge_graph()
            loading_complete[0] = True
        
        # Start the loading in a separate thread
        loading_thread = threading.Thread(target=load_data)
        loading_thread.start()
        
        # Display rotating DNA animation while loading
        frame_index = 0
        while not loading_complete[0]:
            # Display current frame with a centered DNA loading message
            dna_placeholder.markdown(f"""
            <div style="text-align: center;">
                <p style="color: #8be9fd; font-size: 1.5rem; margin-bottom: 10px;">Building Knowledge Graph</p>
                <div style="font-family: monospace; color: #50fa7b;">
                {dna_frames[frame_index]}
                </div>
                <p style="color: #f8f8f2;">Mapping genes, phenotypes, and diagnostic pathways...</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Move to next frame
            frame_index = (frame_index + 1) % len(dna_frames)
            time.sleep(0.2)  # Control animation speed
        
        # Clear the animation when loading is complete
        dna_placeholder.empty()
        
        # Unpack the result
        fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, elapsed_time = result[0]
        
    # Show toast after function completes (outside the cached function)
    st.toast(f"Graph loaded in {elapsed_time:.2f} seconds")
    
    # Display graph statistics
    # First row: node counts
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Genes", len(genes))
    with col2:
        st.metric("Phenotypes", len(phenotypes))
    with col3:
        st.metric("Diagnostic Measures", len(diagnostics))
    
    # Second row: edge counts
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gene-Phenotype Edges", graph_stats["gene_to_pheno_edges"])
    with col2:
        st.metric("Phenotype-Diagnostic Edges", graph_stats["pheno_to_diag_edges"])
    with col3:
        st.metric("Total Edges", graph_stats["total_edges"])
    
    # If search term is provided, highlight the matching nodes
    if search_term:
        # Create a list to hold nodes that match the search term
        matching_nodes = []
        
        # Check for matches in genes
        matching_genes = [gene for gene in genes if search_term.lower() in gene.lower()]
        if matching_genes:
            st.write(f"Found matching genes: {', '.join(matching_genes)}")
            matching_nodes.extend(matching_genes)
        
        # Check for matches in phenotypes
        matching_phenotypes = [phen for phen in phenotypes if search_term.lower() in phen.lower()]
        if matching_phenotypes:
            st.write(f"Found matching phenotypes: {', '.join(matching_phenotypes)}")
            matching_nodes.extend(matching_phenotypes)
        
        # Check for matches in diagnostics
        matching_diagnostics = [diag for diag in diagnostics if search_term.lower() in diag.lower()]
        if matching_diagnostics:
            st.write(f"Found matching diagnostic measures: {', '.join(matching_diagnostics)}")
            matching_nodes.extend(matching_diagnostics)
        
        if not matching_nodes:
            st.warning(f"No nodes found matching '{search_term}'")
    
    # Customize the figure based on user settings - with error handling for data structure
    try:
        fig_data = list(fig.data)
        
        # New trace order:
        # 0: Gene-phenotype edges (trace_edges_gene_pheno)
        # 1: Phenotype-diagnostic edges (trace_edges_pheno_diag)
        # 2: Gene nodes (trace_nodes_gene)
        # 3: Phenotype nodes (trace_nodes_phenotype)
        # 4: Diagnostic nodes (trace_nodes_diagnostic)
        
        # Update gene-phenotype edge visibility and opacity (index 0)
        if not show_gene_pheno_edges or not (show_genes and show_phenotypes):
            # Hide edges completely
            fig_data[0].opacity = 0
            fig_data[0].visible = "legendonly"
        else:
            fig_data[0].opacity = gene_pheno_opacity
            fig_data[0].visible = True
        
        # Update phenotype-diagnostic edge visibility and opacity (index 1)
        if not show_pheno_diag_edges or not (show_phenotypes and show_diagnostics):
            # Hide edges completely
            fig_data[1].opacity = 0
            fig_data[1].visible = "legendonly"
        else:
            fig_data[1].opacity = pheno_diag_opacity
            fig_data[1].visible = True
            
        # Update gene nodes (index 2)
        if not show_genes:
            # Hide gene nodes completely including hover text
            fig_data[2].opacity = 0
            fig_data[2].hoverinfo = "skip"
            fig_data[2].showlegend = False
            fig_data[2].visible = "legendonly"
        else:
            fig_data[2].marker.size = gene_size
            fig_data[2].opacity = gene_opacity
            fig_data[2].hoverinfo = "text"
            fig_data[2].visible = True
        
        # Update phenotype nodes (index 3)
        if not show_phenotypes:
            # Hide phenotype nodes completely including hover text
            fig_data[3].opacity = 0
            fig_data[3].hoverinfo = "skip"
            fig_data[3].showlegend = False
            fig_data[3].visible = "legendonly"
        else:
            fig_data[3].marker.size = phenotype_size
            fig_data[3].opacity = phenotype_opacity
            fig_data[3].hoverinfo = "text"
            fig_data[3].visible = True
            
        # Update diagnostic nodes (index 4)
        if not show_diagnostics:
            # Hide diagnostic nodes completely including hover text
            fig_data[4].opacity = 0
            fig_data[4].hoverinfo = "skip"
            fig_data[4].showlegend = False
            fig_data[4].visible = "legendonly"
        else:
            fig_data[4].marker.size = diagnostic_size
            fig_data[4].opacity = diagnostic_opacity
            fig_data[4].hoverinfo = "text"
            fig_data[4].visible = True
        
        # Create a new figure with the updated data
        updated_fig = go.Figure(data=fig_data, layout=fig.layout)
        
        # Set the figure height to fill most of the screen and hide the legend
        updated_fig.update_layout(
            height=800,
            showlegend=False,
            paper_bgcolor="black",
            plot_bgcolor="black"
        )
        
        # Always hide ticks and axis labels
        show_ticks = False
        
        # Update scene settings based on visibility
        updated_fig.update_layout(
            scene=dict(
                xaxis=dict(
                    showticklabels=show_ticks,
                    showspikes=show_ticks,
                    showgrid=show_ticks,
                    showline=show_ticks,
                    zeroline=show_ticks,
                    backgroundcolor="black"
                ),
                yaxis=dict(
                    showticklabels=show_ticks,
                    showspikes=show_ticks,
                    showgrid=show_ticks,
                    showline=show_ticks,
                    zeroline=show_ticks,
                    backgroundcolor="black"
                ),
                zaxis=dict(
                    showticklabels=show_ticks,
                    showspikes=show_ticks,
                    showgrid=show_ticks,
                    showline=show_ticks,
                    zeroline=show_ticks,
                    backgroundcolor="black"
                ),
                bgcolor="black"
            )
        )
        
        # Calculate number of displayed nodes and edges
        displayed_nodes = 0
        if show_genes:
            displayed_nodes += len(genes)
        if show_phenotypes:
            displayed_nodes += len(phenotypes)
        if show_diagnostics:
            displayed_nodes += len(diagnostics)
            
        displayed_edges = 0
        if show_gene_pheno_edges and show_genes and show_phenotypes:
            displayed_edges += graph_stats["gene_to_pheno_edges"]
        if show_pheno_diag_edges and show_phenotypes and show_diagnostics:
            displayed_edges += graph_stats["pheno_to_diag_edges"]
            
        # Display filtering info
        st.info(f"Displaying {displayed_nodes}/{graph_stats['total_nodes']} nodes " + 
                f"({(displayed_nodes/graph_stats['total_nodes']*100):.1f}%) and " +
                f"{displayed_edges}/{graph_stats['total_edges']} edges " + 
                f"({(displayed_edges/graph_stats['total_edges']*100):.1f}%)")
        
        # Display the interactive 3D graph with a try-catch for memory issues
        try:
            st.plotly_chart(updated_fig, use_container_width=True)
            
            # Add the explanation text below the plotly figure
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
        except Exception as e:
            st.error(f"Error rendering graph: {str(e)}")
            st.warning("The graph may be too large to render. Try filtering nodes or reducing graph complexity.")
            
    except Exception as e:
        st.error(f"Error updating graph visualization: {str(e)}")
        # Fallback - try to show the original figure
        try:
            st.plotly_chart(fig, use_container_width=True)
            
            # Add the explanation text below the plotly figure
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
        except:
            st.error("Unable to display graph visualization. The dataset may be too large.")
    
    # Add some information about interaction
    st.info("""
    **Interaction Tips:**
    - **Rotate**: Click and drag to rotate the graph
    - **Zoom**: Scroll to zoom in/out
    - **Pan**: Right-click and drag to pan
    - **Hover**: Mouse over nodes to see their labels
    """)
    
except Exception as e:
    st.error(f"Error loading knowledge graph: {str(e)}")
    st.write("Please check that the prototype.py file is correctly configured and all dependencies are installed.")
    st.code("""
    # Make sure these packages are installed:
    pip install streamlit plotly networkx owlready2 pandas numpy matplotlib
    """)