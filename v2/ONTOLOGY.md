# Actions Vocabulary Ontology

## Overview

The Actions Vocabulary provides a W3C-compliant semantic foundation for hierarchical task management systems. It extends Schema.org's Action class with specialized features for project organization, Getting Things Done (GTD) methodology, and structured task hierarchies while maintaining full compatibility with existing semantic web infrastructure.

**Namespace**: `https://vocab.example.org/actions/`  
**Version**: 2.1.0  
**Compatible with**: Schema.org Action, OWL 2, SHACL  

## Design Principles

### 1. Schema.org Compatibility
All core properties align with Schema.org Action to enable seamless integration with existing semantic web tools and search engines. Extension properties use `rdfs:subPropertyOf` relationships to maintain semantic consistency.

### 2. Hierarchical Structure
Actions support up to 6 levels of nesting (depths 0-5) with explicit structural constraints enforced through both OWL class definitions and SHACL shapes.

### 3. Plaintext Consideration  
The vocabulary acknowledges that action names serve as secondary keys in plaintext file formats, influencing design decisions around uniqueness and readability.

### 4. Temporal Flexibility
Supports both scheduling (do-date) and deadline (due-date) concepts with optional duration and iCalendar-compatible recurrence patterns.

## Core Class Hierarchy

### Base Classes

#### `actions:Action`
**Parent**: `schema:Action`  
**Description**: Base class for all hierarchical tasks extending Schema.org Action with task management specific properties.

**Key Features**:
- Hierarchical organization support
- Project and context association  
- Temporal scheduling with recurrence
- State management beyond simple completion
- UUID-based identification with human-readable names

### Structural Subclasses

#### `actions:RootAction` (Depth 0)
**Parent**: `actions:Action`  
**Description**: Top-level actions that serve as entry points in the hierarchy.

**Constraints**:
- Cannot have parent actions
- May belong to projects/stories  
- Can have child or leaf actions
- Only actions that can be assigned to projects

**Use Cases**:
- Independent tasks
- Project milestones
- Top-level goals

#### `actions:ChildAction` (Depths 1-4)
**Parent**: `actions:Action`  
**Description**: Intermediate actions that have both parents and potential children.

**Constraints**:
- Must have exactly one parent (RootAction or ChildAction)
- Cannot be assigned to projects (inherit from parent)
- Can have child or leaf actions
- Support up to 4 levels of intermediate nesting

**Use Cases**:
- Task breakdowns
- Sequential dependencies
- Grouped related activities

#### `actions:LeafAction` (Depth 5)  
**Parent**: `actions:Action`  
**Description**: Terminal actions at the maximum nesting level.

**Constraints**:
- Must have exactly one ChildAction parent
- Cannot have child actions
- Cannot be assigned to projects
- Represent atomic, executable tasks

**Use Cases**:
- Individual work items
- Specific deliverables  
- Actionable tasks

## State Management

### `actions:ActionState`
**Parent**: `schema:ActionStatusType`  
**Description**: Enumeration of states extending Schema.org with task management specific values.

#### State Definitions

| State | Symbol | Schema.org Equivalent | Description |
|-------|--------|----------------------|-------------|
| `actions:NotStarted` | ' ' | `schema:PotentialActionStatus` | Default state, no work begun |
| `actions:InProgress` | '-' | `schema:ActiveActionStatus` | Currently being worked on |
| `actions:Completed` | 'x' | `schema:CompletedActionStatus` | Successfully finished |
| `actions:Blocked` | '=' | *(extension)* | Waiting on external dependency |
| `actions:Cancelled` | '_' | *(extension)* | Abandoned, will not be completed |

**Key Property**: `actions:state`
- **Domain**: `actions:Action`
- **Range**: `actions:ActionState`  
- **Cardinality**: Exactly 1
- **Functional**: Yes

## Core Properties Reference

### Identity & Content

