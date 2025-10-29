# Actions Vocabulary v3 - Development Guide

## Context

This is a higher order repo with several other repositories as git submodules.

For a large intro please see [the README](./README.md)

### Repository Structure

This repository uses a **consolidated v3.1.0 layout**:

```
/
├── # V3.1.0 ONTOLOGY (consolidated, production-ready)
├── actions-vocabulary.owl          # Complete v3.1.0 ontology (OWL/XML)
│                                   # Includes: Core + Context + Workflow + Roles
├── imports/                        # BFO/CCO ontologies
│   ├── bfo.owl
│   ├── cco-event.owl
│   └── cco-information.owl
├── tests/                          # Validation tests
│   └── test_poc.py
├── BFO_CCO_ALIGNMENT.md           # v3 architecture docs
├── SCHEMA_ORG_ALIGNMENT.md
├── PHASE2_DESIGN.md               # Extension design rationale
├── PHASE2_IMPLEMENTATION.md       # Implementation details
│
├── # SHARED RESOURCES
├── docs/, examples/, schemas/      # Shared across versions
├── scripts/                        # Shared tooling
├── DEPLOYMENT.md                  # Deployment guide
│
├── # V2 LEGACY
├── v2/                            # Legacy v2 ontology
│   ├── actions-vocabulary.ttl
│   ├── actions-shapes.ttl
│   └── tests/                     # v2 test suite
│
├── # BACKUPS
├── ontology-backup-modular/       # Previous modular v3.0.0-poc structure
│
└── migrations/                     # Version migration docs
    └── V2_TO_V3_MIGRATION.md
```

## Version Status

**Current: v3.1.0** (Consolidated BFO/CCO-aligned ontology)
- **Location:** Root directory (`actions-vocabulary.owl`)
- **Status:** Production-ready, consolidated
- **Format:** OWL/XML
- **Architecture:** BFO 2.0 + CCO compliant formal ontology
- **Contents:** Core + Context extension + Workflow extension + Role integration (all in one file)
- **Use for:** All new development, semantic web integration, production deployments

**Archived: v3.0.0-poc** (Modular POC with separate extensions)
- **Location:** `ontology-backup-modular/`
- **Status:** Superseded by v3.1.0
- **Note:** Separated into core + 3 extension files (now consolidated)

**Legacy: v2** (Schema.org-based pragmatic ontology)
- **Location:** `v2/` directory
- **Status:** Stable, archived
- **Format:** Turtle (TTL)
- **Architecture:** Pragmatic Schema.org-based design
- **Use for:** Existing integrations requiring v2

See [migrations/V2_TO_V3_MIGRATION.md](./migrations/V2_TO_V3_MIGRATION.md) for migration guide.

## Running Components

All submodules have their own README files - please review before doing any work to ensure proper context:

- **ontology** (this repo) - Python project managed through `uv`, generates JSON schemas from ontologies and SHACL shapes
- **tree-sitter-actions** - JavaScript project for generating tree-sitter parser
- **clearhead-cli** - Rust CLI that uses the first two projects

## How It Is Used

The vocabulary is primarily imported into Protégé ontology editor to get the structure right.

We also use code editors (neovim/VSCode) to edit the ontology by hand for structured edits.

**For v3:** OWL/XML format is preferred for Protégé compatibility and industry standards.

## Testing

### v3.1.0 Tests
```bash
# Run v3.1.0 validation (consolidated ontology)
uv run python tests/test_poc.py

# Expected results:
# ✅ 12 classes loaded (core + extensions)
# ✅ 20 properties defined (core + extensions)
# ✅ Logically consistent (HermiT reasoner)
# ✅ ~229 RDF triples
```

### v2 Tests (Legacy)
```bash
cd v2
uv run pytest
```

Check `pyproject.toml` for additional commands.

## v3 Architecture Principles

### Semantic Web Design Philosophy

#### BFO First, Schema.org Second
- **Primary alignment:** BFO/CCO for formal rigor
- **Secondary alignment:** SKOS mapping to Schema.org for web benefits
- **Continuant vs Occurrent:** Separate information (plans) from processes (executions)
- **Reuse CCO Patterns:** Extend proven CCO patterns (Plan, IntentionalAct) before creating custom classes
- **SKOS for Cross-Ontology:** Use `skos:closeMatch` for Schema.org alignment, not `rdfs:subClassOf`
- **Document Decisions:** Record architectural decisions in dedicated markdown files

