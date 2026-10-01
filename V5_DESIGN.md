# V5 Design: Domain Grounding

**Version**: 5.0.0-draft **Date**: 2026-09-30 **Status**: Grounding — domain in plain words, first pass of CCO alignment

## Order of work

1. Competency questions: what the model must be able to answer.
2. The domain in plain words, drawn from those questions.
3. Alignment with BFO and CCO, where CCO sharpens the domain or reveals a gap.
4. Only then, and outside this document: how the spec and its implementations represent it.

Settled choices move to [docs/DECISIONS.md](docs/DECISIONS.md); this note keeps the analysis and the open threads.

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

**Status 2026-10-01:** all eight are answered by `robot query` files in `v5/queries/` (cq1–cq8, built from the human's examples and the real ground-the-ontology charter) and run by `make test`. Question 7 already reports a true gap: the weekly review's objective has no done-condition.

## Principle

The system holds only information: plans, objectives, and records of what happened. The acts, events and states they are about exist, or fail to, in the world. A plan exists whether or not anyone ever carries it out.

## The domain

- **Objective**: a state someone wants to be true. Some are *achieved* once (get a degree, file taxes); some are *maintained* per period and never finish (run three times a week).
- **Plan**: aims at one or more objectives and contains actions. Without an objective it is not a plan; without actions it is a plan still being planned.
- **Action** (an action specification, IAO_0000007): prescribes one thing to do; the product's word "action" means this, never the doing. Actions contain actions, and every action is part of some plan. Splitting stops when whoever does it can do it without further planning, so the right depth depends on the doer. An action may state where or with what it can be done (context), the energy it calls for, a time (fixed, recurring, or none), and what it waits on.
- **Waiting**: a action waits on an event: another action being done, or something outside (a reply, a delivery). The system knows an event through a record of it.
- **Record**: information that something happened: who acted, when, the outcome, and why it fell short.
- **Area of focus**: a plan whose objective is maintained and never finishes ("keep food in the house", "keep the tools pleasant to use"). Not a separate kind of thing. Every action is part of some plan; a action never floats free.
- **Values statement**: what objectives answer to ("be a good partner", "live with integrity"). Never achieved; only reviewed.
- **Weekly review**: a recurring plan whose actions review the other plans: judging maintained objectives and values, and finding plans whose actions no longer lead to their objective.

## Distinctions to keep

- **Fulfilling a plan is not achieving its objective.** When every action is done and the objective is not met, either the objective is too vague (no clear done-condition) or the actions were the wrong ones. The model must tell these apart.
- **Planning done is not work done.** A plan can be complete as a plan while none of its work has started, and the reverse.
- **The doer's situation is not the action's requirement.** Current energy and whereabouts belong to the question being asked; the action states only what it calls for.
- **A plan is sufficient when someone else could carry it out** from what it holds: objective and done-condition, actions, risks, dependencies, materials.
- **"Context" means two things**: where or with what a action can be done, and the information a plan carries. Name them apart later.

## Open threads

- Every plan names an objective, so the root charter needs one too (the human, 2026-10-01: "a plan without an objective is just people daydreaming"). The ontology stays strict; the cost is for the spec phase, proposed: a charter's "Done when" counts as its objective; `init` seeds the root a maintained objective once, as it seeds the root alias, editable afterward; a missing objective is a gap `doctor` reports, never a refusal to load.

Settled threads are in [docs/DECISIONS.md](docs/DECISIONS.md): objectives have state (5), every action is part of a plan and an action with its own objective is a plan (2), values and recurrence need no terms (6).

## Alignment with CCO

Checked against CCO `develop` at be13b74 (2026-09-25), merged file. BFO relations are cited by label.

### How CCO links a plan to what happened

A plan does not reach its acts directly. A Planned Act is *defined* as an Act that **realizes** a role or disposition of the agent, which **concretizes** a Prescriptive Information Content Entity. A plan is followed when an agent holds it (it is concretized in them) and acts on it. `prescribes` (plan → act) is the shortcut. So who carries out a action is not a property of the action: it is the agent in whom the plan is concretized and who is `agent in` the act.

### Mapping

| Domain | CCO / BFO | Fit |
| --- | --- | --- |
| Objective (achieve) | Objective: "prescribes some projected state that some Agent intends to achieve" | Exact. |
| Objective (maintain) | Objective prescribing a Stasis ("a Process in which one or more Independent Continuants endure in an unchanging condition") | Good, no new term. |
| Plan | Plan: prescribes intended acts toward some Objective; axiom *has continuant part some Objective* | Exact, and the axiom is your answer 2: no objective, no plan. |
| Action (was "Step") | **IAO action specification** (IAO_0000007): "a directive information entity that describes an action the bearer will take", part of a plan specification beside an objective specification | **Used as is**, not reinvented: CCO lacks it, IAO (BFO-based, the lineage of CCO's information branch) has it. Imported as a MIREOT module pinned to IAO 2026-03-30. "Part of some plan" is a `robot verify` check on our data, not an axiom on IAO's term. |
| Waiting | CCO **Performance Specification** with `describes condition` | CCO's own pattern; see the standards search below. |
| Record | Report ("conveys an account of some event … or the result of some observation"); more generally a Descriptive ICE `is about` the act | Good. |
| Status (done, in progress) | Event Status Nominal ICE: "a measurement of the current state of a process", `is a nominal measurement of` the act | Good, and it settles *planning done vs work done*: one is the status of the Act of Planning, the other the status of the planned acts. |
| Objective achieved | Deviation Measurement ICE ("the extent to which an entity conforms to how it is expected or supposed to be"), output of an Act of Measuring with an agent | Good. The declaration is a record with an author, as proposed. |
| Weekly review | a Plan prescribing Acts of Planning (and Acts of Measuring for objectives) | Good, no new term. |
| Priority | Priority Measurement ICE, against a Priority Scale | Exact. |
| Risk | Predictive ICE ("describes an uncertain future event"), optionally with a Probability Measurement | Good. |
| Supporting material | any ICE that `is about` the objective or `is input of` the act | Good. |
| Time | Temporal Interval / Instant; the act `occupies temporal region` | Good for single times. **Gap** for recurrence: CCO has no recurrence rule. |
| Area of focus | Plan whose Objective prescribes a Stasis | No new term. The role behind it (household member, maintainer) is real but about the agent, and is not stored, like a habit. |
| Values statement | BCIO personal value (a disposition) plus an information entity about it | Standard terms found: see below. |
| Context, energy (action requirements) | CCO **Performance Specification** ("behavior of a participant … given one or more operating conditions") | CCO's own pattern. |
| Agent | Agent: "a Material Entity that bears an Agent Capability" | Fits people, and AI agents as the running machine: see below. |

### What the alignment pushes back on

- **"Errands" is a context, not an area.** It says where a action can be done (out, at the store). "Buy milk" is done in the errands context *for* the plan "keep food in the house". Context is a action requirement; the plan is the container.
- **"Run three times a week" is a plan, not an objective.** It prescribes acts. Its objective is a state such as being fit. A true maintained objective prescribes a stasis ("inbox stays near empty").
- **Status is a record.** It measures an act, so it is a fact with an author and a time, like any record.

### CCO 3.0 and 4.0

Checked 2026-09-30 against the CCO milestones on GitHub. 3.0 (due 2026-12-31) has 25 open issues and none closed. 4.0 (due 2027-06-30) has 6, all geospatial. CCO's governance board recommends waiting for 4.0 before updating.

- **Untouched by either release:** Plan, Objective, Planned Act, Act of Planning, Act of Measuring, prescribes, is about, Event Status, Stasis, Predictive ICE, Deviation Measurement. Everything this note leans on is stable enough to align to now.
- **In flux in 3.0:** how information relates to what carries it, and the media subtree. Image vs Representational ICE (#875, #593), Book/Database/Spreadsheet moving to Information Medium Artifact (#682), ICE vs qualities of bearers (#596), QUDT replacing CCO measurement units (#307). So a Record is modelled as a Descriptive ICE that `is about` the act, not as Report. Priority Scale may move from Descriptive to Directive (#147); that is cosmetic for us.
- **Wanted from 3.0:** the re-introduced Information Structure Entity (#949, draft module on branch `information-structure-pr`, 2025-06-30) separates how information is structured from what it says. That is the layer this note keeps out of the ontology: a plan is content, and a list of lines, a document or a calendar entry is a structure carrying it. If 3.0 adopts it, the spec's formats can be stated as Information Structures in CCO's own terms. It is a draft with no discussion yet, so it is a direction to watch, not something to build on.
- **Stale text:** some definitions still cite classes that no longer exist ("Directive Information Content Entity" in Planned Act, "Intentional Acts" in Plan). The axioms use Prescriptive ICE. Read the axioms, not the prose.
- **Our pin is behind:** our imports are the 2024-11-06 CCO modules and BFO 2019; current tags are CCO v2.2 on BFO 2020. Align to v2.2 by tag, as the specs are pinned, and re-check when 3.0 is tagged.
- **AI agents (decided 2026-09-30):** the agent is the running machine, a cco:Agent bearing an Agent Capability. The model is part of it in two senses: the copy of the weights in memory is a material part of the machine, and the model's content is information the machine concretizes and acts on, as a person concretizes a plan. (CCO #925 questions the Agent definitions; it does not change this reading.)

### Extensions needed: standards search (2026-09-30)

Searched CCO v2.2 (with its extensions), IAO 2026-03-30, and all of OBO through the EBI Ontology Lookup Service, before minting anything.

| Gap | Existing terms found | Fit |
| --- | --- | --- |
| **Waits on** | IAO **conditional specification** (IAO_0000001): "a directive information entity that specifies what should happen if the trigger condition is fulfilled"; ICO **trigger condition directive** (ICO_0000252): "describes some state of affairs such that, if that state of affairs holds, some other prescription follows"; AFO **condition** (AFC_0000090): "about the portion of reality under which something occurs or is valid … restricts the possible realizations" | Good. "Get current waits on get clear" is a conditional specification with the get-current action as what should happen and, as its trigger, a description of the get-clear act being done. Standard `has part` and `is about` link them. Wordier than one edge (three nodes per wait), but nothing of ours. |
| **Action requirements** (context, energy) | the same conditional specification / AFO condition; the doer's energy is a quality of the person (HP **fatigue**, HP_0012378) | Good. "@home", "@computer", "low energy" are conditions under which the action is to be done, so waiting, context and energy are one pattern, as GTD treats them. Only the condition's description is stored; the doer's actual energy stays part of the question asked. |
| **Values statement** | BCIO **personal value** (BCIO_006063): "a mental disposition to regard certain things as fundamentally important in life, which informs standards for behaviour" | Good. The value is a disposition in the person (like a habit); a values statement is an information entity that `is about` it. No new class. |
| **Recurrence** (if it is more than format) | IAO **time trigger** (IAO_0000034, a conditional specification; uncurated, no definition); AFO **repeated action specification** (AFR_0001972, "an action specification that specifies a repeated activity", count-based lab repetition); CCO **Frequency** | Partial. A scheduled time is a time-triggered conditional specification; a rate is a prescribed Frequency; the calendar rule stays iCal RRULE (see open threads). |

Cautions: AFO's *role* terms (precondition, condition role) are roles of information entities, which BFO does not allow (roles inhere in independent continuants), so take AFO's **condition** class only. IAO's time trigger has no definition yet. AFO's licence must be checked before importing from it. BCIO's personal value belongs with the deferred habit work, and arrives through that door.

**Result:** every gap has a standard candidate. If these hold, ClearHead needs **no terms of its own**: CCO, IAO, ICO and BCIO cover the domain, the spec owns representation, and this repository reduces to examples and checks. **Tried 2026-09-30:** the weekly review was rebuilt with IAO conditional specifications in place of `ch:waitsOn`. The reasoner accepts it, both verify checks pass, and the first competency question returns the identical answer. `clearhead.ttl` now defines no terms. Cost: each wait is a conditional specification plus a trigger description (two nodes, four triples instead of one edge), and queries grow to match; the spec's compact `<` syntax can stay the file form and project to this. Caveat: the trigger is *about* the awaited action specification, standing in for its act, which may not exist yet.


**Update 2026-09-30, later:** the reasoner classified every IAO conditional specification as a CCO **Performance Specification**: CCO's `describes condition` rule (a prescription with a descriptive part describing a condition) is the conditional pattern, already in CCO. Waiting, context and energy now use Performance Specification directly; only IAO's action specification is still imported. All competency answers were unchanged by the switch.
