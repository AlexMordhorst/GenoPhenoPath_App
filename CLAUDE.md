# GenoPhenoPath: 3D Knowledge Graph for Genome-Phenotype-Diagnostic Visualization

## Development Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Alternative: create conda environment
conda env create -f environment.yml
conda activate GenoPhenoPath

# Run application
streamlit run app.py
```

## Coding Standards & Technical Specifications
| Category | Standard |
|----------|----------|
| Code Formatting | PEP 8 compliant, max line length 100 characters |
| Import Order | (1) Standard library (2) Third-party packages (3) Local modules |
| Naming Conventions | snake_case for variables/functions, CamelCase for classes |
| Graph Visualization | 3D network representation via plotly.graph_objects |
| Type Definitions | Function parameters and return values should include type annotations |
| Exception Handling | Use specific exception types with clear error messages |
| Documentation | Triple-quoted docstrings with parameter descriptions |

## System Architecture
- **app.py**: Primary UI layer and visualization controllers
- **prototype.py**: Data processing and knowledge graph generation engine
- **Data/**: Contains tab-separated datasets for:
  - Gene-phenotype associations
  - Phenotype-diagnostic relationships
  - Ontological structures

## Scientific Data Standards
- All phenotypes reference Human Phenotype Ontology (HPO) terms
- Diagnostic procedures follow Medical Action Ontology (MAXO) standards
- Gene symbols follow HUGO Gene Nomenclature Committee conventions