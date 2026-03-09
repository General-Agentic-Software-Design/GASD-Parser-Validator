# GASD Parser Project — GEP-5 User Stories

This document defines the new user stories for GASD 1.1 based on **GEP-5: Mandatory Explicit VALIDATE AS TYPE Binding**, focusing on deterministic type constraint validation mapping.

## Epic

**EPIC-PARSER-001**
Build a **deterministic parser for the GASD 1.1 specification language** using ANTLR that acts as the **canonical validator and interpreter of GASD 1.1 specification files**.

---

# User Story 8 — Mandatory Explicit VALIDATE AS TYPE Binding

**Story ID:** US-PARSER-008
**Epic:** EPIC-PARSER-001

### User Story

As a **language engineer and GASD author**,
I want the parser to **enforce explicit TYPE binding for the VALIDATE keyword** (e.g., `VALIDATE expr AS TYPE.TypeName`),
So that **the parser can deterministically map validation actions to exactly one type contract, enabling downstream test derivation and runtime guard generation without ambiguity.**

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-008-01 | The parser grammar MUST require the `AS TYPE.typePath` syntax for all `VALIDATE` statements. |
| AC-PARSER-008-02 | The parser MUST reject `VALIDATE expr` statements that lack the explicit binding with a clear syntax error. |
| AC-PARSER-008-03 | The parser MUST correctly parse complex type paths in the binding (e.g., `AS TYPE.User.Address`). |
| AC-PARSER-008-04 | The parse tree generated MUST include the `asBinding` and `typePath` node structure under the `action` node. |
| AC-PARSER-008-05 | The parser MUST resolve the `AS TYPE` binding to a defined `TYPE`; it MUST error if the `TYPE` is nonexistent. |

---

### Acceptance Tests

| Test ID          | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| AT-VALIDATE-001  | `VALIDATE user AS TYPE.User` parses and resolves binding correctly, generating guards for all `@annotations`. |
| AT-VALIDATE-002  | Multi-TYPE FLOW with `VALIDATE order AS TYPE.Order` and `VALIDATE user AS TYPE.User` generates separate guard sets. |
| AT-VALIDATE-003  | Transform-then-validate with `VALIDATE result AS TYPE.ProcessedData` binds correctly. |
| BT-VALIDATE-001  | All `@annotation` types (`@format`, `@range`, `@min_length`, `@max_length`, `@unique`, `@default`) generate guards and derived tests. |

---

### Negative Tests

| Test ID          | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| NT-VALIDATE-001  | `VALIDATE user` (without `AS TYPE...`) produces a clear error. |
| NT-VALIDATE-002  | `VALIDATE user AS TYPE.NonexistentType` produces a clear error. |

---

### Regression Tests

| Test ID          | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| RT-VALIDATE-001  | Upgraded `VALIDATE` statements (with `AS` added) transpile successfully. |
| RT-VALIDATE-002  | Other flow keywords (`ACHIEVE`, `CREATE`, `PERSIST`) remain unaffected by the new `VALIDATE` grammar rule. |

---

# Requirements Traceability Matrix

| Requirement                 | User Story    | Acceptance Test  | Negative/Boundary Test | Regression Test  |
| --------------------------- | ------------- | ---------------- | ---------------------- | ---------------- |
| REQ-010 Explicit VALIDATE Syntax | US-PARSER-008 | AT-VALIDATE-001, AT-VALIDATE-003 | NT-VALIDATE-001        | RT-VALIDATE-001 |
| REQ-011 Semantic Validation      | US-PARSER-008 | AT-VALIDATE-002 | NT-VALIDATE-002        | RT-VALIDATE-002 |
| REQ-012 Guard Generation         | US-PARSER-008 | AT-VALIDATE-001 | BT-VALIDATE-001        | RT-VALIDATE-001 |
