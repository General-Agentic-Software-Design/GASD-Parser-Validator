# User Story — Enforce INVARIANT Scope Ordering

**Story ID:** US-PARSER-012
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Language Architect**,
I want the `INVARIANT` keyword to **always precede** the scope qualifier (`LOCAL` or `GLOBAL`),
So that the language grammar remains consistent and follows a predictable "Keyword-then-Qualifier" pattern, reducing syntactic ambiguity and ensuring alignment with the normative specification.

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-012-01 | The parser MUST accept `INVARIANT GLOBAL:` and `INVARIANT LOCAL:` as valid syntactic constructs.       |
| AC-PARSER-012-02 | The parser MUST REJECT `GLOBAL INVARIANT:` and `LOCAL INVARIANT:` with a clear `SyntaxError`.          |
| AC-PARSER-012-03 | The error message for the invalid order SHOULD suggest the correct `INVARIANT <SCOPE>` pattern.         |
| AC-PARSER-012-04 | This ordering enforcement MUST be applied globally across all versions supported by the parser.         |

---

### Acceptance Tests

| Test ID          | Description                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| AT-PARSER-012-01 | Run `gasd_parser` on a file containing `INVARIANT GLOBAL: "..."` and verify it passes. |
| AT-PARSER-012-02 | Run `gasd_parser` on a file containing `GLOBAL INVARIANT: "..."` and verify it triggers a `SyntaxError`. |
| AT-PARSER-012-03 | Verify that the error output provides a helpful hint about the mandatory keyword order. |

---

### Regression Tests

| Test ID          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| RT-PARSER-012-01 | Ensure that all existing 1.2 examples (e.g., `smart_grid_load_balancer.gasd`) that already follow this pattern continue to pass. |
| RT-PARSER-012-02 | Identify and update any legacy files or tests that might use the reversed order (e.g., `user_registration.gasd`). |

---

### Requirements Traceability Matrix

| Requirement | User Story | Acceptance Test | Regression Test |
| :--- | :--- | :--- | :--- |
| REQ-012 Invariant Order Enforcment | US-PARSER-012 | AT-PARSER-012-01, AT-PARSER-012-02, AT-PARSER-012-03 | RT-PARSER-012-01, RT-PARSER-012-02 |
