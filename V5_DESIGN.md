# V5 Design: Domain Grounding

**Version**: 5.0.0-draft **Date**: 2026-09-30 **Status**: Grounding — domain in plain words, first pass of CCO alignment

## Order of work

1. Competency questions: what the model must be able to answer.
2. The domain in plain words, drawn from those questions.
3. Alignment with BFO and CCO, where CCO sharpens the domain or reveals a gap.
4. Only then, and outside this document: how the spec and its implementations represent it.

The first V5 proposal (commit 4eca6e7) went the other way: it started from file formats and asked which CCO class each fit. It was withdrawn.

## Competency questions

From the human, lightly edited:

1. What do I need to do to complete my weekly review?
2. Which steps depend on other steps for my objective to come to fruition?
3. Which steps can I do within my current context, energy and priorities?
4. How do I define done for my objectives, and how do I keep track of my plans and their steps?
5. Which plans go toward a given objective?
6. Did we fulfil those plans? If not, why not?
7. What other details does the plan need to succeed?
8. What are the risks, dependencies and supporting materials for this objective?

## Principle

The system holds only information: plans, objectives, and records of what happened. The acts, events and states they are about exist, or fail to, in the world. A plan exists whether or not anyone ever carries it out.

## The domain

- **Objective**: a state someone wants to be true. Some are *achieved* once (get a degree, file taxes); some are *maintained* per period and never finish (run three times a week).
- **Plan**: aims at one or more objectives and contains steps. Without an objective it is not a plan; without steps it is a plan still being planned.
- **Step**: prescribes something to do. Steps contain steps. Splitting stops when whoever does the step can do it without further planning, so the right depth depends on the doer, not the step. A step may state where or with what it can be done (context), the energy it calls for, a time (fixed, recurring, or none), and what it waits on.
- **Waiting**: a step waits on an event: another step being done, or something outside (a reply, a delivery). The system knows an event through a record of it.
- **Record**: information that something happened: who acted, when, the outcome, and why it fell short.
- **Area of focus**: a standing responsibility with no end ("errands"). It groups steps and objectives, and can hold steps that serve no stated objective.
- **Values statement**: what objectives answer to ("be a good partner", "live with integrity"). Never achieved; only reviewed.
- **Weekly review**: a recurring plan whose steps review the other plans: judging maintained objectives and values, and finding plans whose steps no longer lead to their objective.

## Distinctions to keep

- **Fulfilling a plan is not achieving its objective.** When every step is done and the objective is not met, either the objective is too vague (no clear done-condition) or the steps were the wrong ones. The model must tell these apart.
- **Planning done is not work done.** A plan can be complete as a plan while none of its work has started, and the reverse.
- **The doer's situation is not the step's requirement.** Current energy and whereabouts belong to the question being asked; the step states only what it calls for.
- **A plan is sufficient when someone else could carry it out** from what it holds: objective and done-condition, steps, risks, dependencies, materials.
- **"Context" means two things**: where or with what a step can be done, and the information a plan carries. Name them apart later.

## Open threads

- Who declares an objective achieved? Proposed: a person, or an agent they trust, and the declaration is itself a record; the system shows evidence but never decides.
- Areas of focus and values statements: entities of their own, or properties of objectives? Proposed: entities, because many objectives share one, and an area can hold steps with no objective at all.
- When does a step become a plan? Proposed: when it gains an objective of its own, which is worth stating only when doing the step does not guarantee the outcome.

## Alignment with CCO

Checked against CCO `develop` at be13b74 (2026-09-25), merged file. BFO relations are cited by label.

### How CCO links a plan to what happened

A plan does not reach its acts directly. A Planned Act is *defined* as an Act that **realizes** a role or disposition of the agent, which **concretizes** a Prescriptive Information Content Entity. A plan is followed when an agent holds it (it is concretized in them) and acts on it. `prescribes` (plan → act) is the shortcut. So who carries out a step is not a property of the step: it is the agent in whom the plan is concretized and who is `agent in` the act.

### Mapping

