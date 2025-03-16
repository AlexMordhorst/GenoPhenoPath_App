# GenoPhenoPath 3D Knowledge Graph

A Streamlit application for visualizing and analyzing gene-phenotype-diagnostic pathways in 3D space with a beautiful dark space-themed UI.

## Overview

GenoPhenoPath is a tool for exploring the relationships between genes, phenotypes, and diagnostic measures. It allows users to visualize a 3D knowledge graph of these relationships and explore the connections between different biological entities in an intuitive 3D space.

## Features

- **3D Interactive Visualization**: Explore the knowledge graph in three-dimensional space with genes in the inner sphere, phenotypes in the middle sphere, and diagnostic measures in the outer sphere.
- **Interactive Filtering**: Selectively show/hide different types of nodes and edges.
- **Search Functionality**: Find specific genes, phenotypes, or diagnostic measures within the graph.
- **Customizable Display**: Adjust node sizes, opacities, and edge visibility for optimal visualization.
- **Dark Space Theme**: Visually appealing dark mode with a space-inspired design.
- **Real-time Statistics**: See counts of displayed nodes and edges compared to the total.

## New Project Structure

The project has been reorganized with a clean separation between backend and frontend components:

```
GenoPhenoPath_app/
├── app.py                 # Main application entry point
├── backend/               # Backend modules
│   ├── controller.py      # Main backend controller
│   ├── backA/             # Core data processing
│   │   ├── data_processing/  # Data loading and preparation
│   │   ├── ontology/      # Ontology schema definitions
│   │   ├── knowledge_graph/ # Entity and relationship management
│   │   └── network/       # NetworkX graph generation
│   ├── backB/             # Visualization preparation
│   │   ├── layout/        # 3D layout creation and edge preparation
│   │   └── visualization/ # Plotly figure generation
│   └── backC/             # Analysis tools
│       ├── statistics/    # Graph metrics calculation
│       └── models/        # Models for data analysis
├── frontend/              # Frontend modules
│   ├── frontA/            # Fundamental Streamlit components
│   │   ├── stages/        # Page configuration and layout setup
│   │   ├── session/       # State management
│   │   └── animations/    # Loading and transition animations
│   └── frontB/            # Application core
│       ├── app/           # Main application runner
│       ├── interactions/  # User controls and search functionality
│       └── display/       # Chart rendering and updating
├── Data/                  # Data directory
│   ├── genes_to_phenotype.txt       # Gene-phenotype relationships
│   ├── maxo_diagnostic_annotations2.txt  # Phenotype-diagnostic relationships
│   └── vartest.tsv        # Gene variant test data
├── environment.yml        # Conda environment specification
├── requirements.txt       # Project dependencies
└── README.md              # This file
```

## Installation

### Using pip

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GenoPhenoPath.git
cd GenoPhenoPath_app
```

2. Create a virtual environment and install the dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
```

### Using Conda

1. Navigate to the project directory:
```bash
cd GenoPhenoPath_app
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate GenoPhenoPath
```

## Required packages

The application requires the following Python packages:
- streamlit
- pandas
- networkx
- owlready2
- plotly
- numpy

The full list is available in the requirements.txt file.

## Data Files

The application uses several data files in the `Data/` directory:

- `genes_to_phenotype.txt`: Tab-separated file with gene-phenotype relationships
- `maxo_diagnostic_annotations2.txt`: Tab-separated file with phenotype-diagnostic relationships
- `vartest.tsv`: Gene variant test data with pathogenicity scores

## Usage

Start the Streamlit application from the project directory:

```bash
streamlit run app.py
```

## Using the Application

1. The application will automatically load and display the 3D knowledge graph
2. Use the controls in the sidebar to:
   - Show/hide different node types (genes, phenotypes, diagnostic measures)
   - Adjust node sizes and opacities
   - Control edge visibility
   - Search for specific nodes
3. Interact with the 3D graph:
   - Click and drag to rotate the view
   - Scroll to zoom in/out
   - Hover over nodes to see their labels
   - Use the search feature to highlight specific nodes

## Module Descriptions

### Backend Modules

- **backA**: Core data processing and knowledge graph generation
  - **data_processing/loader.py**: Data loading and preparation from various sources
  - **ontology/schema.py**: Ontology schema and class definitions
  - **knowledge_graph/nodes.py**: Entity creation (genes, phenotypes, diagnostics)
  - **knowledge_graph/edges.py**: Relationship management between entities
  - **knowledge_graph/builder.py**: Knowledge graph construction orchestration
  - **network/generator.py**: NetworkX graph creation from ontology

- **backB**: Visualization preparation
  - **layout/positions.py**: 3D positioning of nodes in concentric shells
  - **layout/edges.py**: Edge coordinate preparation for visualization
  - **visualization/plotter.py**: Plotly figure generation and customization

- **backC**: Analysis tools
  - **statistics/metrics.py**: Graph metrics and statistics calculation
  - **models/**: Future models for data analysis

### Frontend Modules

- **frontA**: Fundamental Streamlit components
  - **stages/layout.py**: Page configuration and UI layout setup
  - **session/state.py**: Session state management
  - **animations/dna_helix.py**: DNA helix animation for loading states

- **frontB**: Application core
  - **app/main.py**: Main application orchestration
  - **interactions/controls.py**: Sidebar controls and settings
  - **interactions/search.py**: Node search functionality
  - **display/chart.py**: Chart rendering and updating

## Deploying to Streamlit Community Cloud

To deploy this app on Streamlit Community Cloud:

1. First, create a GitHub repository and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/GenoPhenoPath.git
git push -u origin main
```

2. Sign up at [streamlit.io/cloud](https://streamlit.io/cloud) (it's free for public repositories)

3. Connect your GitHub account and select the GenoPhenoPath repository

4. Configure the deployment:
   - Main file path: `app.py`
   - Python version: 3.9 or higher
   - Requirements: The platform will automatically use your requirements.txt file

5. Click "Deploy" and wait for the build to complete

6. Your app will be available at a URL like: `https://yourusername-genophenopath-app-xxxxx.streamlit.app`

## Future Features

- Upload custom gene-phenotype-diagnostic data
- Export graph as interactive HTML
- Statistical analysis of node relationships
- Integration with public genomic databases
- Personalized diagnostic pathway recommendations
- Machine learning-based relationship predictions

## License

[MIT License](LICENSE)

## Author

Created by Alex Mordhorst & Niklas Winnewisser
