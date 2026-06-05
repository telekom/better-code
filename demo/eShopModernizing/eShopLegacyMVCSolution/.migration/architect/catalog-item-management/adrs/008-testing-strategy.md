# 8. Testing Strategy

## Status

Accepted

## Context

Discovery found **zero automated tests** in the legacy solution. The spec defines 18 test
cases (TC-001..018) covering 100% of business rules and all five flows, with a ready-made
in-memory test double (`CatalogServiceMock`, `UseMockData=true`). Behavioral equivalence
must be provable before cutover.

## Decision

Adopt a **test pyramid** with **xUnit + FluentAssertions**:

- **Unit** (validators, view-model math, id generator, entity defaults): TC-001, TC-003..009, TC-013, TC-014, TC-016, TC-018 → `CatalogItemValidatorTests`, `PaginatedItemsViewModelTests`, `CatalogIdGeneratorTests`, `CatalogItemTests`.
- **Integration** (service + EF Core via InMemory/Testcontainers): TC-002, TC-010..012, TC-015, TC-017 → `CatalogServiceTests`, `CatalogControllerTests`.
- Establish these as a **characterization suite first** (run against legacy behavior where possible) so EF6→EF Core differences are caught.
- Wire tests into CI as a required gate before any phase cutover.

## Consequences

- **Easier**: creates the regression safety net the legacy app lacks; each spec rule maps to a named test (see mapping.json test_cases).
- **Easier**: `CatalogServiceMock` enables fast DB-free unit tests.
- **Harder**: building the initial suite is net-new effort (no tests to port); integration tests need a DB provider (InMemory has fidelity limits; Testcontainers adds CI cost).
- **Tradeoff**: InMemory provider is fast but doesn't catch all SQL Server semantics — use Testcontainers for the queries that rely on sequences/paging.
