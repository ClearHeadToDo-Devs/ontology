#!/usr/bin/env python3
"""
Generate JSON Type Definition (JTD) from OWL Ontology + SHACL Shapes

⚠️  EXPERIMENTAL STATUS
========================
This is an experimental alternative to JSON Schema generation focused on
code generation rather than validation. See SCHEMA_GENERATION_DECISION.md
for rationale and comparison.

OVERVIEW
========
This script generates JTD (RFC 8927) schemas from the same OWL+SHACL sources
that drive JSON Schema generation. JTD is optimized for:
- Code generation (Rust, TypeScript, Go, Python)
- Simpler type mappings
- Reduced schema complexity

Unlike JSON Schema (which excels at validation), JTD excels at generating
clean, idiomatic type definitions in statically-typed languages.

ARCHITECTURE
============
┌─────────────────────────┐    ┌─────────────────────────┐
│ OWL Ontology            │    │ SHACL Shapes            │
│ (Semantic Truth)        │    │ (Validation Rules)      │
│                         │    │                         │
│ • Class hierarchies     │    │ • Required fields       │
│ • Property domains      │    │ • Cardinality limits    │
│ • BFO/CCO alignment     │    │ • Data type constraints │
│ • Functional properties │    │ • Value ranges          │
└─────────┬───────────────┘    └─────────┬───────────────┘
          │                              │
          └─────────────┬──────────────────┘
                        │
            ┌───────────▼────────────┐
            │ JTD Generator          │
            │ (This Script)          │
            └───────────┬────────────┘
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
┌────▼────┐   ┌────────▼────────┐   ┌─────▼─────┐
│ Rust    │   │ TypeScript      │   │ Go        │
│ Structs │   │ Interfaces      │   │ Structs   │
└─────────┘   └─────────────────┘   └───────────┘

WHY JTD ALONGSIDE JSON SCHEMA?
==============================
• JSON Schema: Runtime validation, complex constraints, documentation
• JTD: Code generation, simple types, compile-time safety

Both are generated from the same ontology source, ensuring consistency.

JTD ADVANTAGES
==============
1. **Precise Integer Types**: uint8, int8, uint16, etc. (vs JSON Schema's "integer")
2. **Cleaner Code Generation**: Maps directly to language type systems
3. **Simpler Schemas**: Less verbose than JSON Schema
4. **Timestamp Support**: Native timestamp type for ISO 8601 datetime

JTD LIMITATIONS
===============
1. **No 64-bit Integers**: JTD omits int64/uint64 due to JSON precision issues
2. **No Pattern Matching**: Cannot express regex constraints
3. **Limited Validation**: No conditional logic, no custom validation
4. **Smaller Ecosystem**: Fewer tools than JSON Schema

EXAMPLE OUTPUT (JTD):
=====================
{
  "properties": {
    "name": { "type": "string" },
    "priority": { "type": "uint8" },
    "state": {
      "enum": ["NotStarted", "InProgress", "Completed", "Blocked", "Cancelled"]
    }
  },
  "optionalProperties": {
    "contexts": {
      "elements": { "type": "string" }
    },
    "durationMinutes": { "type": "uint16" }
  }
}

USAGE
=====
Command Line:
    uv run python scripts/generate_jtd.py
    uv run invoke generate-jtd

Code Generation (Rust):
    jtd-codegen schemas/action.jtd.json --rust-out src/models/

Code Generation (TypeScript):
    jtd-codegen schemas/action.jtd.json --typescript-out src/types/

For more details:
- RFC 8927: https://datatracker.ietf.org/doc/html/rfc8927
- JTD Codegen: https://github.com/jsontypedef/json-typedef-codegen
- SCHEMA_GENERATION_DECISION.md: Design decision documentation
"""

import json
import os
from typing import Dict, Any, Set, List, Optional
from pathlib import Path

# OWL handling with Owlready2
try:
    import owlready2 as owl
except ImportError:
    print("❌ Error: owlready2 not installed. Run: uv add owlready2")
    exit(1)

# SHACL handling with RDFLib
try:
    from rdflib import Graph, Namespace, SH, RDF, RDFS, XSD
except ImportError:
    print("❌ Error: rdflib not installed. Run: uv add rdflib")
    exit(1)

