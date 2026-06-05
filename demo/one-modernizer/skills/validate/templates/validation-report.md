# Validation Report: {{FEATURE_NAME}}

## Verdict: {{PASS / PASS WITH WARNINGS / FAIL}}

## Build

- **Status**: {{PASS / FAIL}}
- **Command**: {{build command used}}
- **Errors**: {{count}}
- **Warnings**: {{count}}

{{If FAIL: list error messages}}

## Tests

- **Status**: {{PASS / FAIL}}
- **Passed**: {{n}}
- **Failed**: {{n}}
- **Skipped**: {{n}}

{{If failures: list failing tests with error messages}}

## Spec Coverage

| Category                | Covered | Total     | Status        |
| ----------------------- | ------- | --------- | ------------- |
| Business Rules (BR-xxx) | {{n}}   | {{total}} | {{PASS/FAIL}} |
| Flows (FLOW-xxx)        | {{n}}   | {{total}} | {{PASS/FAIL}} |
| Test Cases (TC-xxx)     | {{n}}   | {{total}} | {{PASS/FAIL}} |
| Data Model              | {{n}}   | {{total}} | {{PASS/FAIL}} |
| Errors (ERR-xxx)        | {{n}}   | {{total}} | {{PASS/FAIL}} |
| Interfaces              | {{n}}   | {{total}} | {{PASS/FAIL}} |

{{If gaps: list uncovered items}}

## Contracts

| Contract      | Status                                  |
| ------------- | --------------------------------------- |
| OpenAPI spec  | {{Present / Missing / Generated}}       |
| Event schemas | {{Present / Missing / Generated / N/A}} |
| Proto files   | {{Present / Missing / N/A}}             |

## Infrastructure

| Artifact           | Status                            |
| ------------------ | --------------------------------- |
| Dockerfile(s)      | {{Present / Missing / Generated}} |
| docker-compose.yml | {{Present / Missing / Generated}} |
| CI/CD pipeline     | {{Present / Missing / Generated}} |
| Helm/K8s manifests | {{Present / Missing / N/A}}       |
| DB migrations      | {{Present / Missing / Generated}} |

## Code Quality

- **Constitution violations**: {{count}}
- **Stub/TODO methods**: {{count}}
- **Layer boundary violations**: {{count}}
- **Traceability gaps**: {{count}} methods missing BR-xxx reference

{{If violations: list top 5 with file:line}}

## Summary

{{1-2 sentence overall assessment — what's good, what needs attention}}
