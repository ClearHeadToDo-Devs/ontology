# Migration Guide: v2 → v3

## Overview

This guide helps you migrate from Actions Vocabulary v2 to v3. The core conceptual change is the **separation of plans from processes**, aligning with BFO's continuant/occurrent distinction.

## Quick Reference

| v2 Concept | v3 Concept | Type Change |
|-----------|-----------|-------------|
| `actions:Action` | `actions:ActionPlan` | Information entity |
| (implicit execution) | `actions:ActionProcess` | Process |
| `actions:RootAction` | `actions:RootActionPlan` | Plan specialization |
| `actions:ChildAction` | `actions:ChildActionPlan` | Plan specialization |
| `actions:LeafAction` | `actions:LeafActionPlan` | Plan specialization |
| `actions:state` | `actions:hasState` | On process, not plan |
| `actions:parentAction` | `bfo:has_part` (inverse) | BFO relation |

---

## Conceptual Changes

### 1. Single Entity → Plan + Process

**v2: One entity for everything**
```turtle
# v2: Action represents both intention and execution
:review_reports a actions:Action ;
    schema:name "Review quarterly reports" ;
    actions:priority 2 ;
    actions:state actions:Completed ;        # Mixed concern!
    actions:completedDateTime "2025-01-20T14:30:00"^^xsd:dateTime .
```

**v3: Separate plan from execution**
```turtle
# v3: PLAN - What to do (information)
:review_reports_plan a actions:RootActionPlan ;
    schema:name "Review quarterly reports" ;
    actions:hasPriority 2 ;                  # Planning concerns
    actions:hasContext "@office" ;
    actions:prescribes :review_reports_process .

# v3: PROCESS - How it was done (execution)
:review_reports_process a actions:ActionProcess ;
    actions:hasState actions:Completed ;     # Execution concerns
    # completedDateTime will be temporal region property
```

### 2. State Location

**v2:** State on Action
```turtle
:my_action actions:state actions:InProgress .
```

**v3:** State on Process
```turtle
:my_plan actions:prescribes :my_process .
:my_process actions:hasState actions:InProgress .
```

**Rationale:**
- Plans don't have states - they don't change once created
- Processes have states - they progress through phases
- Aligns with BFO: states are qualities that inhere in processes

### 3. Hierarchy Relations

**v2:** Custom `parentAction` property
```turtle
:child_action actions:parentAction :root_action .
```

**v3:** BFO `has_part` relation
```turtle
:root_plan bfo:has_part :child_plan .
# Or inverse:
:child_plan bfo:BFO_0000178 :root_plan .  # part_of
```

**Rationale:**
- Reuses standard BFO mereological relation
- Interoperable with other BFO ontologies
- Reasoners understand BFO parthood

---

## Migration Patterns

### Pattern 1: Simple Root Action

**v2:**
```turtle
:action1 a actions:RootAction ;
    schema:name "Review reports" ;
    schema:description "Q4 performance analysis" ;
    actions:priority 2 ;
    actions:context "@office" ;
    actions:state actions:Completed ;
    actions:completedDateTime "2025-01-20T14:30:00"^^xsd:dateTime .
```

**v3:**
```turtle
# The plan
:action1_plan a actions:RootActionPlan ;
    schema:name "Review reports" ;
    schema:description "Q4 performance analysis" ;
    actions:hasPriority 2 ;
    actions:hasContext "@office" ;
    actions:prescribes :action1_process .

# The execution
:action1_process a actions:ActionProcess ;
    actions:hasState actions:Completed .
    # Temporal properties TBD in full v3
```

**Migration Steps:**
1. Rename `:action1` → `:action1_plan`
2. Change class: `actions:RootAction` → `actions:RootActionPlan`
3. Create new `:action1_process` instance
4. Move `actions:state` to process
5. Add `actions:prescribes` link
6. Keep plan properties on plan

### Pattern 2: Hierarchical Structure

