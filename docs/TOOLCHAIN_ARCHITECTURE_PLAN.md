# Actions Ontology Toolchain Architecture Plan

## Executive Summary

This document outlines the architecture decisions, design rationales, and implementation plan for building a complete Actions language toolchain. The pipeline flows from ontology → tree-sitter parser → actions CLI → supporting tooling (LSP server), with each component consuming schema information rather than ontology-specific code generation.

**Core Philosophy**: The ontology serves as the **"small waist"** - a minimal stable interface that enables schema-driven tool generation without tight coupling.

## Architecture Overview

### Information Flow Pipeline
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   Ontology  │───▶│ Tree-sitter  │───▶│ Actions CLI │───▶│ LSP Server  │
│   (.ttl)    │    │ (syntax)     │    │ (semantics) │    │ (editor)    │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
   Schema.json      grammar.js + AST    Validator + Ops    Completions + Diags
```

### Key Design Decisions & Rationales

#### 1. Consumer-Side Generation (NOT Ontology-Generated Artifacts)
**Decision**: Each tool generates its own artifacts from shared schema at build time.

**Why**:
- ✅ **Separation of Concerns**: Ontology focuses on semantics, tools focus on their domain
- ✅ **Loose Coupling**: New tools don't require ontology repo changes
- ✅ **Independent Release Cycles**: Tools can iterate without waiting for upstream changes
- ✅ **Ownership**: Each consumer owns their build process and customizations
- ✅ **Scalability**: No bottleneck at ontology repo for new format support

**Anti-pattern Avoided**: Central artifact generation that creates tight coupling and cross-language build dependencies.

#### 2. Schema Bridge Pattern
**Decision**: Ontology produces simple JSON schema, tools consume it independently.

**Why**:- ✅ **Simple Integration**: JSON schema is universally parseable
- ✅ **Simple Integration**: JSON schema is universally parseable
- ✅ **Tool-Agnostic**: Each tool interprets schema for its specific needs
- ✅ **Shared Source of Truth**: All tools work from same semantic foundation
- ✅ **Clear Information Boundaries**: Syntax vs semantics vs editor UX

#### 3. Hosted Schema Distribution
**Decision**: Host schema at stable URIs, tools fetch at build time.

**Why**:
- ✅ **Version Control**: Tools can pin to specific schema versions
- ✅ **Reliability**: Can cache/vendor schema files for offline builds
- ✅ **Native Toolchain Compatibility**: Works with Rust, JavaScript, etc. without cross-language deps
- ✅ **Network Resilience**: Fallback to cached/bundled versions if host unavailable

#### 4. Shared Test Cases as Data
**Decision**: Distribute test cases as JSON data, tools execute in their own frameworks.

**Why**:
- ✅ **Write Once, Test Everywhere**: Single definition of valid/invalid cases
- ✅ **Consistency**: All tools validate same edge cases and constraints
- ✅ **Native Testing**: Each tool uses its preferred test framework
- ✅ **Tool-Specific Context**: Error messages and behavior remain tool-appropriate

## Implementation Plan

### Phase 1: Schema Generation Infrastructure

#### 1.1 Schema Generation Script
Create `scripts/generate-schema.py` to produce simplified JSON schema from ontology.

**Input**: `actions-vocabulary.ttl` + `actions-shapes.ttl`  
**Output**: `actions-schema.json`

**Schema Structure**:
```json
{
  "version": "1.0.0",
  "generated_from": "ontology@v1.0.0",
  "classes": {
    "Action": {
      "properties": {
        "id": {"type": "uuid", "required": true},
        "name": {"type": "string", "required": true},
        "priority": {"type": "integer", "range": [1, 4]},
        "doDateTime": {"type": "datetime", "required": false}
      },
      "hierarchy": {"parent": "schema:Action"},
      "constraints": [
        {"rule": "doDateTime < dueDateTime", "when": "both present"}
      ]
    }
  },
  "syntax_hints": {
    "extension": ".actions",
    "structure": "hierarchical", 
    "max_depth": 6
  }
}
```

#### 1.2 Test Case Generation
Create `scripts/generate-test-cases.py` to produce comprehensive test cases.

**Output Structure**:
```
test-cases/
├── valid/
│   ├── basic-action.json
│   ├── nested-actions.json
│   └── all-properties.json
├── invalid/
│   ├── missing-name.json
│   ├── invalid-priority.json
│   └── circular-hierarchy.json
└── syntax/
    ├── basic-action.actions
    ├── complex-nesting.actions
    └── edge-cases.actions
