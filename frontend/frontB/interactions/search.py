"""
Search functionality for the GenoPhenoPath application.

This module provides search capabilities for finding nodes (genes, phenotypes, diagnostics)
in the knowledge graph.

Functions in this module are used in:
- frontend.frontB.app.main: For processing search queries
- frontend.frontB.display.chart: For handling search results
"""

import streamlit as st
from typing import Dict, List, Any, Tuple

def search_nodes(
    search_term: str,
    genes: List[str],
    phenotypes: List[str],
    diagnostics: List[str]
) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Search for nodes that match the given search term.
    
    Args:
        search_term: Search query string
        genes: List of gene names
        phenotypes: List of phenotype IDs
        diagnostics: List of diagnostic labels
        
    Returns:
        Tuple containing:
        - List of all matching node names
        - Dictionary with matching nodes by type:
          - genes: List of matching gene names
          - phenotypes: List of matching phenotype IDs
          - diagnostics: List of matching diagnostic labels
        
    Used in:
    - frontend.frontB.display.chart.handle_search
    """
    # Create a list to hold nodes that match the search term
    matching_nodes = []
    matches_by_type = {
        "genes": [],
        "phenotypes": [],
        "diagnostics": []
    }
    
    # Case-insensitive search
    search_term_lower = search_term.lower()
    
    # Check for matches in genes
    matching_genes = [gene for gene in genes if search_term_lower in gene.lower()]
    if matching_genes:
        matching_nodes.extend(matching_genes)
        matches_by_type["genes"] = matching_genes
    
    # Check for matches in phenotypes
    matching_phenotypes = [phen for phen in phenotypes if search_term_lower in phen.lower()]
    if matching_phenotypes:
        matching_nodes.extend(matching_phenotypes)
        matches_by_type["phenotypes"] = matching_phenotypes
    
    # Check for matches in diagnostics
    matching_diagnostics = [diag for diag in diagnostics if search_term_lower in diag.lower()]
    if matching_diagnostics:
        matching_nodes.extend(matching_diagnostics)
        matches_by_type["diagnostics"] = matching_diagnostics
    
    return matching_nodes, matches_by_type

def display_search_results(matches_by_type: Dict[str, List[str]]):
    """
    Display the results of a node search query.
    
    Args:
        matches_by_type: Dictionary with matching nodes by type
        
    Used in:
    - frontend.frontB.display.chart.handle_search
    """
    # Display gene matches
    if matches_by_type["genes"]:
        st.write(f"Found matching genes: {', '.join(matches_by_type['genes'])}")
    
    # Display phenotype matches
    if matches_by_type["phenotypes"]:
        st.write(f"Found matching phenotypes: {', '.join(matches_by_type['phenotypes'])}")
    
    # Display diagnostic matches
    if matches_by_type["diagnostics"]:
        st.write(f"Found matching diagnostic measures: {', '.join(matches_by_type['diagnostics'])}")
    
    # Display message if no matches found
    if not any(matches_by_type.values()):
        st.warning(f"No nodes found matching '{st.session_state.get('search_term', '')}'")

def handle_search(
    search_term: str,
    genes: List[str],
    phenotypes: List[str],
    diagnostics: List[str]
) -> List[str]:
    """
    Process a search query and display results.
    
    Args:
        search_term: Search query string
        genes: List of gene names
        phenotypes: List of phenotype IDs
        diagnostics: List of diagnostic labels
        
    Returns:
        List of all matching node names
        
    Used in:
    - frontend.frontB.display.chart.update_visualization
    """
    if not search_term:
        return []
    
    # Search for matching nodes
    matching_nodes, matches_by_type = search_nodes(search_term, genes, phenotypes, diagnostics)
    
    # Display search results
    display_search_results(matches_by_type)
    
    return matching_nodes