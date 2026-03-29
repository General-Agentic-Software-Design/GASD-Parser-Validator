# GASD Parser & Validator v2.0 — Exhaustive Traceable User Stories

This document defines the formal requirements for **GASD-Parser-Validator v2.0**, based on **GEP-6: GASD 1.2 — Formal Semantics, Contract Modeling, and Verification Support**. This version transforms GASD from a structural documentation format into a verifiable specification language through formal semantics and strict validation.

---

## References

- **GASD 1.1 Specification**: [GASD_Specification-1.1.md](../../../GASD/GASD-1.1/GASD_Specification-1.1.md)
- **GASD 1.1 Self-Definition**: [gasd-1.1.0.gasd](../../../GASD/GASD-1.1/gasd-1.1.0.gasd)
- **GASD 1.2 Specification**: [GASD_Specification.md](../../../GASD/GASD-1.2/GASD_Specification.md)
- **GASD 1.2 Self-Definition**: [gasd-1.2.0.gasd](../../../GASD/GASD-1.2/gasd-1.2.0.gasd)
- **Source Proposal**: [GEP-6: GASD 1.2 — Formal Semantics, Contract Modeling, and Verification Support](./GEP-6:%20GASD%201.2%20%E2%80%94%20Formal%20Semantics,%20Contract%20Modeling,%20and%20Verification%20Support)

---

## Epic Goals

1. **Formalize Annotations**: Implement semantic triples `(structural_predicate, runtime_contract, environmental_dependency)` for all standard annotations.
2. **Decidable Achievements**: Transform `ACHIEVE` into a verifiable construct via `POSTCONDITION`.
3. **Behavioral Contracts**: Enable `CONTRACT` definitions for cross-component boundaries with provider/consumer agreement.
4. **Dependency Precision**: Support explicit `DEPENDS_ON` and inferred step dependencies (variable/sequential).
5. **Scoped Invariants**: Distinguish between `LOCAL` and `GLOBAL` invariants; GLOBAL requiring explicit enforcement identification.
6. **Unique Identification**: Require `AS identifier` for all obligations (regex: `[A-Z][A-Z0-9_]*`).
7. **External Verification**: Integrate with external formal models (TLA+, Alloy, Spin, Promela).
8. **Assumption Tracking**: Force explicit declaration of environmental dependencies via `ASSUMPTION` blocks.
9. **Strict Validation**: Implement the 12-rule Linting Engine defined in GEP-6.
10. **Backward Compatibility**: Ensure all GASD 1.1 files remain valid (signature-only, auto-IDs, sequential inference).

---

## Technical User Story 1 — Versioning & Directive Compliance (Epic 10)

**Story ID:** US-V2-001
**As a** language engineer,
**I want** the parser to enforce version-specific rules based on the `VERSION` directive,
**So that** existing 1.1 files remain valid while new 1.2 files adhere to strict formal requirements.

### Acceptance Criteria

- **AC-V2-001-01**: Parser recognizes `VERSION version_number` as the first directive (preceding CONTEXT/TARGET).
- **AC-V2-001-02**: Files declaring `VERSION 1.2` MUST use all new REQUIRED constructs (POSTCONDITION, CONTRACT, AS ID, etc.).
- **AC-V2-001-03**: Files without `VERSION` or declaring `VERSION 1.1` are processed with legacy semantics.
- **AC-V2-001-04**: New 1.2 constructs in a 1.1 file SHALL produce a **lint warning**, not a parse error.

---

## Technical User Story 2 — Annotation Semantic Registry (Epic 1)

**Story ID:** US-V2-002
**As a** verification agent,
**I want** every standard annotation to decompose into a `(structural_predicate, runtime_contract, environmental_dependency)` triple,
**So that** I can deterministically verify each dimension of a constraint.

### Acceptance Criteria

- **AC-V2-002-01**: A centralized **Annotation Semantic Registry** is implemented (§1.2).
- **AC-V2-002-02**: Registry MUST support all 21 standard annotations (§1.1):
  - **Data**: `@range`, `@min_length`, `@max_length`, `@format`, `@unique`, `@default`, `@constraint`.
  - **Architectural**: `@injectable`, `@mockable`, `@transaction_type(ACID)`, `@transaction_type(SAGA)`.
  - **Implementation**: `@async`, `@retry(n)`, `@timeout(ms)`, `@external`, `@hash(algo)`, `@circuit_breaker`, `@cacheable(ttl)`, `@idempotent`.
  - **Extended**: `@sensitive`, `@authorized(role)`.
- **AC-V2-002-03**: Registry lookup yields `VERIFICATION` types: `AST_PATTERN_MATCH`, `PROPERTY_BASED_TEST`, or `ASSUMPTION_STATEMENT`.

---

## Technical User Story 3 — ACHIEVE & Outcome Verification (Epic 2)

**Story ID:** US-V2-003
**As a** specification author,
**I want** to specify `POSTCONDITION` blocks for `ACHIEVE` actions,
**So that** liveness properties are transformed into testable assertions.

### Acceptance Criteria

