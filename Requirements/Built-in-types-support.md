# GASD Built-in Types — Traceable User Stories

## GASD Specification References

- [GASD_Specification-1.1.md](Requirements/GASD-Specs/GASD_Specification-1.1.md)
- [gasd-1.1.0.gasd](Requirements/GASD-Specs/gasd-1.1.0.gasd)

---

## Epic

**EPIC-SEMAST-002**
Implement a **Comprehensive System Type System** for the GASD Transpiler that provides native support for fundamental primitives, structural generics, and domain-specific identity types, ensuring deterministic cross-language mapping.

---

# User Story 19 — Built-in Standard Types Support

**Story ID:** US-SEMAST-019
**Epic:** EPIC-SEMAST-002

### User Story

As a **GASD language engineer**,  
I want the GASD parser and semantic validator to **implicitly support a standard library of built-in types**,  
So that authors do not need to explicitly define common primitives (like `String`, `Integer`) or structural patterns (like `Result<T>`, `Optional<T>`) in every specification file.

---

### 1. Functional Requirements: Core Type Categories

#### 1.1 Primitive Types

These represent fundamental value types with defined behavioral semantics (§5.1).

| GASD Type | Description                              | Deterministic Contract                                        |
| --------- | ---------------------------------------- | ------------------------------------------------------------- |
| `String`  | UTF-8 text sequence                      | MUST ensure valid UTF-8 and character-based length validation |
| `Integer` | Signed integer value                     | MUST support at least 64-bit range                            |
| `Float`   | IEEE-754 double precision floating point | Used for approximate numeric values                           |
| `Decimal` | Fixed-point precise numeric value        | MUST be used for financial calculations                       |
| `Boolean` | Logical true/false                       | MUST NOT allow truthy/falsy coercion                          |
| `Int`     | Alias for `Integer`                     | Equivalent to `Integer`                                       |
| `Bytes`   | Raw binary sequence                      | Length checks operate on byte count                           |

#### 1.2 Identity and Time Types

Commonly required domain primitives for agentic and distributed systems.

| GASD Type  | Description                           | Deterministic Contract                               |
| ---------- | ------------------------------------- | ---------------------------------------------------- |
| `UUID`     | 128-bit universally unique identifier | MUST follow RFC-4122 canonical representation        |
| `DateTime` | Timestamp value                       | MUST be stored in UTC and represented using ISO-8601 |

#### 1.3 Structural / Generic Types

Container types that enforce structural composition (§5.2).

| GASD Type     | Description                    | Transpilation Behavior                        |
| ------------- | ------------------------------ | --------------------------------------------- |
| `List<T>`     | Ordered collection of items    | Maps to native `List` or `Array`              |
| `Map<K, V>`   | Key-value dictionary           | Maps to native `Map` or `Dictionary`          |
| `Optional<T>` | Value may be absent            | Forces nullability check or `Option` monad    |
| `Result<T>`   | Success or failure return type | Forces explicit error/success branch handling |

#### 1.4 Utility Types

System-level types for dynamic or terminal behavior.

| GASD Type | Description     | Role                                   |
| --------- | --------------- | -------------------------------------- |
| `Any`     | Dynamic value   | Explicitly disables static type safety |
| `Void`    | No return value | Equivalent to unit type                |
| `Enum`    | Enumerated type | Base type for all enum definitions     |

---

### Acceptance Criteria

| ID                | Criteria                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| AC-SEMAST-019-01  | The Semantic Symbol Table MUST pre-register all 14 built-in types upon initialization.                 |
| AC-SEMAST-019-02  | Reference resolution (V008) MUST NOT produce warnings/errors for these built-in types.                 |
| AC-SEMAST-019-03  | Structural types (`List`, `Map`, `Optional`, `Result`) MUST support generic type arguments.            |
| AC-SEMAST-019-04  | The validator MUST reject re-definition of a built-in type name to prevent shadowing (Collision Error).  |
| AC-SEMAST-019-05  | Built-in types MUST be available in `TYPE` field definitions, `METHOD` signatures, and `FLOW` params.  |
| AC-SEMAST-019-06  | `VALIDATE AS TYPE` bindings MUST resolve correctly to built-in types (e.g., `VALIDATE x AS TYPE.String`).|

