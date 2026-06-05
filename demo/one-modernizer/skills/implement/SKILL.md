---
name: implement
description: "Generate target code from architecture specifications using GitHub's spec-kit methodology. Follows all 6 spec-kit phases: constitution, specify, clarify, plan, tasks, implement. Produces compilable, tested code with full traceability to behavioral spec. Use after 'architect' when you have blueprint.json + mapping.json and want to generate the target project."
---

# Implement (spec-kit style)

You are a code generation engine following GitHub's spec-kit methodology. Given architecture artifacts (blueprint, mapping, scaffold, spec), you produce complete, compilable, tested target code — one file at a time, verified between each, with full traceability back to the behavioral specification.

## Supporting Files

- **References**: Implementation knowledge
  - [references/spec-kit-workflow.md](references/spec-kit-workflow.md) — Spec-kit methodology adapted for migration
  - [references/code-patterns/dotnet.md](references/code-patterns/dotnet.md) — .NET generation patterns
  - [references/verification-rules.md](references/verification-rules.md) — What to check after each generated file
- **Templates**: Output structure
  - [templates/task-schema.json](templates/task-schema.json) — JSON schema for task list
  - [templates/coverage-report.md](templates/coverage-report.md) — Progress report template
- **Scripts**: Automation
  - `scripts/generate_tasks.py` — Break mapping into ordered implementation tasks
  - `scripts/check_coverage.py` — Verify all spec items have generated code

---

## Phase 1: Constitution (`/speckit.constitution`)

### Step 1: Verify Inputs & Detect Template

Confirm the injected pipeline state includes spec.json, blueprint.json, mapping.json, and ADRs. If any are missing → tell user to run the prerequisite skill.

Ask user:

1. "Where should I generate the target project? (provide a path or I'll use `./target/<feature-name>/`)"
2. "Do you have a template or reference project I should use as the base? (existing repo, org starter template, or a project whose style/structure I should match — provide path or 'no')"

**If user provides a template/reference project:**

- Read its structure (packages, layers, naming, config patterns)
- Read 3-5 representative files to extract conventions (how they write controllers, services, tests, configs)
- Use it as the **source of truth for constitution** — override scaffold.json layout with the template's actual structure
- Copy non-generated infrastructure (build files, CI/CD, Docker, shared configs) from the template as the starting point
- Generate business logic INTO the template's structure rather than inventing a new one

**If user says no** → generate from scratch using scaffold.json and code-patterns references as before.

### Step 2: Write Constitution

Synthesize `.migration/implement/<feature>/constitution.md` — the governing principles every generated file must follow:

- **Language & framework conventions** — from tech stack ADR (e.g., "Spring Boot 3, Java 21, records for DTOs")
- **Naming rules** — from scaffold (e.g., "PascalCase classes, camelCase methods, snake_case DB columns")
- **Layer responsibilities** — from mapping layer assignments:
  - Controllers: HTTP concern only, no business logic
  - Services: orchestration and business logic
  - Domain: entities, value objects, rules
  - Repositories: data access only
- **Error handling contract** — from ADR-005
- **Testing contract** — from ADR-008
- **Code quality rules** — self-documenting code, methods < 30 lines, single responsibility
- **Traceability rule** — every method implementing a business rule references its BR-xxx ID

Present constitution to user: "Here are the implementation principles I derived. Anything to add or change?"

Wait for confirmation before proceeding.

---

## Phase 2: Specify (`/speckit.specify`)

### Step 3: Create Implementation Specifications

For each service in blueprint.json, produce a detailed implementation spec at the class/method level.

Read the code-patterns reference for the target stack:

- .NET → [references/code-patterns/dotnet.md](references/code-patterns/dotnet.md)

For each mapped item, define:

- Exact class name, package/namespace, file path
- Method signature (parameters, return type, exceptions thrown)
- Which spec items it implements (BR-xxx, FLOW-xxx)
- Dependencies (what other classes it needs injected/imported)
- Interface contracts (what it exposes, what it consumes)

Store in `.migration/implement/<feature>/specs/<service-name>.json`.

---

## Phase 3: Clarify (`/speckit.clarify`)

### Step 4: Identify and Resolve Ambiguities

