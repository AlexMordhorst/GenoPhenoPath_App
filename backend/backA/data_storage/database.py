"""
Database module for the GenoPhenoPath application.

This module handles the SQLite database connection, schema creation, and provides
basic database operations for storing and retrieving node and edge values.

Functions in this module are used in:
- backend.backA.knowledge_graph.builder: For storing node values during graph creation
- backend.backB.visualization.plotter: For retrieving values during visualization
"""

import os
import sqlite3
from typing import Dict, Any, Optional, List, Tuple

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                      'Data', 'node_values.db')

def get_connection():
    """
    Get a connection to the SQLite database.
    
    Returns:
        SQLite connection object
    """
    # Ensure the Data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn

def create_schema():
    """
    Create the database schema if it doesn't exist.
    
    This function creates the following tables:
    - node_values: Stores values for each node (gene, phenotype, diagnostic)
    - edge_values: Stores values for edges between nodes
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create node_values table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS node_values (
        node_id TEXT PRIMARY KEY,
        node_type TEXT NOT NULL,
        value REAL DEFAULT 0.5,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create edge_values table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS edge_values (
        source_id TEXT,
        target_id TEXT,
        value REAL DEFAULT 0.5,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (source_id, target_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_node_value(node_id: str, node_type: str) -> float:
    """
    Get the value for a node. If the node doesn't exist in the database,
    a default value based on node type is returned.
    
    Args:
        node_id: The ID of the node
        node_type: The type of node ('gene', 'phenotype', 'diagnostic')
        
    Returns:
        The node value (0.0-1.0)
    """
    # Default values based on node type
    default_values = {
        'gene': 1.0,
        'phenotype': 0.5,
        'diagnostic': 0.0
    }
    
    # Get default value based on node type
    default_value = default_values.get(node_type.lower(), 0.5)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try to get the value from the database
    cursor.execute('SELECT value FROM node_values WHERE node_id = ?', (node_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    else:
        # If node doesn't exist in the database, create it with the default value
        set_node_value(node_id, node_type, default_value)
        return default_value

def set_node_value(node_id: str, node_type: str, value: float) -> None:
    """
    Set the value for a node. If the node already exists, its value is updated.
    
    Args:
        node_id: The ID of the node
        node_type: The type of node ('gene', 'phenotype', 'diagnostic')
        value: The value to set (0.0-1.0)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert or replace the node value
    cursor.execute('''
    INSERT OR REPLACE INTO node_values (node_id, node_type, value, last_updated)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (node_id, node_type.lower(), max(0.0, min(1.0, value))))
    
    conn.commit()
    conn.close()

def get_edge_value(source_id: str, target_id: str) -> float:
    """
    Get the value for an edge. If the edge doesn't exist in the database,
    a default value calculated from the connected nodes is returned.
    
    Args:
        source_id: The ID of the source node
        target_id: The ID of the target node
        
    Returns:
        The edge value (0.0-1.0)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try to get the value from the database
    cursor.execute('SELECT value FROM edge_values WHERE source_id = ? AND target_id = ?', 
                  (source_id, target_id))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    else:
        # If the edge doesn't exist, return None to trigger default calculation
        return None

def set_edge_value(source_id: str, target_id: str, value: float) -> None:
    """
    Set the value for an edge. If the edge already exists, its value is updated.
    
    Args:
        source_id: The ID of the source node
        target_id: The ID of the target node
        value: The value to set (0.0-1.0)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert or replace the edge value
    cursor.execute('''
    INSERT OR REPLACE INTO edge_values (source_id, target_id, value, last_updated)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (source_id, target_id, max(0.0, min(1.0, value))))
    
    conn.commit()
    conn.close()

def calculate_edge_value(source_id: str, source_type: str, target_id: str, target_type: str) -> float:
    """
    Calculate the value for an edge based on the values of the connected nodes.
    
    Args:
        source_id: The ID of the source node
        source_type: The type of the source node
        target_id: The ID of the target node
        target_type: The type of the target node
        
    Returns:
        The calculated edge value (0.0-1.0)
    """
    # Get values for source and target nodes
    source_value = get_node_value(source_id, source_type)
    target_value = get_node_value(target_id, target_type)
    
    # Calculate the edge value as the average of the node values
    edge_value = (source_value + target_value) / 2
    
    # Store the calculated value
    set_edge_value(source_id, target_id, edge_value)
    
    return edge_value

def calculate_opacity(value: float) -> float:
    """
    Calculate the opacity based on a node or edge value.
    
    Args:
        value: The node or edge value (0.0-1.0)
        
    Returns:
        The calculated opacity (0.2-0.8)
    """
    # Linear scale from 0.2 (value=0) to 0.8 (value=1)
    return 0.2 + (value * 0.6)

def get_all_node_values() -> Dict[str, float]:
    """
    Get all node values from the database.
    
    Returns:
        Dictionary mapping node IDs to their values
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT node_id, value FROM node_values')
    results = cursor.fetchall()
    
    conn.close()
    
    # Convert to dictionary
    return {row[0]: row[1] for row in results}

def initialize_database():
    """
    Initialize the database, creating the schema if it doesn't exist.
    """
    create_schema()
    print(f"Database initialized at {DB_PATH}")

def clear_session_data(node_ids=None):
    """
    Clear specific node data from the database.

    Args:
        node_ids: Optional list of node IDs to clear. If None, keeps all data
                 (as default values will be regenerated when needed).

    This is different from a full clear - it only removes specific entries
    but keeps the default value mechanism intact.
    """
    if not node_ids:
        print("No specific nodes to clear")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Use parameterized query with placeholders for each node ID
        placeholders = ','.join(['?'] * len(node_ids))
        cursor.execute(f'DELETE FROM node_values WHERE node_id IN ({placeholders})', node_ids)

        # Also delete associated edges
        cursor.execute(f'DELETE FROM edge_values WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})',
                      node_ids + node_ids)

        conn.commit()
        print(f"Cleared data for {len(node_ids)} nodes")
    except Exception as e:
        print(f"Error clearing session data: {e}")
        conn.rollback()
    finally:
        conn.close()

# Initialize the database schema when the module is imported
initialize_database()