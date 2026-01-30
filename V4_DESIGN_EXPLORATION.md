# Actions Vocabulary v4 - Final Design

**Status:** FINAL DRAFT
**Date:** 2025-01-20
**Authors:** Darrion Burgess, Claude (AI Assistant)

---

## Design Philosophy

This ontology follows a disciplined approach: **extend CCO, don't wrap it**.

### Why This Matters

Many domain ontologies make the mistake of creating "wrapper classes" around upper ontology concepts. For example:

```turtle
# Undisciplined approach (what we're NOT doing)
:ActionPlan rdfs:subClassOf cco:Plan .
:PlannedAct rdfs:subClassOf cco:PlannedAct .
:DesiredOutcome rdfs:subClassOf cco:Objective .
```

This creates classes with no differentiating axioms - they're just renamed CCO classes. This is problematic because:

1. **Reduces interoperability** - Other CCO-based systems can't directly use your data
2. **Adds maintenance burden** - More classes to document and maintain
3. **Violates ontology discipline** - Subclasses should have axioms that don't apply to the parent
4. **Obscures semantics** - The wrapper hides that you're really just using CCO

### The Disciplined Alternative

Only create custom classes when you have **genuinely novel concepts** that CCO doesn't provide. For everything else, use CCO classes directly and add your value through:

1. **Domain-specific properties** - New relationships between CCO classes
2. **SHACL constraints** - Business rules and validation
3. **Named individuals** - Enumerated values for your domain

---

## What CCO Provides (Use Directly)

These CCO classes map perfectly to our domain. We use them directly, not as parents for wrapper classes.

| Our Concept | CCO Class | CCO IRI | CCO Definition |
|-------------|-----------|---------|----------------|
| **Task/Action** | Plan | ont00000974 | "A Directive ICE that prescribes some set of intended Intentional Acts through which some Agent expects to achieve some Objective" |
| **Execution** | Planned Act | ont00000228 | "An Act in which at least one Agent plays a causative role and which is prescribed by some Directive ICE" |
| **Project/Outcome** | Objective | ont00000476 | "A Directive ICE that prescribes some projected state that some Agent intends to achieve" |
| **Location** | Facility | ont00000192 | "A material entity designed to support some process or activity" |
| **Tool** | Artifact | ont00000001 | "A material entity designed to have a specific function" |
| **Person/Org** | Agent | ont00000374 | "A material entity that has the capability to perform actions" |
| **Role** | Role | BFO_0000023 | "A realizable entity that exists because of social norms or expectations" |

### Why These Map Directly

**Plan = Task/Action**
- GTD "next action" IS a plan - information prescribing what should be done
- A task definition IS directive information content
- No need to subclass; just instantiate cco:Plan

**Planned Act = Execution**
- When you actually do the task, that's the planned act
- The act is prescribed by the plan
- CCO's definition is exactly what we mean

**Objective = Project/Outcome**
- GTD defines project as "any outcome requiring more than one action"
- CCO Objective is "a projected state an agent intends to achieve"
- These are semantically identical

---

## What CCO Lacks (Our Extensions)

These concepts have no CCO equivalent. We create custom classes for these only.

### 1. Milestone

**Why novel:** CCO has Objective (end state) but no concept of intermediate checkpoint markers.

```turtle
:Milestone a owl:Class ;
    rdfs:subClassOf cco:ont00000965 ;  # Directive ICE
    rdfs:label "Milestone" ;
    skos:definition "A significant checkpoint that marks progress toward an objective." ;
    rdfs:comment "Milestones are sibling to Plan and Objective under Directive ICE. They mark progress but don't prescribe a final state (unlike Objective) or prescribe acts (unlike Plan)." .
```

**Semantic justification:**
- Not an Objective: Milestones mark *progress toward* objectives, they're not end states
- Not a Plan: Milestones don't prescribe acts to perform
- Novel kind of Directive ICE: Prescribes a checkpoint/marker

### 2. Energy Context

**Why novel:** CCO has Facility (location), Artifact (tools), Agent (people), but no concept of cognitive/physical energy requirements.

```turtle
:EnergyContext a owl:Class ;
    rdfs:subClassOf cco:ont00000965 ;  # Directive ICE
    rdfs:label "Energy Context" ;
    skos:definition "A directive prescribing the cognitive or physical energy level required for a plan." ;
    rdfs:comment "Based on GTD principle that energy is a constraint alongside time, location, and tools. No CCO equivalent exists." .
```

**Semantic justification:**
- GTD identifies energy as a key constraint for task selection
- "Can I do this when I'm tired?" is a real planning question
- CCO models physical resources but not human energy states

