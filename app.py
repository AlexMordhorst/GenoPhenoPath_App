"""
GenoPhenoPath Application

This is the main entry point for the GenoPhenoPath application, which creates
a 3D interactive knowledge graph connecting genes, phenotypes, and diagnostic procedures.

The application is built using Streamlit for the frontend and leverages Plotly for
3D visualization, NetworkX for graph operations, and Owlready2 for ontology management.
"""

from frontend.frontB.app.main import run_app

# Run the main application
if __name__ == "__main__":
    run_app()