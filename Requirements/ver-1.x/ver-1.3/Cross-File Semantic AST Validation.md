# Epic: Cross-File Semantic AST Validation

**Epic ID:** EPIC-X-SEMAST-001

## Description

The GASD parser MUST support semantic validation across multiple interconnected specification files. This involves resolving imports, constructing a global symbol table, and enforcing semantic rules (Type, Component, Flow, Decision, etc.) across the entire compilation unit, ensuring structural and architectural consistency at scale.

## GASD Specification References

- [GASD_Specification-1.1.md](Specs/GASD_Specification-1.1.md)
- [gasd-1.1.0.gasd](Specs/gasd-1.1.0.gasd)

---

## General Constraints

- **Backward Compatibility:** All existing single-file validation features, AST generation logic, and syntactic parsing MUST remain unbroken during the implementation of cross-file semantic validation.
- **Regression Testing:** Existing test suites (Unit, Acceptance, Regression) for v1.2.2 MUST maintain 100% pass rate when running with the new v1.3.0 compilation engine.

---

## User Story 1 — Multi-File Compilation Unit Support

**Story ID:** US-X-SEMAST-001
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-001 User Story

As a **GASD transpiler**,
I want to **load and organize multiple GASD files into a single compilation unit**,
So that **cross-file semantic analysis can be performed**.

### US-X-SEMAST-001 Acceptance Criteria

| ID                | Criteria                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-001-01 | The system accepts multiple GASD files as input and normalizes their file paths across different OS environments. |
| AC-X-SEMAST-001-02 | Files are sorted by canonical path to maintain deterministic processing order.                        |
| AC-X-SEMAST-001-03 | Each file node in the compilation unit stores its path, namespace, imports, and syntactic AST root.    |
| AC-X-SEMAST-001-04 | The system handles both absolute and relative paths correctly during compilation unit construction.   |

### US-X-SEMAST-001 Acceptance Tests

| Test ID            | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| AT-X-SEMAST-001-01 | Given files `types.gasd`, `auth.gasd`, `payment.gasd`, the `CompilationUnit` contains exactly 3 file nodes. |
| AT-X-SEMAST-001-02 | Files provided in different command-line order result in the same deterministic internal order.                   |
| AT-X-SEMAST-001-03 | Providing `./types.gasd` and `types.gasd` results in a single normalized node.                                |

### US-X-SEMAST-001 Regression Tests

| Test ID            | Description                                                                        |
| ------------------ | ---------------------------------------------------------------------------------- |
| RT-X-SEMAST-001-01 | Duplicate file paths in the input list produce a fatal error.                    |
| RT-X-SEMAST-001-02 | Missing or inaccessible files produce a clear IO error before semantic analysis. |
| RT-X-SEMAST-001-03 | Large-scale input (500+ files) does not exceed memory or file handle limits.    |

---

## User Story 2 — Import Graph Resolution

**Story ID:** US-X-SEMAST-002
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-002 User Story

As a **semantic analyzer**,
I want to **resolve all IMPORT statements across files**,
So that **dependencies are validated and ordered correctly**.

### US-X-SEMAST-002 Acceptance Criteria

| ID                | Criteria                                                                                                   |
| ----------------- | ---------------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-002-01 | All `IMPORT` statements are parsed and linked to the corresponding physical files in the compilation unit. |
| AC-X-SEMAST-002-02 | Alias imports (e.g., `IMPORT "types.gasd" AS T`) are correctly registered to resolve qualified names.        |
| AC-X-SEMAST-002-03 | A global dependency graph is constructed to determine the correct multi-pass processing order.              |
| AC-X-SEMAST-002-04 | Circular import dependencies (e.g., A → B → C → A) are detected and reported as fatal errors.               |
| AC-X-SEMAST-002-05 | Redundant imports (same file imported multiple times) are handled gracefully without duplication.          |

### US-X-SEMAST-002 Acceptance Tests