### 3. Act Phase

**Why novel:** CCO has Planned Act but no enumeration of execution phases.

```turtle
:ActPhase a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000019 ;  # Quality
    rdfs:label "Act Phase" ;
    skos:definition "A quality inhering in a planned act that describes its execution status." ;
    rdfs:comment "BFO Quality because phase is a property that inheres in the act, not a separate entity." .
```

**Semantic justification:**
- Phases are qualities of acts, not separate entities
- BFO Quality is the correct category for "a property that inheres in a bearer"
- The phase individuals (NotStarted, InProgress, etc.) are instances of this quality

---

## Named Individuals

These are enumerated values - specific instances of our custom classes.

### Act Phase Individuals

| Individual | Label | Definition | Valid Transitions |
|------------|-------|------------|-------------------|
| `:NotStarted` | "Not Started" | Act has not begun | → InProgress, Cancelled |
| `:InProgress` | "In Progress" | Act is currently being executed | → Completed, Blocked, Cancelled |
| `:Completed` | "Completed" | Act finished successfully | (terminal) |
| `:Blocked` | "Blocked" | Act cannot proceed due to external factor | → InProgress, Cancelled |
| `:Cancelled` | "Cancelled" | Act abandoned without completion | (terminal) |

### Energy Level Individuals

| Individual | Label | Definition |
|------------|-------|------------|
| `:HighEnergy` | "High Energy" | Requires full cognitive/physical capacity |
| `:MediumEnergy` | "Medium Energy" | Moderate cognitive/physical demand |
| `:LowEnergy` | "Low Energy" | Can be done when tired or distracted |

### Milestone Status Individuals

| Individual | Label | Definition |
|------------|-------|------------|
| `:Pending` | "Pending" | Milestone not yet reached |
| `:Reached` | "Reached" | Milestone has been achieved |
| `:Missed` | "Missed" | Milestone was not achieved by target date |

---

## Domain-Specific Properties

This is where most of our value lives. Properties define relationships between CCO classes and our extensions.

### Core Relationships

| Property | Domain | Range | Why Needed |
|----------|--------|-------|------------|
| `prescribes` | cco:Plan | cco:Planned Act | Subproperty of cco:prescribes with tighter domain/range |
| `hasObjective` | cco:Plan | cco:Objective | Link plans to the outcomes they work toward |
| `achieves` | cco:Planned Act | cco:Objective | Record what objectives an act achieved (post-hoc) |
| `hasPhase` | cco:Planned Act | :ActPhase | Current execution status (functional property) |
| `performedBy` | cco:Planned Act | cco:Agent | Who actually performed the act |

### Hierarchy and Dependencies

| Property | Domain | Range | Why Needed |
|----------|--------|-------|------------|
| `hasPart` | cco:Plan | cco:Plan | Subproperty of bfo:has_part for plan decomposition |
| `partOf` | cco:Plan | cco:Plan | Inverse of hasPart |
| `dependsOn` | cco:Plan | cco:Plan | Logical prerequisite (transitive) |
| `cannotStartUntil` | cco:Plan | cco:Plan | Hard constraint: must complete before |
| `blockedBy` | cco:Planned Act | bfo:Occurrent | Runtime blocking by external event |

### Context Requirements

| Property | Domain | Range | Why Needed |
|----------|--------|-------|------------|
| `requiresFacility` | cco:Plan | cco:Facility | Location context (GTD @office, @home) |
| `requiresArtifact` | cco:Plan | cco:Artifact | Tool context (GTD @computer, @phone) |
| `requiresAgent` | cco:Plan | cco:Agent | Social context (GTD @agenda) |
| `requiresEnergyContext` | cco:Plan | :EnergyContext | Energy level needed |

### Milestone Relationships

| Property | Domain | Range | Why Needed |
|----------|--------|-------|------------|
| `marksProgressToward` | :Milestone | cco:Objective | Which objective this milestone marks progress toward |
| `hasStatus` | :Milestone | :MilestoneStatus | Pending, Reached, Missed |

### Temporal Properties

| Property | Domain | Range | Why Needed |
|----------|--------|-------|------------|
| `hasDoDateTime` | cco:Plan | xsd:dateTime | When to start (prescriptive) |
| `hasDurationMinutes` | cco:Plan | xsd:positiveInteger | Estimated duration |
| `hasCompletedDateTime` | cco:Planned Act | xsd:dateTime | When act finished (descriptive) |
| `hasTargetDate` | cco:Objective | xsd:date | When to achieve by |
| `hasTargetDate` | :Milestone | xsd:date | When milestone should be reached |