- **AC-V2-003-01**: Support `POSTCONDITION` block inside `ACHIEVE` body.
- **AC-V2-003-02**: Support operators: `IS`, `==`, `!=`, `>`, `<`, `>=`, `<=`.
- **AC-V2-003-03**: Support `TIMEOUT` with duration literals (e.g., `3000ms`, `5s`).
- **AC-V2-003-04**: **LINT-001**: ACHIEVE without POSTCONDITION in 1.2 is an **ERROR**.

---

## Technical User Story 4 — Contract Modeling (Epic 3)

**Story ID:** US-V2-004
**As a** technical architect,
**I want** to define formal `CONTRACT` blocks for component interfaces,
**So that** cross-component behavioral expectations are mechanically synchronized.

### Acceptance Criteria

- **AC-V2-004-01**: Support `CONTRACT qualified_name` with `INPUT`, `OUTPUT`, and `BEHAVIORS`.
- **AC-V2-004-02**: `CASE` clauses support `POSTCONDITION`, `THROWS`, and `AFTER` (duration or retry).
- **AC-V2-004-03**: **LINT-002**: Every `IMPORT` in 1.2 MUST have a corresponding `CONTRACT` (Error).
- **AC-V2-004-04**: **LINT-007**: Every `CASE` MUST specify either `THROWS` or `POSTCONDITION` (Error).
- **AC-V2-004-05**: Contracts SHALL generate a stable hash; provider and consumer MUST compile against the same hash.

---

## Technical User Story 5 — Dependency Semantics (Epic 4)

**Story ID:** US-V2-005
**As a** developer,
**I want** to explicitly override inferred step dependencies using `DEPENDS_ON`,
**So that** complex or non-linear execution flows are accurately represented.

### Acceptance Criteria

- **AC-V2-005-01**: Support `DEPENDS_ON STEP n` clause in flow steps to override inference.
- **AC-V2-005-02**: **LINT-008**: Error if `DEPENDS_ON` references a non-existent step.
- **AC-V2-005-03**: **LINT-009**: Error if circular dependencies are detected.
- **AC-V2-005-04**: In `VERSION 1.2`, steps whose dependencies cannot be unambiguously inferred MUST use explicit `DEPENDS_ON`.

---

## Technical User Story 6 — Scoped Invariants & External Models (Epic 5 & 7)

**Story ID:** US-V2-006
**As a** formal verifier,
**I want** to distinguish between `LOCAL` and `GLOBAL` invariants and link them to `MODEL` blocks,
**So that** high-risk distributed properties are backed by formal verification results (TLA+, etc.).

### Acceptance Criteria

- **AC-V2-006-01**: `INVARIANT` blocks require `LOCAL` or `GLOBAL` scope in 1.2.
- **AC-V2-006-02**: Support `MODEL` block with `TYPE` (TLA+, Alloy, Spin, Promela), `FILE`, `VERIFIES`, and `ASSUMPTIONS`.
- **AC-V2-006-03**: **LINT-003**: Invariant without scope in 1.2 is an ERROR.
- **AC-V2-006-04**: **LINT-006**: GLOBAL INVARIANT with only application-level enforcement (lacking DB/Model) is an ERROR.
- **AC-V2-006-05**: GLOBAL invariants MUST include a GASD-level comment identifying all enforcement points.
- **AC-V2-006-06**: Analyzers MUST validate that the `MODEL` `FILE` path exists; error if missing in 1.2.

---

## Technical User Story 7 — Obligation Identification (Epic 6)

**Story ID:** US-V2-007
**As a** traceability engineer,
**I want** every annotation and constraint to have a stable `AS` identifier,
**So that** verification reports and requirements matrices remain stable across refactors.

### Acceptance Criteria

- **AC-V2-007-01**: Support `AS IDENTIFIER` syntax for all annotations and constraints.
- **AC-V2-007-02**: Identifiers MUST match `[A-Z][A-Z0-9_]*`.
- **AC-V2-007-03**: **LINT-011**: Missing `AS` in 1.2 is an ERROR.
- **AC-V2-007-04**: In 1.1, missing IDs are auto-generated using deterministic logic (e.g., `PO-TYPE-FIELD-ANNOTATION`).
- **AC-V2-007-05**: **LINT-010**: Error if author-assigned identifiers collide within file scope.

---

## Technical User Story 8 — Assumption & Warning System (Epic 8)

**Story ID:** US-V2-008
**As a** risk manager,
**I want** explicit `ASSUMPTION` blocks for all environmental dependencies,
**So that** the limits of the specification's guarantees are visible.

### Acceptance Criteria

- **AC-V2-008-01**: Support `ASSUMPTION` block with `AFFECTS` and `CONSEQUENCE` clauses.
- **AC-V2-008-02**: **LINT-005**: `@transaction_type` without `ASSUMPTION` is an ERROR in 1.2.
- **AC-V2-008-03**: **LINT-012**: Any annotation with an environmental dependency lacking an `ASSUMPTION` is an ERROR in 1.2.
- **AC-V2-008-04**: **LINT-004**: `@retry` without `@idempotent` (or documentation) is an ERROR in 1.2.

---

