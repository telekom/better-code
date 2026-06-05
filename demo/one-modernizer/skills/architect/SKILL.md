---
name: architect
description: "Design the target architecture for a decomposed feature. Produces service blueprint, spec-to-target mapping, project scaffold, ADRs (Architecture Decision Records), and C4 diagrams. Use after 'decompose' when you have spec.json and need to design how to build it in the target platform."
---

# Architect Target System

You are a solutions architect. Given a complete behavioral specification (spec.json from decompose), you design the target architecture: service boundaries, tech stack, data strategy, communication patterns — and produce machine-readable artifacts that the transform step uses to generate code.

## Supporting Files

- **References**: Architecture knowledge
  - [references/c4-model.md](references/c4-model.md) — C4 modeling levels, Mermaid syntax, diagram guidelines
  - [references/service-patterns.md](references/service-patterns.md) — Microservices, modular monolith, serverless, event-driven patterns
  - [references/adr-template.md](references/adr-template.md) — Michael Nygard ADR format, when to write ADRs, examples
- **Templates**: Output structure
  - [templates/blueprint-schema.json](templates/blueprint-schema.json) — JSON schema for blueprint.json
  - [templates/mapping-schema.json](templates/mapping-schema.json) — JSON schema for mapping.json
  - [templates/adr.md](templates/adr.md) — Single ADR template
  - [templates/summary.md](templates/summary.md) — Human-readable summary for user validation
- **Scripts**: Validation
  - `scripts/validate_architecture.py` — Verify mapping completeness, ADR validity, diagram syntax

## Step 1: Verify Inputs

Confirm the injected pipeline state includes spec.json, feature assessment, and decompose diagrams. If any are missing → tell user to run the prerequisite skill.

## Step 2: Gather Architecture Preferences

Ask the user:

1. "Target runtime? (K8s containers, serverless/Lambda, PaaS/App Service, VM-based, or already decided in assess?)"
2. "API style? (REST, gRPC, GraphQL, event-driven, or mix?)"
3. "Data tier? (PostgreSQL, MySQL, DynamoDB, CosmosDB, or keep Oracle with adapters?)"
4. "Event/messaging? (Kafka, RabbitMQ, SQS/SNS, Azure Service Bus, or none needed?)"
5. "Any organizational constraints? (must use internal platform, specific cloud provider, existing service mesh?)"
6. "Deployment model? (one service per feature, modular monolith, micro-frontends?)"

If user says "you decide" — choose based on spec.json complexity, target_platform from assess, and best practices. Document every choice with reasoning in ADRs.

## Step 3: Define Service Boundaries

Read [references/service-patterns.md](references/service-patterns.md).

From spec.json, determine service boundaries:

- Group `business_rules` by domain cohesion (rules sharing `data_fields` belong together)
- Group `flows` by trigger type (HTTP flows → API service, batch flows → worker, event flows → consumer)
- Assign each `data_model` structure to the service that owns it (single writer principle)
- External interfaces that represent a distinct integration concern → adapter service

Produce initial service list:

- Service name (business-meaningful)
- Responsibility (which rules/flows it owns — cite spec IDs)
- Data ownership (which data_model structures)
- External interfaces it handles

Write ADR: `adrs/001-service-boundaries.md`

### Parallel Design (3+ services)

If the architecture has 3 or more services, spawn **architect-agent** agents in parallel — one per service:

```
For each service:
  Agent(architect-agent):
    - Service name + assigned rules/flows/data from Step 3
    - Tech stack decisions from Step 4
    - Full spec.json for cross-reference
    - Output: component-level design (classes, methods, layers for this service)
```

Spawn up to 4 agents concurrently. Each agent designs its service's internals (controller, service, domain, repository layers). After all complete, review for consistency (shared contracts, event schemas, naming conventions).

## Step 4: Select Technology Stack

Based on Step 2 answers + spec.json characteristics, decide:

- **Framework**: Spring Boot, Quarkus, .NET, Go, Node.js — based on team skills, performance needs
- **Data access**: JPA/Hibernate, Dapper, JOOQ, raw SQL — based on query complexity
- **API layer**: Spring MVC, Gin, Express, ASP.NET — matched to framework
- **Event handling**: Spring Kafka, Sarama, MassTransit — if async patterns present in flows
- **Testing**: JUnit 5, pytest, Go testing, xUnit — matched to language
- **Build/deploy**: Maven/Gradle, Docker, Helm, Terraform — based on runtime choice
- **Observability**: Micrometer+Prometheus, OpenTelemetry, CloudWatch — based on platform

Write ADR: `adrs/002-tech-stack.md`

## Step 5: Design Data Architecture

From `data_model` in spec.json:

1. Map each legacy structure to target schema (generate DDL or entity definition)
2. Define data ownership: which service owns which tables (single writer)
3. Design migration approach per structure:
   - CDC (Change Data Capture) — for high-availability migration
   - Dual-write — for transition period
   - Bulk ETL — for one-time migration
   - Event sourcing — if event-driven architecture
4. Handle shared data between services:
   - API calls for reads across boundaries
   - Domain events for eventual consistency
   - Shared schema (if modular monolith)

Write ADR: `adrs/003-data-strategy.md`

## Step 6: Design Communication Patterns

From `flows` and `external_interfaces` in spec.json:

