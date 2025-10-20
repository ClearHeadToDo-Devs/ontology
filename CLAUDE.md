# Purpose
We are building an ontology that will guide development of an open data format platform where common data classes can be leveraged by different stakeholders to build applications

## How it is used
The vocabulary will be primarily imported into protege ontology editor to get the structure right

we are also using our code editor (neovim in our example) to edit the ontology by hand so feel free to use that to review and make structured edits

# Overview
We are using OWL 2 with a scoping for a productivity app

the intention is that we will use this ontology as well as the SHACL structure to generate scaffolding such as:
- tree sitter parsers
- database schemas
- data schema for json
- class generation on static typing languages

to this point we are trying to capture semantic meaning here while also importing enough context that the implementors can take this work one at a time

## Key Files
- README.md covers the concepts in a plaintext format
- actions-vocabulary.ttl is the ontology itself and is the primary unit of work
- action-shapes.ttl is a SHACL file that actually holds the complimentary SHACL constraints needed to function properly

# Testing
This is a typical python project built using `uv` so for testing you simply need to run: `uv run pytest`

check `pyproject.toml` for secondary commands with more granular control or which utilize CLI commands

# Architecture Principles

## Semantic Web Design Philosophy
- **Schema.org First**: Always check Schema.org for existing properties before creating custom ones
- **Inheritance over Equivalence**: Use `rdfs:subPropertyOf` rather than `owl:equivalentProperty` when extending existing vocabularies
- **Property Reuse**: Leverage inherited properties (`schema:name`, `schema:description`) rather than duplicating

## OWL vs SHACL Boundaries

### OWL Responsibilities (Logical Domain Model)
- **Class hierarchy and relationships** - what CAN exist in the domain
- **Disjointness declarations** - mutually exclusive classes  
- **Domain/range restrictions** - semantic constraints
- **Functional properties** - single-valued properties declared at ontology level
- **Schema.org alignment** - semantic relationships via `rdfs:subPropertyOf`
- **OWL restrictions** - class definitions via property constraints

### SHACL Responsibilities (Data Quality Validation)  
- **Required fields and cardinality** - what MUST exist in valid data
- **Value constraints** - ranges, patterns, formats (e.g., UUID v7, priority 1-4)
- **Business rules** - complex validation via SPARQL constraints
- **Non-functional cardinality** - `maxCount` where OWL doesn't declare functional
- **Temporal logic** - date consistency, completion vs deadline validation

### Key Rule: Avoid Redundancy
- **Don't duplicate** `owl:FunctionalProperty` with `sh:maxCount 1`  
- **Do use** SHACL `maxCount` for properties that aren't OWL functional (like `schema:name`)
- **Let OWL handle** logical domain constraints, **let SHACL handle** data validation

## Testing Strategy

### Two-Layer Testing Approach
1. **OWL Reasoning Tests** (`test_owl_reasoning.py`)
   - Ontology satisfiability and logical consistency
   - Class disjointness verification  
   - Property domain/range correctness
   - Schema.org alignment validation
   - Functional property declarations

2. **SHACL Validation Tests** (`test_shacl_validation.py`)
   - Data quality constraints
   - Business rule enforcement
   - Value format validation
   - Required field verification

## "Small Waist" Architecture

This ontology serves as the **minimal stable interface** between different implementations:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Parsers  │    │  Web APIs       │    │   Databases     │
│   (tree-sitter) │    │  (JSON Schema)  │    │   (SQL DDL)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   Actions Ontology       │
                    │   (Semantic Truth)       │  
                    └──────────────────────────┘
```

**Benefits:**
- **Code Generation**: Schemas and classes generated from semantic definitions
- **Interoperability**: Consistent data exchange between implementations
- **Testing**: Unified validation across all tools  
- **Evolution**: Backward-compatible extensions as requirements grow

## File Relationships

### Core Semantic Layer
- **`actions-vocabulary.ttl`** - OWL ontology defining the logical domain model
- **`actions-shapes.ttl`** - SHACL constraints for data validation  
- **`ONTOLOGY.md`** - Comprehensive semantic documentation (THE authoritative reference)

### Documentation Layer  
- **`README.md`** - Project overview and usage instructions
- **`CLAUDE.md`** - AI/human collaboration context (this file)

### Implementation Layer
- **File format specs** - Syntax and parsing rules (separate repos)
- **Generated schemas** - Database, JSON, etc. (downstream artifacts)

### Testing Layer
- **`tests/test_owl_reasoning.py`** - Ontological consistency 
- **`tests/test_shacl_validation.py`** - Data quality validation
- **`tests/data/`** - Valid and invalid test cases

## Decision History & Rationales

### Why Schema.org Alignment?
- **SEO Benefits**: Search engines understand Schema.org properties
- **Tool Compatibility**: Existing semantic web tools work out of the box
- **Standards Compliance**: Leverages W3C recommended practices
- **Avoid Reinvention**: Don't create custom properties when standard ones exist

### Why Dual Temporal Model?
- **`doDate/Time`** - When you plan to work on it (scheduling)
- **`dueDate/Time`** - When it must be completed (deadline) 
- **`completedDateTime`** - When it was actually finished (tracking)
- **All connected to `schema:startTime/endTime`** for semantic consistency

### Why Hierarchical Structure?
- **GTD Compatibility**: Supports Getting Things Done methodology
- **Project Management**: Natural breakdown of complex work
- **6-Level Limit**: Prevents over-nesting while supporting realistic depth
- **Clear Roles**: Root (can have projects), Child (intermediate), Leaf (terminal)

## Common Pitfalls for Future Development

### 🚫 **Avoid These Mistakes**
1. **Creating custom properties** without checking Schema.org first
2. **Using `owl:equivalentProperty`** instead of `rdfs:subPropertyOf` for extensions  
3. **Duplicating cardinality** in both OWL (functional) and SHACL (maxCount)
4. **Mixing logical constraints in SHACL** that belong in OWL
5. **Missing namespace declarations** in test data (don't forget `@prefix schema:`)

### ✅ **Follow These Patterns**
1. **Check inheritance chain**: Thing → Action → actions:Action gets you name, description, etc.
2. **Use proper boundaries**: OWL for CAN exist, SHACL for SHOULD exist
3. **Test both layers**: OWL reasoning + SHACL validation  
4. **Update documentation**: Always sync ONTOLOGY.md with ontology changes
5. **Validate frequently**: `uv run invoke validate` catches syntax errors early

## Integration Guidelines

### For Future AI Assistants
- **Always read ONTOLOGY.md first** - it's the definitive semantic reference
- **Check existing tests** before making changes to understand expected behavior  
- **Run both test suites** after modifications: OWL reasoning + SHACL validation
- **Consider Schema.org alignment** for any new properties
- **Understand the "small waist" concept** - this ontology serves multiple downstream implementations

### For Human Developers  
- **Use Protégé for visual exploration** of the ontology structure
- **Reference file format specs separately** - don't confuse syntax with semantics
- **Start with ONTOLOGY.md** to understand domain concepts before diving into TTL files
- **Leverage the testing framework** to validate changes against real use cases
