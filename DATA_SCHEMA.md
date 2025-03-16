# GenoPhenoPath Data Schema

This document describes the data sources and formats used by the GenoPhenoPath application.

## Primary Data Sources

### 1. Genetic Variants (`vartest.tsv`)

A tab-separated file containing genetic variant information with pathogenicity scores.

**Key Columns:**
- `Chromosome`: Chromosome number where the variant is located
- `Position`: Genomic position of the variant
- `Reference bases`: Original nucleotide sequence
- `Alternative bases`: Altered nucleotide sequence
- `Gene Symbol`: Gene where the variant is located
- `Most pathogenic variant effect`: Effect type (e.g., missense_variant, stop_gained)
- `Pathogenicity Score`: Numerical score indicating likely pathogenicity
- `Protein HGVS change`: Protein-level change in HGVS notation (e.g., p.G358*)
- `Nucleotide HGVS change`: DNA-level change in HGVS notation (e.g., c.1072G>T)

**Usage in Application:**
- Filtered to include variants with Pathogenicity Score ≥ 15
- Provides the gene symbols to link to phenotypic data

### 2. Gene-Phenotype Associations (`genes_to_phenotype.txt`)

A tab-separated file mapping genes to their associated phenotypes (HPO terms).

**Columns:**
- `ncbi_gene_id`: NCBI Gene identifier (numeric)
- `gene_symbol`: Standard gene symbol (e.g., AARS1)
- `hpo_id`: Human Phenotype Ontology term ID (e.g., HP:0002460)
- `hpo_name`: Human Phenotype Ontology term name (e.g., "Distal muscle weakness")
- `frequency`: Occurrence frequency when available (e.g., "15/15" or "HP:0040283")
- `disease_id`: Associated disease identifier (e.g., OMIM:613287)

**Usage in Application:**
- Filtered to include only genes present in the variant data
- Establishes connections between genes and phenotypes in the knowledge graph

### 3. Phenotype-Diagnostic Mappings (`maxo_diagnostic_annotations2.txt`)

A tab-separated file mapping phenotypes to their relevant diagnostic procedures.

**Columns:**
- `hpo_id`: Human Phenotype Ontology term ID (e.g., HP:0003784)
- `hpo_label`: Human Phenotype Ontology term name (e.g., "Type 1 collagen overmodification")
- `predicate_id`: Relationship type (typically "is_observable_through")
- `maxo_id`: Medical Action Ontology term ID (e.g., MAXO:0000001)
- `maxo_label`: Medical Action Ontology term name (e.g., "medical action")
- `creator_id`: ORCID identifier of the mapping creator

**Usage in Application:**
- Establishes connections between phenotypes and diagnostic procedures in the knowledge graph

## Data Flow and Transformation

### Data Loading and Filtering
```python
# Load variant data
table = pd.read_csv("./Data/vartest.tsv", sep='\t')
table2 = table.iloc[:, [0,1,2,3,6,8,22,24,25,26,40]].sort_values("Pathogenicity Score", ascending=False).loc[table["Pathogenicity Score"] >= 15]

# Load diagnostic annotations
hpo2diag = pd.read_csv("./Data/maxo_diagnostic_annotations2.txt", sep='\t')

# Load gene-to-phenotype mappings and filter by genes in variant data
gene2phen = pd.read_csv("./Data/genes_to_phenotype.txt", sep='\t')
gene2phen2 = gene2phen[gene2phen["gene_symbol"].isin(table2["Gene Symbol"])]
```

### Entity Creation in the Ontology
```python
# Create Gene instances
for gene in gene2phen2sg["gene_symbol"]:
    my_new_gene = Gene(gene)

# Create Phenotype instances    
for phen in gene2phen2sp["hpo_id"]:
    my_new_phen = Phenotype(phen)

# Create Diagnostic instances
for diag in hpo2diag["maxo_label"]:
    my_new_diag = Diagnostic(diag)
```

### Relationship Establishment
```python
# Gene to Phenotype connections
Gene(gene_considered).ConnectedTo = phen_list

# Phenotype to Diagnostic connections
Phenotype(phen_considered).ConnectedTo = diag_list
```

## Data Standards and Ontologies

### Human Phenotype Ontology (HPO)
- A standardized vocabulary for phenotypic abnormalities in human diseases
- HPO terms are identified by "HP:" prefixed IDs (e.g., HP:0002460)
- Used to represent phenotypic features associated with genetic variants

### Medical Action Ontology (MAXO)
- A standardized vocabulary for medical procedures and diagnostic tests
- MAXO terms are identified by "MAXO:" prefixed IDs (e.g., MAXO:0000001)
- Used to represent diagnostic procedures that can detect specific phenotypes

### HUGO Gene Nomenclature Committee (HGNC)
- Standardized gene symbols used to identify human genes
- Ensures consistent gene naming conventions across the scientific community
- Used for the gene entities in the knowledge graph

## Derived Data Structures

### NetworkX DiGraph
The application converts the ontology relationships into a directed graph (DiGraph) with:
- Nodes representing genes, phenotypes, and diagnostic procedures
- Directed edges representing connections between these entities
- Node attributes including entity type and label
- Graph metrics calculated for statistical analysis

### Node Communities
Nodes are grouped into three communities for visualization:
1. `community_0`: Gene nodes (innermost sphere)
2. `community_1`: Phenotype nodes (middle sphere)
3. `community_2`: Diagnostic nodes (outermost sphere)

### Graph Statistics Dictionary
A dictionary containing calculated metrics about the graph structure:
```python
graph_stats = {
    "total_nodes": n_nodes,
    "total_edges": n_edges,
    "gene_count": len(community_0),
    "phenotype_count": len(community_1),
    "diagnostic_count": len(community_2),
    "gene_to_pheno_edges": gene_to_pheno_edge_count,
    "pheno_to_diag_edges": pheno_to_diag_edge_count,
    "avg_node_degree": avg_node_degree,
    # ... additional statistics
}
```