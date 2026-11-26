# GASD 1.1.0 — Official Authoritative General Agentic Software Design Language

GASD is a **Design Bridge Language** that connects upstream Requirements (SRS) to downstream Implementation (Code).

## Core Concept: The Deterministic Bridge

GASD does not contain requirements, and it does not contain implementation code. It captures **Design Decisions** and **Implementation Constraints** so that an AI agent produces **identical code every time**.

### Integration with Agile

For GASD to coexist with user-story driven development (Agile), it must not replace user stories — it must sit downstream of them. With GASD, you insert a deterministic design bridge:

`Epic` → `User Stories` → `Acceptance Criteria` → `SRS` (optional formalization layer) → `GASD` (deterministic architecture spec) → `Transpiled Code`

It supports two collaboration paths:

1. **Agent-First**: Agent drafts GASD from an SRS → Human reviews/modifies.
2. **Human-First**: Human specifies the design in GASD → Agent implements the code.

```mermaid
graph TD
    SRS[SRS: Requirements] --"1. Agent Drafts"--> GASD(GASD: Design Bridge)
    Human[Human Architect] --"2. Human Specifies"--> GASD
    GASD --"Transpilation"--> Code[Deterministic Output]
```

Standard natural language allows for "Agent Drift" — where the AI makes different implementation choices each time. GASD eliminates this through a strict constraint system, providing an unambiguous bridge for AI-human collaboration.

- **Lock down Architecture**: Use `DECISION` blocks to choose libraries, strategies, and patterns.
- **Lock down Data**: Use `TYPE` contracts with `@annotations` for validation and formatting.
- **Lock down Logic**: Use `FLOW` and `STRATEGY` with `@error_strategy` to define the steps and algorithms without writing raw code.
- **Strict Compliance**: Fully RFC 2119 compliant (MUST, SHALL, SHOULD) for both human specifications and AI interpretations.

## GASD Ecosystem

The GASD language is supported by a growing ecosystem of tools and resources:

- **[GASD Blog](https://general-agentic-software-design.github.io/)**: Read about the "why" behind GASD and the detailed reasoning for the Design Bridge philosophy.
- **[VS Code Extension](https://github.com/General-Agentic-Software-Design/gasd-vscode-extension)**: Get expert-level support in your editor with syntax highlighting, IntelliSense, real-time diagnostics, and Mermaid visualizations.
- **[GASD Parser & Validator](https://github.com/General-Agentic-Software-Design/GASD-Parser-Validator)**: The canonical tool for ensuring your designs are 100% compliant. Use it in **Self-Verification Loops** to eliminate AI hallucinations and design drift.

## Documentation

- **[Specification](GASD_Specification.md)**: The official normative reference with strict grammar and compliance rules.
- **[Self-Definition](gasd-1.1.0.gasd)**: The official AI-readable ground truth and metamodel of the language.
- **[Tutorial](GASD_Tutorial.md)**: A comprehensive guide for engineers to master GASD.
- **[Examples](examples/GASD_Examples.md)**: Real-world design patterns and algorithmic strategies.
- **[Design Principles](Design_Principles.md)**: The underlying philosophy of the Design Bridge.

## Getting Started

1. **Draft**: Provide your User Stories or SRS (Software Requirements Specification) to an AI agent to generate an initial GASD design.
2. **Review & Refine**: Humans review the GASD file for architectural correctness, security, and specific constraints.
3. **Generate**: Provide the finalized GASD to the agent with a `TARGET` (e.g., Python, Rust) to get production-ready, consistent code.

---

## Changelog

### Version 1.1.0

- **Literal Types** (via GEP-2): Specify that a field must match an exact string or number, enabling discriminant fields, strict state transitions, and constant values. See the [Tutorial](GASD_Tutorial.md) and [Specification](GASD_Specification.md) for details.
- **Formalized Flow Keywords** (via GEP-3): Explicitly defines `TRANSFORM`, `ON_ERROR`, `THROW`, `UPDATE`, and `APPLY` to support deterministic mutations and error handling. See the [Specification](GASD_Specification.md#flow-keywords) for details.
- **Grammar Flexibility, Pattern Matching, and Resources** (via GEP-4): Expands identifier syntax for requirements traceability (e.g., `#AC-1`), allows permissive math expressions in actions, enhances `MATCH` with `CONTAINS` and OR patterns, and formalizes the `RESOURCES` definition block.
- **Mandatory Explicit VALIDATE AS TYPE Binding** (via GEP-5): Requires `VALIDATE expr AS TYPE.TypeName` on every validation step, establishing explicit TYPE→FLOW binding for deterministic annotation enforcement. See the [Specification](GASD_Specification.md#53-annotation-enforcement-via-validate-binding) for details.

---
