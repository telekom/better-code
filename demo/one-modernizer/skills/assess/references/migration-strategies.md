# Migration Strategies

## The 6Rs

| Strategy       | Definition                                    | When to Choose                                                                                                                  |
| -------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Rewrite**    | Build from scratch on new platform            | Complex + poorly tested + platform-incompatible + business-critical. Last resort — highest cost/risk but sometimes only option. |
| **Refactor**   | Restructure existing code for target platform | Good business logic worth keeping, moderate complexity, decent test coverage. Most common for core features.                    |
| **Replace**    | Swap with COTS/SaaS product                   | Feature matches a well-known product (auth→Okta, email→SendGrid, CRM→Salesforce). Build vs buy favors buy.                      |
| **Replatform** | Lift-and-shift with minimal changes           | Works fine, just needs infrastructure change. Standard patterns, no platform-specific coupling.                                 |
| **Retain**     | Keep as-is                                    | Low risk, well-tested, no platform incompatibility, not worth the investment to change.                                         |
| **Retire**     | Decommission                                  | Dead code, replaced by another system, no users, no regulatory requirement to keep.                                             |

## Sequencing Strategies

### Strangler Fig

Incremental replacement. Route traffic from legacy to new service endpoint by endpoint.

**When**: Large monolith with clear API boundaries, need continuous delivery during migration, can't afford big-bang cutover.

**How**:

1. Place a facade/router in front of legacy
2. Build new service for one route
3. Shift traffic to new service
4. Repeat until legacy has no traffic
5. Decommission legacy

**Risks**: Facade complexity, data consistency during dual-operation, long migration tail.

### Domain-First

Identify bounded contexts (DDD), migrate each domain independently.

**When**: System has identifiable business domains with limited cross-domain coupling. Teams align to domains.

**How**:

1. Map features to domains
2. Identify domain boundaries and anti-corruption layers needed
3. Migrate one domain at a time
4. Use events/APIs for cross-domain communication

**Risks**: Hidden coupling between domains, shared database, cross-cutting concerns (auth, logging).

### Data-First

Migrate the database layer first, then services one by one.

**When**: Database is the primary coupling point. Multiple services share tables. Schema is the hardest part.

**How**:

1. Design target schema
2. Set up CDC (Change Data Capture) from legacy to target DB
3. Migrate services one by one to read/write target DB
4. Cut over when all services migrated

**Risks**: Schema translation errors, data loss during sync, performance during dual-write.

### Value-First

Migrate highest business-value features first regardless of technical ordering.

**When**: Strong business pressure for quick ROI, stakeholders need visible progress, features are relatively independent.

**How**:

1. Rank features by business value
2. Build adapters where dependency order conflicts with value order
3. Accept some technical debt (adapters) for faster value delivery

**Risks**: Adapter proliferation, technical debt accumulation, may paint yourself into a corner.

### Risk-First

Tackle hardest/riskiest features first to fail fast.

**When**: High uncertainty, want to surface problems early, team is strong enough to handle the hard stuff first.

**How**:

1. Identify highest-risk features (complex, poorly understood, critical)
2. Prototype/spike the hardest migration first
3. If it works, rest is lower risk. If not, learn early.

**Risks**: Team morale if first attempt is very hard, delayed visible value.

### Hybrid (Most Common)

Combine strategies. Typical: domain-first sequencing + strangler fig execution.

**When**: Real systems don't fit one pattern. Use domain analysis for sequencing, strangler for execution, value-first for prioritization within waves.

## Decision Tree

```
Is the system decomposable into clear domains?
├── Yes → Domain-First sequencing
│   └── Within each domain: Strangler Fig execution
└── No → Is there a shared database coupling everything?
    ├── Yes → Data-First (migrate DB, then services)
    └── No → Value-First prioritization
        └── With Risk-First ordering for equal-value features
```

## Handling Shared State

| Pattern                   | When                                            | How                                                                  |
| ------------------------- | ----------------------------------------------- | -------------------------------------------------------------------- |
| Database seam             | Shared tables between features                  | Introduce API layer over shared tables, route through it, then split |
| Event sourcing            | Features need eventual consistency              | Publish domain events, let each feature maintain its own projection  |
| Dual-write                | Transition period needs both systems in sync    | Write to both old and new, reconcile, then cut over                  |
| CDC (Change Data Capture) | Database migration while services still running | Stream changes from legacy DB to target DB                           |
| Anti-corruption layer     | New service calling legacy or vice versa        | Adapter that translates between old and new interfaces               |
| Feature flag              | Gradual traffic shift                           | Route % of traffic to new implementation, increase over time         |

## Common Anti-Patterns

- **Big bang cutover**: Migrating everything at once. Almost always fails for large systems.
- **Ignoring data**: Focusing on code migration while neglecting data migration strategy.
- **No rollback plan**: Each phase must be independently rollback-able.
- **Adapter debt**: Too many adapters without a plan to remove them.
- **Perfectionism**: Over-engineering the target before proving the migration works.
- **Boiling the ocean**: Trying to migrate AND modernize AND re-architect simultaneously.