Review every implementation spec for:

- **Ambiguous rules** — spec items with confidence "inferred" or "ambiguous" in spec.json
- **Missing information** — return types that can't be determined, unclear error behavior
- **Design conflicts** — two rules that seem contradictory, circular dependencies between classes
- **Edge cases** — what happens at boundaries (null, empty, max values, concurrent access)
- **Implicit behavior** — things the legacy does that aren't captured as explicit rules (default values, implicit type conversions)

For each ambiguity:

1. Try to resolve from spec.json context (other rules, flows, data model may clarify)
2. Check the original source code (file:line references in spec.json)
3. If still unclear → collect and ask the user in one batch

Present all ambiguities: "I found N questions about the implementation. Here they are:"

Store resolutions in `.migration/implement/<feature>/clarifications.json`.

---

## Phase 4: Plan (`/speckit.plan`)

### Step 5: Create Implementation Plan

Define the execution strategy in `.migration/implement/<feature>/plan.md`:

- **Service order** — which service to build first (least dependencies → most)
- **Layer order within each service** — infrastructure → data → domain → API → tests
- **Parallel opportunities** — independent services that can generate concurrently
- **Verification checkpoints** — compile after every N tasks, or after each layer completes
- **Risk mitigation** — complex/uncertain parts first (fail fast)
- **Estimated task count** — how many files to generate total

---

## Phase 5: Tasks (`/speckit.tasks`)

### Step 6: Break Down into Ordered Tasks

Run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/generate_tasks.py .migration/implement/<feature>/
```

This reads implementation specs and produces `.migration/implement/<feature>/tasks.json` — an ordered task list:

Each task:

- `id`: T-001, T-002, ...
- `type`: entity, repository, service, controller, dto, event, config, test, migration, infra, contract
- `description`: what to generate
- `target_file`: exact output path
- `spec_refs`: which spec items this implements
- `depends_on`: task IDs that must complete first
- `service`: which service this belongs to
- `layer`: which architectural layer

**Ordering rules** (dependency-first):

1. Infrastructure — build files, configs, Docker
2. Data layer — entities, migrations, repositories
3. Domain layer — services, validators, business logic
4. API layer — controllers, DTOs, event handlers
5. Cross-cutting — error handlers, security config, observability
6. Tests — unit tests, integration tests
7. Contracts — OpenAPI specs, event schemas

---

## Phase 6: Implement (`/speckit.implement`)

### Step 7: Execute Tasks

For each task in order:

1. **Read the task** — target file, spec refs, dependencies
2. **Read the spec items** — full business rules/flows/data from spec.json
3. **Read the constitution** — conventions to follow
4. **Read the implementation spec** — exact signatures, dependencies
5. **Generate the file** — write complete, compilable source code
6. **Verify** — apply all checks from [references/verification-rules.md](references/verification-rules.md)
7. **Log** — append to `.migration/implement/<feature>/task-log.json`

**If verification fails**: fix the file, re-verify. Max 3 attempts before flagging to user.

### Step 7b: Parallel Execution (multiple services)

If the architecture has 3+ independent services, spawn **implementer** agents in parallel:

```
For each independent service:
  Agent(implementer):
    - Service name + its task subset (from tasks.json)
    - Constitution (conventions/constraints)
    - Implementation spec for this service
    - Spec items assigned to this service (from spec.json)
    - Target directory path
    - Output: generated files + task-log entries for this service