### Priority

| Property | Domain | Range | Why Needed |
|----------|--------|-------|------------|
| `hasPriority` | cco:Plan | xsd:integer | Eisenhower matrix (1-4) |

**Priority values:**
- 1 = Urgent & Important (Do now)
- 2 = Important, not Urgent (Schedule)
- 3 = Urgent, not Important (Delegate)
- 4 = Neither (Delete/Defer)

### Recurrence (iCalendar RRULE pattern)

| Property | Domain | Range | Why Needed |
|----------|--------|-------|------------|
| `hasRecurrenceFrequency` | cco:Plan | xsd:string | DAILY, WEEKLY, MONTHLY, YEARLY |
| `hasRecurrenceInterval` | cco:Plan | xsd:positiveInteger | Every N periods |
| `hasRecurrenceUntil` | cco:Plan | xsd:dateTime | End date |
| `hasRecurrenceCount` | cco:Plan | xsd:positiveInteger | Max occurrences |
| `byDay` | cco:Plan | xsd:string | iCal BYDAY |
| `byMonth` | cco:Plan | xsd:string | iCal BYMONTH |
| `byMonthDay` | cco:Plan | xsd:string | iCal BYMONTHDAY |

**Why iCalendar:** Industry standard, well-understood, handles complex recurrence patterns.

---

## Class Hierarchy Summary

```
BFO / CCO (use directly)                    Actions Vocabulary v4 (extensions only)
════════════════════════                    ════════════════════════════════════════

bfo:Quality
    └── ActPhase ◄─────────────────────── NEW: Execution status quality
            ├── NotStarted (individual)
            ├── InProgress (individual)
            ├── Completed (individual)
            ├── Blocked (individual)
            └── Cancelled (individual)

cco:Directive ICE
    │
    ├── cco:Plan ◄─────────────────────── USE DIRECTLY: Task/action definitions
    │       │
    │       ├── hasPart → cco:Plan
    │       ├── hasObjective → cco:Objective
    │       ├── prescribes → cco:Planned Act
    │       ├── requiresFacility → cco:Facility
    │       ├── requiresArtifact → cco:Artifact
    │       ├── requiresAgent → cco:Agent
    │       ├── requiresEnergyContext → EnergyContext
    │       ├── hasPriority, hasDoDateTime, recurrence...
    │       └── dependsOn → cco:Plan
    │
    ├── cco:Objective ◄────────────────── USE DIRECTLY: Desired outcomes/projects
    │       └── hasTargetDate, hasResponsibleAgent...
    │
    ├── Milestone ◄────────────────────── NEW: Progress checkpoints
    │       ├── marksProgressToward → cco:Objective
    │       └── hasStatus → MilestoneStatus
    │
    └── EnergyContext ◄────────────────── NEW: Cognitive/physical energy requirement
            └── hasEnergyLevel → EnergyLevel

cco:Planned Act ◄──────────────────────── USE DIRECTLY: Actual execution
        ├── prescribedBy → cco:Plan
        ├── hasPhase → ActPhase
        ├── achieves → cco:Objective
        ├── performedBy → cco:Agent
        └── hasCompletedDateTime

cco:Facility ◄─────────────────────────── USE DIRECTLY: Location context
cco:Artifact ◄─────────────────────────── USE DIRECTLY: Tool context
cco:Agent ◄────────────────────────────── USE DIRECTLY: Social context
cco:Role ◄─────────────────────────────── USE DIRECTLY: Areas of focus
```

---

## Cardinality Decisions

| Relationship | Cardinality | Rationale |
|--------------|-------------|-----------|
| Plan → Planned Act | 1..* | At least one act created with plan (state needs somewhere to live) |
| Planned Act → Plan | 1 | Every planned act is prescribed by exactly one plan |
| Plan → Objective | 0..* | Standalone tasks have no project; some serve multiple objectives |
| Objective → Plan | 0..* | An objective might have no plans yet, or many |
| Planned Act → ActPhase | 1 | Functional property - exactly one current phase |
| Plan → hasPart | 0..* | Flat or nested hierarchy |
| Plan → dependsOn | 0..* | No dependencies or many |

### Why Plan → Planned Act is 1..*

This is a pragmatic decision:
- State (NotStarted, InProgress, etc.) lives on Planned Act, not Plan
- Plan is information (continuant); Planned Act is occurrence (occurrent)
- To track state, we need at least one Planned Act per Plan
- For recurring plans, additional Planned Acts are created per occurrence