---

### Acceptance Tests

| Test ID            | Description                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| AT-SEMAST-019-01   | Validating a file using `String` and `Integer` without local definition passes without V008 warnings. |
| AT-SEMAST-019-02   | `Result<UserProfile>` in a `COMPONENT` interface resolves its base type to the built-in `Result`.     |
| AT-SEMAST-019-03   | `DateTime` field in a `TYPE` resolves correctly and enables `@format`/`@range` annotations.           |
| AT-SEMAST-019-04   | `VALIDATE payload AS TYPE.String` resolves successfully in a `FLOW`.                                  |
| AT-SEMAST-019-05   | Attempting to define `TYPE String: value: String` produces a `SymbolCollisionError`.                  |

---

### Negative Tests

| Test ID            | Description                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| NT-SEMAST-019-01   | Using an unknown type `MyCustomType` (not built-in, not defined) produces a `V008` warning.           |
| NT-SEMAST-019-02   | Providing too many/few generic arguments to `Map` (e.g., `Map<String>`) produces a resolution error.  |

---

# User Story 20 — Backward Compatibility & Regression Safety

**Story ID:** US-SEMAST-020
**Epic:** EPIC-SEMAST-002

### User Story

As a **GASD language engineer**,  
I want the GASD parser and semantic validator to **maintain backward compatibility with existing specifications**,  
So that new features and improvements do not inadvertently break existing, validated `.gasd` files or change their expected behavior.

---

### Acceptance Criteria

| ID                | Criteria                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| AC-SEMAST-020-01  | All existing `.gasd` files in the `Specs/examples/` and `Impl/tests/` suites MUST continue to pass validation. |
| AC-SEMAST-020-02  | The Semantic Pipeline MUST NOT introduce side effects that break Syntactic AST extraction.              |
| AC-SEMAST-020-03  | Standard validation passes (DuplicateNames, RequiredSections) MUST remain functional and independent.  |
| AC-SEMAST-020-04  | The `gasd-parser` CLI output and exit codes MUST remain consistent with previous versions.             |

---

### Negative Tests

| Test ID            | Description                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| RT-SEMAST-020-01   | Automated regression check: Ensure CLI `--no-validate` flag still works exactly as before.           |
| RT-SEMAST-020-02   | Cross-platform parity test: Ensure the validator behaves identically on MacOS, Linux, and Windows.   |

---

### Requirements Traceability Matrix

| Requirement                | User Story    | Acceptance Test  | Negative Test    | Spec Reference |
| -------------------------- | ------------- | ---------------- | ---------------- | -------------- |
| REQ-BUILTIN-01 Primitives  | US-SEMAST-019 | AT-SEMAST-019-01 | NT-SEMAST-019-01 | §5.1           |
| REQ-BUILTIN-02 Identity    | US-SEMAST-019 | AT-SEMAST-019-03 | NT-SEMAST-019-01 | §5.1           |
| REQ-BUILTIN-03 Generics    | US-SEMAST-019 | AT-SEMAST-019-02 | NT-SEMAST-019-02 | §5.2           |
| REQ-BUILTIN-04 Bindings    | US-SEMAST-019 | AT-SEMAST-019-04 | -                | §5.3 / GEP-5   |
| REQ-BUILTIN-05 No Shadowing| US-SEMAST-019 | AT-SEMAST-019-05 | -                | §2.4           |

---

## 💎 Future Recommendations: Mission-Critical Agentic Types

To enhance the robustness of agent-generated systems, the following types should be considered for future GASD iterations:

1. **`Money`**: A structural type ensuring currency/amount pair to prevent precision loss.
2. **`Stream<T>`**: Asynchronous sequence type for handling high-volume agent telemetry.
3. **`Secret<T>`**: A wrapper type that forces redaction in logs and encourages secure handling.
