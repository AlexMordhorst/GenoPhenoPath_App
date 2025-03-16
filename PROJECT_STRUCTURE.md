# GenoPhenoPath Project Structure

## Overview
GenoPhenoPath is a 3D visualization tool for exploring the relationships between genes, phenotypes, and diagnostic procedures. The application creates an interactive knowledge graph connecting genomic data with phenotypic manifestations and related diagnostic measures.

## Core Components

### Main Files
- `app.py`: Main entry point for the Streamlit application
- `prototype.py`: Core implementation of the knowledge graph generation and visualization logic
- `requirements.txt`: Project dependencies
- `CLAUDE.md`: Development guidelines and documentation

### Data Files
- `Data/vartest.tsv`: Genetic variant data with pathogenicity scores and gene information
- `Data/genes_to_phenotype.txt`: Mapping between genes and associated phenotypes (HPO terms)
- `Data/maxo_diagnostic_annotations.tsv`: Mapping of phenotypes to diagnostic procedures (MAXO terms)
- `Data/maxo_diagnostic_annotations2.txt`: Alternative format of the diagnostic annotations
- `Data/karate.gml`: Graph data file (likely used for testing)

## Data Flow

1. **Data Loading**: 
   - Genetic variant data loaded from `vartest.tsv`
   - Gene-to-phenotype mappings loaded from `genes_to_phenotype.txt`
   - Phenotype-to-diagnostic mappings loaded from `maxo_diagnostic_annotations2.txt`

2. **Knowledge Graph Construction**:
   - Creation of an ontology using Owlready2 with three main entity types: Gene, Phenotype, and Diagnostic
   - Establishment of connections between entities based on the loaded data
   - Conversion of the ontology to a NetworkX directed graph for analysis and visualization

3. **3D Visualization**:
   - Custom 3D shell layout that positions nodes in concentric spheres
   - Genes in innermost sphere (blue)
   - Phenotypes in middle sphere (orange)
   - Diagnostics in outermost sphere (magenta)
   - Gene-phenotype connections shown as blue lines
   - Phenotype-diagnostic connections shown as orange lines

4. **Statistics Generation**:
   - Graph metrics calculation for nodes and edges
   - Entity-specific statistics (degree distribution, connectivity patterns)

## Scientific Standards
- Phenotypes reference Human Phenotype Ontology (HPO) terms
- Diagnostic procedures follow Medical Action Ontology (MAXO) standards
- Gene symbols follow HUGO Gene Nomenclature Committee conventions

## Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## Key Technologies
- **Streamlit**: Web application framework
- **NetworkX**: Graph manipulation and analysis
- **Owlready2**: Ontology management
- **Plotly**: 3D interactive visualization
- **Pandas/NumPy**: Data manipulation and analysis

## Visual Representation
The knowledge graph visualization arranges nodes in three concentric spheres:
- **Inner Sphere (Blue)**: Gene nodes
- **Middle Sphere (Orange)**: Phenotype nodes
- **Outer Sphere (Magenta)**: Diagnostic procedure nodes

Connections between nodes are visualized as directed edges (lines):
- **Blue Lines**: Gene → Phenotype connections
- **Orange Lines**: Phenotype → Diagnostic connections

## Performance Considerations
- Edge limit mechanism to prevent overloading with large datasets (default: 1000 edges)
- Optimized marker and line sizes for better visualization
- Custom 3D layout algorithm for improved clarity and node separation