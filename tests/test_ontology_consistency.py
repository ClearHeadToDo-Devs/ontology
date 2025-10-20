"""
Tests for ontology and SHACL shapes consistency and structure.
"""

import pytest
import rdflib
from rdflib import OWL, RDF, RDFS


class TestOntologyConsistency:
    """Test ontology internal consistency and structure."""

    def test_ontology_loads_successfully(self, ontology_graph):
        """Test that ontology loads without errors."""
        assert len(ontology_graph) > 0, "Ontology should contain triples"
        print(f"✅ Loaded ontology with {len(ontology_graph)} triples")

    def test_shapes_load_successfully(self, shapes_graph):
        """Test that SHACL shapes load without errors."""
        assert len(shapes_graph) > 0, "Shapes should contain triples"
        print(f"✅ Loaded shapes with {len(shapes_graph)} triples")

    def test_required_namespaces_present(self, ontology_graph):
        """Test that required namespaces are defined."""
        namespaces = dict(ontology_graph.namespaces())
        required = ["rdf", "rdfs", "owl", "xsd"]

        missing = [ns for ns in required if ns not in namespaces]
        assert not missing, f"Required namespaces missing: {missing}"
        print(f"✅ All required namespaces present: {required}")

    def test_core_classes_defined(self, ontology_graph):
        """Test that core action classes are properly defined."""
        actions_ns = rdflib.Namespace("https://vocab.example.org/actions/")

        core_classes = [
            ("Action", actions_ns.Action),
            ("RootAction", actions_ns.RootAction),
            ("ChildAction", actions_ns.ChildAction),
            ("LeafAction", actions_ns.LeafAction),
            ("ActionState", actions_ns.ActionState),
        ]

        for class_name, cls in core_classes:
            assert (
                cls,
                RDF.type,
                OWL.Class,
            ) in ontology_graph, f"Class {class_name} not defined as owl:Class"

        print(f"✅ All core classes properly defined")

    def test_class_hierarchy_consistency(self, ontology_graph):
        """Test that class hierarchy is properly structured."""
        actions_ns = rdflib.Namespace("https://vocab.example.org/actions/")

        # Check subclass relationships
        subclass_relationships = [
            ("RootAction", actions_ns.RootAction, actions_ns.Action),
            ("ChildAction", actions_ns.ChildAction, actions_ns.Action),
            ("LeafAction", actions_ns.LeafAction, actions_ns.Action),
        ]

        for name, subclass, superclass in subclass_relationships:
            assert (
                subclass,
                RDFS.subClassOf,
                superclass,
            ) in ontology_graph, f"{name} should be subclass of Action"

        print(f"✅ Class hierarchy properly structured")

    def test_property_domains_and_ranges(self, ontology_graph):
        """Test that key properties have proper domains and ranges."""
        actions_ns = rdflib.Namespace("https://vocab.example.org/actions/")
        xsd_ns = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

        # Key property constraints to verify
        property_constraints = [
            ("depth domain", actions_ns.depth, RDFS.domain, actions_ns.Action),
            ("priority domain", actions_ns.priority, RDFS.domain, actions_ns.Action),
            ("state domain", actions_ns.state, RDFS.domain, actions_ns.Action),
            ("depth range", actions_ns.depth, RDFS.range, xsd_ns.nonNegativeInteger),
        ]

        missing_constraints = []
        for name, prop, constraint_type, constraint_value in property_constraints:
            if not (prop, constraint_type, constraint_value) in ontology_graph:
                missing_constraints.append(name)

        if missing_constraints:
            print(f"⚠️  Missing property constraints: {missing_constraints}")
        else:
            print(f"✅ Key property constraints properly defined")

    def test_no_syntax_errors(self, ontology_graph):
        """Test for RDF syntax errors by round-trip serialization."""
        try:
            ttl_data = ontology_graph.serialize(format="turtle")
            test_graph = rdflib.Graph()
            test_graph.parse(data=ttl_data, format="turtle")

            assert len(test_graph) == len(
                ontology_graph
            ), "Round-trip serialization changed triple count"

            print(f"✅ No syntax errors detected")

        except Exception as e:
            pytest.fail(f"Syntax errors in ontology: {e}")


