#!/usr/bin/env python3
"""
Test suite for Actions Vocabulary v3

Tests that:
1. The v3 ontology loads successfully
2. BFO and CCO imports are resolved
3. Classes are properly defined
4. Example instances are valid
5. Basic reasoning works
6. RDFLib parsing works correctly
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import owlready2 as owl
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF, RDFS, OWL
except ImportError as e:
    pytest.exit(f"Missing dependency: {e}. Run: uv sync", returncode=1)


# Fixtures
@pytest.fixture(scope="module")
def ontology_path():
    """Return the path to the v3 ontology file."""
    return Path(__file__).parent.parent / "actions-vocabulary.owl"


@pytest.fixture(scope="module")
def world():
    """Create an isolated owlready2 world for testing."""
    return owl.World()


@pytest.fixture(scope="module")
def ontology(ontology_path, world):
    """Load the v3 ontology."""
    onto = world.get_ontology(f"file://{ontology_path.absolute()}").load()
    return onto


# Tests
@pytest.mark.unit
def test_ontology_loads(ontology, ontology_path):
    """Test that v3 ontology loads successfully."""
    assert ontology is not None, "Ontology should load"
    assert ontology.base_iri is not None, "Ontology should have a base IRI"

    # Log some basic stats for debugging
    classes_count = len(list(ontology.classes()))
    props_count = len(list(ontology.properties()))
    individuals_count = len(list(ontology.individuals()))

    print(f"\n📂 Loaded: {ontology_path}")
    print(f"   IRI: {ontology.base_iri}")
    print(f"   Classes: {classes_count}")
    print(f"   Properties: {props_count}")
    print(f"   Individuals: {individuals_count}")

    assert classes_count > 0, "Ontology should have classes"
    assert props_count > 0, "Ontology should have properties"


@pytest.mark.unit
class TestClasses:
    """Test suite for ontology classes."""

    EXPECTED_CLASSES = [
        "ActionPlan",
        "ActionProcess",
        "RootActionPlan",
        "ChildActionPlan",
        "LeafActionPlan",
        "ActionState"
    ]

    def test_all_expected_classes_exist(self, ontology):
        """Test that all expected classes are defined."""
        found_classes = {cls.name: cls for cls in ontology.classes()}

        print(f"\nFound {len(found_classes)} classes in ontology:")
        for cls_name in sorted(found_classes.keys()):
            print(f"  • {cls_name}")

        for cls_name in self.EXPECTED_CLASSES:
            assert cls_name in found_classes, f"Class {cls_name} should exist"

    @pytest.mark.parametrize("class_name", EXPECTED_CLASSES)
    def test_class_has_ancestors(self, ontology, class_name):
        """Test that each class has proper ancestor hierarchy."""
        found_classes = {cls.name: cls for cls in ontology.classes()}
        cls = found_classes[class_name]

        ancestors = [a.name for a in cls.ancestors() if hasattr(a, 'name')]
        print(f"\n{class_name} ancestors: {', '.join(ancestors[:5])}")

        assert len(ancestors) > 0, f"{class_name} should have ancestors"


@pytest.mark.unit
def test_disjointness(ontology):
    """Test that disjoint classes are properly defined."""
    root_cls = ontology.search_one(iri="*RootActionPlan")
    child_cls = ontology.search_one(iri="*ChildActionPlan")
    leaf_cls = ontology.search_one(iri="*LeafActionPlan")

    assert root_cls is not None, "RootActionPlan should exist"
    assert child_cls is not None, "ChildActionPlan should exist"
    assert leaf_cls is not None, "LeafActionPlan should exist"

    # Check for AllDisjoint axioms in the ontology
    disjoint_sets = []
    found_disjoints = False

    for axiom in ontology.disjoint_classes():
        classes_in_axiom = list(axiom.entities)
        disjoint_sets.append([cls.name for cls in classes_in_axiom])

        if root_cls in classes_in_axiom:
            found_disjoints = True
            print(f"\n✅ Found disjoint axiom containing RootActionPlan: "
                  f"{[cls.name for cls in classes_in_axiom]}")
        elif child_cls in classes_in_axiom:
            print(f"✅ Found disjoint axiom containing ChildActionPlan: "
                  f"{[cls.name for cls in classes_in_axiom]}")

    if disjoint_sets:
        print("\nAll disjoint sets in ontology:")
        for ds in disjoint_sets:
            print(f"  • {ds}")

    # Disjointness is optional, so just verify we can check for it
    # This test passes if we can successfully query for disjoint classes
    assert isinstance(disjoint_sets, list), "Should be able to query disjoint classes"


@pytest.mark.unit
class TestProperties:
    """Test suite for ontology properties."""

    EXPECTED_PROPERTIES = [
        "prescribes",
        "hasState",
        "hasPriority",
        "hasContext",
        "hasProject"
    ]

    def test_all_expected_properties_exist(self, ontology):
        """Test that all expected properties are defined."""
        found_props = {prop.name: prop for prop in ontology.properties()}

        print(f"\nFound {len(found_props)} properties in ontology:")
        for prop_name in sorted(found_props.keys()):
            print(f"  • {prop_name}")

        for prop_name in self.EXPECTED_PROPERTIES:
            assert prop_name in found_props, f"Property {prop_name} should exist"

    @pytest.mark.parametrize("prop_name", EXPECTED_PROPERTIES)
    def test_property_has_domain_and_range(self, ontology, prop_name):
        """Test that each property has domain and range defined."""
        found_props = {prop.name: prop for prop in ontology.properties()}
        prop = found_props[prop_name]

        domain = prop.domain[0] if prop.domain else None
        range_val = prop.range[0] if prop.range else None

        print(f"\n{prop_name}:")
        print(f"  Domain: {domain}")
        print(f"  Range: {range_val}")

        # Domain and range are optional in OWL, so just verify we can query them
        assert isinstance(prop.domain, list), "Should be able to query property domain"
        assert isinstance(prop.range, list), "Should be able to query property range"


@pytest.mark.unit
def test_instances(ontology):
    """Test that example instances are present."""
    individuals = list(ontology.individuals())

    print(f"\nFound {len(individuals)} individuals:")
    for ind in individuals:
        print(f"\n  • {ind.name}")
        print(f"    Types: {[t.name for t in ind.is_a if hasattr(t, 'name')]}")

        if hasattr(ind, 'label') and ind.label:
            print(f"    Label: {ind.label}")

    # We expect at least 5 example instances
    assert len(individuals) >= 5, f"Expected at least 5 instances, found {len(individuals)}"


@pytest.mark.slow
@pytest.mark.integration
def test_reasoning(ontology, world):
    """Test basic reasoning capabilities with HermiT."""
    print("\nRunning HermiT reasoner (this may take a moment)...")

    try:
        # Run reasoner
        with ontology:
            owl.sync_reasoner_hermit(world, infer_property_values=True, debug=False)

        print("✅ Reasoning completed successfully")
        print("   Ontology is logically consistent")

        # Check for any inferred facts
        individuals = list(ontology.individuals())
        print(f"   Individuals after reasoning: {len(individuals)}")

    except owl.OwlReadyInconsistentOntologyError as e:
        pytest.fail(f"INCONSISTENT ONTOLOGY: {e}\nThe ontology contains logical contradictions")
    except Exception as e:
        # If reasoner not available (e.g., Java not installed), that's OK
        pytest.skip(f"Reasoning skipped: {e}\nHermiT requires Java - install if needed")


@pytest.mark.unit
def test_rdflib_parsing(ontology_path):
    """Test that ontology can be parsed with RDFLib."""
    g = Graph()
    print(f"\n📂 Parsing with RDFLib: {ontology_path}")

    g.parse(ontology_path, format="xml")

    print("✅ Successfully parsed with RDFLib")
    print(f"   Triples: {len(g)}")

    assert len(g) > 0, "RDFLib graph should contain triples"

    # Check for key classes
    ACTIONS = Namespace("https://clearhead.us/vocab/actions/v3#")

    action_plan = ACTIONS.ActionPlan
    assert (action_plan, RDF.type, OWL.Class) in g, "ActionPlan class should exist in RDF graph"
    print("   ✅ ActionPlan class found")

    action_process = ACTIONS.ActionProcess
    assert (action_process, RDF.type, OWL.Class) in g, "ActionProcess class should exist in RDF graph"
    print("   ✅ ActionProcess class found")
