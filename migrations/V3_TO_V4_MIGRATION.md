# Actions Vocabulary v3 → v4 Migration Guide

**Status:** PREPARED
**Target Audience:** System integrators, developers
**Last Updated:** 2025-01-20

---

## Overview

This guide explains how to migrate from Actions Vocabulary v3 to v4. The v4 design removes wrapper classes and uses CCO (Common Core Ontologies) classes directly, providing better interoperability and reduced maintenance burden.

### Key Changes

| Aspect | v3 | v4 |
|--------|-----|-----|
| **Classes** | 12 custom classes | 3 custom classes + CCO |
| **Plan** | `actions:ActionPlan` | `cco:Plan` (ont00000974) |
| **Process** | `actions:ActionProcess` | `cco:PlannedAct` (ont00000228) |
| **Project** | String `hasProject` | Object `cco:Objective` (ont00000476) |
| **Hierarchy** | `parentAction` property | BFO `hasPart`/`partOf` |
| **State** | `ActionState` class | `ActPhase` class (BFO Quality) |
| **Context** | 4 wrapper classes | Direct CCO usage + EnergyContext |
| **Milestone** | Subclass of RootActionPlan | Subclass of DirectiveICE |

### Why Migrate?

1. **Better Interoperability** - CCO is DoD/IC baseline standard
2. **Reduced Maintenance** - 75% fewer custom classes
3. **Stronger Semantics** - Grounded in BFO/CCO philosophy
4. **Future-Proof** - Aligned with evolving ontology standards

---

## Prerequisites

1. **Backup existing data**
   ```bash
   cp -r ontology/v3 ontology/v3-backup-$(date +%Y%m%d)
   ```

2. **Install migration tools**
   ```bash
   cd ontology
   uv sync
   ```

3. **Test environment**
   ```bash
   uv run pytest --version  # Should pass
   ```

---

## Automated Migration

### Step 1: Run Migration Script

```bash
cd ontology
python migrations/v3_to_v4.py \
    examples/v3/valid/simple-actionplan.ttl \
    examples/v4/migrated/simple-actionplan.ttl
```

### Step 2: Validate Output

```bash
uv run pytest tests/v4/test_shacl_validation.py -v
```

### Step 3: Review Changes

```bash
diff examples/v3/valid/simple-actionplan.ttl \
     examples/v4/migrated/simple-actionplan.ttl
```

---

## Manual Migration Guide

If you need to migrate data manually or understand the transformations:

### 1. Plan Class Changes

#### Before (v3)
```turtle
@prefix v3: <https://clearhead.us/vocab/actions/v3#> .

:my_task a v3:ActionPlan ;
    schema:name "Review reports" ;
    v3:hasPriority 2 ;
    v3:hasContext "@office" ;
    v3:hasProject "Q1 Operations" .
```

#### After (v4)
```turtle
@prefix v4: <https://clearhead.us/vocab/actions/v4#> .
@prefix cco: <https://www.commoncoreontologies.org/> .

:my_task a cco:ont00000974 ;  # CCO Plan
    schema:name "Review reports" ;
    v4:hasPriority 2 ;
    v4:requiresFacility cco:ont00000192 ;  # Facility (context)
    v4:hasObjective :q1_operations_objective .

:q1_operations_objective a cco:ont00000476 ;  # CCO Objective
    schema:name "Q1 Operations" .
```

### 2. Process Class Changes

#### Before (v3)
```turtle
:task_execution a v3:ActionProcess ;
    v3:hasState v3:InProgress ;
    v3:hasCompletedDateTime "2025-01-20T14:30:00Z"^^xsd:dateTime .
```

#### After (v4)
```turtle
@prefix v4: <https://clearhead.us/vocab/actions/v4#> .
@prefix cco: <https://www.commoncoreontologies.org/> .

:task_execution a cco:ont00000228 ;  # CCO PlannedAct
    v4:hasPhase v4:InProgress ;  # Changed from hasState
    v4:hasCompletedDateTime "2025-01-20T14:30:00Z"^^xsd:dateTime .
```

### 3. Hierarchy Changes

#### Before (v3)
```turtle
:child_task a v3:ChildActionPlan ;
    v3:parentAction :parent_task .
```

#### After (v4)
```turtle
@prefix bfo: <http://purl.obolibrary.org/obo/BFO_> .

:child_task a cco:ont00000974 ;
    bfo:BFO_0000050 :parent_task .  # BFO part_of
    # Or use our subproperty:
    v4:partOf :parent_task .
```