---

## GTD Alignment

| GTD Concept | Representation | Why This Mapping |
|-------------|----------------|------------------|
| **Project** | `cco:Objective` | Both define "a desired end state" |
| **Next Action** | `cco:Plan` (with no parent) | A next action IS a plan for what to do |
| **Subtask** | `cco:Plan` (with parent) | Sub-plans related via `hasPart` |
| **Waiting For** | `cco:Planned Act` with phase Blocked | Waiting = act blocked by external factor |
| **Someday/Maybe** | `cco:Plan` with low priority or specific context | Deferred plans |
| **Context** | `requiresFacility`, `requiresArtifact`, `requiresAgent`, `requiresEnergyContext` | GTD @context = resource requirements |
| **Area of Focus** | `cco:Role` via `inRoleContext` | Areas map to roles/responsibilities |
| **Milestone** | `:Milestone` | Checkpoints toward project completion |

---

## What's NOT in the Ontology (SHACL's Job)

These are business rules, not ontological truths. They belong in SHACL:

| Constraint | Why SHACL |
|------------|-----------|
| Max hierarchy depth of 5 | Arbitrary limit, not a kind distinction |
| Priority must be 1-4 | Value constraint, not class definition |
| Completed acts can't transition back | State machine rule |
| Root plans can have projects | Relational constraint |
| Required fields (name, etc.) | Data quality, not semantics |

---

## Migration from v3

### Removed (classes that were just CCO wrappers)

| v3 Class | v4 Replacement |
|----------|----------------|
| `ActionPlan` | Use `cco:Plan` directly |
| `ActionProcess` | Use `cco:Planned Act` directly |
| `RootActionPlan` | Query: Plan with no `partOf` |
| `ChildActionPlan` | Query: Plan with `partOf` |
| `LeafActionPlan` | Query: Plan with no `hasPart` |
| `ActionContext` | Removed - use CCO directly |
| `LocationContext` | Use `cco:Facility` directly |
| `ToolContext` | Use `cco:Artifact` directly |
| `SocialContext` | Use `cco:Agent` directly |
| `Objective` / `DesiredOutcome` | Use `cco:Objective` directly |

### Renamed

| v3 | v4 | Reason |
|----|-----|--------|
| `ActionState` | `ActPhase` | "Phase" better captures temporal quality of execution |
| `hasProject` (string) | `hasObjective` (to cco:Objective) | Proper entity, not string |
| `hasState` | `hasPhase` | Consistency with class rename |

### Retained

- `Milestone` (moved to Directive ICE subclass)
- `EnergyContext` (no CCO equivalent)
- All recurrence properties
- All temporal properties
- Priority, dependency properties

---

## File Structure

```
ontology/
├── v4/actions-vocabulary.owl    # The ontology (OWL/XML)
├── actions-shapes-v4.ttl        # SHACL constraints
├── imports/
│   ├── bfo.owl                  # BFO 2.0
│   └── cco-merged.owl           # CCO (or individual modules)
└── PROPOSED_V4_DESIGN.md        # This document
```

---

## Summary: Why This Design

1. **Disciplined** - Only 3 custom classes (Milestone, EnergyContext, ActPhase), all genuinely novel
2. **Interoperable** - Direct CCO usage means other CCO systems can consume our data
3. **Simple** - Value is in properties and SHACL, not class proliferation
4. **Grounded** - Every decision traced back to BFO/CCO semantics or GTD principles
5. **Extensible** - Adding new properties is easy; the core is stable

The ontology is small because CCO already did the hard work. We're standing on their shoulders, not rebuilding the ladder.

---

---

## Implementation & Migration Plan

### Phase 0: Preparation (Prerequisites)

- [ ] **Read migration guide**: `ontology/migrations/V3_TO_V4_MIGRATION.md`
- [ ] **Backup current v3 data**
  ```bash
  cp -r ontology/v3 ontology/v3-backup-$(date +%Y%m%d)
  ```

- [ ] **Verify CCO imports work**
  - Import CCO Plan class (ont00000974) in test OWL file
  - Import CCO Objective class (ont00000476)
  - Import CCO PlannedAct class (ont00000228)
  - Import CCO DirectiveICE class (ont00000965)
  - Confirm no import errors

- [ ] **Create migration branch**
  ```bash
  git checkout -b feature/v4-transition
  ```

**References:**
- Migration Guide: `migrations/V3_TO_V4_MIGRATION.md`
- Migration Script: `migrations/v3_to_v4.py`

