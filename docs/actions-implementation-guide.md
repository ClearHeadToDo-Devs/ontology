# Actions Implementation Guide
**Version:** 2.1.0  
**Semantic Vocabulary:** [Actions Vocabulary](https://vocab.example.org/actions/)  
**File Format:** [Actions File Format](actions-fileformat-spec.md)

## Overview

This guide helps developers implement tools that work with the Actions ecosystem by providing:

1. **Mapping tables** between file syntax and RDF vocabulary
2. **Parsing guidelines** for building compliant parsers  
3. **RDF generation examples** for semantic web integration
4. **Interoperability patterns** for tool ecosystems

## File Format to RDF Mapping

### Core Action Structure

| File Syntax | RDF Triple Pattern | Notes |
|-------------|-------------------|-------|
| `[ ] Task name` | `?action a actions:Action ; schema:name "Task name" ; actions:state actions:NotStarted ; actions:depth 1` | Root action |
| `> [ ] Child task` | `?child a actions:Action ; schema:name "Child task" ; actions:state actions:NotStarted ; actions:depth 2 ; actions:parentAction ?parent` | Child relationship |

### State Mappings

| File Syntax | RDF Property | RDF Value | Schema.org Equivalent |
|-------------|-------------|-----------|----------------------|
| `[ ]` | `actions:state` | `actions:NotStarted` | `schema:PotentialActionStatus` |
| `[x]` | `actions:state` | `actions:Completed` | `schema:CompletedActionStatus` |
| `[-]` | `actions:state` | `actions:InProgress` | `schema:ActiveActionStatus` |
| `[=]` | `actions:state` | `actions:Blocked` | *(extension)* |
| `[_]` | `actions:state` | `actions:Cancelled` | *(extension)* |

### Property Mappings

| File Syntax | RDF Property | RDF Value Type | Schema.org Relation |
|-------------|-------------|----------------|-------------------|
| `!1` | `actions:priority` | `xsd:positiveInteger` | *(extension)* |
| `*Project` | `actions:project` | `xsd:string` | *(extension)* |
| `+context` | `actions:context` | `xsd:string` | `rdfs:subPropertyOf schema:location` |
| `$description` | `schema:description` | `xsd:string` | `schema:description` |
| `@2025-01-20` | `actions:doDate` | `xsd:date` | `rdfs:subPropertyOf schema:startTime` |
| `@14:30` | `actions:doTime` | `xsd:time` | `rdfs:subPropertyOf schema:startTime` |
| `@2025-01-20T14:30` | `actions:doDateTime` | `xsd:dateTime` | `rdfs:subPropertyOf schema:startTime` |
| `D30` | `actions:durationMinutes` | `xsd:positiveInteger` | *(extension)* |
| `%2025-01-20T16:45` | `actions:completedDateTime` | `xsd:dateTime` | `rdfs:subPropertyOf schema:endTime` |
| `#uuid` | `schema:identifier` | `xsd:string` | `schema:identifier` |

### Hierarchy Mappings

| File Depth | RDF Class | RDF Property |
|------------|-----------|--------------|
| *(root)* | `actions:RootAction` | `actions:depth "1"^^xsd:positiveInteger` |
| `>` | `actions:ChildAction` | `actions:depth "2"^^xsd:positiveInteger ; actions:parentAction ?parent` |
| `>>` | `actions:ChildAction` | `actions:depth "3"^^xsd:positiveInteger ; actions:parentAction ?parent` |
| `>>>` | `actions:ChildAction` | `actions:depth "4"^^xsd:positiveInteger ; actions:parentAction ?parent` |
| `>>>>` | `actions:ChildAction` | `actions:depth "5"^^xsd:positiveInteger ; actions:parentAction ?parent` |
| `>>>>>` | `actions:ChildAction` | `actions:depth "6"^^xsd:positiveInteger ; actions:parentAction ?parent` |

## Implementation Examples

### Parsing to RDF (Turtle)

#### Input File:
```
[x] Complete project proposal *Q1 Planning +computer,office @2025-01-15T14:00D120 %2025-01-15T16:15
> [ ] Research requirements +research,computer  
> [ ] Draft proposal +writing,computer
```

#### Generated RDF:
```turtle
@prefix actions: <https://vocab.example.org/actions/> .
@prefix schema: <http://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:action1 a actions:RootAction, actions:CompletedAction ;
    schema:name "Complete project proposal" ;
    actions:state actions:Completed ;
    actions:depth 1 ;
    actions:project "Q1 Planning" ;
    actions:context "computer", "office" ;
    actions:doDateTime "2025-01-15T14:00:00"^^xsd:dateTime ;
    actions:durationMinutes 120 ;
    actions:completedDateTime "2025-01-15T16:15:00"^^xsd:dateTime ;
    actions:childAction :action2, :action3 .

:action2 a actions:ChildAction ;
    schema:name "Research requirements" ;
    actions:state actions:NotStarted ;
    actions:depth 2 ;
    actions:context "research", "computer" ;
    actions:parentAction :action1 .

:action3 a actions:ChildAction ;
    schema:name "Draft proposal" ;
    actions:state actions:NotStarted ;
    actions:depth 2 ;
    actions:context "writing", "computer" ;
    actions:parentAction :action1 .
```

### JSON-LD Output

```json
{
  "@context": {
    "actions": "https://vocab.example.org/actions/",
    "schema": "http://schema.org/"
  },
  "@graph": [
    {
      "@type": ["actions:RootAction", "actions:CompletedAction", "schema:Action"],
      "schema:name": "Complete project proposal",
      "actions:state": {"@id": "actions:Completed"},
      "actions:depth": 1,
      "actions:project": "Q1 Planning",
      "actions:context": ["computer", "office"],
      "actions:doDateTime": "2025-01-15T14:00:00",
      "actions:durationMinutes": 120,
      "actions:completedDateTime": "2025-01-15T16:15:00",
      "actions:childAction": [
        {"@id": "_:action2"},
        {"@id": "_:action3"}
      ]
    },
    {
      "@id": "_:action2",
      "@type": ["actions:ChildAction", "schema:Action"],
      "schema:name": "Research requirements",
      "actions:state": {"@id": "actions:NotStarted"},
      "actions:depth": 2,
      "actions:context": ["research", "computer"],
      "actions:parentAction": {"@id": "_:action1"}
    }
  ]
}
```

## Parsing Guidelines

### 1. Tokenization Strategy

```javascript
// Pseudo-code for parsing core properties
function parseAction(line) {
  const action = {};
  let remaining = line.trim();
  
  // Extract depth
  const depthMatch = remaining.match(/^(>*)/);
  action.depth = depthMatch[1].length + 1;
  remaining = remaining.slice(depthMatch[1].length);
  
  // Extract state
  const stateMatch = remaining.match(/^\[(.)\]/);
  action.state = stateSymbolToState(stateMatch[1]);
  remaining = remaining.slice(stateMatch[0].length).trim();
  
  // Extract name and properties
  const { name, properties } = parseNameAndProperties(remaining);
  action.name = name;
  Object.assign(action, properties);
  
  return action;
}
```

### 2. Property Extraction

```javascript
function parseNameAndProperties(text) {
  const properties = {};
  let name = text;
  
  // Extract properties (order independent)
  const patterns = [
    { regex: /\$([^$!*+@%>#]+)/, prop: 'description' },
    { regex: /!([1-4])/, prop: 'priority', type: 'int' },
    { regex: /\*([^$!*+@%>#]+)/, prop: 'project' },
    { regex: /\+([^$!*+@%>#,]+(?:,[^$!*+@%>#,]+)*)/, prop: 'context', multi: true },
    { regex: /@([0-9T:\-]+(?:D[0-9]+)?(?:R[A-Za-z0-9,]+)?)/, prop: 'doDateTime' },
    { regex: /%([0-9T:\-]+)/, prop: 'completedDateTime' },
    { regex: /#([0-9a-f\-]+)/, prop: 'identifier' }
  ];
  
  patterns.forEach(({ regex, prop, type, multi }) => {
    const match = text.match(regex);
    if (match) {
      let value = match[1];
      if (type === 'int') value = parseInt(value);
      if (multi && value.includes(',')) value = value.split(',');
      properties[prop] = value;
      name = name.replace(match[0], '').trim();
    }
  });
  
  return { name, properties };
}
```

### 3. Hierarchy Building

```javascript
function buildHierarchy(actions) {
  const stack = [];
  const roots = [];
  
  actions.forEach(action => {
    // Pop stack until we find parent level
    while (stack.length >= action.depth) {
      stack.pop();
    }
    
    if (stack.length > 0) {
      const parent = stack[stack.length - 1];
      parent.children = parent.children || [];
      parent.children.push(action);
      action.parentAction = parent;
    } else {
      roots.push(action);
    }
    
    stack.push(action);
  });
  
  return roots;
}
```

## RDF Generation Patterns

### Basic Triple Generation

```javascript
function actionToRDF(action, format = 'turtle') {
  const triples = [];
  const actionId = `:action${action.id}`;
  
  // Core triples
  triples.push(`${actionId} a actions:Action, schema:Action`);
  triples.push(`${actionId} schema:name "${escapeString(action.name)}"`);
  triples.push(`${actionId} actions:state actions:${action.state}`);
  triples.push(`${actionId} actions:depth ${action.depth}`);
  
  // Optional properties
  if (action.project) {
    triples.push(`${actionId} actions:project "${escapeString(action.project)}"`);
  }
  
  if (action.context) {
    const contexts = Array.isArray(action.context) ? action.context : [action.context];
    contexts.forEach(ctx => {
      triples.push(`${actionId} actions:context "${escapeString(ctx)}"`);
    });
  }
  
  // Hierarchy
  if (action.parentAction) {
    triples.push(`${actionId} actions:parentAction :action${action.parentAction.id}`);
  }
  
  if (action.children) {
    action.children.forEach(child => {
      triples.push(`${actionId} actions:childAction :action${child.id}`);
    });
  }
  
  return triples.join(' .\n') + ' .';
}
```

## SPARQL Query Examples

### Find All Completed Actions in a Project

```sparql
PREFIX actions: <https://vocab.example.org/actions/>
PREFIX schema: <http://schema.org/>

SELECT ?action ?name ?completedDate WHERE {
  ?action a actions:Action ;
          schema:name ?name ;
          actions:state actions:Completed ;
          actions:project "Website Redesign" ;
          actions:completedDateTime ?completedDate .
} ORDER BY ?completedDate
```

### Find Actions by Context

```sparql
PREFIX actions: <https://vocab.example.org/actions/>
PREFIX schema: <http://schema.org/>

SELECT ?action ?name ?context WHERE {
  ?action a actions:Action ;
          schema:name ?name ;
          actions:context ?context ;
          actions:state actions:NotStarted .
  FILTER(CONTAINS(?context, "computer"))
}
```

### Get Project Hierarchy

```sparql
PREFIX actions: <https://vocab.example.org/actions/>
PREFIX schema: <http://schema.org/>

SELECT ?parent ?parentName ?child ?childName ?depth WHERE {
  ?parent a actions:Action ;
          schema:name ?parentName ;
          actions:project "Q1 Goals" ;
          actions:childAction* ?child .
  ?child schema:name ?childName ;
         actions:depth ?depth .
} ORDER BY ?depth ?parentName ?childName
```

## Interoperability Patterns

### Calendar Integration (iCalendar)

```javascript
function actionToICalEvent(action) {
  if (!action.doDateTime) return null;
  
  const event = {
    summary: action.name,
    dtstart: action.doDateTime,
    status: action.state === 'Completed' ? 'COMPLETED' : 'TENTATIVE'
  };
  
  if (action.durationMinutes) {
    event.dtend = addMinutes(action.doDateTime, action.durationMinutes);
  }
  
  if (action.project) {
    event.categories = [action.project];
  }
  
  if (action.context) {
    event.location = Array.isArray(action.context) 
      ? action.context.join(', ') 
      : action.context;
  }
  
  return event;
}
```

### GTD System Integration

```javascript
function getActionsByContext(actions, context) {
  return actions.filter(action => 
    action.context && 
    (Array.isArray(action.context) ? 
      action.context.includes(context) : 
      action.context === context) &&
    action.state === 'NotStarted'
  );
}

function getNextActions(actions) {
  return actions.filter(action => 
    action.state === 'NotStarted' &&
    (!action.children || action.children.length === 0)
  );
}
```

### Project Management Export

```javascript
function toProjectStructure(rootActions) {
  return rootActions.map(root => ({
    name: root.name,
    project: root.project,
    status: calculateProjectStatus(root),
    progress: calculateProgress(root),
    tasks: flattenHierarchy(root),
    contexts: getUniqueContexts(root),
    timeline: calculateTimeline(root)
  }));
}
```

## Validation and Compliance

### Schema Validation

Use SHACL shapes to validate RDF output:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix actions: <https://vocab.example.org/actions/> .

actions:ActionShape a sh:NodeShape ;
    sh:targetClass actions:Action ;
    sh:property [
        sh:path schema:name ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path actions:state ;
        sh:class actions:ActionState ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] .
```

### File Format Validation

Validate against Tree-sitter grammar or create custom validation rules for common issues:

- Missing state markers
- Invalid depth progression  
- Malformed dates/times
- Invalid priority values (1-4)
- Missing project names for `*` markers

## Best Practices

1. **Preserve source format:** When round-tripping through RDF, maintain original file format preferences
2. **Handle missing properties gracefully:** Not all actions need all properties
3. **Validate UUIDs:** Ensure UUIDv7 format for identifiers when present
4. **Support incremental parsing:** Allow parsing individual actions without full file context
5. **Maintain order:** Preserve action order from source file in RDF generation
6. **Error recovery:** Handle malformed entries by skipping rather than failing entirely

This implementation guide provides the foundation for building tools that work seamlessly with the Actions ecosystem while maintaining semantic web compatibility.
