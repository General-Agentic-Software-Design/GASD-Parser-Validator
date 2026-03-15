# GASD Semantic AST — Traceable User Stories

## GASD Specification References

- [GASD_Specification-1.1.md](Requirements/GASD-Specs/GASD_Specification-1.1.md)
- [gasd-1.1.0.gasd](Requirements/GASD-Specs/gasd-1.1.0.gasd)

---

## Epic

**EPIC-SEMAST-001**
Build a **Semantic Model Construction layer for the GASD Transpiler** that transforms the syntactic AST produced by the ANTLR4 parser into a **fully resolved Semantic AST** capable of feeding deterministic code generation.

### Epic Goal

The Semantic AST must:

* Resolve all symbols
* Enforce GASD semantics
* Bind TYPE contracts to FLOW logic
* Resolve architecture dependencies
* Extract and normalize annotations
* Validate deterministic design
* Process context directives, human-in-the-loop constructs, and resource blocks
* Produce a **normalized semantic model for code generation**

### Determinism Requirement (GASD §1.2.1)

The Semantic AST **MUST** guarantee:

```
same GASD source → same Semantic AST → same generated code
```

This is achieved through symbol resolution, canonical ordering, normalized generics, and deterministic hashing.

---

# User Story 1 — Semantic AST Class Model Design

**Story ID:** US-SEMAST-001
**Epic:** EPIC-SEMAST-001

### User Story

As a **compiler architect**,
I want a **complete semantic class model covering 60+ node types across all GASD language domains**,
So that the GASD transpiler can represent **all language constructs in a deterministic, fully-typed form**.

### Domain Architecture

The Semantic AST is composed of **eight primary domains**:

```
SemanticModel
 ├── DirectiveSystem       (CONTEXT, TARGET, TRACE, NAMESPACE, IMPORT)
 ├── TypeSystem             (TYPE definitions, fields, annotations)
 ├── Architecture           (COMPONENT, INTERFACE, dependencies)
 ├── FlowGraph              (FLOW definitions, steps, control flow)
 ├── StrategySystem          (STRATEGY definitions, invocations)
 ├── DecisionSystem          (DECISION, CHOSEN, AFFECTS)
 ├── ConstraintSystem        (CONSTRAINT, INVARIANT, ENSURE)
 ├── HumanInTheLoopSystem    (QUESTION, APPROVE, TODO, REVIEW)
 └── ResourceSystem          (RESOURCES block)
```

---

### Acceptance Criteria

| ID                | Criteria                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| AC-SEMAST-001-01  | A `SemanticModel` root node exists containing all domain sub-trees.                                    |
| AC-SEMAST-001-02  | Core model nodes are defined: `CompilationUnit`, `NamespaceNode`, `ImportNode`, `MetadataNode`, `SourceLocation`, `AnnotationNode`, `ConstraintNode`. |
| AC-SEMAST-001-03  | Type system nodes cover all GASD types: `TypeSymbol`, `PrimitiveType`, `GenericType`, `OptionalType`, `LiteralType`, `ListType`, `MapType`, `EnumType`, `AliasType`, `UnionType`, `IntersectionType`. |
| AC-SEMAST-001-04  | `LiteralType` supports both string literals (`"Review"`) and numeric literals (`404`) per §5.2.        |
| AC-SEMAST-001-05  | Field-level nodes include `FieldSymbol`, `FieldConstraint`, `FieldAnnotation`.                        |
| AC-SEMAST-001-06  | TYPE-level nodes include `TypeConstraint`, `TypeAnnotation`, `TypeValidator`.                         |
| AC-SEMAST-001-07  | Architecture nodes include `ComponentSymbol`, `ComponentDependency`, `ComponentInterface`, `ComponentMethod`, `ComponentAnnotation`, `ResourceNode`, `RepositoryNode`, `ExternalServiceNode`. |
| AC-SEMAST-001-08  | Dependency wiring nodes include `DependencyGraph`, `InjectionPoint`, `ServiceBinding`.                |
| AC-SEMAST-001-09  | Flow graph nodes include `FlowSymbol`, `FlowParameter`, `FlowReturnType`, `FlowStep`.                |
| AC-SEMAST-001-10  | All 16 flow step subclasses are defined: `ValidateStep`, `EnsureStep`, `AchieveStep`, `CreateStep`, `PersistStep`, `TransformStep`, `UpdateStep`, `ApplyStep`, `ThrowStep`, `ReturnStep`, `MatchStep`, `IfStep`, `LogStep`, `CallStep`, `AssignStep`. |
| AC-SEMAST-001-11  | Flow control-flow nodes include `ConditionNode`, `MatchCaseNode`, `MatchPatternNode`, `ContainsPatternNode`, `OrPatternNode`, `DefaultCaseNode`, `ElseBranchNode`, `OnErrorNode`. |
| AC-SEMAST-001-12  | Flow expression nodes include `TransformExpressionNode` for `TRANSFORM(value, @annotation)` syntax and `StepReferenceNode` for `result_of(step N)` cross-step references. |
| AC-SEMAST-001-13  | Strategy nodes include `StrategySymbol`, `StrategyParameter`, `StrategyReturnType`, `StrategyBody`, `AlgorithmAnnotation`, `StrategyInvocation`, `PreconditionNode`, `ComplexityNode`, `SortKeyNode`. |
| AC-SEMAST-001-14  | Decision system nodes include `DecisionNode`, `DecisionChoice`, `DecisionImpact`, `DecisionReference`, `DecisionScope`, `DecisionAlternatives`. |
| AC-SEMAST-001-15  | Constraint & invariant nodes include `ConstraintRule`, `InvariantRule`, `EnsureRule`, `ValidationRule`, `ContractRule`. |
| AC-SEMAST-001-16  | Expression nodes include `ExpressionNode`, `BinaryExpression`, `UnaryExpression`, `LiteralExpression`, `VariableExpression`, `FunctionExpression`, `MemberAccessExpression`. |
| AC-SEMAST-001-17  | Directive nodes include `ContextDirectiveNode`, `TargetDirectiveNode`, `TraceDirectiveNode`.           |
| AC-SEMAST-001-18  | Human-in-the-loop nodes include `QuestionNode`, `ApproveNode`, `TodoNode`, `ReviewNode`.              |
| AC-SEMAST-001-19  | Resource system nodes include `ResourceBlockNode`, `ResourceItemNode`.                                |
| AC-SEMAST-001-20  | Documentation comment node `DocCommentNode` captures `///` comments with embedded `@trace` references. |
| AC-SEMAST-001-21  | Total node types across all domains is ≥ 65.                                                          |

---

### Acceptance Tests

| Test ID            | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| AT-SEMAST-001-01   | `SemanticModel` can be instantiated with all domain sub-trees.                  |
| AT-SEMAST-001-02   | Each core node type (`CompilationUnit`, `NamespaceNode`, etc.) can be created and attached to the model. |
| AT-SEMAST-001-03   | All 11 type system nodes can represent their corresponding GASD type constructs. |
| AT-SEMAST-001-04   | A string literal type (`"Review"`) produces a `LiteralType` node with exact-match contract. |
| AT-SEMAST-001-05   | A numeric literal type (`404`) produces a `LiteralType` node with exact-match contract. |
| AT-SEMAST-001-06   | All 16 flow step subclasses correctly inherit from `FlowStep`.                  |
| AT-SEMAST-001-07   | `OnErrorNode` correctly attaches to `AchieveStep` as an error-handling child.   |
| AT-SEMAST-001-08   | Architecture dependency wiring correctly links `ComponentSymbol` nodes via `DependencyGraph`. |
| AT-SEMAST-001-09   | Expression nodes support nested compositions (e.g., `BinaryExpression` with `MemberAccessExpression` children). |
| AT-SEMAST-001-10   | Strategy and decision nodes correctly reference each other via `DecisionReference`. |
| AT-SEMAST-001-11   | `DocCommentNode` captures `///` comment text and embedded `@trace` references.  |

