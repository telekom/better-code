# Catalog Services

## Purpose

The business-logic layer behind the controllers. Defines `ICatalogService` and two
interchangeable implementations: `CatalogService` (Entity Framework 6, real SQL Server
LocalDB) and `CatalogServiceMock` (in-memory, seeded from `PreconfiguredData`). Which
one is bound is decided at startup by the `UseMockData` app setting via Autofac.

## Source Files

| File | Language | Lines | Role |
| ---- | -------- | ----- | ---- |
| `src/eShopLegacyMVC/Services/ICatalogService.cs` | C# | 17 | primary — service contract |
| `src/eShopLegacyMVC/Services/CatalogService.cs` | C# | 74 | primary — EF6-backed implementation |
| `src/eShopLegacyMVC/Services/CatalogServiceMock.cs` | C# | 83 | primary — in-memory implementation |

## Data Structures

- `ICatalogService : IDisposable` — 7 members: `FindCatalogItem`, `GetCatalogBrands`, `GetCatalogItemsPaginated`, `GetCatalogTypes`, `CreateCatalogItem`, `UpdateCatalogItem`, `RemoveCatalogItem` (`src/eShopLegacyMVC/Services/ICatalogService.cs:8-17`).
- Consumes `CatalogItem`, `CatalogBrand`, `CatalogType`, `PaginatedItemsViewModel<CatalogItem>`.

## Data Flow

### Inbound

- Controllers → service methods (in-process).

### Outbound

- `CatalogService` → `CatalogDBContext` (EF6 → SQL Server LocalDB).
- `CatalogServiceMock` → `PreconfiguredData` static lists (no DB).

## Business Rules

| # | Rule | Source Location | Confidence |
| --- | ---- | --------------- | ---------- |
| 1 | Pagination: `Skip(pageSize*pageIndex).Take(pageSize)`, ordered by `Id`; eager-loads Brand+Type | `src/eShopLegacyMVC/Services/CatalogService.cs:21-35` | clear |
| 2 | `FindCatalogItem` eager-loads `CatalogBrand` and `CatalogType` | `src/eShopLegacyMVC/Services/CatalogService.cs:37-40` | clear |
| 3 | New item Id assigned from HiLo generator before insert | `src/eShopLegacyMVC/Services/CatalogService.cs:51-56` | clear |
| 4 | Update sets EF entity state to `Modified` then `SaveChanges` | `src/eShopLegacyMVC/Services/CatalogService.cs:58-62` | clear |
| 5 | Mock new-item Id = `max(existing Id)+1` | `src/eShopLegacyMVC/Services/CatalogServiceMock.cs:48-53` | clear |
| 6 | Mock joins brand/type into items in-memory by FK before returning a page | `src/eShopLegacyMVC/Services/CatalogServiceMock.cs:73-82` | clear |

## Dependencies

### Calls (downstream)

- `CatalogDBContext`, `CatalogItemHiLoGenerator` (domain-model / data-persistence).
- `PreconfiguredData.GetPreconfigured*` (data-persistence-seeding) — mock only.

### Called by (upstream)

- `CatalogController`, `PicController`, `BrandsController`, `FilesController` (web-controllers).

## External Interfaces

| Type | Target | Details |
| ---- | ------ | ------- |
| DB | SQL Server LocalDB (`CatalogDBContext`) | EF6 LINQ; `SaveChanges` per write; no explicit transaction/retry |

## Complexity Assessment

**Rating**: Simple

**Justification**: ~174 LOC, single responsibility, no concurrency beyond EF defaults.
The mock and real implementations are symmetric, which de-risks migration.

## Unknowns

- `CatalogServiceMock.GetCatalogItemsPaginated` mutates shared static `PreconfiguredData` lists via `ComposeCatalogItems` (`ForEach` assigns navigation props) — possible cross-request state bleed in the mock path. See unknowns.md.
