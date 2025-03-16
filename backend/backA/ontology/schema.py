"""
Schema definitions for the GenoPhenoPath ontology.

This module defines the ontology structure including main entity classes (Gene, Phenotype, 
Diagnostic) and their relationships.

Functions in this module are used in:
- backend.backA.knowledge_graph.builder: For initializing the knowledge graph
- backend.backA.knowledge_graph.nodes: For creating ontology entity instances
"""

import owlready2 as owl
from typing import Any

def create_ontology_schema() -> Any:
    """
    Create a new ontology with defined class structure for the knowledge graph.
    
    Returns:
        Ontology instance with defined classes and relationships
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
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
    
    return onto