---

### Regression Tests

| Test ID            | Description                                                                        |
| ------------------ | ---------------------------------------------------------------------------------- |
| RT-SEMAST-001-01   | Adding new node types does not break existing node hierarchies.                    |
| RT-SEMAST-001-02   | Existing node serialization formats remain backward-compatible after model changes. |

---

# User Story 2 — Symbol Resolution

**Story ID:** US-SEMAST-002
**Epic:** EPIC-SEMAST-001

### User Story

As a **compiler architect**,
I want the semantic pass to **resolve all symbol references in the AST**,
So that every identifier in a GASD file is bound to its defining declaration.

---

### Acceptance Criteria

| ID                | Criteria                                                                              |
| ----------------- | ------------------------------------------------------------------------------------- |
| AC-SEMAST-002-01  | All TYPE references within FLOW parameters, return types, and fields resolve to their defining `TypeSymbol`. |
| AC-SEMAST-002-02  | All COMPONENT references in dependency declarations resolve to their defining `ComponentSymbol`. |
| AC-SEMAST-002-03  | All STRATEGY invocations resolve to their defining `StrategySymbol`.                  |
| AC-SEMAST-002-04  | All DECISION references in FLOW steps resolve to their defining `DecisionNode`.       |
| AC-SEMAST-002-05  | Unresolved references produce a semantic error with file, line, and context information. |
| AC-SEMAST-002-06  | IMPORT statements are processed and resolve symbols from external namespaces.         |
| AC-SEMAST-002-07  | Alias imports are resolved correctly (e.g., `IMPORT X AS Y`).                         |

---

### Acceptance Tests

| Test ID            | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| AT-SEMAST-002-01   | A FLOW parameter referencing a defined TYPE resolves correctly.           |
| AT-SEMAST-002-02   | A FLOW step referencing an undefined TYPE produces a semantic error.      |
| AT-SEMAST-002-03   | A COMPONENT dependency referencing another defined COMPONENT resolves.    |
| AT-SEMAST-002-04   | A STRATEGY invocation referencing a defined STRATEGY resolves correctly.  |
| AT-SEMAST-002-05   | A DECISION reference in a FLOW resolves to the correct DECISION node.    |
| AT-SEMAST-002-06   | An IMPORT statement correctly brings external symbols into scope.         |
| AT-SEMAST-002-07   | Duplicate IMPORT of the same symbol produces a warning.                   |
| AT-SEMAST-002-08   | Alias imports resolve to the correct original symbol.                     |

---

### Regression Tests

| Test ID            | Description                                                               |
| ------------------ | ------------------------------------------------------------------------- |
| RT-SEMAST-002-01   | Existing valid symbol references continue to resolve after parser updates.|
| RT-SEMAST-002-02   | Error messages for unresolved references remain stable in format.         |

---

# User Story 3 — TYPE Contract Binding

**Story ID:** US-SEMAST-003
**Epic:** EPIC-SEMAST-001

### User Story

As a **GASD specification author**,
I want the semantic layer to **bind TYPE contracts to FLOW logic via `VALIDATE AS TYPE.X`**,
So that FLOW steps enforce type constraints and produce type-safe generated code.

---

### Acceptance Criteria

| ID                | Criteria                                                                                  |
| ----------------- | ----------------------------------------------------------------------------------------- |
| AC-SEMAST-003-01  | `VALIDATE AS TYPE.X` binds the step to the corresponding TYPE definition and field.        |
| AC-SEMAST-003-02  | Field-level annotations (`@range`, `@min_length`, `@max_length`, `@format`, `@unique`, `@default`) are propagated to the bound FLOW step. |
| AC-SEMAST-003-03  | TYPE-level constraints (`TypeConstraint`, `TypeValidator`) are enforced at the step level.  |
| AC-SEMAST-003-04  | Missing or invalid TYPE binding produces a semantic error with context.                    |
| AC-SEMAST-003-05  | `VALIDATE` without `AS TYPE.X` produces a semantic error per §5.3 / GEP-5.                |
| AC-SEMAST-003-06  | Generic type bindings (e.g., `List<T>`, `Map<K,V>`) resolve correctly in FLOW steps.       |
| AC-SEMAST-003-07  | A TYPE with `@annotations` but no VALIDATE binding produces a transpiler warning: "TYPE X has @annotations but no VALIDATE binding" (§5.3). |
| AC-SEMAST-003-08  | Multiple FLOWs MAY validate the same TYPE; each becomes a specialized enforcer.            |

---

### Acceptance Tests

| Test ID            | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| AT-SEMAST-003-01   | `VALIDATE email AS TYPE.EmailAddress` correctly binds to the TYPE definition.   |
| AT-SEMAST-003-02   | Field annotations from the TYPE propagate to the semantic FLOW step.            |
| AT-SEMAST-003-03   | A `VALIDATE` step referencing a non-existent TYPE produces a semantic error.     |
| AT-SEMAST-003-04   | A `VALIDATE` step referencing a non-existent field on a valid TYPE produces an error. |
| AT-SEMAST-003-05   | A `VALIDATE` step without `AS TYPE.X` produces a semantic error.                |
| AT-SEMAST-003-06   | Generic type bindings resolve and propagate constraints correctly.               |
| AT-SEMAST-003-07   | A TYPE with `@format` but no FLOW binding produces a warning.                   |
| AT-SEMAST-003-08   | Two FLOWs both binding `VALIDATE AS TYPE.EmailAddress` resolve independently.   |

---

### Regression Tests

| Test ID            | Description                                                                      |
| ------------------ | -------------------------------------------------------------------------------- |
| RT-SEMAST-003-01   | Existing TYPE-bound FLOW steps remain valid after TYPE definition changes.        |
| RT-SEMAST-003-02   | Annotation propagation behavior does not change for existing valid specifications.|

---

# User Story 4 — Annotation Extraction & Normalization

**Story ID:** US-SEMAST-004
**Epic:** EPIC-SEMAST-001

### User Story

As a **compiler architect**,
I want the semantic pass to **extract, normalize, and canonically order all annotations from the Standard Annotation Library (§14)**,
So that annotations are deterministically represented regardless of source ordering.

---

### Acceptance Criteria

| ID                | Criteria                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------- |
| AC-SEMAST-004-01  | All annotations from §14.1 Data Validation are recognized: `@range`, `@min_length`, `@max_length`, `@format`, `@unique`, `@default`. |
| AC-SEMAST-004-02  | All annotations from §14.2 Architectural Directives are recognized: `@injectable`, `@mockable`, `@optimize`, `@transaction_type`. |
| AC-SEMAST-004-03  | All annotations from §14.3 Implementation Modifiers are recognized: `@async`, `@external`, `@error_strategy`, `@algorithm`, `@hash`. |
| AC-SEMAST-004-04  | All annotations from §14.4 Metadata & Lifecycle are recognized: `@trace`, `@status`, `@agent_note`, `@heuristic`. |
| AC-SEMAST-004-05  | All annotations from §14.5 Extended Library are recognized: `@sensitive`, `@authorized`, `@mask`, `@retry`, `@timeout`, `@circuit_breaker`, `@metric`, `@trace_id`, `@cacheable`, `@idempotent`, `@index`, `@transient`, `@deprecated`, `@rest`. |
| AC-SEMAST-004-06  | Additional spec-referenced annotations are recognized: `@testable`, `@constraint`, `@auto_generate`, `@pattern`. |
| AC-SEMAST-004-07  | Annotations with scoped parameters (e.g., `@unique(scope: UserRepository)`) have their scope references resolved. |
| AC-SEMAST-004-08  | Annotations are sorted by a canonical key (alphabetical by annotation name).                 |
| AC-SEMAST-004-09  | Duplicate annotations on the same element produce a semantic warning.                        |
| AC-SEMAST-004-10  | Annotations with parameters have their arguments validated where applicable.                 |
| AC-SEMAST-004-11  | Annotation ordering in the source does not affect the semantic hash (see US-SEMAST-010).      |

