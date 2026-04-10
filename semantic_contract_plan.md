# Semantic Contract Plan

This note is the ontology-side companion to `clearhead-core/.clearhead/semantic_export_plan.md`.

## Current State

Recent alignment work brought the source ontology, examples, generated site, and core graph behavior closer together.

The main semantic decisions now reflected across the repo are:

1. use upstream CCO "Prescriptive Information Content Entity" language where appropriate
2. keep objective linkage at the charter level for now
3. treat duration as `PlannedAct` data, not `Plan` data
4. use `cco:is_successor_of` for dependency ordering
5. use `actions:hasRecurrenceRule` for recurrence semantics
6. treat recurrence as anchored by scheduled acts, not by plan-level do-date metadata alone

## What Still Needs To Be Settled

Before JSON-LD becomes the real semantic seam for the CLI and future integrations, we still need to tighten three things.

### 1. Canonical Ontology-Out JSON-LD Shape

We should define one compacted JSON-LD contract that is:

1. graph-derived
2. deterministic
3. pleasant for downstream code to consume
4. honest about what is supported now versus deferred

This should be documented with sample payloads, not inferred from serializer output.

### 2. Explicit Context Deferral

Contexts are real ontology concepts, but core does not model them as first-class nodes yet.

Until that changes, the ontology-out contract should explicitly say whether contexts are:

1. omitted from the canonical export
2. partially represented in a clearly provisional way

The important rule is to avoid over-promising support.

### 3. Validation Scope

The ontology and the core validation subset should agree on the semantics we claim to support in practice.

The next validation pass should focus on:

1. successor-cycle checks
2. recurrence anchor requirements
3. UUID and alias constraints
4. completed-act date requirements
5. sequential-children boolean semantics

## Source Of Truth Reminder

`site/` is generated from source via `tasks.py`.

That means ontology edits should be made in:

1. `v4/actions-vocabulary.owl`
2. `v4/actions-shapes-v4.ttl`
3. `v4/actions.context.json`
4. `v4/actions.schema.json`
5. `examples/v4/valid/*`

Then regenerate the published artifacts with:

```bash
uv run invoke build-site
```

## Intended Next Order

1. document the canonical ontology-out JSON-LD shape
2. make context deferral explicit in docs/examples/schema
3. expand core validation to match the supported ontology semantics
4. build JSON-LD export in core against that contract

At that point, display work can safely consume the semantic export instead of inventing a parallel representation layer.
