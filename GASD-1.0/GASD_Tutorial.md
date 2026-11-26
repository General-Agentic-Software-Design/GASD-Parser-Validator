# Mastering GASD 1.0.0: The Official Guide

Welcome to **GASD 1.0.0 (General Agentic Software Design Language)**. This tutorial will take you from the basics of design-level abstraction to expert-level techniques for generating deterministic, production-ready code. GASD is the **Official Authoritative** technical standard for AI-human architectural collaboration.

---

## 1. What is GASD?

GASD is a **Design Bridge Language**. It sits between your upstream requirements — whether that's a formal **SRS** or **Agile User Stories** — and your Implementation (Code).

Instead of telling an AI agent what you *want* in natural language (which leads to "Agent Drift" and inconsistent code), you use GASD to define the **constraints and decisions** that make the implementation inevitable.

It supports two distinct engineering workflows:
1.  **AI-Driven**: An agent drafts the design from your requirements, which you then review and refine.
2.  **Human-Driven**: You write the design first to "contract" the agent to write the implementation for you.

### 1.1 Agile & User Story Coexistence
For GASD to coexist with user-story driven development (Agile), it must not replace user stories — it must sit downstream of them. With GASD, you insert a deterministic design bridge:

`Epic` → `User Stories` → `Acceptance Criteria` → `SRS` (optional formalization layer) → `GASD` (deterministic architecture spec) → `Transpiled Code`

- **SRS or User Stories define behavior.**
- **GASD removes architectural degrees of freedom.**

By strictly separating these concerns, GASD makes code generation:
- **Deterministic**: The same input always yields the same output.
- **Stable**: Changes to requirements don't break the architecture.
- **Reproducible**: Anyone can regenerate the codebase.
- **Testable**: Design decisions are explicit and verifiable.
- **Versionable**: Architecture is code.


> [!IMPORTANT]
> **GASD Rule #1**: If the agent has a choice, you haven't written enough GASD. 
> 
> **GASD Rule #2**: All design elements **MUST** align with the [Official Self-Definition](gasd-1.0.0.gasd).

---

## 2. The Core Syntax

### 2.1 Setting the Stage: `CONTEXT`, `TARGET`, and `TRACE`
Every GASD file starts with directives that tell the transpiler what environment it's targeting and which upstream artifacts it fulfills. `TRACE` supports any traceable identifier — SRS requirements, User Stories, Epics, or Acceptance Criteria.

```gasd
CONTEXT: "Microservices Architecture / Kubernetes"
TARGET: "Rust 1.70+"

// SRS-driven
TRACE: "SRS-101", "SRS-115"

// Or User Story-driven
TRACE: "EPIC-007", "US-042", "AC-042-1"
```

### 2.2 Locking the Architecture: `DECISION`
Use `DECISION` blocks to eliminate variance in library choices or strategies.

```gasd
DECISION "State Management" @status("APPROVED"):
    CHOSEN: "Redux with Saga"
    RATIONALE: "Needed for complex side-effects in the dashboard"
    AFFECTS: [DashboardComponent, NotificationSystem]
```

### 2.3 The Data Contract: `TYPE`
GASD uses strict type contracts. Annotations (`@format`, `@range`, etc.) are converted into validation logic in the target language.

```gasd
TYPE User:
    id: UUID @auto_generate
    email: String @format("email") @unique
    age: Integer @range(18, 120)
```

---

## 3. Designing Logic with `FLOW`

A `FLOW` is not "code"—it's a series of design-level steps. It uses high-level primitives that the transpiler understands.

```gasd
FLOW process_payment(amount, token):
    1. VALIDATE amount > 0
    2. ACHIEVE "Authorize with Stripe"
        ON_ERROR: THROW PaymentUnauthorizedException
    3. CREATE TransactionRecord:
        status: "AUTHORIZED"
        timestamp: @now
    4. PERSIST TransactionRecord via DB
    5. RETURN TransactionRecord.id
```

---

## 4. Modular Design (Multi-File Support)

For large systems, you can split your design into multiple GASD files using `NAMESPACE` and `IMPORT`.

### Key Concepts
1.  **`NAMESPACE`**: Defines a logical package for your types (prevents name collisions).
2.  **`IMPORT`**: Brings external definitions into your current file.

### Example Structure
```
project/
├── common/
│   └── types.gasd      (NAMESPACE: "common")
└── services/
    └── payment.gasd    (IMPORT "../common/types.gasd" AS Shared)
```

### 4.1 Defining Shared Types (`types.gasd`)
```gasd
NAMESPACE: "common"
TYPE Money:
    amount: Decimal
    currency: String
```

### 4.2 Importing and Using (`payment.gasd`)
```gasd
NAMESPACE: "payment"
IMPORT "../common/types.gasd" AS Shared

TYPE Transaction:
    id: UUID
    cost: Shared.Money  // <-- Using imported type
```

See the full example in:
- [examples/multi_doc_system/shared_types.gasd](examples/multi_doc_system/shared_types.gasd)
- [examples/multi_doc_system/payment_service.gasd](examples/multi_doc_system/payment_service.gasd)

---

