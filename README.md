# Actions Vocabulary v4 - CCO-Aligned Ontology
**Current Version**: 4.0.0 (Current)
**Namespace**: `https://clearhead.us/vocab/actions/v4#`
**Status**: Current

## What is This?

The Actions Vocabulary provides a **formal semantic foundation** for personal task management, built as a **minimal extension** to the [Common Core Ontologies (CCO)](https://github.com/CommonCoreOntology/CommonCoreOntologies).

**Design Philosophy:** Use CCO classes directly. Only create custom classes for genuinely novel concepts.

## Core Concepts

We use three CCO classes directly (no wrapper classes):

| Concept | CCO Class | IRI | What It Represents |
|---------|-----------|-----|-------------------|
| **Plan** | Plan | `cco:ont00000974` | Task definition / template |
| **Planned Act** | Planned Act | `cco:ont00000228` | Actual execution (one per occurrence) |
| **Objective** | Objective | `cco:ont00000476` | Desired outcome / project |

### The Plan / Planned Act Distinction

This is the key BFO insight: **information vs. occurrence**.

- A **Plan** is a *continuant* — information content that persists and can be realized multiple times
- A **Planned Act** is an *occurrent* — something that unfolds through time

**Example:** "Do laundry weekly" is one Plan. Each week you do laundry, that's a separate Planned Act prescribed by that Plan. For non-recurring tasks, there's still one Plan and one Planned Act — the phase (completion status) lives on the Planned Act.

### Custom Extension: ActPhase

CCO lacks lifecycle phase tracking. We add one class:

```
ActPhase (subclass of bfo:Quality)
├── NotStarted  [ ]
├── InProgress  [-]
├── Completed   [x]
├── Blocked     [=]
└── Cancelled   [_]
```

**Why BFO Quality?** A phase is a property that inheres in its bearer (the Planned Act). It's not a separate entity.

### Custom Properties

| Property | Domain | Range | Purpose |
|----------|--------|-------|---------|
| `hasPhase` | Planned Act | ActPhase | Current lifecycle state |
| `hasObjective` | Plan | Objective | Links task to project |
| `partOf` | Plan | Plan | Task hierarchy |
| `prescribes` | Plan | Planned Act | Links definition to execution |

## Why This Design?

Many domain ontologies create "wrapper classes" around upper ontology concepts:

```turtle
# Undisciplined (what we're NOT doing)
:ActionPlan rdfs:subClassOf cco:Plan .
:PlannedAction rdfs:subClassOf cco:PlannedAct .
```

This creates classes with no differentiating axioms. Problems:
1. Reduces interoperability with other CCO systems
2. Adds maintenance burden
3. Violates ontology discipline (subclasses should have distinct axioms)

Instead, we use CCO directly and add value through custom properties and SHACL constraints.

## Version History

- **v4.0.0** (Development) - Minimal CCO extension
  - Uses CCO classes directly (Plan, Planned Act, Objective)
  - Only custom class: ActPhase
  - See: [V4_DESIGN.md](./V4_DESIGN.md)

- **v3.1.0** (Previous) - BFO/CCO-aligned with wrapper classes
  - Location: `actions-vocabulary.owl`
  - Had custom ActionPlan, ActionProcess classes

- **v2** (Legacy) - Schema.org-based
  - Location: `v2/` directory

## Documentation

- **[V4_DESIGN.md](./V4_DESIGN.md)** - Full v4 design rationale
- **[V4_DESIGN_EXPLORATION.md](./V4_DESIGN_EXPLORATION.md)** - Design exploration and alternatives
- **[CLAUDE.md](./CLAUDE.md)** - Development guide
- **[BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md)** - Technical mapping to BFO/CCO
- **[v4/actions-shapes-v4.ttl](./v4/actions-shapes-v4.ttl)** - SHACL validation shapes
- **[v4/actions.context.json](./v4/actions.context.json)** - JSON-LD context map
- **[v4/actions.schema.json](./v4/actions.schema.json)** - JSON Schema for ontology-out exports

## Quick Start

### Local Development
```bash
# Python 3.12+ with uv package manager
uv sync

# Run validation tests
uv run pytest -v
```

### Visual Exploration
```bash
# Open in Protégé ontology editor
# File → Open → actions-vocabulary.owl
# Reasoner → HermiT → Start reasoner
```

## Tooling

### Recommended Tools
- **[Protégé](https://protege.stanford.edu/)** - Visual ontology editor with HermiT reasoner
- **[owlready2](https://owlready2.readthedocs.io/)** - Python library for OWL ontologies
- **[pySHACL](https://github.com/RDFLib/pySHACL)** - SHACL constraint validation (future)
- **Text Editors** - OWL/XML editing with understanding (VS Code, Neovim, etc.)

## Contributing

When making changes:

1. **Understand BFO/CCO** - Review BFO_CCO_ALIGNMENT.md for design patterns
2. **Test thoroughly** - Run validation suite and HermiT reasoner
3. **Document decisions** - Update relevant .md files with architectural choices

## License

See [LICENSE](./LICENSE)

## Support

- Issues: GitHub issue tracker
- Documentation: See [CLAUDE.md](./CLAUDE.md) for comprehensive development guide
- v2 Support: See [v2/README.md](./v2/README.md) for legacy version
