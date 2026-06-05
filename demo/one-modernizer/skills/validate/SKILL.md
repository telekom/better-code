---
name: validate
description: "Post-implementation quality gates with self-healing fix loop. Verifies generated code compiles, tests pass, APIs respond, contracts are complete, and spec coverage is 100%. Automatically fixes issues and re-verifies until all checks pass or no progress is made. Run after 'implement'."
---

# Validate Implementation

You are a quality gate enforcer with self-healing capability. Run all checks, fix what fails, re-run until green — or until stuck.

## Supporting Files

- **References**: Quality standards
  - [references/quality-gates.md](references/quality-gates.md) — What must pass before code is considered done
- **Templates**: Output format
  - [templates/validation-report.md](templates/validation-report.md) — Final quality report template
- **Scripts**: Automated checks
  - `scripts/validate_build.py` — Attempt build, parse errors, report
  - `scripts/validate_contracts.py` — Check OpenAPI/AsyncAPI completeness against blueprint

---

## Step 1: Locate Implementation Output

Use the `target_dir` from the injected pipeline state.

If not present, fall back to `./target/<feature>/` or `./target/`, then ask the user.

---

## Step 2: Run All Checks (Detect Phase)

Run each check and **collect failures into a list** — do NOT fix anything yet. Just detect.

### Check A: Build

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate_build.py <project-dir>
```

### Check B: Unit Tests

```bash
# Java/Gradle
cd <project-dir> && ./gradlew test --tests '*Unit*' --tests '*Test' -x integrationTest 2>&1

# Go
cd <project-dir> && go test -short ./... 2>&1

# Python
cd <project-dir> && pytest tests/ -m "not integration" --tb=short 2>&1

# .NET
cd <project-dir> && dotnet test --filter "Category!=Integration" 2>&1
```

### Check C: Infrastructure Up

```bash
cd <project-dir> && docker-compose up -d 2>&1
# Wait for healthy
```

If docker unavailable → mark integration/startup/API checks as SKIPPED (not FAIL).

### Check D: Database Migrations

```bash
# Apply migrations against running DB
# Java: ./gradlew flywayMigrate
# Go: migrate -path migrations -database "$DB_URL" up
# Python: alembic upgrade head
```

### Check E: Integration Tests

```bash
# Java: ./gradlew integrationTest
# Go: go test -run Integration ./...
# Python: pytest tests/ -m integration
```

### Check F: Application Startup

```bash
# Start app in background, wait for health endpoint
cd <project-dir> && <start-command> &
APP_PID=$!
sleep 10
curl -sf http://localhost:8080/actuator/health || curl -sf http://localhost:8080/health
```

### Check G: REST API Tests

For each endpoint in blueprint APIs:

- Send valid request → expect 2xx
- Send empty/invalid request → expect 400 (not 500)
- Request non-existent resource → expect 404
- Any 500 = FAIL

### Check H: Cleanup

```bash
kill $APP_PID 2>/dev/null
cd <project-dir> && docker-compose down -v 2>/dev/null
```

### Check I: Spec Coverage

```bash
python3 ${CLAUDE_SKILL_DIR}/../implement/scripts/check_coverage.py .migration/implement/<feature>/
```

### Check J: Contracts

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate_contracts.py <project-dir>
```

### Check K: Infrastructure Artifacts

- Dockerfile exists (per service)
- docker-compose.yml exists
- CI/CD pipeline exists
- Helm charts (if K8s target)
- DB migrations cover all data model tables

### Check L: Code Quality

- No TODO/FIXME in business logic
- No empty method bodies
- Naming conventions followed
- Layer boundaries clean
- BR-xxx traceability comments present

---

## Step 3: Fix Loop

```
failures = collect_all_failures_from_step_2()
previous_count = infinity
fix_log = []

LOOP:
  if len(failures) == 0:
    → PASS. Go to Step 4.

  if len(failures) >= previous_count:
    → STUCK (no progress). Go to Step 4 with FAIL.

  previous_count = len(failures)

  for each failure:
    diagnose(failure)  → identify root cause file:line
    fix(failure)       → edit the source file
    log(fix)           → append to fix_log

  re-run ONLY the checks that failed (not all checks)
  failures = collect_new_failures()

  GO TO LOOP
```

### Fix Strategies

