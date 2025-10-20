# Vocabulary Introduction
As part of the clearhead platform, we want to build out a foundation that is both logically sound while also conforming to exsting standards.

To this end, we are going to be using the ontology defined within this repository our core foundation upon which all applications can be built

## Terms
For now we are working primarily with Actions which are a generic format that is intended to express an intent to complete something as either an individual or a system

To this end, we are trying to conform to the [Action Class on Schema.org](https://schema.org/Action)


we are trying to take the base class while extending it to include support for:
- GTD-style context lists
- optional support for the [Project Class](https://schema.org/Project) as the parent to the Root Action class
- recurrance support for both the do-date and the due-date
- support for both the due-date and do-date for scheduling support

# Purpose
The purpose of this repo works at many levels:
- at the highest level, this is our base ground of reality, how the various _things_ within our domain are understood and should be seen as a living document that is updated when our understanding of the domain changes
- this will also help implementors start to work with this set of classes as they implement various data and writing mechanisms including
    - parsers for file formats
    - schemas for semi-structured files
    - schemas for databases
    - class structures for applications

    while this is going to still leave implementation details open, it should give implementors a good base of reality

    ## Small waist
    This will allow us to generate the proper schemas and class structures and will atleast make testing much easier since we will know the exchange format we plan to use as well for our base layer of structure

# Class Structure
At its base, we have the `PlannedAction` class which is a subclass of the Action class of schema.org and we have a few key sublcasses of those:
- `Root`
    - MAY have an action as the parent but does not have to
    - MAY have 1 or more child Actions
- `Child`
    - MUST have a parent `Root` Action or `Child` action
    - MAY have one or more `Child` Actions or `Leaf` Actions
- `Leaf`
    - MUST have a parent `Child` action
    - CANNOT have child actions

We have a state hierarchy that extends to the [actionStatusType](https://schema.org/ActionStatusType) that includes the ones defined [Active, Completed, Failed, Potential] and adds two more:
- Blocked

# Tooling
To support all this we are expecting people to leverage the tooling that will make this all most useful
- protege for a GUI to review ontology structure
- `pySHACL` for CLI validation

to support this we have a test suite that does SHACL validation on a set of valid and invlaid TTL documents that one can use to both validate the current state of the constraints while also getting some examples of what code snippets may look like