```

Spawn up to 4 agents concurrently. Within each agent, tasks execute sequentially (layer order). After all agents complete, verify cross-service references (shared contracts, event schemas).

### Step 8: Generate Tests

For each TC-xxx in spec.json test_cases:

1. Look up mapping → target test class/method
2. Read the spec: input, expected_output, type, preconditions
3. Generate test method:
   - **Arrange**: set up input data from spec
   - **Act**: call the target handler/service method
   - **Assert**: verify expected_output matches actual

Test type → framework mapping:

- `unit` → isolated test, mocked dependencies
- `integration` → real DB (Testcontainers / in-memory), real event bus
- `boundary` → parameterized/table-driven test with edge values
- `negative` → test expecting specific exception/error code

### Step 9: Generate Infrastructure

From scaffold.json shared section:

- `docker-compose.yml` — local dev (DB, broker, all services)
- `Dockerfile` per service — multi-stage build optimized for target language
- `helm/` charts or K8s manifests (if K8s deployment)
- CI/CD pipeline (GitHub Actions / GitLab CI / Azure Pipelines — ask if unclear)
- Database migration scripts — from data-model.json field definitions

### Step 10: Generate Contracts

From blueprint.json APIs and events:

- **OpenAPI spec** (openapi.yaml) — from mapped endpoints
- **Event schemas** (Avro / JSON Schema / AsyncAPI) — from events_published
- **Proto files** (if gRPC) — from service interface definitions
- **Shared DTOs** — cross-service request/response types

### Step 11: Verify Coverage

Run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/check_coverage.py .migration/implement/<feature>/
```

Checks:

- Every BR-xxx from spec.json has a method implementing it
- Every FLOW-xxx has a handler/endpoint
- Every TC-xxx has a test method
- Every data_model structure has an entity + migration
- Every ERR-xxx has an exception class + handler
- Every external interface has an adapter/client

Report uncovered items. If gaps remain → generate additional tasks and execute them.

### Step 12: User Review

Present:

- Coverage report (% of spec implemented)
- Generated project tree (directory structure)
- Items that couldn't be auto-generated (flagged for manual work)
- Task log summary (N files generated, M verified, K warnings)

Ask:

1. "Generated code covers X% of the spec. Want me to attempt the remaining?"
2. "Any files to regenerate differently?"
3. "Ready to try compiling?"

### Step 13: Build Verification

Attempt to build/compile the generated project:

```bash
# Detect and run appropriate build command based on tech stack
```

If build fails:

- Parse error messages
- Identify the offending file(s)
- Fix compilation errors (missing imports, type mismatches, etc.)
- Re-run build
- Max 5 iterations before escalating to user

If build succeeds → run unit tests. Report results.

---

## Rules

- **File-at-a-time for business logic** — domain services, validators, complex controllers: generate ONE file, verify, log, then next. This is where bugs hide.
- **Batch-OK for boilerplate** — entities, DTOs, configs, migrations, Dockerfiles: may batch-generate in groups of up to 10, then verify the batch together. These are mechanical translations.
- **Traceability is non-negotiable** — every business method must reference its source BR/FLOW/ERR ID
- **Constitution is law** — no file may violate constitution conventions (naming, structure, layers)
- **Dependencies forward only** — a file may only import/reference files generated in earlier tasks
- **Spec-complete** — the generated code must implement 100% of spec.json items (not 80%, not "most")
- **Tests are mandatory** — every business rule gets at least one test. No untested logic.
- **No dead code** — don't generate placeholder methods, TODO comments, or stub implementations
- **Self-documenting** — code should be readable without comments. Names convey intent.

## Hard Checkpoints (STOP — do NOT proceed without completing)

These are non-skippable gates. The LLM MUST complete each before moving to the next phase:

| After Phase      | Checkpoint                 | Must Exist                                                                    |
| ---------------- | -------------------------- | ----------------------------------------------------------------------------- |
| Phase 1          | User confirms constitution | `.migration/implement/<feature>/constitution.md`                              |
| Phase 3          | All ambiguities resolved   | `.migration/implement/<feature>/clarifications.json`                          |
| Phase 5          | Tasks generated            | `.migration/implement/<feature>/tasks.json` (run `generate_tasks.py`)         |
| Phase 6, Step 7  | Task log exists            | `.migration/implement/<feature>/task-log.json` (append after each file/batch) |
| Phase 6, Step 11 | Coverage verified          | Run `check_coverage.py`, report results to user                               |
| Phase 6, Step 13 | Build attempted            | Run the build command, report success/failure                                 |

If a checkpoint file doesn't exist when the next phase starts, STOP and go back to create it. Do not skip.

## When to ask vs. when to proceed

- **Ask**: ambiguous rules, conflicting requirements, user hasn't confirmed constitution
- **Proceed silently**: boilerplate generation, mechanical type mappings, obvious error handlers
- **Report at end**: coverage gaps, build failures, skipped test cases (present in Step 12 review)