## 5. Designing for UX & Web Apps

GASD can support complex web application development with many UX elements.
However, it adheres to a strict philosophy:

- **It defines behavior, not pixels.**
- **It constrains logic, not layout.**
- **It drives state, not CSS.**

If architected correctly, your GASD file becomes a **deterministic behavioral backbone** for large-scale UX systems (React, Vue, Swift).

### Example: The "Behavioral Backbone"
Instead of describing a "Blue Button", describe the **Flow** that happens when a user attempts an action.

```gasd
// The UI is a function of this State
TYPE WizardState:
    step: Enum(IDENTITY, PAYMENT, SUCCESS)
    errors: List<String>

// The Logic determines valid transitions
FLOW next_clicked(current_state: WizardState, input: FormData):
    MATCH current_state.step:
        IDENTITY ->
            1. VALIDATE input.email
            2. IF valid -> TRANSITION to PAYMENT
            3. ELSE -> RETURN error "Invalid Email"
```

The agent generates the State Machine logic (Redux/Zustand), while the frontend team (or agent) builds the UI components to *render* that state.

See the full example: [examples/onboarding_wizard.gasd](examples/onboarding_wizard.gasd)

---

## 6. Workflow A: AI-Driven Drafting (SRS or User Stories → GASD)

One of the most powerful features of GASD is its ability to serve as a handoff point between an AI agent and a human engineer. The upstream input can be a formal **SRS** or **Agile artifacts** (Epics, User Stories, Acceptance Criteria) — GASD is agnostic to which methodology you use.

### The Lifecycle:
1.  **Input**: You provide upstream artifacts to an AI agent — either an **SRS** or a set of **User Stories with Acceptance Criteria**.
2.  **Generation**: The agent generates a `.gasd` file. It uses **`TRACE`** to link components back to the source artifacts and **`@agent_note`** to explain its architectural choices.
3.  **Review**: You (the human expert) review the design. Elements are marked as **`@status("DRAFT")`**; you update them to **`@status("APPROVED")`** as you go.
4.  **Finalization**: Once approved, the GASD file acts as the "source of truth" for code generation.

### Example: Agent-Generated Draft (from SRS)
```gasd
TRACE: "SRS-402 (Payment Gateway)"

COMPONENT StripeAdapter @status("REVIEW_REQUIRED"):
    @agent_note("Selected Stripe due to SRS mention of credit card support")
    INTERFACE: process(payment: Payment) -> Result<Void>
```

### Example: Agent-Generated Draft (from User Story)
```gasd
TRACE: "US-042 (As a customer, I want to pay by credit card)"
TRACE: "AC-042-1 (System must support Visa and Mastercard)"

COMPONENT StripeAdapter @status("REVIEW_REQUIRED"):
    @agent_note("Selected Stripe because AC-042-1 requires Visa/Mastercard support")
    INTERFACE: process(payment: Payment) -> Result<Void>
```

> [!TIP]
> **Expert Workflow**: Use the agent to do the "heavy lifting" of mapping requirements or stories to components, then use your expertise to "lock down" the critical architectural decisions that an agent might miss.

---

## 7. Workflow B: Human-Driven Specification (Writing GASD First)

Sometimes you already know exactly how the system should be built. In this mode, you write GASD to "contract" the agent to do the coding for you.

### Why write GASD first?
- **Speed**: It's faster to write a `FLOW` than to write 500 lines of boilerplate C++ or Java.
- **Portability**: Write the design once, generate it in Rust today and Go tomorrow.
- **Enforcement**: You define the `DECISION` (e.g., "Use Redis for caching") and the agent *must* follow it.

### Workflow:
1. **Define Intent**: You write types, components, and flows in GASD.
2. **Set Constraints**: You add `@range`, `@format`, and `INVARIANT` rules.
3. **Agent Generates**: The agent implements the "how" while respecting your "what".

---

## 8. Hands-on Tutorial: Building a "Notification Service"

Let's design a service that sends alerts to users, fulfilling **SRS-102 (User Notifications)**.

### Step 1: Context and Tracing
Start by setting up the file.
```gasd
CONTEXT: "User Messaging Service"
TARGET: "TypeScript"
TRACE: "SRS-102"
```

### Step 2: Define the Types
Define the data contract for an alert.
```gasd
TYPE AlertRequest:
    user_id: UUID
    message: String @max_length(280)
    priority: Enum(LOW, MEDIUM, HIGH)
```

### Step 3: Define the Component
Architect the service as an Observer pattern.
```gasd
COMPONENT NotificationService @status("APPROVED"):
    PATTERN: "Observer"
    DEPENDENCIES: [EmailProvider, PushNotificationProvider]
    INTERFACE:
        send_alert(request: AlertRequest) -> Result<Void>
```

### Step 4: Define the Flow with Strategic Precision
Describe the logic in deterministic steps.
```gasd
FLOW send_alert(request):
    MATCH request.priority:
        HIGH -> ACHIEVE "Send Push" AND "Send Email" @async
        MEDIUM -> ACHIEVE "Send Push"
        LOW -> ACHIEVE "Log to Buffer"
    RETURN Result.success
```

---

