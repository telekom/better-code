# 5. Error Handling Strategy

## Status

Accepted

## Context

The legacy feature handles errors inline: null id → 400 (ERR-001), missing item → 404
(ERR-002), invalid model → redisplay form (ERR-003), and any unhandled exception falls to
the global `HandleErrorAttribute` (ERR-004). There is no per-action try/catch around EF
`SaveChanges` and no optimistic concurrency token (spec unknowns #2).

## Decision

- Preserve explicit **400 (BadRequest)** for missing ids and **404 (NotFound)** for absent items in controllers (BR-006, BR-007).
- Use **FluentValidation** for input rules (BR-001..005); on failure, redisplay the form (MVC) or return **`ValidationProblemDetails`** (any API caller).
- Add **global exception-handling middleware** producing **ProblemDetails** for unhandled exceptions (ERR-004), replacing `HandleErrorAttribute`.
- Introduce an **optimistic concurrency token (`rowversion`)** on `CatalogItem` to make concurrent Edit/Delete safe (closes spec unknown #2), surfacing `DbUpdateConcurrencyException` as a 409 with a retry hint.
- Implement **HiLo id allocation** as an injectable `CatalogIdGenerator` (EF Core HiLo / explicit sequence) with thread-safe batch semantics; document scale-out behavior (spec unknown #4).

## Consequences

- **Easier**: consistent, observable error responses; safer concurrent edits than the legacy last-write-wins.
- **Easier**: validation centralized and unit-testable (TC-001..008).
- **Harder**: adding a concurrency token is a behavior change (new 409 path) and a schema column — must be covered by tests and communicated.
- **Tradeoff**: EF Core HiLo semantics differ slightly from the hand-rolled generator; tests (TC-016) pin the 10-per-fetch contract.
