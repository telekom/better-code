# Feature: Reference Data (Brands & Types) + Web API

## Business Capability

Provides the catalog's reference data — brands (Azure, .NET, …) and types (Mug, T-Shirt,
…) — used to populate UI dropdowns and exposed over a small Web API (`api/Brands`,
`api/Brands/{id}`, `api/Files`). Supports the item editing experience and external
integration.

## Current Implementation

### Modules

| Module | Role | Complexity | Source |
| ------ | ---- | ---------- | ------ |
| web-controllers | primary (BrandsController, FilesController) | Moderate | discovery/modules/web-controllers.md |
| catalog-services | primary (GetCatalogBrands/Types) | Simple | discovery/modules/catalog-services.md |
| domain-model | support (CatalogBrand, CatalogType) | Simple | discovery/modules/domain-model.md |
| shared-utilities | support (Serializing/BinaryFormatter) | Simple (high risk) | discovery/modules/shared-utilities.md |

### Data Flow

`BrandsController.Get` → `ICatalogService.GetCatalogBrands` → EF6 → JSON.
`FilesController.Get` → projects brands to `BrandDTO` → `Serializing.SerializeBinary`
(BinaryFormatter) → `StreamContent` octet-stream (`Controllers/WebApi/FilesController.cs:21-36`).
`BrandsController.Delete` is a deliberate no-op returning 200 (`BrandsController.cs:48-49`).

### External Interfaces

| Type | Target | Protocol | Notes |
| ---- | ------ | -------- | ----- |
| API | HTTP clients | REST/JSON | `api/Brands` read |
| API | HTTP clients | binary stream | `api/Files` BinaryFormatter — obsolete contract |
| DB | SQL Server LocalDB | EF6 | read-only for reference data |

## Migration Strategy

### Approach: Refactor (brands/types reads) + Replace/Retire (BinaryFormatter `api/Files`)

### Target Design

Port `BrandsController` reads to ASP.NET Core Web API returning JSON. **Replace** the
`api/Files` BinaryFormatter payload with a JSON (or protobuf) endpoint — `BinaryFormatter`
is removed/blocked in modern .NET for security reasons and cannot be carried forward. If
no live external consumer exists, **Retire** `api/Files` and `eShopLegacy.Utilities`.
Make the `Delete` no-op an explicit decision (implement real delete or remove the route).

### Feature Parity

| Current Behavior | Target Behavior | Gap/Change |
| ---------------- | --------------- | ---------- |
| `api/Brands` JSON | same, ASP.NET Core | none |
| `api/Files` binary stream | JSON endpoint or removed | **breaking** wire-format change |
| `Delete` returns 200, no effect | real delete or 405/remove | behavior decision needed |

### Data Migration

None — reference data lives in the same tables; seeded by the Data Seeding feature.

## Dependencies

### Depends On (migrate these first)

- Application Platform — hosting/DI/routing.
- Catalog Item Management — shares `ICatalogService` and entity model.

### Depended Upon By

- Catalog Item Management — UI dropdowns need brands/types.

## Risks

- **High** — `BinaryFormatter` removal forces an `api/Files` contract break; unknown external consumers (unknowns.md #2). Mitigation: confirm consumers; version the new endpoint.
- **Low** — no-op `Delete` may hide an expected behavior; clarify with owner.

## Priority

- **Business Value**: High (enables item editing)
- **Usage Frequency**: Medium
- **Migration Complexity**: S (reads) / M (api/Files replacement)
- **Recommended Wave**: 2
