# Architecture Decision Records (ADRs)

## Michael Nygard Format

Every significant architecture decision gets documented as an ADR. The format:

```markdown
# N. Title

Short noun phrase. Example: "Use PostgreSQL for order data"

## Status

One of: Proposed | Accepted | Deprecated | Superseded by [ADR-NNN]

## Context

What is the issue that we're seeing that is motivating this decision or change?
Include forces at play (technical, political, social, project constraints).
Use neutral language — describe facts, not opinions.

## Decision

What is the change that we're proposing and/or doing?
State it as an active voice directive: "We will..." or "The system will..."

## Consequences

What becomes easier or more difficult to do because of this change?
Include both positive and negative consequences. Be honest about tradeoffs.
```

## When to Write an ADR

Write an ADR when:

- There are 2+ reasonable options and you chose one
- The decision is hard to reverse once code is written
- Future developers will ask "why did we do it this way?"
- The decision affects multiple services or teams
- You're rejecting an obvious/popular choice for good reasons

Do NOT write an ADR for:

- Trivial choices (variable naming, minor formatting)
- Decisions already mandated by organizational policy
- Temporary/experimental decisions that will be revisited

## Numbering Convention

Sequential, zero-padded: `001`, `002`, `003`, ...

Never reuse numbers. If an ADR is superseded, add "Superseded by ADR-NNN" to its Status.

## Common ADR Topics for Migration

| #   | Topic                  | Decision Area                                        |
| --- | ---------------------- | ---------------------------------------------------- |
| 001 | Service boundaries     | How to split the monolith                            |
| 002 | Technology stack       | Language, framework, libraries                       |
| 003 | Data strategy          | Database choice, migration approach, ownership       |
| 004 | Communication patterns | Sync vs async, protocols, contracts                  |
| 005 | Error handling         | Exception hierarchy, retry, circuit breaker          |
| 006 | Observability          | Logging, tracing, metrics stack                      |
| 007 | Security               | Auth mechanism, secrets, encryption                  |
| 008 | Testing strategy       | Test types, framework, coverage targets              |
| 009 | Deployment             | CI/CD, containerization, orchestration               |
| 010 | Migration coexistence  | How legacy and target run together during transition |

## Example ADR

```markdown
# 3. Use PostgreSQL for persistent storage

## Status

Accepted

## Context

The legacy system uses Oracle 12c for all data storage. We need to choose a target database for the migrated services. Key factors:

- 47 tables in this feature with complex relationships
- Heavy use of stored procedures (being moved to application layer per ADR-001)
- Need managed hosting option for cloud deployment
- Team has limited Oracle expertise but strong PostgreSQL experience
- License cost reduction is a migration driver

## Decision

We will use PostgreSQL 16 as the primary relational database for all migrated services. Specifically:

- Managed PostgreSQL (Cloud SQL / RDS) for production
- Local PostgreSQL via Docker for development
- Flyway for schema migrations (version-controlled DDL)

## Consequences

**Easier:**

- Zero license cost (vs. Oracle's per-core pricing)
- Team already knows PostgreSQL well — faster development
- Excellent cloud-managed options with automated backups, HA
- Rich ecosystem (PostGIS, pg_cron, logical replication)

**Harder:**

- Must translate Oracle-specific SQL (CONNECT BY → recursive CTE, NVL → COALESCE)
- No equivalent to Oracle Materialized Views with automatic refresh (use application-level caching)
- Partition syntax differs (declarative in PG, but less flexible than Oracle)
- Some PL/SQL bulk operations have no direct PG equivalent (use batch inserts)
```
