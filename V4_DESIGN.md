# V4 Design: CCO Extension for Intention Information Entities

**Version**: 4.1.0
**Date**: 2026-02-07
**Status**: Current

## Overview

The Actions Vocabulary v4 is a **CCO Extension for Intention Information Entities** — a small, disciplined extension to the [Common Core Ontologies](https://github.com/CommonCoreOntology/CommonCoreOntologies) that fills genuine gaps in modeling intentional planning and execution.

Rather than wrapping CCO concepts in domain-specific classes, v4 **reuses CCO directly** and adds only what CCO lacks: a Charter class for declaring scope of directed concern, and an `inServiceOf` property for teleological linkage.

## Design Principles

1. **Reuse CCO directly** — don't subclass without differentiating axioms
2. **Fill genuine gaps** — only add what CCO provably lacks
3. **SHACL for data quality** — use shapes for application-level constraints, not OWL axioms
4. **Separate information from process** — Plans are continuants, Planned Acts are occurrents

## The Directive ICE Family

All three core classes are siblings under CCO's `Directive Information Content Entity` (ont00000965):

```
Directive ICE (CCO ont00000965)
├── Charter (actions:Charter)     — declares scope of directed concern
├── Plan (CCO ont00000974)        — prescribes intended acts
└── Objective (CCO ont00000476)   — prescribes desired states
```

### Charter (NEW — `actions:Charter`)

A **Charter** is a Directive ICE that declares the scope of directed concern for an agent or organization. It answers "what domain am I responsible for?" without prescribing specific acts or outcomes.

**Why Charter is a genuine extension:**
- CCO has Plan (prescribes acts) and Objective (prescribes states)
- CCO lacks a class for "scope declarations" — the boundary that contains Plans and Objectives
- A Charter is not a Plan (it doesn't prescribe acts) and not an Objective (it doesn't prescribe a target state)
- Example: "Health & Fitness" is a Charter — it declares a domain of concern. "Run a marathon" is an Objective within that Charter. "Run 3x/week" is a Plan serving that Objective.

### Plan (CCO ont00000974)

A Directive ICE that prescribes some set of intended Intentional Acts. Used directly from CCO — represents task definitions/templates.

### Objective (CCO ont00000476)

A Directive ICE that prescribes some projected state of affairs. Used directly from CCO — represents projects/desired outcomes.

## The Charter → Plan → PlannedAct Pipeline

```
Charter (Scope)
  └─ contains ─→ Plan (Prescription)     [via bfo:part_of]
                   ├─ inServiceOf ─→ Objective (Outcome)
                   └─ prescribes ──→ Planned Act (Execution)  [via cco:prescribes]
                                      └─ measured by ─→ Event Status  [via cco:is_measured_by_nominal]
```

This pipeline models the full lifecycle:
1. **Scope**: A Charter declares what matters ("Health & Fitness")
2. **Prescription**: Plans within the Charter prescribe acts ("Run 3x/week")
3. **Teleology**: Plans serve Objectives via `inServiceOf` ("Complete a marathon")
4. **Execution**: Plans produce Planned Acts via `prescribes` (each run session)
5. **Status**: Planned Acts are measured by Event Status Nominal ICEs (NotStarted, InProgress, Completed, etc.)

## Event Status: Why ActPhase Was Removed

**Previous (v4.0.0):** `ActPhase` was a custom class subclassing BFO Quality, with individuals like NotStarted, InProgress, Completed.

**Problem:** CCO already solves this. `Event Status Nominal ICE` (ont00000203) is an Information Content Entity "whose referent is the status of a process" with values like "proposed, approved, planned, in progress, completed, failed, or successful."

**Resolution:** The status individuals (NotStarted, InProgress, Completed, Blocked, Cancelled) are now typed as `cco:ont00000203` (Event Status Nominal ICE), and linked to Planned Acts via CCO's `is_measured_by_nominal` (ont00001868, inverse of ont00000293's measurement relation).

This is better because:
- Status is information *about* a process, not a quality *of* a process
- CCO's measurement pattern is the standard way to associate nominal values with entities
- Other CCO-aligned systems can interpret our status values without domain-specific knowledge

## `inServiceOf`: The Genuine CCO Gap

**Previous (v4.0.0):** `hasObjective` — named the range in the property (anti-pattern in ontology design).

**Problem:** CCO lacks a general teleological relation connecting a Directive ICE to the Objective it serves. `prescribes` connects to acts, not outcomes. There is no CCO property for "this Plan exists in service of that Objective."

**Resolution:** `inServiceOf` is a custom property with domain `Directive ICE` and range `Objective`. It fills a genuine gap: the teleological relation between any directive entity and the objective it works toward.

This is better because:
- Property names should not encode the range type
- Domain is Directive ICE (not just Plan), so Charters can also serve Objectives
- "In service of" captures the teleological nature of the relationship

## `is_successor_of`: Replacing `dependsOn`

**Previous (v4.0.0):** `dependsOn` — a custom property for plan ordering.

**Resolution:** CCO has `is_successor_of` (ont00001775) and its inverse `is_predecessor_of` (ont00001928) for temporal ordering. While CCO's domain is technically Independent Continuant (BFO_0000004) and Plans are GDCs (Generically Dependent Continuants), this is pragmatic reuse — SHACL constrains the domain to Plans at the data validation layer.

## Plan Containment: `part_of` for Charter → Plan

Plans are contained within Charters via BFO's `part_of` (BFO_0000050). This is natural: a Plan is part of the Charter that scopes it. No custom property needed.

## What's CCO Reuse vs. Genuine Extension

### CCO Reuse (by reference)
| Entity | CCO IRI | Role |
|--------|---------|------|
| Directive ICE | ont00000965 | Parent class |
| Plan | ont00000974 | Task definitions |
| Objective | ont00000476 | Desired outcomes |
| Planned Act | ont00000228 | Task executions |
| Act | ont00000832 | Parent of Planned Act |
| Event Status Nominal ICE | ont00000203 | Status values |
| prescribes | ont00001942 | Plan → Planned Act |
| is_measured_by_nominal | ont00001868 | Planned Act → Status |
| is_successor_of | ont00001775 | Plan ordering |
| has_part / part_of | BFO_0000051/50 | Hierarchy |
| has datetime value | ont00001767 | Temporal base property |

### Genuine Extensions
| Entity | IRI | Rationale |
|--------|-----|-----------|
| **Charter** | actions:Charter | No CCO class for scope-of-concern declarations |
| **inServiceOf** | actions:inServiceOf | No CCO teleological relation to Objectives |

### Application-Level Additions
These are pragmatic additions for the .actions file format, not ontological claims:

| Entity | Notes |
|--------|-------|
| Context / ContextType | GTD execution contexts (facility, agent, tool, category) |
| Status individuals | NotStarted, InProgress, Completed, Blocked, Cancelled |
| Temporal sub-properties | hasDoDateTime, hasCompletedDateTime, hasCreatedDateTime |
| Data properties | hasUUID, hasAlias, hasPriority, hasDurationMinutes, hasRecurrenceRule, hasSequentialChildren |
| Context properties | requiresContext, hasContextType, contextBroader/Narrower, hasContextIdentifier |

## Version History

- **4.1.0** — Charter class, inServiceOf property, Event Status Nominal ICE, is_successor_of
- **4.0.0** — Initial minimal CCO extension (ActPhase, hasObjective, hasPhase, dependsOn)
