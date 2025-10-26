# Lessons Learned: OWL + SHACL → JSON Schema Generation

*For future AI assistants and human developers working on this codebase*

## 🎯 Core Architecture Insights

### ✅ What Worked Well

**"Small Waist" Architecture**
- OWL ontology + SHACL shapes as single source of truth is powerful
- JSON Schema generation enables multi-platform consumption
- Clear separation: OWL = "what CAN exist", SHACL = "what MUST exist"

**Tool Selection**
- **Owlready2** for OWL: Pythonic API beats raw RDFLib graph traversal
- **RDFLib** for SHACL: Mature, reliable SHACL constraint parsing
- **Specialized tools > generic**: Don't try to use one library for everything

**Multi-Shape Processing**
- SHACL shapes targeting same class needed to be grouped and processed together
- 16 shapes → 4 classes required careful deduplication logic
- Multiple constraints per property from different shapes works well

### ❌ What Didn't Work Initially

**Inheritance Assumptions**
- SHACL inheritance is NOT automatic (unlike OWL)
- Child classes don't inherit parent SHACL constraints by default
- Had to disable `allOf` inheritance in individual schemas due to broken references

**Cross-Reference Complexity**  
- Individual schema files can't resolve `$ref` to missing `$defs`
- Combined schema vs individual schemas have different reference needs
- Started with complex inheritance, had to simplify to string types

## 🔧 Technical Gotchas

### File Format Issues
```python
# Owlready2 struggles with Turtle files
try:
    ontology = world.get_ontology(f"file://{path}").load()
except:
    # ALWAYS have RDFLib fallback for Turtle parsing
    temp_graph = Graph()
    temp_graph.parse(owl_file, format="turtle") 
    temp_graph.serialize("temp.owl", format="xml")
    ontology = world.get_ontology(f"file://{temp_file}").load()
```

### SHACL Inheritance Gap
```python
# This was a key insight - SHACL constraints don't inherit automatically
# actions:ActionShape targets actions:Action
# actions:RootActionShape targets actions:RootAction  
# RootAction instances DON'T automatically get ActionShape constraints
# Must manually apply parent constraints to child classes if needed
```

### Reference Resolution  
```python
# WRONG: Breaks validation in individual schemas
{"$ref": "#/$defs/ActionState"}  # ActionState not defined in individual file

# RIGHT: Self-contained schemas
{"type": "string", "description": "Reference to ActionState"}
```

## 📋 Development Process Lessons

### Start Simple, Add Complexity
1. **First**: Get basic property extraction working
2. **Then**: Add SHACL constraint application  
3. **Then**: Handle multiple shapes per class
4. **Finally**: Optimize inheritance and references

### Debugging is Critical
```python
# Extensive logging was essential for debugging
print(f"    Processing class: {owl_class.name}")
print(f"    Found {len(properties)} properties from OWL")
print(f"    Applied {constraints} SHACL constraints from {len(shapes)} shapes")
```

### Example Data + Validation Tests
- Created both valid AND invalid examples
- Automated validation tests caught schema bugs immediately  
- Examples serve as living documentation

## 🏗️ Code Organization Insights

### Script Structure That Worked
```python
class OntologyJSONSchemaGenerator:
    def load_files()           # File I/O with fallbacks
    def generate_schemas()     # Main orchestration  
    def _get_class_properties() # OWL semantics
    def _apply_shacl_constraints() # SHACL validation
    def _clean_schema_metadata()   # Output cleanup
```

### Task Runner Integration
```python
# Having invoke tasks made development much smoother
@task
def full_pipeline(c):
    validate(c)        # Check TTL syntax
    generate_schemas(c) # Generate JSON Schema  
    test_examples(c)   # Validate with real data
```

## 📚 Documentation That Matters

### For Future AI Assistants

**Essential Context**:
- Understand OWL vs SHACL boundaries clearly
- Know that SHACL inheritance isn't automatic
- JSON Schema reference resolution varies by use case
- Owlready2 has Turtle parsing limitations

**Architecture Diagrams**:
- Visual "small waist" concept is worth 1000 words
- Show data flow: OWL+SHACL → Generator → Multiple Outputs

**Working Examples**:
- Valid/invalid data examples prevent schema bugs
- Integration examples (OpenAPI, SQL, TypeScript) show real value
- Command line examples for immediate testing

### For Human Developers

**Onboarding Checklist**:
1. Read `SCHEMA_GENERATION.md` for overview
2. Run `uv run invoke full-pipeline` to see it work  
3. Look at `examples/` for data patterns
4. Check `scripts/generate_json_schema.py` docstring for architecture

**Common Pitfalls**:
- Don't assume SHACL constraints inherit
- Individual schemas can't use cross-references  
- Owlready2 may need RDFLib fallback for Turtle files
- Multiple SHACL shapes per class need grouping

## 🔮 Future Enhancement Guidelines

### Adding New Schema Formats
```python
# Follow this pattern for extensibility
def generate_typescript_types(self) -> Dict[str, str]:
    # Use same OWL property extraction
    # Apply same SHACL constraints  
    # Output TypeScript instead of JSON Schema
```

### Extending SHACL Support
- Add support for `sh:or`, `sh:and`, `sh:not` constraints
- Handle `sh:sparql` custom validation rules
- Support `sh:closed` for additional property restrictions

### Performance Optimization  
- Cache OWL property extraction results
- Parallel processing of multiple classes
- Incremental generation for large ontologies

## ⚡ Key Commands for Future Work

```bash
# Development cycle
uv run invoke validate          # Check ontology syntax
uv run invoke generate-schemas  # Generate JSON Schema
uv run invoke test-examples     # Validate with data
uv run invoke full-pipeline     # All of the above

# Debugging
jq '.properties.priority' schemas/action.schema.json  # Check specific property
jq '.required' schemas/action.schema.json             # Check required fields  
jq '.["$defs"] | keys' schemas/actions-combined.schema.json # Check definitions
```

## 🎯 Success Metrics

**What Success Looks Like**:
- All validation tests pass (5/5)
- Schemas validate real-world data
- Generated schemas are self-contained and usable
- Documentation enables independent development
- Pipeline runs end-to-end without errors

**Red Flags**:
- Broken `$ref` links in individual schemas
- SHACL constraints not applying to subclasses  
- Owlready2 parsing failures without fallback
- Missing required fields in generated schemas

## 🚀 For Your Next Session

**Context to Remember**:
- This implements "small waist" architecture successfully
- OWL ontology defines semantic structure
- SHACL shapes define validation constraints  
- JSON Schema enables multi-platform consumption
- Examples and tests are crucial for correctness

**Files to Check First**:
1. `scripts/generate_json_schema.py` - Main implementation
2. `examples/test_validation.py` - Validation test suite  
3. `schemas/action.schema.json` - Reference implementation
4. `tasks.py` - Development workflow

The system works well and is ready for extension to other schema formats (TypeScript, SQL DDL, GraphQL, etc.). The foundation is solid!