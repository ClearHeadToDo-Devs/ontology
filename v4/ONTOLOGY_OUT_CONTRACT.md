# Ontology-Out Contract (v4.3.0)

This document defines the canonical compacted JSON-LD contract for ontology-out exports.

## Canonical Scope

The canonical seam includes only:

1. `Charter`
2. `Plan`
3. `PlannedAct`
4. `Objective`

This shape is graph-derived, deterministic, and stable for downstream consumers.

## Deferred Scope

`Context` and `ContextType` are intentionally deferred from the canonical export for now.

Rationale:

1. Context is modeled in ontology source, but not yet first-class in core export semantics.
2. Deferring avoids over-promising support at the contract seam.
3. We can add context later as an explicit contract revision.

## Canonical Node Fields

### Shared

- `id`
- `type`
- `name`
- `description`

### Charter

- `subCharters`
- `inServiceOf`

### Plan

- `partOf`
- `plannedActs`
- `isSuccessorOf`
- `inServiceOf`
- `uuid`
- `alias`
- `priority`
- `sequentialChildren`
- `recurrence`
- `dueRecurrence`
- `createdDate`

### PlannedAct

- `status`
- `scheduledAt`
- `dueDate`
- `completedDate`
- `durationMinutes`

### Objective

- `name`
- `description`

## Notes

1. Scheduling and due semantics are act-level (`scheduledAt`, `dueDate`), not plan-level.
2. Recurrence semantics are plan-level (`recurrence`, optional `dueRecurrence`) and anchor into acts via scheduled instances.
3. `subCharters` is preferred over generic `hasPart` for charter hierarchy.

## Example

See `examples/v4/valid/ontology-out.jsonld` for canonical compacted structure.
