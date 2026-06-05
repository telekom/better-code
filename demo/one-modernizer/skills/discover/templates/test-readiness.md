# Test Asset Inventory & Migration Validation Readiness

## Test Coverage Summary

| Metric                      | Value     |
| --------------------------- | --------- |
| Total source files          | {{count}} |
| Test files                  | {{count}} |
| Production files with tests | {{count}} |
| Estimated coverage          | {{%}}     |

## Test Frameworks Detected

| Framework | Files Using | Language | Notes            |
| --------- | ----------- | -------- | ---------------- |
| {{name}}  | {{count}}   | {{lang}} | {{any concerns}} |

## Fixture/Golden File Assets

| Directory | Type                      | File Count | Description        |
| --------- | ------------------------- | ---------- | ------------------ |
| {{path}}  | {{fixtures/golden/mocks}} | {{count}}  | {{what they test}} |

## Coverage Gaps (Untested Modules)

| Module/Directory | Files | Risk Assessment                     |
| ---------------- | ----- | ----------------------------------- |
| {{name}}         | {{n}} | {{high — no regression safety net}} |

## Integration Test Infrastructure

| Component         | Exists? | Location  | Notes         |
| ----------------- | ------- | --------- | ------------- |
| Test database     | {{y/n}} | {{where}} | {{schema?}}   |
| Mock services     | {{y/n}} | {{where}} | {{coverage}}  |
| CI pipeline       | {{y/n}} | {{tool}}  | {{status}}    |
| Performance tests | {{y/n}} | {{where}} | {{baseline?}} |

## Migration Validation Strategy

### Pre-Migration Baseline

- [ ] Capture current test pass/fail status
- [ ] Record performance baselines for hot paths
- [ ] Snapshot reconciliation reports for batch outputs
- [ ] Document expected behavior for critical business rules

### Post-Migration Validation

- [ ] Run existing test suites against migrated code
- [ ] Compare batch output datasets (byte-for-byte or field-level)
- [ ] Replay production traffic against new system (shadow mode)
- [ ] Verify audit trail continuity
- [ ] Performance comparison against baseline

### Gaps Requiring New Tests

| Area       | What's Missing          | Priority         | Effort   |
| ---------- | ----------------------- | ---------------- | -------- |
| {{module}} | {{type of test needed}} | {{high/med/low}} | {{days}} |