## Comprehensive Acceptance Testing Matrix

| Test ID | Category | Requirement Detail | Expected Result (1.2 / 1.1) |
| :--- | :--- | :--- | :--- |
| **AT-V2-101** | Version | `VERSION 1.2` at top | Parses / N/A |
| **AT-V2-102** | ACHIEVE | `ACHIEVE "..."` (no post) | **Error (LINT-001)** / Warning |
| **AT-V2-103** | ACHIEVE | `ACHIEVE "..." : POSTCONDITION: result IS UUID` | Pass / Pass (with Migration Warning) |
| **AT-V2-104** | CONTRACT | `IMPORT "a.gasd"` (no contract) | **Error (LINT-002)** / Warning |
| **AT-V2-105** | CONTRACT | `CONTRACT Case: BEHAVIORS: CASE x: POSTCONDITION: y` | Pass / Pass (Migration Warning) |
| **AT-V2-106** | CONTRACT | `CASE x:` (missing THROWS/POST) | **Error (LINT-007)** / **Error** |
| **AT-V2-107** | FLOW | `1. ACHIEVE ... DEPENDS_ON STEP 5` (non-existent) | **Error (LINT-008)** / **Error** |
| **AT-V2-108** | FLOW | `1. A DEPENDS ON 2; 2. B DEPENDS ON 1` | **Error (LINT-009)** / **Error** |
| **AT-V2-109** | INVARIANT | `INVARIANT: "..."` (no scope) | **Error (LINT-003)** / Info |
| **AT-V2-110** | INVARIANT | `INVARIANT GLOBAL: "..."` (no MODEL/DB) | **Error (LINT-006)** / Warning |
| **AT-V2-111** | ID | `@retry(3)` (no AS ID) | **Error (LINT-011)** / Pass (Auto-ID) |
| **AT-V2-112** | ID | `@retry(3) AS lower_case_id` | **Error (Regex Match)** / **Error** |
| **AT-V2-113** | ID | `AS ID1` repeated twice | **Error (LINT-010)** / **Error** |
| **AT-V2-114** | ASSUME | `@transaction_type(ACID)` (no ASSUMPTION) | **Error (LINT-005)** / Warning |
| **AT-V2-115** | ASSUME | `@retry(3)` (no @idempotent) | **Error (LINT-004)** / Warning |
| **AT-V2-116** | MODEL | `TYPE: "TLA+" FILE: "missing.tla"` | **Error (Path missing)** / Warning |
| **AT-V2-117** | SEMANTIC | Semantic Registry lookup for `@circuit_breaker` | Returns Triple: (Breaker wrapper, FSM states, None) |

---

## Regression & Compatibility Matrix (v1.1)

| Test ID | Feature | Rule | Expected Output |
| :--- | :--- | :--- | :--- |
| **RT-V2-201** | Directive | Missing `VERSION` | Treated as 1.1; no new-feature errors |
| **RT-V2-202** | ACHIEVE | Standard 1.1 `ACHIEVE "..."` | Parses successfully (Warning emitted) |
| **RT-V2-203** | INVARIANT | Standard 1.1 `INVARIANT: "..."` | Defaults to `LOCAL` |
| **RT-V2-204** | ID | 1.1 Annotation without `AS` | Auto-ID generated: `PO-TYPE-FIELD-ANNOTATION` |
| **RT-V2-205** | Grammar | 1.1 productions | Verbatim match to GASD 1.1 EBNF |

---

## Requirements Traceability Matrix (Full GEP-6 Mapping)

| GEP-6 Section | User Story | Acceptance Criteria | Acceptance Test |
| :--- | :--- | :--- | :--- |
| **Epic 1: Semantic Triples** | US-V2-002 | AC-V2-002-01 to 03 | AT-V2-117 |
| **Epic 2: ACHIEVE Formalization** | US-V2-003 | AC-V2-003-01 to 04 | AT-V2-102, AT-V2-103 |
| **Epic 3: Contract Modeling** | US-V2-004 | AC-V2-004-01 to 05 | AT-V2-104 to AT-V2-106 |
| **Epic 4: Dependency Semantics** | US-V2-005 | AC-V2-005-01 to 04 | AT-V2-107, AT-V2-108 |
| **Epic 5: Invariant Scoping** | US-V2-006 | AC-V2-006-01, 03, 05 | AT-V2-109 |
| **Epic 6: Obligation Identification** | US-V2-007 | AC-V2-007-01 to 05 | AT-V2-111 to AT-V2-113 |
| **Epic 7: External Model Integration** | US-V2-006 | AC-V2-006-02, 04, 06 | AT-V2-110, AT-V2-116 |
| **Epic 8: Assumption System** | US-V2-008 | AC-V2-008-01 to 04 | AT-V2-114, AT-V2-115 |
| **Epic 9: Linting Engine** | All | LINT Rule Integration | AT-V2-102 to AT-V2-116 |
| **Epic 10: Version Declaration** | US-V2-001 | AC-V2-001-01 to 04 | AT-V2-101 |
| **Backward Compatibility** | All | Compatibility fallback logic | RT-V2-201 to RT-V2-205 |