| Test ID            | Description                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------- |
| AT-X-SEMAST-002-01 | `IMPORT "types.gasd"` successfully links to the `types.gasd` file node.                   |
| AT-X-SEMAST-002-02 | Qualified reference `T.EmailAddress` resolves to the correct symbol in the aliased file. |
| AT-X-SEMAST-002-03 | A circular import chain produces a `CircularImportError` with the full path of the cycle. |
| AT-X-SEMAST-002-04 | Importing a non-existent file path produces a specific `FileNotFoundImportError`.         |

### US-X-SEMAST-002 Regression Tests

| Test ID            | Description                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------- |
| RT-X-SEMAST-002-01 | Deep import chains (10+ levels) are handled without stack overflow.                     |
| RT-X-SEMAST-002-02 | Multiple aliases for the same file in different files do not cause resolution conflicts. |
| RT-X-SEMAST-002-03 | Absolute path imports work consistently across different file systems.                   |

---

## User Story 3 — Global Symbol Table Construction

**Story ID:** US-X-SEMAST-003
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-003 User Story

As a **semantic analyzer**,
I want to **construct a global symbol table across all files**,
So that **all references resolve consistently across the entire system**.

### US-X-SEMAST-003 Acceptance Criteria

| ID                | Criteria                                                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------ |
| AC-X-SEMAST-003-01 | Every symbol (`TYPE`, `COMPONENT`, `FLOW`, `STRATEGY`, `DECISION`) is registered in a unified table.                    |
| AC-X-SEMAST-003-02 | Namespace scoping is respected, allowing same-name symbols in different namespaces (`com.a.User` vs `com.b.User`).       |
| AC-X-SEMAST-003-03 | Duplicate symbol definitions within the same namespace produce a `DuplicateSymbolError`.                               |
| AC-X-SEMAST-003-04 | Standard built-in types (`String`, `Integer`, `List`, `Map`, `Result`) are always globally available.                    |
| AC-X-SEMAST-003-05 | Shadowing rules are enforced: Local definitions cannot shadow built-ins, but can shadow imports if qualified correctly. |

### US-X-SEMAST-003 Acceptance Tests

| Test ID            | Description                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| AT-X-SEMAST-003-01 | Symbols from all 15 example files are correctly merged into the final global table.                  |
| AT-X-SEMAST-003-02 | Attempting to define two `TYPE User` in the same namespace fails with a specific error message.      |
| AT-X-SEMAST-003-03 | Qualified `NamespaceA.User` and unqualified `User` (local) are distinguished correctly.               |

### US-X-SEMAST-003 Regression Tests

| Test ID            | Description                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------- |
| RT-X-SEMAST-003-01 | Scaling test: Global table construction remains performant with 1000+ symbols.           |
| RT-X-SEMAST-003-02 | Built-in symbols cannot be shadowed or redefined by user declarations.                   |

---

---

## User Story 4 — Cross-File Type Resolution

**Story ID:** US-X-SEMAST-004
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-004 User Story

As a **semantic analyzer**,
I want to **resolve all type references across files**,
So that **TYPE contracts are enforced globally across the multi-file system**.

### US-X-SEMAST-004 Acceptance Criteria

| ID                | Criteria                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-004-01 | Type references in `TYPE` fields, `FLOW` parameters/returns, and `COMPONENT` interfaces resolve across files. |
| AC-X-SEMAST-004-02 | Fully qualified names (e.g., `Common.EmailAddress`) resolve correctly using namespace/import rules.            |
| AC-X-SEMAST-004-03 | Generic types (e.g., `List<T>`, `Map<K,V>`) resolve their type arguments recursively across files.          |
| AC-X-SEMAST-004-04 | Unresolved type references produce an `UnknownTypeError` with the context of the reference.                    |
| AC-X-SEMAST-004-05 | Recursive generic depth is handled (up to 10 levels) without resolution failure.                              |

### US-X-SEMAST-004 Acceptance Tests

