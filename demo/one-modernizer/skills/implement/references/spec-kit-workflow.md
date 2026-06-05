# Spec-Kit Workflow for Migration Code Generation

## Core Principle

Specifications drive code generation. Every line of generated code traces back to a formal spec item. The process is sequential with verification — never batch-generate without checking.

## The 6 Phases

### Phase 1: Constitution

Establish the rules that govern ALL generated code. These are non-negotiable constraints derived from architecture decisions (ADRs, tech stack, naming conventions). Think of it as the project's "coding standards" but stricter — it's a machine-enforceable contract.

**Key outputs**: `constitution.md`

### Phase 2: Specify

Translate abstract architecture (mapping.json) into concrete code-level specifications. This is where "OrderValidator implements BR-001" becomes "public ValidationResult validateCreditLimit(Order order, Customer customer) throws CreditLimitExceededException".

**Key outputs**: `specs/<service>.json` per service

### Phase 3: Clarify

Find and resolve every ambiguity BEFORE writing code. Cheaper to ask one question now than to rewrite three files later. Focus on: ambiguous spec items, missing return types, contradictory rules, edge cases.

**Key outputs**: `clarifications.json`

### Phase 4: Plan

Define execution order. Not all tasks are equal — some are risky (complex rules), some are foundational (entities that everything depends on), some are independent (separate services). Plan accordingly.

**Key outputs**: `plan.md`

### Phase 5: Tasks

Break the plan into atomic, ordered tasks. Each task = one file. Each file has clear inputs (spec refs) and outputs (generated code). Dependencies are explicit — T-002 depends on T-001 means T-001 must pass verification before T-002 starts.

**Key outputs**: `tasks.json`

### Phase 6: Implement

Execute tasks sequentially. For each: read spec → generate code → verify → log → next. If verification fails, fix and retry (max 3). If still failing, flag to user and skip to next non-dependent task.

**Key outputs**: generated source files + `task-log.json`

## Verification Between Each Task

Apply all checks from `verification-rules.md` after every generated file. Fix failures and retry (max 3). If unresolvable, flag to user and skip to the next independent task.

## Traceability

Every generated method that implements business logic must be traceable:

**Java/Spring**: Use a constant or annotation

```java
// Implements: BR-001
public ValidationResult validateCreditLimit(Order order, Customer customer) { ... }
```

**Go**: Use a comment on the function

```go
// Implements: BR-001
func (s *OrderService) ValidateCreditLimit(order Order, customer Customer) error { ... }
```

**Python**: Use a decorator or docstring reference

```python
@implements("BR-001")
def validate_credit_limit(self, order: Order, customer: Customer) -> ValidationResult: ...
```

This enables post-generation auditing: grep for BR-xxx IDs to verify coverage.

## Parallel Generation

Services that don't depend on each other's source code can generate in parallel. Each parallel agent gets:

- Its own task subset
- The shared constitution
- Its service's implementation spec
- Relevant spec.json items

After parallel generation completes:

1. Verify cross-service contracts (shared DTOs, event schemas)
2. Check that generated API clients match generated API servers
3. Verify event publishers match event consumers
