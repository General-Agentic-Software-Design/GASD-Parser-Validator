# GASD Enhancement Proposal (GEP)

```text
GEP: 5
Title: Mandatory Explicit VALIDATE AS TYPE Binding
Author: Agentic Software Design (https://github.com/agentic-software-design)
Status: Accepted
Type: Standards Track
Created: 2026-03-08
Requires: GASD 1.1.0
```

---

# Abstract

This proposal extends the `VALIDATE` keyword in GASD 1.1.0 to **require** an explicit `AS TYPE.TypeName` binding on every VALIDATE step. This eliminates ambiguity in TYPE annotation enforcement by declaring exactly which TYPE's `@annotation` contracts are being enforced at each validation point.

---

# Motivation

The current GASD 1.1.0 specification defines VALIDATE as:

> "VALIDATE — Triggers validation from TYPE constraints against an expression"

This leaves critical questions unanswered: which TYPE is being validated, how the transpiler identifies the authoritative enforcer of a TYPE's `@annotations`, and what happens when expressions are transformed before validation.

Without explicit binding, agents and transpilers must infer the target TYPE — a fragile process that violates GASD's core principle of eliminating interpretation variance. Analysis shows agents perform significantly better with mandatory explicit rules (90%+ quality) compared to implicit inference (65–75% quality).

---

# Specification

### Grammar Changes (Appendix A)

The `action` rule for VALIDATE is updated to require `asBinding`:

```diff
 (* --- Flows --- *)
- action        ::= "VALIDATE" expr
+ action        ::= "VALIDATE" expr asBinding
```

New grammar rules are added:

```ebnf
asBinding       ::= "AS" typePath
typePath        ::= "TYPE" "." typeIdentifier { "." fieldIdentifier }
typeIdentifier  ::= IDENTIFIER
fieldIdentifier ::= IDENTIFIER
```

### Flow Keywords (Section 7)

The VALIDATE row is updated to reflect mandatory binding:

| Keyword | Purpose | Determinism Effect |
|---|---|---|
| `VALIDATE` | Triggers validation from TYPE constraints. Requires explicit binding: `VALIDATE expr AS TYPE.TypeName`. See §5.3. | Agent uses exact annotations |

### Types & Contracts (Section 5 — New Subsection 5.3)

A new subsection **5.3 Annotation Enforcement via VALIDATE Binding** is added, defining:

* **Active Contracts**: `@annotations` on TYPE fields declare active constraints that MUST be enforced.
* **Mandatory Binding**: All VALIDATE steps MUST include `AS TYPE.TypeName`. No implicit binding is supported.
* **Enforcement Semantics**: When binding is declared, the transpiler generates runtime guards, routes boundary tests, and designates the FLOW as authoritative enforcer.
* **Multiple Validators**: Multiple FLOWs MAY validate the same TYPE.
* **Unbound TYPEs**: TYPEs with `@annotations` but no VALIDATE binding produce no guards or tests; transpiler SHOULD warn.
* **Errors**: Transpiler MUST error if AS binding is missing or resolves to undefined TYPE.

### Examples

```gasd
// Simple explicit binding
FLOW validate_user(user: User) -> Result<User>:
    1. VALIDATE user AS TYPE.User
    2. RETURN user

// Multi-TYPE explicit binding
FLOW validate_pair(order: Order, user: User) -> Result<(Order, User)>:
    1. VALIDATE order AS TYPE.Order
    2. VALIDATE user AS TYPE.User
    3. RETURN (order, user)

// Transform then validate
FLOW transform_and_validate(raw: RawInput) -> Result<ProcessedData>:
    1. ACHIEVE "Transform RawInput to ProcessedData"
    2. VALIDATE result AS TYPE.ProcessedData
    3. RETURN result

// Field-level binding (advanced)
FLOW validate_order_total(order: Order) -> Result<Order>:
    1. VALIDATE order.total AS TYPE.Order.total
    2. RETURN order
```

### Standard Annotation Library (Section 13)

No changes required. All existing annotations remain valid.

---

# Rationale

Mandatory explicit binding was chosen over implicit inference and hybrid (optional AS) approaches for three reasons:

1. **Agent performance**: Agents score 90%+ quality with explicit rules vs 65–75% with implicit inference — a significant 20pp improvement.
2. **GASD philosophy alignment**: Implicit binding introduces "magical behavior" that violates GASD's principle that all design choices must be declared.
3. **Simplicity**: One clear rule (always use `AS TYPE`) is easier to specify, implement, lint, and audit than a hybrid system with two conflicting styles.

The trade-off is ~30% more text per VALIDATE step, which is acceptable given the quality and reliability gains.

---

# Backwards Compatibility

This change requires adding `AS TYPE.TypeName` to existing `VALIDATE` statements. The migration is mechanical:

```diff
- 1. VALIDATE user
+ 1. VALIDATE user AS TYPE.User
```

Transpilers MUST support clear migration warnings to guide users through the upgrade path.

---

# Reference Implementation (Optional)

The reference implementation involves:

* **Parser**: Update the VALIDATE action rule to require `asBinding` (not optional). Add `asBinding`, `typePath`, `typeIdentifier`, `fieldIdentifier` grammar rules.
* **AST**: The `ValidateStep` node stores a required `binding: TypePath` field alongside the existing `target: Expression`.
* **Semantic Analysis**: Resolve AS binding to a TYPE definition; error if missing or undefined.
* **Code Generation**: Generate runtime guard functions for all `@annotations` on the bound TYPE.
* **Test Derivation**: Route boundary tests to the FLOW containing the VALIDATE binding.

---

# Test Plan

* **Acceptance Test (AT-VALIDATE-001)**: `VALIDATE user AS TYPE.User` parses and resolves binding correctly, generating guards for all `@annotations`.
* **Acceptance Test (AT-VALIDATE-002)**: Multi-TYPE FLOW with `VALIDATE order AS TYPE.Order` and `VALIDATE user AS TYPE.User` generates separate guard sets.
* **Acceptance Test (AT-VALIDATE-003)**: Transform-then-validate with `VALIDATE result AS TYPE.ProcessedData` binds correctly.
* **Regression Test (RT-VALIDATE-001)**: Upgraded VALIDATE statements (with AS added) transpile successfully.
* **Regression Test (RT-VALIDATE-002)**: Other flow keywords (ACHIEVE, CREATE, PERSIST) remain unaffected.
* **Negative Test (NT-VALIDATE-001)**: `VALIDATE user` (without AS) produces a clear error.
* **Negative Test (NT-VALIDATE-002)**: `VALIDATE user AS TYPE.NonexistentType` produces a clear error.
* **Boundary Test (BT-VALIDATE-001)**: All `@annotation` types (@format, @range, @min_length, @max_length, @unique, @default) generate guards and derived tests.

---

# Traceability

* **Requirement**: Mandatory explicit TYPE→FLOW binding for deterministic annotation enforcement.
* **Grammar**: `asBinding`, `typePath` rules in Appendix A.
* **Spec Sections**: 5.3 (Annotation Enforcement via VALIDATE Binding), 7 (Flow Keywords).
* **Tests**: AT-VALIDATE-001 through BT-VALIDATE-001.

---

# Change History

```
2026-03-08 — Revised to mandatory explicit binding (removed implicit support)
2026-03-08 — Initial draft (hybrid implicit + explicit)
```