- [ ] **Verify CCO imports work**
  - Import CCO Plan class (ont00000974) in test OWL file
  - Import CCO Objective class (ont00000476)
  - Import CCO PlannedAct class (ont00000228)
  - Confirm no import errors

- [ ] **Create migration branch**
  ```bash
  git checkout -b feature/v4-transition
  ```

---

### Phase 1: Create v4 Ontology

#### 1.1 Core Structure

- [ ] Create `ontology/v4/actions-vocabulary.owl` with:
  - Namespace: `https://clearhead.us/vocab/actions/v4#`
  - Imports: BFO, CCO (ont00000974, ont00000476, ont00000228, ont00000965)
  - Version: 4.0.0

- [ ] Add custom class definitions:
  ```turtle
  :Milestone a owl:Class ;
      rdfs:subClassOf cco:ont00000965 ;  # Directive ICE
      rdfs:label "Milestone" ;
      skos:definition "A significant checkpoint that marks progress toward an objective." .
  
  :EnergyContext a owl:Class ;
      rdfs:subClassOf cco:ont00000965 ;
      rdfs:label "Energy Context" ;
      skos:definition "A directive prescribing the cognitive or physical energy level required for a plan." .
  
  :ActPhase a owl:Class ;
      rdfs:subClassOf bfo:BFO_0000019 ;  # Quality
      rdfs:label "Act Phase" ;
      skos:definition "A quality inhering in a planned act that describes its execution status." .
  ```

- [ ] Add named individuals:
  ```turtle
  # Act Phase Individuals
  :NotStarted a :ActPhase, owl:NamedIndividual ;
      rdfs:label "Not Started" .
  :InProgress a :ActPhase, owl:NamedIndividual ;
      rdfs:label "In Progress" .
  :Completed a :ActPhase, owl:NamedIndividual ;
      rdfs:label "Completed" .
  :Blocked a :ActPhase, owl:NamedIndividual ;
      rdfs:label "Blocked" .
  :Cancelled a :ActPhase, owl:NamedIndividual ;
      rdfs:label "Cancelled" .
  
  # Energy Level Individuals
  :HighEnergy a :EnergyContext, owl:NamedIndividual ;
      rdfs:label "High Energy" .
  :MediumEnergy a :EnergyContext, owl:NamedIndividual ;
      rdfs:label "Medium Energy" .
  :LowEnergy a :EnergyContext, owl:NamedIndividual ;
      rdfs:label "Low Energy" .
  
  # Milestone Status Individuals
  :MilestonePending a :Milestone, owl:NamedIndividual ;
      rdfs:label "Pending" .
  :MilestoneReached a :Milestone, owl:NamedIndividual ;
      rdfs:label "Reached" .
  :MilestoneMissed a :Milestone, owl:NamedIndividual ;
      rdfs:label "Missed" .
  ```

#### 1.2 Domain-Specific Properties

- [ ] Add object properties:
  ```turtle
  # Core Relationships
  :prescribes a owl:ObjectProperty ;
      rdfs:subPropertyOf cco:ont00001942 ;
      rdfs:domain cco:ont00000974 ;  # CCO Plan
      rdfs:range cco:ont00000228 ;  # CCO PlannedAct
      rdfs:label "prescribes" .
  
  :hasObjective a owl:ObjectProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000476 ;
      rdfs:label "has objective" .
  
  :achieves a owl:ObjectProperty ;
      rdfs:domain cco:ont00000228 ;
      rdfs:range cco:ont00000476 ;
      rdfs:label "achieves" .
  
  :hasPhase a owl:ObjectProperty, owl:FunctionalProperty ;
      rdfs:domain cco:ont00000228 ;
      rdfs:range :ActPhase ;
      rdfs:label "has phase" .
  
  :performedBy a owl:ObjectProperty ;
      rdfs:domain cco:ont00000228 ;
      rdfs:range cco:ont00000374 ;
      rdfs:label "performed by" .
  
  # Hierarchy
  :hasPart a owl:ObjectProperty ;
      rdfs:subPropertyOf bfo:BFO_0000051 ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000974 ;
      rdfs:label "has part" .
  
  :partOf a owl:ObjectProperty ;
      rdfs:subPropertyOf bfo:BFO_0000050 ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000974 ;
      rdfs:label "part of" ;
      owl:inverseOf :hasPart .
  
  :dependsOn a owl:ObjectProperty, owl:TransitiveProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000974 ;
      rdfs:label "depends on" .
  
  :cannotStartUntil a owl:ObjectProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000974 ;
      rdfs:label "cannot start until" .
  
  :blockedBy a owl:ObjectProperty ;
      rdfs:domain cco:ont00000228 ;
      rdfs:range bfo:BFO_0000003 ;
      rdfs:label "blocked by" .
  
  # Context Requirements
  :requiresFacility a owl:ObjectProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000192 ;
      rdfs:label "requires facility" .
  
  :requiresArtifact a owl:ObjectProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000001 ;
      rdfs:label "requires artifact" .
  
  :requiresAgent a owl:ObjectProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range cco:ont00000374 ;
      rdfs:label "requires agent" .
  
  :requiresEnergyContext a owl:ObjectProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range :EnergyContext ;
      rdfs:label "requires energy context" .
  
  # Milestone Relationships
  :marksProgressToward a owl:ObjectProperty ;
      rdfs:domain :Milestone ;
      rdfs:range cco:ont00000476 ;
      rdfs:label "marks progress toward" .
  
  :hasStatus a owl:ObjectProperty ;
      rdfs:domain :Milestone ;
      rdfs:range :MilestoneStatus ;
      rdfs:label "has status" .
  ```

