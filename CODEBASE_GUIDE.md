# GenoPhenoPath Codebase Guide

This document provides detailed guidance for navigating and understanding the GenoPhenoPath application codebase.

## Application Architecture

### Entry Point (`app.py`)
A minimal entry point that imports and runs the main application function:
```python
from frontend.frontB.app.main import run_app

if __name__ == "__main__":
    run_app()
```

### Core Implementation (`prototype.py`)
Contains the majority of the application logic, including:

1. **Data Processing Functions**:
   - Loading genetic variants, gene-phenotype associations, and diagnostic mappings
   - Filtering and transforming data for visualization
   - Line 9-21: Data loading and initial filtering

2. **Ontology Management**:
   - Creation of an Owlready2 ontology with Gene, Phenotype, and Diagnostic classes
   - Establishment of relationships between entity instances
   - Line 27-87: Ontology creation and entity relationship mapping

3. **Graph Construction**:
   - Conversion of ontology to NetworkX directed graph
   - Node and edge creation from the ontology data
   - Line 88-124: Graph construction and population

4. **Custom Layout Algorithm**:
   - Implementation of a 3D shell layout for concentric spherical arrangement
   - Position calculation for nodes based on entity type
   - Line 128-206: Custom shell_layout_3d function and node positioning

5. **Visualization Components**:
   - Creation of Plotly visualization traces for nodes and edges
   - Customization of visual properties (colors, sizes, opacity)
   - Line 207-449: Visualization preparation and Plotly figure creation

6. **Statistics Generation**:
   - Calculation of graph metrics and entity-specific statistics
   - Line 389-476: Graph statistics calculation

7. **Main Function**:
   - Integration of all components to create the final visualization
   - Line 479-487: Assembly of the final Plotly figure with all traces

## Data Files Breakdown

### Genetic Variants (`vartest.tsv`)
Contains detailed genetic variant information with over 85 columns including:
- Chromosome and position
- Reference and alternative bases
- Variant types and dbSNP IDs
- Gene symbols and effects
- Pathogenicity scores and clinical significance

### Gene-Phenotype Associations (`genes_to_phenotype.txt`)
Maps genes to associated phenotypes with columns:
- ncbi_gene_id: NCBI gene identifier
- gene_symbol: Gene symbol (e.g., AARS1)
- hpo_id: Human Phenotype Ontology term ID (e.g., HP:0002460)
- hpo_name: Human Phenotype Ontology term name (e.g., "Distal muscle weakness")
- frequency: Occurrence frequency (when available)
- disease_id: Associated disease identifier (e.g., OMIM:613287)

### Phenotype-Diagnostic Mappings (`maxo_diagnostic_annotations2.txt`)
Maps phenotypes to relevant diagnostic procedures with columns:
- hpo_id: Human Phenotype Ontology term ID
- hpo_label: Human Phenotype Ontology term name
- predicate_id: Relationship type (typically "is_observable_through")
- maxo_id: Medical Action Ontology term ID
- maxo_label: Medical Action Ontology term name (diagnostic procedure)
- creator_id: ORCID identifier of the mapping creator

## Key Implementation Details

### Ontology Structure
The application creates a custom ontology with:
- `Gene` class: Represents genetic entities
- `Phenotype` class: Represents phenotypic manifestations
- `Diagnostic` class (subclass of `Measure`): Represents diagnostic procedures
- `ConnectedTo` property: Represents relationships between entities

### Visualization Layout
Nodes are positioned in three concentric spheres:
- Inner sphere (radius 0.5): Gene nodes
- Middle sphere (radius 1.0): Phenotype nodes
- Outer sphere (radius 1.5): Diagnostic nodes

The Fibonacci sphere algorithm is used to distribute nodes evenly on each sphere, with small random offsets to avoid perfect alignment.

### Edge Rendering
- Gene-to-Phenotype edges: Blue lines with 0.26 width and 0.4 opacity
- Phenotype-to-Diagnostic edges: Orange lines with 0.19 width and 0.3 opacity

### Node Rendering
- Gene nodes: Blue circles with size 6.37 and 0.9 opacity
- Phenotype nodes: Orange circles with size 1.9 and 0.2 opacity
- Diagnostic nodes: Magenta circles with size 5.13 and 0.7 opacity

## Performance Optimizations

1. **Edge Limiting**:
   - Maximum edges capped at 1000 (configurable)
   - Random sampling for large edge sets (with fixed seed for consistency)

2. **Layout Optimization**:
   - Custom 3D shell layout instead of force-directed layout for better clarity
   - Small random position offsets to prevent node overlap

3. **Visualization Optimizations**:
   - Reduced marker sizes and line widths for better performance
   - Adjusted opacity settings to manage visual complexity

## Development Workflow
To modify or extend the application:

1. **Data Processing Changes**:
   - Modify the data loading and filtering in lines 9-21 of prototype.py

2. **Ontology Structure Changes**:
   - Update the ontology definition in lines 27-42 of prototype.py

3. **Visualization Customization**:
   - Adjust node and edge appearance in lines 312-387 of prototype.py
   - Modify layout settings in lines 419-449 of prototype.py

4. **Adding New Entity Types**:
   - Add new classes to the ontology (lines 27-42)
   - Create corresponding node collections (similar to lines 89-103)
   - Add visualization traces for the new entity types (similar to lines 312-387)

## Common Tasks

### Adding a New Data Source
To incorporate a new data source:
1. Add the data file to the `Data/` directory
2. Update the data loading section in prototype.py
3. Modify the ontology creation to include new entities and relationships
4. Update the graph construction to incorporate the new data

### Customizing the Visualization
To change the visual appearance:
1. Modify the trace definitions in lines 312-387 of prototype.py
2. Adjust layout settings in lines 419-449
3. Update the node positioning in the shell_layout_3d function if needed

### Extracting Additional Statistics
To add new statistical metrics:
1. Define new calculations in the statistics section (lines 389-476)
2. Add the new metrics to the graph_stats dictionary (lines 456-476)