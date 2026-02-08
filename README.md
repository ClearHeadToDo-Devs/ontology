# CCO Extension for Intention Information Entities
**Current Version**: 4.1.0 (Current)
**Namespace**: `https://clearhead.us/vocab/actions/v4#`
**Status**: Current

## What is This?

The Actions Vocabulary v4 is a **CCO Extension for Intention Information Entities** — a disciplined extension to the [Common Core Ontologies (CCO)](https://github.com/CommonCoreOntology/CommonCoreOntologies) that fills genuine gaps in modeling intentional planning and execution.

**Design Philosophy:** Reuse CCO directly. Only add what CCO provably lacks.

## Core Concepts

The core is three CCO Directive ICE siblings:

```
Directive ICE (CCO ont00000965)
├── Charter (actions:Charter)     — declares scope of directed concern
├── Plan (CCO ont00000974)        — prescribes intended acts
└── Objective (CCO ont00000476)   — prescribes desired states
```

| Concept | Class | IRI | What It Represents |
|---------|-------|-----|-------------------|
| **Charter** | Charter | `actions:Charter` | Scope of directed concern |
| **Plan** | Plan (CCO) | `cco:ont00000974` | Task definition / template |
| **Planned Act** | Planned Act (CCO) | `cco:ont00000228` | Actual execution (one per occurrence) |
| **Objective** | Objective (CCO) | `cco:ont00000476` | Desired outcome / project |

### The Charter → Plan → PlannedAct Pipeline

```
Charter (Scope) → Plan (Prescription) → Planned Act (Execution)
                   └── inServiceOf → Objective (Outcome)
```

- A **Charter** declares a domain of concern ("Health & Fitness")
- **Plans** within a Charter prescribe acts ("Run 3x/week")
- Plans serve **Objectives** via `inServiceOf` ("Complete a marathon")
- Plans produce **Planned Acts** via `prescribes` (each run session)
- Planned Acts have status via `is_measured_by_nominal` (NotStarted, InProgress, etc.)

### Status Tracking: Event Status Nominal ICE

CCO's `Event Status Nominal ICE` (ont00000203) models process status. Our status individuals:

```
Event Status Nominal ICE (CCO ont00000203)
├── NotStarted  [ ]
├── InProgress  [-]
├── Completed   [x]
├── Blocked     [=]
└── Cancelled   [_]
```

### Genuine Extensions (what CCO lacks)

| Entity | IRI | Rationale |
|--------|-----|-----------|
| **Charter** | `actions:Charter` | No CCO class for scope-of-concern declarations |
| **inServiceOf** | `actions:inServiceOf` | No CCO teleological relation to Objectives |

### Key Properties

| Property | Source | Domain → Range | Purpose |
|----------|--------|----------------|---------|
| `inServiceOf` | Custom | Directive ICE → Objective | Teleological linkage |
| `is_measured_by_nominal` | CCO | Planned Act → Event Status | Status tracking |
| `is_successor_of` | CCO | Plan → Plan | Dependency ordering |
| `prescribes` | CCO | Plan → Planned Act | Links definition to execution |
| `part_of` | BFO | Plan → Plan/Charter | Hierarchy |

## Why This Design?

Most domain ontologies wrap upper ontology concepts in unnecessary subclasses. We don't. Instead, we reuse CCO directly and add only what CCO provably lacks: Charter (scope declarations) and `inServiceOf` (teleological relation). Everything else is CCO by reference.

See **[V4_DESIGN.md](./V4_DESIGN.md)** for the full design rationale.

## Version History

- **v4.1.0** (Current) - CCO Extension for Intention Information Entities
  - Added Charter class, `inServiceOf` property
  - Replaced ActPhase with CCO Event Status Nominal ICE
  - Replaced `hasObjective` with `inServiceOf`, `hasPhase` with `is_measured_by_nominal`, `dependsOn` with `is_successor_of`
  - See: [V4_DESIGN.md](./V4_DESIGN.md)

- **v4.0.0** (Previous) - Minimal CCO extension
  - Uses CCO classes directly (Plan, Planned Act, Objective)
  - Custom class: ActPhase (now replaced)

- **v3.1.0** (Previous) - BFO/CCO-aligned with wrapper classes
  - Location: `actions-vocabulary.owl`
  - Had custom ActionPlan, ActionProcess classes

- **v2** (Legacy) - Schema.org-based
  - Location: `v2/` directory

## Documentation

- **[V4_DESIGN.md](./V4_DESIGN.md)** - Full v4 design rationale
- **[V4_DESIGN_EXPLORATION.md](./V4_DESIGN_EXPLORATION.md)** - Design exploration and alternatives (historical)
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
