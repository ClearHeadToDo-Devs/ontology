# JSON Schema Generation from OWL + SHACL

This document explains the JSON Schema generation system that converts your Actions Ontology (OWL) and SHACL validation shapes into usable JSON Schema files.

## 🎯 Purpose

Implements the **"small waist" architecture** where your OWL ontology + SHACL shapes serve as the **single source of semantic truth** that generates all downstream artifacts:

```
┌─────────────────────────┐    ┌─────────────────────────┐
│ OWL Ontology            │    │ SHACL Shapes            │
│ (What CAN exist)        │    │ (What MUST exist)       │
└─────────┬───────────────┘    └─────────┬───────────────┘
          │                              │
          └─────────────┬──────────────────┘
                        │
            ┌───────────▼────────────┐
            │ JSON Schema Generator  │
            └───────────┬────────────┘
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
┌────▼────┐   ┌────────▼────────┐   ┌─────▼─────┐
│ Web APIs│   │ Database Schema │   │ UI Forms  │
│ OpenAPI │   │ SQL DDL         │   │ Validation│
└─────────┘   └─────────────────┘   └───────────┘
```

## 🔧 How It Works

### Input Processing
1. **OWL Ontology** (`actions-vocabulary.ttl`):
   - Loads with Owlready2 (with RDFLib fallback for Turtle files)
   - Extracts classes, properties, inheritance hierarchies
   - Identifies functional properties, domain/range constraints
   - Preserves Schema.org alignments

2. **SHACL Shapes** (`actions-shapes.ttl`):
   - Parses with RDFLib 
   - Groups multiple shapes by target class
   - Extracts validation constraints (cardinality, patterns, types)
   - Identifies required fields via `sh:minCount`

### Schema Generation
1. **Base Properties**: All properties available to each class via OWL domain/range
2. **SHACL Constraints**: Validation rules applied from all matching shapes
3. **Type Conversion**: XSD datatypes → JSON Schema types
4. **Inheritance Hints**: Semantic relationships noted in descriptions

### Key Features
✅ **Multi-shape processing**: Handles 16 SHACL shapes targeting 4 classes  
✅ **Comprehensive constraints**: UUID patterns, priority ranges, required fields  
✅ **Self-contained schemas**: Individual files work without external references  
✅ **Clean metadata**: Internal processing markers removed from output  
✅ **Schema.org compatibility**: Inherits from Schema.org Action  

## 📁 Generated Files

### Individual Schemas (Self-contained)
- **`action.schema.json`**: Base Action class (23 properties, 3 required)
- **`rootaction.schema.json`**: Root-level actions (24 properties, 0 required)  
- **`childaction.schema.json`**: Child actions (24 properties, 1 required)
- **`leafaction.schema.json`**: Leaf actions (24 properties, 1 required)

### Combined Schema (With References)
- **`actions-combined.schema.json`**: All schemas in `$defs` for cross-referencing

## 🚀 Usage

### Command Line
```bash
# Generate schemas from ontology
uv run invoke generate-schemas

# Test with example data  
uv run invoke test-examples

# Run complete pipeline
uv run invoke full-pipeline

# Clean up
uv run invoke clean
```

### Programmatic
```python
generator = OntologyJSONSchemaGenerator()
generator.load_files("actions-vocabulary.ttl", "actions-shapes.ttl") 
schemas = generator.generate_schemas()
```

### Validation Example
```python
import json
from jsonschema import validate

# Load schema and data
schema = json.load(open('schemas/action.schema.json'))
data = {
    "uuid": "01936194-d5b0-7890-8000-123456789abc",
    "name": "Review quarterly reports",
    "priority": 2,
    "state": "active"
}

# Validate
validate(instance=data, schema=schema)  # ✅ Valid!
```

## 📋 Schema Details

### Action Schema Highlights
```json
{
  "type": "object",
  "title": "Action", 
  "required": ["name", "priority", "state"],
  "properties": {
    "uuid": {
      "type": "string",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    },
    "priority": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4
    },
    "durationMinutes": {
      "type": "integer", 
      "minimum": 1,
      "maximum": 10080
    },
    "context": {
      "type": "string",
      "pattern": "^@[a-zA-Z0-9_-]+$"
    }
  }
}
```

### Key Constraints Applied
- **UUID**: Version 7 format validation
- **Priority**: 1-4 integer (Eisenhower Matrix)
- **Duration**: 1-10080 minutes (max 1 week)
- **Context**: GTD-style @context pattern
- **Required**: name, priority, state fields

## 🔄 Integration Examples

### OpenAPI/Swagger
```yaml
components:
  schemas:
    Action:
      $ref: 'schemas/action.schema.json'
    CreateAction:
      allOf:
        - $ref: '#/components/schemas/Action'
        - required: [name, priority]
```

### Database Schema (PostgreSQL)
```sql
CREATE TABLE actions (
    uuid UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    priority INTEGER CHECK (priority BETWEEN 1 AND 4) NOT NULL,
    state VARCHAR(50) NOT NULL,
    duration_minutes INTEGER CHECK (duration_minutes BETWEEN 1 AND 10080),
    -- ... other columns derived from schema
);
```

### TypeScript Types
```typescript
// Generated from JSON Schema
interface Action {
  uuid: string; // UUID v7 pattern
  name: string;
  priority: 1 | 2 | 3 | 4;
  state: string;
  durationMinutes?: number; // 1-10080
  context?: string; // @context pattern
  // ... other properties
}
```

## 🧪 Example Data

### Valid Action
```json
{
  "uuid": "01936194-d5b0-7890-8000-123456789abc",
  "name": "Review quarterly reports",
  "description": "Analyze Q4 performance metrics", 
  "priority": 2,
  "state": "active",
  "context": "@office",
  "durationMinutes": 90
}
```

### Valid Root Action (With Project)
```json
{
  "uuid": "01936194-d5b0-7890-8000-abcdef123456",
  "name": "Launch new product feature",
  "priority": "1",
  "state": "active", 
  "project": "Q1-2025-Dashboard",
  "context": "@computer"
}
```

### Valid Child Action (With Parent)
```json
{
  "uuid": "01936194-d5b0-7890-8000-fedcba654321",
  "name": "Implement user authentication",
  "priority": "1", 
  "state": "active",
  "parentAction": "01936194-d5b0-7890-8000-abcdef123456",
  "context": "@computer"
}
```

## 🎯 Benefits

1. **Single Source of Truth**: Ontology changes automatically update all schemas
2. **Semantic Consistency**: Schema.org alignment ensures interoperability  
3. **Code Generation**: Generate database schemas, TypeScript types, API specs
4. **Validation Pipeline**: SHACL ensures data quality before persistence
5. **Evolution Support**: Add new classes/properties without breaking existing code

## 🔮 Future Extensions

- **Database DDL generation**: PostgreSQL, MySQL, MongoDB schemas
- **TypeScript type generation**: Compile-time validation  
- **GraphQL schema generation**: API development
- **Tree-sitter parser generation**: File format parsing
- **OpenAPI specification generation**: REST API documentation

## 🚦 Status

✅ **Working**: JSON Schema generation from OWL + SHACL  
✅ **Tested**: Validation examples with real data  
✅ **Integrated**: Build system tasks and pipeline  
✅ **Documented**: Usage examples and integration guides  

The foundation is solid for your "small waist" architecture - your ontology now drives downstream schema generation!