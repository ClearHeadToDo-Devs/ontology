"""
Test SHACL validation for Actions Vocabulary v3.

This test suite validates that the SHACL shapes correctly enforce
constraints on ActionPlan and ActionProcess instances.
"""

import pytest
from pathlib import Path
from rdflib import Graph
from pyshacl import validate

# Paths
ONTOLOGY_DIR = Path(__file__).parent.parent.parent
SHAPES_FILE = ONTOLOGY_DIR / "actions-shapes-v3.ttl"
ONTOLOGY_FILE = ONTOLOGY_DIR / "actions-vocabulary.owl"
VALID_DATA_DIR = Path(__file__).parent / "data" / "valid"
INVALID_DATA_DIR = Path(__file__).parent / "data" / "invalid"


def load_shapes_graph():
    """Load the SHACL shapes graph."""
    shapes_graph = Graph()
    shapes_graph.parse(SHAPES_FILE, format="turtle")
    return shapes_graph


def validate_data(data_file: Path, shapes_graph: Graph):
    """
    Validate an RDF data file against SHACL shapes.

    Returns:
        tuple: (conforms: bool, results_graph: Graph, results_text: str)
    """
    data_graph = Graph()
    data_graph.parse(data_file, format="turtle")

    # Load ontology for class inference
    ont_graph = Graph()
    ont_graph.parse(ONTOLOGY_FILE, format="xml")

    # Run SHACL validation
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ont_graph,  # Load ontology for inference
        inference='rdfs',  # Use RDFS inference
        abort_on_first=False,
    )

    return conforms, results_graph, results_text


class TestValidActionPlans:
    """Test that valid action plans pass validation."""

    @pytest.fixture(scope="class")
    def shapes(self):
        return load_shapes_graph()

    def test_simple_action_plan(self, shapes):
        """Test a simple valid action plan."""
        data_file = VALID_DATA_DIR / "simple-actionplan.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert conforms, f"Simple action plan should be valid. Violations:\n{results_text}"

    def test_action_plan_with_children(self, shapes):
        """Test hierarchical action plan structure."""
        data_file = VALID_DATA_DIR / "actionplan-with-children.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert conforms, f"Hierarchical action plan should be valid. Violations:\n{results_text}"

    def test_action_process_execution(self, shapes):
        """Test action process (execution) instances."""
        data_file = VALID_DATA_DIR / "actionprocess-execution.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert conforms, f"Action process should be valid. Violations:\n{results_text}"


class TestInvalidActionPlans:
    """Test that invalid action plans fail validation with appropriate errors."""

    @pytest.fixture(scope="class")
    def shapes(self):
        return load_shapes_graph()

    def test_invalid_priority(self, shapes):
        """Test that priority outside 1-4 range is rejected."""
        data_file = INVALID_DATA_DIR / "invalid-priority.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert not conforms, "Priority outside 1-4 should be invalid"
        assert "Priority must be between 1" in results_text or "maxInclusive" in results_text, \
            "Should mention priority constraint violation"

    def test_invalid_uuid_format(self, shapes):
        """Test that non-UUID-v7 format is rejected."""
        data_file = INVALID_DATA_DIR / "invalid-uuid.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert not conforms, "Invalid UUID format should be rejected"
        assert "UUID" in results_text or "pattern" in results_text, \
            "Should mention UUID format violation"

    def test_root_with_parent(self, shapes):
        """Test that root action plans cannot have parents."""
        data_file = INVALID_DATA_DIR / "invalid-root-with-parent.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert not conforms, "Root plans cannot have parents"
        assert "parent" in results_text.lower() or "maxCount" in results_text, \
            "Should mention parent constraint violation"

    def test_invalid_temporal_order(self, shapes):
        """Test that do date cannot be after due date."""
        data_file = INVALID_DATA_DIR / "invalid-temporal.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert not conforms, "Do date after due date should be invalid"
        assert "date" in results_text.lower() or "temporal" in results_text.lower(), \
            "Should mention temporal constraint violation"

    def test_depth_mismatch(self, shapes):
        """Test that declared depth must match actual depth."""
        data_file = INVALID_DATA_DIR / "invalid-depth-mismatch.ttl"
        conforms, results_graph, results_text = validate_data(data_file, shapes)

        assert not conforms, "Depth mismatch should be invalid"
        assert "depth" in results_text.lower(), \
            "Should mention depth constraint violation"


class TestConstraintCoverage:
    """Test that all important constraints are defined in SHACL shapes."""

    @pytest.fixture(scope="class")
    def shapes(self):
        return load_shapes_graph()

    def test_shapes_file_exists(self):
        """Test that SHACL shapes file exists."""
        assert SHAPES_FILE.exists(), f"SHACL shapes file not found: {SHAPES_FILE}"

    def test_shapes_load_successfully(self, shapes):
        """Test that shapes graph loaded successfully."""
        assert len(shapes) > 0, "Shapes graph should not be empty"

    def test_has_priority_constraint(self, shapes):
        """Test that priority constraint exists."""
        # Check for minInclusive/maxInclusive in shapes
        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        ASK {
            ?shape sh:minInclusive ?min .
            ?shape sh:maxInclusive ?max .
        }
        """
        result = shapes.query(query)
        assert bool(result), "Should have min/max inclusive constraints (for priority)"

    def test_has_uuid_pattern(self, shapes):
        """Test that UUID pattern constraint exists."""
        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        ASK {
            ?shape sh:pattern ?pattern .
            FILTER(CONTAINS(STR(?pattern), "uuid") || CONTAINS(STR(?pattern), "[0-9a-f]"))
        }
        """
        result = shapes.query(query)
        assert bool(result), "Should have UUID pattern constraint"

    def test_has_temporal_sparql_constraint(self, shapes):
        """Test that temporal SPARQL constraints exist."""
        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        ASK {
            ?shape sh:sparql ?sparqlConstraint .
            ?sparqlConstraint sh:select ?selectQuery .
            FILTER(CONTAINS(STR(?selectQuery), "DateTime"))
        }
        """
        result = shapes.query(query)
        assert bool(result), "Should have temporal SPARQL constraints"

    def test_has_hierarchical_constraints(self, shapes):
        """Test that hierarchical constraints exist."""
        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX actions: <https://vocab.clearhead.io/actions/v3#>
        ASK {
            ?shape sh:targetClass ?class .
            FILTER(?class IN (actions:RootActionPlan, actions:ChildActionPlan, actions:LeafActionPlan))
        }
        """
        result = shapes.query(query)
        assert bool(result), "Should have shapes for hierarchical action plan classes"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