| Domain | CCO / BFO | Fit |
| --- | --- | --- |
| Objective (achieve) | Objective: "prescribes some projected state that some Agent intends to achieve" | Exact. |
| Objective (maintain) | Objective prescribing a Stasis ("a Process in which one or more Independent Continuants endure in an unchanging condition") | Good, no new term. |
| Plan | Plan: prescribes intended acts toward some Objective; axiom *has continuant part some Objective* | Exact, and the axiom is your answer 2: no objective, no plan. |
| Step | none | **Gap.** A step cannot be a cco:Plan without an Objective part. Needs a new Prescriptive ICE subclass, part of a plan. A step that gains an objective is then also a Plan. |
| Waiting | `precedes` holds only between occurrents (acts that happened) | **Gap.** Waiting is stated in the plan about acts that may never exist. Needs one relation from a step to what it waits on: another step, or a description of an expected outside event. |
| Record | Report ("conveys an account of some event … or the result of some observation"); more generally a Descriptive ICE `is about` the act | Good. |
| Status (done, in progress) | Event Status Nominal ICE: "a measurement of the current state of a process", `is a nominal measurement of` the act | Good, and it settles *planning done vs work done*: one is the status of the Act of Planning, the other the status of the planned acts. |
| Objective achieved | Deviation Measurement ICE ("the extent to which an entity conforms to how it is expected or supposed to be"), output of an Act of Measuring with an agent | Good. The declaration is a record with an author, as proposed. |
| Weekly review | a Plan prescribing Acts of Planning (and Acts of Measuring for objectives) | Good, no new term. |
| Priority | Priority Measurement ICE, against a Priority Scale | Exact. |
| Risk | Predictive ICE ("describes an uncertain future event"), optionally with a Probability Measurement | Good. |
| Supporting material | any ICE that `is about` the objective or `is input of` the act | Good. |
| Time | Temporal Interval / Instant; the act `occupies temporal region` | Good for single times. **Gap** for recurrence: CCO has no recurrence rule. |
| Area of focus | BFO role (a realizable entity borne because of circumstances: parent, maintainer) | Good, but it changes what an area is: see below. |
| Values statement | none; closest is Performance Specification ("prescribes some aspect of the behavior of a participant in a Process") | **Gap.** Performance Specification is engineering-flavored; likely a new Prescriptive ICE subclass. |
| Context, energy (step requirements) | none directly | **Gap**, small: properties on a step. |
| Agent | Agent: "a Material Entity that bears an Agent Capability" | Fits people. Open for AI agents: see below. |

### What the alignment pushes back on

- **An area of focus is a role, not information.** "Errands" is something you bear (household member, maintainer of the platform), and the steps in it realize that role. The system stores a description of the role, not the role itself. This also explains why an area holds steps with no objective: roles are realized by acts, not by reaching states.
- **"Run three times a week" is a plan, not an objective.** It prescribes acts. Its objective is a state such as being fit. A true maintained objective prescribes a stasis ("inbox stays near empty").
- **Status is a record.** It measures an act, so it is a fact with an author and a time, like any record.

### CCO 3.0 and 4.0

Checked 2026-09-30 against the CCO milestones on GitHub. 3.0 (due 2026-12-31) has 25 open issues and none closed. 4.0 (due 2027-06-30) has 6, all geospatial. CCO's governance board recommends waiting for 4.0 before updating.

- **Untouched by either release:** Plan, Objective, Planned Act, Act of Planning, Act of Measuring, prescribes, is about, Event Status, Stasis, Predictive ICE, Deviation Measurement. Everything this note leans on is stable enough to align to now.
- **In flux in 3.0:** how information relates to what carries it, and the media subtree. Image vs Representational ICE (#875, #593), Book/Database/Spreadsheet moving to Information Medium Artifact (#682), ICE vs qualities of bearers (#596), QUDT replacing CCO measurement units (#307). So a Record is modelled as a Descriptive ICE that `is about` the act, not as Report. Priority Scale may move from Descriptive to Directive (#147); that is cosmetic for us.
- **Wanted from 3.0:** the re-introduced Information Structure Entity (#949, draft module on branch `information-structure-pr`, 2025-06-30) separates how information is structured from what it says. That is the layer this note keeps out of the ontology: a plan is content, and a list of lines, a document or a calendar entry is a structure carrying it. If 3.0 adopts it, the spec's formats can be stated as Information Structures in CCO's own terms. It is a draft with no discussion yet, so it is a direction to watch, not something to build on.
- **Stale text:** some definitions still cite classes that no longer exist ("Directive Information Content Entity" in Planned Act, "Intentional Acts" in Plan). The axioms use Prescriptive ICE. Read the axioms, not the prose.
- **Our pin is behind:** our imports are the 2024-11-06 CCO modules and BFO 2019; current tags are CCO v2.2 on BFO 2020. Align to v2.2 by tag, as the specs are pinned, and re-check when 3.0 is tagged.
- Is an AI agent a cco:Agent? An Agent is a material entity bearing an Agent Capability (definitions under discussion in #925). The defensible reading is that the running machine bears the capability, and the model is information it concretizes. Undecided.

### Extensions needed

Five, all small: **Step** (Prescriptive ICE, part of a Plan), **waits on** (step → step or expected-event description), **Values Statement** (Prescriptive ICE), **recurrence** (on a step or plan), and **step requirements** (context, energy). Everything else is CCO or BFO as is.
