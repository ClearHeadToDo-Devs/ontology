"""
Parameterized SHACL validation tests for all v4 ontology examples.

Covers:
- All TTL files in examples/v4/valid/ must conform to SHACL shapes
- All TTL files in examples/v4/invalid/ must FAIL SHACL shapes
- Each valid file is tested independently so failures are isolated
"""

from pathlib import Path

import pytest
from rdflib import Graph
from pyshacl import validate


ONTOLOGY_DIR = Path(__file__).parent.parent.parent
SHAPES_FILE = ONTOLOGY_DIR / "v4" / "actions-shapes-v4.ttl"
ONTOLOGY_FILE = ONTOLOGY_DIR / "v4" / "actions-vocabulary.owl"
VALID_DIR = ONTOLOGY_DIR / "examples" / "v4" / "valid"
INVALID_DIR = ONTOLOGY_DIR / "examples" / "v4" / "invalid"


@pytest.fixture(scope="module")
def shapes_graph():
    g = Graph()
    g.parse(SHAPES_FILE, format="turtle")
    return g


@pytest.fixture(scope="module")
def ontology_graph():
    g = Graph()
    g.parse(ONTOLOGY_FILE, format="xml")
    return g


def _validate_ttl(path: Path, shapes_graph: Graph, ontology_graph: Graph):
    data = Graph()
    data.parse(path, format="turtle")
    conforms, _, report = validate(
        data,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph,
        inference="rdfs",
        abort_on_first=False,
    )
    return conforms, report


# ---------------------------------------------------------------------------
# Collect all .ttl fixtures (exclude ontology-out.jsonld which is JSON-LD)
# ---------------------------------------------------------------------------

VALID_TTL = sorted(VALID_DIR.glob("*.ttl"))
INVALID_TTL = sorted(INVALID_DIR.glob("*.ttl"))

assert VALID_TTL, f"No valid TTL examples found in {VALID_DIR}"
assert INVALID_TTL, f"No invalid TTL examples found in {INVALID_DIR}"


class TestValidExamples:
    """Every file in examples/v4/valid/*.ttl must conform to SHACL shapes."""

    @pytest.mark.parametrize("example", VALID_TTL, ids=[f.name for f in VALID_TTL])
    def test_valid_example_conforms(self, example, shapes_graph, ontology_graph):
        conforms, report = _validate_ttl(example, shapes_graph, ontology_graph)
        assert conforms, (
            f"{example.name} should pass SHACL validation.\n\nViolations:\n{report}"
        )

    @pytest.mark.parametrize("example", VALID_TTL, ids=[f.name for f in VALID_TTL])
    def test_valid_example_has_triples(self, example, shapes_graph, ontology_graph):
        """Sanity check: every valid example must contain actual data."""
        data = Graph()
        data.parse(example, format="turtle")
        assert len(data) > 0, f"{example.name} parsed to an empty graph"


class TestInvalidExamples:
    """Every file in examples/v4/invalid/*.ttl must FAIL SHACL shapes."""

    @pytest.mark.parametrize(
        "example", INVALID_TTL, ids=[f.name for f in INVALID_TTL]
    )
    def test_invalid_example_fails(self, example, shapes_graph, ontology_graph):
        conforms, report = _validate_ttl(example, shapes_graph, ontology_graph)
        assert not conforms, (
            f"{example.name} should FAIL SHACL validation but it passed.\n"
            "Check that the example actually violates a shape, or remove it from invalid/."
        )
