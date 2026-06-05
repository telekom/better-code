# Feature: Catalog Data Seeding & Initialization

## Business Capability

Bootstraps the catalog database on first run: creates the schema, runs SQL sequence
scripts, and seeds catalog types, brands, and items — either from hardcoded data or from
operator-supplied CSV/ZIP files under `Setup/`. Also owns primary-key allocation (HiLo).

## Current Implementation

### Modules

| Module | Role | Complexity | Source |
| ------ | ---- | ---------- | ------ |
| data-persistence-seeding | primary (CatalogDBInitializer, PreconfiguredData) | Complex | discovery/modules/data-persistence-seeding.md |
| domain-model | support (CatalogDBContext, CatalogItemHiLoGenerator) | Simple | discovery/modules/domain-model.md |

### Data Flow

EF6 `Database.SetInitializer` (wired only when `UseMockData=false`,
`Global.asax.cs:83-91`) → `CatalogDBInitializer.Seed` runs 3 SQL sequence scripts, then
seeds types → brands → items → pictures. Source toggled by `UseCustomizationData`:
hardcoded `PreconfiguredData` vs `Setup/*.csv` with header validation and per-column
parsing (`Models/Infrastructure/CatalogDBInitializer.cs:32-324`). Item ids come from the
HiLo generator (`SELECT NEXT VALUE FOR catalog_hilo`, 10 ids per round-trip).

### External Interfaces

| Type | Target | Protocol | Notes |
| ---- | ------ | -------- | ----- |
| DB (DDL/DML) | SQL Server LocalDB | raw SQL + EF6 | `CREATE SEQUENCE` scripts, bulk inserts |
| File | `Setup/*.csv` | local FS | startup read when customization enabled |
| File | `Setup/CatalogItems.zip` | local FS | extracted to `~/Pics` |

## Migration Strategy

### Approach: Rewrite (re-implement on EF Core Migrations) — bounded, low-risk

### Target Design

Replace EF6 `CreateDatabaseIfNotExists` + raw `NEXT VALUE FOR` scripts with **EF Core
Migrations** (the `eShopPorted/Migrations` project already demonstrates this) plus an
idempotent seeding/`HasData` step or a hosted startup task. Move CSV/ZIP ingestion into a
dedicated, testable importer service. Rewrite is justified by Complex rating + zero tests
+ SQL-Server-specific raw scripts + framework incompatibility (EF6 initializer has no EF
Core equivalent) — Refactor cannot carry the initializer API forward.

### Feature Parity

| Current Behavior | Target Behavior | Gap/Change |
| ---------------- | --------------- | ---------- |
| `CreateDatabaseIfNotExists` + Seed | EF Core Migrations + seed task | schema-evolution model changes |
| Raw `CREATE SEQUENCE` .sql | EF Core sequence / HiLo config | engine-portable mapping |
| `UseCustomizationData` CSV/ZIP | importer service (same toggle) | extracted from initializer |
| HiLo singleton (10/batch) | EF Core HiLo or DB identity | scale-out-safe id strategy |

### Data Migration

Existing rows: bulk-load or repoint EF Core at the same DB; preserve current id ranges so
HiLo/sequence continues without collision.

## Dependencies

### Depends On (migrate these first)

- Application Platform — config toggles (`UseMockData`, `UseCustomizationData`) + host startup.

### Depended Upon By

- Catalog Item Management — shares `CatalogDBContext` + HiLo id allocation.
- Product Imagery — picture import lives here.
- Reference Data — brands/types rows seeded here.

## Risks

- **Medium** — id-continuity: HiLo process singleton + DB sequence must not collide post-migration. Mitigation: preserve sequence current value; switch to EF Core HiLo carefully.
- **Medium** — Complex, untested CSV parser with many throw paths. Mitigation: add parser unit tests before rewrite (characterization).
- **Low** — SQL-Server-specific scripts not portable. Mitigation: EF Core provider abstraction.

## Priority

- **Business Value**: High (nothing works without seeded data + ids)
- **Usage Frequency**: Low (startup/first-run) but critical-path
- **Migration Complexity**: L
- **Recommended Wave**: 1 (enabler — must precede item/reference/imagery)
