# Depth Property Design Decision

## Context

During ontology simplification, we removed explicit `actions:depth` to eliminate redundancy. However, we later reinstated it as an **optional validated property** after recognizing its unique value. This document explains the reasoning.

## Decision: Optional Depth with Validation

**The `actions:depth` property is optional but validated when present.**

## Why Depth is Different from childAction

### Depth = Calculated Metadata ✅
- **Adds semantic value**: Provides hierarchical position metadata
- **Single source of truth**: Calculated from `parentAction` chain
- **Query optimization**: Enables efficient depth-based filtering
- **Validation makes sense**: Can verify claimed depth matches reality

### childAction = Redundant Relationship ❌
- **Duplicates existing data**: Same information as `parentAction` (inverted)
- **Creates consistency risk**: Two places to maintain same relationship
- **No added semantic value**: Doesn't provide new information
- **Complex validation**: Need to ensure both directions stay synchronized

## Usage Patterns

### Without Depth (Implicit)
```turtle
actions:task a actions:LeafAction ;
    actions:parentAction actions:subtask ;
    actions:priority 1 ;
    actions:state actions:NotStarted .
```

### With Depth (Explicit + Validated)
```turtle
actions:task a actions:LeafAction ;
    actions:depth 5 ;              # Must be consistent!
    actions:parentAction actions:subtask ;
    actions:priority 1 ;
    actions:state actions:NotStarted .
```

## Validation Rules

When depth is specified, it must be consistent:

### Class-Depth Consistency
```turtle
# SHACL ensures LeafActions claim depth 5 if specified
actions:LeafDepthConsistency
    a sh:NodeShape ;
    sh:targetClass actions:LeafAction ;
    sh:sparql [
        sh:select """
            SELECT $this WHERE {
                $this actions:depth ?depth .
                FILTER(?depth != 5)
            }
        """ ;
        sh:message "LeafAction depth, when specified, must be 5"
    ] .
```

### Hierarchy-Depth Consistency
The ontology validates that claimed depth matches actual nesting level through parent chain analysis.

## Query Capabilities

### Calculate Depth On-Demand
```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Calculate actual depth for any action
SELECT ?action ?calculatedDepth WHERE {
    ?action a actions:Action .
    {
        SELECT ?action (COUNT(?ancestor) as ?calculatedDepth) WHERE {
            ?action (actions:parentAction)* ?ancestor .
            FILTER(?ancestor != ?action)
        }
    }
}
```

### Find Actions by Depth
```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Find all actions at specific depth (explicit or calculated)
SELECT ?action WHERE {
    ?action (actions:parentAction)* ?root .
    ?root a actions:RootAction .
    # This finds actions exactly 3 levels deep
    ?action actions:parentAction/actions:parentAction/actions:parentAction ?root .
    FILTER NOT EXISTS { 
        ?action actions:parentAction/actions:parentAction/actions:parentAction/actions:parentAction ?deeper 
    }
}
```

### Validate Depth Consistency
```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Find actions with inconsistent depth claims
SELECT ?action ?claimed ?actual WHERE {
    ?action actions:depth ?claimed .
    {
        SELECT ?action (COUNT(?ancestor) as ?actual) WHERE {
            ?action (actions:parentAction)* ?ancestor .
            FILTER(?ancestor != ?action)
        }
    }
    FILTER(?claimed != ?actual)
}
```

## Benefits of Optional Approach

### 1. Flexibility
- **Minimal use**: Omit depth entirely, rely on class semantics
- **Explicit use**: Include depth for tooling/query optimization
- **Mixed use**: Some actions with depth, others without

### 2. Validation Robustness
- **Prevents semantic errors**: LeafAction claiming depth 2 → INVALID
- **Ensures consistency**: Claimed depth must match hierarchy
- **Class constraints**: RootAction=0, ChildAction=1-4, LeafAction=5

### 3. Tooling Support
- **Code generators**: Can use explicit depth for optimization
- **Query engines**: Can use depth for efficient filtering
- **Visualization tools**: Direct access to hierarchical level
- **Import/export**: Depth aids in serialization formats

## Alternative Approaches Considered

### 1. No Depth Property
❌ **Problem**: Lost query optimization and tooling benefits

### 2. Required Depth Property
❌ **Problem**: Forces redundant data entry, violates DRY principle

### 3. Optional Unvalidated Depth
❌ **Problem**: Risk of inconsistent data, semantic confusion

### 4. Optional Validated Depth
✅ **Chosen**: Best balance of flexibility, validation, and utility

## Implementation Guidelines

### For Application Developers

#### Calculate Depth When Needed
```python
def calculate_depth(action_uri, graph):
    query = f"""
    SELECT (COUNT(?ancestor) as ?depth) WHERE {{
        <{action_uri}> (actions:parentAction)* ?ancestor .
        FILTER(?ancestor != <{action_uri}>)
    }}
    """
    return graph.query(query).bindings[0]['depth']
```

#### Validate Depth If Present
```python
def validate_action_depth(action_uri, graph):
    # Check if depth is specified
    depth_query = f"ASK {{ <{action_uri}> actions:depth ?d }}"
    if not graph.query(depth_query).askAnswer:
        return True  # No depth specified, no validation needed
    
    # Validate consistency
    consistency_query = f"""
    SELECT ?claimed ?actual WHERE {{
        <{action_uri}> actions:depth ?claimed .
        {{
            SELECT (COUNT(?ancestor) as ?actual) WHERE {{
                <{action_uri}> (actions:parentAction)* ?ancestor .
                FILTER(?ancestor != <{action_uri}>)
            }}
        }}
    }}
    """
    result = graph.query(consistency_query).bindings[0]
    return result['claimed'] == result['actual']
```

### For Data Authors

#### Option 1: Omit Depth (Recommended for most cases)
```turtle
actions:my_task a actions:ChildAction ;
    actions:parentAction actions:my_parent ;
    actions:priority 2 ;
    actions:state actions:InProgress .
```

#### Option 2: Include Depth (For tooling/optimization)
```turtle
actions:my_task a actions:ChildAction ;
    actions:depth 2 ;  # Will be validated!
    actions:parentAction actions:my_parent ;
    actions:priority 2 ;
    actions:state actions:InProgress .
```

## Summary

The optional depth approach provides:
- ✅ **Semantic value**: Hierarchical position metadata
- ✅ **Validation robustness**: Prevents inconsistent claims
- ✅ **Query optimization**: Efficient depth-based filtering
- ✅ **Flexibility**: Use when helpful, omit when not needed
- ✅ **Tooling support**: Aids code generation and visualization

Unlike bidirectional relationships, optional depth adds genuine value while maintaining data integrity through validation.