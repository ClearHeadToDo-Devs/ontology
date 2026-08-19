# Ontology-Out Contract (v4.5.0)

This document defines the canonical compacted JSON-LD contract for ontology-out exports.

## Canonical Scope

The canonical seam includes:

1. `Charter`
2. `Plan`
3. `Action`
4. `Objective`
5. `Context`
6. `ContextType`

This shape is graph-derived, deterministic, and stable for downstream consumers.

Context is first-class in the canonical ontology-out contract.

`ContextType` remains optional in payloads while type taxonomy stabilizes.

## Canonical Node Fields

### Shared

- `id`
- `type`
- `name`
- `description`

### Charter

- `subCharters`
- `inServiceOf`
- `charterState`

### Plan

- `partOf`
- `actions`
- `isSuccessorOf`
- `inServiceOf`
- `requiresContext`
- `uuid`
- `alias`
- `priority`
- `sequentialChildren`
- `recurrence`
- `dueRecurrence`
- `createdDate`

### Action

- `status`
- `scheduledAt`
- `dueDate`
- `completedDate`
- `durationMinutes`
- `externalScheduleId` (optional)
- `externalOccurrenceKey` (optional)

### Objective

- `name`
- `description`

### Context

- `contextIdentifier` (required)
- `contextType` (optional)
- `contextBroader` (optional)
- `contextNarrower` (optional)

### ContextType

- `name`
- `description`

## Notes

1. Scheduling and due semantics are act-level (`scheduledAt`, `dueDate`), not plan-level.
2. Recurrence semantics are plan-level (`recurrence`, optional `dueRecurrence`) and anchor into acts via scheduled instances.
3. `subCharters` is preferred over generic `hasPart` for charter hierarchy.
4. Context hierarchy is canonical and represented via `contextBroader` / `contextNarrower`.
5. Context typing is supported but optional while type catalog semantics are still evolving.
6. External schedule linkage is optional and source-agnostic: `externalScheduleId` (series) and `externalOccurrenceKey` (instance).
7. `charterState` is a `@vocab` term over distinct charter-lifecycle individuals (`CharterNew`, `CharterActive`, `CharterBlocked`, `CharterClosed`, `CharterCancelled`), parallel to Action `status` but never sharing individuals with it.
8. Relations are published in a single canonical direction; derivable inverses are omitted. In particular `prescribes` (Plan → Action) is published while its inverse `prescribed_by` (ont00001920) is not.
9. A Plan's originating template is not published. A template today is only a filename resolved at expansion time, with no stable identity. If templates ever become referenceable entities, the natural model is a Prescriptive ICE (ont00000965) subclass that a Plan relates to via a "derived-from" predicate — not a bare string.

## Example

See `examples/v4/valid/ontology-out.jsonld` for canonical compacted structure.