# Namespaces
ACTIONS = Namespace("https://vocab.clearhead.io/actions/v3#")
SCHEMA = Namespace("http://schema.org/")


class OntologyJTDGenerator:
    """
    Generate JSON Type Definition (JTD) schemas from OWL ontology.

    JTD is simpler than JSON Schema and optimized for code generation.
    This class mirrors OntologyJSONSchemaGenerator but produces JTD output.
    """

    def __init__(self):
        self.ontology = None
        self.shacl_graph = Graph()

    def load_files(self, owl_file: str, shacl_file: Optional[str] = None):
        """Load OWL with Owlready2 and optionally SHACL with RDFLib."""
        print(f"🔍 Loading OWL ontology: {owl_file}")

        try:
            world = owl.World()
            try:
                self.ontology = world.get_ontology(f"file://{Path(owl_file).absolute()}").load()
            except Exception as e1:
                print(f"      Direct load failed ({e1}), trying RDFLib conversion...")
                temp_graph = Graph()
                temp_graph.parse(owl_file)
                temp_file = "temp_ontology.owl"
                temp_graph.serialize(temp_file, format="xml")
                self.ontology = world.get_ontology(f"file://{Path(temp_file).absolute()}").load()
                os.remove(temp_file)

            print(f"✅ Loaded ontology with {len(list(self.ontology.classes()))} classes")
        except Exception as e:
            print(f"❌ Error loading OWL file: {e}")
            raise

        if shacl_file and os.path.exists(shacl_file):
            print(f"🔍 Loading SHACL shapes: {shacl_file}")
            try:
                self.shacl_graph.parse(shacl_file, format="turtle")
                print(f"✅ Loaded SHACL graph with {len(self.shacl_graph)} triples")
            except Exception as e:
                print(f"❌ Error loading SHACL file: {e}")
                raise
        else:
            print("⚠️  No SHACL file provided - using OWL constraints only")

    def generate_schemas(self) -> Dict[str, Any]:
        """Generate JTD schemas for all classes in the ontology."""
        schemas = {}

        print("🔧 Generating JTD schemas for ontology classes...")

        # For now, generate schemas for all concrete classes
        # (In future, could filter by SHACL NodeShapes like JSON Schema generator)
        for owl_class in self.ontology.classes():
            # Skip abstract/imported classes
            if self._should_skip_class(owl_class):
                continue

            class_name = owl_class.name
            print(f"   Processing class: {class_name}")

            schema = self._generate_class_schema(owl_class)
            schemas[class_name] = schema
            print(f"✅ Generated JTD schema for: {class_name}")

        return schemas

    def _should_skip_class(self, owl_class: owl.ThingClass) -> bool:
        """Determine if we should skip generating a schema for this class."""
        # Skip owl:Thing
        if owl_class.name == 'Thing':
            return True

        # Skip classes from imported ontologies (BFO, CCO)
        iri = str(owl_class.iri)
        if 'basic-formal-ontology' in iri or 'commoncoreontologies' in iri:
            return True

        return False

    def _generate_class_schema(self, owl_class: owl.ThingClass) -> Dict[str, Any]:
        """
        Generate JTD schema for a single class.

        JTD has a simpler structure than JSON Schema:
        {
          "properties": { ... },           // Required properties
          "optionalProperties": { ... },   // Optional properties
          "definitions": { ... }           // Nested type definitions
        }
        """
        schema = {
            "metadata": {
                "description": self._get_class_description(owl_class),
                "javaPackage": "io.clearhead.actions",
                "typescriptType": owl_class.name
            }
        }

        # Collect properties
        required_props = {}
        optional_props = {}

        available_properties = self._get_class_properties(owl_class)
        print(f"    Found {len(available_properties)} properties from OWL")

        for prop in available_properties:
            prop_name = prop.name
            jtd_type = self._owl_property_to_jtd_type(prop)

            # Determine if required based on SHACL or OWL
            is_required = self._is_required_property(prop, owl_class)

            if is_required:
                required_props[prop_name] = jtd_type
            else:
                optional_props[prop_name] = jtd_type

        # Add to schema
        if required_props:
            schema["properties"] = required_props
        if optional_props:
            schema["optionalProperties"] = optional_props

        print(f"    Generated schema with {len(required_props)} required, {len(optional_props)} optional properties")
        return schema

    def _get_class_properties(self, owl_class: owl.ThingClass) -> Set[owl.Property]:
        """Get all properties available to this class (including inherited)."""
        properties = set()

        # Get properties from this class and all ancestors
        ancestors = list(owl_class.ancestors())
        all_classes = [owl_class] + ancestors

        for cls in all_classes:
            # Skip imported classes
            if 'basic-formal-ontology' in str(cls.iri) or 'commoncoreontologies' in str(cls.iri):
                continue

            # Properties where this class is in domain
            for prop in self.ontology.properties():
                if hasattr(prop, 'domain') and prop.domain:
                    if cls in prop.domain:
                        # Skip properties from imported ontologies
                        if 'commoncoreontologies' in str(prop.iri):
                            continue
                        properties.add(prop)

        return properties

    def _owl_property_to_jtd_type(self, prop: owl.Property) -> Dict[str, Any]:
        """
        Convert OWL property to JTD type.

        JTD types:
        - type: "boolean" | "string" | "timestamp" |
                "float32" | "float64" |
                "int8" | "uint8" | "int16" | "uint16" | "int32" | "uint32"
        - enum: [...]
        - elements: { ... }  // For arrays
        - ref: "..."         // For references to definitions
        """

        # Check for cardinality (array vs single value)
        is_array = not isinstance(prop, owl.FunctionalProperty)

        # Determine base type from OWL range
        if hasattr(prop, 'range') and prop.range:
            range_class = prop.range[0] if prop.range else None
            base_type = self._owl_range_to_jtd_type(range_class, prop)
        else:
            base_type = {"type": "string"}  # Default

        # Wrap in array if needed
        if is_array and not self._looks_like_enum(prop):
            return {"elements": base_type}
        else:
            return base_type

    def _owl_range_to_jtd_type(self, range_class, prop: owl.Property) -> Dict[str, Any]:
        """Convert OWL range to JTD type with intelligent type selection."""

        if not range_class or not hasattr(range_class, 'iri'):
            return {"type": "string"}

        iri = str(range_class.iri)
        prop_name = prop.name.lower() if prop else ""

        # Check for enums (named individuals of a class)
        if hasattr(range_class, 'instances') and list(range_class.instances()):
            enum_values = [ind.name for ind in range_class.instances() if hasattr(ind, 'name')]
            if enum_values:
                return {"enum": enum_values}

        # String types
        if 'string' in iri or 'String' in iri:
            return {"type": "string"}

        # Timestamp types
        if 'dateTime' in iri or 'datetime' in prop_name:
            return {"type": "timestamp"}

        # Integer types - use smart sizing based on property name and expected range
        if 'integer' in iri or 'int' in iri:
            # Priority: 1-4 fits in uint8
            if 'priority' in prop_name:
                return {"type": "uint8"}
            # Duration in minutes: up to 10080 (1 week) fits in uint16
            elif 'duration' in prop_name and 'minutes' in prop_name:
                return {"type": "uint16"}
            # Default to int32 for general integers
            else:
                return {"type": "int32"}

        # Boolean
        if 'boolean' in iri:
            return {"type": "boolean"}

        # Float types
        if 'decimal' in iri or 'float' in iri:
            return {"type": "float32"}
        if 'double' in iri:
            return {"type": "float64"}

        # Object references (to other classes)
        if hasattr(range_class, 'name') and range_class.name != 'string':
            # For references to other types, use string (UUID reference)
            # In a more complete implementation, could use {"ref": range_class.name}
            return {"type": "string"}

        # Default
        return {"type": "string"}

    def _is_required_property(self, prop: owl.Property, owl_class: owl.ThingClass) -> bool:
        """
        Determine if a property is required.

        Checks:
        1. SHACL sh:minCount > 0
        2. OWL FunctionalProperty (implies single value, but not required)

        For now, using conservative approach: only required if explicitly marked.
        """
        # Check SHACL constraints if available
        if len(self.shacl_graph) > 0:
            # Find shape for this class
            for shape in self.shacl_graph.subjects(RDF.type, SH.NodeShape):
                target_class = self.shacl_graph.value(shape, SH.targetClass)
                if target_class and str(target_class) == str(owl_class.iri):
                    # Find property constraint
                    for prop_shape in self.shacl_graph.objects(shape, SH.property):
                        path = self.shacl_graph.value(prop_shape, SH.path)
                        if path and str(path) == str(prop.iri):
                            min_count = self.shacl_graph.value(prop_shape, SH.minCount)
                            if min_count and int(min_count) > 0:
                                return True

        # Default to optional
        return False

    def _looks_like_enum(self, prop: owl.Property) -> bool:
        """Check if property looks like it should be a single enum value rather than array."""
        # Functional properties are single-valued
        if isinstance(prop, owl.FunctionalProperty):
            return True

        # Properties with "state" or "status" in name are usually single-valued enums
        prop_name = prop.name.lower()
        if 'state' in prop_name or 'status' in prop_name:
            return True

        return False

    def _get_class_description(self, owl_class: owl.ThingClass) -> str:
        """Get class description from comment."""
        if hasattr(owl_class, 'comment') and owl_class.comment:
            if isinstance(owl_class.comment, list):
                return owl_class.comment[0] if owl_class.comment else ""
            else:
                return str(owl_class.comment)
        return f"{owl_class.name} from Actions Vocabulary"


