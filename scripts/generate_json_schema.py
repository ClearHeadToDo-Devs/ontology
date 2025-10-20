#!/usr/bin/env python3
"""
Generate JSON Schema from OWL Ontology + SHACL Shapes

OVERVIEW
========
This script implements the "small waist" architecture pattern for semantic interoperability.
It takes an OWL ontology (semantic domain model) and SHACL shapes (data validation rules)
and generates JSON Schema that can be used by downstream applications, APIs, and databases.

ARCHITECTURE
============
┌─────────────────────────┐    ┌─────────────────────────┐
│ OWL Ontology            │    │ SHACL Shapes            │
│ (Semantic Truth)        │    │ (Validation Rules)      │
│                         │    │                         │
│ • Class hierarchies     │    │ • Required fields       │
│ • Property domains      │    │ • Cardinality limits    │
│ • Schema.org alignment  │    │ • Data type constraints │
│ • Functional properties │    │ • Pattern validation    │
└─────────┬───────────────┘    └─────────┬───────────────┘
          │                              │
          └─────────────┬──────────────────┘
                        │
            ┌───────────▼────────────┐
            │ JSON Schema Generator  │
            │ (This Script)          │
            └───────────┬────────────┘
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
┌────▼────┐   ┌────────▼────────┐   ┌─────▼─────┐
│ Web APIs│   │ Database Schema │   │ UI Forms  │
│ OpenAPI │   │ SQL DDL         │   │ Validation│
└─────────┘   └─────────────────┘   └───────────┘

WHY BOTH OWL AND SHACL?
======================
• OWL defines WHAT CAN EXIST (open world assumption)
  - "Actions have names, priorities, and contexts"
  - "RootActions inherit from Actions"
  - "priority is a functional property (single-valued)"

• SHACL defines WHAT MUST EXIST for valid data (closed world validation)
  - "Actions MUST have exactly one name (required)"
  - "Priority MUST be an integer between 1-4"
  - "UUID MUST match version 7 pattern"

BENEFITS
========
1. **Single Source of Truth**: Ontology drives all downstream schemas
2. **Semantic Consistency**: Schema.org alignment ensures interoperability
3. **Code Generation**: Generate schemas for multiple languages/platforms
4. **Evolution Support**: Add new classes/properties without breaking existing code
5. **Validation Pipeline**: SHACL ensures data quality before persistence

INPUT FILES
===========
• actions-vocabulary.ttl: OWL 2 ontology with classes, properties, inheritance
• actions-shapes.ttl: SHACL NodeShapes with validation constraints

OUTPUT FILES
============
• schemas/action.schema.json: Base Action class schema
• schemas/rootaction.schema.json: Root-level action schema (inherits from Action)
• schemas/childaction.schema.json: Child action schema (inherits from Action)  
• schemas/leafaction.schema.json: Leaf action schema (inherits from Action)
• schemas/actions-combined.schema.json: Combined schema with $defs for references

EXAMPLE USAGE
=============
Command Line:
    uv run python scripts/generate_json_schema.py
    uv run invoke generate-schemas

Programmatic:
    generator = OntologyJSONSchemaGenerator()
    generator.load_files("actions-vocabulary.ttl", "actions-shapes.ttl")
    schemas = generator.generate_schemas()

EXAMPLE INPUT (OWL):
    actions:Action rdfs:subClassOf schema:Action ;
        rdfs:comment "A hierarchical task that can be performed" .
    
    actions:priority rdf:type owl:DatatypeProperty ;
        rdfs:domain actions:Action ;
        rdfs:range xsd:integer .

EXAMPLE INPUT (SHACL):
    actions:ActionShape sh:targetClass actions:Action ;
        sh:property [
            sh:path actions:priority ;
            sh:minCount 1 ;
            sh:minInclusive 1 ;
            sh:maxInclusive 4
        ] .

EXAMPLE OUTPUT (JSON Schema):
    {
      "type": "object",
      "properties": {
        "priority": {
          "type": "integer",
          "minimum": 1,
          "maximum": 4
        }
      },
      "required": ["priority"]
    }

EXAMPLE VALID JSON DATA:
    {
      "uuid": "01936194-d5b0-7890-8000-123456789abc",
      "name": "Review quarterly reports", 
      "description": "Analyze Q4 performance metrics",
      "priority": 2,
      "state": "active",
      "context": ["@office", "@computer"],
      "durationMinutes": 60
    }
"""