```

**Test Case Format**:
```json
{
  "description": "Basic action with required fields only",
  "input": { /* action data */ },
  "expected": {
    "valid": true,
    "errors": []
  },
  "syntax": "action \"Buy groceries\" {\n  priority: 2\n}",
  "tags": ["basic", "required-fields"]
}
```

#### 1.3 Schema Hosting Setup
**Host Location**: `https://schemas.yourproject.com/actions/`

**URL Structure**:
```
/actions/
├── v1.0.0/
│   ├── schema.json
│   ├── test-cases/
│   └── metadata.json
├── v1.1.0/
└── latest/       # Symlink to current
    └── schema.json
```

**Hosting Options**:
- GitHub Pages with custom domain
- S3 + CloudFront 
- Simple static file server

### Phase 2: Tree-sitter Parser

#### 2.1 Repository Structure
```bash
tree-sitter-actions/
├── build.js                   # Schema fetch + grammar generation
├── grammar.js                 # Generated (gitignored)
├── package.json              # npm distribution
├── src/                      # Tree-sitter generated files
├── queries/                  # Syntax highlighting queries
└── test/
    ├── syntax.test.js        # Shared test case execution
    └── corpus/               # Tree-sitter specific tests
```

#### 2.2 Build Process
```javascript
// build.js - Schema to Grammar Generation
const schema = await fetchSchema('https://schemas.yourproject.com/actions/v1.0.0/schema.json');

const grammar = generateGrammar(schema);
// Tree-sitter focuses on SYNTAX only:
// - Block structure from schema.syntax_hints
// - Property names from schema.classes[*].properties 
// - Value patterns from SHACL constraints
// - Hierarchical nesting rules

fs.writeFileSync('grammar.js', grammarCode);
```

**Key Focus**: Tree-sitter handles **parsing and AST generation only**, not semantic validation.

#### 2.3 Generated Grammar Example
```javascript
// Generated grammar.js
module.exports = grammar({
  name: 'actions',
  rules: {
    source_file: $ => repeat($.action_block),
    
    action_block: $ => seq(
      'action',
      $.string_literal,  // action name
      '{',
      repeat($.property),
      optional(repeat($.action_block)), // nested actions
      '}'
    ),
    
    property: $ => choice(
      $.priority_property,  // Generated from schema
      $.context_property,
      $.due_date_property,
      // ... other properties from schema
    ),
    
    priority_property: $ => seq('priority', ':', /[1-4]/),  // From SHACL constraints
    // ... rest generated from schema
  }
});
```

### Phase 3: Actions CLI (Rust)

#### 3.1 Repository Structure
```bash
actions-cli/
├── Cargo.toml
├── build.rs                  # Schema fetch + struct generation
├── src/
│   ├── main.rs
│   ├── parser.rs            # Tree-sitter integration
│   ├── semantic.rs          # Schema-based validation
│   ├── commands/            # CLI subcommands
│   └── generated.rs         # Generated from schema (include!)
└── tests/
    ├── validation.rs        # Shared test case execution
    └── cli_specific.rs      # CLI-only tests
```

#### 3.2 Build-Time Generation
```rust
// build.rs
fn main() {
    // Fetch schema
    let schema_url = "https://schemas.yourproject.com/actions/v1.0.0/schema.json";
    let schema: Value = reqwest::blocking::get(schema_url)?.json()?;
    
    // Generate Rust structs from schema
    let generated_code = generate_rust_structs(&schema);
    
    let out_dir = env::var("OUT_DIR").unwrap();
    fs::write(format!("{}/generated.rs", out_dir), generated_code)?;
}

fn generate_rust_structs(schema: &Value) -> String {
    // Generate structs, enums, validation methods from schema
    // CLI cares about SEMANTICS + file operations
}
```

#### 3.3 CLI Responsibilities
- **File parsing**: Use tree-sitter for syntax → AST
- **Semantic validation**: Use schema + generated structs for validation
- **File operations**: Read, write, transform `.actions` files
- **Business logic**: Task management operations (complete, schedule, etc.)

**Example Usage**:
```bash
actions validate my-tasks.actions       # Parse + validate against schema
actions complete "Buy groceries"        # Mark task complete
actions list --priority 1               # Query tasks by priority
actions add "New task" --context @phone # Add new task
```

### Phase 4: LSP Server