#### `actions:name`
#### `schema:name` *(inherited from Schema.org)*
- **Type**: `owl:DatatypeProperty`
- **Domain**: `schema:Thing` (inherited by `actions:Action`)
- **Range**: `xsd:string`
- **Description**: Human-readable title serving as secondary key in plaintext contexts
- **Source**: [Schema.org Thing](https://schema.org/Thing)

#### `schema:description` *(inherited from Schema.org)*
- **Type**: `owl:DatatypeProperty`
- **Domain**: `schema:Thing` (inherited by `actions:Action`)  
- **Range**: `xsd:string`
- **Description**: Extended details about the action
- **Source**: [Schema.org Thing](https://schema.org/Thing)

#### `actions:uuid`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`  
- **Domain**: `actions:Action`
- **Range**: `xsd:string`
- **Schema.org**: `rdfs:subPropertyOf schema:identifier`
- **Description**: Version 7 UUID for universal uniqueness
- **Standard**: [UUID Version 7](https://tools.ietf.org/html/draft-peabody-dispatch-new-uuid-format)

### Hierarchical Structure

#### `actions:parentAction`
- **Type**: `owl:ObjectProperty`
- **Domain**: `actions:ChildAction ∪ actions:LeafAction`
- **Range**: `actions:RootAction ∪ actions:ChildAction`
- **Description**: Links child/leaf actions to their hierarchical parent

#### `actions:depth`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`  
- **Range**: `xsd:nonNegativeInteger` (0-5)
- **Description**: Optional calculated hierarchical depth level
- **Validation**: Must match actual parent chain when specified

### Project Management

#### `actions:project`
- **Type**: `owl:DatatypeProperty`
- **Domain**: `actions:RootAction` *(only)*
- **Range**: `xsd:string`
- **Description**: Project or story name for organizational grouping
- **Constraint**: Only root actions can have project assignments

#### `actions:priority`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:positiveInteger` (1-4)
- **Description**: Priority level based on Eisenhower Decision Matrix
- **Reference**: [Time Management - Eisenhower Method](https://en.wikipedia.org/wiki/Time_management#The_Eisenhower_Method)

**Priority Levels**:
1. **Urgent & Important** - Do first
2. **Important, Not Urgent** - Schedule  
3. **Urgent, Not Important** - Delegate
4. **Neither Urgent nor Important** - Eliminate

### GTD Context System

#### `actions:context`
- **Type**: `owl:DatatypeProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:string`
- **Schema.org**: `rdfs:subPropertyOf schema:location`
- **Description**: GTD-style context tags indicating environmental requirements
- **Cardinality**: Multiple values allowed
- **Format**: Typically `@contextname` (e.g., `@phone`, `@computer`, `@errands`)
- **Reference**: [Getting Things Done](https://gettingthingsdone.com/)

**Common Contexts**:
- `@phone` - Requires phone/calling capability
- `@computer` - Requires computer/internet access  
- `@errands` - Location-based outside tasks
- `@office` - Requires office environment
- `@home` - Can be done at home
- `@anywhere` - Location independent

### Temporal Properties

#### Scheduling (Do Dates)

##### `actions:doDateTime`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:dateTime`  
- **Schema.org**: `rdfs:subPropertyOf schema:startTime`
- **Description**: When action should be performed (scheduled start)

##### `actions:doDate`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:date`
- **Schema.org**: `rdfs:subPropertyOf schema:startTime`
- **Description**: Date action should be performed

##### `actions:doTime`  
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:time`
- **Schema.org**: `rdfs:subPropertyOf schema:startTime`
- **Description**: Time action should be performed

#### Deadlines (Due Dates)

##### `actions:dueDateTime`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:dateTime`
- **Schema.org**: `rdfs:subPropertyOf schema:endTime`
- **Description**: When action must be completed by (deadline)

##### `actions:dueDate`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:date`
- **Schema.org**: `rdfs:subPropertyOf schema:endTime`
- **Description**: Date action must be completed by

##### `actions:dueTime`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:time`
- **Schema.org**: `rdfs:subPropertyOf schema:endTime`
- **Description**: Time action must be completed by

#### Completion Tracking

##### `actions:completedDateTime`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:dateTime`
- **Schema.org**: `rdfs:subPropertyOf schema:endTime`
- **Description**: When action was actually completed (auto-generated by tooling)

##### `actions:durationMinutes`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:positiveInteger`
- **Description**: Expected duration in minutes for completing the action
- **Validation**: 1 minute to 7 days (10080 minutes)

### Recurrence System

The vocabulary supports iCalendar-compatible recurrence patterns for creating repeating actions.

#### Core Recurrence Properties

##### `actions:recurrenceFrequency`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:string`
- **Values**: `"DAILY"`, `"WEEKLY"`, `"MONTHLY"`, `"YEARLY"`
- **Standard**: [RFC 5545 Section 3.3.10](https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10)

##### `actions:recurrenceInterval`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:positiveInteger`
- **Default**: 1 (every occurrence)
- **Description**: Interval between recurrences (e.g., 2 = every other occurrence)

#### Recurrence Termination

##### `actions:recurrenceUntil`
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:date`
- **Description**: End date for recurrence pattern
- **Constraint**: Mutually exclusive with `recurrenceCount`

##### `actions:recurrenceCount`  
- **Type**: `owl:DatatypeProperty`, `owl:FunctionalProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:positiveInteger`
- **Description**: Maximum number of recurrence instances
- **Constraint**: Mutually exclusive with `recurrenceUntil`

#### Recurrence Refinement Properties

##### `actions:byDay`
- **Type**: `owl:DatatypeProperty`
- **Domain**: `actions:Action`  
- **Range**: `xsd:string`
- **Values**: `"Mon"`, `"Tue"`, `"Wed"`, `"Thu"`, `"Fri"`, `"Sat"`, `"Sun"`
- **Description**: Days of week for weekly/monthly/yearly recurrence

##### `actions:byMonth`
- **Type**: `owl:DatatypeProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:string`  
- **Values**: `"Jan"`, `"Feb"`, `"Mar"`, `"Apr"`, `"May"`, `"Jun"`, `"Jul"`, `"Aug"`, `"Sep"`, `"Oct"`, `"Nov"`, `"Dec"`
- **Description**: Months for yearly recurrence

##### `actions:byMonthDay`
- **Type**: `owl:DatatypeProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:integer` (1-31, negative values allowed)
- **Description**: Days of month for monthly/yearly recurrence
- **Note**: Negative values count from end of month (-1 = last day)

##### `actions:byHour`
- **Type**: `owl:DatatypeProperty`
- **Domain**: `actions:Action`
- **Range**: `xsd:integer` (0-23)
- **Description**: Hours for daily/weekly/monthly/yearly recurrence

##### `actions:byMinute`
- **Type**: `owl:DatatypeProperty` 
- **Domain**: `actions:Action`
- **Range**: `xsd:integer` (0-59)
- **Description**: Minutes for hourly/daily/weekly/monthly/yearly recurrence

## Derived Classes (Query Convenience)

### `actions:CompletedAction`
**Description**: Actions that have been completed  
**Definition**: `actions:Action ⊓ ∃actions:state.{actions:Completed}`

### `actions:RecurringAction`  
**Description**: Actions with recurrence patterns
**Definition**: `actions:Action ⊓ ∃actions:recurrenceFrequency.xsd:string`

### `actions:ProjectAction`
**Description**: Root actions belonging to a specific project  
**Definition**: `actions:RootAction ⊓ ∃actions:project.xsd:string`

## SHACL Validation Rules

The accompanying `actions-shapes.ttl` enforces critical constraints:

### Hierarchical Constraints
- Maximum 6 levels of nesting (depths 0-5)
- Proper parent-child relationships
- Project assignments only on root actions
- Depth consistency validation

### State Management
- Exactly one state per action
- Valid state transitions (implementation dependent)

### Temporal Logic
- Completion dates cannot precede do dates
- Duration constraints (1 minute to 7 days)
- Recurrence termination exclusivity

### Data Integrity  
- Priority values within valid range (1-4)
- UUID format validation
- Context format recommendations

## Usage Examples

### Basic Action
```turtle
:action1 a actions:RootAction ;
    schema:name "Review quarterly reports" ;
    actions:state actions:NotStarted ;
    actions:priority 2 ;
    actions:context "@office" ;
    actions:doDate "2025-01-25"^^xsd:date .
```

### Hierarchical Structure
```turtle  
:project_task a actions:RootAction ;
    schema:name "Launch new product" ;
    actions:project "Product Development" ;
    actions:state actions:InProgress .

:subtask1 a actions:ChildAction ;
    schema:name "Finalize specifications" ;
    actions:parentAction :project_task ;
    actions:state actions:Completed .

:subtask2 a actions:LeafAction ;
    schema:name "Update documentation" ;
    actions:parentAction :subtask1 ;
    actions:state actions:NotStarted .
```

### Recurring Action
```turtle
:weekly_standup a actions:RootAction ;
    schema:name "Team standup meeting" ;
    actions:doTime "09:00:00"^^xsd:time ;
    actions:durationMinutes 30 ;
    actions:recurrenceFrequency "WEEKLY" ;
    actions:byDay "Mon" ;
    actions:context "@office" .
```

## Integration Guidelines

### For Application Developers
1. **Import the vocabulary** into your application's ontology
2. **Use SHACL validation** to ensure data integrity  
3. **Leverage derived classes** for efficient querying
4. **Extend carefully** using `rdfs:subPropertyOf` for custom properties

### For Data Exchange
1. **Include namespace declarations** in RDF serializations
2. **Validate against SHACL shapes** before data exchange
3. **Use Schema.org equivalencies** for broader compatibility
4. **Document extensions** when adding domain-specific properties

### For Search & Discovery
1. **Utilize Schema.org mappings** for search engine optimization
2. **Implement structured data** using JSON-LD serialization
3. **Support common vocabularies** like FOAF for person references
4. **Enable federation** through stable URIs and CORS headers

## Future Extensions

The vocabulary is designed for extension while maintaining backward compatibility:

- **Resource Management**: Equipment, materials, cost tracking
- **Collaboration**: Assignment, delegation, approval workflows  
- **Analytics**: Performance metrics, time tracking, reporting
- **Integration**: Calendar sync, notification systems, API bindings

## Standards Compliance

- **OWL 2**: Full compliance for reasoning and inference
- **SHACL**: Constraint validation and data quality assurance
- **Schema.org**: Property alignment and search optimization  
- **iCalendar**: Recurrence pattern compatibility (RFC 5545)
- **UUID v7**: Modern identifier standard for temporal ordering
- **ISO 8601**: Date, time, and duration formatting

## References

1. [Schema.org Action](http://schema.org/Action)
2. [Getting Things Done Methodology](https://gettingthingsdone.com/)  
3. [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/)
4. [SHACL Constraint Language](https://www.w3.org/TR/shacl/)
5. [iCalendar Specification (RFC 5545)](https://datatracker.ietf.org/doc/html/rfc5545)
6. [UUID Version 7 Specification](https://tools.ietf.org/html/draft-peabody-dispatch-new-uuid-format)
7. [Eisenhower Decision Matrix](https://en.wikipedia.org/wiki/Time_management#The_Eisenhower_Method)
