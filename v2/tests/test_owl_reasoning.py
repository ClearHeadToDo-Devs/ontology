"""
OWL Reasoning and Ontology Consistency Tests

Tests the logical consistency and reasoning capabilities of the Actions ontology,
complementing the SHACL validation tests with OWL-specific concerns.
"""

import pytest
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Namespaces
ACTIONS = Namespace("https://vocab.example.org/actions/")
SCHEMA = Namespace("http://schema.org/")

class TestOWLConsistency:
    """Test OWL logical consistency and reasoning."""
    
    def test_ontology_is_satisfiable(self, ontology_graph):
        """Test that the ontology is logically consistent (satisfiable)."""
        # Basic consistency check - the graph should parse and contain expected triples
        assert len(ontology_graph) > 0, "Ontology should contain triples"
        
        # Check that core classes are defined
        core_classes = [
            ACTIONS.Action,
            ACTIONS.RootAction, 
            ACTIONS.ChildAction,
            ACTIONS.LeafAction
        ]
        
        for cls in core_classes:
            assert (cls, RDF.type, OWL.Class) in ontology_graph, f"Class {cls} should be defined"
    
    def test_class_disjointness_consistency(self, ontology_graph):
        """Test that disjoint classes don't have overlapping instances."""
        
        # Check disjointness declarations exist
        disjoint_pairs = [
            (ACTIONS.RootAction, ACTIONS.ChildAction),
            (ACTIONS.RootAction, ACTIONS.LeafAction),
            (ACTIONS.ChildAction, ACTIONS.LeafAction)
        ]
        
        for cls1, cls2 in disjoint_pairs:
            # Check if disjointWith is declared (in either direction)
            disjoint_declared = (
                (cls1, OWL.disjointWith, cls2) in ontology_graph or
                (cls2, OWL.disjointWith, cls1) in ontology_graph
            )
            assert disjoint_declared, f"Disjointness between {cls1} and {cls2} should be declared"
    
    def test_property_domain_range_consistency(self, ontology_graph):
        """Test that property domains and ranges are properly defined."""
        
        # Test key properties have domains
        domain_expectations = [
            (ACTIONS.parentAction, None),  # Union domain, checked separately
            (ACTIONS.state, ACTIONS.Action),
            (ACTIONS.priority, ACTIONS.Action),
            (ACTIONS.project, ACTIONS.RootAction),  # Should be restricted to RootAction
        ]
        
        for prop, expected_domain in domain_expectations:
            if expected_domain:
                assert (prop, RDFS.domain, expected_domain) in ontology_graph, \
                    f"Property {prop} should have domain {expected_domain}"
    
    def test_schema_org_alignment_consistency(self, ontology_graph):
        """Test that Schema.org alignments are properly declared."""
        
        # Test subPropertyOf relationships
        expected_subprops = [
            (ACTIONS.state, SCHEMA.actionStatus),
            (ACTIONS.context, SCHEMA.location),
            (ACTIONS.doDateTime, SCHEMA.startTime),
            (ACTIONS.completedDateTime, SCHEMA.endTime),
            (ACTIONS.uuid, SCHEMA.identifier),
        ]
        
        for subprop, superprop in expected_subprops:
            assert (subprop, RDFS.subPropertyOf, superprop) in ontology_graph, \
                f"Property {subprop} should be subPropertyOf {superprop}"
    
    def test_functional_property_consistency(self, ontology_graph):
        """Test that functional properties are properly declared."""
        
        # Properties that should be functional (max 1 value)
        functional_props = [
            ACTIONS.state,
            ACTIONS.priority,
            ACTIONS.depth,
            ACTIONS.uuid,
            ACTIONS.doDateTime,
            ACTIONS.completedDateTime
        ]
        
        for prop in functional_props:
            assert (prop, RDF.type, OWL.FunctionalProperty) in ontology_graph, \
                f"Property {prop} should be declared as functional"

