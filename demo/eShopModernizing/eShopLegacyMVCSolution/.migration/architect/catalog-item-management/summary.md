# Architecture Summary: Catalog Item Management

## Target Platform

Cloud-native containers — .NET 8 ASP.NET Core, Docker, Azure App Service / Kubernetes,
Azure SQL Database, Application Insights, Key Vault. Single modular-monolith service.

## Services

| Service | Responsibility | Tech Stack | Data Owned | Flows Handled |
| ------- | -------------- | ---------- | ---------- | ------------- |
| catalog-service | Catalog product CRUD + paginated browse, validation, HiLo id allocation, admin UI | ASP.NET Core 8 MVC + EF Core 8 | CatalogItem, CatalogBrand, CatalogType, PaginatedItemsViewModel | FLOW-001..005 |

## Technology Stack

- **Language**: C# (.NET 8)
- **Framework**: ASP.NET Core MVC 8 + EF Core 8
- **Database**: SQL Server / Azure SQL (managed)
- **Messaging**: none
- **API Style**: REST / server-rendered MVC
- **Deployment**: Docker container on Azure App Service / Kubernetes

## Architecture Decisions (ADRs)

| # | Decision | Status |
| --- | -------- | ------ |
| 001 | Single modular monolith (`catalog-service`) | Accepted |
| 002 | .NET 8 / ASP.NET Core MVC + EF Core + SQL Server | Accepted |
| 003 | Shared schema, bulk-ETL, EF Core Migrations, preserve id sequences | Accepted |
| 004 | Synchronous in-process MVC, no broker, no saga | Accepted |
| 005 | FluentValidation + global exception middleware + optimistic concurrency | Accepted |
| 006 | OpenTelemetry + App Insights + ILogger | Accepted |
| 007 | Anti-forgery + request DTOs + add auth + Key Vault secrets | Accepted |
| 008 | xUnit test pyramid; build characterization suite first | Accepted |

## Mapping Completeness

| Category | Mapped | Total | Coverage |
| -------- | ------ | ----- | -------- |
| Business Rules | 17 | 17 | 100% |
| Flows | 5 | 5 | 100% |
| Data Structures | 4 | 4 | 100% |
| Errors | 4 | 4 | 100% |
| Interfaces | 4 | 4 | 100% |
| Test Cases | 18 | 18 | 100% |

## Project Structure

```
eShopModernized.Catalog/            (catalog-service, net8.0, Sdk.Web)
├─ Controllers/        CatalogController
├─ Application/        ICatalogService, CatalogService, CatalogServiceMock
├─ Validation/         CatalogItemValidator (FluentValidation)
├─ Domain/             CatalogItem, CatalogBrand, CatalogType
├─ ViewModels/         PaginatedItemsViewModel<T>, CatalogItemEditRequest
├─ Infrastructure/     CatalogDbContext, Config/*, CatalogRepository, CatalogIdGenerator
├─ Middleware/         GlobalExceptionHandlerMiddleware
├─ Views/Catalog/      Index/Details/Create/Edit/Delete.cshtml
├─ Program.cs          appsettings.json
eShopModernized.Catalog.Tests/      (xUnit + FluentAssertions + EF InMemory)
docker-compose.yml / Dockerfile      (catalog-service + mssql)
```

## Notable Behavior Changes vs Legacy (surfaced from spec unknowns)

- **Optimistic concurrency** token added (`rowversion`) → safe concurrent Edit/Delete (was last-write-wins). New 409 path.
- **Authentication** added for the admin UI (was anonymous).
- **`[Bind]` allow-list → request DTOs** for overposting protection.
- HiLo re-implemented as injectable `CatalogIdGenerator`; 10-per-fetch contract pinned by TC-016.

## Diagrams

See `diagrams.md` for C4 Context, Container, Component (catalog-service internals), the
Create-item data-flow sequence, and the deployment view (Mermaid + PlantUML).