- [ ] Add datatype properties:
  ```turtle
  :hasPriority a owl:DatatypeProperty, owl:FunctionalProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:positiveInteger ;
      rdfs:label "has priority" .
  
  :hasDoDateTime a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:dateTime ;
      rdfs:label "has do date time" .
  
  :hasDurationMinutes a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:positiveInteger ;
      rdfs:label "has duration minutes" .
  
  :hasCompletedDateTime a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000228 ;
      rdfs:range xsd:dateTime ;
      rdfs:label "has completed date time" .
  
  :hasTargetDate a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000476, :Milestone ;
      rdfs:range xsd:date ;
      rdfs:label "has target date" .
  
  # Recurrence (iCalendar RRULE pattern)
  :hasRecurrenceFrequency a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:string ;
      rdfs:label "has recurrence frequency" .
  
  :hasRecurrenceInterval a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:positiveInteger ;
      rdfs:label "has recurrence interval" .
  
  :hasRecurrenceUntil a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:dateTime ;
      rdfs:label "has recurrence until" .
  
  :hasRecurrenceCount a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:positiveInteger ;
      rdfs:label "has recurrence count" .
  
  :byDay a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:string ;
      rdfs:label "by day" .
  
  :byMonth a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:string ;
      rdfs:label "by month" .
  
  :byMonthDay a owl:DatatypeProperty ;
      rdfs:domain cco:ont00000974 ;
      rdfs:range xsd:string ;
      rdfs:label "by month day" .
  ```

#### 1.3 Validation

- [ ] Run OWL reasoner (HermiT or Pellet) to verify:
  - [ ] No inconsistencies
  - [ ] Correct class hierarchy
  - [ ] Property domain/range constraints satisfied

- [ ] Run pytest validation:
  ```bash
  cd ontology
  uv run pytest tests/ -v
  ```

---

### Phase 2: Create v4 SHACL Shapes

- [ ] Create `ontology/actions-shapes-v4.ttl` with:

  - [ ] Common shapes (UUID, name, description)
  - [ ] Priority constraint (1-4)
  - [ ] Recurrence validation
  - [ ] Phase transition rules
  - [ ] Cardinality constraints (Plan→PlannedAct = 1..*)
  - [ ] Dependency cycle detection
  - [ ] Objective/Project linkage validation

- [ ] Test shapes against example data:
  ```bash
  uv run pytest tests/v4/test_shacl_validation.py
  ```

---

### Phase 3: Data Migration Scripts

#### 3.1 Migration Utilities

Create `ontology/migrations/v3_to_v4.py`:

