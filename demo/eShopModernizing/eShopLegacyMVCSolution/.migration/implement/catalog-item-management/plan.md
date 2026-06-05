# Implementation Plan — Catalog Item Management

## Service order

Single service (`catalog-service`) — no parallelism needed.

## Layer order (dependency-first)

1. **Infrastructure**: `.csproj`, `Program.cs`, `appsettings.json`, Dockerfile, docker-compose.
2. **Data/Domain entities**: `CatalogItem`, `CatalogBrand`, `CatalogType`, `PaginatedItemsViewModel`.
3. **Infrastructure (persistence)**: `PreconfiguredData`, `Config/*`, `CatalogDBContext`, `CatalogIdGenerator`.
4. **Domain/Application**: `ICatalogService`, `CatalogService`, `CatalogServiceMock`.
5. **API**: `CatalogController`, Razor views.
6. **Cross-cutting**: `GlobalExceptionHandlerMiddleware`.
7. **Tests**: validation, service (InMemory), controller, view-model, id-generator.

## Verification checkpoints

- Boilerplate (entities, configs, csproj, views) batch-generated then reviewed together.
- Business-logic files (`CatalogService`, `CatalogController`, `CatalogIdGenerator`) generated one at a time with traceability comments.
- After all files: run `check_coverage.py` (target 100% across rules/flows/tests/data/errors).
- Attempt `dotnet build` — **note: dotnet SDK is not installed in this environment**, so build verification will be reported as unavailable; code is generated to compile under .NET 8.

## Risk mitigation

- HiLo (`CatalogIdGenerator`) is the riskiest piece (raw sequence semantics) → generate early and pin behavior with `CatalogIdGeneratorTests` (TC-016).
- EF6→EF Core query differences covered by `CatalogServiceTests` against the InMemory provider.

## Estimated task count

~26 files: 1 csproj + Program + 2 config (app) + 4 entities/VM + 4 persistence + 3 services + 1 controller + ~7 views + 1 middleware + 1 test csproj + 5 test classes + Dockerfile/compose.
