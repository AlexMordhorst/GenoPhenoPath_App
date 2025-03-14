import streamlit as st
import plotly.graph_objects as go
import sys
import os
import math
import time
import random

# Set page config to make the app wider with dark mode
st.set_page_config(
    page_title="GenoPhenoPath 3D Knowledge Graph",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# Add custom CSS for dark spacey theme
st.markdown("""
<style>
    /* Pure black background */
    .stApp {
        background: #000000;
    }
    
    /* Hide and remove the top header bar completely */
    header {
        display: none !important;
    }
    
    /* Target the main elements that create margins/padding */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: -39px !important;  /* 30% more negative margin to further reduce space */
    }
    
    /* Remove extra padding from the root container */
    .css-k1vhr4, .css-18e3th9, .css-1d391kg, 
    [data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
        margin-top: -20px !important;  /* 30% more negative margin */
    }
    
    /* Target the top toolbar area */
    [data-testid="stToolbar"] {
        display: none !important;
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
    
    /* Make sidebar headers stand out */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #8be9fd !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Style sidebar checkboxes */
    [data-testid="stSidebar"] [data-testid="stCheckbox"] {
        margin-bottom: 0.5rem !important;
    }
    
    /* Style sidebar sliders */
    [data-testid="stSidebar"] [data-testid="stSlider"] {
        margin-bottom: 1.2rem !important;
    }
    
    /* Improve spacing between sections */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        margin-bottom: 0.5rem !important;
    }
    
    /* Hide the sidebar toggle completely */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Position our custom dropdown bar at the very top */
    div[data-testid="stExpander"] {
        position: fixed !important;
        top: 0px !important;
        left: 10% !important;
        right: 0 !important;
        z-index: 9999 !important;
        width: 80% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Style the dropdown header itself */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: none !important;
        border-radius: 0 !important; /* Remove border radius for a menu bar look */
        color: #8be9fd !important;
        font-weight: 500 !important;
        margin: 0 !important;
        width: 100% !important;
        padding: 5px 10px !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Style the dropdown content */
    .streamlit-expanderContent {
        background-color: rgba(15, 20, 30, 0.8) !important;
        border-radius: 0 0 4px 4px !important;
        border: none !important;
        padding: 10px !important;
        margin: 0 !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    
    /* Remove additional outlines and borders that might appear */
    .streamlit-expanderHeader:focus, .streamlit-expanderHeader:hover,
    .streamlit-expanderContent:focus, .streamlit-expanderContent:hover {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Style the expander arrow */
    .streamlit-expanderHeader svg {
        color: #8be9fd !important;
        fill: #8be9fd !important;
    }
    
    /* Remove the white outline around the icon */
    .st-emotion-cache-1w5q6cr, .css-1w5q6cr {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Remove padding from the main content to eliminate space at the top */
    .main .block-container {
        padding-top: 0px !important;
        margin-top: -52px !important;  /* 30% more negative margin (from -40px to -52px) */
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
    
    /* Make metric values more visible and colorful */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: bold !important;
    }
    
    /* Colorize different metric types */
    /* First row - node counts */
    [data-testid="column"]:nth-child(1) [data-testid="stMetricValue"] {
        color: #8be9fd !important; /* Blue for genes */
    }
    [data-testid="column"]:nth-child(2) [data-testid="stMetricValue"] {
        color: #ffb86c !important; /* Orange for phenotypes */
    }
    [data-testid="column"]:nth-child(3) [data-testid="stMetricValue"] {
        color: #ff79c6 !important; /* Magenta for diagnostics */
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

# No title

# Declare variables in a container to store graph stats
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

# Create a container for the dropdown
dropdown_container = st.container()

# Create a placeholder for the DNA animation
animation_placeholder = st.empty()

# We'll generate the animation directly during loading

# We'll add the dropdown content after we load the graph data
# This ensures we can access the actual statistics

# No custom sidebar toggle

# Description will be moved below the plotly figure

# Create a simplified sidebar with better user experience
with st.sidebar:
    st.header("Display Controls")
    
    # Section for node visibility - clean and simple layout
    st.subheader("Show/Hide Nodes")
    
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
    
    # Simple checkboxes without complex callbacks
    show_genes = st.checkbox("Genes (blue)", value=True)
    show_phenotypes = st.checkbox("Phenotypes (orange)", value=True)
    show_diagnostics = st.checkbox("Diagnostic Measures (magenta)", value=True)
    
    # Section for connections
    st.subheader("Show/Hide Connections")
    
    show_gene_pheno_edges = st.checkbox("Gene-Phenotype Connections", value=True)
    show_pheno_diag_edges = st.checkbox("Phenotype-Diagnostic Connections", value=True)
    
    # Add a search option
    st.subheader("Search")
    search_term = st.text_input("🔍 Search for a node")
    
    # Size and appearance controls (simplified)
    st.subheader("Node Size")
    gene_size = st.slider("Gene Size", min_value=1, max_value=20, value=10)
    phenotype_size = st.slider("Phenotype Size", min_value=1, max_value=10, value=3)
    diagnostic_size = st.slider("Diagnostic Size", min_value=1, max_value=15, value=8)
    
    # Opacity controls
    st.subheader("Opacity")
    gene_opacity = st.slider("Gene Opacity", min_value=0.1, max_value=1.0, value=0.9, step=0.1)
    phenotype_opacity = st.slider("Phenotype Opacity", min_value=0.1, max_value=1.0, value=0.2, step=0.1)
    diagnostic_opacity = st.slider("Diagnostic Opacity", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
    gene_pheno_opacity = st.slider("Gene-Phenotype Connection Opacity", min_value=0.1, max_value=1.0, value=0.4, step=0.1)
    pheno_diag_opacity = st.slider("Phenotype-Diagnostic Connection Opacity", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
    
    # Performance control
    st.subheader("Performance")
    edge_limit = st.select_slider(
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

# Import the spinning.py script functionality
def render_dna_frame(frame_num, max_frames, width=70, height=30):
    """Generate a single frame of DNA helix animation"""
    # Configuration
    radius = 10
    helix_length = 25
    dna_chars = ['G', 'T', 'C', 'A']  # DNA nucleotide characters
    
    # Create an empty screen buffer
    screen = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Calculate the center of the screen
    center_x = width // 2
    center_y = height // 2
    
    # Draw the two helical strands
    for y_offset in range(-helix_length, helix_length + 1):
        # Calculate the y position
        y = center_y + y_offset
        
        # Skip if out of bounds
        if y < 0 or y >= height:
            continue
        
        # Calculate the phase for this position
        phase = y_offset / 4 + frame_num / max_frames
        
        # Determine which character to use based on position
        char_index = (y_offset + helix_length) % 4
        current_char = dna_chars[char_index]
        
        # Calculate x positions for the two strands (opposite sides of the helix)
        x1 = center_x + int(radius * math.sin(phase))
        x2 = center_x + int(radius * math.sin(phase + math.pi))
        
        # Place characters if in bounds
        if 0 <= x1 < width:
            screen[y][x1] = current_char
        if 0 <= x2 < width:
            # Use complementary base pair on opposite strand
            complementary_index = (char_index + 2) % 4
            screen[y][x2] = dna_chars[complementary_index]
            
        # Add connecting rungs between the strands (less frequently)
        if y % 4 == 0:
            # Calculate the beginning and end of the rung
            if x1 > x2:
                x1, x2 = x2, x1
            
            # Draw the rung
            for x in range(x1 + 1, x2):
                if 0 <= x < width:
                    # Use hyphen for the connecting rungs
                    screen[y][x] = '-'
    
    # Convert the 2D screen array to a string
    return '\n'.join(''.join(row) for row in screen)

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

    # Start loading in background
    import threading
    
    ##### 3D Plotly Figure: Load Fundamental Data  #####
    
    result = [None]  # Use a list to store the result since nonlocal isn't available
    loading_complete = [False]  # Flag to indicate when loading is complete
    
    def load_data():
        # Call the non-cached function
        result[0] = load_knowledge_graph()
        loading_complete[0] = True
    
    # Start the loading in a separate thread
    loading_thread = threading.Thread(target=load_data)
    loading_thread.start()
    max_dna_frames = 200
    # Show DNA animation while loading
    
    ##### Waiting Screen Animation  #####
    with st.spinner(""):
        # Generate frames for the DNA animation
        frames = [render_dna_frame(i,max_dna_frames) for i in range(max_dna_frames)]
        frame_index = 0
        
        # Create a placeholder for the DNA animation
        dna_placeholder = animation_placeholder
        
        # Display the spinning DNA animation while loading
        while not loading_complete[0]:
            dna_placeholder.markdown(f"""
            <div style="text-align: center; padding: 20px; background-color: rgba(0, 0, 0, 0.8); border-radius: 10px;">
                <div style="font-family: monospace; white-space: pre; color: #50fa7b; text-shadow: 0 0 5px rgba(80, 250, 123, 0.7);">
                {frames[frame_index]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Move to next frame
            frame_index = (frame_index + 1) % len(frames)
            time.sleep(0.01)  # Control animation speed
    
    # Clear the animation when done
    animation_placeholder.empty()
    
    # Unpack the result
    fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, elapsed_time = result[0]
        
    # Show toast after function completes (outside the cached function)
    st.toast(f"Graph loaded in {elapsed_time:.2f} seconds")
    
    # No metrics displayed here - only in the dropdown
    
    
    ##### Search for Terms if Activated #####
    
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
        
        ##### 3D Plotly Figure: Update Visibility based on Sliders #####
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
        
        ##### 3D Plotly Figure: Figure Size Update  #####
        
        # Set the figure dimensions to 63.65% of original and hide the legend
        # Calculate the reduction factor (0.6365 = 0.95 * 0.67)
        reduction_factor = 0.6365
        original_width = 1000
        original_height = 800
        
        updated_fig.update_layout(
            height=original_height * reduction_factor,
            width=original_width * reduction_factor,
            showlegend=False,
            paper_bgcolor="black",
            plot_bgcolor="black",
            margin=dict(t=0, l=0, r=0, b=0)  # Remove all margins around the plot
        )
        
        ##### 3D Plotly Figure: Coordinate System  #####
        
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
                bgcolor="black",
                # Apply zoom using the reduction factor
                camera=dict(
                    eye=dict(x=1.0 * reduction_factor, y=1.0 * reduction_factor, z=1.0 * reduction_factor)  # Reducing eye distance for more zoom
                )
            )
        )
        
        ##### Calculate Statistics #####
        
        # Calculate number of displayed nodes and edges
        displayed_nodes = 0
        visible_genes = 0
        visible_phenotypes = 0
        visible_diagnostics = 0
        
        if show_genes:
            visible_genes = len(genes)
            displayed_nodes += visible_genes
        if show_phenotypes:
            visible_phenotypes = len(phenotypes)
            displayed_nodes += visible_phenotypes
        if show_diagnostics:
            visible_diagnostics = len(diagnostics)
            displayed_nodes += visible_diagnostics
            
        displayed_edges = 0
        visible_gene_pheno_edges = 0
        visible_pheno_diag_edges = 0
        
        if show_gene_pheno_edges and show_genes and show_phenotypes:
            visible_gene_pheno_edges = graph_stats["gene_to_pheno_edges"]
            displayed_edges += visible_gene_pheno_edges
        if show_pheno_diag_edges and show_phenotypes and show_diagnostics:
            visible_pheno_diag_edges = graph_stats["pheno_to_diag_edges"]
            displayed_edges += visible_pheno_diag_edges
            
        # Store the total statistics in session_state
        st.session_state.graph_statistics = {
            'gene_count': len(genes),
            'phenotype_count': len(phenotypes),
            'diagnostic_count': len(diagnostics),
            'gene_pheno_edges': graph_stats["gene_to_pheno_edges"],
            'pheno_diag_edges': graph_stats["pheno_to_diag_edges"],
            'total_edges': graph_stats["total_edges"],
            'visible_genes': visible_genes,
            'visible_phenotypes': visible_phenotypes,
            'visible_diagnostics': visible_diagnostics,
            'visible_gene_pheno_edges': visible_gene_pheno_edges,
            'visible_pheno_diag_edges': visible_pheno_diag_edges,
            'visible_total_edges': displayed_edges
        }
            
        # No display filtering info
        
        # Check if any visualization settings changed
        if (show_genes != st.session_state.last_gene_state or
            show_phenotypes != st.session_state.last_phenotype_state or
            show_diagnostics != st.session_state.last_diagnostic_state or
            show_gene_pheno_edges != st.session_state.last_gene_pheno_edges_state or
            show_pheno_diag_edges != st.session_state.last_pheno_diag_edges_state):
            
            # Show DNA animation when settings change
            # Generate frames for the DNA animation
            frames = [render_dna_frame(i,max_dna_frames) for i in range(max_dna_frames)]
            frame_index = 0
            
            # Display the spinning DNA animation briefly
            for _ in range(5):  # Show 5 frames of animation
                animation_placeholder.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: rgba(0, 0, 0, 0.8); border-radius: 10px;">
                    <div style="font-family: monospace; white-space: pre; color: #50fa7b; text-shadow: 0 0 5px rgba(80, 250, 123, 0.7);">
                    {frames[frame_index]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Move to next frame
                frame_index = (frame_index + 1) % len(frames)
                time.sleep(0.1)  # Control animation speed
            
            # Update session state with current settings
            st.session_state.last_gene_state = show_genes
            st.session_state.last_phenotype_state = show_phenotypes
            st.session_state.last_diagnostic_state = show_diagnostics
            st.session_state.last_gene_pheno_edges_state = show_gene_pheno_edges
            st.session_state.last_pheno_diag_edges_state = show_pheno_diag_edges
                
        # Clear the animation placeholder
        animation_placeholder.empty()
        
        # Add custom styling to further reduce top space for plotly chart
        st.markdown("""
        <style>
            [data-testid="element-container"] {
                margin-top: -50px !important;
                padding-top: 0 !important;
            }
            iframe {
                margin-top: -30px !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
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
            
            # Now use the dropdown container to display statistics from our calculated values
            with dropdown_container:
                with st.expander("🧬 DNA Genopath - Statistics 🧬", expanded=False):
                    # Create columns for a nice layout of statistics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Genes", visible_genes, 
                                 delta=f"{visible_genes}/{len(genes)}" if visible_genes < len(genes) else None)
                    with col2:
                        st.metric("Phenotypes", visible_phenotypes,
                                 delta=f"{visible_phenotypes}/{len(phenotypes)}" if visible_phenotypes < len(phenotypes) else None)
                    with col3:
                        st.metric("Diagnostic Measures", visible_diagnostics,
                                 delta=f"{visible_diagnostics}/{len(diagnostics)}" if visible_diagnostics < len(diagnostics) else None)
                        
                    # Add a small vertical space
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Second row for edges
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Gene-Phenotype Edges", visible_gene_pheno_edges)
                    with col2:
                        st.metric("Phenotype-Diagnostic Edges", visible_pheno_diag_edges)
                    with col3:
                        st.metric("Total Edges", displayed_edges)
        except Exception as e:
            st.error(f"Error rendering graph: {str(e)}")
            st.warning("The graph may be too large to render. Try filtering nodes or reducing graph complexity.")
            
    except Exception as e:
        st.error(f"Error updating graph visualization: {str(e)}")
        # Fallback - try to show the original figure and hide animation
        try:
            # Hide the DNA animation
            st.markdown("""
            <script>
                if (typeof window.toggleDnaAnimation === 'function') {
                    window.toggleDnaAnimation(false);
                }
            </script>
            """, unsafe_allow_html=True)
            
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
            
            # Also update the dropdown in the fallback case
            with dropdown_container:
                with st.expander("🧬 DNA Genopath - Statistics 🧬", expanded=False):
                    # Create columns for a nice layout of statistics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Genes", len(genes))
                    with col2:
                        st.metric("Phenotypes", len(phenotypes))
                    with col3:
                        st.metric("Diagnostic Measures", len(diagnostics))
                        
                    # Add a small vertical space
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Second row for edges
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Gene-Phenotype Edges", graph_stats["gene_to_pheno_edges"])
                    with col2:
                        st.metric("Phenotype-Diagnostic Edges", graph_stats["pheno_to_diag_edges"])
                    with col3:
                        st.metric("Total Edges", graph_stats["total_edges"])
        except:
            st.error("Unable to display graph visualization. The dataset may be too large.")
    
    # No interaction tips
    
except Exception as e:
    st.error(f"Error loading knowledge graph: {str(e)}")
    st.write("Please check that the prototype.py file is correctly configured and all dependencies are installed.")
    st.code("""
    # Make sure these packages are installed:
    pip install streamlit plotly networkx owlready2 pandas numpy matplotlib
    """)