## 9. Comprehensive GASD Examples

The following examples include detailed **Step-by-Step Breakdowns** within the files themselves to help you understand the design intent.

### 7.1 Basic Foundations
1.  **Hello World**: [hello_world.gasd](examples/hello_world.gasd) - Minimal valid GASD file.
2.  **Binary Search**: [binary_search.gasd](examples/binary_search.gasd) - Pure algorithmic logic with constraints.
3.  **Discount Calculation**: [discount_calculation.gasd](examples/discount_calculation.gasd) - Simple business logic branching.

### 7.2 Service Design Patterns
4.  **User Registration**: [user_registration.gasd](examples/user_registration.gasd) - CRUD service with validation.
5.  **E-commerce Checkout**: [ecommerce_checkout.gasd](examples/ecommerce_checkout.gasd) - Dependency injection and persistence.
6.  **User Management System**: [user_management.gasd](examples/user_management.gasd) - Full microservice with global architectural rules.

### 7.3 Advanced Distributed Systems
7.  **Distributed SAGA Transaction**: [saga_transaction.gasd](examples/saga_transaction.gasd) - Handling distributed failure with compensation.
8.  **Raft Consensus (Lite)**: [raft_consensus.gasd](examples/raft_consensus.gasd) - Strict state machine implementation.
9.  **Autonomous Drone Navigation**: [drone_navigation.gasd](examples/drone_navigation.gasd) - Human-in-the-Loop safety systems.



---

## 10. Engineering Best Practices

### 💡 Practice 1: Favor Constraints over Logic
Instead of writing complex loops in `FLOW`, use `@annotations` or `STRATEGY`. Let the transpiler handle the implementation details of the loop while you define the *rules*.

### 💡 Practice 2: The "Determinism Test"
Ask yourself: "If I give this GASD file to two different AI agents, will they make different choices?" If yes, add a `DECISION` or a `CONSTRAINT` to lock it down.

### 💡 Practice 3: Cross-Language Thinking
GASD types are abstract. `List<T>` might be `ArrayList` in Java and `Vec` in Rust. Trust the `TARGET` directive to handle the mapping.

---

## 11. Expert Tips

### 🚀 Tip 1: Strategic Algorithmic Precision
When the *way* something is calculated matters, use `STRATEGY`.

```gasd
STRATEGY tax_calculation:
    ALGORITHM: "Bracket-based progressive tax"
    PRECISION: "Decimal (18, 8)"
    COMPLEXITY: O(n) where n is number of brackets
```

### 🚀 Tip 2: Human-in-the-Loop
Use `QUESTION` to pause the generation if a design choice is ambiguous.

```gasd
QUESTION: "Should we use a cache-aside or write-through pattern for the session store?"
    BLOCKING: true
```

### 🚀 Tip 3: The AI-Readable Ground Truth
Always refer to the [Official Self-Definition (gasd-1.0.0.gasd)](gasd-1.0.0.gasd) for the most precise mapping of language constructs. AI agents use this file as their normative reference for what is possible within the GASD 1.0.0 standard.

---

## 13. Operational & Infrastructure Design

Real-world engineering requires more than just business logic. GASD allows you to codify infrastructure, security, and maintenance concerns so the generated system is "production-ready" by design.

### 13.1 Infrastructure & Deployment Strategy
Use `CONTEXT` and `DECISION` to lock down how the system is hosted and deployed.

```gasd
CONTEXT: "AWS / EKS / Terraform"

DECISION "Deployment Strategy":
    CHOSEN: "Blue-Green Deployment"
    RATIONALE: "Zero-downtime requirements for the checkout service"
    AFFECTS: [CheckoutService]
```

### 13.2 Security Boundaries
Use annotations to enforce security at the design level. This ensures the agent implements proper middleware and encryption.

```gasd
TYPE UserSecret @sensitive:  // Never logged or exposed in API
    api_key: String @mask

FLOW delete_resource(id):
    @authorized("ROLE_ADMIN")
    1. ACHIEVE "Delete from DB"
```

### 13.3 Error Handling & Resilience
Beyond simple `THROW`, use systemic directives to handle failure at scale. The `@error_strategy` annotation defines the overall approach for a flow (e.g., "Fail-Fast" vs "Exception-based").

```gasd
FLOW external_api_call():
    @error_strategy("Fail-Fast")
    @retry(3)
    @circuit_breaker
    @timeout(500)
    1. ACHIEVE "Call Remote Service"
        ON_ERROR @type("NetworkError"):
            LOG "Remote service unreachable" @severity("CRITICAL")
            RETURN Result.failure
```

### 13.4 Logging & Monitoring
Codify what needs to be tracked for DevOps visibility.

```gasd
FLOW process_order(order):
    1. LOG "Starting order process" @trace_id(order.id)
    2. ACHIEVE "Payment"
    3. UPDATE Metric "orders_processed" @increment
```

---

## 14. Next Steps

1.  Explore the [GASD Specification](GASD_Specification.md) for a full keyword list.
2.  Try generating code from your first GASD file!
3.  Check out the [Operational Concerns Example](examples/operational_concerns.gasd) for production-scale design patterns.
