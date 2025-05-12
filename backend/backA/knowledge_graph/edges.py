"""
Edge creation for the GenoPhenoPath knowledge graph.

This module handles the creation of relationships between entities (Gene-Phenotype and 
Phenotype-Diagnostic) in the ontology based on the loaded data.

Functions in this module are used in:
- backend.backA.knowledge_graph.builder: For building the complete knowledge graph
"""

from typing import Any, Dict
import pandas as pd

def create_gene_phenotype_relations(onto: Any, gene_phenotype_data: pd.DataFrame) -> None:
    """
    Establish gene-to-phenotype relationships in the ontology.
    
    Args:
        onto: Ontology instance with defined classes and nodes
        gene_phenotype_data: DataFrame containing gene-phenotype mappings
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    # Handle empty dataframe case
    if gene_phenotype_data.empty:
        print("DEBUG - No gene-phenotype relations to create")
        return
        
    # Important: Get all existing nodes first to avoid creating duplicates
    try:
        # Pre-cache existing gene entities
        gene_entities = {}
        for gene_entity in onto.Gene.instances():
            gene_name = str(gene_entity).removeprefix("onto.")
            gene_entities[gene_name] = gene_entity
            
        # Pre-cache existing phenotype entities
        phenotype_entities = {}
        for phenotype_entity in onto.Phenotype.instances():
            phenotype_id = str(phenotype_entity).removeprefix("onto.")
            phenotype_entities[phenotype_id] = phenotype_entity
            
        print(f"DEBUG - Cached {len(gene_entities)} genes and {len(phenotype_entities)} phenotypes")
    except Exception as e:
        print(f"WARNING - Failed to pre-cache entities: {e}")
        # Continue with the original approach if caching fails
        gene_entities = {}
        phenotype_entities = {}
    
    # Make sure the dataframe is sorted by gene symbol for proper grouping
    gene_phenotype_data = gene_phenotype_data.sort_values('gene_symbol')
    
    # Group phenotypes by gene and establish connections
    gene_considered = gene_phenotype_data.iloc[0]["gene_symbol"]  # Start with first gene
    phen_list = []  # Initialize list to collect phenotypes for current gene
    
    for index, entry in gene_phenotype_data.iterrows():
        # Get phenotype entity - use cached version if available
        phenotype_id = entry["hpo_id"]
        if phenotype_id in phenotype_entities:
            phenotype_entity = phenotype_entities[phenotype_id]
        else:
            # Try to find the entity first before creating a new one
            try:
                # Look for existing entity to avoid duplicate creation
                phenotype_entity = next(iter(onto.search(iri="*" + phenotype_id)), None)
                if phenotype_entity:
                    phenotype_entities[phenotype_id] = phenotype_entity
                else:
                    # Create new entity if needed
                    phenotype_entity = onto.Phenotype(phenotype_id)
                    phenotype_entities[phenotype_id] = phenotype_entity
            except Exception as e:
                print(f"WARNING - Error handling phenotype {phenotype_id}: {e}")
                continue
        
        if gene_considered == entry["gene_symbol"]:
            # Add phenotype to the current gene's list
            phen_list.append(phenotype_entity)
        elif gene_considered != entry["gene_symbol"]:  # Use != instead of 'is not'
            # Get gene entity - use cached version if available
            if gene_considered in gene_entities:
                gene_entity = gene_entities[gene_considered]
            else:
                # Try to find the entity first before creating a new one
                try:
                    gene_entity = next(iter(onto.search(iri="*" + gene_considered)), None)
                    if gene_entity:
                        gene_entities[gene_considered] = gene_entity
                    else:
                        gene_entity = onto.Gene(gene_considered)
                        gene_entities[gene_considered] = gene_entity
                except Exception as e:
                    print(f"WARNING - Error handling gene {gene_considered}: {e}")
                    # Reset for next gene
                    phen_list = []
                    gene_considered = entry["gene_symbol"]
                    continue
            
            # When we encounter a new gene, connect the previous gene to all its phenotypes
            try:
                # Connect the gene to phenotypes
                gene_entity.ConnectedTo = phen_list
            except Exception as e:
                print(f"WARNING - Error connecting gene {gene_considered} to phenotypes: {e}")
            
            # Reset for next gene
            phen_list = []
            gene_considered = entry["gene_symbol"]
            phen_list.append(phenotype_entity)
    
    # Don't forget to connect the last gene to its phenotypes
    if phen_list:
        try:
            # Get gene entity for the last gene
            if gene_considered in gene_entities:
                gene_entity = gene_entities[gene_considered]
            else:
                gene_entity = next(iter(onto.search(iri="*" + gene_considered)), None)
                if not gene_entity:
                    gene_entity = onto.Gene(gene_considered)
            
            # Connect the last gene
            gene_entity.ConnectedTo = phen_list
        except Exception as e:
            print(f"WARNING - Error connecting last gene {gene_considered} to phenotypes: {e}")

def create_phenotype_diagnostic_relations(onto: Any, diagnostic_data: pd.DataFrame) -> None:
    """
    Establish phenotype-to-diagnostic relationships in the ontology.
    
    Args:
        onto: Ontology instance with defined classes and nodes
        diagnostic_data: DataFrame containing phenotype-diagnostic mappings
        
    Used in:
    - backend.backA.knowledge_graph.builder.build_knowledge_graph
    """
    # Handle empty dataframe case
    if diagnostic_data.empty:
        print("DEBUG - No phenotype-diagnostic relations to create")
        return
        
    # Important: Get all existing nodes first to avoid creating duplicates
    try:
        # Pre-cache existing phenotype entities
        phenotype_entities = {}
        for phenotype_entity in onto.Phenotype.instances():
            phenotype_id = str(phenotype_entity).removeprefix("onto.")
            phenotype_entities[phenotype_id] = phenotype_entity
            
        # Pre-cache existing diagnostic entities
        diagnostic_entities = {}
        for diagnostic_entity in onto.Diagnostic.instances():
            diagnostic_id = str(diagnostic_entity).removeprefix("onto.")
            diagnostic_entities[diagnostic_id] = diagnostic_entity
            
        print(f"DEBUG - Cached {len(phenotype_entities)} phenotypes and {len(diagnostic_entities)} diagnostics")
    except Exception as e:
        print(f"WARNING - Failed to pre-cache entities: {e}")
        # Continue with the original approach if caching fails
        phenotype_entities = {}
        diagnostic_entities = {}
    
    # Make sure the dataframe is sorted by phenotype ID for proper grouping
    diagnostic_data = diagnostic_data.sort_values('hpo_id')
    
    # Group diagnostics by phenotype and establish connections
    phen_considered = diagnostic_data.iloc[0]["hpo_id"]  # Start with first phenotype
    diag_list = []  # Initialize list to collect diagnostics for current phenotype
    
    for index, entry in diagnostic_data.iterrows():
        # Get diagnostic entity - use cached version if available
        diagnostic_id = entry["maxo_label"]
        if diagnostic_id in diagnostic_entities:
            diagnostic_entity = diagnostic_entities[diagnostic_id]
        else:
            # Try to find the entity first before creating a new one
            try:
                # Look for existing entity to avoid duplicate creation
                diagnostic_entity = next(iter(onto.search(iri="*" + diagnostic_id)), None)
                if diagnostic_entity:
                    diagnostic_entities[diagnostic_id] = diagnostic_entity
                else:
                    # Create new entity if needed
                    diagnostic_entity = onto.Diagnostic(diagnostic_id)
                    diagnostic_entities[diagnostic_id] = diagnostic_entity
            except Exception as e:
                print(f"WARNING - Error handling diagnostic {diagnostic_id}: {e}")
                continue
                
        if phen_considered == entry["hpo_id"]:
            # Add diagnostic to the current phenotype's list
            diag_list.append(diagnostic_entity)
        elif phen_considered != entry["hpo_id"]:  # Use != instead of 'is not'
            # Get phenotype entity - use cached version if available
            if phen_considered in phenotype_entities:
                phenotype_entity = phenotype_entities[phen_considered]
            else:
                # Try to find the entity first before creating a new one
                try:
                    phenotype_entity = next(iter(onto.search(iri="*" + phen_considered)), None)
                    if phenotype_entity:
                        phenotype_entities[phen_considered] = phenotype_entity
                    else:
                        phenotype_entity = onto.Phenotype(phen_considered)
                        phenotype_entities[phen_considered] = phenotype_entity
                except Exception as e:
                    print(f"WARNING - Error handling phenotype {phen_considered}: {e}")
                    # Reset for next phenotype
                    diag_list = []
                    phen_considered = entry["hpo_id"]
                    continue
            
            # When we encounter a new phenotype, connect the previous phenotype to all its diagnostics
            try:
                # Connect the phenotype to diagnostics
                phenotype_entity.ConnectedTo = diag_list
            except Exception as e:
                print(f"WARNING - Error connecting phenotype {phen_considered} to diagnostics: {e}")
            
            # Reset for next phenotype
            diag_list = []
            phen_considered = entry["hpo_id"]
            diag_list.append(diagnostic_entity)
    
    # Don't forget to connect the last phenotype to its diagnostics
    if diag_list:
        try:
            # Get phenotype entity for the last phenotype
            if phen_considered in phenotype_entities:
                phenotype_entity = phenotype_entities[phen_considered]
            else:
                phenotype_entity = next(iter(onto.search(iri="*" + phen_considered)), None)
                if not phenotype_entity:
                    phenotype_entity = onto.Phenotype(phen_considered)
            
            # Connect the last phenotype
            phenotype_entity.ConnectedTo = diag_list
        except Exception as e:
            print(f"WARNING - Error connecting last phenotype {phen_considered} to diagnostics: {e}")