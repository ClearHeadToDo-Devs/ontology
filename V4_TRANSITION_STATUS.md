# V4 Transition Status

**Last Updated:** 2025-01-21
**Status:** Minimal Ontology Complete

---

## Summary

The Actions Vocabulary v4 has been implemented as a **minimal CCO extension**. The design uses CCO classes directly and adds only what CCO lacks - lifecycle phase tracking.

- **1 custom class** (ActPhase)
- **2 custom properties** (hasPhase, hasObjective)
- **5 named individuals** (NotStarted, InProgress, Completed, Blocked, Cancelled)
- **Reference-based imports** (self-documenting, no tight coupling)

---

## Design Documents

### 1. Design Specification
- **File:** `ontology/V4_DESIGN.md`
- **Status:** ✅ Complete
- **Key Points:**
  - Uses `cco:Plan` (ont00000974) directly
  - Uses `cco:PlannedAct` (ont00000228) directly
  - Uses `cco:Objective` (ont00000476) directly
  - 1 custom class: `ActPhase`
  - 2 custom properties: `hasPhase`, `hasObjective`

### 2. Design Exploration (Historical)
- **File:** `ontology/V4_DESIGN_EXPLORATION.md`
- **Status:** Archived
- **Contents:** Full exploration of design alternatives and rationale

### 3. Ontology File
- **File:** `ontology/v4/actions-vocabulary.owl`
- **Status:** ✅ Complete
- **Features:**
  - Self-documenting (CCO/BFO classes declared with labels and comments)
  - No owl:imports (reference-based approach)
  - Maps directly to .actions file format states

---

## Implementation Checklist

### Phase 1: Core Ontology ✅
- [x] Design minimal approach (reference CCO, don't wrap)
- [x] Create `ontology/v4/actions-vocabulary.owl`
- [x] Add 1 custom class (ActPhase)
- [x] Add 2 custom properties (hasPhase, hasObjective)
- [x] Add 5 named individuals (phase states)
- [x] Reference CCO/BFO classes with documentation
- [x] Review in Protégé

### Phase 2: Documentation ✅
- [x] Create `V4_DESIGN.md` (concise design doc)
- [x] Archive `V4_DESIGN_EXPLORATION.md` (historical rationale)
- [x] Update this status document

### Phase 3: Integration (Future)
- [x] Create SHACL shapes (if needed for validation)
- [ ] Update parser to emit RDF using v4 vocabulary
- [ ] Update CLAUDE.md with v4 guidance
- [ ] Deploy to production URL

---

## What's in v4

### CCO Classes (by reference)
| Class | IRI | Maps To |
|-------|-----|---------|
| Plan | ont00000974 | Action definitions |
| Planned Act | ont00000228 | Action instances |
| Objective | ont00000476 | Projects/stories |
| Directive ICE | ont00000965 | Parent class (context) |
| Act | ont00000832 | Parent class (context) |

### Custom Extension
| Element | Type | Purpose |
|---------|------|---------|
| ActPhase | Class | Lifecycle states |
| hasPhase | Property | PlannedAct → ActPhase |
| hasObjective | Property | Plan → Objective |

### ActPhase Individuals
| Individual | File Format |
|------------|-------------|
| NotStarted | `[ ]` |
| InProgress | `[-]` |
| Completed | `[x]` |
| Blocked | `[=]` |
| Cancelled | `[_]` |

---

## Files

| File | Purpose |
|------|---------|
| `v4/actions-vocabulary.owl` | The ontology |
| `v4/actions-shapes-v4.ttl` | SHACL validation shapes |
| `V4_DESIGN.md` | Design specification |
| `V4_DESIGN_EXPLORATION.md` | Historical design exploration |
| `V4_TRANSITION_STATUS.md` | This file |

---

## Next Steps

When ready to integrate:
1. Update parser to emit RDF using v4 vocabulary
2. Create SHACL shapes if validation needed
3. Deploy to production URL
4. Update CLAUDE.md

---

**End of Status Document**