See [BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md) for detailed technical mapping.

### OWL vs SHACL Boundaries (Future)

When SHACL shapes are added to v3:

**OWL Responsibilities (Logical Domain Model)**
- Class hierarchy and relationships - what CAN exist
- Disjointness declarations - mutually exclusive classes
- Domain/range restrictions - semantic constraints
- Functional properties - single-valued properties
- Schema.org alignment via SKOS

**SHACL Responsibilities (Data Quality Validation)**
- Required fields and cardinality - what MUST exist
- Value constraints - ranges, patterns, formats
- Business rules - complex validation via SPARQL
- Non-functional cardinality
- Temporal logic

**Key Rule:** Avoid Redundancy
- Don't duplicate `owl:FunctionalProperty` with `sh:maxCount 1`
- Let OWL handle logical constraints, let SHACL handle data validation

### Testing Strategy

**Current (POC Phase):**
1. Python validation script (`tests/test_poc.py`)
2. Protégé + HermiT reasoner validation

**Future (Full v3):**
1. **OWL Reasoning Tests** - Ontology satisfiability, class disjointness, property correctness
2. **SHACL Validation Tests** - Data quality constraints, business rules

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
- **Code Generation:** Schemas and classes generated from semantic definitions
- **Interoperability:** Consistent data exchange between implementations
- **Testing:** Unified validation across all tools
- **Evolution:** Backward-compatible extensions

## Key Files

### v3.1.0 Files (Current at Root)
- **README.md** - Project overview and quick start
- **CLAUDE.md** - This file (development guide for AI & humans)
- **actions-vocabulary.owl** - Consolidated v3.1.0 ontology (OWL/XML)
  - Includes: Core + Context + Workflow + Roles (all integrated)
