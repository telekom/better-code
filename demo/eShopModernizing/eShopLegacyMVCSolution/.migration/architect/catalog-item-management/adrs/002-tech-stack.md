# 2. Technology Stack

## Status

Accepted

## Context

The legacy feature is ASP.NET MVC 5 + EF6 on .NET Framework 4.7.2, IIS-hosted. The
assessed strategy is Refactor to a cloud-native .NET target. The in-repo `eShopPorted`
project already demonstrates an ASP.NET Core + EF Core port of this exact domain. Team
skills are .NET/C#; the business logic is thin and worth preserving.

## Decision

Adopt: **.NET 8**, **ASP.NET Core MVC 8** (keep server-rendered Razor for the admin UI),
**EF Core 8** for persistence, **SQL Server / Azure SQL** as the database, **FluentValidation**
for input rules, **xUnit + FluentAssertions + EF Core InMemory/Testcontainers** for tests,
**dotnet CLI / SDK-style projects** for build, **Docker** for packaging, and
**OpenTelemetry + Azure Application Insights + ILogger** for observability. API style is
**REST/server-rendered MVC** (no separate JSON API in this feature's scope).

## Consequences

- **Easier**: minimal logic rewrite (Refactor), direct mapping from EF6 to EF Core, Razor views port with small changes, blueprint already exists in `eShopPorted`.
- **Easier**: modern, supported runtime; container/cloud deployment; structured logging and tracing.
- **Harder**: EF6→EF Core query-behavior differences (deferred execution, `Include`, raw SQL) require characterization tests; log4net idioms replaced by `ILogger`.
- **Tradeoff**: keeping SQL Server (vs PostgreSQL) minimizes data-migration risk now; PostgreSQL remains an option later (see ADR 003 consequences).