### 4. Context Migration

#### Location Context (v3→v4)

**Before:**
```turtle
:office_ctx a v3:LocationContext ;
    v3:requiresFacility cco:ont00000192 .

:task a v3:ActionPlan ;
    v3:requiresContext :office_ctx .
```

**After:**
```turtle
:task a cco:ont00000974 ;
    v4:requiresFacility cco:ont00000192 .  # Direct CCO
```

**Note:** v3 wrapper classes (`LocationContext`, `ToolContext`, `SocialContext`) are removed. Link directly to CCO classes using `requiresFacility`, `requiresArtifact`, or `requiresAgent`.

#### Energy Context (v3→v4) - **Only Custom Context Retained**

**Before:**
```turtle
:high_energy a v3:EnergyContext ;
    v3:hasEnergyLevel "high" .

:task a v3:ActionPlan ;
    v3:requiresContext :high_energy .
```

**After:**
```turtle
:high_energy a v4:EnergyContext, v4:HighEnergy ;  # v4 class
    schema:name "High Energy" .

:task a cco:ont00000974 ;
    v4:requiresEnergyContext :high_energy .
```

### 5. Milestone Changes

#### Before (v3)
```turtle
:milestone_1 a v3:Milestone ;  # Subclass of RootActionPlan
    v3:hasProject "Q1 Operations" ;
    v3:parentAction :root_plan .
```

#### After (v4)
```turtle
:milestone_1 a v4:Milestone ;  # Subclass of DirectiveICE
    v4:marksProgressToward :q1_operations_objective .
    # No parent in v4 - milestones are standalone checkpoints
```

**Important:** v3 milestones had parent actions. v4 milestones are independent checkpoints that mark progress toward objectives.

### 6. Project → Objective Migration

#### Before (v3) - String-Based
```turtle
:task a v3:RootActionPlan ;
    v3:hasProject "Q1 Operations" .  # String
```

#### After (v4) - Object-Based
```turtle
:q1_ops_obj a cco:ont00000476 ;  # Create Objective entity
    schema:name "Q1 Operations" ;
    v4:hasTargetDate "2025-03-31"^^xsd:date .

:task a cco:ont00000974 ;
    v4:hasObjective :q1_ops_obj .
```

**Why this change:** Objects enable richer relationships, querying, and reasoning.

---

## Property Mapping Table

| v3 Property | v4 Property | Notes |
|--------------|--------------|-------|
| `prescribes` | `prescribes` | Same, tighter domain/range |
| `hasState` | `hasPhase` | Renamed to "phase" semantics |
| `parentAction` | `partOf` | Use BFO property or subproperty |
| `hasProject` | `hasObjective` | String → object change |
| `requiresContext` | `requiresFacility`, `requiresArtifact`, `requiresAgent`, `requiresEnergyContext` | Split by context type |
| `assignedToAgent` | `assignedToAgent` | No change |
| `performedBy` | `performedBy` | No change |
| `hasPriority` | `hasPriority` | No change |
| `hasDoDateTime` | `hasDoDateTime` | No change |
| `hasDurationMinutes` | `hasDurationMinutes` | No change |
| All recurrence props | Same | No change |

---

## Common Migration Issues

### Issue 1: Multiple Projects per Plan

**v3:** Plans could have multiple `hasProject` strings (though SHACL restricted this).

**v4:** `hasObjective` is 0..*, so multiple objectives are supported.

**Migration:** Create separate Objective entities for each string.

### Issue 2: Deep Hierarchies

**v3:** Root/Child/Leaf classes enforced depth.

**v4:** No depth classes - use `hasPart`/`partOf` with arbitrary nesting.

**Migration:** Use SHACL to enforce max depth if needed (not in v4 ontology by default).

### Issue 3: Milestone Dependencies

**v3:** Milestones could be parents/children like any plan.

**v4:** Milestones are standalone - they don't have hierarchy.

**Migration:** Convert milestone hierarchies to `dependsOn` relationships between plans, or keep milestones independent and use `cannotStartUntil` constraints.

### Issue 4: Legacy Context Strings

**v3:** `hasContext "@office"` (deprecated string property).

**v4:** No context strings - all context is typed.

**Migration:** Parse string pattern (e.g., `@office`) and map to appropriate CCO class:
- `@office`, `@home` → `cco:Facility` types
- `@computer`, `@phone` → `cco:Artifact` types
- `@agenda:person` → `cco:Agent`

---

## Query Migration

### Before (v3)