- **BFO_CCO_ALIGNMENT.md** - Technical BFO/CCO mapping
- **SCHEMA_ORG_ALIGNMENT.md** - Schema.org integration strategy
- **PHASE2_DESIGN.md** - Extension design rationale
- **PHASE2_IMPLEMENTATION.md** - Extension implementation details
- **DEPLOYMENT.md** - Vocabulary hosting and deployment guide
- **tests/test_poc.py** - Validation script
- **imports/** - BFO and CCO ontology files

### Shared Files
- **docs/** - Additional documentation
- **examples/** - Example data
- **schemas/** - Generated schemas
- **scripts/** - Tooling scripts

### Archived Files
- **ontology-backup-modular/** - Previous v3.0.0-poc modular structure
  - actions-vocabulary.owl (core only)
  - actions-context.owl
  - actions-roles.owl
  - actions-workflow.owl

### v2 Files (Legacy in v2/ directory)
- **v2/README.md** - v2 concepts and usage
- **v2/CLAUDE.md** - v2 development guide
- **v2/ONTOLOGY.md** - v2 semantic documentation
- **v2/actions-vocabulary.ttl** - v2 ontology
- **v2/actions-shapes.ttl** - v2 SHACL constraints
- **v2/tests/** - v2 test suite

## Which Version to Work On?

**Work on v3.1.0 (root) for:**
- All new development (core + extensions consolidated)
- BFO compliance and semantic web integrations
- Production deployments
- New projects and features
- Bug fixes and improvements

The consolidated v3.1.0 ontology is now the single source of truth.

**Work on v2 (v2/ directory) only if:**
- Maintaining existing v2 deployments
- Supporting legacy integrations
- Cannot migrate to v3 yet

## Common Pitfalls for Future Development

### 🚫 Avoid These Mistakes

1. **Mixing upper ontologies** - Don't use both `rdfs:subClassOf cco:ont00000965` and `rdfs:subClassOf schema:Action`
2. **State on plans** - Plans don't have state, processes do
3. **Forgetting reasoner validation** - Always run HermiT after OWL changes
4. **Unclear property names** - Use `hasDoDate`, not just `date`
5. **Missing namespace declarations** - Always declare prefixes
6. **Using non-existent CCO classes** - CCO doesn't have a `Plan` class; use `DirectiveInformationContentEntity` (ont00000965)

### ✅ Follow These Patterns

1. **Use SKOS for Schema.org alignment** - `skos:closeMatch schema:Action`, not `rdfs:subClassOf`
2. **Separate plans from processes** - Information vs occurrents
3. **Test both layers** - Syntax validation + reasoning
4. **Update documentation** - Always sync markdown files with changes
5. **Validate frequently** - `uv run python tests/test_poc.py`

## Integration Guidelines

### For Future AI Assistants

- **Always read documentation first** - README.md, BFO_CCO_ALIGNMENT.md, SCHEMA_ORG_ALIGNMENT.md
- **Understand version structure** - Root = v3, v2/ = legacy
- **Check existing tests** before making changes
- **Run validation after modifications** - Python tests + HermiT reasoner
- **Consider BFO/CCO alignment** for any new classes/properties
- **Use SKOS for Schema.org** - Not class hierarchy mixing

### For Human Developers

- **Use Protégé for visual exploration** of the ontology structure
- **Start with documentation** - BFO_CCO_ALIGNMENT.md explains design decisions
- **Leverage testing framework** to validate changes
- **Reference v2 for comparison** - See how concepts evolved
- **Join BFO/CCO community** for broader context

## Common Tasks

### Validate v3.1.0 Ontology
```bash
uv run python tests/test_poc.py

# Expected: 12 classes, 20 properties, ~229 triples
# All tests should pass (logically consistent)
```

### Edit v3.1.0 Ontology
```bash
# Option 1: Protégé (recommended)
# - Open actions-vocabulary.owl
# - Make changes visually
# - Run HermiT reasoner to check consistency
# - Save
# - Run: uv run python tests/test_poc.py

# Option 2: Direct OWL/XML editing
# - Edit actions-vocabulary.owl (use your editor)
# - Validate: uv run python tests/test_poc.py
# - Check reasoning in Protégé if making structural changes
```

### Work on v2 (Legacy - rarely needed)
```bash
cd v2
# Edit actions-vocabulary.ttl or actions-shapes.ttl
uv run pytest
```

### Generate Schemas (Future)
```bash
# When schema generation is fully implemented for v3.1.0
uv run invoke generate-schemas
```

## Decision History & Rationales

### Why BFO/CCO for v3?
- **Scientific Rigor:** ISO standard ontology framework
- **Interoperability:** 450+ ontologies use BFO as upper ontology
- **Clear Semantics:** Formal distinctions (continuant/occurrent)
- **Long-term Maintainability:** Proven patterns from CCO

### Why Separate Plans from Processes?
- **Recurring Actions:** One plan → multiple executions
- **Reality vs Intention:** Execution can diverge from plan
- **BFO Compliance:** Aligns with continuant/occurrent distinction
- **Clear Semantics:** Information (persistent) vs events (temporal)

### Why SKOS for Schema.org?
- **Avoid Upper Ontology Conflicts:** BFO and Schema.org have different philosophies
- **Preserve Benefits:** Still get SEO/web advantages via SKOS alignment
- **Clean Separation:** Formal semantics (BFO) + pragmatic mapping (Schema.org)

See [SCHEMA_ORG_ALIGNMENT.md](./SCHEMA_ORG_ALIGNMENT.md) for full details.

## Resources

### BFO/CCO Resources
- **BFO Specification:** http://basic-formal-ontology.org/
- **CCO Repository:** https://github.com/CommonCoreOntology/CommonCoreOntologies
- **NCOR Resources:** https://ontology.buffalo.edu/

### Tools
- **Protégé:** https://protege.stanford.edu/
- **owlready2 docs:** https://owlready2.readthedocs.io/
- **SKOS Primer:** https://www.w3.org/TR/skos-primer/

### Our Docs
- [README.md](./README.md) - User guide
- [BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md) - Technical mapping
- [SCHEMA_ORG_ALIGNMENT.md](./SCHEMA_ORG_ALIGNMENT.md) - Web integration
- [migrations/V2_TO_V3_MIGRATION.md](./migrations/V2_TO_V3_MIGRATION.md) - Migration guide
- [v2/ONTOLOGY.md](./v2/ONTOLOGY.md) - v2 semantic documentation
