# eShopPorted — Parallel ASP.NET Core Port (reference variant)

## Purpose

`eShopPorted` is a second project in the same solution that mirrors `eShopLegacyMVC`
but is ported to **ASP.NET Core 2.2** (SDK-style `Microsoft.NET.Sdk.Web`, still on
`net461`) using **EF Core** with `IEntityTypeConfiguration<>` mappings and EF Core
migrations. It is the "after" reference showing where the legacy MVC app is headed.
Out of primary discovery scope (scope = eShopLegacyMVC) but documented for coverage and
because it is the de-facto target architecture.

## Source Files

| File | Language | Role |
| ---- | -------- | ---- |
| `eShopPorted/eShopPorted.csproj` | XML | SDK-style ASP.NET Core 2.2 project (net461) |
| `eShopPorted/Controllers/CatalogController.cs` | C# | MVC catalog controller (Core) |
| `eShopPorted/Controllers/PicController.cs` | C# | picture controller (Core) |
| `eShopPorted/Controllers/Api/BrandsController.cs` | C# | Web API brands |
| `eShopPorted/Controllers/Api/FilesController.cs` | C# | Web API files |
| `eShopPorted/Services/ICatalogService.cs` | C# | service contract |
| `eShopPorted/Services/CatalogService.cs` | C# | EF Core service |
| `eShopPorted/Services/CatalogServiceMock.cs` | C# | in-memory service |
| `eShopPorted/Models/CatalogDBContext.cs` | C# | EF Core `DbContext` (options-injected) |
| `eShopPorted/Models/CatalogItem.cs`, `CatalogBrand.cs`, `CatalogType.cs` | C# | entities |
| `eShopPorted/Models/Config/CatalogBrandConfig.cs` | C# | `IEntityTypeConfiguration<>` mapping |
| `eShopPorted/Models/Config/CatalogItemConfig.cs` | C# | `IEntityTypeConfiguration<>` mapping |
| `eShopPorted/Models/Config/CatalogTypeConfig.cs` | C# | `IEntityTypeConfiguration<>` mapping |
| `eShopPorted/Models/Infrastructure/PreconfiguredData.cs` | C# | seed data |
| `eShopPorted/Migrations/20201130044339_Initial.cs` (+ Designer, ModelSnapshot) | C# | EF Core migration |

## Key Differences vs eShopLegacyMVC

| Aspect | eShopLegacyMVC (legacy) | eShopPorted (target) |
| ------ | ----------------------- | -------------------- |
| Framework | ASP.NET MVC 5 / System.Web | ASP.NET Core 2.2 |
| ORM | EF6 (`System.Data.Entity`) | EF Core (`Microsoft.EntityFrameworkCore`) |
| DbContext | parameterless, `name=` conn | `DbContextOptions`-injected |
| EF mapping | fluent in `OnModelCreating` | `IEntityTypeConfiguration<>` per entity |
| Schema evolution | `CreateDatabaseIfNotExists` + raw SQL seq | EF Core Migrations |
| Bootstrap | `Global.asax` + `HttpApplication` | `Startup`/`Program` (Core hosting) |

## Dependencies

- EF Core, ASP.NET Core, Autofac.Extensions.DependencyInjection (`eShopPorted/eShopPorted.csproj:5-8`).

## External Interfaces

| Type | Target | Details |
| ---- | ------ | ------- |
| DB | SQL Server via EF Core | options-configured connection |

## Complexity Assessment

**Rating**: Moderate

**Justification**: Functionally equivalent to the legacy app; complexity lies in the
framework/ORM differences rather than business logic. Useful as the migration blueprint.

## Unknowns

- Whether `eShopPorted` is the sanctioned migration target or an experimental spike is not stated in-repo. See unknowns.md.
