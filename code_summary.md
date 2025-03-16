# GenoPhenoPath Code Structure and Organization

This document summarizes the code structure of the GenoPhenoPath application, which creates a 3D interactive knowledge graph connecting genes, phenotypes, and diagnostic procedures. The codebase is split into two main files:

1. `prototype.py`: Data processing and knowledge graph generation
2. `app.py`: User interface and visualization controls

## 1. Data Processing and Knowledge Graph Generation (`prototype.py`)

### 1.1 Data Loading and Preparation

The application loads and processes data from various tab-separated files:

```python
# Load Patient Genome Sequencing Data
table = pd.read_csv("./Data/vartest.tsv", sep='\t')
table2 = table.iloc[:, [0,1,2,3,6,8,22,24,25,26,40]].sort_values("Pathogenicity Score", ascending=False).loc[table["Pathogenicity Score"] >= 15]

# Load diagnostic annotations data - maps HPO terms to diagnostic procedures (MAXO terms)
hpo2diag = pd.read_csv("./Data/maxo_diagnostic_annotations2.txt", sep='\t')

# Load gene-to-phenotype mapping data
gene2phen = pd.read_csv("./Data/genes_to_phenotype.txt", sep='\t')
# Filter gene-phenotype associations to only include genes from table2
gene2phen2 = gene2phen[gene2phen["gene_symbol"].isin(table2["Gene Symbol"])]
```

### 1.2 Ontology Creation

The app creates an ontology structure using owlready2:

```python
# Create a new ontology for our knowledge graph
onto = owl.get_ontology("http://test.org/onto.owl")
with onto:
    # Define main entity classes in our ontology
    class Gene(owl.Thing):
        pass
    class Phenotype(owl.Thing):
        pass
    class Measure(owl.Thing):
        pass
    class Diagnostic(Measure):  # Diagnostic is a subclass of Measure
        pass
    
    # Define relationship between entities
    class ConnectedTo(owl.Thing >> owl.Thing):  # Generic relationship between any two entities
        pass
```

### 1.3 Entity Population

The ontology is populated with entities from the data:

```python
# Create Gene instances in the ontology from our data
for gene in gene2phen2sg["gene_symbol"]:
    my_new_gene = Gene(gene)

# Create Phenotype instances in the ontology from our data    
for phen in gene2phen2sp["hpo_id"]:
    my_new_phen = Phenotype(phen)

# Create Diagnostic instances in the ontology from our data
for diag in hpo2diag["maxo_label"]:
    my_new_diag = Diagnostic(diag)
```

### 1.4 Relationship Mapping

Relationships between entities are established:

```python
# Group phenotypes by gene and establish connections
gene_considered = gene2phen2.iloc[0]["gene_symbol"]  # Start with first gene
phen_list = []  # Initialize list to collect phenotypes for current gene
for index, entry in gene2phen2.iterrows():
    if gene_considered == entry["gene_symbol"]:
        # Add phenotype to the current gene's list
        phen_list.append(Phenotype(entry["hpo_id"]))
    elif gene_considered is not entry["gene_symbol"]:
        # When we encounter a new gene, connect the previous gene to all its phenotypes
        Gene(gene_considered).ConnectedTo = phen_list
        # Reset for next gene
        phen_list = []
        gene_considered = entry["gene_symbol"]
        phen_list.append(Phenotype(entry["hpo_id"]))
```

### 1.5 NetworkX Graph Creation

The ontology is converted to a NetworkX directed graph:

```python
# Create directed graph to represent our knowledge graph
G = nx.DiGraph()

# Add all nodes and edges to the graph from our ontology
# First, add diagnostic nodes
for nodediag in onto.Diagnostic.instances():
    G.add_node(nodediag.name, label=nodediag.is_a[0].name)
# Add phenotype nodes
for nodephen in onto.Phenotype.instances():
    G.add_node(nodephen.name, label=nodephen.is_a[0].name)
# Add gene nodes and gene->phenotype edges
for nodegene in onto.Gene.instances():
    G.add_node(nodegene.name, label=nodegene.is_a[0].name)
    for genephenconnected in nodegene.ConnectedTo:
        G.add_edge(nodegene.name, genephenconnected.name)
# Add phenotype->diagnostic edges
for nodephen in onto.Phenotype.instances():
    for phendiagconnected in nodephen.ConnectedTo:
        G.add_edge(nodephen.name, phendiagconnected.name)
```

### 1.6 3D Layout Generation

A custom 3D shell layout is created to position nodes in concentric spheres:

```python
def shell_layout_3d(G, node_types):
    """
    Position nodes in concentric 3D shells (spheres).
    
    Parameters:
    -----------
    G : NetworkX graph
        A graph
    
    node_types : dict
        Dictionary with node names as keys and node types as values.
        Node types should be integers representing the shell (0=innermost, 1=middle, 2=outermost)
    
    Returns:
    --------
    pos : dict
        Dictionary of positions keyed by node
    """
    import numpy as np
    import random
    
    # Define radii for each shell - innermost has smallest radius
    shell_radii = {0: 0.5, 1: 1.0, 2: 1.5}  # These values can be adjusted
    
    # Initialize the position dictionary
    pos = {}
    
    # Group nodes by shell
    shells = {}
    for node, shell in node_types.items():
        if shell not in shells:
            shells[shell] = []
        shells[shell].append(node)
    
    # Distribute nodes in each shell
    for shell_number, nodes in shells.items():
        # Get radius for this shell
        radius = shell_radii[shell_number]
        
        # Number of nodes in this shell
        n_nodes = len(nodes)
        
        # Calculate positions for each node in this shell
        for i, node in enumerate(nodes):
            # For evenly spaced distribution on a sphere, we use the Fibonacci sphere algorithm
            golden_ratio = (1 + 5**0.5) / 2
            
            # Create a randomization offset for each node
            random_offset = random.uniform(-0.05, 0.05)
            
            # Calculate angles
            i_offset = i + random_offset  # Add a small random offset for variation
            phi = np.arccos(1 - 2 * (i_offset + 0.5) / n_nodes)
            theta = 2 * np.pi * i_offset / golden_ratio
            
            # Convert spherical to Cartesian coordinates
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            
            # Set position
            pos[node] = np.array([x, y, z])
    
    return pos
```

