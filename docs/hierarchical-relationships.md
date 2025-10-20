# Hierarchical Relationships Design Decision

## Context

During ontology development, we faced a key design choice: should we store hierarchical relationships bidirectionally (both `parentAction` and `childAction`) or unidirectionally (only `parentAction`)?

## Decision: Unidirectional Relationships

**We chose to store only `parentAction` relationships and calculate children via SPARQL queries.**

## Rationale

### Problems with Bidirectional Storage

1. **Data Duplication**: Same relationship stored twice (parent→child and child→parent)
2. **Consistency Risk**: Two places to maintain the same information
3. **Complex Validation**: Need SHACL rules to ensure both directions stay synchronized
4. **Update Complexity**: Every relationship change requires updating two triples
5. **Storage Overhead**: Doubles the storage for relationship data

### Benefits of Unidirectional Design

1. **Single Source of Truth**: Only `parentAction` needs to be maintained
2. **Semantic Clarity**: Parent-child relationships flow naturally upward
3. **Simpler Validation**: Only need to validate parent-child constraints
4. **Better Performance**: Less data to store and validate
5. **Standards Compliant**: Follows semantic web best practices

### Depth Property: The Exception

We do include an optional `actions:depth` property because:

- **Adds semantic value**: Provides metadata about hierarchical position
- **Enables efficient queries**: Depth-based filtering without path traversal
- **Single calculated value**: Not a duplicate relationship
- **Validated when present**: Ensures consistency with actual hierarchy

## Navigation Patterns

Here are common queries for navigating hierarchies without `childAction`:

### Direct Children

```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Find immediate children of a specific action
SELECT ?child WHERE {
    ?child actions:parentAction actions:some_parent .
}
```

### All Descendants (Recursive)

```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Find all descendants at any depth
SELECT ?descendant WHERE {
    ?descendant actions:parentAction+ actions:some_parent .
}
```

### Descendants by Level

```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Find descendants with their depth levels
SELECT ?descendant ?level WHERE {
    ?descendant actions:parentAction+ actions:some_parent .
    {
        SELECT ?descendant (COUNT(?intermediate)-1 as ?level) WHERE {
            ?descendant (actions:parentAction)* ?intermediate .
            ?intermediate (actions:parentAction)* actions:some_parent .
        }
    }
}
ORDER BY ?level
```

### Leaf Nodes in Subtree

```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Find all leaf actions under a parent
SELECT ?leaf WHERE {
    ?leaf actions:parentAction+ actions:some_parent .
    ?leaf a actions:LeafAction .
}
```

### Siblings

```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Find siblings of a specific action
SELECT ?sibling WHERE {
    actions:some_action actions:parentAction ?parent .
    ?sibling actions:parentAction ?parent .
    FILTER(?sibling != actions:some_action)
}
```

### Complete Family Tree

```sparql
PREFIX actions: <https://vocab.example.org/actions/>

# Build parent-child pairs with generation distances
SELECT ?parent ?child ?generation WHERE {
    ?parent a actions:Action .
    ?child actions:parentAction+ ?parent .
    {
        SELECT ?parent ?child (COUNT(?intermediate) as ?generation) WHERE {
            ?child (actions:parentAction)* ?intermediate .
            ?intermediate (actions:parentAction)* ?parent .
            FILTER(?intermediate != ?child)
            FILTER(?intermediate != ?parent)
        }
    }
}
ORDER BY ?parent ?generation
```

## Implementation Strategies

### For Applications Needing Frequent Child Access

If your application frequently navigates down the hierarchy, consider these patterns:

#### 1. Application-Level Caching

```python
class ActionHierarchy:
    def __init__(self, rdf_graph):
        self.graph = rdf_graph
        self._children_cache = self._build_children_cache()
    
    def _build_children_cache(self):
        query = """
        SELECT ?parent ?child WHERE { 
            ?child actions:parentAction ?parent 
        }
        """
        cache = {}
        for parent, child in self.graph.query(query):
            cache.setdefault(parent, []).append(child)
        return cache
    
    def get_children(self, action):
        return self._children_cache.get(action, [])
    
    def get_descendants(self, action):
        descendants = []
        for child in self.get_children(action):
            descendants.append(child)
            descendants.extend(self.get_descendants(child))
        return descendants
```

#### 2. Materialized Views

```sparql
# Create a temporary graph with computed children
CONSTRUCT { ?parent actions:hasChild ?child }
WHERE { ?child actions:parentAction ?parent }
```

#### 3. Database Views (if using triplestore with SQL interface)

```sql
CREATE VIEW action_children AS
SELECT parent, child 
FROM triples 
WHERE predicate = 'actions:parentAction';
```

## Validation Benefits

Our unidirectional approach enables simpler, more robust validation:

```turtle
# Simple parent validation
actions:ChildActionShape sh:property [
    sh:path actions:parentAction ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:message "Child actions must have exactly one parent"
] .

# No need for complex bidirectional consistency checks
# No risk of orphaned relationships
# No duplicate data to synchronize
```

## Performance Considerations

### Query Performance
- **Modern SPARQL engines** optimize path queries (`parentAction+`) efficiently
- **Indexing** on `parentAction` provides fast parent→child lookups
- **Property paths** are well-supported in RDF databases

### Storage Performance
- **50% less relationship data** to store
- **Simpler update operations** (single triple vs. two)
- **Reduced validation overhead** (no bidirectional consistency checks)

## Alternative Approaches Considered

### 1. Bidirectional Storage
❌ **Rejected**: Too much complexity for minimal benefit

### 2. Parent-only + Computed Properties
✅ **Chosen**: Best balance of simplicity and functionality

### 3. Separate Child Index
❌ **Rejected**: Adds implementation complexity without semantic benefits

## Future Considerations

If future use cases require extremely frequent child navigation:

1. **Add application-level caching** (recommended)
2. **Use materialized views** in your triplestore
3. **Consider hybrid approaches** (computed properties)

**Do not add `childAction` back to the ontology** - it violates semantic web principles and creates unnecessary complexity.

## Summary

The unidirectional relationship design provides:
- ✅ **Clean semantics** (single source of truth)
- ✅ **Rich querying capabilities** (all navigation patterns supported)
- ✅ **Simpler validation** (no consistency conflicts)
- ✅ **Better performance** (less data, simpler updates)
- ✅ **Standards compliance** (semantic web best practices)

SPARQL's path querying capabilities make bidirectional storage unnecessary while maintaining full navigation functionality.