| Test ID            | Description                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| AT-X-SEMAST-004-01 | `FLOW register(email: EmailAddress)` resolves to an `EmailAddress` defined in an imported file. |
| AT-X-SEMAST-004-02 | `List<EmailAddress>` correctly resolves the inner `EmailAddress` symbol from another namespace. |
| AT-X-SEMAST-004-03 | Type `A` in File 1 references Type `B` in File 2, which references Type `C` in File 3; resolve. |

### US-X-SEMAST-004 Regression Tests

| Test ID            | Description                                                                             |
| ------------------ | --------------------------------------------------------------------------------------- |
| RT-X-SEMAST-004-01 | Nested generic resolution (e.g., `Map<String, List<User>>`) remains stable and correct. |
| RT-X-SEMAST-004-02 | Invalid generic arity (e.g., `List<T, U>`) produces a semantic error even across files. |

---

## User Story 5 — Cross-File Component & Dependency Resolution

**Story ID:** US-X-SEMAST-005
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-005 User Story

As a **semantic analyzer**,
I want to **resolve component dependencies across files**,
So that **architecture wiring is valid globally**.

### US-X-SEMAST-005 Acceptance Criteria

| ID                | Criteria                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| AC-X-SEMAST-005-01 | `DEPENDENCIES` blocks in `COMPONENT` definitions resolve to symbols defined in other GASD files.        |
| AC-X-SEMAST-005-02 | Cross-file component references are verified for existence in the global symbol table.                 |
| AC-X-SEMAST-005-03 | Circular dependencies between components defined in different files are detected and reported.          |
| AC-X-SEMAST-005-04 | Component `REQUIRES` vs `PROVIDES` contracts are validated across file boundaries.                     |

### US-X-SEMAST-005 Acceptance Tests

| Test ID            | Description                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------ |
| AT-X-SEMAST-005-01 | `DEPENDENCIES: [UserRepository]` resolves to a component defined in `repositories.gasd`.   |
| AT-X-SEMAST-005-02 | Referencing a non-existent component across files produces an `UnknownComponentError`.    |
| AT-X-SEMAST-005-03 | `COMPONENT A` requiring `COMPONENT B` (in File 2) fails if `B` is not defined or visible. |

### US-X-SEMAST-005 Regression Tests

| Test ID            | Description                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| RT-X-SEMAST-005-01 | Deep dependency chains (A -> B -> C where each is in a different file) resolve correctly.        |
| RT-X-SEMAST-005-02 | Moving a component between files does not break dependencies as long as imports are updated. |

---

---

## User Story 6 — Cross-File FLOW Binding

**Story ID:** US-X-SEMAST-006
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-006 User Story

As a **semantic analyzer**,
I want to **bind FLOW definitions to COMPONENT interface methods across files**,
So that **execution semantics are deterministic regardless of module boundaries**.

### US-X-SEMAST-006 Acceptance Criteria

| ID                | Criteria                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-006-01 | `FLOW` definitions bind to `COMPONENT` interface methods even when defined in different GASD files.     |
| AC-X-SEMAST-006-02 | The binding pass verifies signature compatibility (parameter names and types) across file boundaries.  |
| AC-X-SEMAST-006-03 | A `COMPONENT` method without a corresponding `FLOW` (or vice-versa) is reported if mandatory.           |
| AC-X-SEMAST-006-04 | Overloaded methods (if supported) are correctly resolved using cross-file type information.              |

### US-X-SEMAST-006 Acceptance Tests

| Test ID            | Description                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------- |
| AT-X-SEMAST-006-01 | `Greeter.say_hello()` in `api.gasd` correctly binds to `FLOW say_hello()` in `logic.gasd`.                        |
| AT-X-SEMAST-006-02 | An `UnboundFlowError` is produced if a `FLOW` references a component method that doesn't exist.                   |
| AT-X-SEMAST-006-03 | Signature mismatch (e.g., File 1 expects `String`, File 2 defines `Integer`) triggers a `SignatureMismatchError`. |

### US-X-SEMAST-006 Regression Tests

| Test ID            | Description                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| RT-X-SEMAST-006-01 | Multiple components in different files with the same method name do not cause binding ambiguity. |
| RT-X-SEMAST-006-02 | Namespaced flows (e.g., `com.acme.process_order`) bind correctly to their target interfaces.      |

