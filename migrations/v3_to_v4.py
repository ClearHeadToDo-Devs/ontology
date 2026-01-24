#!/usr/bin/env python3
"""
Migrate Actions Vocabulary v3 to v4.
Handles class mapping and data transformation.

Usage:
    python v3_to_v4.py <input.ttl> <output.ttl>
"""

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, OWL
import sys

# Namespaces
V3 = Namespace("https://clearhead.us/vocab/actions/v3#")
V4 = Namespace("https://clearhead.us/vocab/actions/v4#")
CCO = Namespace("https://www.commoncoreontologies.org/")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")
SCHEMA = Namespace("http://schema.org/")


# Property mapping (V3 -> V4)
PROPERTY_MAP = {
    V3.hasPriority: V4.hasPriority,
    V3.hasUUID: V4.hasUUID,
    V3.hasDoDateTime: V4.hasDoDateTime,
    V3.hasDueDateTime: V4.hasDueDateTime,  # Assuming V4 keeps this
    V3.hasDurationMinutes: V4.hasDurationMinutes,
    V3.hasRecurrenceFrequency: V4.hasRecurrenceFrequency,
    V3.hasRecurrenceInterval: V4.hasRecurrenceInterval,
    V3.hasRecurrenceUntil: V4.hasRecurrenceUntil,
    V3.hasRecurrenceCount: V4.hasRecurrenceCount,
    V3.byDay: V4.byDay,
    V3.byMonth: V4.byMonth,
    V3.byMonthDay: V4.byMonthDay,
    V3.assignedToAgent: V4.assignedToAgent,
    V3.performedBy: V4.performedBy,
    V3.hasCompletedDateTime: V4.hasCompletedDateTime,
    V3.hasDepth: V4.hasDepth, # Keeping if present
}

def get_v4_iri(v3_iri):
    """Convert a V3 IRI to V4."""
    return URIRef(str(v3_iri).replace("/v3#", "/v4#"))

def migrate_properties(g_v4, subject_v4, g_v3, subject_v3, skip_props=None):
    """
    Copy and map properties from v3 subject to v4 subject.
    """
    if skip_props is None:
        skip_props = []
        
    for p, o in g_v3.predicate_objects(subject_v3):
        if p in skip_props:
            continue
            
        # Handle specific property mapping
        if p in PROPERTY_MAP:
            mapped_p = PROPERTY_MAP[p]
            if mapped_p:
                g_v4.add((subject_v4, mapped_p, o))
        elif p == RDF.type:
            continue # Handled by caller
        elif str(p).startswith(str(V3)):
            # Warning: unmapped V3 property. 
            # Strategy: Auto-map to V4 namespace
            new_p = get_v4_iri(p)
            g_v4.add((subject_v4, new_p, o))
        else:
            # Copy other properties (schema:, rdfs:, etc.)
            g_v4.add((subject_v4, p, o))