```sparql
PREFIX v3: <https://clearhead.us/vocab/actions/v3#>

SELECT ?plan ?project WHERE {
    ?plan a v3:ActionPlan ;
          v3:hasProject ?project .
}
```

### After (v4)

```sparql
PREFIX v4: <https://clearhead.us/vocab/actions/v4#>
PREFIX cco: <https://www.commoncoreontologies.org/>

SELECT ?plan ?project WHERE {
    ?plan a cco:ont00000974 ;
          v4:hasObjective ?objective .
    ?objective a cco:ont00000476 ;
               schema:name ?project .
}
```

---

## Testing Your Migration

### 1. Validate OWL Consistency

```bash
cd ontology
uv run pytest tests/v4/test_ontology_consistency.py -v
```

### 2. Validate SHACL Shapes

```bash
uv run pytest tests/v4/test_shacl_validation.py -v
```

### 3. Reasoning Test

```bash
# Load v4 ontology in Protégé
# File → Open → actions-vocabulary-v4.owl
# Reasoner → HermiT → Start reasoner
# Verify no inconsistencies
```

### 4. Semantic Comparison

Compare v3 and v4 graphs to ensure no data loss:

```python
from rdflib import Graph

g_v3 = Graph()
g_v3.parse("v3-data.ttl")

g_v4 = Graph()
g_v4.parse("v4-data.ttl")

# Count entities
print(f"v3 plans: {len(list(g_v3.subjects(None, None)))}")
print(f"v4 plans: {len(list(g_v4.subjects(None, None)))}")

# Compare names
v3_names = set(str(o) for o in g_v3.objects(None, RDFS.label))
v4_names = set(str(o) for o in g_v4.objects(None, RDFS.label))
print(f"Unique in v3: {v3_names - v4_names}")
print(f"Unique in v4: {v4_names - v3_names}")
```

---

## Rollback Procedure

If migration causes issues:

1. **Restore backup:**
   ```bash
   cp -r ontology/v3-backup-YYYYMMDD/* ontology/
   ```

2. **Revert git commits:**
   ```bash
   git log --oneline
   git revert <commit-hash>
   ```

3. **Switch to v3 namespace:**
   - Update imports in code
   - Update documentation
   - Revert URL redirects in `site/_redirects`

---

## Support

- **Documentation:** See `ontology/PROPOSED_V4_DESIGN.md` for design rationale
- **Examples:** `ontology/examples/v4/` for valid v4 data
- **Tests:** `ontology/tests/v4/` for validation patterns
- **Issues:** Report bugs at https://github.com/your-repo/issues

---

## Appendix: Complete Mapping Reference

### Class Mapping

| v3 Class | v4 Replacement | CCO Equivalent |
|-----------|----------------|-----------------|
| `ActionPlan` | Use `cco:ont00000974` directly | `cco:Plan` |
| `RootActionPlan` | Query: `cco:Plan` with no `partOf` | N/A |
| `ChildActionPlan` | Query: `cco:Plan` with `partOf` | N/A |
| `LeafActionPlan` | Query: `cco:Plan` with no `hasPart` | N/A |
| `ActionProcess` | Use `cco:ont00000228` directly | `cco:PlannedAct` |
| `ActionState` | `:ActPhase` (v4 class) | N/A (BFO Quality) |
| `ActionContext` | Removed | N/A |
| `LocationContext` | Use `cco:ont00000192` directly | `cco:Facility` |
| `ToolContext` | Use `cco:ont00000001` directly | `cco:Artifact` |
| `EnergyContext` | `:EnergyContext` (v4 class) | N/A |
| `SocialContext` | Use `cco:ont00000374` directly | `cco:Agent` |
| `Milestone` | `:Milestone` (v4 class) | N/A (DirectiveICE) |

### Individual Mapping

| v3 Individual | v4 Individual | Change |
|---------------|----------------|--------|
| `NotStarted` | `NotStarted` | Same name, new class (`:ActPhase`) |
| `InProgress` | `InProgress` | Same name, new class |
| `Completed` | `Completed` | Same name, new class |
| `Blocked` | `Blocked` | Same name, new class |
| `Cancelled` | `Cancelled` | Same name, new class |
| (No individuals) | `HighEnergy` | New |
| (No individuals) | `MediumEnergy` | New |
| (No individuals) | `LowEnergy` | New |
| (No individuals) | `MilestonePending` | New |
| (No individuals) | `MilestoneReached` | New |
| (No individuals) | `MilestoneMissed` | New |

---

**End of Migration Guide**
