# GASD — General Agentic Software Design Language

## Vision

GASD is a **Software-Requirements-Design-Code Bridge** language that sits between an SRS (Software Requirements Specification) or user story and the generated implementation code. It expresses **design intent, architectural decisions, and implementation constraints** — not requirements (that's the SRS) and not code (that's the transpiler's output).

The language enables two primary **AI-Human Collaboration** workflows:

### 1. AI-Supported Drafting (SRS or Story Driven)
1.  **Input Ingestion**: An AI agent parses formal requirements (SRS) or agile artifacts (User Stories, Epics) to understand the desired behavior.
2.  **Draft Generation**: The agent generates an initial GASD design, mapping requirements/stories to architectural components and flows.
3.  **Human-in-the-Loop Review**: Architects review and refine the GASD, locking down critical decisions and adding constraints.
4.  **Deterministic Transpilation**: The approved GASD is transpiled into consistent, identical code.

### 2. Human-Driven Specification (Architect-First)
1.  **Direct Specification**: An engineer writes GASD directly to define a system's core architecture and logic with precision, independent of upstream artifacts.
2.  **Agent Implementation**: The AI agent uses the GASD as a blueprint to generate the full implementation without ambiguity.
3.  **Guaranteed Compliance**: The generated code is guaranteed to follow the exact constraints defined by the human.

By capturing enough constraint and context at the design level, GASD ensures:
- **No ambiguity**: The agent has explicit rules, not vague intent.
- **No hallucination**: Decisions are locked down, not interpreted.
- **No inconsistency**: The same GASD file produces identical code every transpilation.
- **Collaborative Engineering**: Human experts guide the high-level architecture while agents handle the design-to-code mapping.

## Design Principles

1. **Design-Level Abstraction**: Higher than code (captures architecture/intent), lower than requirements (captures logic/constraints). Enough precision to eliminate agent interpretation variance.

2. **Multi-Target**: GASD expressions are transpilable into any major programming language (Python, Java, C++, Rust, Go, etc.) based on project context. The constraint system ensures identical output regardless of when transpilation occurs.

3. **Constraint-Driven Determinism**: Type contracts (`@format`, `@range`, `@hash`), design decisions (`DECISION`), algorithmic strategies (`STRATEGY`), and invariants (`INVARIANT`) collectively lock down enough context for reproducible code generation.

4. **Turing Complete**: Fully capable of expressing any computational logic and design intent.

5. **Testable**: Explicitly supports defining testability constraints (`@testable`, `@mockable`, `@injectable`).

## Core Constructs

| Construct | Purpose |
|---|---|
| `DECISION` | Lock down architectural choices (e.g., bcrypt vs argon2) |
| `COMPONENT` / `INTERFACE` | Define building blocks and their contracts |
| `TYPE` + annotations | Strict type contracts with generation constraints |
| `FLOW` | Design-level logic with constraint annotations |
| `STRATEGY` | Algorithmic approach specification |
| `CONSTRAINT` / `INVARIANT` / `ENSURE` | Rules the generated code must obey |
| `QUESTION` / `APPROVE` | Human-in-the-loop lifecycle |
| `CONTEXT` / `TARGET` | Generation directives |

## Review Notes

> [!IMPORTANT]
> This is a design language, not a programming language. GASD files should be intuitive for architects and engineers to read, write, and review — enabling human-in-the-loop design before any code is generated.
