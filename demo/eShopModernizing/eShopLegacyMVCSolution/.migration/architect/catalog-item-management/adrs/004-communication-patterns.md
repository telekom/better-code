# 4. Communication Patterns

## Status

Accepted

## Context

All five flows (FLOW-001..005) are synchronous HTTP request/response interactions from a
browser to MVC actions. There are no batch flows, no message queues, and no cross-service
transactions in this feature. The only outbound reference is URL generation for the
picture route (owned by the Product Imagery feature).

## Decision

Use **synchronous in-process MVC** for all flows — controllers call the application
service directly. **No messaging broker, no saga/outbox** (transaction_pattern = none);
EF Core `SaveChanges` provides the single-database transaction per write. The picture URL
is produced with ASP.NET Core **`LinkGenerator`/`IUrlHelper`** referencing the imagery
route, not by calling an external service. Anti-forgery tokens are enforced on all state-
changing POSTs (BR-012).

## Consequences

- **Easier**: simplest possible model; no eventual-consistency or broker operational burden.
- **Easier**: existing request/response behavior is preserved exactly.
- **Harder/limits**: if catalog and imagery are later split into separate services, the URL generation becomes a cross-service contract (anti-corruption layer) — noted for future.
- No distributed-transaction concerns because all writes hit one database.
