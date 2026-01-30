"""
Validate ontology-out JSON-LD examples for Actions Vocabulary v4.
"""

from pathlib import Path

import pytest
from rdflib import Graph
from pyshacl import validate


ONTOLOGY_DIR = Path(__file__).parent.parent.parent
SHAPES_FILE = ONTOLOGY_DIR / "v4" / "actions-shapes-v4.ttl"
ONTOLOGY_FILE = ONTOLOGY_DIR / "v4" / "actions-vocabulary.owl"
VALID_DATA_DIR = ONTOLOGY_DIR / "examples" / "v4" / "valid"


def load_shapes_graph():
    shapes_graph = Graph()
    shapes_graph.parse(SHAPES_FILE, format="turtle")
    return shapes_graph


def load_ontology_graph():
    ont_graph = Graph()
    ont_graph.parse(ONTOLOGY_FILE, format="xml")
    return ont_graph


def validate_data(data_file: Path, shapes_graph: Graph, ont_graph: Graph):
    data_graph = Graph()
    data_graph.parse(data_file, format="json-ld")

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ont_graph,
        inference="rdfs",
        abort_on_first=False,
    )

    return conforms, results_graph, results_text, data_graph


class TestOntologyOutExamples:
    @pytest.fixture(scope="class")
    def shapes(self):
        return load_shapes_graph()

    @pytest.fixture(scope="class")
    def ontology(self):
        return load_ontology_graph()

    def test_example_conforms_to_shapes(self, shapes, ontology):
        data_file = VALID_DATA_DIR / "ontology-out.jsonld"
        conforms, _, results_text, _ = validate_data(data_file, shapes, ontology)
        assert conforms, (
            f"Ontology-out example should be valid. Violations:\n{results_text}"
        )

    def test_example_exports_to_turtle(self, shapes, ontology, tmp_path):
        data_file = VALID_DATA_DIR / "ontology-out.jsonld"
        conforms, _, results_text, data_graph = validate_data(
            data_file, shapes, ontology
        )
        assert conforms, (
            f"Ontology-out example should be valid. Violations:\n{results_text}"
        )

        export_path = tmp_path / "ontology-out.ttl"
        data_graph.serialize(export_path, format="turtle")

        roundtrip = Graph()
        roundtrip.parse(export_path, format="turtle")
        assert len(roundtrip) > 0, "Exported Turtle should contain triples"
