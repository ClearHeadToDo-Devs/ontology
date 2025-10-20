# Actions Vocabulary Documentation

This directory contains design documentation and rationale for key decisions in the Actions Vocabulary ontology development.

## Design Documents

### [Hierarchical Relationships](./hierarchical-relationships.md)
**Why we chose unidirectional relationships over bidirectional storage**

- Explains the decision to store only `parentAction` (not `childAction`)
- Provides SPARQL patterns for navigating hierarchies
- Demonstrates how to find children, descendants, siblings, and leaf nodes
- Discusses implementation strategies for applications needing frequent navigation

### [Depth Property Design](./depth-property-design.md)
**Why depth is optional but validated when present**

- Explains why `depth` is different from bidirectional relationships
- Shows validation rules that ensure depth consistency
- Provides query patterns for calculated vs. explicit depth
- Offers implementation guidelines for developers

## Key Principles

### 1. Single Source of Truth
- Store relationships in one direction (`parentAction`)
- Calculate derived information (children, depth) when needed
- Validate optional properties for consistency

### 2. Semantic Web Best Practices
- Avoid redundant data storage
- Use SPARQL for complex navigation
- Leverage class hierarchy for constraints

### 3. Pragmatic Flexibility
- Support both minimal and explicit data authoring
- Enable tooling optimization through optional properties
- Maintain validation robustness

## Quick Reference

### Finding Children
```sparql
# Direct children
SELECT ?child WHERE { ?child actions:parentAction ?parent }

# All descendants  
SELECT ?descendant WHERE { ?descendant actions:parentAction+ ?parent }
```

### Working with Depth
```sparql
# Calculate depth
SELECT (COUNT(?ancestor) as ?depth) WHERE {
    ?action (actions:parentAction)* ?ancestor .
    FILTER(?ancestor != ?action)
}

# Find by depth level
SELECT ?action WHERE {
    ?action actions:parentAction/actions:parentAction/actions:parentAction ?root .
    ?root a actions:RootAction .
    FILTER NOT EXISTS { ?action actions:parentAction/actions:parentAction/actions:parentAction/actions:parentAction ?deeper }
}
```

### Class Hierarchy
- `RootAction` (depth 0): No parent, may have children
- `ChildAction` (depth 1-4): Must have parent, may have children  
- `LeafAction` (depth 5): Must have parent, cannot have children

## Evolution Notes

The ontology has evolved through several iterations:

1. **v1.0**: Bidirectional relationships + required depth
2. **v2.0**: Unidirectional relationships, no depth
3. **v2.1**: Unidirectional relationships + optional validated depth ← Current

Each change improved semantic clarity while maintaining or enhancing functionality.

## Contributing

When making design changes:

1. Document the rationale (what problem does it solve?)
2. Show alternatives considered (why were they rejected?)
3. Provide usage examples (how should developers use it?)
4. Update validation rules (what constraints ensure correctness?)
5. Consider backward compatibility (how does it affect existing users?)

## Questions?

These documents capture the reasoning behind major design decisions. For implementation questions, see the test suite in `tests/` for comprehensive examples of valid and invalid usage patterns.