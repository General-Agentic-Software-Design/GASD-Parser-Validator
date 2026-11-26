# GASD Enhancement Proposal (GEP)

```text
GEP: 4
Title: Enhancing GASD 1.1.0: Grammar Flexibility, Pattern Matching, and Resource Specification
Author: Agentic Software Design (https://github.com/agentic-software-design)
Status: Accepted
Type: Standards Track
Created: 2026-03-07
```

---

# Abstract

This proposal addresses several critical gaps in the GASD 1.1.0 specification identified during parser refinement. It formalizes expert usage patterns, relaxes restrictive grammar rules for actions and identifiers, enhances pattern matching capabilities, and introduces a missing `RESOURCES` section to the normative grammar.

---

# Motivation

The currently published GASD 1.1.0 EBNF grammar is slightly too restrictive compared to the "expert" designs required for complex architectural specifications. Specifically:

* Flow actions are too rigid to support complex math or structured logic descriptions.
* Identifiers lack support for symbols like hyphens and trace labels (e.g., `#AC-1`) which are common in requirements traceability.
* Certain "soft keywords" like `STATUS` or `DATE` are currently blocked from being used as field names.
* The `MATCH` construct is too limited for common string-pattern or multi-pattern matching needs.
* The `RESOURCES` section, used in many reference designs, is entirely missing from the formal grammar.

---

# Specification

### 1. Action Rule Permissivity

The `action` and `expr` rules are updated to support math operators and more complex expressions.

```ebnf
action        ::= "VALIDATE" expr
                | "ACHIEVE" string_literal [ ":" assignments ] [ block ]
                | "CREATE" identifier ":" block
                | "PERSIST" identifier "via" identifier
                | "UPDATE" identifier "SET" identifier "=" expr
                | "APPLY" identifier "TO" expr
                | "THROW" identifier [ "(" arg_list ")" ]
                | "RETURN" expr
                | "LOG" string_literal

assignments   ::= property { "," property }
```

Update `expr` to support binary operators:

```ebnf
expr          ::= term { bin_op term }
term          ::= "TRANSFORM" "(" value "," annotations ")"
                | value
                | identifier { "." identifier } [ "(" [ arg_list ] ")" ]
bin_op        ::= "+" | "-" | "*" | "/" | "^" | "==" | "!=" | ">" | "<" | ">=" | "<="
```

### 2. Identifier and Symbol Extensions

The lexical tokens for `identifier` are expanded to support trace labels, hyphens, and versioning.

```ebnf
identifier    ::= [a-zA-Z_#] { [a-zA-Z0-9_.-] }
```

New symbols to support: Backticks (``` ` ```), Caret (`^`), Single Quote (`'`).

### 3. "Soft Keywords"

Keywords in positions where they are clearly identifiers (e.g., as field names or component names) SHALL be allowed. This is a parser implementation requirement to treat keywords as "soft" in non-ambiguous contexts.

### 4. Enhanced Pattern Matching (`MATCH`)

Expand `match_case` to support OR patterns and the `CONTAINS` operator.

```ebnf
match_case    ::= pattern_list "->" ( flow_step | action )
pattern_list  ::= pattern { "|" pattern }
pattern       ::= [ "CONTAINS" ] ( string_literal | number_literal | identifier | "DEFAULT" )
```

### 5. Metadata and RESOURCES section

Add a new `resources_stmt` to the top-level `section` rule.

```ebnf
section       ::= ... | strategy_def | constraint | resources_stmt

resources_stmt::= "RESOURCES" ":" indent { resource_item } dedent
resource_item ::= "-" string_literal [ annotations ]
```

### 6. Shorthand Annotations

Allow trace labels and more complex identifiers within annotations.

```ebnf
annotations   ::= "@" identifier [ "(" value_list ")" ] { "@" identifier [ "(" value_list ")" ] }
value_list    ::= value { "," value }
```

---

# Rationale

These changes bridge the gap between "textbook" GASD and "production" GASD. Allowing identifiers like `#AC-1` directly supports the core promise of GASD as a "Design Bridge" by making requirements traceability first-class. Permissive actions allow architects to describe logic precisely without dropping into implementation code, maintaining the abstraction level while ensuring the transpiler has enough information to generate math or complex assignments.

---

# Backwards Compatibility

This proposal is largely backward compatible. Existing valid GASD files will remain valid under the expanded grammar. Tooling (parsers and transpilers) will need to be updated to support the expanded token set and relaxed rules.

---

# Reference Implementation (Optional)

Update the GASD ANTLR4 grammar:

1. Relax `ID` token definition.
2. Add `bin_op` to the expression sub-grammar.
3. Add `RESOURCES` as a new top-level block handler.
4. Implement "soft keyword" logic for `STATUS`, `DATE`, `INPUT`, `OUTPUT`, and `INTERFACE`.

---

# Test Plan

* **Acceptance Test**: `ACHIEVE "Calc": x = y * 2` parses successfully.
* **Acceptance Test**: `@trace(#AC-1)` parses successfully.
* **Acceptance Test**: `RESOURCES` block with bulleted list parses successfully.
* **Negative Test**: Unbalanced parentheses in complex expressions fail validation.

---

# Traceability

* **Requirement**: Support complex expressions in FLOW steps.
* **Requirement**: Support requirements traceability via `#` identifiers.
* **Requirement**: Formalize `RESOURCES` section.

---

# Change History

```
2026-03-07 — Initial draft formally addressing specification gaps in GASD 1.1.0
```