def migrate_action_plan(g_v3, plan_iri_v3):
    """
    Migrate v3 ActionPlan to v4 CCO Plan.
    """
    plan_iri_v4 = get_v4_iri(plan_iri_v3)

    g_v4 = Graph()
    g_v4.bind("v4", V4)
    g_v4.bind("cco", CCO)
    g_v4.bind("bfo", BFO)
    g_v4.bind("schema", SCHEMA)

    # Change class from v3:ActionPlan to cco:Plan
    g_v4.add((plan_iri_v4, RDF.type, CCO.ont00000974))

    # Properties to handle specially
    special_props = [
        V3.parentAction,
        V3.hasProject,
        V3.requiresContext,
        V3.hasContext, # Handle hasContext too
        RDF.type
    ]
    
    migrate_properties(g_v4, plan_iri_v4, g_v3, plan_iri_v3, special_props)

    # Handle hierarchy migration (parentAction → partOf)
    for parent_iri in g_v3.objects(plan_iri_v3, V3.parentAction):
        parent_iri_v4 = get_v4_iri(parent_iri)
        g_v4.add((plan_iri_v4, V4.partOf, parent_iri_v4))

    # Handle project→objective migration (string → object)
    for project_name in g_v3.objects(plan_iri_v3, V3.hasProject):
        # Create objective IRI from project name
        safe_name = (
            str(project_name).lower().strip().replace(" ", "_").replace("/", "_").replace("\\", "_")
        )
        objective_iri = URIRef(f"urn:objective:{safe_name}")
        g_v4.add((objective_iri, RDF.type, CCO.ont00000476))
        g_v4.add((objective_iri, RDFS.label, Literal(project_name)))
        g_v4.add((plan_iri_v4, V4.hasObjective, objective_iri))

    # Handle context migration
    # Collect contexts from both requiresContext and hasContext
    contexts = list(g_v3.objects(plan_iri_v3, V3.requiresContext))
    contexts.extend(list(g_v3.objects(plan_iri_v3, V3.hasContext)))
    
    for ctx_iri in contexts:
        ctx_types = list(g_v3.objects(ctx_iri, RDF.type))

        if V3.LocationContext in ctx_types:
            # Check if it wraps a facility or IS the facility (migrated)
            facilities = list(g_v3.objects(ctx_iri, V3.requiresFacility))
            if facilities:
                for facility in facilities:
                    g_v4.add((plan_iri_v4, V4.requiresFacility, facility))
            else:
                # Link to the migrated context entity itself
                ctx_iri_v4 = get_v4_iri(ctx_iri)
                g_v4.add((plan_iri_v4, V4.requiresFacility, ctx_iri_v4))

        elif V3.ToolContext in ctx_types:
            artifacts = list(g_v3.objects(ctx_iri, V3.requiresArtifact))
            if artifacts:
                for artifact in artifacts:
                    g_v4.add((plan_iri_v4, V4.requiresArtifact, artifact))
            else:
                ctx_iri_v4 = get_v4_iri(ctx_iri)
                g_v4.add((plan_iri_v4, V4.requiresArtifact, ctx_iri_v4))

        elif V3.SocialContext in ctx_types:
            agents = list(g_v3.objects(ctx_iri, V3.requiresAgent))
            if agents:
                for agent in agents:
                    g_v4.add((plan_iri_v4, V4.requiresAgent, agent))
            else:
                ctx_iri_v4 = get_v4_iri(ctx_iri)
                g_v4.add((plan_iri_v4, V4.requiresAgent, ctx_iri_v4))

        elif V3.EnergyContext in ctx_types:
            energy_iri_v4 = get_v4_iri(ctx_iri)
            g_v4.add((plan_iri_v4, V4.requiresEnergyContext, energy_iri_v4))

    return g_v4


def migrate_action_process(g_v3, process_iri_v3):
    """
    Migrate v3 ActionProcess to v4 CCO PlannedAct.
    """
    process_iri_v4 = get_v4_iri(process_iri_v3)

    g_v4 = Graph()
    g_v4.bind("v4", V4)
    g_v4.bind("cco", CCO)

    # Change class from v3:ActionProcess to cco:PlannedAct
    g_v4.add((process_iri_v4, RDF.type, CCO.ont00000228))

    skip_props = [V3.hasState, V3.prescribedBy, RDF.type]
    migrate_properties(g_v4, process_iri_v4, g_v3, process_iri_v3, skip_props)

    for p, o in g_v3.predicate_objects(process_iri_v3):
        if p == V3.hasState:
            # Convert hasState → hasPhase
            state_iri = URIRef(str(o).replace("/v3#", "/v4#"))
            phase_name = str(state_iri).split("#")[-1]
            phase_iri = V4[phase_name]
            g_v4.add((process_iri_v4, V4.hasPhase, phase_iri))
        elif p == V3.prescribedBy:
            # Convert to CCO prescribes inverse (Plan prescribes Act)
            # OR keep prescribedBy (Act prescribedBy Plan) if V4 supports it.
            # Design says "prescribedBy -> prescribedBy" is valid.
            # But let's follow the "prescribes" preference if possible.
            # Actually CCO has `is_prescribed_by` (ont00000965 inverse). 
            # But V3 used `prescribedBy`. 
            # Let's map to V4 `prescribes` (inverse) as per previous script
            # or `v4:prescribedBy` if we want to keep direction.
            # Given previous script used `prescribes` (inverse), let's stick to that for consistency with design "prescribes" property.
            plan_iri_v4 = get_v4_iri(o)
            g_v4.add((plan_iri_v4, V4.prescribes, process_iri_v4))

    return g_v4