#### 4.1 Repository Structure
```bash
actions-lsp/
├── Cargo.toml
├── build.rs                 # Schema fetch + feature generation
├── src/
│   ├── main.rs
│   ├── completion.rs        # Schema-driven completions
│   ├── diagnostics.rs       # Schema-based validation errors
│   ├── hover.rs             # Schema documentation
│   └── generated.rs         # Generated from schema
└── tests/
    ├── lsp_features.rs      # LSP-specific tests
    └── integration.rs       # Editor integration tests
```

#### 4.2 LSP Feature Generation
```rust
// LSP uses schema for editor features:
impl CompletionProvider {
    pub fn get_completions(&self, position: Position) -> Vec<CompletionItem> {
        let ast = self.parser.parse(&source, None)?;
        let context = self.get_context_at_position(ast, position);
        
        match context {
            CompletionContext::PropertyName => {
                // Generate completions from schema.classes[*].properties
                self.schema_property_completions()
            },
            CompletionContext::PropertyValue(prop) => {
                // Generate values from SHACL constraints
                self.schema_value_completions(prop)
            },
        }
    }
}
```

#### 4.3 LSP Capabilities
- **Completions**: Property names and values from schema
- **Diagnostics**: Real-time validation using schema constraints
- **Hover**: Documentation from schema property descriptions
- **Go to Definition**: Navigate action hierarchy
- **Formatting**: Canonical format from schema syntax hints
- **Symbol Search**: Find actions by name/property

## Repository Organization

### Primary Ontology Repository (This Repo)
```
actions-ontology/
├── ontology/
│   ├── actions-vocabulary.ttl
│   └── actions-shapes.ttl
├── scripts/
│   ├── generate-schema.py       # NEW
│   ├── generate-test-cases.py   # NEW
│   └── publish-schema.py        # NEW
├── docs/
│   ├── ONTOLOGY.md
│   ├── README.md
│   ├── CLAUDE.md
│   └── TOOLCHAIN_ARCHITECTURE_PLAN.md  # This file
├── tests/                       # Current ontology tests
└── artifacts/                   # NEW - Generated schema + test cases
    ├── schema.json
    └── test-cases/
```

### Consumer Repositories (Separate)
- `tree-sitter-actions` - Syntax parsing
- `actions-cli` - Semantic validation + file operations  
- `actions-lsp` - Editor integration
- `actions-web-ui` - Web interface (future)
- `actions-mobile` - Mobile app (future)

## CI/CD Pipeline

### Ontology Repository Pipeline
```yaml
name: Generate and Publish Schema

on:
  push:
    tags: ['v*']

jobs:
  generate-artifacts:
    steps:
      - name: Generate schema from ontology
        run: uv run python scripts/generate-schema.py
        
      - name: Generate test cases
        run: uv run python scripts/generate-test-cases.py
        
      - name: Validate with SHACL
        run: uv run pytest  # Ensures our test cases actually work
        
      - name: Deploy to schema hosting
        run: |
          aws s3 cp artifacts/schema.json s3://schemas.yourproject.com/actions/${{ github.ref_name }}/
          aws s3 cp -r artifacts/test-cases/ s3://schemas.yourproject.com/actions/${{ github.ref_name }}/test-cases/
          # Update latest symlink
          aws s3 cp artifacts/schema.json s3://schemas.yourproject.com/actions/latest/schema.json
```

### Consumer Repository Pipelines
```yaml
# In tree-sitter-actions, actions-cli, actions-lsp repos
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    steps:
      - name: Fetch and generate from schema
        run: |
          # Tool-specific build commands that fetch schema
          npm run prebuild  # tree-sitter
          cargo build       # rust projects
          
      - name: Run shared test cases
        run: |
          # Execute shared test cases in tool's native framework
          npm test          # tree-sitter 
          cargo test        # rust projects
          
      - name: Run tool-specific tests
        run: |
          # Additional tests specific to each tool
```

## Testing Strategy

### Multi-Layer Testing Approach

#### Layer 1: Ontology Tests (Current - This Repo)
- **OWL Reasoning**: Class hierarchy, property domains/ranges
- **SHACL Validation**: Constraint enforcement  
- **Test Case Validation**: Ensure generated test cases work with SHACL
- **Schema Generation**: Verify schema correctly reflects ontology

#### Layer 2: Shared Test Case Execution (Consumer Repos)
- **Validation Consistency**: All tools validate same cases identically
- **Edge Case Coverage**: Comprehensive constraint violation testing
- **Regression Testing**: Prevent behavior drift between tools