---

## User Story 7 — Cross-File VALIDATE Binding

**Story ID:** US-X-SEMAST-007
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-007 User Story

As a **semantic analyzer**,
I want to **enforce VALIDATE AS TYPE bindings across files**,
So that **type-level constraints are applied correctly to flow logic globally**.

### US-X-SEMAST-007 Acceptance Criteria

| ID                | Criteria                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-007-01 | `VALIDATE ... AS TYPE.X` statements resolve the `TYPE` symbol from imported files.                      |
| AC-X-SEMAST-007-02 | Field-level annotations and constraints from the target `TYPE` are propagated to the local `FLOW` step. |
| AC-X-SEMAST-007-03 | Missing `TYPE` definitions in `VALIDATE` steps across files are reported as semantic errors.            |
| AC-X-SEMAST-007-04 | Partial element validation (e.g., validating only specific fields of a shared `TYPE`) is supported.      |

### US-X-SEMAST-007 Acceptance Tests

| Test ID            | Description                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------ |
| AT-X-SEMAST-007-01 | `VALIDATE email AS TYPE.EmailAddress` correctly binds to a `TYPE` defined in `shared.gasd`.                  |
| AT-X-SEMAST-007-02 | A `ValidateBindingMismatch` error is raised if the validated field type differs from the `TYPE` definition. |
| AT-X-SEMAST-007-03 | Validating a field against a `TYPE` that exists but doesn't share fields fails with `FieldMismatchError`.    |

### US-X-SEMAST-007 Regression Tests

| Test ID            | Description                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------- |
| RT-X-SEMAST-007-01 | Multiple `VALIDATE` steps in different files binding to the same shared `TYPE` resolve correctly. |
| RT-X-SEMAST-007-02 | Updating a `TYPE` in one file correctly reflects in all `VALIDATE` steps across the unit.           |

---

---

## User Story 8 — Cross-File DECISION Enforcement

**Story ID:** US-X-SEMAST-008
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-008 User Story

As a **software architect**,
I want to **apply DECISION constraints across files**,
So that **architectural determinism is preserved globally across the system design**.

### US-X-SEMAST-008 Acceptance Criteria

| ID                | Criteria                                                                                                   |
| ----------------- | ---------------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-008-01 | `DECISION` impact declarations (`AFFECTS`) resolve to `COMPONENT`, `FLOW`, or `TYPE` nodes in other files. |
| AC-X-SEMAST-008-02 | Field-level impact (e.g., `User.password_hash`) resolves correctly across file boundaries.                 |
| AC-X-SEMAST-008-03 | Wildcard impacts (`AFFECTS: [*]`) are correctly applied to all relevant symbols in the compilation unit.   |
| AC-X-SEMAST-008-04 | Conflicting decisions affecting the same symbol across files are detected and reported.                    |
| AC-X-SEMAST-008-05 | Decision `STRATEGY` resolution works globally across file boundaries.                                     |

### US-X-SEMAST-008 Acceptance Tests

| Test ID            | Description                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| AT-X-SEMAST-008-01 | A decision in `arch.gasd` correctly affects a `TYPE` defined in `models.gasd`.                 |
| AT-X-SEMAST-008-02 | A `DecisionTargetError` is raised if an `AFFECTS` clause references an unknown symbol.        |
| AT-X-SEMAST-008-03 | Two decisions in different files affecting the same symbol result in a `DecisionConflictError`. |

### US-X-SEMAST-008 Regression Tests

| Test ID            | Description                                                                         |
| ------------------ | ----------------------------------------------------------------------------------- |
| RT-X-SEMAST-008-01 | Decisions affecting 50+ files simultaneously are processed with stable performance. |
| RT-X-SEMAST-008-02 | Reordering decisions in the source does not change the resulting affected symbol set. |

---

## User Story 9 — Global Constraints & Invariants

**Story ID:** US-X-SEMAST-009
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-009 User Story