import json
import os
from typing import Dict, Any, Set, List
from pathlib import Path

# OWL handling with Owlready2
try:
    import owlready2 as owl
except ImportError:
    print("❌ Error: owlready2 not installed. Run: uv add owlready2")
    exit(1)

# SHACL handling with RDFLib (pySHACL uses it)
try:
    from rdflib import Graph, Namespace, SH, RDF, RDFS, XSD
except ImportError:
    print("❌ Error: rdflib not installed. Run: uv add rdflib")
    exit(1)

# Namespaces
ACTIONS = Namespace("https://vocab.example.org/actions/")
SCHEMA = Namespace("http://schema.org/")

class OntologyJSONSchemaGenerator:
    def __init__(self):
        self.ontology = None
        self.shacl_graph = Graph()
        
    def load_files(self, owl_file: str, shacl_file: str):
        """Load OWL with Owlready2 and SHACL with RDFLib."""
        print(f"🔍 Loading OWL ontology: {owl_file}")
        
        # Load the ontology file
        try:
            # Create a temporary world to avoid conflicts
            world = owl.World()
            # Load the ontology file - Owlready2 can be picky about file format detection
            # Try loading as turtle format explicitly
            try:
                self.ontology = world.get_ontology(f"file://{Path(owl_file).absolute()}").load()
            except Exception as e1:
                # If that fails, try using RDFLib to convert to a format Owlready2 likes better
                print(f"      Direct load failed ({e1}), trying RDFLib conversion...")
                temp_graph = Graph()
                temp_graph.parse(owl_file, format="turtle")
                temp_file = "temp_ontology.owl"
                temp_graph.serialize(temp_file, format="xml")
                self.ontology = world.get_ontology(f"file://{Path(temp_file).absolute()}").load()
                os.remove(temp_file)  # Clean up
                
            print(f"✅ Loaded ontology with {len(list(self.ontology.classes()))} classes")
        except Exception as e:
            print(f"❌ Error loading OWL file: {e}")
            raise
        
        print(f"🔍 Loading SHACL shapes: {shacl_file}")
        try:
            self.shacl_graph.parse(shacl_file, format="turtle")
            print(f"✅ Loaded SHACL graph with {len(self.shacl_graph)} triples")
        except Exception as e:
            print(f"❌ Error loading SHACL file: {e}")
            raise
            
    def generate_schemas(self) -> Dict[str, Any]:
        """Generate JSON schemas for all classes with SHACL shapes."""
        schemas = {}
        class_shapes = {}  # Group shapes by target class
        
        print("🔧 Finding classes with SHACL NodeShapes...")
        
        # Group all SHACL NodeShapes by target class
        shapes_found = 0
        for shape in self.shacl_graph.subjects(RDF.type, SH.NodeShape):
            shapes_found += 1
            target_class_uri = self.shacl_graph.value(shape, SH.targetClass)
            if target_class_uri:
                class_name = str(target_class_uri).split('/')[-1]
                if class_name not in class_shapes:
                    class_shapes[class_name] = {
                        'uri': str(target_class_uri),
                        'shapes': []
                    }
                class_shapes[class_name]['shapes'].append(shape)
        
        print(f"🔍 Found {shapes_found} SHACL shapes for {len(class_shapes)} classes")
        
        # Process each class with all its shapes
        for class_name, shape_info in class_shapes.items():
            print(f"   Processing class: {class_name} with {len(shape_info['shapes'])} shapes")
            
            # Find the corresponding Owlready2 class
            owl_class = self._find_owl_class(shape_info['uri'])
            if owl_class:
                print(f"   Generating schema for: {class_name}")
                schema = self._generate_class_schema(owl_class, shape_info['shapes'])
                schemas[class_name] = schema
                print(f"✅ Generated schema for: {class_name}")
            else:
                print(f"⚠️  Could not find OWL class for URI: {shape_info['uri']}")
                    
        return schemas
    
    def _find_owl_class(self, uri: str) -> owl.ThingClass:
        """Find Owlready2 class by URI."""
        for cls in self.ontology.classes():
            if str(cls.iri) == uri:
                return cls
        return None
    
    def _generate_class_schema(self, owl_class: owl.ThingClass, shacl_shapes: List) -> Dict[str, Any]:
        """Generate JSON schema combining OWL class info with SHACL constraints from multiple shapes."""
        
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "title": owl_class.name,
            "description": self._get_class_description(owl_class),
            "properties": {},
            "required": []
        }
        
        print(f"    Processing class: {owl_class.name}")
        
        # Get all properties available to this class via OWL semantics
        available_properties = self._get_class_properties(owl_class)
        print(f"    Found {len(available_properties)} properties from OWL")
        
        # Add base property schemas from OWL
        for prop in available_properties:
            prop_name = prop.name
            prop_schema = self._owl_property_to_json_schema(prop)
            schema["properties"][prop_name] = prop_schema
            
        # Apply SHACL constraints from all shapes
        total_constraints = 0
        for shacl_shape in shacl_shapes:
            constraints = self._apply_shacl_constraints(schema, shacl_shape)
            total_constraints += constraints
        
        if total_constraints > 0:
            print(f"    Applied {total_constraints} SHACL constraints from {len(shacl_shapes)} shapes")
        
        # Add inheritance via allOf if there are parent classes
        self._add_inheritance(schema, owl_class)
        
        # Clean up internal metadata from final schema
        self._clean_schema_metadata(schema)
        
        # Count properties - handle both direct and allOf structures
        prop_count = 0
        if 'properties' in schema:
            prop_count = len(schema['properties'])
        elif 'allOf' in schema:
            for item in schema['allOf']:
                if isinstance(item, dict) and 'properties' in item:
                    prop_count += len(item['properties'])
        print(f"    Generated schema with {prop_count} properties")
        return schema
    
    def _get_class_properties(self, owl_class: owl.ThingClass) -> Set[owl.Property]:
        """Get all properties available to this class."""
        properties = set()
        
        # Get properties from this class and all ancestors
        ancestors = list(owl_class.ancestors())
        all_classes = [owl_class] + ancestors
        
        for cls in all_classes:
            # Properties where this class is in domain
            for prop in self.ontology.properties():
                if hasattr(prop, 'domain') and prop.domain:
                    if cls in prop.domain:
                        properties.add(prop)
                        
        # Also include properties that are inherited through rdfs:subPropertyOf
        for prop in self.ontology.properties():
            # Check if this property is a subproperty of schema.org properties
            if hasattr(prop, 'is_a'):
                for parent in prop.is_a:
                    if hasattr(parent, 'iri') and 'schema.org' in str(parent.iri):
                        properties.add(prop)
                        
        return properties
    
    def _owl_property_to_json_schema(self, prop: owl.Property) -> Dict[str, Any]:
        """Convert Owlready2 property to base JSON schema."""
        prop_schema = {
            "title": prop.name,
            "description": self._get_property_description(prop)
        }
        
        # Determine type from range
        if hasattr(prop, 'range') and prop.range:
            range_class = prop.range[0] if prop.range else None
            if range_class:
                prop_schema.update(self._owl_range_to_json_type(range_class))
            
        # Handle functional properties
        if isinstance(prop, owl.FunctionalProperty):
            prop_schema["_is_functional"] = True
        else:
            prop_schema["_is_functional"] = False
            
        return prop_schema
    
    def _owl_range_to_json_type(self, range_class) -> Dict[str, Any]:
        """Convert OWL range to JSON Schema type."""
        
        # Handle XSD datatypes
        if hasattr(range_class, 'iri'):
            iri = str(range_class.iri)
            
            if 'string' in iri or 'String' in iri:
                return {"type": "string"}
            elif 'dateTime' in iri:
                return {"type": "string", "format": "date-time"}
            elif 'date' in iri:
                return {"type": "string", "format": "date"}
            elif 'integer' in iri or 'int' in iri:
                return {"type": "integer"}
            elif 'boolean' in iri:
                return {"type": "boolean"}
            elif 'decimal' in iri or 'float' in iri or 'double' in iri:
                return {"type": "number"}
                
        # Handle object properties (references to other classes)
        if hasattr(range_class, 'name'):
            # For individual schema files, don't use $ref since they won't have $defs
            # Instead, use a string type as a placeholder
            return {"type": "string", "description": f"Reference to {range_class.name}"}
            
        # Default
        return {"type": "string"}
    
    def _apply_shacl_constraints(self, schema: Dict[str, Any], shacl_shape) -> int:
        """Apply SHACL constraints to the schema and return count of constraints applied."""
        constraint_count = 0
        # Process property shapes
        for prop_shape in self.shacl_graph.objects(shacl_shape, SH.property):
            constraint_count += 1
            path = self.shacl_graph.value(prop_shape, SH.path)
            if not path:
                continue
                
            prop_name = str(path).split('/')[-1].split('#')[-1]
            
            if prop_name not in schema["properties"]:
                schema["properties"][prop_name] = {}
                
            prop_schema = schema["properties"][prop_name]
            
            # Apply constraints
            self._apply_property_constraints(prop_schema, prop_shape)
            
            # Check if required
            min_count = self.shacl_graph.value(prop_shape, SH.minCount)
            if min_count and int(min_count) > 0:
                if prop_name not in schema["required"]:
                    schema["required"].append(prop_name)
                    
        return constraint_count
    
    def _apply_property_constraints(self, prop_schema: Dict[str, Any], prop_shape):
        """Apply SHACL property constraints."""
        
        # Cardinality
        min_count = self.shacl_graph.value(prop_shape, SH.minCount)
        max_count = self.shacl_graph.value(prop_shape, SH.maxCount)
        
        is_functional = prop_schema.pop("_is_functional", False) if prop_schema else False
        
        # Ensure prop_schema is a dictionary
        if not prop_schema:
            prop_schema = {}
        
        # Handle array conversion
        if max_count and int(max_count) > 1:
            if prop_schema.get("type") != "array":
                item_schema = {k: v for k, v in prop_schema.items() 
                              if k not in ["title", "description"]}
                title = prop_schema.get("title", "")
                description = prop_schema.get("description", "")
                prop_schema.clear()
                prop_schema.update({
                    "type": "array",
                    "items": item_schema,
                    "title": title,
                    "description": description
                })
                
            if min_count:
                prop_schema["minItems"] = int(min_count)
            prop_schema["maxItems"] = int(max_count)
            
        # Datatype constraints
        datatype = self.shacl_graph.value(prop_shape, SH.datatype)
        if datatype:
            prop_schema.update(self._xsd_to_json_type(datatype))
            
        # String constraints
        pattern = self.shacl_graph.value(prop_shape, SH.pattern)
        if pattern:
            prop_schema["pattern"] = str(pattern)
            
        min_length = self.shacl_graph.value(prop_shape, SH.minLength)
        if min_length:
            prop_schema["minLength"] = int(min_length)
            
        max_length = self.shacl_graph.value(prop_shape, SH.maxLength)
        if max_length:
            prop_schema["maxLength"] = int(max_length)
            
        # Numeric constraints
        min_inclusive = self.shacl_graph.value(prop_shape, SH.minInclusive)
        if min_inclusive:
            prop_schema["minimum"] = int(min_inclusive)
            
        max_inclusive = self.shacl_graph.value(prop_shape, SH.maxInclusive)
        if max_inclusive:
            prop_schema["maximum"] = int(max_inclusive)
    
    def _xsd_to_json_type(self, xsd_type) -> Dict[str, Any]:
        """Convert XSD type to JSON Schema type."""
        type_str = str(xsd_type)
        
        if 'string' in type_str:
            return {"type": "string"}
        elif 'dateTime' in type_str:
            return {"type": "string", "format": "date-time"}
        elif 'date' in type_str:
            return {"type": "string", "format": "date"}
        elif 'integer' in type_str:
            return {"type": "integer"}
        elif 'boolean' in type_str:
            return {"type": "boolean"}
        else:
            return {"type": "string"}
    
    def _add_inheritance(self, schema: Dict[str, Any], owl_class: owl.ThingClass):
        """Add inheritance information using allOf."""
        # For individual schema files, don't add inheritance to avoid broken references
        # Inheritance will be handled in the combined schema
        if hasattr(owl_class, 'is_a'):
            # Filter out self-references and OWL Thing
            parents = [cls for cls in owl_class.is_a 
                      if hasattr(cls, 'name') 
                      and cls.name != 'Thing' 
                      and cls.name != owl_class.name  # Avoid self-reference
                      and not str(cls).startswith('schema.org')]  # Skip schema.org classes
        
            if parents and len(parents) > 0:
                # Add a note about inheritance without using $ref  
                parent_names = [parent.name for parent in parents]
                if schema.get("description"):
                    schema["description"] += f" (Inherits from: {', '.join(parent_names)})"
                else:
                    schema["description"] = f"Inherits from: {', '.join(parent_names)}"
    
    def _get_class_description(self, owl_class: owl.ThingClass) -> str:
        """Get class description from comment."""
        if hasattr(owl_class, 'comment') and owl_class.comment:
            if isinstance(owl_class.comment, list):
                return owl_class.comment[0] if owl_class.comment else ""
            else:
                return str(owl_class.comment)
        return ""
    
    def _get_property_description(self, prop: owl.Property) -> str:
        """Get property description from comment."""
        if hasattr(prop, 'comment') and prop.comment:
            if isinstance(prop.comment, list):
                return prop.comment[0] if prop.comment else ""
            else:
                return str(prop.comment)
        return ""

    def _clean_schema_metadata(self, schema: Dict[str, Any]):
        """Remove internal metadata like _is_functional from schema."""
        if 'properties' in schema:
            for prop_schema in schema['properties'].values():
                prop_schema.pop('_is_functional', None)
        elif 'allOf' in schema:
            for item in schema['allOf']:
                if isinstance(item, dict) and 'properties' in item:
                    for prop_schema in item['properties'].values():
                        prop_schema.pop('_is_functional', None)
