# JSON Schema Examples

This directory contains example JSON data that demonstrates how to use the generated JSON schemas from your Actions Ontology.

## Generated Schemas

The `generate-schemas` command creates these schema files:

- **`action.schema.json`** - Base Action class with all common properties
- **`rootaction.schema.json`** - Root-level actions (can have projects, no parents)
- **`childaction.schema.json`** - Child actions (must have parents, no projects)  
- **`leafaction.schema.json`** - Leaf actions (terminal nodes in hierarchy)
- **`actions-combined.schema.json`** - Combined schema with `$defs` for referencing

## Example Data Files

### Valid Examples
- **`valid-action.json`** - A basic action with all required fields
- **`valid-rootaction.json`** - A root action with project assignment
- **`valid-childaction.json`** - A child action with parent reference

### Invalid Examples  
- **`invalid-action-examples.json`** - Common validation errors to avoid

## Validation Examples

### Using Node.js with AJV
```bash
npm install ajv ajv-formats
```

```javascript
const Ajv = require('ajv')
const addFormats = require('ajv-formats')
const fs = require('fs')

const ajv = new Ajv()
addFormats(ajv)

// Load schema
const schema = JSON.parse(fs.readFileSync('../schemas/action.schema.json'))
const validate = ajv.compile(schema)

// Validate data
const data = JSON.parse(fs.readFileSync('valid-action.json'))
const valid = validate(data)

if (!valid) {
  console.log('Validation errors:', validate.errors)
} else {
  console.log('✅ Data is valid!')
}
```

### Using Python with jsonschema
```bash
pip install jsonschema
```

```python
import json
from jsonschema import validate, ValidationError

# Load schema and data
with open('../schemas/action.schema.json') as f:
    schema = json.load(f)
    
with open('valid-action.json') as f:
    data = json.load(f)

try:
    validate(instance=data, schema=schema)
    print("✅ Data is valid!")
except ValidationError as e:
    print(f"❌ Validation error: {e.message}")
```

### Using curl with online validators
```bash
# Validate against remote JSON Schema validator
curl -X POST \
  -H "Content-Type: application/json" \
  -d @valid-action.json \
  "https://www.jsonschemavalidator.net/api/validate"
```

## Key Properties Explained

### Required Fields (all actions)
- **`name`** - Human-readable action title
- **`priority`** - Integer 1-4 (Eisenhower Matrix: 1=urgent+important, 4=neither)  
- **`state`** - Current action state (active, completed, someday, etc.)

### UUID Format
- **`uuid`** - Version 7 UUID for time-ordered uniqueness
- Pattern: `01936194-d5b0-7890-8000-123456789abc`
- First part encodes timestamp for natural sorting

### Hierarchical Properties
- **`parentAction`** - UUID reference to parent action (required for child/leaf actions)
- **`project`** - Project/story name (only allowed on root actions)

### Time Properties  
- **`doDateTime`** - When to work on this (scheduling)
- **`dueDateTime`** - When it must be completed (deadline)
- **`completedDateTime`** - When it was actually finished (tracking)

### GTD Properties
- **`context`** - Where/how action can be performed (`@office`, `@phone`, `@computer`)
- **`durationMinutes`** - Estimated time to complete (1-10080 minutes = 1 week max)

## Schema Inheritance

The schemas use JSON Schema `allOf` to model OWL class inheritance:

```json
{
  "allOf": [
    {"$ref": "#/$defs/Action"},  // Inherit base Action properties
    {
      "type": "object",
      "properties": {
        "project": {"type": "string"}  // Add RootAction-specific properties
      }
    }
  ]
}
```

This ensures:
- **Consistency**: All action types share base properties
- **Extensibility**: Each subclass can add specific constraints
- **Validation**: Inheritance rules are enforced at validation time

## Integration Examples

### OpenAPI Specification
```yaml
components:
  schemas:
    Action:
      $ref: '../schemas/action.schema.json'
    CreateActionRequest:
      allOf:
        - $ref: '#/components/schemas/Action'
        - required: [name, priority]
```

### Database Migration (PostgreSQL)
```sql
-- Generate table schema from JSON Schema
CREATE TABLE actions (
    uuid UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    priority INTEGER CHECK (priority BETWEEN 1 AND 4) NOT NULL,
    state VARCHAR(50) NOT NULL,
    context VARCHAR(100),
    duration_minutes INTEGER CHECK (duration_minutes BETWEEN 1 AND 10080),
    do_datetime TIMESTAMPTZ,
    due_datetime TIMESTAMPTZ,
    completed_datetime TIMESTAMPTZ,
    parent_action UUID REFERENCES actions(uuid),
    project VARCHAR(100)
);
```

### React Form Validation
```typescript
import { JSONSchema7 } from 'json-schema'
import actionSchema from '../schemas/action.schema.json'

interface Action {
  uuid: string
  name: string
  priority: 1 | 2 | 3 | 4
  state: string
  // ... other properties inferred from schema
}

const validateAction = (data: unknown): data is Action => {
  // Use schema for runtime validation
  return ajv.validate(actionSchema, data)
}
```

## Next Steps

1. **Try validation** - Use the examples above to validate your own data
2. **Generate code** - Use tools like `quicktype` to generate types from schemas
3. **Integrate APIs** - Reference schemas in OpenAPI specifications
4. **Database schemas** - Generate DDL from JSON Schema constraints
5. **Extend schemas** - Add new properties to ontology and regenerate

The beauty of this approach is that your ontology serves as the single source of truth, and all downstream artifacts (JSON Schema, TypeScript types, database schemas) can be generated automatically!