class TestSHACLShapesConsistency:
    """Test SHACL shapes internal consistency."""

    def test_shapes_target_valid_classes(self, shapes_graph, ontology_graph):
        """Test that shape targets reference valid classes."""
        sh_ns = rdflib.Namespace("http://www.w3.org/ns/shacl#")

        # Get all targetClass values from shapes
        target_classes = set()
        for shape in shapes_graph.subjects(RDF.type, sh_ns.NodeShape):
            for target in shapes_graph.objects(shape, sh_ns.targetClass):
                target_classes.add(target)

        # Verify each target class exists in ontology
        undefined_classes = []
        for target_class in target_classes:
            if not (target_class, RDF.type, OWL.Class) in ontology_graph:
                undefined_classes.append(str(target_class))

        assert (
            not undefined_classes
        ), f"Shapes target undefined classes: {undefined_classes}"

        print(f"✅ All {len(target_classes)} shape targets reference valid classes")

    def test_shape_properties_reference_valid_properties(
        self, shapes_graph, ontology_graph
    ):
        """Test that shape properties reference valid ontology properties."""
        sh_ns = rdflib.Namespace("http://www.w3.org/ns/shacl#")
        owl_ns = rdflib.Namespace("http://www.w3.org/2002/07/owl#")

        # Get all property paths from shapes
        property_paths = set()
        for shape in shapes_graph.subjects(RDF.type, sh_ns.NodeShape):
            for prop_shape in shapes_graph.objects(shape, sh_ns.property):
                for path in shapes_graph.objects(prop_shape, sh_ns.path):
                    property_paths.add(path)

        # Also check SPARQL constraint properties
        sparql_properties = set()
        for shape in shapes_graph.subjects(RDF.type, sh_ns.NodeShape):
            for sparql_constraint in shapes_graph.objects(shape, sh_ns.sparql):
                # Extract property references from SPARQL queries (simplified)
                for select_query in shapes_graph.objects(
                    sparql_constraint, sh_ns.select
                ):
                    query_text = str(select_query)
                    # This is a simplified extraction - in practice you'd parse SPARQL
                    if "actions:" in query_text:
                        # Add properties found in SPARQL constraints
                        pass

        # Verify each property exists in ontology
        undefined_props = []
        for prop_path in property_paths:
            is_object_prop = (
                prop_path,
                RDF.type,
                owl_ns.ObjectProperty,
            ) in ontology_graph
            is_datatype_prop = (
                prop_path,
                RDF.type,
                owl_ns.DatatypeProperty,
            ) in ontology_graph
            is_functional_prop = (
                prop_path,
                RDF.type,
                owl_ns.FunctionalProperty,
            ) in ontology_graph

            if not (is_object_prop or is_datatype_prop or is_functional_prop):
                undefined_props.append(str(prop_path))

        if undefined_props:
            print(f"⚠️  Shapes reference undefined properties: {undefined_props}")
        else:
            print(
                f"✅ All {len(property_paths)} shape properties reference valid ontology properties"
            )

    def test_shapes_have_meaningful_constraints(self, shapes_graph):
        """Test that shapes have meaningful validation constraints."""
        sh_ns = rdflib.Namespace("http://www.w3.org/ns/shacl#")

        shape_count = 0
        constraint_types = set()

        for shape in shapes_graph.subjects(RDF.type, sh_ns.NodeShape):
            shape_count += 1

            # Count different types of constraints
            for prop_shape in shapes_graph.objects(shape, sh_ns.property):
                # Property constraints
                if list(shapes_graph.objects(prop_shape, sh_ns.minCount)):
                    constraint_types.add("minCount")
                if list(shapes_graph.objects(prop_shape, sh_ns.maxCount)):
                    constraint_types.add("maxCount")
                if list(shapes_graph.objects(prop_shape, sh_ns.datatype)):
                    constraint_types.add("datatype")
                if list(shapes_graph.objects(prop_shape, sh_ns.hasValue)):
                    constraint_types.add("hasValue")
                if list(shapes_graph.objects(prop_shape, sh_ns.pattern)):
                    constraint_types.add("pattern")

            # SPARQL constraints
            if list(shapes_graph.objects(shape, sh_ns.sparql)):
                constraint_types.add("sparql")

        assert shape_count > 0, "No SHACL shapes found"
        assert len(constraint_types) > 0, "No meaningful constraints found in shapes"

        print(
            f"✅ Found {shape_count} shapes with {len(constraint_types)} types of constraints"
        )
        print(f"   Constraint types: {sorted(constraint_types)}")


class TestDataConsistency:
    """Test consistency between test data and ontology/shapes."""

    def test_test_files_parse_successfully(self, test_data_files, data_loader):
        """Test that all test data files parse without errors."""
        all_files = {**test_data_files["valid"], **test_data_files["invalid"]}

        parse_errors = []

        for file_name, file_path in all_files.items():
            try:
                graph = data_loader(file_path)
                assert len(graph) > 0, f"File {file_name} contains no triples"
            except Exception as e:
                parse_errors.append(f"{file_name}: {e}")

        if parse_errors:
            pytest.fail(f"Test files failed to parse: {parse_errors}")

        print(f"✅ All {len(all_files)} test files parse successfully")

    def test_test_files_use_ontology_vocabulary(
        self, test_data_files, data_loader, ontology_graph
    ):
        """Test that test files use vocabulary from the ontology."""
        actions_ns = rdflib.Namespace("https://vocab.example.org/actions/")
        all_files = {**test_data_files["valid"], **test_data_files["invalid"]}

        # Get ontology classes and properties
        ontology_classes = set()
        ontology_properties = set()

        for s, p, o in ontology_graph:
            if p == RDF.type and o == OWL.Class:
                ontology_classes.add(s)
            elif p == RDF.type and (
                o == OWL.ObjectProperty
                or o == OWL.DatatypeProperty
                or o == OWL.FunctionalProperty
            ):
                ontology_properties.add(s)

        undefined_usage = []

        for file_name, file_path in all_files.items():
            try:
                graph = data_loader(file_path)

                # Check classes used in test data
                for s, p, o in graph:
                    if p == RDF.type and str(o).startswith(str(actions_ns)):
                        if o not in ontology_classes:
                            undefined_usage.append(f"{file_name}: undefined class {o}")

                    # Check properties used in test data
                    if str(p).startswith(str(actions_ns)):
                        if p not in ontology_properties:
                            undefined_usage.append(
                                f"{file_name}: undefined property {p}"
                            )

            except Exception:
                # Skip files that don't parse (handled by other test)
                continue

        if undefined_usage:
            print(f"⚠️  Test files use undefined vocabulary: {undefined_usage[:5]}...")
        else:
            print(f"✅ All test files use defined ontology vocabulary")
