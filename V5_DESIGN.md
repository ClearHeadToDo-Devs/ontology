# V5 Design Proposal: Plans All the Way Down

**Version**: 5.0.0-proposal **Date**: 2026-09-30 **Status**: Proposal, open questions below

## Why

Reading CUBRC's *Modeling Information with the Common Core Ontologies* against the current CCO (checkout `be13b74`, 2026-09-25) showed that v4 narrows or duplicates CCO where it should reuse it:

- v4 narrows `cco:Plan` to "a recurrence prescription — a schedule-backed template that prescribes Actions". CCO's Plan is general.
- `actions:Action` is a sibling of `cco:Plan` under Prescriptive ICE, yet everything an Action is (information prescribing an intended act toward some end) is what a Plan is.
- `actions:Charter` and its states (New, Active, Closed) run a second state machine beside Action statuses, although both say the same thing: whether the prescribed work has started, is going, or is over.
- Status is recorded on the information entity. CCO measures status on processes.

## What CCO says

| Term | IRI | Definition (verbatim) |
| --- | --- | --- |
| Plan | ont00000974 | A Prescriptive Information Content Entity that prescribes some set of intended Intentional Acts through which some Agent expects to achieve some Objective. Axiom: *has continuant part some Objective*. No subclasses. |
| Objective | ont00000476 | A Prescriptive Information Content Entity that prescribes some projected state that some Agent intends to achieve. |
| prescribes | ont00001942 | x prescribes y iff x is an Information Content Entity and y an Entity, such that x serves as a rule or guide for y if y is an Occurrent, or as a model for y if y is a Continuant. |
| Planned Act | ont00000228 | An Act in which at least one Agent plays a causative role and which is prescribed by some Directive Information Content Entity held by at least one of the Agents. |
| Unplanned Act | ont00000546 | An Act … not prescribed by some Objective held by any of the Agents. |
| Act of Planning | ont00000511 | A Planned Act that involves making a Plan to achieve some specified Objective. |
| Event Status Nominal ICE | ont00000203 | A Nominal Measurement ICE that is a measurement of the current state of a process. |

CUBRC (section 3.3) distinguishes the ordinary `prescribes`, which links a plan to "some actual [act] that was following the plan (or trying to)", from the modal `prescribes`, which links it to the act "as described exactly in the plan".

CCO has no Schedule, Task, Project or Calendar Event class. Calendars appear only as time (Calendar Day, Calendar System).

## Proposed model

| Today | v5 | Notes |
| --- | --- | --- |
| Objective (`.md`) | `cco:Objective` | Unchanged. Shared by several plans. |
| Action (`.actions` line) | `cco:Plan` | The smallest plan: one step. Child actions are plan parts (`bfo:has_part`); sequence stays `is_predecessor_of`. |
| Charter (`.actions` file + `.md`) | `cco:Plan` | A plan with a document. Its `objectives` become *has part* Objective; a "Done when" section states its objective. |
| Plan (`.ics` VTODO with RRULE) | `cco:Plan` that prescribes recurring acts | The name "Plan" moves to the general notion; this needs a new name (open question 3). Its occurrences are plan parts pinned to dates. |
| Action status, Charter state | one status: Event Status on the prescribed act | Charter New / Active / Closed and Action NotStarted / InProgress / Completed / Cancelled become one scale. `[x]` on a plan remains shorthand for the status of the act it prescribes. |
| (not modeled) | `cco:Planned Act` | What happened: an attempt or a completion, with agent, interval, outcome and outputs, linked by ordinary `prescribes` from the plan. Recorded by whoever acted (e.g. the agent sandbox), never in the plan files. |
| (not modeled) | `cco:Act of Planning` | The act that produced a plan, when it is worth recording. |

Genuine extensions left in `actions:`: `inServiceOf` if still needed beside *has part* Objective (open question 4), GTD contexts, and the application data properties. `actions:Charter` and `actions:Action` retire as classes.

## What does not change

The file formats. `.actions` files, charter `.md` documents, objective `.md` files and `.ics` series keep their syntax and layout; what changes is the RDF they project to. User-facing words ("charter", "action") may stay as names for kinds of plan: that is a separate, later decision.

## Open questions for the human

1. **Is every action a Plan?** Proposed: yes.
2. **Areas without an end** (the root, `support`): a Plan whose objective is a maintained state, or keep a Charter class only for areas? Proposed: a Plan; CCO's Objective does not require an end.
3. **The recurring plan's name**, once "Plan" means the general notion: schedule, series, routine, or keep "plan" for it in files and say "recurring plan" in the model.
4. **`inServiceOf`**: still needed once a Plan *has part* its Objective, or only for a plan serving an objective it does not contain (for example a shared objective)?
5. **Scheduling**: proposed that a single time stays on the plan (`^date`) and `.ics` holds recurring series and their exceptions only.
6. **Unifying states**: charter New and action NotStarted become one value; how does a workspace migrate the charter state field?
