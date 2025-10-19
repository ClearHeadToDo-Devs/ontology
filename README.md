# Actions Ecosystem

**A semantic web-friendly task management format and vocabulary**

## Overview

The Actions Ecosystem provides a comprehensive solution for task management that bridges human-readable plaintext files with semantic web standards. It consists of:

1. **[Actions Vocabulary](actions-vocabulary.ttl)** - RDF vocabulary extending Schema.org Action
2. **[File Format Specification](actions-fileformat-spec.md)** - Plaintext serialization syntax  
3. **[Implementation Guide](actions-implementation-guide.md)** - Developer integration guidance
4. **[Tree-sitter Parser](https://github.com/your-repo/tree-sitter-actions)** - Grammar implementation

## Quick Start

### Example Actions File

```actions
[x] Plan Q1 marketing campaign $Create comprehensive strategy
    !2 *Product Launch +computer,office @2025-01-15T09:00D120 
    %2025-01-16T11:30 #01234567-89ab-7def-8123-456789abcdef
> [ ] Research competitor campaigns +research,computer  
> [ ] Design campaign assets +design,computer
> [ ] Set up tracking analytics +technical,computer

[ ] Weekly team standup @2025-01-20T09:00D30RWMon,Wed,Fri +meeting *Team Management
```

### Semantic Mapping

The plaintext above maps to RDF triples using the Actions Vocabulary:

```turtle
:action1 a actions:RootAction, actions:CompletedAction ;
    schema:name "Plan Q1 marketing campaign" ;
    schema:description "Create comprehensive strategy" ;
    actions:state actions:Completed ;
    actions:priority 2 ;
    actions:project "Product Launch" ;
    actions:context "computer", "office" ;
    actions:doDateTime "2025-01-15T09:00:00"^^xsd:dateTime ;
    actions:durationMinutes 120 ;
    actions:completedDateTime "2025-01-16T11:30:00"^^xsd:dateTime ;
    schema:identifier "01234567-89ab-7def-8123-456789abcdef" ;
    actions:childAction :action2, :action3, :action4 .
```

## Key Features

### 🏗️ **Semantic Web Citizen**
- Extends Schema.org Action vocabulary
- Full RDF compatibility with SPARQL querying
- Interoperates with semantic web tools and standards

### 📝 **Human-Friendly Format**
- Plain text editing with any text editor
- Minimal syntax optimized for readability
- No special tooling required for basic usage

### 🌳 **Hierarchical Structure**
- Up to 6 levels of nested actions
- Clear parent-child relationships
- Project and story organization

### ⚡ **GTD Integration**
- Context-based action organization (`+phone`, `+computer`)
- Priority levels using Eisenhower Matrix
- Next action identification

### 📅 **Rich Temporal Support**
- ISO 8601 dates and times
- Duration tracking
- iCalendar-compatible recurrence patterns

### 🔧 **Tool Ecosystem Ready**
- Tree-sitter grammar for reliable parsing
- JSON-LD and Turtle RDF serialization
- Calendar app integration
- Project management tool compatibility

## Architecture

### Two-Layer Design

**Layer 1: Semantic Vocabulary** (conceptual model)
```turtle
actions:Action rdfs:subClassOf schema:Action .
actions:project rdf:type owl:DatatypeProperty .
actions:context rdf:type owl:DatatypeProperty .
```

**Layer 2: File Format** (concrete syntax)
```
[x] Task name !1 *Project +context @2025-01-19
```

This separation enables:
- **Vocabulary reuse** across multiple file formats
- **Tool interoperability** via shared semantic model  
- **Format evolution** without breaking semantic compatibility
- **Standards compliance** with semantic web best practices

## Use Cases

### 📋 Personal Task Management
- Individual todo lists with GTD methodology
- Project planning and tracking
- Calendar integration for time blocking

### 👥 Team Collaboration  
- Shared project files in version control
- Cross-tool integration via RDF export
- Standardized task status reporting

### 🔄 Tool Integration
- Import/export between task management systems
- Calendar app synchronization
- Project management dashboard feeding
- Analytics and reporting on task completion

### 🌐 Semantic Web Applications
- Knowledge graph integration
- SPARQL-based task querying and analysis
- Linked data publishing for organizational transparency

## Example Queries

### Find All In-Progress Actions
```sparql
PREFIX actions: <https://vocab.example.org/actions/>
PREFIX schema: <http://schema.org/>

SELECT ?action ?name ?project WHERE {
  ?action a actions:Action ;
          schema:name ?name ;
          actions:state actions:InProgress ;
          actions:project ?project .
}
```

### Get Context-Based Task Lists
```sparql
PREFIX actions: <https://vocab.example.org/actions/>

SELECT ?action ?name WHERE {
  ?action a actions:Action ;
          schema:name ?name ;
          actions:context "computer" ;
          actions:state actions:NotStarted .
}
```

### Project Progress Analysis
```sparql
PREFIX actions: <https://vocab.example.org/actions/>

SELECT ?project (COUNT(?total) as ?totalTasks) (COUNT(?completed) as ?completedTasks) WHERE {
  ?action actions:project ?project .
  
  OPTIONAL { 
    ?completed actions:project ?project ;
               actions:state actions:Completed .
  }
  
  { SELECT ?project (COUNT(?action) as ?total) WHERE {
      ?action actions:project ?project .
    } GROUP BY ?project }
    
} GROUP BY ?project
```

## Getting Started

### For End Users
1. Create a `.actions` file with your task list
2. Use any text editor to manage your actions
3. Leverage tools that support the Actions format for enhanced features

### For Developers
1. Review the [Actions Vocabulary](actions-vocabulary.ttl) specification
2. Study the [File Format Specification](actions-fileformat-spec.md) for syntax details
3. Use the [Implementation Guide](actions-implementation-guide.md) for integration patterns
4. Build on the [Tree-sitter grammar](https://github.com/your-repo/tree-sitter-actions) for parsing

### For Tool Builders
1. Import actions files using the Tree-sitter parser
2. Generate RDF using the vocabulary mapping tables
3. Query with SPARQL for advanced task management features  
4. Export to other formats (JSON-LD, iCalendar, etc.)

## Standards Compliance

### Extends Schema.org
- Compatible with existing Schema.org Action consumers
- Proper `rdfs:subPropertyOf` relationships where applicable
- Maps standard states to Schema.org ActionStatusType

### Follows Semantic Web Best Practices
- Persistent, dereferenceable URIs
- Rich documentation with examples
- Proper use of OWL for class and property definitions
- SPARQL-friendly query patterns

### Integrates with Established Standards
- ISO 8601 for dates and times
- iCalendar recurrence patterns (RFC 5545)
- UUIDv7 for unique identifiers
- GTD methodology for context organization

## Community and Contribution

This project aims to be a good citizen of the semantic web community by:

- **Open Standards**: All specifications are open and documented
- **Interoperability Focus**: Designed to work with existing tools and standards
- **Backwards Compatibility**: File format designed to evolve without breaking changes
- **Community Input**: Welcoming feedback and contributions from users and developers

## License

**MIT License** - Use freely in personal and commercial projects.

## Links

- **Vocabulary Specification**: [actions-vocabulary.ttl](actions-vocabulary.ttl)
- **File Format Specification**: [actions-fileformat-spec.md](actions-fileformat-spec.md)  
- **Implementation Guide**: [actions-implementation-guide.md](actions-implementation-guide.md)
- **Tree-sitter Grammar**: [grammar.js](grammar.js)
- **Schema.org Action**: https://schema.org/Action
- **Getting Things Done**: https://gettingthingsdone.com/

---

*Building bridges between human-readable task management and the semantic web.*