As a **software architect**,
I want to **enforce constraints and invariants across the entire system**,
So that **global design invariants are preserved across module boundaries**.

### US-X-SEMAST-009 Acceptance Criteria

| ID                | Criteria                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| AC-X-SEMAST-009-01 | `INVARIANT` and `CONSTRAINT` blocks are collected from all files into a global validation registry.     |
| AC-X-SEMAST-009-02 | Cross-file references within invariant expressions (e.g., `Account.balance`) are resolved correctly.   |
| AC-X-SEMAST-009-03 | Structural violations of global invariants (detected at design-time) are reported with clear context.   |
| AC-X-SEMAST-009-04 | Conflicting invariants (e.g., File 1: `x > 0`, File 2: `x < 0`) are detected and reported.             |

### US-X-SEMAST-009 Acceptance Tests

| Test ID            | Description                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------- |
| AT-X-SEMAST-009-01 | A global invariant `balance >= 0` is correctly associated with the shared `Account` model. |
| AT-X-SEMAST-009-02 | Conflicting invariants defined in different files trigger a `ConstraintConflictError`.      |
| AT-X-SEMAST-009-03 | Invariants referencing aliased types (e.g., `T.Price > 0`) resolve correctly.               |

### US-X-SEMAST-009 Regression Tests

| Test ID            | Description                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| RT-X-SEMAST-009-01 | Adding a new file with an invariant does not invalidate existing valid specifications. |
| RT-X-SEMAST-009-02 | Global invariants are included in the deterministic semantic hash computation.          |

---

---

## User Story 10 — Cross-File Semantic Error Detection

**Story ID:** US-X-SEMAST-010
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-010 User Story

As a **software developer**,
I want to **receive detailed error reports for cross-file semantic violations**,
So that **I can quickly identify and fix issues in multi-module system designs**.

### US-X-SEMAST-010 Acceptance Criteria

| ID                | Criteria                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------ |
| AC-X-SEMAST-010-01 | All cross-file semantic errors (e.g., `UnknownTypeError`, `DuplicateSymbolError`) are detected and reported. |
| AC-X-SEMAST-010-02 | Error messages include the full file path, line number, column, and the offending symbol name.              |
| AC-X-SEMAST-010-03 | Errors are aggregated across all files in the compilation unit into a single report summary.                 |
| AC-X-SEMAST-010-04 | Severity levels (ERROR vs WARNING) are enforced; `--ast-sem` fails on any warning or error.                 |
| AC-X-SEMAST-010-05 | Error reporting order is deterministic (sorted by file path then line/column).                              |

### US-X-SEMAST-010 Acceptance Tests

| Test ID            | Description                                                                      |
| ------------------ | -------------------------------------------------------------------------------- |
| AT-X-SEMAST-010-01 | Referencing a type from an unimported file produces an `UnknownTypeError`.       |
| AT-X-SEMAST-010-02 | Error output correctly identifies a failure in `auth.gasd:45:12`.                |
| AT-X-SEMAST-010-03 | Running with `--ast-sem` on a spec with warnings returns exit code 1 and no AST. |

### US-X-SEMAST-010 Regression Tests

| Test ID            | Description                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------- |
| RT-X-SEMAST-010-01 | Multiple errors in different files are all reported, not just the first one found.          |
| RT-X-SEMAST-010-02 | Syntax errors in one file do not suppress semantic errors in others (if analysis proceeds). |

---

## User Story 11 — Deterministic Semantic Graph

**Story ID:** US-X-SEMAST-011
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-011 User Story

As a **GASD transpiler**,
I want to **produce a deterministic cross-file semantic graph**,
So that **identical inputs always yield identical outputs regardless of environment or execution order**.

### US-X-SEMAST-011 Acceptance Criteria

| ID                | Criteria                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-011-01 | All symbol collections (types, components, flows) are sorted alphabetically in the output.        |
| AC-X-SEMAST-011-02 | Identifiers are normalized and stable IDs are generated based on namespace and name hashes.        |
| AC-X-SEMAST-011-03 | The Semantic AST JSON output is identical for the same set of input files across different runs.  |

