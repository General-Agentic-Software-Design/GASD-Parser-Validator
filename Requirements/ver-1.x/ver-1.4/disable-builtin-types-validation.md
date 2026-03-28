# GASD CLI Options — Traceable User Stories

## Epic

**EPIC-CLI-003**
Enhance GASD Parser configuration and CLI options to support flexible validation rules for legacy systems.

---

# User Story 21 — Disable Built-in Types Validation

**Story ID:** US-CLI-021
**Epic:** EPIC-CLI-003

### User Story

As a **GASD language engineer**,  
I want the GASD parser CLI to **support bypassing built-in type shadowing via the `--no-validate` option**,  
So that the parser bypasses the `BuiltinShadowingError: Cannot redefine built-in type` validation, allowing me to redefine or shadow built-in types in legacy or specialized `.gasd` specifications.

---

### Acceptance Criteria

| ID                | Criteria                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| AC-CLI-021-01     | The GASD CLI MUST support bypassing built-in shadowing when `--no-validate` is present.              |
| AC-CLI-021-02     | When `--no-validate` is provided, the parser MUST bypass validation for redefining built-in types in the Semantic AST system. |
| AC-CLI-021-03     | When the flag is provided, defining a `TYPE` that shares a name with a built-in type MUST NOT throw a `BuiltinShadowingError`. |
| AC-CLI-021-04     | When the flag is omitted (default behavior), redefining a built-in type MUST continue to throw a `BuiltinShadowingError`. |

---

### Acceptance Tests

| Test ID            | Description                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| AT-CLI-021-01      | Running `gasd-parser --no-validate spec.gasd` where `spec.gasd` defines `TYPE String` passes validation without throwing `BuiltinShadowingError`. |
| AT-CLI-021-02      | Running `gasd-parser spec.gasd` where `spec.gasd` defines `TYPE String` throws `BuiltinShadowingError`. |

---

### Negative Tests

| Test ID            | Description                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| NT-CLI-021-01      | The `--no-validate` flag MUST ONLY bypass the specific `BuiltinShadowingError` in the Semantic AST system if it is being generated. |
