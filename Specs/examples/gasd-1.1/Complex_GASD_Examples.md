# Complex GASD Examples

This document contains advanced examples of **GASD** usage, demonstrating complex patterns like distributed transactions (SAGA), consensus algorithms, and human-machine collaboration.

---

## Example 4: Distributed SAGA Transaction (E-commerce Order)
**Scenario**: An order fulfillment process across microservices that requires compensation (undo) steps if any part fails.
[Source: saga_transaction.gasd](saga_transaction.gasd)

## Example 5: Distributed Consensus (Raft-Lite)
**Scenario**: Implementing a consensus algorithm state machine with strict safety guarantees.
[Source: raft_consensus.gasd](raft_consensus.gasd)

## Example 6: Autonomous Drone with Human Oversight
**Scenario**: A flight control system that operates autonomously but requests human permission for critical actions or when confidence is low.
[Source: drone_navigation.gasd](drone_navigation.gasd)
