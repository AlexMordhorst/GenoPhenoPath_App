"""
Node and edge value management for the GenoPhenoPath application.

This module provides higher-level functions to manage node and edge values,
including setting default values and calculating edge values based on node values.

Functions in this module are used in:
- backend.backA.knowledge_graph.builder: For initializing node values
- backend.backB.visualization.plotter: For retrieving values during visualization

The module implements opacity bucketing to allow for more granular control of node opacities
while maintaining good performance in the visualization.
"""

from typing import Dict, List, Tuple, Any, Optional
import networkx as nx

from backend.backA.data_storage.database import (
    get_node_value,
    set_node_value,
    get_edge_value,
    set_edge_value,
    calculate_edge_value,
    calculate_opacity,
    clear_session_data
)

def initialize_node_values(communities: Dict[str, List[str]]) -> None:
    """
    Initialize default values for all nodes in the communities.
    
    This sets default values based on node type:
    - Genes: 1.0
    - Phenotypes: 0.5
    - Diagnostics: 0.0
    
    Args:
        communities: Dictionary mapping community names to lists of node IDs
    """
    # Set default values for genes (1.0)
    for gene_id in communities.get('genes', []):
        set_node_value(gene_id, 'gene', 1.0)
    
    # Set default values for phenotypes (0.5)
    for phenotype_id in communities.get('phenotypes', []):
        set_node_value(phenotype_id, 'phenotype', 0.5)
    
    # Set default values for diagnostics (0.0)
    for diagnostic_id in communities.get('diagnostics', []):
        set_node_value(diagnostic_id, 'diagnostic', 0.0)

def calculate_edge_values(G: nx.DiGraph, communities: Dict[str, List[str]]) -> None:
    """
    Calculate and store values for all edges in the graph.
    
    Edge values are calculated as the average of the values of the connected nodes.
    
    Args:
        G: NetworkX graph containing the nodes and edges
        communities: Dictionary mapping community names to lists of node IDs
    """
    # Get all edges from the graph
    for source, target in G.edges():
        # Determine node types
        source_type = get_node_type(source, communities)
        target_type = get_node_type(target, communities)
        
        # Calculate and store the edge value
        calculate_edge_value(source, source_type, target, target_type)

def get_node_type(node_id: str, communities: Dict[str, List[str]]) -> str:
    """
    Determine the type of a node based on which community it belongs to.
    
    Args:
        node_id: The ID of the node
        communities: Dictionary mapping community names to lists of node IDs
        
    Returns:
        The node type ('gene', 'phenotype', 'diagnostic')
    """
    if node_id in communities.get('genes', []):
        return 'gene'
    elif node_id in communities.get('phenotypes', []):
        return 'phenotype'
    elif node_id in communities.get('diagnostics', []):
        return 'diagnostic'
    else:
        return 'unknown'

def get_node_opacity(node_id: str, node_type: str) -> float:
    """
    Calculate the opacity for a node based on its value.
    
    Args:
        node_id: The ID of the node
        node_type: The type of the node
        
    Returns:
        The calculated opacity (0.2-0.8)
    """
    value = get_node_value(node_id, node_type)
    return calculate_opacity(value)

def get_edge_opacity(source_id: str, source_type: str, target_id: str, target_type: str) -> float:
    """
    Calculate the opacity for an edge based on its value.

    Args:
        source_id: The ID of the source node
        source_type: The type of the source node
        target_id: The ID of the target node
        target_type: The type of the target node

    Returns:
        The calculated opacity (0.2-0.8)
    """
    # Check if edge value exists
    edge_value = get_edge_value(source_id, target_id)

    # If edge value doesn't exist, calculate it
    if edge_value is None:
        edge_value = calculate_edge_value(source_id, source_type, target_id, target_type)

    return calculate_opacity(edge_value)

# Opacity bucketing functionality

def create_opacity_buckets(num_buckets: int = 10) -> List[Tuple[float, float]]:
    """
    Create opacity bucket ranges.

    Args:
        num_buckets: Number of opacity buckets to create

    Returns:
        List of tuples with (min_value, max_value) for each bucket
    """
    bucket_size = 1.0 / num_buckets
    return [(i * bucket_size, (i + 1) * bucket_size) for i in range(num_buckets)]

def get_bucket_for_value(value: float, buckets: List[Tuple[float, float]]) -> int:
    """
    Determine which bucket a value belongs to.

    Args:
        value: The node value (0.0-1.0)
        buckets: List of buckets as (min_value, max_value) tuples

    Returns:
        Bucket index
    """
    # Handle edge cases
    if value <= 0.0:
        return 0
    if value >= 1.0:
        return len(buckets) - 1

    # Find the appropriate bucket
    for i, (min_val, max_val) in enumerate(buckets):
        if min_val <= value < max_val:
            return i

    # Fallback to the last bucket if we somehow missed it
    return len(buckets) - 1

def get_bucket_opacity(bucket_index: int, buckets: List[Tuple[float, float]]) -> float:
    """
    Get the opacity value for a specific bucket.

    Args:
        bucket_index: Index of the bucket
        buckets: List of buckets as (min_value, max_value) tuples

    Returns:
        The opacity value (average of min and max for the bucket)
    """
    min_val, max_val = buckets[bucket_index]
    # Use the midpoint of the bucket for the opacity
    value = (min_val + max_val) / 2
    return calculate_opacity(value)

def group_nodes_by_opacity(
    node_ids: List[str],
    node_type: str,
    num_buckets: int = 10
) -> Dict[int, List[str]]:
    """
    Group nodes into opacity buckets for visualization.

    Args:
        node_ids: List of node IDs to group
        node_type: Type of nodes ('gene', 'phenotype', 'diagnostic')
        num_buckets: Number of opacity buckets to use

    Returns:
        Dictionary mapping bucket indices to lists of node IDs
    """
    # Create buckets
    buckets = create_opacity_buckets(num_buckets)

    # Group nodes by bucket
    grouped_nodes = {i: [] for i in range(num_buckets)}

    for node_id in node_ids:
        # Get the node value
        value = get_node_value(node_id, node_type)

        # Determine which bucket it belongs to
        bucket_index = get_bucket_for_value(value, buckets)

        # Add to the appropriate bucket
        grouped_nodes[bucket_index].append(node_id)

    # Remove empty buckets
    return {k: v for k, v in grouped_nodes.items() if v}

def clear_gene_data(gene_list: List[str]) -> None:
    """
    Clear data for specific genes from the database.

    Args:
        gene_list: List of gene IDs to clear
    """
    if not gene_list:
        return

    # Call the database function to clear the data
    clear_session_data(gene_list)