---

### Acceptance Tests

| Test ID            | Description                                                                          |
| ------------------ | ------------------------------------------------------------------------------------ |
| AT-SEMAST-004-01   | Each annotation from §14.1–§14.5 is correctly extracted from a GASD source file.     |
| AT-SEMAST-004-02   | `@agent_note` and `@heuristic` metadata annotations are extracted and attached.      |
| AT-SEMAST-004-03   | Annotations declared in reverse order produce the same canonical ordering.            |
| AT-SEMAST-004-04   | Duplicate annotation on a field produces a warning.                                   |
| AT-SEMAST-004-05   | An annotation with an invalid parameter value produces an error.                      |
| AT-SEMAST-004-06   | `@auto_generate` on a DateTime field is correctly extracted.                          |

---

### Regression Tests

| Test ID            | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| RT-SEMAST-004-01   | Adding a new annotation type does not affect canonicalization of existing ones.  |
| RT-SEMAST-004-02   | Annotation extraction remains stable across parser grammar updates.             |

---

# User Story 5 — Architecture Dependency Validation

**Story ID:** US-SEMAST-005
**Epic:** EPIC-SEMAST-001

### User Story

As a **software architect using GASD**,
I want the semantic pass to **validate all architecture dependencies between COMPONENTs**,
So that the design specification has verified, conflict-free wiring before code generation.

---

### Acceptance Criteria

| ID                | Criteria                                                                               |
| ----------------- | -------------------------------------------------------------------------------------- |
| AC-SEMAST-005-01  | `ComponentDependency` declarations resolve to defined `ComponentSymbol` nodes.          |
| AC-SEMAST-005-02  | Interface methods on components are validated against referenced types (including `Optional<T>`, `List<T>`, `Map<K,V>` return types). |
| AC-SEMAST-005-03  | Circular component dependencies are detected and produce a semantic error.               |
| AC-SEMAST-005-04  | `RepositoryNode` and `ExternalServiceNode` references resolve correctly.                 |
| AC-SEMAST-005-05  | A complete `DependencyGraph` is constructed representing all component relationships.    |
| AC-SEMAST-005-06  | `PATTERN` field on COMPONENT is captured in the semantic model.                          |
| AC-SEMAST-005-07  | COMPONENT-level annotations (per formal syntax `COMPONENT Name [Annotations]:`) are extracted and attached. |

---

### Acceptance Tests

| Test ID            | Description                                                                          |
| ------------------ | ------------------------------------------------------------------------------------ |
| AT-SEMAST-005-01   | A COMPONENT declaring a DEPENDENCY on another defined COMPONENT resolves correctly.   |
| AT-SEMAST-005-02   | A COMPONENT declaring a DEPENDENCY on an undefined COMPONENT produces an error.       |
| AT-SEMAST-005-03   | A circular dependency chain (A→B→C→A) is detected and reported.                       |
| AT-SEMAST-005-04   | A COMPONENT interface method referencing a defined TYPE resolves.                      |
| AT-SEMAST-005-05   | A COMPONENT interface method with `Optional<User>` return type resolves the generic.  |
| AT-SEMAST-005-06   | The `DependencyGraph` correctly reflects all declared wiring.                         |
| AT-SEMAST-005-07   | `PATTERN: "Repository"` is captured on the `ComponentSymbol` node.                    |
| AT-SEMAST-005-08   | `@injectable` and `@mockable` on a COMPONENT are extracted and attached.              |

---

### Regression Tests

| Test ID            | Description                                                                        |
| ------------------ | ---------------------------------------------------------------------------------- |
| RT-SEMAST-005-01   | Existing valid dependency resolutions remain intact after architecture changes.     |
| RT-SEMAST-005-02   | Circular dependency detection does not produce false positives on valid graphs.     |

---

# User Story 6 — FLOW Semantic Analysis

**Story ID:** US-SEMAST-006
**Epic:** EPIC-SEMAST-001

### User Story

As a **GASD specification author**,
I want the semantic pass to **fully analyze FLOW definitions, resolving all step types, control-flow constructs, and their references**,
So that generated code accurately implements the specified business logic.

---

### Acceptance Criteria

| ID                | Criteria                                                                                        |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| AC-SEMAST-006-01  | All 16 FLOW step types are semantically resolved: `VALIDATE`, `ENSURE`, `ACHIEVE`, `CREATE`, `PERSIST`, `TRANSFORM`, `UPDATE`, `APPLY`, `THROW`, `RETURN`, `MATCH`, `IF`, `LOG`, `CALL`, `ASSIGN`. |
| AC-SEMAST-006-02  | Each FLOW step with a type reference has that reference resolved to its defining `TypeSymbol`.    |
| AC-SEMAST-006-03  | Invalid references in FLOW steps produce a semantic error with step location.                    |
| AC-SEMAST-006-04  | FLOW-level annotations (`@pattern`, `@error_strategy`, `@async`, etc.) are extracted and attached to the `FlowSymbol` node. |
| AC-SEMAST-006-05  | Step-level annotations are extracted and attached to the corresponding `FlowStep` node.          |
| AC-SEMAST-006-06  | `ENSURE ... OTHERWISE` is resolved as a control-flow construct: the condition is captured in a `ConditionNode`, and the `OTHERWISE` action (e.g., `THROW`) is captured as a nested action node. |
| AC-SEMAST-006-07  | `ON_ERROR` clauses within `ACHIEVE` blocks are resolved as `OnErrorNode` children with their nested action (e.g., `THROW`). |
| AC-SEMAST-006-08  | `ACHIEVE` blocks with property assignments (e.g., `payment_id = result_of(step 3)`) produce `StepReferenceNode` cross-references. |
| AC-SEMAST-006-09  | `CREATE` blocks resolve field assignments, including `TRANSFORM(value, @annotation)` expressions producing `TransformExpressionNode`. |
| AC-SEMAST-006-10  | `PERSIST entity via Repository` resolves the repository reference to its `ComponentSymbol`.       |
| AC-SEMAST-006-11  | `MATCH` blocks produce correctly nested `MatchCaseNode` children.                                |
| AC-SEMAST-006-12  | MATCH OR patterns (`"admin" \| "superadmin" -> ...`) produce `OrPatternNode` with multiple child patterns per §11. |
| AC-SEMAST-006-13  | MATCH `CONTAINS` keyword pattern (`CONTAINS "manager" -> ...`) produces a `ContainsPatternNode` per §11. |
| AC-SEMAST-006-14  | MATCH `DEFAULT` case (`DEFAULT -> ...`) produces a `DefaultCaseNode` per §11.                    |
| AC-SEMAST-006-15  | `IF` blocks with `ELSE` branches produce correctly nested `ConditionNode` and `ElseBranchNode` trees. |
| AC-SEMAST-006-16  | FLOW parameters and return types are validated against defined TYPEs.                            |
| AC-SEMAST-006-17  | FLOW step numbering is captured and deterministically ordered in the semantic model.              |

---

### Acceptance Tests