| Failure Type                         | Diagnosis                            | Fix Action                                       |
| ------------------------------------ | ------------------------------------ | ------------------------------------------------ | ----------- |
| Build: missing import                | Compiler output → file:line          | Add the import statement                         |
| Build: type mismatch                 | Expected vs actual type              | Cast, change type, or fix assignment             |
| Build: undefined symbol              | Missing class/method                 | Generate it or fix the reference                 |
| Build: syntax error                  | Parser output → file:line            | Fix syntax                                       |
| Unit test: NPE/null                  | Missing mock setup                   | Add `when(...).thenReturn(...)` or equivalent    |
| Unit test: assertion failed          | Expected vs actual values            | Check spec.json → fix test OR fix implementation |
| Unit test: missing dependency        | Bean/injection not wired             | Add @Mock or constructor setup                   |
| Integration test: connection refused | DB/broker not started                | Restart docker-compose, increase wait time       |
| Integration test: table not found    | Migration not applied                | Run migration, or fix DDL                        |
| Integration test: data mismatch      | Wrong test data setup                | Fix test fixture                                 |
| Startup: bean not found              | Missing @Component/@Service          | Add annotation                                   |
| Startup: config missing              | Property not in application.yml      | Add property with sensible default               |
| Startup: port in use                 | Previous run leaked                  | `lsof -ti:8080                                   | xargs kill` |
| API: 500 error                       | Unhandled exception in handler       | Add try/catch or fix null check                  |
| API: wrong status code               | Controller returning wrong status    | Fix @ResponseStatus or ResponseEntity            |
| API: wrong response body             | DTO mapping incorrect                | Fix the mapping method                           |
| Coverage: BR-xxx not implemented     | Rule exists in spec but no code      | Generate the implementing method                 |
| Coverage: TC-xxx no test             | Test case in spec but no test method | Generate the test                                |
| Contract: OpenAPI missing            | No openapi.yaml                      | Generate from controller annotations             |
| Contract: event schema missing       | No AsyncAPI/Avro                     | Generate from event publisher                    |
| Infra: no Dockerfile                 | File doesn't exist                   | Generate multi-stage Dockerfile                  |
| Infra: no CI/CD                      | Pipeline file missing                | Generate GitHub Actions / GitLab CI              |
| Quality: empty method body           | Stub implementation                  | Implement the logic from spec.json               |
| Quality: missing BR-xxx ref          | No traceability comment              | Add `// Implements: BR-xxx`                      |

### Priority Order for Fixes

Fix in this order (upstream fixes often resolve downstream failures):

1. Build errors (nothing else works if it doesn't compile)
2. Missing infrastructure/contracts (generate them)
3. Code quality / empty stubs (implement the logic)
4. Unit test failures (after logic is implemented)
5. Migration issues (fix DDL)
6. Integration test failures
7. Startup issues
8. API test failures
9. Coverage gaps (generate missing tests last)

---

## Step 4: Generate Report

After the loop exits (PASS or STUCK):

Write `.migration/validate/<feature>/fix-log.json`:

```json
{
  "feature": "<name>",
  "iterations": [
    {
      "iteration": 1,
      "failures_before": 15,
      "fixes_applied": 12,
      "failures_after": 5
    },
    {
      "iteration": 2,
      "failures_before": 5,
      "fixes_applied": 4,
      "failures_after": 1
    },
    {
      "iteration": 3,
      "failures_before": 1,
      "fixes_applied": 1,
      "failures_after": 0
    }
  ],
  "total_fixes": 17,
  "total_iterations": 3,
  "final_status": "PASS"
}
```

Write `.migration/validate/<feature>/report.md` using [templates/validation-report.md](templates/validation-report.md):

- Build status
- Test results (unit + integration)
- API test results
- Spec coverage
- Contract completeness
- Infrastructure checklist
- Code quality
- Fix loop summary (iterations, fixes applied)
- **Verdict: PASS / PASS WITH WARNINGS / FAIL**

Also write `.migration/validate/<feature>/report.json` (machine-readable).

Update `.migration/index.json`: set `pipeline.validate.status` and `features.<name>.stage`.

---

## Step 5: Present Results

**If PASS:**

- "All checks pass. Implementation is complete and ready for human review/PR."

**If PASS WITH WARNINGS:**

- List warnings (non-critical: optional infra missing, advisory quality findings)
- "These are non-blocking. Proceed to review?"

**If FAIL (stuck):**

- Show remaining failures with file:line references
- Show what was fixed successfully (N fixes across M iterations)
- "These N issues need manual attention. Here's what I couldn't resolve:"
- List each remaining failure with diagnosis

---

## Rules

- Never mark PASS if build fails
- Never mark PASS if spec coverage < 100%
- PASS WITH WARNINGS: build passes + tests pass + coverage 100%, but optional infra/contracts/quality findings remain
- The fix loop stops on NO PROGRESS (same or more failures), never on a fixed iteration count
- Always fix the highest-priority failures first (build before tests before coverage)
- When fixing a test: check spec.json to determine if the TEST is wrong or the IMPLEMENTATION is wrong. Spec is truth.
- Log every fix — the fix-log is an audit trail of what was auto-corrected
