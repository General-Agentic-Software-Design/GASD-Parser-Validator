# Technical User Story 9 — Command-Line Versioning (Epic 10)

**Story ID:** US-V2-009
**As a** software designer,
**I want** to specify the expected GASD version via a command-line flag,
**So that** I can enforce strict version compliance across multiple files without manual internal directive modification.

## Acceptance Criteria

### 1. Command-Line Interface (CLI)

- **AC-V2-009-01**: Parser supports `--gasd-ver {1.1 | 1.2}` command-line argument.
- **AC-V2-009-02**: If `--gasd-ver` is provided, it acts as the authoritative version; any file-level `VERSION` directive MUST match this value, otherwise a **VERSION_MISMATCH** (LINT-013) error is raised.
- **AC-V2-009-03**: If `--gasd-ver` is NOT provided, the parser MUST default to version `1.2`.
- **AC-V2-009-04**: Files without an internal `VERSION` directive are processed using the version specified by `--gasd-ver` (or the default 1.2).

### 2. Version 1.2 Strict Enforcement (GEP-6 Compliance)

When version 1.2 is active (via flag or directive), the following GEP-6 requirements MUST be strictly enforced:
- **AC-V2-009-05 (Epic 2)**: `ACHIEVE` blocks MUST include a `POSTCONDITION` (LINT-001).
- **AC-V2-009-06 (Epic 3)**: Each `IMPORT` boundary MUST define a corresponding `CONTRACT` (LINT-002).
- **AC-V2-009-07 (Epic 5)**: `INVARIANT` declarations MUST include an explicit `LOCAL` or `GLOBAL` scope (LINT-003).
- **AC-V2-009-08 (Epic 6)**: Every annotation and constraint MUST have a unique `AS` identifier matching `[A-Z][A-Z0-9_]*` (LINT-011).
- **AC-V2-009-09 (Epic 8)**: Environmental annotations (e.g., `@transaction_type`, `@retry`) MUST be paired with explicit `ASSUMPTION` blocks (LINT-005, LINT-012).
- **AC-V2-009-10 (Epic 9)**: The 12-rule GEP-6 Linting Engine (LINT-001 to LINT-012) MUST be fully operational, elevating relevant warnings to errors as specified.

### 3. Backward Compatibility (Version 1.1)

- **AC-V2-009-11**: When version 1.1 is active, new 1.2 constructs (POSTCONDITION, CONTRACT, etc.) are treated as OPTIONAL; their absence produces warnings (or info) rather than errors, except for critical structural rules.

### Comprehensive Acceptance Testing Matrix

| Test ID | Category | Scenario | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **AT-V2-118** | CLI Override | `--gasd-ver 1.1` where file has `VERSION 1.2` | **Error (LINT-013)**: Version Mismatch |
| **AT-V2-119** | CLI Override | `--gasd-ver 1.2` where file has `VERSION 1.1` | **Error (LINT-013)**: Version Mismatch |
| **AT-V2-120** | Defaulting | No flag, file has no `VERSION` | Evaluates as **1.2** (Strict GEP-6 rules applied) |
| **AT-V2-121** | Batch | `--gasd-ver 1.1` on multiple files | All processed with **1.1** legacy semantics |
| **AT-V2-122** | GEP-6 (AC-05) | `--gasd-ver 1.2` on file with `ACHIEVE` (no post) | **Error (LINT-001)**: Missing POSTCONDITION |
| **AT-V2-123** | GEP-6 (AC-06) | `--gasd-ver 1.2` on file with `IMPORT` (no contract) | **Error (LINT-002)**: Missing CONTRACT |
| **AT-V2-124** | GEP-6 (AC-08) | `--gasd-ver 1.2` on file with `@retry` (no AS ID) | **Error (LINT-011)**: Missing AS identifier |

### Requirements Traceability Matrix

| GEP-6 Section | User Story | Acceptance Criteria | Acceptance Test |
| :--- | :--- | :--- | :--- |
| **Epic 10: Version Declaration** | US-V2-009 | AC-V2-009-01 to 04 | AT-V2-118 to AT-V2-121 |
| **Epic 2: ACHIEVE Formalization** | US-V2-009 | AC-V2-009-05 | AT-V2-122 |
| **Epic 3: Contract Modeling** | US-V2-009 | AC-V2-009-06 | AT-V2-123 |
| **Epic 6: ID Identification** | US-V2-009 | AC-V2-009-08 | AT-V2-124 |
| **Epic 9: Linting Engine** | US-V2-009 | AC-V2-009-10 | AT-V2-122 to AT-V2-124 |