| Test ID            | Description                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| AT-SEMAST-006-01   | A FLOW containing all 16 step types parses and resolves without errors.                 |
| AT-SEMAST-006-02   | A `VALIDATE` step with a valid TYPE reference resolves correctly.                       |
| AT-SEMAST-006-03   | A `CALL` step referencing an undefined FLOW produces a semantic error.                  |
| AT-SEMAST-006-04   | `ENSURE uniqueness(email) OTHERWISE THROW ConflictException` produces a `ConditionNode` with a nested `ThrowStep`. |
| AT-SEMAST-006-05   | `ACHIEVE "Create payment" ON_ERROR: THROW BadGatewayException` produces an `OnErrorNode` child with `ThrowStep`. |
| AT-SEMAST-006-06   | `CREATE User: password_hash = TRANSFORM(password, @hash("bcrypt"))` produces a `TransformExpressionNode`. |
| AT-SEMAST-006-07   | `PERSIST User via UserRepository` resolves `UserRepository` to its `ComponentSymbol`.   |
| AT-SEMAST-006-08   | `payment_id = result_of(step 3)` produces a `StepReferenceNode` pointing to step 3.    |
| AT-SEMAST-006-09   | A `MATCH` block with `"admin" \| "superadmin" -> ACHIEVE "Grant full access"` produces an `OrPatternNode`. |
| AT-SEMAST-006-10   | A `MATCH` block with `CONTAINS "manager" -> ...` produces a `ContainsPatternNode`.      |
| AT-SEMAST-006-11   | A `MATCH` block with `DEFAULT -> THROW UnauthorizedException` produces a `DefaultCaseNode`. |
| AT-SEMAST-006-12   | An `IF` block with an `ELSE` branch produces a correct `ElseBranchNode`.               |
| AT-SEMAST-006-13   | FLOW-level `@pattern("Service Method")` and `@error_strategy("Exception-based")` are attached to the `FlowSymbol`. |
| AT-SEMAST-006-14   | Step-level annotations (e.g., `@async` on `ACHIEVE`) are correctly attached.           |

---

### Regression Tests

| Test ID            | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| RT-SEMAST-006-01   | Existing valid FLOW definitions remain semantically valid after updates.           |
| RT-SEMAST-006-02   | Step resolution behavior does not change for established test fixtures.            |

---

# User Story 7 — Strategy Resolution

**Story ID:** US-SEMAST-007
**Epic:** EPIC-SEMAST-001

### User Story

As a **compiler architect**,
I want the semantic pass to **resolve STRATEGY definitions, their sub-fields, and invocations**,
So that algorithm-level constructs are correctly bound and available for code generation.

---

### Acceptance Criteria

| ID                | Criteria                                                                                |
| ----------------- | --------------------------------------------------------------------------------------- |
| AC-SEMAST-007-01  | `StrategySymbol` definitions are registered in the symbol table.                         |
| AC-SEMAST-007-02  | `StrategyInvocation` references resolve to a defined `StrategySymbol`.                   |
| AC-SEMAST-007-03  | `@algorithm` annotations on strategies are extracted and validated.                      |
| AC-SEMAST-007-04  | Generic strategies resolve type parameters correctly.                                    |
| AC-SEMAST-007-05  | Invalid strategy references produce a semantic error with location context.              |
| AC-SEMAST-007-06  | `PRECONDITION` field is captured as a `PreconditionNode` on the strategy (§8).           |
| AC-SEMAST-007-07  | `COMPLEXITY` field is captured as a `ComplexityNode` on the strategy (§8).               |
| AC-SEMAST-007-08  | `SORT_KEY` and `ORDER` fields are captured as a `SortKeyNode` on the strategy (§8).      |
| AC-SEMAST-007-09  | `INPUT` and `OUTPUT` fields resolve their type references to defined `TypeSymbol` nodes.  |

---

### Acceptance Tests

| Test ID            | Description                                                                    |
| ------------------ | ------------------------------------------------------------------------------ |
| AT-SEMAST-007-01   | A STRATEGY definition is correctly registered in the symbol table.              |
| AT-SEMAST-007-02   | A STRATEGY invocation referencing a defined STRATEGY resolves.                  |
| AT-SEMAST-007-03   | A STRATEGY invocation referencing an undefined STRATEGY produces an error.      |
| AT-SEMAST-007-04   | An `@algorithm` annotation on a STRATEGY is correctly extracted.                |
| AT-SEMAST-007-05   | A generic STRATEGY resolves type parameters from invocation context.            |
| AT-SEMAST-007-06   | `PRECONDITION: input IS_SORTED` produces a `PreconditionNode`.                  |
| AT-SEMAST-007-07   | `COMPLEXITY: O(log n) time, O(1) space` produces a `ComplexityNode`.            |
| AT-SEMAST-007-08   | `SORT_KEY: User.created_at` with `ORDER: ASCENDING` produces a `SortKeyNode`.   |
| AT-SEMAST-007-09   | `INPUT: sorted_list: List<Comparable>` resolves `List<Comparable>` type reference. |

---

### Regression Tests

| Test ID            | Description                                                                    |
| ------------------ | ------------------------------------------------------------------------------ |
| RT-SEMAST-007-01   | Existing strategy resolutions remain valid after adding new strategies.         |
| RT-SEMAST-007-02   | Strategy resolution error messages remain stable in format.                    |

---

# User Story 8 — Decision System Resolution

**Story ID:** US-SEMAST-008
**Epic:** EPIC-SEMAST-001

### User Story

As a **software architect using GASD**,
I want the semantic pass to **resolve DECISION definitions, CHOSEN options, and AFFECTS references**,
So that architectural decisions are traceable across the design and code generation.

---

### Acceptance Criteria

| ID                | Criteria                                                                                           |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| AC-SEMAST-008-01  | `DecisionNode` definitions are registered in the symbol table.                                      |
| AC-SEMAST-008-02  | `DecisionChoice` children represent each option with a CHOSEN marker.                               |
| AC-SEMAST-008-03  | `RATIONALE` text is captured on the `DecisionNode`.                                                 |
| AC-SEMAST-008-04  | `ALTERNATIVES` list is captured as `DecisionAlternatives` child nodes per §4 formal syntax.         |
| AC-SEMAST-008-05  | `DecisionImpact` / `AFFECTS` references resolve to valid COMPONENTs, FLOWs, TYPEs, or member paths (e.g., `User.password_hash`). |
| AC-SEMAST-008-06  | `AFFECTS: [*]` (wildcard) is resolved as impacting all elements in scope.                           |
| AC-SEMAST-008-07  | DECISION-level annotations (per formal syntax `DECISION "name" [Annotations]:`) are extracted.      |
| AC-SEMAST-008-08  | Cross-flow decision impact is tracked (a DECISION affecting multiple FLOWs).                        |
| AC-SEMAST-008-09  | Invalid DECISION references produce a semantic error.                                               |

---

### Acceptance Tests

| Test ID            | Description                                                                          |
| ------------------ | ------------------------------------------------------------------------------------ |
| AT-SEMAST-008-01   | A DECISION with ALTERNATIVES and a CHOSEN option resolves correctly.                  |
| AT-SEMAST-008-02   | `RATIONALE` text is captured on the semantic DECISION node.                           |
| AT-SEMAST-008-03   | `ALTERNATIVES: ["Error codes", "Result monad"]` produces `DecisionAlternatives` nodes.|
| AT-SEMAST-008-04   | An `AFFECTS` clause referencing a defined COMPONENT resolves.                         |
| AT-SEMAST-008-05   | An `AFFECTS` clause referencing a member path (`User.password_hash`) resolves.        |
| AT-SEMAST-008-06   | An `AFFECTS: [*]` clause is resolved as a wildcard impact.                            |
| AT-SEMAST-008-07   | An `AFFECTS` clause referencing an undefined element produces an error.                |
| AT-SEMAST-008-08   | A DECISION impacting multiple FLOWs is correctly tracked in the semantic model.        |
| AT-SEMAST-008-09   | An invalid DECISION reference in a FLOW step produces a semantic error.                |