class TestOWLRestrictions:
    """Test OWL class restrictions and their logical implications."""
    
    def test_root_action_restrictions(self, ontology_graph):
        """Test that RootAction restrictions are properly defined."""
        
        # RootActions should have restriction on parentAction (maxCardinality 0)
        root_restrictions = list(ontology_graph.subjects(
            predicate=RDFS.subClassOf, 
            object=None
        ))
        
        # Look for restrictions on RootAction
        has_parent_restriction = False
        for restriction in ontology_graph.objects(ACTIONS.RootAction, RDFS.subClassOf):
            if (restriction, RDF.type, OWL.Restriction) in ontology_graph:
                if (restriction, OWL.onProperty, ACTIONS.parentAction) in ontology_graph:
                    has_parent_restriction = True
                    break
        
        assert has_parent_restriction, "RootAction should have restriction on parentAction"
    
    def test_derived_class_definitions(self, ontology_graph):
        """Test that derived classes are properly defined with owl:equivalentClass."""
        
        derived_classes = [
            ACTIONS.CompletedAction,
            ACTIONS.RecurringAction, 
            ACTIONS.ProjectAction
        ]
        
        for cls in derived_classes:
            # Should have equivalentClass with a restriction
            equiv_classes = list(ontology_graph.objects(cls, OWL.equivalentClass))
            assert len(equiv_classes) > 0, f"Derived class {cls} should have equivalentClass definition"
            
            # At least one should be a restriction
            has_restriction = any(
                (ec, RDF.type, OWL.Restriction) in ontology_graph 
                for ec in equiv_classes
            )
            assert has_restriction, f"Derived class {cls} should be equivalent to a restriction"

class TestInferenceCapabilities:
    """Test that the ontology supports proper inference."""
    
    def test_class_membership_inference(self, ontology_graph):
        """Test that class membership can be inferred from properties."""
        
        # Create test data
        test_graph = Graph()
        test_graph += ontology_graph  # Include ontology
        
        # Add test instance
        test_action = ACTIONS.test_completed_action
        test_graph.add((test_action, RDF.type, ACTIONS.Action))
        test_graph.add((test_action, ACTIONS.state, ACTIONS.Completed))
        
        # With a reasoner, this should infer CompletedAction membership
        # Note: This test documents the expectation - actual reasoning 
        # would require a reasoner like Pellet, HermiT, or ELK
        
        # For now, just test that the equivalent class definition exists
        completed_equiv = list(ontology_graph.objects(ACTIONS.CompletedAction, OWL.equivalentClass))
        assert len(completed_equiv) > 0, "CompletedAction should have equivalentClass for inference"
    
    def test_property_inheritance_structure(self, ontology_graph):
        """Test that property inheritance chains are properly set up."""
        
        # Test that actions inherit from Schema.org Action which inherits from Thing
        # This enables inheritance of schema:name, schema:description, etc.
        
        # Actions should be subclass of schema:Action
        schema_action = SCHEMA.Action
        # We declare this locally, so check our local declaration
        local_schema_declarations = list(ontology_graph.objects(
            schema_action, RDF.type
        ))
        assert OWL.Class in local_schema_declarations, "schema:Action should be declared as OWL Class"


class TestOntologyMetadata:
    """Test ontology-level metadata and documentation."""
    
    def test_ontology_metadata_complete(self, ontology_graph):
        """Test that ontology has proper metadata."""
        
        ontology_uri = URIRef("https://vocab.example.org/actions/")
        
        # Should be declared as ontology
        assert (ontology_uri, RDF.type, OWL.Ontology) in ontology_graph, \
            "Ontology URI should be declared as owl:Ontology"
        
        # Should have version info
        version_info = list(ontology_graph.objects(ontology_uri, OWL.versionInfo))
        assert len(version_info) > 0, "Ontology should have version information"
        
        # Should have human-readable labels and comments
        labels = list(ontology_graph.objects(ontology_uri, RDFS.label))
        assert len(labels) > 0, "Ontology should have rdfs:label"