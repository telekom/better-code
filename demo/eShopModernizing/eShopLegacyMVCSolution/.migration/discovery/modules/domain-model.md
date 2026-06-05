# Domain Model & Persistence Mapping

## Purpose

The catalog domain entities, the EF6 `DbContext` that maps them to SQL Server, the
paging view model, and the HiLo primary-key generator. This is the data backbone the
services operate on.

## Source Files

| File | Language | Lines | Role |
| ---- | -------- | ----- | ---- |
| `src/eShopLegacyMVC/Models/CatalogItem.cs` | C# | 63 | primary — product entity + DataAnnotations |
| `src/eShopLegacyMVC/Models/CatalogBrand.cs` | C# | 12 | primary — brand entity |
| `src/eShopLegacyMVC/Models/CatalogType.cs` | C# | 12 | primary — type entity |
| `src/eShopLegacyMVC/Models/CatalogDBContext.cs` | C# | 88 | primary — EF6 DbContext + fluent mapping |
| `src/eShopLegacyMVC/Models/CatalogItemHiLoGenerator.cs` | C# | 34 | primary — thread-safe HiLo id generator |
| `src/eShopLegacyMVC/ViewModel/PaginatedItemsViewModel.cs` | C# | 27 | helper — generic paging envelope |

## Data Structures

- `CatalogItem` — 12 properties: `Id, Name, Description, Price, PictureFileName, PictureUri, CatalogTypeId, CatalogType, CatalogBrandId, CatalogBrand, AvailableStock, RestockThreshold, MaxStockThreshold, OnReorder`; default picture `dummy.png` (`src/eShopLegacyMVC/Models/CatalogItem.cs:6-63`).
- `CatalogBrand` — `{int Id, string Brand}` (`src/eShopLegacyMVC/Models/CatalogBrand.cs:8-12`).
- `CatalogType` — `{int Id, string Type}` (`src/eShopLegacyMVC/Models/CatalogType.cs:8-12`).
- `PaginatedItemsViewModel<TEntity>` — `{ActualPage, ItemsPerPage, TotalItems, TotalPages, Data}` (`src/eShopLegacyMVC/ViewModel/PaginatedItemsViewModel.cs:6-26`).

## Data Flow

### Inbound

- `CatalogService` LINQ queries materialize entities from SQL Server.

### Outbound

- Entities flow to controllers/views; `CatalogDBContext.SaveChanges` persists writes.

## Business Rules

| # | Rule | Source Location | Confidence |
| --- | ---- | --------------- | ---------- |
| 1 | `Price` must be positive, ≤ 1,000,000, max 2 decimals (regex + Range + Currency) | `src/eShopLegacyMVC/Models/CatalogItem.cs:22-25` | clear |
| 2 | `Name` required; stock/restock/maxstock ranges 0–10,000,000 | `src/eShopLegacyMVC/Models/CatalogItem.cs:16-17,45-57` | clear |
| 3 | Tables mapped: `CatalogType`→"CatalogType", `CatalogBrand`→"CatalogBrand", `CatalogItem`→"Catalog" | `src/eShopLegacyMVC/Models/CatalogDBContext.cs:31,45,59` | clear |
| 4 | `CatalogItem.Id` has `DatabaseGeneratedOption.None` (app-assigned via HiLo, not identity) | `src/eShopLegacyMVC/Models/CatalogDBContext.cs:63-65` | clear |
| 5 | `Name` max length 50; `Type`/`Brand` max length 100; `PictureUri` not persisted (`Ignore`) | `src/eShopLegacyMVC/Models/CatalogDBContext.cs:38-40,52-54,67-77` | clear |
| 6 | Required FK relationships Item→Brand and Item→Type | `src/eShopLegacyMVC/Models/CatalogDBContext.cs:79-85` | clear |
| 7 | HiLo: fetch `NEXT VALUE FOR catalog_hilo`, hand out 10 ids per DB round-trip, `lock`-guarded | `src/eShopLegacyMVC/Models/CatalogItemHiLoGenerator.cs:11-33` | clear |
| 8 | `TotalPages = ceil(count/pageSize)` | `src/eShopLegacyMVC/ViewModel/PaginatedItemsViewModel.cs:23` | clear |

## Dependencies

### Calls (downstream)

- `CatalogDBContext` → SQL Server LocalDB via EF6.
- `CatalogItemHiLoGenerator` → raw `SqlQuery` against `catalog_hilo` sequence.

### Called by (upstream)

- catalog-services, data-persistence-seeding, web-controllers.

## External Interfaces

| Type | Target | Details |
| ---- | ------ | ------- |
| DB | SQL Server LocalDB | connection name `CatalogDBContext`; EF6 code-first fluent mapping |
| DB (raw SQL) | `catalog_hilo` sequence | `SELECT NEXT VALUE FOR catalog_hilo` |

## Complexity Assessment

**Rating**: Simple

**Justification**: Plain POCO entities with annotations + one fluent mapping class.
The only nontrivial logic is the HiLo generator's lock + sequence batching.

## Unknowns

- HiLo generator caches `sequenceId` in a singleton across the process; correctness under multi-instance/scale-out depends on the DB sequence being the single source — relevant for cloud migration. See unknowns.md.