```python
#!/usr/bin/env python3
"""
Migrate Actions Vocabulary v3 to v4.
Handles class mapping and data transformation.
"""

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

# Namespaces
V3 = Namespace("https://clearhead.us/vocab/actions/v3#")
V4 = Namespace("https://clearhead.us/vocab/actions/v4#")
CCO = Namespace("https://www.commoncoreontologies.org/")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")

def migrate_action_plan(g_v3, plan_iri_v3):
    """
    Migrate v3 ActionPlan to v4 CCO Plan.
    """
    plan_iri_v4 = URIRef(str(plan_iri_v3).replace("/v3#", "/v4#"))
    
    g_v4 = Graph()
    g_v4.bind("v4", V4)
    g_v4.bind("cco", CCO)
    g_v4.bind("bfo", BFO)
    
    # Change class from v3:ActionPlan to cco:Plan
    g_v4.add((plan_iri_v4, RDF.type, CCO.ont00000974))
    
    # Copy common properties
    for p, o in g_v3.predicate_objects(plan_iri_v3):
        if p not in [
            V3.parentAction,  # Replace with v4:partOf
            V3.hasProject,    # Replace with v4:hasObjective
            V3.requiresContext, # Replace with context-specific properties
        ]:
            g_v4.add((plan_iri_v4, p, o))
    
    # Handle hierarchy migration
    for parent_iri in g_v3.objects(plan_iri_v3, V3.parentAction):
        parent_iri_v4 = URIRef(str(parent_iri).replace("/v3#", "/v4#"))
        g_v4.add((plan_iri_v4, V4.partOf, parent_iri_v4))
    
    # Handle project→objective migration
    for project_name in g_v3.objects(plan_iri_v3, V3.hasProject):
        objective_iri = URIRef(f"urn:objective:{project_name.lower().replace(' ', '_')}")
        g_v4.add((objective_iri, RDF.type, CCO.ont00000476))
        g_v4.add((objective_iri, RDFS.label, Literal(project_name)))
        g_v4.add((plan_iri_v4, V4.hasObjective, objective_iri))
    
    return g_v4


def migrate_action_process(g_v3, process_iri_v3):
    """
    Migrate v3 ActionProcess to v4 CCO PlannedAct.
    """
    process_iri_v4 = URIRef(str(process_iri_v3).replace("/v3#", "/v4#"))
    
    g_v4 = Graph()
    
    # Change class
    g_v4.add((process_iri_v4, RDF.type, CCO.ont00000228))
    
    # Copy properties
    for p, o in g_v3.predicate_objects(process_iri_v3):
        if p == V3.hasState:
            # Convert hasState to hasPhase
            state_label = str(o).split("#")[-1]
            phase_iri = V4[state_label]
            g_v4.add((process_iri_v4, V4.hasPhase, phase_iri))
        else:
            g_v4.add((process_iri_v4, p, o))
    
    return g_v4


def migrate_context(g_v3, context_iri_v3):
    """
    Migrate v3 Context classes to direct CCO usage or EnergyContext.
    """
    context_types = list(g_v3.objects(context_iri_v3, RDF.type))
    
    # Check for EnergyContext (only custom context in v4)
    if V3.EnergyContext in context_types:
        # Keep as v4:EnergyContext
        context_iri_v4 = URIRef(str(context_iri_v3).replace("/v3#", "/v4#"))
        g_v4 = Graph()
        g_v4.add((context_iri_v4, RDF.type, V4.EnergyContext))
        for p, o in g_v3.predicate_objects(context_iri_v3):
            g_v4.add((context_iri_v4, p, o))
        return g_v4
    else:
        # Map to CCO directly (no wrapper)
        # LocationContext → requiresFacility → cco:Facility
        # ToolContext → requiresArtifact → cco:Artifact
        # SocialContext → requiresAgent → cco:Agent
        # Return None - handled in plan migration
        return None


def migrate_milestone(g_v3, milestone_iri_v3):
    """
    Migrate v3 Milestone from RootActionPlan subclass to Directive ICE subclass.
    """
    milestone_iri_v4 = URIRef(str(milestone_iri_v3).replace("/v3#", "/v4#"))
    
    g_v4 = Graph()
    
    # Change: v3:Milestone (subclass of RootActionPlan) → v4:Milestone (subclass of DirectiveICE)
    g_v4.add((milestone_iri_v4, RDF.type, V4.Milestone))
    
    # Copy properties
    for p, o in g_v3.predicate_objects(milestone_iri_v3):
        if p not in [V3.parentAction]:  # Milestones don't have parents in v4
            g_v4.add((milestone_iri_v4, p, o))
    
    # Link to objective if it had project
    for project_name in g_v3.objects(milestone_iri_v3, V3.hasProject):
        objective_iri = URIRef(f"urn:objective:{project_name.lower().replace(' ', '_')}")
        g_v4.add((milestone_iri_v4, V4.marksProgressToward, objective_iri))
    
    return g_v4


def full_migration(v3_file, v4_file):
    """
    Perform full v3→v4 migration.
    """
    g_v3 = Graph()
    g_v3.parse(v3_file, format="turtle")
    
    g_v4 = Graph()
    g_v4.bind("v4", V4)
    g_v4.bind("cco", CCO)
    g_v4.bind("bfo", BFO)
    
    # Migrate all plans
    for plan_iri in g_v3.subjects(RDF.type, V3.ActionPlan):
        g_v4 += migrate_action_plan(g_v3, plan_iri)
    
    # Migrate all processes
    for process_iri in g_v3.subjects(RDF.type, V3.ActionProcess):
        g_v4 += migrate_action_process(g_v3, process_iri)
    
    # Migrate energy contexts (skip other contexts - map to CCO in plans)
    for ctx_iri in g_v3.subjects(RDF.type, V3.EnergyContext):
        g_v4 += migrate_context(g_v3, ctx_iri)
    
    # Migrate milestones
    for ms_iri in g_v3.subjects(RDF.type, V3.Milestone):
        g_v4 += migrate_milestone(g_v3, ms_iri)
    
    g_v4.serialize(v4_file, format="turtle")
    print(f"Migrated {v3_file} → {v4_file}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: v3_to_v4.py <input.ttl> <output.ttl>")
        sys.exit(1)
    
    full_migration(sys.argv[1], sys.argv[2])
```