def migrate_milestone(g_v3, milestone_iri_v3):
    """
    Migrate v3 Milestone from RootActionPlan subclass to Directive ICE subclass.
    """
    milestone_iri_v4 = get_v4_iri(milestone_iri_v3)

    g_v4 = Graph()
    g_v4.bind("v4", V4)
    g_v4.bind("cco", CCO)

    # Change: v3:Milestone (subclass of RootActionPlan) → v4:Milestone (subclass of DirectiveICE)
    g_v4.add((milestone_iri_v4, RDF.type, V4.Milestone))

    # Copy properties
    migrate_properties(g_v4, milestone_iri_v4, g_v3, milestone_iri_v3, [V3.parentAction, RDF.type, V3.hasProject])

    # Link to objective if it had project
    for project_name in g_v3.objects(milestone_iri_v3, V3.hasProject):
        safe_name = (
            str(project_name).lower().strip().replace(" ", "_").replace("/", "_").replace("\\", "_")
        )
        objective_iri = URIRef(f"urn:objective:{safe_name}")
        g_v4.add((milestone_iri_v4, V4.marksProgressToward, objective_iri))

    return g_v4

def migrate_context_entity(g_v3, ctx_iri_v3):
    """
    Migrate a context entity to V4.
    """
    ctx_iri_v4 = get_v4_iri(ctx_iri_v3)
    g_v4 = Graph()
    
    ctx_types = list(g_v3.objects(ctx_iri_v3, RDF.type))
    
    new_type = None
    if V3.EnergyContext in ctx_types:
        new_type = V4.EnergyContext
    elif V3.LocationContext in ctx_types:
        new_type = CCO.ont00000192 # Facility
    elif V3.ToolContext in ctx_types:
        new_type = CCO.ont00000001 # Artifact
    elif V3.SocialContext in ctx_types:
        new_type = CCO.ont00000374 # Agent
        
    if new_type:
        g_v4.add((ctx_iri_v4, RDF.type, new_type))
        # Migrate properties, skipping V3 context specific links that are no longer needed on the context itself
        # (e.g. requiresFacility on LocationContext is redundant if LocationContext BECOMES Facility)
        skip = [V3.requiresFacility, V3.requiresArtifact, V3.requiresAgent, RDF.type]
        migrate_properties(g_v4, ctx_iri_v4, g_v3, ctx_iri_v3, skip)
        return g_v4
    return None

def full_migration(v3_file, v4_file):
    """
    Perform full v3→v4 migration.
    """
    print(f"Migrating {v3_file} → {v4_file}...")

    g_v3 = Graph()
    g_v3.parse(v3_file, format="turtle")

    g_v4 = Graph()
    g_v4.bind("v4", V4)
    g_v4.bind("cco", CCO)
    g_v4.bind("bfo", BFO)
    g_v4.bind("schema", SCHEMA)

    # Count entities
    plan_subclasses = [
        V3.ActionPlan,
        V3.RootActionPlan,
        V3.ChildActionPlan,
        V3.LeafActionPlan,
    ]
    plans = []
    for sc in plan_subclasses:
        plans.extend(list(g_v3.subjects(RDF.type, sc)))
    
    # Remove duplicates
    plans = list(set(plans))
    plans_count = len(plans)

    processes = list(g_v3.subjects(RDF.type, V3.ActionProcess))
    processes_count = len(processes)
    
    milestones = list(g_v3.subjects(RDF.type, V3.Milestone))
    milestones_count = len(milestones)

    print(f"  Found {plans_count} action plans")
    print(f"  Found {processes_count} action processes")
    print(f"  Found {milestones_count} milestones")

    # Migrate all plans
    for plan_iri in plans:
        g_v4 += migrate_action_plan(g_v3, plan_iri)

    # Migrate all processes
    for process_iri in processes:
        g_v4 += migrate_action_process(g_v3, process_iri)

    # Migrate milestones
    for ms_iri in milestones:
        g_v4 += migrate_milestone(g_v3, ms_iri)

    # Migrate context entities
    context_classes = [V3.EnergyContext, V3.LocationContext, V3.ToolContext, V3.SocialContext]
    for ctx_class in context_classes:
        for ctx_iri in g_v3.subjects(RDF.type, ctx_class):
            res = migrate_context_entity(g_v3, ctx_iri)
            if res:
                g_v4 += res

    # Write output
    g_v4.serialize(v4_file, format="turtle")
    print(f"  ✅ Wrote {len(g_v4)} triples to {v4_file}")
    print("Migration complete!")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python v3_to_v4.py <input.ttl> <output.ttl>")
        print("\nExample:")
        print(
            "  python v3_to_v4.py examples/v3/valid/simple-actionplan.ttl examples/v4/migrated/simple-actionplan.ttl"
        )
        sys.exit(1)

    try:
        full_migration(sys.argv[1], sys.argv[2])
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"File not found: {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