### 1.7 Plotly Visualization Preparation

The 3D network visualization is created using Plotly:

```python
# Create gene-to-phenotype edges trace (blue lines)
trace_edges_gene_pheno = go.Scatter3d(
    x=gene_pheno_x,
    y=gene_pheno_y,
    z=gene_pheno_z,
    mode='lines',
    line=dict(color='blue', width=0.3*reduction_factor),
    opacity=0.4,
    hoverinfo='none',
    name='Gene-Phenotype Connections'
)

# Create gene nodes trace (blue color)
trace_nodes_gene = go.Scatter3d(
    x=x_nodes_gene,
    y=y_nodes_gene,
    z=z_nodes_gene,
    mode='markers',
    marker=dict(
        symbol='circle',
        size=10*reduction_factor,
        color="blue",
        line=dict(width=0)  # No border line
    ),
    hoverinfo='text', 
    hovertext=community_0, 
    opacity=0.9,
    name='Genes'
)
```

### 1.8 Statistical Analysis

Graph statistics are calculated for informative visualizations:

```python
# Calculate graph statistics for the title/description
n_nodes = G.number_of_nodes()
n_edges = G.number_of_edges()
avg_node_degree = round(np.mean([j for i, j in G.degree()]),2)

# Calculate gene-specific statistics
avg_node_degree_gene = round(np.mean([j for i, j in G.degree(community_0)]),2)
max_node_degree_gene = np.max([j for i, j in G.degree(community_0)])
max_node_name_gene = str([tup[0] for tup in G.degree(community_0) if tup[1] == max_node_degree_gene]).replace("'","").replace("[","").replace("]","")
```

## 2. User Interface and Visualization Controls (`app.py`)


### A - Setting up Streamlit Fundamentals:

### 2.1 Streamlit UI Configuration

The UI is configured with Streamlit fundamental settings:

```python
# Set page config to make the app wider with dark mode
st.set_page_config(
    page_title="GenoPhenoPath 3D Knowledge Graph",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)
```

### 2.2 Custom CSS Styling

Custom CSS creates a dark space-themed interface:

```python
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
    
    /* Title styling */
    h1 {
        color: #8be9fd !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 10px rgba(139, 233, 253, 0.7);
    }
</style>
""", unsafe_allow_html=True)
```

### 2.3 Session State Management

Session state maintains application state between interactions:

```python
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
```

### 2.4 Sidebar Controls

Controls for customizing the visualization are provided:

```python
# Create a simplified sidebar with better user experience
with st.sidebar:
    st.header("Display Controls")
    
    # Section for node visibility - clean and simple layout
    st.subheader("Show/Hide Nodes")
    
    # Simple checkboxes without complex callbacks
    show_genes = st.checkbox("Genes (blue)", value=True)
    show_phenotypes = st.checkbox("Phenotypes (orange)", value=True)
    show_diagnostics = st.checkbox("Diagnostic Measures (magenta)", value=True)
    
    # Section for connections
    st.subheader("Show/Hide Connections")
    
    show_gene_pheno_edges = st.checkbox("Gene-Phenotype Connections", value=True)
    show_pheno_diag_edges = st.checkbox("Phenotype-Diagnostic Connections", value=True)
```

### 2.5 Loading Animation

A DNA helix animation is displayed during loading:

```python
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
```

### 2.6 Graph Loading

The graph is loaded from prototype.py:

```python
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
```

### B - Start Application with Threading 

# This should be part of main.py for the app (frontend)
# the app starts with initial loading screen
# meanwhile load the inital knowledge graph

"# Try to load the graph data
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
        [...]
            # Clear the animation when done
    animation_placeholder.empty()
    
    # Unpack the result
    fig, genes, phenotypes, diagnostics, layout_3d, graph, graph_stats, elapsed_time = result[0]
        
    # Show toast after function completes (outside the cached function)
    st.toast(f"Graph loaded in {elapsed_time:.2f} seconds")
    
    # No metrics displayed here - only in the dropdown"

### the app should include the following functionalities:

### 2.9 Search Functionality

Users can search for specific nodes:

```python
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
```


### 2.7 Update Customized Graph Visualization

The visualization is customized based on user input:

```python
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
```

### 2.8 Display Statistics (based on current setting in sidebar)

The app shows statistics about the graph:

```python
# Calculate statistics
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
```


### 2.10 Error Handling

The application includes robust error handling:

```python
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
```

## 3. Potential Refactoring Areas

Based on this analysis, here are some areas for potential refactoring:

1. **Modular Code Structure**:
   - Split data loading into separate module
   - Create visualization module
   - Create UI components module
   - Create utilities/helpers module

2. **Improved Data Processing**:
   - Abstract ontology creation
   - Create data models
   - Implement caching for faster loading

3. **Enhanced Visualization**:
   - Abstract visualization settings
   - Create configurable layout options
   - Implement node highlighting and filtering

4. **UI Enhancements**:
   - Create reusable UI components
   - Implement state management
   - Add advanced search and filtering

These suggested improvements could be implemented in a reorganized project structure for better maintainability and scalability.