---

### Regression Tests

| Test ID            | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| RT-SEMAST-008-01   | Existing decision resolutions remain valid after model changes.                   |
| RT-SEMAST-008-02   | `AFFECTS` cross-references remain stable across versions.                         |

---

# User Story 9 — Namespace & Import Resolution

**Story ID:** US-SEMAST-009
**Epic:** EPIC-SEMAST-001

### User Story

As a **GASD specification author**,
I want the semantic pass to **resolve IMPORT statements and namespace scoping**,
So that multi-file GASD projects have correct symbol visibility across modules.

---

### Acceptance Criteria

| ID                | Criteria                                                                              |
| ----------------- | ------------------------------------------------------------------------------------- |
| AC-SEMAST-009-01  | IMPORT statements resolve symbols from external GASD files into the local scope.       |
| AC-SEMAST-009-02  | Alias imports (e.g., `IMPORT "payment_service.gasd" AS Payment`) bind correctly.       |
| AC-SEMAST-009-03  | Duplicate imports of the same symbol produce a warning.                                |
| AC-SEMAST-009-04  | Namespace collisions (same symbol name from different imports) produce a semantic error.|
| AC-SEMAST-009-05  | Cyclic imports are detected and produce a semantic error.                              |

---

### Acceptance Tests

| Test ID            | Description                                                                  |
| ------------------ | ---------------------------------------------------------------------------- |
| AT-SEMAST-009-01   | An IMPORT of a TYPE from another file resolves correctly.                     |
| AT-SEMAST-009-02   | An alias import resolves to the original symbol.                              |
| AT-SEMAST-009-03   | Importing the same symbol twice produces a warning.                           |
| AT-SEMAST-009-04   | Importing two symbols with the same name from different files produces an error.|
| AT-SEMAST-009-05   | A cyclic import chain (A→B→A) is detected and reported.                       |

---

### Regression Tests

| Test ID            | Description                                                                           |
| ------------------ | ------------------------------------------------------------------------------------- |
| RT-SEMAST-009-01   | Existing multi-file resolutions remain valid after import handling changes.            |
| RT-SEMAST-009-02   | Alias import behavior does not regress.                                               |

---

# User Story 10 — Deterministic Semantic Hashing

**Story ID:** US-SEMAST-010
**Epic:** EPIC-SEMAST-001

### User Story

As a **CI/CD pipeline engineer**,
I want the semantic layer to produce a **deterministic SHA-256 hash of the Semantic AST**,
So that build reproducibility, cache correctness, and CI determinism can be verified.

### Hashing Goal

```
identical GASD input → identical semantic hash
```

### Canonical Serialization

The semantic model is serialized into a **canonical JSON-like structure** before hashing.

Example:

```json
{
  "type": "Flow",
  "name": "register_user",
  "parameters": [
     { "name": "email", "type": "EmailAddress" }
  ],
  "steps": [
     { "type": "ValidateStep", "target": "email", "typeBinding": "EmailAddress" }
  ]
}
```

### Canonical Ordering Rules

The following elements must be sorted by `symbol.name`:

* types
* components
* flows
* strategies
* decisions
* annotations
* fields
* dependencies

### Hash Algorithm

**Recommended:** SHA-256

**Procedure:**

1. Build Semantic AST
2. Normalize ordering
3. Canonical serialize
4. Compute SHA-256

**Pseudo-code:**

```python
def semantic_hash(model):
    normalized = normalize(model)
    serialized = canonical_serialize(normalized)
    return sha256(serialized)
```

---

### Acceptance Criteria

| ID                | Criteria                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| AC-SEMAST-010-01  | A SHA-256 hash is computed from the canonically serialized Semantic AST.                         |
| AC-SEMAST-010-02  | The same GASD source always produces the same semantic hash.                                     |
| AC-SEMAST-010-03  | Whitespace differences in the source do not affect the semantic hash.                            |
| AC-SEMAST-010-04  | Different annotation ordering in the source does not affect the semantic hash.                   |
| AC-SEMAST-010-05  | Different file processing order does not affect the semantic hash.                               |
| AC-SEMAST-010-06  | A semantic change in the source (e.g., adding a FLOW step) produces a different hash.            |
| AC-SEMAST-010-07  | The hash is stable across transpiler versions given the same semantic pass.                       |

---

### Acceptance Tests

| Test ID            | Description                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------- |
| AT-SEMAST-010-01   | Parsing the same file twice produces the same semantic hash.                              |
| AT-SEMAST-010-02   | A GASD file with extra whitespace produces the same hash as the compact version.          |
| AT-SEMAST-010-03   | A GASD file with reordered annotations produces the same hash.                            |
| AT-SEMAST-010-04   | Processing files in different order produces the same hash.                               |
| AT-SEMAST-010-05   | Adding a new FLOW step produces a different hash.                                         |
| AT-SEMAST-010-06   | `FLOW f(): RETURN 1` always produces a known golden hash.                                 |

---

### Regression Tests

| Test ID            | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| RT-SEMAST-010-01   | Golden hashes for existing test files remain unchanged across updates.             |
| RT-SEMAST-010-02   | Normalization rules do not regress when new node types are added.                  |

---

# User Story 11 — CI/CD Determinism Validation

**Story ID:** US-SEMAST-011
**Epic:** EPIC-SEMAST-001

### User Story

As a **CI/CD pipeline engineer**,
I want the build pipeline to **compare the semantic hash against a golden hash and fail on mismatch**,
So that non-deterministic transpiler behavior is caught before deployment.

---

### Acceptance Criteria

| ID                | Criteria                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| AC-SEMAST-011-01  | A CI step compiles the GASD source and computes the semantic hash.                              |
| AC-SEMAST-011-02  | The computed hash is compared against a stored golden hash.                                     |
| AC-SEMAST-011-03  | A hash mismatch causes the build to **FAIL**.                                                   |
| AC-SEMAST-011-04  | A hash match allows the build to proceed.                                                       |

---

### Acceptance Tests

| Test ID            | Description                                                                        |
| ------------------ | ---------------------------------------------------------------------------------- |
| AT-SEMAST-011-01   | A matching golden hash allows the CI build to pass.                                |
| AT-SEMAST-011-02   | A mismatched golden hash causes the CI build to fail.                              |
| AT-SEMAST-011-03   | The golden hash can be updated when intentional semantic changes are made.          |

---

### Regression Tests

| Test ID            | Description                                                                   |
| ------------------ | ----------------------------------------------------------------------------- |
| RT-SEMAST-011-01   | CI determinism checks remain functional after pipeline configuration changes. |

---

# User Story 12 — Semantic Error Reporting

**Story ID:** US-SEMAST-012
**Epic:** EPIC-SEMAST-001

### User Story

As a **GASD specification author**,
I want the semantic pass to produce **clear, actionable error messages with file, line, and context information**,
So that I can quickly locate and fix semantic issues in my specifications.

---

### Acceptance Criteria

| ID                | Criteria                                                                               |
| ----------------- | -------------------------------------------------------------------------------------- |
| AC-SEMAST-012-01  | Every semantic error includes the source file path.                                     |
| AC-SEMAST-012-02  | Every semantic error includes the line number and column (where available).              |
| AC-SEMAST-012-03  | Every semantic error includes contextual information (e.g., "in FLOW `register_user`"). |
| AC-SEMAST-012-04  | Errors are machine-readable (structured format for tooling integration).                |
| AC-SEMAST-012-05  | Warnings are distinguished from errors in severity level.                               |

---

### Acceptance Tests

| Test ID            | Description                                                                        |
| ------------------ | ---------------------------------------------------------------------------------- |
| AT-SEMAST-012-01   | An unresolved TYPE reference error shows file path and line number.                 |
| AT-SEMAST-012-02   | A duplicate symbol warning includes the location of both declarations.              |
| AT-SEMAST-012-03   | Error output can be parsed by an automated tool (e.g., JSON or structured format). |

