"""
Direct test of node value visualization.

This script:
1. Sets a phenotype node to a specific value
2. Generates a visualization from scratch
3. Displays the visualization
"""

import streamlit as st
import time
from backend.backA.data_storage.value_manager import set_node_value
from backend.backA.data_storage.database import get_node_value

# Set page title and width
st.set_page_config(page_title="Test Visualization", layout="wide")

st.title("Node Value Visualization Test")

# User inputs
gene_input = st.text_input("Gene to visualize (e.g., TBXT)", value="TBXT")
phenotype_id = st.text_input("Phenotype ID to modify", value="HP:0000252")

# Value controls
col1, col2, col3 = st.columns(3)
with col1:
    present = st.button("Set to Present (1.0)")
with col2:
    uncertain = st.button("Set to Uncertain (0.5)")
with col3:
    absent = st.button("Set to Absent (0.0)")

# Set the value based on button clicks
if present or uncertain or absent:
    value = 1.0 if present else (0.0 if absent else 0.5)
    set_node_value(phenotype_id, 'phenotype', value)
    
    # Get the actual value to verify
    actual_value = get_node_value(phenotype_id, 'phenotype')
    st.success(f"Set {phenotype_id} to {value} (actual value: {actual_value})")
    
    # Force a delay to ensure value is written
    time.sleep(0.5)

# Generate visualization button
if st.button("Generate Visualization"):
    if not gene_input:
        st.error("Please enter a gene to visualize")
    else:
        # Clear ontology to force rebuild
        from backend.backA.ontology.schema import clear_ontology
        clear_ontology()
        
        with st.spinner("Generating knowledge graph..."):
            # Get the current value of the phenotype
            current_value = get_node_value(phenotype_id, 'phenotype')
            st.write(f"Current value of {phenotype_id}: {current_value}")
            
            # Generate the visualization
            from backend.controller import create_knowledge_graph
            fig, genes, phenotypes, diagnostics, positions_3d, G, graph_stats = create_knowledge_graph(
                [gene_input.strip()], 
                force_refresh=True
            )
            
            # Check if the phenotype is in the result
            st.write(f"Phenotypes in result: {len(phenotypes)}")
            if phenotype_id in phenotypes:
                st.write(f"Phenotype {phenotype_id} is in the visualization")
                
                # Check its value in the final graph
                final_value = get_node_value(phenotype_id, 'phenotype')
                st.write(f"Final value in graph: {final_value}")
            else:
                st.warning(f"Phenotype {phenotype_id} is not in the visualization")
                st.write(f"Available phenotypes: {phenotypes}")
        
        # Display the visualization
        st.plotly_chart(fig, use_container_width=True)