#### 3.2 Test Migration

- [ ] Create test data files:
  ```
  ontology/migrations/test-data/
  ├── valid-v3-simple.ttl
  ├── valid-v3-hierarchy.ttl
  ├── valid-v3-contexts.ttl
  └── valid-v3-milestones.ttl
  ```

- [ ] Run migration tests:
  ```bash
  cd ontology
  uv run pytest migrations/test_v3_to_v4.py -v
  ```

---

### Phase 4: Update Test Suite

#### 4.1 Port v3 Tests

- [ ] Copy `tests/v3/test_shacl_validation.py` to `tests/v4/test_shacl_validation.py`
- [ ] Update namespace references: `v3#` → `v4#`
- [ ] Update class references: `ActionPlan` → `cco:Plan`, `ActionProcess` → `cco:PlannedAct`
- [ ] Update property references: `hasState` → `hasPhase`, `parentAction` → `partOf`

#### 4.2 Add v4-Specific Tests

- [ ] Test direct CCO class usage
- [ ] Test EnergyContext instances
- [ ] Test Milestone status transitions
- [ ] Test Objective creation from project strings

---

### Phase 5: Update Downstream Specs

- [ ] Update `ontology/docs/ontology.md`:
  - Replace v3 class diagrams with v4
  - Update examples to use CCO classes directly
  - Document migration path

- [ ] Update any code that imports v3 vocabulary:
  ```python
  # Old
  from actions.v3 import ActionPlan, ActionProcess
  
  # New
  from actions.v4 import Plan as ActionPlan, PlannedAct as ActionProcess
  from cco import ont00000974 as Plan, ont00000228 as PlannedAct
  ```

- [ ] Update documentation site (`ontology/site/`):
  - Generate v4 documentation
  - Publish to `https://clearhead.us/vocab/actions/v4/`
  - Add v3→v4 migration guide

---

### Phase 6: Deployment

- [ ] Deploy v4 ontology:
  ```bash
  cd ontology
  uv run python build_extensions.py
  # Generates site/vocab/actions/v4/
  ```

- [ ] Run full test suite:
  ```bash
  uv run pytest tests/ -v --slow
  ```

- [ ] Commit and push:
  ```bash
  git add .
  git commit -m "Implement Actions Vocabulary v4 - CCO-aligned design"
  git push origin feature/v4-transition
  ```

- [ ] Create pull request with:
  - Detailed migration guide
  - Breaking changes documentation
  - Test results
  - Reasoner output

---

### Phase 7: Monitoring & Rollback Plan

- [ ] Monitor deployment for 1 week
- [ ] Gather feedback from users
- [ ] Document any issues

**Rollback plan:** If critical issues arise:
  ```bash
  git revert <commit-hash>
  # Or restore backup:
  cp -r ontology/v3-backup-YYYYMMDD/* ontology/
  ```

---

## Summary Checklist

**Design Phase:**
- [x] Design document finalized
- [x] CCO Plan class verified (ont00000974)
- [x] Migration requirements identified

**Implementation Phase:**
- [ ] v4 OWL file created
- [ ] v4 SHACL shapes created
- [ ] Migration scripts written and tested
- [ ] Test suite updated
- [ ] Downstream specs updated

**Deployment Phase:**
- [ ] Documentation deployed
- [ ] Full test suite passing
- [ ] Migration guide published
- [ ] Monitoring period completed

---

## References

- [BFO 2.0 Specification](http://basic-formal-ontology.org/)
- [CCO Documentation](https://github.com/CommonCoreOntology/CommonCoreOntologies)
- [GTD - Getting Things Done](https://gettingthingsdone.com/)
- [iCalendar RRULE Specification](https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html)
