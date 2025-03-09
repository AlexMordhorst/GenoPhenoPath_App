# Import necessary libraries for data manipulation, ontology management, network analysis, and visualization
import numpy as np
import pandas as pd
import owlready2 as owl  # Python library for ontology manipulation
import networkx as nx    # Graph/network manipulation library
import plotly.graph_objects as go  # For interactive 3D visualization

# Function to create the knowledge graph - allows app.py to import this directly
def create_knowledge_graph():
    # Load Patient Genome Sequencing Data
    table = pd.read_csv("./Data/vartest.tsv", sep='\t')
    table2 = table.iloc[:, [0,1,2,3,6,8,22,24,25,26,40]].sort_values("Pathogenicity Score", ascending=False).loc[table["Pathogenicity Score"] >= 15]
    
    # Load diagnostic annotations data - maps HPO terms to diagnostic procedures (MAXO terms)
    hpo2diag = pd.read_csv("./Data/maxo_diagnostic_annotations2.txt", sep='\t')
    
    # Load gene-to-phenotype mapping data
    gene2phen = pd.read_csv("./Data/genes_to_phenotype.txt", sep='\t')
    # Filter gene-phenotype associations to only include genes from table2
    gene2phen2 = gene2phen[gene2phen["gene_symbol"].isin(table2["Gene Symbol"])]
    
    # Create deduplicated dataframes for unique genes and phenotypes
    gene2phen2sg = gene2phen2.drop_duplicates(subset=["gene_symbol"])  # One row per unique gene
    gene2phen2sp = gene2phen2.drop_duplicates(subset=["hpo_id"])       # One row per unique phenotype


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

        # Create Gene instances in the ontology from our data
        for gene in gene2phen2sg["gene_symbol"]:
            my_new_gene = Gene(gene)
        
        # Create Phenotype instances in the ontology from our data    
        for phen in gene2phen2sp["hpo_id"]:
            my_new_phen = Phenotype(phen)

        # Create Diagnostic instances in the ontology from our data
        for diag in hpo2diag["maxo_label"]:
            my_new_diag = Diagnostic(diag)

        ## Insert Gene to Phenotype Relations
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
        
        ## Insert Phenotype to Diagnostics Relations
        # Group diagnostics by phenotype and establish connections   
        phen_considered = hpo2diag.iloc[0]["hpo_id"]  # Start with first phenotype
        diag_list = []  # Initialize list to collect diagnostics for current phenotype
        for index, entry in hpo2diag.iterrows():
            if phen_considered == entry["hpo_id"]:
                # Add diagnostic to the current phenotype's list
                diag_list.append(Diagnostic(entry["maxo_label"]))
            elif phen_considered is not entry["hpo_id"]:
                # When we encounter a new phenotype, connect the previous phenotype to all its diagnostics
                Phenotype(phen_considered).ConnectedTo = diag_list
                # Reset for next phenotype
                diag_list = []
                phen_considered = entry["hpo_id"]
                diag_list.append(Diagnostic(entry["maxo_label"]))
                
    # Create lists to store entities by type (for visualization grouping)
    community_0 = []  # Genes
    community_1 = []  # Phenotypes
    community_2 = []  # Diagnostics

    # Extract gene names from ontology and remove prefix
    for i in onto.Gene.instances():
        community_0.append(str(i).removeprefix("onto."))

    # Extract phenotype IDs from ontology and remove prefix
    for i in onto.Phenotype.instances():
        community_1.append(str(i).removeprefix("onto."))

    # Extract diagnostic names from ontology and remove prefix
    for i in onto.Diagnostic.instances():
        community_2.append(str(i).removeprefix("onto."))


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


    # Define a custom 3D shell layout function
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
    
    # Create a node type dictionary for the 3D shell layout
    node_types = {}
    # Genes in the innermost shell (0)
    for gene in community_0:
        node_types[gene] = 0
    # Phenotypes in the middle shell (1)
    for phenotype in community_1:
        node_types[phenotype] = 1
    # Diagnostics in the outermost shell (2)
    for diagnostic in community_2:
        node_types[diagnostic] = 2
        
    # Use our custom shell layout instead of spring layout
    spring_3D = shell_layout_3d(G, node_types)

    # Get node counts
    n_genes = len(onto.Gene.instances())
    n_pheno = len(onto.Phenotype.instances())
    n_diag = len(onto.Diagnostic.instances())
    Num_nodes = n_genes + n_pheno + n_diag

    # Extract node coordinates from the 3D layout - optimize by direct indexing
    nodes_list = list(spring_3D.values())
    x_nodes = [nodes_list[i][0] for i in range(Num_nodes)]
    y_nodes = [nodes_list[i][1] for i in range(Num_nodes)]
    z_nodes = [nodes_list[i][2] for i in range(Num_nodes)]

    # Split node coordinates by entity type (gene, phenotype, diagnostic)
    # Fix the slicing to include all nodes
    x_nodes_gene = x_nodes[0:n_genes]
    x_nodes_phenotype = x_nodes[n_genes:(n_genes+n_pheno)]
    x_nodes_diagnostic = x_nodes[(n_genes+n_pheno):]

    y_nodes_gene = y_nodes[0:n_genes]
    y_nodes_phenotype = y_nodes[n_genes:(n_genes+n_pheno)]
    y_nodes_diagnostic = y_nodes[(n_genes+n_pheno):]

    z_nodes_gene = z_nodes[0:n_genes]
    z_nodes_phenotype = z_nodes[n_genes:(n_genes+n_pheno)]
    z_nodes_diagnostic = z_nodes[(n_genes+n_pheno):]


    # Prepare edge coordinates for visualization more efficiently
    # For large graphs, limit the number of edges to improve performance
    edge_list = list(G.edges())
    
    # By default, limit to 1000 edges, but make this configurable
    # This will be connected to the app.py edge_limit parameter
    original_edge_count = len(edge_list)
    max_edges = 1000  # Default limit
    
    if original_edge_count > max_edges:
        # Use a sample of edges if there are too many
        import random
        random.seed(42)  # For consistent results
        edge_list = random.sample(edge_list, max_edges)

    x_edges = []
    y_edges = []
    z_edges = []

    # Process edges in batches for efficiency
    for edge in edge_list:
        # For each edge, create line coordinates
        # None values create gaps between edges for better visualization
        x_coords = [spring_3D[edge[0]][0], spring_3D[edge[1]][0], None]
        x_edges.extend(x_coords)
        
        y_coords = [spring_3D[edge[0]][1], spring_3D[edge[1]][1], None]
        y_edges.extend(y_coords)
        
        z_coords = [spring_3D[edge[0]][2], spring_3D[edge[1]][2], None]
        z_edges.extend(z_coords)
        
    # Split edges by type for better visualization and control
    # Find edges between genes and phenotypes
    gene_to_pheno_edges = []
    pheno_to_diag_edges = []
    
    for edge in edge_list:
        source, target = edge
        if source in community_0 and target in community_1:
            # Gene to phenotype edge
            gene_to_pheno_edges.append(edge)
        elif source in community_1 and target in community_2:
            # Phenotype to diagnostic edge
            pheno_to_diag_edges.append(edge)
    
    # Create coordinates for gene-to-phenotype edges
    gene_pheno_x = []
    gene_pheno_y = []
    gene_pheno_z = []
    
    for edge in gene_to_pheno_edges:
        x_coords = [spring_3D[edge[0]][0], spring_3D[edge[1]][0], None]
        gene_pheno_x.extend(x_coords)
        
        y_coords = [spring_3D[edge[0]][1], spring_3D[edge[1]][1], None]
        gene_pheno_y.extend(y_coords)
        
        z_coords = [spring_3D[edge[0]][2], spring_3D[edge[1]][2], None]
        gene_pheno_z.extend(z_coords)
    
    # Create coordinates for phenotype-to-diagnostic edges
    pheno_diag_x = []
    pheno_diag_y = []
    pheno_diag_z = []
    
    for edge in pheno_to_diag_edges:
        x_coords = [spring_3D[edge[0]][0], spring_3D[edge[1]][0], None]
        pheno_diag_x.extend(x_coords)
        
        y_coords = [spring_3D[edge[0]][1], spring_3D[edge[1]][1], None]
        pheno_diag_y.extend(y_coords)
        
        z_coords = [spring_3D[edge[0]][2], spring_3D[edge[1]][2], None]
        pheno_diag_z.extend(z_coords)
    
    # Create gene-to-phenotype edges trace (blue lines)
    trace_edges_gene_pheno = go.Scatter3d(
        x=gene_pheno_x,
        y=gene_pheno_y,
        z=gene_pheno_z,
        mode='lines',
        line=dict(color='blue', width=0.4),  # Blue lines for gene-phenotype connections
        opacity=0.4,
        hoverinfo='none',
        name='Gene-Phenotype Connections'
    )
    
    # Create phenotype-to-diagnostic edges trace (orange lines)
    trace_edges_pheno_diag = go.Scatter3d(
        x=pheno_diag_x,
        y=pheno_diag_y,
        z=pheno_diag_z,
        mode='lines',
        line=dict(color='orange', width=0.3),  # Orange lines for phenotype-diagnostic connections
        opacity=0.3,
        hoverinfo='none',
        name='Phenotype-Diagnostic Connections'
    )

    # Create gene nodes trace (blue color)
    trace_nodes_gene = go.Scatter3d(
        x=x_nodes_gene,
        y=y_nodes_gene,
        z=z_nodes_gene,
        mode='markers',
        marker=dict(
            symbol='circle',
            size=10,  # Moderate size for genes
            color="blue",
            line=dict(width=0)  # No border line
        ),
        hoverinfo='text', 
        hovertext=community_0, 
        opacity=0.9,
        name='Genes'
    )

    # Create phenotype nodes trace (orange color)
    trace_nodes_phenotype = go.Scatter3d(
        x=x_nodes_phenotype,
        y=y_nodes_phenotype,
        z=z_nodes_phenotype,
        mode='markers',
        marker=dict(
            symbol='circle',
            size=3,  # Very small size for phenotypes
            color="orange",
            line=dict(width=0)  # No border line
        ),
        hoverinfo='text', 
        hovertext=community_1, 
        opacity=0.2,  # Lower opacity for phenotypes
        name='Phenotypes'
    )

    # Create diagnostic nodes trace (magenta color)
    trace_nodes_diagnostic = go.Scatter3d(
        x=x_nodes_diagnostic,
        y=y_nodes_diagnostic,
        z=z_nodes_diagnostic,
        mode='markers',
        marker=dict(
            symbol='circle',
            size=8,  # Smaller than genes but larger than phenotypes
            color="magenta",
            line=dict(width=0)  # No border line
        ),
        hoverinfo='text', 
        hovertext=community_2, 
        opacity=0.7,
        name='Diagnostic Measures'
    )


    # Configure axis settings for the 3D plot (hide all axes)
    axis = dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title='')

    # Calculate graph statistics for the title/description
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    avg_node_degree = round(np.mean([j for i, j in G.degree()]),2)

    # Calculate gene-specific statistics
    avg_node_degree_gene = round(np.mean([j for i, j in G.degree(community_0)]),2)
    max_node_degree_gene = np.max([j for i, j in G.degree(community_0)])
    max_node_name_gene = str([tup[0] for tup in G.degree(community_0) if tup[1] == max_node_degree_gene]).replace("'","").replace("[","").replace("]","")
    min_node_degree_gene = np.min([j for i, j in G.degree(community_0) if j != 0])
    min_node_name_gene = str([tup[0] for tup in G.degree(community_0) if tup[1] == min_node_degree_gene]).replace("'","").replace("[","").replace("]","")
    gene_nophenotype = str([tup[0] for tup in G.degree(community_0) if tup[1] == 0]).replace("'","").replace("[","").replace("]","")

    # Calculate diagnostic-specific statistics
    avg_node_degree_diagnostic = round(np.mean([j for i, j in G.degree(community_2)]),2)
    max_node_degree_diagnostic = np.max([j for i, j in G.degree(community_2)])
    max_node_name_diagnostic = str([tup[0] for tup in G.degree(community_2) if tup[1] == max_node_degree_diagnostic]).replace("'","").replace("[","").replace("]","")
    min_node_degree_diagnostic = np.min([j for i, j in G.degree(community_2)])
    min_node_name_diagnostic = str([tup[0] for tup in G.degree(community_2) if tup[1] == min_node_degree_diagnostic]).replace("'","").replace("[","").replace("]","")

    # Create a dark spacey layout for the 3D graph
    layout = go.Layout(
        # No title
        title_text = "",
        width=1000,
        height=800,
        showlegend=False,  # Hide legend
        legend=dict(
            font=dict(color="#f8f8f2"),
            bgcolor="rgba(15, 22, 36, 0.5)"
        ),
        scene=dict(
            xaxis=dict(axis,
                      gridcolor="#1a1a2e", 
                      zerolinecolor="#1a1a2e"),
            yaxis=dict(axis,
                      gridcolor="#1a1a2e", 
                      zerolinecolor="#1a1a2e"),
            zaxis=dict(axis,
                      gridcolor="#1a1a2e", 
                      zerolinecolor="#1a1a2e"),
            bgcolor="rgb(5, 10, 25)",  # Dark space background
        ),
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper bg to blend with app bg
        plot_bgcolor="rgba(0,0,0,0)",   # Transparent plot bg
        margin=dict(t=50, l=0, r=0, b=0),
        hovermode='closest'
    )

    # Calculate edge counts between different node types
    gene_to_pheno_edge_count = len(gene_to_pheno_edges)
    pheno_to_diag_edge_count = len(pheno_to_diag_edges)
    
    # Store graph statistics as separate variables for the app to use if needed
    graph_stats = {
        "total_nodes": n_nodes,
        "total_edges": n_edges,
        "gene_count": len(community_0),
        "phenotype_count": len(community_1),
        "diagnostic_count": len(community_2),
        "gene_to_pheno_edges": gene_to_pheno_edge_count,
        "pheno_to_diag_edges": pheno_to_diag_edge_count,
        "avg_node_degree": avg_node_degree,
        "avg_gene_phenotypes": avg_node_degree_gene,
        "max_phenotype_gene": max_node_name_gene,
        "max_phenotype_count": max_node_degree_gene,
        "min_phenotype_gene": min_node_name_gene,
        "min_phenotype_count": min_node_degree_gene,
        "genes_no_phenotype": gene_nophenotype,
        "avg_diagnostic_coverage": avg_node_degree_diagnostic,
        "max_coverage_diagnostic": max_node_name_diagnostic,
        "max_coverage_count": max_node_degree_diagnostic,
        "min_coverage_diagnostic": min_node_name_diagnostic,
        "min_coverage_count": min_node_degree_diagnostic
    }

    # Combine all traces and create the final figure with the new edge types
    data = [
        trace_edges_gene_pheno,  # Gene-phenotype edges
        trace_edges_pheno_diag,  # Phenotype-diagnostic edges
        trace_nodes_gene,        # Gene nodes
        trace_nodes_phenotype,   # Phenotype nodes
        trace_nodes_diagnostic   # Diagnostic nodes
    ]
    fig = go.Figure(data=data, layout=layout)
    
    # Return all the relevant objects for use in the app
    return fig, community_0, community_1, community_2, spring_3D, G, graph_stats

# Execute function if script is run directly (not imported)
if __name__ == "__main__":
    fig, community_0, community_1, community_2, spring_3D, G, graph_stats = create_knowledge_graph()
