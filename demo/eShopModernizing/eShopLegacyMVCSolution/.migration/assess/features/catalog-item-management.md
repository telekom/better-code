# Feature: Catalog Item Management

## Business Capability

Lets an operator browse the product catalog with pagination and create, view, edit, and
delete catalog items (name, description, price, stock thresholds, brand, type, picture).
This is the application's core reason to exist.

## Current Implementation

### Modules

| Module | Role | Complexity | Source |
| ------ | ---- | ---------- | ------ |
| web-controllers | primary (CatalogController) | Moderate | discovery/modules/web-controllers.md |
| catalog-services | primary (CatalogService/Mock) | Simple | discovery/modules/catalog-services.md |
| domain-model | primary (CatalogItem, paging) | Simple | discovery/modules/domain-model.md |
| views-and-static | support (Razor CRUD views) | Simple | discovery/modules/views-and-static.md |

### Data Flow

Browser → `CatalogController` action → `ICatalogService` → `CatalogDBContext` (EF6, LINQ
`Skip/Take`, eager-load Brand+Type) → SQL Server → `PaginatedItemsViewModel` → Razor view.
Writes assign Id via HiLo then `SaveChanges` (`Services/CatalogService.cs:51-68`).

### External Interfaces

| Type | Target | Protocol | Notes |
| ---- | ------ | -------- | ----- |
| DB | SQL Server LocalDB | EF6 | per-request; `SaveChanges` per write; no retry |
| Screen | Browser | HTTP/Razor | anti-forgery + `[Bind]` allow-list on POST |

## Migration Strategy

### Approach: Refactor (re-platform to ASP.NET Core)

### Target Design

Port to ASP.NET Core MVC (.NET 8) controllers + EF Core, keeping the `ICatalogService`
seam and the entity model. The in-repo `eShopPorted` project is the working blueprint
(EF Core `DbContextOptions`, `IEntityTypeConfiguration<>`). Business logic is sound and
thin — preserve it; only the framework/ORM substrate changes.

### Feature Parity

| Current Behavior | Target Behavior | Gap/Change |
| ---------------- | --------------- | ---------- |
| EF6 LINQ paging, eager load | EF Core equivalent | `IEnumerable` enumeration semantics differ; verify lazy/eager |
| `[Bind(Include=...)]` overposting guard | Core model binding / DTOs | replace with input DTOs / `[BindNever]` |
| Server-rendered Razor | Razor (Core) or keep MVC views | minimal change |
| HiLo app-assigned Id | EF Core HiLo / sequence | re-implement id strategy (see data-seeding) |

### Data Migration

Catalog table schema is unchanged; bulk-load existing rows or point EF Core at the same
DB. No transformation needed for the entity shape.

## Dependencies

### Depends On (migrate these first)

- Application Platform — DI, routing, config host must exist first.
- Catalog Data Seeding & Initialization — shares `CatalogDBContext` + HiLo id allocation.

### Depended Upon By

- Reference Data + Web API — UI dropdowns and item editing consume brands/types.
- Product Imagery — item `PictureUri` is computed from the picture route.

## Risks

- **Medium** — EF6→EF Core query-behavior differences (deferred execution, `Include`, raw SQL). Mitigation: characterization tests via `CatalogServiceMock` before/after.
- **Low** — overposting protection idiom changes; mitigate with explicit request DTOs.

## Priority

- **Business Value**: Critical
- **Usage Frequency**: High (estimate — no runtime data)
- **Migration Complexity**: M
- **Recommended Wave**: 2
