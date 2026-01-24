# Actions Vocabulary v4 - Design

**Status:** FINAL
**Date:** 2025-01-21
**Authors:** Darrion Burgess, Claude (AI Assistant)

---

## Philosophy

This ontology is a **minimal extension** to the Common Core Ontologies (CCO), not a wrapper around it.

**Principles:**
1. Use CCO classes directly - don't create wrapper classes with no differentiating axioms
2. Reference by IRI, don't import - keeps the ontology self-contained and portable
3. Add only what CCO lacks - in our case, lifecycle phase tracking
4. Let the file format handle syntax - the ontology provides semantic grounding, not application logic

**Grounding:** BFO is a realist ontology. We model *information artifacts* (recorded commitments), not mental states (intentions). This aligns with what a data system can actually capture.

---

## Core Concepts

We use three CCO classes directly:

| Our Term | CCO Class | IRI | What It Represents |
|----------|-----------|-----|-------------------|
| **Action** | Plan | ont00000974 | Task definition / template |
| **Action Instance** | Planned Act | ont00000228 | Actual execution (one per occurrence) |
| **Project** | Objective | ont00000476 | Desired outcome / story |

### Why These Map Directly

**Plan = Action definition**
When you write `[ ] Buy groceries`, you're creating a Plan - information that prescribes an act. The Plan is the template; it can produce multiple executions (for recurring actions).

**Planned Act = Action instance**
When you actually buy groceries, that's a Planned Act - an occurrence prescribed by the Plan. For recurring actions, one Plan → many Planned Acts.

**Objective = Project/Story**
The `*` marker in the file format points to an Objective - a desired end state that Plans work toward.

---

## Custom Extension

CCO lacks lifecycle phase tracking. We add one class:

### ActPhase

```
ActPhase (subclass of bfo:Quality)
├── NotStarted  [ ]
├── InProgress  [-]
├── Completed   [x]
├── Blocked     [=]
└── Cancelled   [_]
```

**Why BFO Quality?** A phase is a property that inheres in its bearer (the Planned Act). It's not a separate entity - it's a characteristic of the execution.

---

## Properties

### Custom (2)

| Property | Domain | Range | Purpose |
|----------|--------|-------|---------|
| `hasPhase` | Planned Act | ActPhase | Current lifecycle state (functional) |
| `hasObjective` | Plan | Objective | Links to parent project/story |

### Reused from BFO/CCO

| Property | Source | Purpose |
|----------|--------|---------|
| `has_part` | BFO | Plan hierarchy (parent → child actions) |
| `part_of` | BFO | Inverse of has_part |
| `prescribes` | CCO | Plan → Planned Act relationship |

---

## File Format Mapping

| File Format | Ontology |
|-------------|----------|
| `[ ]`, `[-]`, `[x]`, `[=]`, `[_]` | ActPhase individuals |
| `*project/path` | hasObjective → Objective |
| `> [ ] child` | has_part (BFO) |
| Recurrence `R:FREQ=...` | One Plan, multiple Planned Acts |
| `@date`, `%completed`, etc. | Application layer (not in ontology) |

---

## What's NOT in the Ontology

These are handled at the file format or application layer:

- Dates/times (do-date, completed-date, created-date)
- Recurrence rules (RRULE syntax)
- Priority (Eisenhower matrix)
- Contexts/tags
- Duration
- Predecessors/dependencies
- Aliases

The ontology provides semantic grounding. The file format provides syntax. Applications provide behavior.

---

## Class Hierarchy

```
BFO
├── Quality (BFO_0000019)
│   └── ActPhase ◄────────────────── CUSTOM
│       ├── NotStarted
│       ├── InProgress
│       ├── Completed
│       ├── Blocked
│       └── Cancelled
│
CCO
├── Directive ICE (ont00000965)
│   ├── Plan (ont00000974) ◄──────── Action definitions
│   └── Objective (ont00000476) ◄─── Projects/stories
│
├── Act (ont00000832)
│   └── Planned Act (ont00000228) ◄─ Action instances
```

---

## Import Strategy

**Reference, don't import.**

We declare CCO/BFO classes and properties with labels and comments so the ontology is self-documenting. We don't use `owl:imports` because:

1. Keeps the ontology portable (no external dependencies at load time)
2. Avoids pulling in CCO's full axiom set
3. Reader can understand the ontology without opening CCO

Each referenced class includes:
- `rdfs:label` - human-readable name
- `rdfs:comment` - what it means + how we use it
- `rdfs:isDefinedBy` - pointer to source ontology

---

## Design Exploration

For the full exploration of design alternatives and rationale, see `V4_DESIGN_EXPLORATION.md`. That document traces the evolution from wrapper classes to this minimal approach.

---

## Summary

| Metric | Count |
|--------|-------|
| Custom classes | 1 |
| Custom properties | 2 |
| Named individuals | 5 |
| CCO classes referenced | 5 |
| BFO classes referenced | 1 |
| BFO/CCO properties referenced | 3 |

The ontology is small because CCO already did the hard work. We're extending, not rebuilding.
