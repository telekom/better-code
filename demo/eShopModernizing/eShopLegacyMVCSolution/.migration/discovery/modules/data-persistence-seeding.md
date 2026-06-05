# Database Initialization & Seeding

## Purpose

Builds and seeds the catalog database on first run. `CatalogDBInitializer` creates the
DB if absent, runs three SQL sequence scripts, and seeds types, brands, and items —
either from hardcoded `PreconfiguredData` or, when `UseCustomizationData=true`, from
CSV/ZIP files under `Setup/`.

## Source Files

| File | Language | Lines | Role |
| ---- | -------- | ----- | ---- |
| `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs` | C# | 355 | primary — DB create + seed orchestration |
| `src/eShopLegacyMVC/Models/Infrastructure/PreconfiguredData.cs` | C# | 51 | primary — hardcoded seed data |
| `src/eShopLegacyMVC/Models/Infrastructure/dbo.catalog_hilo.Sequence.sql` | SQL | 11 | config — item id sequence |
| `src/eShopLegacyMVC/Models/Infrastructure/dbo.catalog_brand_hilo.Sequence.sql` | SQL | ~11 | config — brand id sequence |
| `src/eShopLegacyMVC/Models/Infrastructure/dbo.catalog_type_hilo.Sequence.sql` | SQL | ~11 | config — type id sequence |
| `src/eShopLegacyMVC/Setup/CatalogTypes.csv` | CSV | data | optional seed source |
| `src/eShopLegacyMVC/Setup/CatalogBrands.csv` | CSV | data | optional seed source |
| `src/eShopLegacyMVC/Setup/CatalogItems.csv` | CSV | data | optional seed source |
| `src/eShopLegacyMVC/Setup/CatalogItems.zip` | ZIP | data | optional item pictures |

## Data Structures

- Seed lists of `CatalogItem` (12 items), `CatalogBrand` (5: Azure, .NET, Visual Studio, SQL Server, Other), `CatalogType` (4: Mug, T-Shirt, Sheet, USB Memory Stick) (`src/eShopLegacyMVC/Models/Infrastructure/PreconfiguredData.cs:10-50`).

## Data Flow

### Inbound

- EF6 `Database.SetInitializer` triggers `Seed` on first DB access (wired only when `UseMockData=false`) (`src/eShopLegacyMVC/Global.asax.cs:83-91`).
- Optional: `Setup/*.csv` read via `File.ReadAllLines`; `Setup/CatalogItems.zip` extracted to `~/Pics`.

### Outbound

- Inserts into `CatalogType`, `CatalogBrand`, `Catalog` tables; creates SQL sequences; writes picture files to `~/Pics`.

## Business Rules

| # | Rule | Source Location | Confidence |
| --- | ---- | --------------- | ---------- |
| 1 | Seed order: sequences → types → brands → items → pictures | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:32-43` | clear |
| 2 | Type/Brand ids assigned from `NEXT VALUE FOR catalog_type_hilo`/`catalog_brand_hilo`, incremented per row | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:45-77,326-331` | clear |
| 3 | Item ids assigned via `CatalogItemHiLoGenerator` (10-id batches) | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:79-93` | clear |
| 4 | `UseCustomizationData` toggles CSV vs hardcoded seed; missing CSV falls back to hardcoded | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:29,47-49,100-103` | clear |
| 5 | CSV header validation: required vs optional header counts enforced, else throw | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:298-324` | clear |
| 6 | CSV item parse: type/brand names must resolve to existing ids; price parsed invariant-culture | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:192-225` | clear |
| 7 | Picture import only when `UseCustomizationData`; deletes all existing `~/Pics` files first, then unzips | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:339-354` | clear |
| 8 | Sequence scripts located relative to `AppDomain.BaseDirectory` and executed verbatim | `src/eShopLegacyMVC/Models/Infrastructure/CatalogDBInitializer.cs:333-337` | clear |

## Dependencies

### Calls (downstream)

- `CatalogDBContext`, `CatalogItemHiLoGenerator` (domain-model).
- `PreconfiguredData` (this module).
- `System.IO.Compression.ZipFile`, `System.IO.File`, `HostingEnvironment` (filesystem).

### Called by (upstream)

- `MvcApplication.ConfigDataBase` via EF initializer (app-bootstrap-config).

## External Interfaces

| Type | Target | Details |
| ---- | ------ | ------- |
| DB (DDL/DML) | SQL Server LocalDB | CREATE SEQUENCE scripts + bulk inserts |
| File | `Setup/*.csv` | read on startup when customization enabled |
| File | `Setup/CatalogItems.zip` → `~/Pics` | extracted, destination wiped first |

## Complexity Assessment

**Rating**: Complex

**Justification**: 355 LOC, the single largest file. Dense CSV parsing with per-column
index lookups, header validation, multiple throw paths, filesystem and DB side effects,
and `AppDomain.BaseDirectory`-relative script paths — all migration-sensitive.

## Unknowns

- The destructive `~/Pics` wipe runs only under `UseCustomizationData`; behavior with concurrent first-run requests is unspecified. See unknowns.md.
- Sequence `.sql` scripts are SQL Server-specific (`NEXT VALUE FOR`) — not portable to other engines without rewrite.