---

### Regression Tests

| Test ID            | Description                                                                  |
| ------------------ | ---------------------------------------------------------------------------- |
| RT-SEMAST-012-01   | Error message formats remain stable for downstream tooling integration.      |
| RT-SEMAST-012-02   | Adding new semantic checks does not alter the format of existing error types. |

---

# User Story 13 — Context & Directive Resolution

**Story ID:** US-SEMAST-013
**Epic:** EPIC-SEMAST-001

### User Story

As a **compiler architect**,
I want the semantic pass to **resolve CONTEXT, TARGET, and TRACE directives**,
So that transpiler behavior is correctly driven by the file's global settings and upstream traceability is maintained.

### Spec Reference

Per §3, a GASD file **MUST** begin with `CONTEXT` and `TARGET` directives. `TRACE` links the design to upstream SRS requirements or Agile artifacts.

---

### Acceptance Criteria

| ID                | Criteria                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| AC-SEMAST-013-01  | `CONTEXT` directive is captured as a `ContextDirectiveNode` in the semantic model.              |
| AC-SEMAST-013-02  | `TARGET` directive is captured as a `TargetDirectiveNode` in the semantic model.                |
| AC-SEMAST-013-03  | A GASD file missing `CONTEXT` or `TARGET` produces a semantic error per §3.                    |
| AC-SEMAST-013-04  | `TRACE` directives are captured as `TraceDirectiveNode` nodes with their reference IDs.         |
| AC-SEMAST-013-05  | `TRACE` supports both SRS-style (`"SRS-101"`) and Agile-style (`"EPIC-007"`, `"US-042"`, `"AC-042-1"`) identifiers. |
| AC-SEMAST-013-06  | Multiple `TRACE` directives are accumulated (not overwritten) in the semantic model.            |
| AC-SEMAST-013-07  | `NAMESPACE` directive value is captured and validated for dot-separated path format.             |

---

### Acceptance Tests

| Test ID            | Description                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------- |
| AT-SEMAST-013-01   | `CONTEXT: "Spring Boot microservice"` produces a `ContextDirectiveNode` with value "Spring Boot microservice". |
| AT-SEMAST-013-02   | `TARGET: "Java 17"` produces a `TargetDirectiveNode` with value "Java 17".               |
| AT-SEMAST-013-03   | A file without `CONTEXT` produces a semantic error.                                       |
| AT-SEMAST-013-04   | A file without `TARGET` produces a semantic error.                                        |
| AT-SEMAST-013-05   | `TRACE: "SRS-101", "US-042"` produces a `TraceDirectiveNode` with two reference IDs.     |
| AT-SEMAST-013-06   | `NAMESPACE: "com.acme.payment"` is captured and validated.                                |

---

### Regression Tests

| Test ID            | Description                                                                   |
| ------------------ | ----------------------------------------------------------------------------- |
| RT-SEMAST-013-01   | Existing files with valid directives remain semantically valid after changes. |
| RT-SEMAST-013-02   | Directive parsing does not conflict with other top-level constructs.           |

---

# User Story 14 — Human-in-the-Loop Construct Resolution

**Story ID:** US-SEMAST-014
**Epic:** EPIC-SEMAST-001

### User Story

As a **software architect using GASD**,
I want the semantic pass to **resolve QUESTION, APPROVE, TODO, and REVIEW constructs**,
So that human-AI design collaboration markers are represented in the semantic model and can influence downstream tooling.

### Spec Reference

Per §10, these constructs support the AI-human design review cycle. `@status` annotations track lifecycle maturity (`DRAFT` → `REVIEW_REQUIRED` → `APPROVED`), and `@heuristic` / `@agent_note` annotations capture agent reasoning.

---

### Acceptance Criteria

| ID                | Criteria                                                                                           |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| AC-SEMAST-014-01  | `QUESTION` blocks are captured as `QuestionNode` with `BLOCKING` and `CONTEXT` fields.              |
| AC-SEMAST-014-02  | `QUESTION` with `CONTEXT` referencing a COMPONENT method resolves that reference.                   |
| AC-SEMAST-014-03  | `APPROVE` blocks are captured as `ApproveNode` with `STATUS`, `BY`, `DATE`, and `NOTES` fields.     |
| AC-SEMAST-014-04  | `APPROVE` `STATUS` is validated to be one of: `APPROVED`, `REJECTED`.                               |
| AC-SEMAST-014-05  | `TODO` markers are captured as `TodoNode` with their text content.                                  |
| AC-SEMAST-014-06  | `REVIEW` markers are captured as `ReviewNode` with their text content.                              |
| AC-SEMAST-014-07  | `@status("DRAFT" \| "REVIEW_REQUIRED" \| "APPROVED")` on any element is validated for allowed values.|

---

### Acceptance Tests

| Test ID            | Description                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| AT-SEMAST-014-01   | `QUESTION: "Should we support OAuth2?" BLOCKING: true CONTEXT: AuthService.register` resolves. |
| AT-SEMAST-014-02   | `APPROVE "Password Storage": STATUS: APPROVED BY: "Lead Architect" DATE: "2026-02-15"` resolves.|
| AT-SEMAST-014-03   | `APPROVE` with an invalid `STATUS` value (e.g., `"PENDING"`) produces a semantic error.        |
| AT-SEMAST-014-04   | `TODO: "Add rate limiting logic in v2"` is captured as a `TodoNode`.                           |
| AT-SEMAST-014-05   | `REVIEW: "Check if this handles race conditions"` is captured as a `ReviewNode`.               |
| AT-SEMAST-014-06   | `@status("INVALID")` on a COMPONENT produces a validation error.                              |

---

### Regression Tests

| Test ID            | Description                                                                           |
| ------------------ | ------------------------------------------------------------------------------------- |
| RT-SEMAST-014-01   | Existing constructs without human-in-the-loop markers remain unaffected.              |
| RT-SEMAST-014-02   | Adding QUESTION/APPROVE blocks does not alter semantic resolution of other elements.  |

---

# User Story 15 — Resource Block Resolution

**Story ID:** US-SEMAST-015
**Epic:** EPIC-SEMAST-001

### User Story

As a **GASD specification author**,
I want the semantic pass to **resolve RESOURCES blocks and their items**,
So that external references and documentation links are captured in the semantic model for downstream tooling.

### Spec Reference

Per §12, `RESOURCES` is an optional top-level block for external references, documentation links, or architectural assets. Resource items may include annotations such as `@trace(#AC-100)`.

---

### Acceptance Criteria

| ID                | Criteria                                                                                        |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| AC-SEMAST-015-01  | `RESOURCES` block is captured as a `ResourceBlockNode` in the semantic model.                    |
| AC-SEMAST-015-02  | Each resource item is captured as a `ResourceItemNode` with its string value.                    |
| AC-SEMAST-015-03  | Annotations on resource items (e.g., `@trace(#AC-100)`) are extracted and attached.              |
| AC-SEMAST-015-04  | An empty `RESOURCES` block is valid and produces an empty `ResourceBlockNode`.                    |

---

### Acceptance Tests

| Test ID            | Description                                                                          |
| ------------------ | ------------------------------------------------------------------------------------ |
| AT-SEMAST-015-01   | `RESOURCES: - "https://docs.stripe.com/api"` produces a `ResourceItemNode`.          |
| AT-SEMAST-015-02   | `- "System Architecture PDF" @trace(#AC-100)` captures the `@trace` annotation.      |
| AT-SEMAST-015-03   | An empty `RESOURCES:` block produces a valid empty `ResourceBlockNode`.               |

---

### Regression Tests

