# Actions Vocabulary v3 - BFO/CCO-Aligned Ontology

**Current Version**: 3.0 (Development)
**Namespace**: `https://vocab.clearhead.io/actions/`
**Status**: Active development, POC validated

## What is This?

The Actions Vocabulary provides a **formal semantic foundation** for task management systems, combining:

- **BFO 2.0 Compliance** - ISO standard upper ontology (ISO/IEC 21838-2:2021)
- **CCO Integration** - Common Core Ontologies mid-level framework
- **Schema.org Alignment** - SKOS-mapped for web/SEO benefits
- **Practical Tooling** - JSON Schema generation for APIs, databases, and applications

This ontology serves as the **"small waist" architecture** - a minimal, semantically rigorous interface that enables scientific-grade reasoning while supporting practical code generation.

## Version History

- **v3** (Current) - BFO/CCO-aligned formal ontology at root level
  - Location: Root directory
  - Format: OWL/XML (`actions-vocabulary.owl`)
  - See: [BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md), [SCHEMA_ORG_ALIGNMENT.md](./SCHEMA_ORG_ALIGNMENT.md)

- **v2** (Legacy) - Schema.org-based pragmatic ontology
  - Location: `v2/` directory
  - Format: Turtle (`.ttl`)
  - See: [v2/README.md](./v2/README.md), [v2/ONTOLOGY.md](./v2/ONTOLOGY.md)
  - Migration guide: [migrations/V2_TO_V3_MIGRATION.md](./migrations/V2_TO_V3_MIGRATION.md)

## Quick Start

### Prerequisites
```bash
# Python 3.12+ with uv package manager
uv sync
```

### Validation
```bash
# Run v3 validation tests
uv run python tests/test_poc.py

# For v2 legacy tests
cd v2 && uv run pytest
```

### Visual Exploration
```bash
# Open in Protégé ontology editor
# File → Open → actions-vocabulary.owl
# Reasoner → HermiT → Start reasoner
```

## Key Architectural Change: Plan vs Process Separation

### v2 Model (Single Entity)
```turtle
:action1 a actions:Action ;
    schema:name "Review reports" ;
    actions:state actions:Completed .
```
❌ **Problem:** Conflates WHAT to do (plan) with HOW it was done (execution)

### v3 Model (Separation of Concerns)
```turtle
# The PLAN (information - what to do)
:review_plan a actions:ActionPlan ;
    schema:name "Review reports" ;
    actions:hasPriority 2 ;
    actions:prescribes :review_process .

# The EXECUTION (process - how it was done)
:review_process a actions:ActionProcess ;
    actions:hasState actions:Completed .
```
✅ **Benefits:**
- Plans can prescribe multiple executions (recurring actions)
- Execution can diverge from plan (reality vs intention)
- Aligns with BFO continuant/occurrent distinction
- Separates information (persistent) from events (temporal)

## Documentation

### Core Documentation
- **[BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md)** - Technical mapping to BFO/CCO
- **[SCHEMA_ORG_ALIGNMENT.md](./SCHEMA_ORG_ALIGNMENT.md)** - Schema.org integration strategy
- **[SUMMARY.md](./SUMMARY.md)** - Comprehensive v3 overview
- **[CLAUDE.md](./CLAUDE.md)** - Development guide (AI & human)

### Shared Resources
- **[docs/](./docs/)** - Shared documentation across versions
- **[examples/](./examples/)** - Example data and integration guides
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Vocabulary hosting guide

## Files Structure

```
/
├── actions-vocabulary.owl          # v3 ontology (OWL/XML)
├── imports/                        # BFO and CCO imports
├── tests/                          # v3 validation tests
├── docs/, examples/, schemas/      # Shared resources
├── v2/                             # Legacy v2 ontology
└── migrations/                     # Version migration guides
```

## Usage

### For Ontology Developers
```bash
# Edit in Protégé (recommended)
# Or edit OWL/XML directly with understanding of the format

# Validate changes
uv run python tests/test_poc.py

# Check consistency with HermiT reasoner in Protégé
```

### For Application Developers
```bash
# Generate JSON schemas (future feature)
uv run invoke generate-schemas

# Integrate with your application
# - Parse actions-vocabulary.owl for class/property definitions
# - Use generated JSON schemas for data validation
# - See examples/ for integration patterns
```

## Why v3?

v2 was a **pragmatic Schema.org-based design** that served production needs well. v3 is a **complete architectural redesign** for:

1. **Formal Semantic Rigor** - BFO compliance enables scientific interoperability
2. **Separation of Concerns** - Plans (information) vs Processes (executions)
3. **CCO Patterns** - Reuse proven mid-level ontology patterns
4. **Broader Interoperability** - Join 450+ BFO-based ontologies
5. **Long-term Maintainability** - Clearer semantics, better reasoner support

See [migrations/V2_TO_V3_MIGRATION.md](./migrations/V2_TO_V3_MIGRATION.md) for detailed rationale and migration path.

## Tooling

### Recommended Tools
- **[Protégé](https://protege.stanford.edu/)** - Visual ontology editor with HermiT reasoner
- **[owlready2](https://owlready2.readthedocs.io/)** - Python library for OWL ontologies
- **[pySHACL](https://github.com/RDFLib/pySHACL)** - SHACL constraint validation (future)
- **Text Editors** - OWL/XML editing with understanding (VS Code, Neovim, etc.)

## Contributing

When making changes:

1. **Read the docs first** - See CLAUDE.md for development guidelines
2. **Understand BFO/CCO** - Review BFO_CCO_ALIGNMENT.md for design patterns
3. **Test thoroughly** - Run validation suite and HermiT reasoner
4. **Document decisions** - Update relevant .md files with architectural choices

## License

See [LICENSE](./LICENSE)

## Support

- Issues: GitHub issue tracker
- Documentation: See [CLAUDE.md](./CLAUDE.md) for comprehensive development guide
- v2 Support: See [v2/README.md](./v2/README.md) for legacy version
