"""Validate v4 JSON-LD context mappings and behavior."""

import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD


ONTOLOGY_DIR = Path(__file__).parent.parent.parent
CONTEXT_FILE = ONTOLOGY_DIR / "v4" / "actions.context.json"
EXAMPLE_FILE = ONTOLOGY_DIR / "examples" / "v4" / "valid" / "ontology-out.jsonld"

ACTIONS = Namespace("https://clearhead.us/vocab/actions/v4#")
CCO = Namespace("https://www.commoncoreontologies.org/")
BFO = Namespace("http://purl.obolibrary.org/obo/")


def load_context_map() -> dict:
    with CONTEXT_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)["@context"]


class TestActionsContext:
    def test_context_includes_canonical_terms(self):
        ctx = load_context_map()

        assert ctx["Plan"] == "https://www.commoncoreontologies.org/ont00000974"
        assert ctx["PlannedAct"] == "https://www.commoncoreontologies.org/ont00000228"
        assert ctx["Objective"] == "https://www.commoncoreontologies.org/ont00000476"
        assert ctx["Charter"] == "https://clearhead.us/vocab/actions/v4#Charter"
        assert ctx["Context"] == "https://clearhead.us/vocab/actions/v4#Context"
        assert ctx["ContextType"] == "https://clearhead.us/vocab/actions/v4#ContextType"

        assert ctx["plannedActs"]["@id"] == "cco:ont00001942"
        assert ctx["requiresContext"]["@id"] == "actions:requiresContext"
        assert ctx["subCharters"]["@id"] == "actions:hasSubCharter"
        assert ctx["partOf"]["@id"] == "bfo:BFO_0000050"
        assert ctx["scheduledAt"]["@id"] == "actions:hasScheduledDateTime"
        assert ctx["dueDate"]["@id"] == "actions:hasDueDateTime"
        assert ctx["dueRecurrence"]["@id"] == "actions:hasDueRecurrenceRule"
        assert ctx["contextType"]["@id"] == "actions:hasContextType"
        assert ctx["contextIdentifier"]["@id"] == "actions:hasContextIdentifier"
        assert ctx["contextBroader"]["@id"] == "actions:contextBroader"
        assert ctx["contextNarrower"]["@id"] == "actions:contextNarrower"

    def test_context_expands_ontology_out_compacted_payload(self):
        graph = Graph()
        graph.parse(EXAMPLE_FILE, format="json-ld")

        charter = URIRef("urn:charter:groceries")
        sub_charter = URIRef("urn:charter:groceries/fresh")
        plan = URIRef("urn:uuid:plan-1")
        act = URIRef("urn:uuid:act-1")
        errands = URIRef("urn:context:errands")
        grocery_store = URIRef("urn:context:grocery-store")
        facility_type = URIRef("urn:context-type:facility")

        assert (charter, RDF.type, ACTIONS.Charter) in graph
        assert (charter, ACTIONS.hasSubCharter, sub_charter) in graph
        assert (plan, BFO.BFO_0000050, charter) in graph
        assert (plan, CCO.ont00001942, act) in graph
        assert (plan, ACTIONS.requiresContext, errands) in graph
        assert (plan, ACTIONS.requiresContext, grocery_store) in graph

        assert (errands, RDF.type, ACTIONS.Context) in graph
        assert (grocery_store, RDF.type, ACTIONS.Context) in graph
        assert (facility_type, RDF.type, ACTIONS.ContextType) in graph
        assert (grocery_store, ACTIONS.contextBroader, errands) in graph
        assert (grocery_store, ACTIONS.hasContextType, facility_type) in graph
        assert (
            grocery_store,
            ACTIONS.hasContextIdentifier,
            Literal("@grocery-store", datatype=XSD.string),
        ) in graph

        scheduled_values = list(graph.objects(act, ACTIONS.hasScheduledDateTime))
        due_values = list(graph.objects(act, ACTIONS.hasDueDateTime))

        assert len(scheduled_values) == 1
        assert len(due_values) == 1
        assert scheduled_values[0].datatype == XSD.dateTime
        assert due_values[0].datatype == XSD.dateTime
        assert "2026-04-10T00:00:00" in str(scheduled_values[0])
        assert "2026-04-11T00:00:00" in str(due_values[0])
        assert (act, CCO.ont00001868, ACTIONS.Completed) in graph
        assert (plan, RDFS.label, Literal("Buy milk")) in graph
