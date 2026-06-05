# Service Architecture Patterns

## Microservices

**When**: Large team (10+), independent deployment needed, distinct bounded contexts, polyglot requirements.

**Characteristics**:

- One service per bounded context
- Each service owns its data (separate DB or schema)
- Communication via APIs and events
- Independent deployment and scaling
- Service size: 1-3 developers can own it

**Data ownership**: Single writer principle — only one service writes to a table. Others read via API or subscribe to events.

**Pitfalls**:

- Distributed monolith (services coupled at deploy time)
- Chatty interfaces (too many synchronous calls)
- Shared database (defeats the purpose)
- Over-decomposition (50 services for 5 developers)

## Modular Monolith

**When**: Small team (3-8), features tightly coupled, shared database acceptable, deployment simplicity valued.

**Characteristics**:

- Single deployment unit
- Internal module boundaries (packages/namespaces)
- Shared database with schema-per-module
- In-process calls between modules
- Can evolve to microservices later by extracting modules

**Data ownership**: Each module owns a schema. Cross-module access via internal APIs (method calls), not direct table access.

**Pitfalls**:

- Boundary erosion over time (shortcuts through shared code)
- Hard to scale individual modules
- Single point of failure

## Serverless (FaaS)

**When**: Event-driven workloads, variable traffic, no infrastructure team, pay-per-use economics.

**Characteristics**:

- Function per flow/endpoint
- Managed infrastructure (Lambda, Cloud Functions, Azure Functions)
- Event triggers (HTTP, queue, schedule, storage)
- Stateless execution
- Auto-scaling to zero

**Data ownership**: Managed databases (DynamoDB, Cosmos, Firestore). State in external stores only.

**Pitfalls**:

- Cold start latency
- Vendor lock-in
- Complex local development
- 15-min execution limit (not for long batch)
- Distributed tracing harder

## Event-Driven Architecture

### Choreography

Each service reacts to events independently. No central coordinator.

**When**: Loose coupling, services don't need to know about each other, eventually consistent is OK.

```
OrderService → publishes OrderCreated
PaymentService → subscribes, processes payment, publishes PaymentCompleted
ShippingService → subscribes to PaymentCompleted, ships
```

### Orchestration

Central coordinator (saga) directs the flow.

**When**: Complex workflows with compensation, need visibility into flow state, strong consistency requirements.

```
OrderSaga:
  1. Call PaymentService.charge()
  2. If success → call ShippingService.ship()
  3. If failure → call PaymentService.refund() (compensation)
```

### Event Sourcing

Store events as the source of truth, derive state from event replay.

**When**: Audit trail required, temporal queries needed, complex domain with many state transitions.

### CQRS (Command Query Responsibility Segregation)

Separate write model (commands) from read model (queries).

**When**: Read and write patterns differ dramatically, complex queries, read-heavy workload.

## API Gateway Pattern

**When**: Multiple services need a single entry point, cross-cutting concerns (auth, rate limiting, logging).

**Responsibilities**:

- Request routing to backend services
- Authentication/authorization
- Rate limiting and throttling
- Request/response transformation
- API versioning
- SSL termination

**Options**: Kong, AWS API Gateway, Azure APIM, Envoy, Traefik

## Anti-Corruption Layer (ACL)

**When**: Integrating with legacy system during migration, external system with messy API, protecting domain model from external concepts.

**How**:

- Adapter that translates between legacy and target models
- Facade that simplifies legacy interface
- Maps legacy data types to target domain types
- Handles legacy error codes → target exceptions

## Choosing a Pattern

```
How many developers?
├── < 5 → Modular Monolith
├── 5-15 → Microservices (2-5 services)
└── 15+ → Microservices (domain-aligned)

Traffic pattern?
├── Steady → Containers (K8s)
├── Spiky/unpredictable → Serverless
└── Batch/scheduled → Worker services + scheduler

Consistency requirement?
├── Strong (ACID) → Single DB, saga with compensation
├── Eventual → Events + CQRS
└── Mixed → Synchronous for critical, async for rest

Integration complexity?
├── Many external systems → API Gateway + ACL
├── Few/simple → Direct integration
└── Legacy coexistence → Strangler Fig + ACL
```