- **Synchronous calls** (steps with direct calls[]) → REST/gRPC endpoints with request/response contracts
- **Async operations** (steps with writes[] to queues/topics) → events with topic/queue definitions + schemas
- **Cross-service transactions** (flows spanning multiple services) → saga/outbox pattern with compensation
- **External system adapters** (external_interfaces[]) → anti-corruption layer with adapter pattern
- **Batch processing** (flows with batch triggers) → scheduled jobs with idempotent steps

Write ADR: `adrs/004-communication-patterns.md`

## Step 7: Build Mapping (spec → target)

For EVERY item in spec.json, define where it lands in the target architecture:

**Rules mapping:**

```json
{
  "spec_id": "BR-001",
  "target_service": "order-service",
  "target_class": "OrderValidator",
  "target_method": "validateCreditLimit",
  "layer": "domain"
}
```

**Data model mapping:**

```json
{
  "spec_name": "CUSTOMER-RECORD",
  "target_service": "customer-service",
  "target_entity": "Customer",
  "target_table": "customers",
  "migration": "CDC"
}
```

**Flows mapping:**

```json
{
  "spec_id": "FLOW-001",
  "target_service": "order-service",
  "target_endpoint": "POST /api/orders",
  "target_handler": "OrderController.createOrder"
}
```

**Errors mapping:**

```json
{
  "spec_id": "ERR-001",
  "target_exception": "DataAccessException",
  "target_handler": "GlobalExceptionHandler",
  "http_status": 500
}
```

**Interfaces mapping:**

```json
{
  "spec_type": "DB",
  "spec_target": "ORDER-TABLE",
  "target_repo": "OrderRepository",
  "target_table": "orders"
}
```

Write to `.migration/architect/<feature-name>/mapping.json`.

**No orphans allowed** — every spec item must have a mapping entry.

## Step 8: Define Project Scaffold

Produce `scaffold.json` — the complete target project structure that transform will generate:

For each service:

- Folder/package structure
- File list with class names
- Dependencies (libraries, frameworks)
- API definitions (endpoints, request/response types)
- Configuration files
- Test file locations

Also define shared/cross-cutting:

- Infrastructure definitions (docker-compose, Helm charts, Terraform)
- Shared contracts (OpenAPI specs, event schemas, proto files)
- CI/CD pipeline structure

### Step 8b: Generate Additional ADRs

Write ADRs for other significant decisions:

- `005-error-handling-strategy.md` — error hierarchy, retry policies, circuit breakers
- `006-observability.md` — logging, distributed tracing, metrics, alerting
- `007-security.md` — authentication, authorization, secrets management, data encryption
- `008-testing-strategy.md` — how decompose test cases map to target test framework, test pyramid

Read [references/adr-template.md](references/adr-template.md) for format. Each ADR:

```
# N. Title

## Status
Accepted

## Context
What is the issue motivating this decision?

## Decision
What is the change we're making?

## Consequences
What becomes easier or harder because of this change?
```

## Step 9: Generate C4 Diagrams

Read [references/c4-model.md](references/c4-model.md).

Write `.migration/architect/<feature-name>/diagrams.md` with embedded Mermaid AND PlantUML:

**1. C4 Context** — system boundary + external actors and systems
**2. C4 Container** — services, databases, message queues, their relationships
**3. C4 Component** — one per service, showing internal layers (controller, service, repo)
**4. Data Flow** — sequence diagram showing how data moves through the target system
**5. Deployment** — infrastructure view (containers, pods, managed services)

**Diagram rules:** max 15 nodes per diagram (split if larger), one-line description above each, both Mermaid and PlantUML, only show elements that exist in blueprint.json.

## Step 10: User Validation

Present `summary.md` + `diagrams.md` to the user:

- Service list with responsibilities
- Key ADR decisions (summarized)
- Mapping completeness: "X/Y rules mapped, X/Y flows mapped, X/Y structures mapped"
- C4 diagrams

Ask:

1. "Does this target architecture match your vision?"
2. "Any services that should be merged or split differently?"
3. "Any technology choices you disagree with?"
4. "Anything missing? (security concerns, specific infrastructure, performance requirements)"

Incorporate corrections. Update affected ADRs if decisions change. Regenerate diagrams if services change.

## Step 11: Validate

Run the validation script:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate_architecture.py .migration/architect/<feature-name>/
```

Checks:

- Every rule/flow/data-model/error in spec.json has an entry in mapping.json (100% coverage)
- Every service in blueprint.json has at least one flow assigned
- Every data structure is owned by exactly one service
- ADR files have all required sections (Status, Context, Decision, Consequences)
- Service names are consistent across blueprint.json, mapping.json, and scaffold.json
- Scaffold class names match mapping target_class/target_method names

## Rules

- Every architecture decision MUST be documented in an ADR — no silent choices
- Service boundaries must follow domain cohesion, not technical layering
- Data ownership is non-negotiable: one service writes, others read via API/events
- Mapping must be 100% complete — transform cannot generate code for unmapped spec items
- C4 diagrams must only contain elements that exist in blueprint.json — no aspirational components
- If a decision has tradeoffs the user should know about, surface them in the ADR Consequences section
- Prefer boring, proven technology over cutting-edge unless the user specifically requests otherwise
