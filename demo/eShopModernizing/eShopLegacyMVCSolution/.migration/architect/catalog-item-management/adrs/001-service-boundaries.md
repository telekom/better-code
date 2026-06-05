# 1. Service Boundaries — Single Modular Monolith

## Status

Accepted

## Context

Catalog Item Management is one cohesive capability inside a single bounded context
(Catalog). The spec has 17 rules, 5 flows, and 3 persistent entities (CatalogItem,
CatalogBrand, CatalogType) that share one database and are always queried together
(items eager-load brand+type, BR-008). The whole legacy app is ~1,500 LOC. Splitting
this into multiple network services would create a distributed monolith and violate the
"match team topology / avoid over-decomposition" anti-patterns.

## Decision

Implement the feature as a **single ASP.NET Core service, `catalog-service`, structured
as a modular monolith** with clear internal layers: Controllers → Application (services)
→ Domain (entities) → Infrastructure (EF Core repository, id generator). The
`ICatalogService` seam from the legacy app is preserved as the application boundary. No
cross-service calls are introduced for this feature.

## Consequences

- **Easier**: single deployable, in-process calls (no network/serialization overhead), one transaction scope, simplest possible migration path, fastest delivery.
- **Easier**: the existing `eShopPorted` project is a near-identical blueprint, de-risking the design.
- **Harder/limits**: if the broader system later demands independent scaling of catalog sub-capabilities, this monolith would need decomposition — acceptable given current size and the single shared schema.
- Other features (Reference Data, Product Imagery, Seeding) will live in the same service/solution as additional modules rather than separate services.