**v2:**
```turtle
:launch a actions:RootAction ;
    schema:name "Launch product" ;
    actions:project "Product Development" .

:specs a actions:ChildAction ;
    schema:name "Finalize specs" ;
    actions:parentAction :launch ;
    actions:state actions:Completed .

:docs a actions:ChildAction ;
    schema:name "Update docs" ;
    actions:parentAction :launch ;
    actions:state actions:InProgress .
```

**v3:**
```turtle
# Root plan
:launch_plan a actions:RootActionPlan ;
    schema:name "Launch product" ;
    actions:hasProject "Product Development" ;
    bfo:has_part :specs_plan, :docs_plan .

# Child plan 1
:specs_plan a actions:ChildActionPlan ;
    schema:name "Finalize specs" ;
    bfo:BFO_0000178 :launch_plan ;  # part_of
    actions:prescribes :specs_process .

:specs_process a actions:ActionProcess ;
    actions:hasState actions:Completed .

# Child plan 2
:docs_plan a actions:ChildActionPlan ;
    schema:name "Update docs" ;
    bfo:BFO_0000178 :launch_plan ;
    actions:prescribes :docs_process .

:docs_process a actions:ActionProcess ;
    actions:hasState actions:InProgress .
```

**Migration Steps:**
1. Rename all actions: append `_plan`
2. Change class names (Root/Child/Leaf → RootActionPlan/ChildActionPlan/LeafActionPlan)
3. Replace `actions:parentAction` with `bfo:BFO_0000178` (part_of)
4. Add `bfo:has_part` on parents (optional - reasoner can infer)
5. Create process instances for each plan
6. Move states to processes
7. Add `actions:prescribes` links

### Pattern 3: Recurring Action

**v2:**
```turtle
:standup a actions:RootAction ;
    schema:name "Weekly standup" ;
    actions:recurrenceFrequency "WEEKLY" ;
    actions:byDay "Mon" ;
    actions:doTime "09:00:00"^^xsd:time .
```

**v3 (demonstrates power of separation):**
```turtle
# ONE plan prescribes MULTIPLE processes
:standup_plan a actions:RootActionPlan ;
    schema:name "Weekly standup" ;
    actions:hasRecurrenceFrequency "WEEKLY" ;
    actions:hasByDay "Mon" ;
    actions:prescribes :standup_jan20, :standup_jan27, :standup_feb03 .

# Each execution is separate
:standup_jan20 a actions:ActionProcess ;
    actions:hasState actions:Completed .

:standup_jan27 a actions:ActionProcess ;
    actions:hasState actions:Completed .

:standup_feb03 a actions:ActionProcess ;
    actions:hasState actions:InProgress .
```

**Benefits:**
- Clear that one plan generates multiple executions
- Each execution has independent state
- Historical tracking of all occurrences

---

## Property Mapping

### Properties That Stay on Plan

These describe WHAT to do (planning concerns):

| v2 Property | v3 Property | Notes |
|------------|-------------|-------|
| `schema:name` | `schema:name` | Unchanged |
| `schema:description` | `schema:description` | Unchanged |
| `actions:priority` | `actions:hasPriority` | Renamed for clarity |
| `actions:context` | `actions:hasContext` | Renamed |
| `actions:project` | `actions:hasProject` | On RootActionPlan only |
| `actions:doDate` | `actions:hasDoDate` | When to do it |
| `actions:dueDate` | `actions:hasDueDate` | Deadline |
| `actions:durationMinutes` | `actions:hasDurationMinutes` | Expected duration |
| `actions:recurrence*` | `actions:hasRecurrence*` | All recurrence properties |
| `actions:uuid` | `actions:hasUUID` | Plan identifier |

### Properties That Move to Process

These describe HOW it was done (execution concerns):

| v2 Property | v3 Property | Notes |
|------------|-------------|-------|
| `actions:state` | `actions:hasState` | NOW on ActionProcess |
| `actions:completedDateTime` | (TBD) | Temporal region property |

### New Properties in v3

| Property | Domain | Range | Description |
|---------|--------|-------|-------------|
| `actions:prescribes` | ActionPlan | ActionProcess | Links plan to execution(s) |

### Changed Relations

