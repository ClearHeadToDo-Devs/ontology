# Actions Vocabulary v2 (Legacy)

> **⚠️ NOTICE:** This is the **legacy v2 version** of the Actions Vocabulary.
> **For new development**, see the [v3 ontology at the root directory](../README.md).
> **Migration guide:** [V2_TO_V3_MIGRATION.md](../migrations/V2_TO_V3_MIGRATION.md)

**Version:** 2.1.0
**Status:** Stable, production-ready (archived)
**Format:** Turtle (TTL)
**Architecture:** Pragmatic Schema.org-based design

This version is maintained for existing production systems and stable integrations. New projects should use v3.

---

# Vocabulary Introduction
As part of the clearhead platform, we want to build out a foundation that is both logically sound while also conforming to exsting standards.

To this end, we are going to be using the ontology defined within this repository our core foundation upon which all applications can be built

## Documentation

 - **[SCHEMA_GENERATION.md](./SCHEMA_GENERATION.md)** - JSON Schema generation from OWL + SHACL
 - **[LESSONS_LEARNED.md](./LESSONS_LEARNED.md)** - Development insights and technical guidance

## Usage

This ontology provides W3C-compliant RDF/OWL vocabulary and SHACL constraints for task management systems.

### Schema Generation ("Small Waist" Architecture)

Generate JSON Schema files from your OWL ontology + SHACL shapes for use in APIs, databases, and applications:

```bash
# Generate JSON schemas from ontology
uv run invoke generate-schemas

# Test schemas with example data
uv run invoke test-examples

# Run complete pipeline (validate → generate → test)
uv run invoke full-pipeline
```

**Generated artifacts:**
- `schemas/action.schema.json` - Base Action class schema
- `schemas/rootaction.schema.json` - Root-level action schema  
- `schemas/childaction.schema.json` - Child action schema
- `schemas/leafaction.schema.json` - Leaf action schema
- `schemas/actions-combined.schema.json` - Combined schema with `$defs`

See `examples/` directory for valid data examples and integration guides.

### Validation (Downstream Consumers)

```bash
# Install dependencies
uv sync

# Run all validation tests (recommended)
uv run pytest

# Quick syntax validation
uv run invoke validate

# Clean artifacts
uv run invoke clean

# See all available tasks
uv run invoke --list
```

### Integration

Your downstream applications should:

1. Parse `actions-vocabulary.ttl` for class/property definitions
2. Use `actions-shapes.ttl` for validation rules  
3. Run `uv run invoke test` to validate your data against these constraints

### Files

- `actions-vocabulary.ttl` - Core ontology (OWL 2)
- `actions-shapes.ttl` - SHACL constraints  
- `tests/` - Validation test suite with example data
- `tasks.py` - Invoke task definitions

## Terms
For now we are working primarily with Actions which are a generic format that is intended to express an intent to complete something as either an individual or a system

**For detailed semantic definitions, see [ONTOLOGY.md](./ONTOLOGY.md).**

The vocabulary extends the [Schema.org Action Class](https://schema.org/Action) with:
- Hierarchical task organization (6-level depth structure)
- GTD-style context tags for environmental requirements  
- Project/story organization for root actions
- Dual temporal model (do-date scheduling + due-date deadlines)
- iCalendar-compatible recurrence patterns
- Extended state management beyond simple completion

# Purpose
The purpose of this repo works at many levels:
- **Semantic Foundation**: Provides the definitive semantic model for task management concepts, serving as the authoritative reference for domain understanding
- **Implementation Guide**: Enables implementors to build consistent tooling including:
  - File format parsers and serializers
  - Database schemas and migrations  
  - API data models and validation
  - Application class structures and types
  - Search and analytics systems

**The ontology maintains implementation flexibility while ensuring semantic consistency across all tools and platforms.**

## Architecture
This vocabulary serves as the "small waist" of the platform - a minimal, stable interface that enables:
- **Code Generation**: Automated schema and class generation from semantic definitions
- **Interoperability**: Consistent data exchange between different implementations  
- **Testing**: Unified validation and compliance testing across tools
- **Evolution**: Backward-compatible extensions as requirements grow

**For detailed class definitions, property specifications, and usage examples, see [ONTOLOGY.md](./ONTOLOGY.md).**

# Tooling
## Recommended Tools
- **[Protégé](https://protege.stanford.edu/)** - GUI ontology editor for visual exploration and editing
- **[pySHACL](https://github.com/RDFLib/pySHACL)** - Python library for SHACL constraint validation
- **Text Editors** - Direct TTL editing with syntax highlighting (VS Code, Neovim, etc.)

The included test suite validates both positive and negative cases against the SHACL constraints, providing practical examples of valid and invalid data structures.
