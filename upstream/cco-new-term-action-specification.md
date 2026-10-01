# Draft: CCO new term request — Action Specification

Draft for the human to review and file at https://github.com/CommonCoreOntology/CommonCoreOntologies/issues, following CCO's "Instructions for Creating a New Term Request". No existing issue covers it (searched 2026-09-30). Once CCO publishes the term, ClearHead switches from IAO_0000007 to the CCO IRI.

---

**Title:** New Term: Action Specification

**Ontology file:** Information Entity Ontology

**Scope and reasoning**

A Plan (ont00000974) "prescribes some set of intended Intentional Acts" and has continuant part some Objective, but CCO has no term for the parts of a plan that each prescribe one of those acts. Task lists, checklists and procedures need them: a weekly review plan whose parts are "collect loose papers", "process the inbox" and so on, each prescribing one act and ordered among themselves.

IAO has this term as action specification (IAO_0000007), a part of plan specification beside objective specification. CCO already sources Information Content Entity, is about, Information Bearing Entity and Algorithm from IAO; this would follow the same pattern.

Related CCO terms and why they do not fit:

- **Plan**: has an Objective as continuant part. A single step of a plan usually has no objective of its own, so typing steps as Plans either forces an objective onto each or leaves them misclassified.
- **Algorithm**: a whole "finite sequence of unambiguous instructions", not one instruction within it.
- **Process Requirement**: a Process Regulation, the output of a process realizing an Authority Role; a self-made step carries no authority.
- **Performance Specification**: prescribes behavior of a participant given operating conditions, not an act to perform.

The textual definition of Planned Act also cites a "Directive Information Content Entity", which CCO no longer has; Action Specification would give a planned act a prescribing information entity at the granularity of one act.

**Proposals**

- rdfs:label: Action Specification
- Definition: A Prescriptive Information Content Entity that prescribes some intended Act that an Agent is to perform.
- Source: IAO action specification (http://purl.obolibrary.org/obo/IAO_0000007), from the OBI Plan and Planned Process branch.
- Parent class: Prescriptive Information Content Entity (ont00000965)
- Example of usage: "Pour the contents of flask 1 into flask 2"; "Collect loose papers and materials" as a part of a weekly review Plan.
- Not proposed: an axiom requiring Plans to have Action Specifications as parts. A plan still being drafted may have none yet, and CCO's Plan currently requires only an Objective.
