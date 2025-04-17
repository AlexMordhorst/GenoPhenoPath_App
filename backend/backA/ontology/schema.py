"""
Schema definitions for the GenoPhenoPath ontology.

This module defines the ontology structure including main entity classes (Gene, Phenotype, 
Diagnostic) and their relationships.

Functions in this module are used in:
- backend.backA.knowledge_graph.builder: For initializing the knowledge graph
- backend.backA.knowledge_graph.nodes: For creating ontology entity instances
"""

import owlready2 as owl
from typing import Any, Optional

# Store a global reference to the ontology
_GLOBAL_ONTOLOGY = None

def create_ontology_schema() -> Any:
    """
    Create a new ontology with defined class structure for the knowledge graph.
    
    Returns:
        Ontology instance with defined classes and relationships
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    global _GLOBAL_ONTOLOGY
    
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
    
    # Store the ontology globally
    _GLOBAL_ONTOLOGY = onto
    
    return onto

def clear_ontology(onto: Optional[Any] = None) -> None:
    """
    Clear all instances from the ontology while preserving the class structure.
    
    This function removes all individual entities (instances) from the ontology
    but keeps the class definitions intact, effectively resetting the knowledge graph.
    
    Args:
        onto: Optional ontology instance to clear. If None, uses the global ontology.
        
    Used in:
    - frontend.frontB.app.main: For resetting the knowledge graph when returning to landing page
    """
    global _GLOBAL_ONTOLOGY
    
    # Use the global ontology if none is provided
    if onto is None:
        onto = _GLOBAL_ONTOLOGY
    
    if onto is None:
        # No ontology exists yet
        return
    
    print(f"DEBUG - Clearing ontology: removing {len(list(onto.individuals()))} individuals")
    
    # Get all instances (individuals) in the ontology
    individuals = list(onto.individuals())
    
    # Destroy each individual
    for individual in individuals:
        # Remove all properties first
        for prop in list(individual.get_properties()):
            prop[individual] = []
        
        # Destroy the individual
        try:
            owl.destroy_entity(individual)
        except Exception as e:
            print(f"Warning: Failed to destroy entity {individual}: {e}")
    
    # Force garbage collection
    import gc
    gc.collect()
    
    print(f"DEBUG - Ontology cleared: {len(list(onto.individuals()))} individuals remaining")