# Plan: Model Functionality in Actions Vocabulary for Interoperability
 Answer: YES, you can and should model functionality

 Based on research into Schema.org Actions, PROV-O, BFO/CCO patterns, and
 OWL-S, functionality CAN be modeled in ontologies without creating
 implementation coupling. The key is using a layered architecture that
 separates:

 1. Domain model (what exists) - Current ontology ✅
 2. Operations (what can be done) - New module 🆕
 3. Validation rules (constraints) - Extended SHACL ➕
 4. Execution history (what happened) - PROV-O integration 🆕

 Recommended Approach: Hybrid Architecture

 Create 4 layers:

 Layer 1: Core Ontology (actions-vocabulary.owl) - Keep as-is

 - No changes needed - stays focused on domain model
 - ActionPlan, ActionProcess, states, properties already defined

 Layer 2: Operations Module (NEW)

 File: actions-operations.owl
 - Define operation types: CRUD, StructuralMutation, StateTransition
 - Use IOPE pattern (Inputs, Outputs, Preconditions, Effects)
 - Operations are capabilities (what CAN be done), not implementations
 - Each operation includes SPARQL queries for validation and execution
 - Examples: UpdatePriorityOp, ReparentOp, SplitActionOp

 Layer 3: Workflow Rules (EXTEND)

 File: actions-workflow-rules.ttl (extend existing SHACL)
 - Auto-transition rules (NotStarted → InProgress when do date arrives)
 - Auto-blocking rules (block when dependencies incomplete)
 - Structural constraints (prevent cycles, depth violations)
 - Precondition validation before operations execute

 Layer 4: Provenance Integration (NEW)

 Import: PROV-O vocabulary
 - Track execution history (what happened, when, by whom)
 - Entity versioning (plan_v1 → plan_v2)
 - Audit trails and time-travel queries
 - Links operations to their executions

 Implementation Phases

 Phase 1 (Foundation): Operations Module
 1. Create actions-operations.owl
 2. Define 5-10 core operations (Create, Read, Update, Delete, Reparent, Split)
 3. Document IOPE pattern for each operation
 4. Add to deployment (include in build-site)

 Phase 2 (Validation): SHACL Workflow Rules
 1. Extend actions-shapes-v3.ttl with workflow rules
 2. Add state transition logic
 3. Add structural mutation constraints
 4. Update tests to verify rules work

 Phase 3 (History): PROV-O Integration
 1. Import PROV-O vocabulary
 2. Document provenance pattern (how to record executions)
 3. Create example queries for audit trails
 4. Add provenance examples to examples/v3/

 Benefits for Interoperability

 ✅ Self-documenting - CLI can discover operations via SPARQL✅
 Technology-agnostic - Any tool can read RDF operations✅ Standardized - Uses
 W3C patterns (OWL-S, PROV-O, SHACL)✅ Validation - Prevents invalid operations
  before execution✅ Audit trails - Complete history of changes✅ Loosely 
 coupled - Core ontology remains stable

 Files to Create/Modify

 New files:
 - actions-operations.owl - Operation definitions
 - actions-workflow-rules.ttl - State transition and validation rules
 - examples/operations/ - Example operation executions
 - docs/OPERATIONS.md - Operations documentation

 Modified files:
 - actions-vocabulary.owl - Add import of PROV-O
 - actions-shapes-v3.ttl - Add workflow validation rules
 - tasks.py - Include operations in build
 - CLAUDE.md - Document operations architecture
 - README.md - Mention operations module

 No changes needed:
 - Core domain classes remain unchanged
 - Existing tests continue to pass
 - Current deployment unaffected until operations added

 Recommendation

 Proceed with Phase 1 - Create operations module with 5-10 core operations.
 This provides immediate value for CLI interoperability without disrupting
 current ontology.

 Keep operations as implementation-independent capability descriptions using
 SPARQL, not code. Different tools (Rust CLI, TypeScript parser, Python
 scripts) can all interpret the same operation definitions.
