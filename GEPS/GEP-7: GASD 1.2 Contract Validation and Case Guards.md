# GASD Enhancement Proposal (GEP)

```text
GEP: 7
Title: GASD 1.2 Contract Validation and Case Guards
Author: Agentic Software Design (https://github.com/agentic-software-design)
Status: Accepted
Type: Standards Track
Created: 2026-11-21
Requires: GEP 6 (GASD 1.2)
```

---

# Abstract

This proposal completes the grammar for GASD 1.2 contract parameters and defines how to validate contract cases. Optional `WHEN` guards let authors state which inputs make a case eligible. A verifier checks each observed call against the eligible cases and reports when it lacks evidence to verify an outcome.

---

# Motivation

GASD 1.2 already defines `CONTRACT` blocks. Two gaps in that definition affect automated validation. Appendix A referenced `param_list` without defining it, even though GEP 6 included the production. A `CASE` also lacked a formal trigger for deciding when it applies. GEP 7 restores the missing production and adds optional `WHEN` guards so validators can determine case eligibility from the supplied inputs. [GASD 1.2 specification](../GASD-1.2/GASD_Specification.md#appendix-a-formal-ebnf-grammar) · [GEP 6](./GEP-6%3A%20GASD%201.2%20%E2%80%94%20Formal%20Semantics%2C%20Contract%20Modeling%2C%20and%20Verification%20Support)

The inventory example exposed a separate enforcement gap. `InventoryService.release_stock` had no `BEHAVIORS` block, yet `gasd_parser` 2.1.6 reported a pass and emitted a contract with zero cases. The example now specifies success, failure, and the effect of repeating a release. [Inventory service example](../examples/gasd-1.2/multi-file/inventory_service.gasd)

---

# Specification

## Grammar

The following excerpt uses the shared type, expression, and lexical rules in Appendix A. A `WHEN` clause belongs to the `CASE` that contains it and precedes that case's outcome clauses. [GASD 1.2 Appendix A](../GASD-1.2/GASD_Specification.md#appendix-a-formal-ebnf-grammar)

```ebnf
param_list      ::= parameter { "," parameter }
parameter       ::= identifier ":" type_expr

contract_def    ::= "CONTRACT" qualified_name ":" indent
                    [ "INPUT" ":" param_list ]
                    "OUTPUT" ":" type_expr
                    "BEHAVIORS" ":" indent case_def { case_def } dedent
                    [ "IDEMPOTENT" ":" boolean_literal ]
                    [ "VERSION" ":" string_literal ]
                    dedent

case_def        ::= "CASE" identifier ":" indent
                    { "WHEN" ":" input_predicate }
                    case_clause { case_clause }
                    dedent

case_clause     ::= "POSTCONDITION" ":" ( postcondition_expr | string_literal )
                  | "THROWS" ":" qualified_name
                  | "AFTER" ":" ( duration_literal | identifier "(" value_list ")" )

input_predicate ::= input_operand ( comparison_op input_operand | "IS" type_expr )
input_operand   ::= qualified_name | string_literal | number_literal | boolean_literal | "null"
comparison_op   ::= "==" | "!=" | ">" | "<" | ">=" | "<="
```

## Static validation

- A contract **MUST** declare typed inputs with unique names for methods that take parameters. Omit `INPUT` for a zero-parameter method. The contract's parameter order, parameter types, and output type **MUST** match the referenced interface method.
- `BEHAVIORS` **MUST** contain at least one case. Case names **MUST** be unique within the contract. Every case **MUST** contain at least one `POSTCONDITION` or `THROWS`. It **MAY** contain at most one `THROWS` and one `AFTER`.
- A guard's value references **MUST** resolve to declared input parameters or their fields. Comparisons use GASD strict type semantics. Ordering operators require numeric operands. `null` may be used in equality comparisons and is equal only to itself.
- `LINT-007` treats a contract with zero cases or a case with zero outcome clauses as an error. A guard or timing clause alone leaves the case without an outcome.

## Case eligibility and outcomes

Evaluate guards against supplied arguments before argument validation or invocation. Within a case, evaluate guards in source order and stop at the first false guard. A case with all guards true or with zero guards is eligible. A guard that is reached and cannot be evaluated **MUST** produce a verification error. Several cases can be eligible for one call, regardless of their declaration order.

An observed call conforms when an eligible case matches the completion mode and all of its postconditions and timing requirements. `THROWS` requires exceptional completion with the declared error type. Cases with no `THROWS` require a normal return. `result` denotes the return value on a normal return. For `Result<T>`, `result` denotes the success payload and `error` denotes the failure payload, each on its respective variant. `void` denotes the unit value. On an exceptional return, `error` denotes the exception and `result` is available if the verifier observes a partial result. A predicate using an unavailable binding cannot satisfy the case.

`AFTER` with a duration requires at least that much time between invocation and completion. `AFTER: retry(n)` requires `n` additional attempts, where `n` is a nonnegative integer. Quoted postconditions require independent evidence. If no eligible case is verified, report the call as **unverified** when a case could match and evidence is missing. Report a **contract violation** when no eligible case can match. Coverage across all inputs and outcomes requires evidence beyond individual call checks.

```gasd
CONTRACT PaymentService.createCustomer:
    INPUT: email: String
    OUTPUT: PaymentCustomer
    BEHAVIORS:
        CASE success:
            WHEN: email != null
            POSTCONDITION: result.status == "ACTIVE"
            POSTCONDITION: result.customerId IS UUID
        CASE service_failure:
            WHEN: email != null
            THROWS: PaymentGatewayException
            AFTER: retry(2)
        CASE timeout:
            WHEN: email != null
            THROWS: PaymentGatewayException
            AFTER: 3000ms
        CASE null_input:
            WHEN: email == null
            THROWS: IllegalArgumentException
    IDEMPOTENT: true
```

---

# Rationale

Optional guards preserve input-independent cases and let authors add predicates where input actually changes the expected behavior. Requiring a guard on every case would add repeated conditions to contracts that allow several outcomes for the same input. A first-match rule would make a valid service failure or timeout depend on case order. Checking all eligible cases lets the payment example describe both outcomes for a non-null email without inventing a priority.

Quoted postconditions capture observable effects, such as inventory state changes, that often require a test fixture or inspection of external state. Reporting these calls as unverified when evidence is missing keeps the distinction between a successful parse and a verified invocation explicit.

---

# Backwards Compatibility

Existing GASD 1.2 contracts with complete, valid unguarded cases continue to use the same syntax. An unguarded case remains eligible for every call. A contract that omitted `BEHAVIORS` needs at least one case, and a case containing only timing needs a `POSTCONDITION` or `THROWS`. Contract signature mismatches and duplicate case names become explicit validation errors. The proposal applies to GASD 1.2 contracts.

Tools need to preserve `WHEN` in the AST before they can verify guarded cases. `gasd_parser` 2.1.6 accepts the guarded example but omits its guards from the contract AST.

---

# Reference Implementation (Optional)

The written specification and GASD metamodel include the contract changes. `CaseDefinition.when` stores the guard expressions in source order. The repaired `release_stock` example uses `result` for success and `error` for failure, along with observable inventory postconditions. [GASD 1.2 specification](../GASD-1.2/GASD_Specification.md#61-contract-modeling--contract-gasd-12-addition) · [GASD metamodel](../GASD-1.2/gasd-1.2.0.gasd) · [Inventory service example](../examples/gasd-1.2/multi-file/inventory_service.gasd)

Parser and verifier work remains. Parse leading `WHEN` clauses into each case and retain them in syntactic and semantic AST exports. Validate the referenced interface signature, guard types and bindings, and case structure, including `LINT-007` for a contract with zero cases. Apply the eligibility and outcome rules when checking an observed call.

---

# Test Plan

| ID | Type | Expected result |
| --- | --- | --- |
| `AT-GEP7-001` | Acceptance | A contract with multiple parameters, a qualified type such as `List<Common.OrderItem>`, and a `Result<Void>` output parses. A zero-parameter contract parses with `INPUT` omitted. |
| `AT-GEP7-002` | Acceptance | Multiple `WHEN` clauses survive AST export in source order. A false guard short-circuits later guards in the same case. |
| `AT-GEP7-003` | Acceptance | A null email can match `null_input`. A non-null email can match success, service failure, or timeout if the outcome requirements hold. Reordering the cases leaves the results unchanged. |
| `AT-GEP7-004` | Acceptance | A matching return with an unevidenced quoted postcondition is unverified. An observed return that cannot satisfy any eligible case is a violation. |
| `RT-GEP7-001` | Regression | `gasd_parser --gasd-ver 1.2 examples/gasd-1.2` reports each file's status. The baseline with parser 2.1.6 was 31 passes and zero warnings, both individually and as a suite. |
| `RT-GEP7-002` | Regression | The `release_stock` AST contains the `released` and `failed` cases with the expected predicates. A repeat release leaves stock unchanged. |
| `NT-GEP7-001` | Negative | A missing or empty `BEHAVIORS` block, a guard-only case, and a timing-only case are rejected. |
| `NT-GEP7-002` | Negative | Duplicate parameter names, duplicate case names, and an interface signature mismatch are rejected. |
| `NT-GEP7-003` | Negative | A guard that references an undeclared value or `result`, compares nonnumeric values with an ordering operator, or follows an outcome clause is rejected. |

The observed parser results cover the 31 bundled files and the repaired inventory AST. The guard round-trip, stricter diagnostics, and runtime checks describe expected results for an implementation of this proposal.

---

# Traceability

| Requirement | Specification and artifacts | Tests |
| --- | --- | --- |
| Parse typed contract signatures | [GASD 1.2 Appendix A](../GASD-1.2/GASD_Specification.md#appendix-a-formal-ebnf-grammar) and [GASD metamodel](../GASD-1.2/gasd-1.2.0.gasd) | `AT-GEP7-001`, `NT-GEP7-002` |
| Require cases and observable outcomes | [GASD 1.2 contract rules and `LINT-007`](../GASD-1.2/GASD_Specification.md#static-validation), [inventory service example](../examples/gasd-1.2/multi-file/inventory_service.gasd) | `RT-GEP7-001`, `RT-GEP7-002`, `NT-GEP7-001` |
| Preserve and evaluate guards | [GASD 1.2 call verification](../GASD-1.2/GASD_Specification.md#verifying-a-call) and [GASD metamodel](../GASD-1.2/gasd-1.2.0.gasd) | `AT-GEP7-002`, `AT-GEP7-003`, `NT-GEP7-003` |
| Report the status of observed outcomes | [GASD 1.2 call verification](../GASD-1.2/GASD_Specification.md#verifying-a-call) | `AT-GEP7-004` |

---

# Change History

```text
2026-11-21 — Initial draft
2026-11-21 — Accepted
```