| Test ID            | Description                                                                   |
| ------------------ | ----------------------------------------------------------------------------- |
| RT-SEMAST-015-01   | Adding RESOURCES blocks does not affect resolution of other top-level elements.|

---

# User Story 16 — `--ast-sem` CLI Option

**Story ID:** US-SEMAST-016
**Epic:** EPIC-SEMAST-001

### User Story

As a **GASD specification author**,
I want a **`--ast-sem` CLI option** that produces the fully resolved Semantic AST in JSON format,
So that I can inspect, debug, and integrate the semantic model into downstream tooling.

### Context

The existing `--ast` option outputs the **syntactic AST** (parse tree structure). The new `--ast-sem` option outputs the **Semantic AST** — a fully resolved model with symbols bound, types validated, and annotations normalized. Both options **MUST coexist** — `--ast` is NOT replaced.

---

### Acceptance Criteria

| ID                | Criteria                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| AC-SEMAST-016-01  | A new `--ast-sem` flag is added to the CLI argument parser.                                     |
| AC-SEMAST-016-02  | `--ast-sem` triggers semantic AST construction after the existing parse + validation pipeline.   |
| AC-SEMAST-016-03  | The semantic AST is exported as JSON to stdout ONLY when the `--json` flag is specified (Silent JSON behavior). |
| AC-SEMAST-016-04  | The existing `--ast` flag continues to output the syntactic AST unchanged.                      |
| AC-SEMAST-016-05  | `--ast` and `--ast-sem` can be used independently or together in a single invocation.            |
| AC-SEMAST-016-06  | When both `--ast` and `--ast-sem` are specified, both outputs are produced (syntactic first, then semantic). |
| AC-SEMAST-016-07  | `--ast-sem` output includes all resolved domain sub-trees: directives, types, components, flows, strategies, decisions, constraints, human-in-the-loop, and resources. |
| AC-SEMAST-016-08  | If parsing or validation fails, `--ast-sem` produces no output and the CLI reports errors normally. |
| AC-SEMAST-016-09  | `--ast-sem` is documented in `--help` output with a clear description.                          |
| AC-SEMAST-016-10  | A new `--json` flag is provided to explicitly enable JSON output to stdout.                     |

---

### Acceptance Tests

| Test ID            | Description                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------- |
| AT-SEMAST-016-01   | `gasd-parser file.gasd --ast-sem --json` outputs semantic AST JSON to stdout.            |
| AT-SEMAST-016-02   | `gasd-parser file.gasd --ast --json` still outputs syntactic AST JSON.                    |
| AT-SEMAST-016-03   | `gasd-parser file.gasd --ast --ast-sem --json` outputs both ASTs.                        |
| AT-SEMAST-016-04   | `gasd-parser file.gasd --ast-sem` on a file with parse errors produces no AST and exits with error code. |
| AT-SEMAST-016-05   | `gasd-parser file.gasd --ast-sem` on a file with semantic errors produces no AST and exits with error code. |
| AT-SEMAST-016-06   | `gasd-parser --help` shows `--ast-sem` in the options list with its description.         |
| AT-SEMAST-016-07   | `--ast-sem` output contains all expected top-level keys (types, components, flows, strategies, decisions, etc.). |

---

### Regression Tests

| Test ID            | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| RT-SEMAST-016-01   | Existing `--ast` output format and content remain unchanged after adding `--ast-sem`. |
| RT-SEMAST-016-02   | CLI exit codes remain unchanged for all existing invocations.                     |

---

# User Story 17 — Backward Compatibility Guarantee

**Story ID:** US-SEMAST-017
**Epic:** EPIC-SEMAST-001

### User Story

As a **CI/CD pipeline engineer**,
I want a **guarantee that all existing features and tests remain unchanged** after the Semantic AST layer is added,
So that the addition of semantic analysis is purely additive and does not break any existing behavior.

### Context

The Semantic AST layer is a **new, additive capability**. All existing features — parsing, syntactic AST extraction (`--ast`), validation pipeline, error reporting, JSON output, directory traversal, and the entire existing test suite — **MUST** continue to work identically.

---

### Acceptance Criteria

| ID                | Criteria                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| AC-SEMAST-017-01  | The existing `--ast` flag behavior is unchanged: same output format, same content, same file.   |
| AC-SEMAST-017-02  | The existing `--validate` / `--no-validate` behavior is unchanged.                              |
| AC-SEMAST-017-03  | The existing `--json` output format is unchanged for all current fields.                        |
| AC-SEMAST-017-04  | The existing CLI exit codes (0 for success, 1 for failure) are unchanged.                       |
| AC-SEMAST-017-05  | All existing acceptance tests pass without modification.                                        |
| AC-SEMAST-017-06  | All existing regression tests pass without modification.                                        |
| AC-SEMAST-017-07  | The `ASTGenerator`, `ASTExporter`, `ValidationPipeline`, and `ErrorReporter` public APIs are unchanged. |
| AC-SEMAST-017-08  | `gasd-parser file.gasd` (no flags) produces identical output to the pre-semantic-AST version.   |
| AC-SEMAST-017-09  | The semantic AST pipeline is only invoked when `--ast-sem` is explicitly specified.              |

---

### Acceptance Tests

| Test ID            | Description                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------- |
| AT-SEMAST-017-01   | All existing acceptance tests in `Impl/tests/acceptance/` pass without modification.      |
| AT-SEMAST-017-02   | All existing regression tests in `Impl/tests/regression/` pass without modification.      |
| AT-SEMAST-017-03   | `gasd-parser file.gasd --ast` output is byte-identical to pre-semantic-AST version.       |
| AT-SEMAST-017-04   | `gasd-parser file.gasd` (no flags) output is identical to pre-semantic-AST version.       |
| AT-SEMAST-017-05   | `gasd-parser file.gasd --json` output schema is unchanged.                                |
| AT-SEMAST-017-06   | `gasd-parser invalid.gasd` exits with code 1 (unchanged).                                 |

---

### Regression Tests

| Test ID            | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| RT-SEMAST-017-01   | The full existing test suite passes as a mandatory pre-merge gate.                |
| RT-SEMAST-017-02   | No existing test file is modified as part of the semantic AST implementation.     |

---

# User Story 18 — `--ast-output` and `--ast-combine` Reuse for Semantic AST

**Story ID:** US-SEMAST-018
**Epic:** EPIC-SEMAST-001

### User Story

As a **GASD specification author**,
I want the existing **`--ast-output` and `--ast-combine` options to also apply when `--ast-sem` is used**,
So that I can save semantic AST output to files and combine multi-file semantic ASTs using the same familiar options.

### Context

The existing options work as follows with `--ast`:
- `--ast-output PATH` saves the AST JSON to a file instead of stdout. For multiple input files, each gets a separate output file with the input filename appended.
- `--ast-combine` merges multiple file ASTs into a single combined JSON output.

These options **MUST** work identically when `--ast-sem` is used, applying to the semantic AST output instead.

---

### Acceptance Criteria

| ID                | Criteria                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| AC-SEMAST-018-01  | `--ast-sem --ast-output PATH` saves the semantic AST JSON to the specified file path.           |
| AC-SEMAST-018-02  | `--ast-sem --ast-output PATH` with multiple input files produces separate output files per input (same naming convention as `--ast`). |
| AC-SEMAST-018-03  | `--ast-sem --ast-combine` merges multiple file semantic ASTs into a single combined JSON output. |
| AC-SEMAST-018-04  | `--ast-sem --ast-combine --ast-output PATH` writes the combined semantic AST to the specified file. |
| AC-SEMAST-018-05  | When both `--ast` and `--ast-sem` are used with `--ast-output`, semantic AST files use a `.sem.json` suffix to distinguish from syntactic AST files. |
| AC-SEMAST-018-06  | `--ast-output` and `--ast-combine` continue to work unchanged with `--ast` alone.               |

