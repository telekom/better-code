# Quality Gates

## Gate 1: Build (MUST PASS)

The generated project must compile without errors.

- Zero compilation errors
- Zero linker errors
- Warnings are acceptable (report but don't block)

## Gate 2: Tests (MUST PASS)

All generated tests must pass.

- Unit tests: 100% pass rate required
- Integration tests: allowed to skip if infrastructure unavailable (Testcontainers, external services) — but must be flagged
- Skipped tests count as warnings, not failures

## Gate 3: Spec Coverage (MUST PASS)

Every item from decompose spec.json must have corresponding generated code:

| Spec Item              | Must Have                               |
| ---------------------- | --------------------------------------- |
| BR-xxx (business rule) | A method implementing the logic         |
| FLOW-xxx (flow)        | An endpoint/handler processing the flow |
| ERR-xxx (error)        | An exception class + handler            |
| TC-xxx (test case)     | A test method                           |
| Data model structure   | An entity class + DB migration          |
| External interface     | An adapter/client class                 |

Target: 100%. Anything less is FAIL.

## Gate 4: Contracts (SHOULD PASS)

API and event contracts should be defined:

| Contract                 | Required When                      |
| ------------------------ | ---------------------------------- |
| OpenAPI (openapi.yaml)   | REST endpoints exist               |
| AsyncAPI / event schemas | Events published/consumed          |
| Proto files (.proto)     | gRPC services exist                |
| Shared DTOs              | Cross-service communication exists |

Missing contracts = WARNING (not FAIL), but generate them if possible.

## Gate 5: Infrastructure (SHOULD PASS)

Production infrastructure should be defined:

| Artifact           | Required When        |
| ------------------ | -------------------- |
| Dockerfile         | Always (per service) |
| docker-compose.yml | Always (local dev)   |
| CI/CD pipeline     | Always               |
| Helm/K8s manifests | Target is K8s        |
| DB migrations      | Database exists      |

Missing infrastructure = WARNING. Generate what's missing.

## Gate 6: Code Quality (ADVISORY)

Constitution compliance check:

- No TODO/FIXME in business logic
- No empty/stub implementations
- Naming conventions followed
- Layer boundaries clean
- Traceability comments present (BR-xxx)
- Methods under 30 lines (advisory)
- Single responsibility (advisory)

Quality violations = INFO level (always report, never block).

## Verdict Matrix

| Build | Tests | Coverage | Contracts | Infra    | Quality      | Verdict                |
| ----- | ----- | -------- | --------- | -------- | ------------ | ---------------------- |
| PASS  | PASS  | 100%     | Complete  | Complete | Clean        | **PASS**               |
| PASS  | PASS  | 100%     | Partial   | Partial  | Minor issues | **PASS WITH WARNINGS** |
| PASS  | PASS  | < 100%   | Any       | Any      | Any          | **FAIL**               |
| PASS  | FAIL  | Any      | Any       | Any      | Any          | **FAIL**               |
| FAIL  | Any   | Any      | Any       | Any      | Any          | **FAIL**               |
