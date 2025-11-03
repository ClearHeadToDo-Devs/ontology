# Actions Vocabulary v3 - Example Data

This directory contains RDF/Turtle example data for the Actions Vocabulary v3.1.0 ontology.

## Purpose

These examples serve **dual purposes**:
1. **Testing**: Used by the SHACL validation test suite to verify that constraints work correctly
2. **Documentation**: Deployed to the website as reference examples for developers

## Directory Structure

```
examples/v3/
├── README.md           # This file
├── valid/              # ✅ Valid examples that pass all SHACL constraints
│   ├── simple-actionplan.ttl
│   ├── actionplan-with-children.ttl
│   └── actionprocess-execution.ttl
└── invalid/            # ❌ Invalid examples that violate specific constraints
    ├── invalid-priority.ttl
    ├── invalid-uuid.ttl
    ├── invalid-root-with-parent.ttl
    ├── invalid-temporal.ttl
    └── invalid-depth-mismatch.ttl
```

## Valid Examples

### `simple-actionplan.ttl`
A simple, standalone action plan demonstrating:
- Root action plan structure
- Priority, dates, and duration
- Context assignment
- UUID v7 format

**Use case**: Basic task with context and scheduling

### `actionplan-with-children.ttl`
A hierarchical action plan structure showing:
- Root action plan (project level)
- Child action plans (tasks)
- Grandchild action plans (subtasks)
- Dependencies between tasks
- Depth validation

**Use case**: Project breakdown with task hierarchy

### `actionprocess-execution.ttl`
Action process (execution) instances demonstrating:
- Plan vs Process separation (BFO distinction)
- Recurring action plan
- Multiple process executions from the same plan
- Process state management
- Completion timestamps

**Use case**: Recurring tasks with execution tracking

## Invalid Examples

These examples are designed to **fail validation** to test that SHACL constraints properly reject bad data.

### `invalid-priority.ttl`
**Violation**: Priority is 5 (must be 1-4)
```turtle
actions:hasPriority 5 ;  # ❌ Out of range
```

### `invalid-uuid.ttl`
**Violation**: UUID is not version 7 format
```turtle
actions:hasUUID "not-a-valid-uuid-v7-format" ;  # ❌ Invalid format
```

### `invalid-root-with-parent.ttl`
**Violation**: Root action plan has a parent
```turtle
a actions:RootActionPlan ;
actions:hasParentPlan actions:plan-parent .  # ❌ Roots can't have parents
```

### `invalid-temporal.ttl`
**Violation**: Do date is after due date
```turtle
actions:hasDoDateTime "2025-01-20T09:00:00"^^xsd:dateTime ;
actions:hasDueDateTime "2025-01-15T17:00:00"^^xsd:dateTime .  # ❌ Due before do
```

### `invalid-depth-mismatch.ttl`
**Violation**: Declared depth doesn't match actual parent chain depth
```turtle
actions:hasDepth 3 ;  # Claims depth 3
actions:hasParentPlan actions:plan-root .  # But only 1 level deep ❌
```

## Using These Examples

### For Testing
Run the SHACL validation test suite:
```bash
uv run pytest tests/v3/test_shacl_validation.py -v
```

The tests will:
- Load each example file
- Validate against SHACL shapes
- Verify that valid examples pass
- Verify that invalid examples fail with the expected error

### For Learning
Study these examples to understand:
- How to structure action plans in RDF
- What constraints exist in the vocabulary
- How to represent hierarchies and relationships
- How to separate plans (information) from processes (execution)

### For Development
Use these as templates for your own action data:
```bash
# View a simple example
cat examples/v3/valid/simple-actionplan.ttl

# Validate your own data against SHACL shapes
uv run python -c "
from pyshacl import validate
from rdflib import Graph

data = Graph()
data.parse('your-data.ttl', format='turtle')

shapes = Graph()
shapes.parse('actions-shapes-v3.ttl', format='turtle')

conforms, results, text = validate(data, shacl_graph=shapes)
print('Valid!' if conforms else f'Errors:\\n{text}')
"
```

## Viewing Online

These examples are deployed to the vocabulary website:
- **Valid examples**: https://clearhead.us/vocab/actions/examples/v3/valid/
- **Invalid examples**: https://clearhead.us/vocab/actions/examples/v3/invalid/

## Key Concepts Demonstrated

### BFO/CCO Alignment
- **ActionPlan** (Continuant): Information that persists, can be reused
- **ActionProcess** (Occurrent): Temporal execution events
- **Prescribed By**: CCO relationship linking processes to plans

### Hierarchical Structure
- **RootActionPlan**: Top-level (depth 0), can have project assignment
- **ChildActionPlan**: Mid-level (depth 1-4), inherits project from root
- **LeafActionPlan**: Bottom level (depth 5), cannot have children

### GTD-Style Contexts
- Context names follow `@contextName` pattern
- Typed contexts (LocationContext, ToolContext, etc.)
- Multiple contexts per action

### Temporal Planning
- `hasDoDateTime`: When to start the action
- `hasDueDateTime`: When action must be complete
- `hasCompletedDateTime`: When action was actually completed (processes only)
- Validation: Do date must be before due date

### Priority System (Eisenhower Matrix)
- Priority 1: Urgent + Important
- Priority 2: Important, not urgent
- Priority 3: Urgent, not important
- Priority 4: Neither urgent nor important

## Related Files

- **Ontology**: `actions-vocabulary.owl` - Class and property definitions
- **SHACL Shapes**: `actions-shapes-v3.ttl` - Validation constraints
- **Test Suite**: `tests/v3/test_shacl_validation.py` - Automated validation tests
- **Documentation**: `README.md` - Complete vocabulary documentation

## Contributing Examples

When adding new examples:

1. **Valid examples** should:
   - Pass all SHACL validation constraints
   - Demonstrate a clear use case
   - Use realistic data (UUIDs, dates, names)
   - Include comments explaining key concepts

2. **Invalid examples** should:
   - Violate exactly one constraint
   - Include a comment explaining the violation
   - Use descriptive file names (`invalid-{constraint}.ttl`)
   - Be used in test suite to verify constraint works

3. **All examples** should:
   - Use the correct namespace: `https://clearhead.us/vocab/actions/v3#`
   - Follow Turtle syntax conventions
   - Be well-documented with inline comments
   - Work with the current ontology version

## License

These examples are part of the Actions Vocabulary project and are available under the same license as the ontology.
