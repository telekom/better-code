# Implementation Constitution — Catalog Item Management (catalog-service)

Every generated file MUST obey these principles. Derived from the ADRs (architect) and
the chosen reference template (`eShopPorted`).

## Target & Template

- **Target framework**: .NET 8 (ADR-002). _Note: the `eShopPorted` template targets
  net461/ASP.NET Core 2.2; we adopt its **layout, naming, and conventions** but modernize
  the framework to .NET 8 per the approved ADR._
- **Project type**: `Microsoft.NET.Sdk.Web`, ASP.NET Core MVC (server-rendered Razor).
- **Output root**: `./target/catalog-item-management/`.
- **Solution**: `eShopModernized.Catalog` (app) + `eShopModernized.Catalog.Tests` (xUnit).

## Conventions (from eShopPorted)

- Namespaces rooted at `eShopModernized.Catalog` (e.g., `.Models`, `.Services`, `.Controllers`, `.ViewModel`, `.Models.Config`, `.Models.Infrastructure`).
- Folders: `Models/`, `Models/Config/`, `Models/Infrastructure/`, `Services/`, `Controllers/`, `ViewModel/`, `Views/Catalog/`, `Middleware/`.
- PascalCase for classes/methods/properties; camelCase for locals/params; table names exact (`Catalog`, `CatalogBrand`, `CatalogType`).
- EF Core mapping via `IEntityTypeConfiguration<T>` + `ApplyConfigurationsFromAssembly` (matches eShopPorted `CatalogDBContext`).
- `ICatalogService` seam preserved with EF (`CatalogService`) and in-memory (`CatalogServiceMock`) implementations, chosen by `UseMockData` config.

## Layer Responsibilities

- **Controllers** (`CatalogController`): HTTP concern only — routing, model binding, anti-forgery, status codes, view selection. No business logic.
- **Services** (`CatalogService`/`CatalogServiceMock`): orchestration + business logic; the only layer that touches the DbContext.
- **Domain** (`CatalogItem`/`CatalogBrand`/`CatalogType`): entities + validation annotations + defaults.
- **Infrastructure** (`CatalogDBContext`, `Config/*`, `CatalogIdGenerator`, `PreconfiguredData`): persistence, mapping, id allocation, seed data.
- **Cross-cutting** (`GlobalExceptionHandlerMiddleware`): unhandled-exception → ProblemDetails (ERR-004).

## Behavioral Contract (must match spec.json exactly)

- Validation rules BR-001..005 preserved as **DataAnnotations** on `CatalogItem` (identical attributes to legacy, incl. the exact Price regex `^\d+(\.\d{0,2})*$`).
- BR-006 null id → `BadRequest()` (400); BR-007 missing item → `NotFound()` (404).
- BR-008 pagination: `Include(Brand,Type).OrderBy(Id).Skip(pageSize*pageIndex).Take(pageSize)`.
- BR-009 `TotalPages = ceil(count/pageSize)`.
- BR-010 `PictureUri` computed per item (route to imagery; placeholder URL until imagery feature lands).
- BR-011 + BR-016 new-item Id from **HiLo** (`CatalogIdGenerator`, 10 ids per `NEXT VALUE FOR catalog_hilo`), preserved from legacy.
- BR-012 anti-forgery + bound allow-list on POST. BR-013 persist only if `ModelState.IsValid`, else redisplay.
- BR-014 default `PictureFileName = "dummy.png"`. BR-015 update via `EntityState.Modified`. BR-017 delete by id then redirect.

## Error Handling (ADR-005)

- Explicit 400/404 in controllers; invalid model → redisplay form (ERR-003).
- Global exception middleware → ProblemDetails 500 (ERR-004).

## Testing (ADR-008)

- xUnit + FluentAssertions; EF Core InMemory for service/integration tests.
- Every BR has ≥1 test; every TC-xxx in spec maps to a test method (see mapping.json).

## Quality Rules

- Self-documenting names; methods < 30 lines; single responsibility.
- **Traceability**: each method implementing a rule references its `BR-xxx`/`FLOW-xxx`/`ERR-xxx` id in an XML-doc or comment.
- No dead code, no TODO stubs, forward-only dependencies.

## Deliberate Deviations (for template fidelity / behavioral parity — confirm or override)

| # | Constitution choice | ADR said | Why |
| - | ------------------- | -------- | --- |
| 1 | **DataAnnotations** validation on entity | ADR-005: FluentValidation | Matches eShopPorted + legacy exactly; lower risk, exact parity |
| 2 | **`[Bind]` allow-list** on controller | ADR-007: request DTOs | Matches template; same overposting protection |
| 3 | **Built-in DI** (`Program.cs`) | eShopPorted: Autofac | Idiomatic .NET 8; Autofac available as drop-in if preferred |
| 4 | **No concurrency token** this pass | ADR-005: add `rowversion` | Preserve exact legacy behavior first; add as a follow-up change |
| 5 | **Auth not implemented** here | ADR-007: add auth | Auth is the Application Platform feature's concern |

These keep the first generation a faithful, low-risk refactor; the ADR enhancements
(FluentValidation, DTOs, concurrency token, auth) become explicit follow-up tasks.