def main():
    print("🚀 Starting JSON Schema generation from OWL ontology + SHACL shapes")
    
    generator = OntologyJSONSchemaGenerator()
    
    # Check if files exist
    owl_file = "actions-vocabulary.ttl"
    shacl_file = "actions-shapes.ttl"
    
    if not os.path.exists(owl_file):
        print(f"❌ OWL file not found: {owl_file}")
        return
        
    if not os.path.exists(shacl_file):
        print(f"❌ SHACL file not found: {shacl_file}")
        return
    
    try:
        generator.load_files(owl_file, shacl_file)
        schemas = generator.generate_schemas()
        
        if not schemas:
            print("⚠️  No schemas generated. Check that your SHACL file has NodeShapes with targetClass.")
            return
        
        # Create output directory
        os.makedirs("schemas", exist_ok=True)
        print(f"📁 Created schemas/ directory")
        
        # Write individual schema files
        for name, schema in schemas.items():
            filename = f"schemas/{name.lower()}.schema.json"
            with open(filename, 'w') as f:
                json.dump(schema, f, indent=2)
            print(f"✅ Generated: {filename}")
        
        # Combined schema
        combined = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://vocab.example.org/actions/schemas/actions.schema.json",
            "title": "Actions Ontology JSON Schemas",
            "description": "JSON Schema definitions generated from Actions OWL ontology and SHACL shapes",
            "$defs": schemas
        }
        
        with open("schemas/actions-combined.schema.json", 'w') as f:
            json.dump(combined, f, indent=2)
        print("✅ Generated: schemas/actions-combined.schema.json")
        
        print(f"🎉 Successfully generated {len(schemas)} JSON schemas!")
        
        # Show usage examples
        print("\n📖 USAGE EXAMPLES:")
        print("==================")
        print("Validate JSON data:")
        print("  pip install jsonschema")
        print("  python -c \"")
        print("import json")
        print("from jsonschema import validate")
        print("schema = json.load(open('schemas/action.schema.json'))")
        print("data = {'uuid': '01936194-d5b0-7890-8000-123456789abc', 'name': 'Test', 'priority': 2, 'state': 'active'}")
        print("validate(instance=data, schema=schema)")
        print("print('✅ Valid!')\"")
        print()
        print("Available schemas:")
        for name in schemas.keys():
            print(f"  • {name.lower()}.schema.json - {name} class schema")
        print("  • actions-combined.schema.json - All schemas with $defs")
        print()
        print("Example data files available in examples/ directory")
        print("See examples/README.md for integration guides")
        
    except Exception as e:
        print(f"❌ Error generating schemas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()