| v2 Relation | v3 Relation | Notes |
|------------|-------------|-------|
| `actions:parentAction` | `bfo:BFO_0000178` | BFO part_of relation |
| (inverse) | `bfo:has_part` | Optional (reasoner infers) |

---

## Automated Migration Script

### Conceptual Algorithm

```python
def migrate_v2_to_v3(v2_graph):
    """
    Migrate v2 RDF graph to v3 structure.
    """
    v3_graph = Graph()

    for action in v2_graph.subjects(RDF.type, ACTIONS_V2.Action):
        # Create plan
        plan_uri = action + "_plan"
        plan_class = determine_plan_class(action)  # Root/Child/Leaf
        v3_graph.add((plan_uri, RDF.type, plan_class))

        # Copy plan properties
        for prop in PLAN_PROPERTIES:
            copy_property(v2_graph, v3_graph, action, plan_uri, prop)

        # Create process
        process_uri = action + "_process"
        v3_graph.add((process_uri, RDF.type, ACTIONS_V3.ActionProcess))

        # Link plan to process
        v3_graph.add((plan_uri, ACTIONS_V3.prescribes, process_uri))

        # Move state to process
        state = v2_graph.value(action, ACTIONS_V2.state)
        if state:
            v3_graph.add((process_uri, ACTIONS_V3.hasState, state))

        # Update hierarchy relations
        parent = v2_graph.value(action, ACTIONS_V2.parentAction)
        if parent:
            parent_plan = parent + "_plan"
            v3_graph.add((plan_uri, BFO.BFO_0000178, parent_plan))

    return v3_graph
```

### Script Location

Full migration script: `scripts/migrate_v2_to_v3.py` (to be created)

---

## JSON Data Migration

### v2 JSON Structure

```json
{
  "@type": "Action",
  "uuid": "01936194-d5b0-7890-8000-123456789abc",
  "name": "Review reports",
  "priority": 2,
  "state": "completed",
  "completedDateTime": "2025-01-20T14:30:00Z"
}
```

### v3 JSON Structure

```json
{
  "plan": {
    "@type": "RootActionPlan",
    "uuid": "01936194-d5b0-7890-8000-123456789abc",
    "name": "Review reports",
    "priority": 2,
    "prescribes": "process_01936194-d5b1-7890-8000-abcdef123456"
  },
  "process": {
    "@type": "ActionProcess",
    "id": "process_01936194-d5b1-7890-8000-abcdef123456",
    "state": "completed",
    "completedDateTime": "2025-01-20T14:30:00Z"
  }
}
```

**Alternative (flat with references):**
```json
[
  {
    "@type": "RootActionPlan",
    "@id": "plan:01936194-d5b0-7890-8000-123456789abc",
    "name": "Review reports",
    "priority": 2,
    "prescribes": "process:01936194-d5b1-7890-8000-abcdef123456"
  },
  {
    "@type": "ActionProcess",
    "@id": "process:01936194-d5b1-7890-8000-abcdef123456",
    "state": "completed"
  }
]
```

---

## Testing Migration

### Validation Checklist

After migrating data, verify:

- [ ] All v2 actions have corresponding v3 plans
- [ ] All v3 plans have corresponding processes
- [ ] `prescribes` links exist between plans and processes
- [ ] States moved from plans to processes
- [ ] Hierarchy uses BFO relations
- [ ] Plan properties on plans, not processes
- [ ] Process properties on processes, not plans
- [ ] UUIDs preserved
- [ ] Reasoner confirms consistency
- [ ] SHACL validation passes (when shapes ready)

### Comparison Script

```bash
# Compare v2 vs v3 data
python scripts/compare_v2_v3.py \
  --v2-data data/v2/actions.ttl \
  --v3-data data/v3/actions.ttl \
  --report migration-report.html
```

---

## Common Pitfalls

### ❌ DON'T: Put state on plan

```turtle
# WRONG
:my_plan a actions:ActionPlan ;
    actions:hasState actions:Completed .  # Plans don't have states!
```

### ✅ DO: Put state on process

```turtle
# CORRECT
:my_plan actions:prescribes :my_process .
:my_process actions:hasState actions:Completed .
```

