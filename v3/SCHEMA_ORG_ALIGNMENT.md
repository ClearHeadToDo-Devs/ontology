# Schema.org Alignment Strategy

## Problem Statement

Schema.org and BFO are two different ontology frameworks with incompatible upper ontologies:

- **BFO**: Formal upper ontology with continuant/occurrent distinction, designed for scientific rigor
- **Schema.org**: Pragmatic vocabulary for web markup, SEO, and search engines

We want to leverage both: BFO for semantic rigor, Schema.org for web/SEO benefits.

## Solution: Two-Level Alignment Strategy

### Level 1: Classes → SKOS Mapping

**Use `skos:closeMatch` for class alignment** because classes inherit from different upper ontologies:

```turtle
@prefix actions: <https://vocab.example.org/actions/v3#> .
@prefix cco: <https://www.commoncoreontologies.org/> .
@prefix schema: <http://schema.org/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

# BFO/CCO hierarchy (formal inheritance)
actions:ActionPlan rdfs:subClassOf cco:ont00000965 .  # DirectiveInformationContentEntity
actions:ActionPlan rdfs:subClassOf bfo:InformationContentEntity .  # via CCO

# Schema.org mapping (cross-vocabulary alignment)
actions:ActionPlan skos:closeMatch schema:Action .
```

**Why not `rdfs:subClassOf schema:Action`?**
- Would create multiple inheritance from two upper ontologies
- Could confuse reasoners
- Mixes BFO and Schema.org philosophical commitments
- Violates "don't cross upper ontology boundaries" principle

**Why SKOS?**
- ✅ Designed specifically for cross-vocabulary mapping
- ✅ Machine-readable semantics
- ✅ Doesn't interfere with OWL reasoning
- ✅ Widely adopted in semantic web community
- ✅ Multiple granularities available

### Level 2: Properties → rdfs:subPropertyOf

**Direct inheritance is safe for properties** because they don't have upper ontology commitments:

```turtle
# These are fine - properties are more flexible
actions:hasDoDate rdfs:subPropertyOf schema:startTime .
actions:hasDueDate rdfs:subPropertyOf schema:endTime .
actions:hasCompletedDateTime rdfs:subPropertyOf schema:endTime .
actions:hasUUID rdfs:subPropertyOf schema:identifier .
actions:hasContext rdfs:subPropertyOf schema:location .
actions:hasState rdfs:subPropertyOf schema:actionStatus .
```

**Why this works:**
- Properties don't inherit upper ontology constraints
- RDF property hierarchies are simpler than class hierarchies
- Enables Schema.org tooling to recognize our properties
- SEO benefits without breaking BFO reasoning

## SKOS Vocabulary Reference

SKOS provides multiple mapping properties with different strengths:

### 1. `skos:exactMatch`
**Use when:** Concepts are identical for all applications
- Strongest mapping
- Rare in cross-ontology alignment
- Example: Two vocabularies defining the exact same concept

### 2. `skos:closeMatch` ✅ **OUR CHOICE**
**Use when:** Concepts are sufficiently similar for many applications
- Strong but not identical
- Appropriate for ActionPlan ↔ schema:Action
- "Close enough for practical purposes"

### 3. `skos:relatedMatch`
**Use when:** Concepts are related but not similar
- Weaker association
- Example: Related but distinct concepts

### 4. `skos:broadMatch` / `skos:narrowMatch`
**Use when:** One concept is broader/narrower than another
- Hierarchical relationships across vocabularies
- Example: schema:Action is broader than actions:ActionPlan

## Examples in Action

### Class Alignment

```xml
<!-- OWL/XML -->
<owl:Class rdf:about="https://vocab.example.org/actions/v3#ActionPlan">
    <!-- BFO/CCO hierarchy -->
    <rdfs:subClassOf rdf:resource="http://www.ontologyrepository.com/CommonCoreOntologies/Plan"/>

    <!-- Schema.org mapping -->
    <skos:closeMatch rdf:resource="http://schema.org/Action"/>

    <rdfs:label>Action Plan</rdfs:label>
    <rdfs:comment>
        A plan that prescribes an action to be performed.
        Closely aligned with Schema.org Action via SKOS mapping.
    </rdfs:comment>
</owl:Class>
```

### Property Alignment

```xml
<!-- Direct inheritance is fine for properties -->
<owl:DatatypeProperty rdf:about="https://vocab.example.org/actions/v3#hasDoDate">
    <rdfs:domain rdf:resource="https://vocab.example.org/actions/v3#ActionPlan"/>
    <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#date"/>

    <!-- Safe to use subPropertyOf -->
    <rdfs:subPropertyOf rdf:resource="http://schema.org/startTime"/>

    <rdfs:label>has do date</rdfs:label>
    <rdfs:comment>When action should be performed (scheduled start)</rdfs:comment>
</owl:DatatypeProperty>
```

## Benefits of This Approach

### For BFO Reasoning
✅ Clean class hierarchy rooted in BFO
✅ No multiple inheritance conflicts
✅ Reasoners can process without confusion
✅ Formal semantics preserved

### For Schema.org Integration
✅ Machine-readable mapping to Schema.org concepts
✅ Properties inherit Schema.org semantics
✅ Search engines can recognize aligned properties
✅ SEO benefits for web-published data

### For Downstream Applications
✅ Clear documentation of relationships
✅ Applications can choose which alignment to follow
✅ JSON-LD context can map to either vocabulary
✅ Flexibility for different use cases

## Implementation Checklist

When adding new classes:
- [ ] Define `rdfs:subClassOf` relationship to BFO/CCO parent
- [ ] Add `skos:closeMatch` to Schema.org equivalent (if exists)
- [ ] Document the mapping rationale in `rdfs:comment`

When adding new properties:
- [ ] Define domain and range
- [ ] Add `rdfs:subPropertyOf` to Schema.org property (if appropriate)
- [ ] Ensure range types are compatible

## Tools That Understand SKOS

- **Protégé**: Displays SKOS mappings in annotations
- **SPARQL**: Can query across SKOS mappings
- **Ontology alignment tools**: Recognize SKOS as standard
- **Semantic web frameworks**: Built-in SKOS support

## References

- **SKOS Specification**: https://www.w3.org/TR/skos-reference/
- **SKOS Primer**: https://www.w3.org/TR/skos-primer/
- **Schema.org**: https://schema.org/
- **BFO**: http://basic-formal-ontology.org/
- **Common Core Ontologies**: https://github.com/CommonCoreOntology/CommonCoreOntologies

## Decision Log

**2025-01-25**: Adopted `skos:closeMatch` for ActionPlan ↔ schema:Action alignment
- Rationale: Avoids multiple inheritance from incompatible upper ontologies
- Alternative considered: `rdfs:subClassOf schema:Action` - rejected due to reasoning conflicts
- Community practice: SKOS is the standard approach for cross-ontology mapping