#### Layer 3: Tool-Specific Tests (Consumer Repos) 
- **Tree-sitter**: Parsing performance, error recovery, syntax highlighting
- **CLI**: File I/O, command interface, error formatting
- **LSP**: Editor features, completion accuracy, diagnostic quality

### Test Case Categories

#### Valid Cases
- Minimal required properties
- All optional properties
- Hierarchical nesting (all 6 levels)
- Recurrence patterns
- GTD contexts and project assignments

#### Invalid Cases
- Missing required properties (name, priority)
- Invalid property values (priority 0, invalid UUID format)
- Structural violations (leaf with children, wrong depth)
- Temporal inconsistencies (do date after due date)
- Circular references in hierarchy

#### Edge Cases
- Maximum nesting depth
- Unicode in names and descriptions  
- Timezone handling in datetime properties
- Large action hierarchies (performance testing)

## Migration Strategy

### Phase 1: Foundation (Weeks 1-2)
1. ✅ **Current ontology testing working** (Already complete)
2. 🔲 **Implement schema generation script**
3. 🔲 **Implement test case generation**
4. 🔲 **Set up schema hosting**
5. 🔲 **Validate end-to-end: ontology → schema → test cases**

### Phase 2: Tree-sitter (Weeks 3-4)
1. 🔲 **Create tree-sitter-actions repository**
2. 🔲 **Implement schema → grammar generation**
3. 🔲 **Generate working grammar for basic actions**
4. 🔲 **Add shared test case execution**
5. 🔲 **Publish to npm for downstream consumption**

### Phase 3: Actions CLI (Weeks 5-7)
1. 🔲 **Create actions-cli repository**  
2. 🔲 **Implement schema → struct generation**
3. 🔲 **Add tree-sitter integration for parsing**
4. 🔲 **Implement semantic validation using schema**
5. 🔲 **Add basic file operations (validate, list, add)**
6. 🔲 **Execute shared test cases**

### Phase 4: LSP Server (Weeks 8-10)
1. 🔲 **Create actions-lsp repository**
2. 🔲 **Implement basic LSP protocol**
3. 🔲 **Add schema-driven completions**
4. 🔲 **Add real-time diagnostics**
5. 🔲 **Add hover documentation**
6. 🔲 **Test with VS Code/Neovim**

### Phase 5: Integration & Polish (Weeks 11-12)
1. 🔲 **Full pipeline testing: edit → parse → validate → LSP features**
2. 🔲 **Performance optimization**
3. 🔲 **Documentation and usage guides**
4. 🔲 **Package distribution (npm, crates.io)**

## Risk Mitigation

### Technical Risks
- **Schema hosting reliability**: Implement caching/fallback mechanisms
- **Cross-tool compatibility**: Comprehensive shared test suite
- **Performance**: Load testing with large action hierarchies
- **Breaking changes**: Semantic versioning + compatibility testing

### Process Risks
- **Coordination complexity**: Clear ownership boundaries between repos
- **Testing overhead**: Automated CI/CD to reduce manual work
- **Documentation drift**: Single source of truth in ontology repo

## Success Metrics

### Technical Success
- All tools pass shared test cases with 100% consistency
- Schema generation takes <5 seconds
- Tree-sitter parsing handles 10,000+ line files
- CLI validates files in <100ms
- LSP provides completions in <50ms

### Architectural Success
- New tools can be added without ontology repo changes
- Schema changes propagate to all tools automatically
- Each tool can iterate independently
- Clear separation of concerns maintained

## Future Extensions

### Additional Tools
- **Database migrations**: Schema → SQL DDL generation
- **API services**: Schema → OpenAPI specification
- **Documentation sites**: Schema → interactive docs
- **Mobile parsers**: Schema → Swift/Kotlin classes

### Advanced Features
- **Multi-language support**: i18n property names
- **Plugin architecture**: Custom property extensions
- **Real-time sync**: Collaborative editing support
- **Analytics**: Usage tracking and optimization

## Conclusion

This architecture provides a scalable, maintainable approach to building a complete language toolchain from semantic foundations. By using the ontology as a "small waist" interface and distributing schema information rather than generated code, we achieve loose coupling while maintaining consistency across all tools.

The key insight is that **each tool needs different "views" of the same semantic information**, and the schema bridge pattern enables this without creating tight coupling or cross-language dependency issues.

**Next Steps**: Begin Phase 1 implementation with schema generation script and test case generation.