---

### Acceptance Tests

| Test ID            | Description                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------- |
| AT-SEMAST-018-01   | `gasd-parser file.gasd --ast-sem --ast-output out.json` writes semantic AST to `out.json`. |
| AT-SEMAST-018-02   | `gasd-parser dir/ --ast-sem --ast-output out.json` produces per-file semantic AST output files. |
| AT-SEMAST-018-03   | `gasd-parser dir/ --ast-sem --ast-combine` outputs a single combined semantic AST JSON.   |
| AT-SEMAST-018-04   | `gasd-parser dir/ --ast-sem --ast-combine --ast-output combined.json` writes combined output to file. |
| AT-SEMAST-018-05   | `gasd-parser file.gasd --ast --ast-sem --ast-output out.json` produces both `out.json` (syntactic) and `out.sem.json` (semantic). |
| AT-SEMAST-018-06   | `gasd-parser file.gasd --ast --ast-output out.json` still works exactly as before.        |

---

### Regression Tests

| Test ID            | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| RT-SEMAST-018-01   | Existing `--ast --ast-output` behavior is unchanged.                              |
| RT-SEMAST-018-02   | Existing `--ast --ast-combine` behavior is unchanged.                             |

---

# Requirements Traceability Matrix

| Requirement                            | Spec Section | User Story     | Acceptance Test   | Regression Test   |
| -------------------------------------- | ------------ | -------------- | ----------------- | ----------------- |
| REQ-SEMAST-001 AST Class Model         | §2–§12       | US-SEMAST-001  | AT-SEMAST-001-01  | RT-SEMAST-001-01  |
| REQ-SEMAST-002 Symbol Resolution       | §3–§8        | US-SEMAST-002  | AT-SEMAST-002-01  | RT-SEMAST-002-01  |
| REQ-SEMAST-003 TYPE Contract Binding   | §5, §5.3     | US-SEMAST-003  | AT-SEMAST-003-01  | RT-SEMAST-003-01  |
| REQ-SEMAST-004 Annotation Handling     | §14          | US-SEMAST-004  | AT-SEMAST-004-01  | RT-SEMAST-004-01  |
| REQ-SEMAST-005 Architecture Deps       | §6           | US-SEMAST-005  | AT-SEMAST-005-01  | RT-SEMAST-005-01  |
| REQ-SEMAST-006 FLOW Analysis           | §7, §11      | US-SEMAST-006  | AT-SEMAST-006-01  | RT-SEMAST-006-01  |
| REQ-SEMAST-007 Strategy Resolution     | §8           | US-SEMAST-007  | AT-SEMAST-007-01  | RT-SEMAST-007-01  |
| REQ-SEMAST-008 Decision Resolution     | §4           | US-SEMAST-008  | AT-SEMAST-008-01  | RT-SEMAST-008-01  |
| REQ-SEMAST-009 Namespace & Imports     | §3           | US-SEMAST-009  | AT-SEMAST-009-01  | RT-SEMAST-009-01  |
| REQ-SEMAST-010 Semantic Hashing        | §1.2.1       | US-SEMAST-010  | AT-SEMAST-010-01  | RT-SEMAST-010-01  |
| REQ-SEMAST-011 CI/CD Validation        | §1.2.1       | US-SEMAST-011  | AT-SEMAST-011-01  | RT-SEMAST-011-01  |
| REQ-SEMAST-012 Error Reporting         | —            | US-SEMAST-012  | AT-SEMAST-012-01  | RT-SEMAST-012-01  |
| REQ-SEMAST-013 Context & Directives    | §3           | US-SEMAST-013  | AT-SEMAST-013-01  | RT-SEMAST-013-01  |
| REQ-SEMAST-014 Human-in-the-Loop       | §10          | US-SEMAST-014  | AT-SEMAST-014-01  | RT-SEMAST-014-01  |
| REQ-SEMAST-015 Resource Blocks         | §12          | US-SEMAST-015  | AT-SEMAST-015-01  | RT-SEMAST-015-01  |
| REQ-SEMAST-016 `--ast-sem` CLI Option  | —            | US-SEMAST-016  | AT-SEMAST-016-01  | RT-SEMAST-016-01  |
| REQ-SEMAST-017 Backward Compatibility  | —            | US-SEMAST-017  | AT-SEMAST-017-01  | RT-SEMAST-017-01  |
| REQ-SEMAST-018 Output Option Reuse     | —            | US-SEMAST-018  | AT-SEMAST-018-01  | RT-SEMAST-018-01  |

---

# Test Coverage Summary

| Category                         | Story           | Acceptance Tests | Regression Tests | Total |
| -------------------------------- | --------------- | ---------------- | ---------------- | ----- |
| AST Class Model                  | US-SEMAST-001   | 11               | 2                | 13    |
| Symbol Resolution                | US-SEMAST-002   | 8                | 2                | 10    |
| TYPE Contract Binding            | US-SEMAST-003   | 8                | 2                | 10    |
| Annotation Handling              | US-SEMAST-004   | 6                | 2                | 8     |
| Architecture Dependencies        | US-SEMAST-005   | 8                | 2                | 10    |
| FLOW Semantic Analysis           | US-SEMAST-006   | 14               | 2                | 16    |
| Strategy Resolution              | US-SEMAST-007   | 9                | 2                | 11    |
| Decision System Resolution       | US-SEMAST-008   | 9                | 2                | 11    |
| Namespace & Imports              | US-SEMAST-009   | 5                | 2                | 7     |
| Deterministic Hashing            | US-SEMAST-010   | 6                | 2                | 8     |
| CI/CD Determinism                | US-SEMAST-011   | 3                | 1                | 4     |
| Error Reporting                  | US-SEMAST-012   | 3                | 2                | 5     |
| Context & Directives             | US-SEMAST-013   | 6                | 2                | 8     |
| Human-in-the-Loop                | US-SEMAST-014   | 6                | 2                | 8     |
| Resource Blocks                  | US-SEMAST-015   | 3                | 1                | 4     |
| `--ast-sem` CLI Option           | US-SEMAST-016   | 7                | 2                | 9     |
| Backward Compatibility           | US-SEMAST-017   | 6                | 2                | 8     |
| Output Option Reuse              | US-SEMAST-018   | 6                | 2                | 8     |
| **Total**                        |                 | **124**          | **34**           | **158** |

---

# Definition of Done

The Semantic AST layer is complete when:

- [ ] All symbols resolved
- [ ] TYPE contracts bound to FLOWs with VALIDATE AS TYPE.X enforcement
- [ ] Annotations normalized and canonically ordered (all §14 annotations)
- [ ] Architecture dependencies validated
- [ ] Strategies and decisions resolved (including PRECONDITION, COMPLEXITY, SORT_KEY)
- [ ] Namespaces and imports resolved
- [ ] CONTEXT, TARGET, and TRACE directives processed
- [ ] FLOW control-flow fully resolved (ENSURE...OTHERWISE, ON_ERROR, MATCH CONTAINS/OR/DEFAULT)
- [ ] Human-in-the-loop constructs (QUESTION, APPROVE, TODO, REVIEW) captured
- [ ] RESOURCES blocks captured
- [ ] Documentation comments (`///`) with `@trace` extracted
- [ ] `--ast-sem` CLI option implemented and documented
- [ ] `--ast-output` and `--ast-combine` work with `--ast-sem`
- [ ] All existing features and tests unchanged (backward compatibility)
- [ ] 158 tests passing (124 acceptance + 34 regression)
- [ ] Semantic hash deterministic and verified in CI
- [ ] Error messages include file, line, and context
- [ ] Semantic model feeds code generation