### ❌ DON'T: Forget to create process

```turtle
# WRONG - Plan without process
:my_plan a actions:ActionPlan ;
    schema:name "Do something" .
# Missing process!
```

### ✅ DO: Always create corresponding process

```turtle
# CORRECT
:my_plan actions:prescribes :my_process .
:my_process a actions:ActionProcess .
```

### ❌ DON'T: Use old property names

```turtle
# WRONG
:my_plan actions:priority 2 .  # v2 style
```

### ✅ DO: Use new property names

```turtle
# CORRECT
:my_plan actions:hasPriority 2 .  # v3 style
```

---

## Rollback Strategy

If migration causes issues:

1. **Keep v2 alongside v3** (different directories)
2. **Gradual migration**: Migrate subset, test, iterate
3. **Dual support**: Applications can support both temporarily
4. **Clear cutover date**: Plan transition timeline

---

## Timeline Recommendation

**Phase 1 (Weeks 1-2):** Test migration
- Migrate sample data
- Validate with Protégé
- Test downstream tools

**Phase 2 (Weeks 3-4):** Partial migration
- Migrate non-critical data
- Run in parallel with v2
- Monitor for issues

**Phase 3 (Week 5+):** Full migration
- Migrate all data
- Deprecate v2
- Remove v2 support

---

## Support

Questions about migration?
- Review examples in `v3/examples/`
- Check test cases in `v3/tests/`
- See [BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md) for concepts
- Consult [README.md](./README.md) for architecture

---

## Appendix: Complete Example

### v2 Full Example

```turtle
@prefix actions: <https://vocab.example.org/actions/> .
@prefix schema: <http://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:launch a actions:RootAction ;
    schema:name "Launch new product" ;
    actions:priority 1 ;
    actions:project "Product Development" ;
    actions:state actions:InProgress .

:specs a actions:ChildAction ;
    schema:name "Finalize specifications" ;
    actions:parentAction :launch ;
    actions:state actions:Completed ;
    actions:completedDateTime "2025-01-15T16:00:00"^^xsd:dateTime .

:docs a actions:ChildAction ;
    schema:name "Update documentation" ;
    actions:parentAction :launch ;
    actions:state actions:InProgress .

:api_section a actions:LeafAction ;
    schema:name "Review API section" ;
    actions:parentAction :docs ;
    actions:state actions:NotStarted .
```

### v3 Equivalent

```turtle
@prefix actions: <https://vocab.example.org/actions/v3#> .
@prefix schema: <http://schema.org/> .
@prefix bfo: <http://purl.obolibrary.org/obo/BFO_> .

# PLANS
:launch_plan a actions:RootActionPlan ;
    schema:name "Launch new product" ;
    actions:hasPriority 1 ;
    actions:hasProject "Product Development" ;
    bfo:has_part :specs_plan, :docs_plan ;
    actions:prescribes :launch_process .

:specs_plan a actions:ChildActionPlan ;
    schema:name "Finalize specifications" ;
    bfo:BFO_0000178 :launch_plan ;
    actions:prescribes :specs_process .

:docs_plan a actions:ChildActionPlan ;
    schema:name "Update documentation" ;
    bfo:BFO_0000178 :launch_plan ;
    bfo:has_part :api_section_plan ;
    actions:prescribes :docs_process .

:api_section_plan a actions:LeafActionPlan ;
    schema:name "Review API section" ;
    bfo:BFO_0000178 :docs_plan ;
    actions:prescribes :api_section_process .

# PROCESSES
:launch_process a actions:ActionProcess ;
    actions:hasState actions:InProgress .

:specs_process a actions:ActionProcess ;
    actions:hasState actions:Completed .

:docs_process a actions:ActionProcess ;
    actions:hasState actions:InProgress .

:api_section_process a actions:ActionProcess ;
    actions:hasState actions:NotStarted .
```

**Key differences:**
- 4 plans + 4 processes (vs 4 actions)
- States on processes
- BFO parthood relations
- Clear plan-process separation
- Same semantic meaning, more explicit structure