def main():
    """Main entry point for JTD generation."""
    print("🚀 Starting JTD generation from OWL ontology")
    print("⚠️  EXPERIMENTAL: JTD generation is experimental. See SCHEMA_GENERATION_DECISION.md")
    print()

    generator = OntologyJTDGenerator()

    # Check for v3 ontology file
    owl_file = "actions-vocabulary.owl"
    shacl_file = "actions-shapes.ttl" if os.path.exists("actions-shapes.ttl") else None

    if not os.path.exists(owl_file):
        print(f"❌ OWL file not found: {owl_file}")
        print("   Make sure you're running from the ontology directory")
        return

    try:
        generator.load_files(owl_file, shacl_file)
        schemas = generator.generate_schemas()

        if not schemas:
            print("⚠️  No schemas generated.")
            return

        # Create output directory
        os.makedirs("schemas/jtd", exist_ok=True)
        print(f"📁 Created schemas/jtd/ directory")

        # Write individual JTD schema files
        for name, schema in schemas.items():
            filename = f"schemas/jtd/{name.lower()}.jtd.json"
            with open(filename, 'w') as f:
                json.dump(schema, f, indent=2)
            print(f"✅ Generated: {filename}")

        # Combined schema with definitions
        combined = {
            "metadata": {
                "description": "Actions Vocabulary v3 - JTD Type Definitions",
                "version": "3.1.0"
            },
            "definitions": schemas
        }

        with open("schemas/jtd/actions-combined.jtd.json", 'w') as f:
            json.dump(combined, f, indent=2)
        print("✅ Generated: schemas/jtd/actions-combined.jtd.json")

        print(f"\n🎉 Successfully generated {len(schemas)} JTD schemas!")

        # Show usage examples
        print("\n📖 USAGE EXAMPLES:")
        print("==================")
        print("Generate Rust code:")
        print("  cargo install jtd-codegen")
        print("  jtd-codegen schemas/jtd/actionplan.jtd.json \\")
        print("    --rust-out src/models/ \\")
        print("    --rust-edition 2021")
        print()
        print("Generate TypeScript types:")
        print("  npm install -g jtd-codegen")
        print("  jtd-codegen schemas/jtd/actionplan.jtd.json \\")
        print("    --typescript-out src/types/")
        print()
        print("Generate Go structs:")
        print("  jtd-codegen schemas/jtd/actionplan.jtd.json \\")
        print("    --go-out pkg/models/")
        print()
        print("Generate Python dataclasses:")
        print("  jtd-codegen schemas/jtd/actionplan.jtd.json \\")
        print("    --python-out models/")
        print()
        print("⚠️  NOTE: JTD is experimental. For validation, use JSON Schema.")
        print("   See schemas/*.schema.json and SCHEMA_GENERATION_DECISION.md")

    except Exception as e:
        print(f"❌ Error generating JTD schemas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