### US-X-SEMAST-011 Acceptance Tests

| Test ID            | Description                                                                    |
| ------------------ | ------------------------------------------------------------------------------ |
| AT-X-SEMAST-011-01 | Running the tool on `[fileA, fileB]` yields the same JSON as `[fileB, fileA]`. |
| AT-X-SEMAST-011-02 | Semantic hashes remain stable across different machine environments.           |

### US-X-SEMAST-011 Regression Tests

| Test ID            | Description                                                                           |
| ------------------ | ------------------------------------------------------------------------------------- |
| RT-X-SEMAST-011-01 | Parallel execution (if implemented) does not introduce non-determinism in the output. |
| RT-X-SEMAST-011-02 | Adding or removing comments does not affect the semantic graph or its hash.           |

---

## User Story 12 — Full Test Matrix & Regression Strategy

**Story ID:** US-X-SEMAST-012
**Epic:** EPIC-X-SEMAST-001

### US-X-SEMAST-012 User Story

As a **quality engineer**,
I want to **verify the cross-file validation system against a comprehensive test matrix**,
So that **all features are validated and regressions are prevented**.

### US-X-SEMAST-012 Acceptance Criteria

| ID                | Criteria                                                                                                              |
| ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| AC-X-SEMAST-012-01 | A test matrix covering 100+ feature/error combinations (Imports, Types, Flows, Decisions, Invariants) is implemented. |
| AC-X-SEMAST-012-02 | A "Golden File" regression suite compares actual Semantic AST JSON output against expected baselines.                  |
| AC-X-SEMAST-012-03 | Fuzz testing and mutation testing (e.g., reordering imports) are used to verify system robustness.                     |
| AC-X-SEMAST-012-04 | The test matrix includes specific 'Stress Tests' for deep import recursion and massive symbol tables.                 |

### Featured Test Domains (Full Coverage Matrix)

| Domain             | Coverage Details                                                                 |
| ------------------ | -------------------------------------------------------------------------------- |
| **Imports**        | Single/Multi, Aliased, Circular, Absolute/Relative, Redundant, Missing.          |
| **Namespaces**     | Global vs Local, Nested Namespaces, Cross-Namespace Resolution, Shadowing.       |
| **Types**          | Primivite, Custom, Generic (Nested), Recursive, Optional, Literal, Unresolved.   |
| **Components**     | Dependencies, REQUIRES/PROVIDES contracts, Signature validation, Circular deps.  |
| **Flows**          | Component Binding, Parameter/Return validation, Unbound flows, Name collisions.  |
| **Decisions**      | Multi-file affects, Field-level targeting, Conflict detection, Wildcards.        |
| **Constraints**    | Global Invariants, Local Constraints, Conflict Resolution, Aliased enforcement.  |
| **Determinism**    | Input Permutation, Parallel Execution, Hash stability, Environment neutrality.   |
| **Error Handling** | Aggregation, Location accuracy, Severity enforcement, Deterministic reporting.   |

### US-X-SEMAST-012 Acceptance Tests

| Test ID            | Description                                                                           |
| ------------------ | ------------------------------------------------------------------------------------- |
| AT-X-SEMAST-012-01 | 100% pass rate on the 100-feature semantic test matrix across all 12 stories.         |
| AT-X-SEMAST-012-02 | Golden file comparison fails immediately if output structure or data changes.         |
| AT-X-SEMAST-012-03 | Mutation tools confirm that no semantic change is invisible to the validation engine. |

### US-X-SEMAST-012 Regression Tests

| Test ID            | Description                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| RT-X-SEMAST-012-01 | Scale testing with 100+ files and 10,000 symbols remains within performance bounds.   |
| RT-X-SEMAST-012-02 | Mutation tests confirm that renaming a shared symbol correctly updates all references. |
| RT-X-SEMAST-012-03 | Cross-OS path normalization regression test (Windows vs Linux style paths).           |

---

---
