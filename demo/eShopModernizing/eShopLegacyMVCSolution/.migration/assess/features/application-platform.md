# Feature: Application Platform (cross-cutting)

## Business Capability

The hosting and cross-cutting foundation every other feature runs on: web hosting,
dependency injection, routing (MVC + Web API), configuration, logging, and telemetry.
Not user-facing, but nothing functions without it.

## Current Implementation

### Modules

| Module | Role | Complexity | Source |
| ------ | ---- | ---------- | ------ |
| app-bootstrap-config | primary (Global.asax, ApplicationModule, App_Start, Web.config) | Moderate | discovery/modules/app-bootstrap-config.md |
| shared-utilities | support (eShopLegacy.Utilities) | Simple (high risk) | discovery/modules/shared-utilities.md |

### Data Flow

IIS → `MvcApplication.Application_Start` builds the Autofac container, configures Web API,
registers routes/filters/bundles, and wires the EF initializer
(`Global.asax.cs:27-91`). Per request: log4net `activityid`/`requestinfo` context set
(`:47-55`). `ApplicationModule` binds `ICatalogService` (mock vs EF), `CatalogDBContext`,
`CatalogDBInitializer`, `CatalogItemHiLoGenerator` (`Modules/ApplicationModule.cs:16-39`).

### External Interfaces

| Type | Target | Protocol | Notes |
| ---- | ------ | -------- | ----- |
| Config | `Web.config` | XML | connection string + `UseMockData`/`UseCustomizationData` |
| Telemetry | Azure Application Insights | HTTPS | HTTP modules |
| Logging | log4net | local/appenders | per-request context providers |
| Hosting | IIS / System.Web | — | `HttpApplication` lifecycle |

## Migration Strategy

### Approach: Rewrite (bootstrap) — unavoidable; foundation for everything else

### Target Design

Re-implement on the ASP.NET Core generic host: `Program.cs`/`Startup` with built-in DI
(or Autofac via `Autofac.Extensions.DependencyInjection`, as `eShopPorted` does), routing
via endpoint middleware, configuration via `appsettings.json` + environment variables +
secrets, logging via `Microsoft.Extensions.Logging` (Serilog/log4net provider optional),
and telemetry via the modern Application Insights SDK. `System.Web`/`Global.asax`/IIS
modules have no ASP.NET Core equivalent — this is a ground-up rewrite of the substrate,
not a port of logic. Containerize for the cloud-native target.

### Feature Parity

| Current Behavior | Target Behavior | Gap/Change |
| ---------------- | --------------- | ---------- |
| `Global.asax` lifecycle | `Program`/host + middleware | full rewrite |
| Autofac via Global.asax | Autofac via Core host integration | preserved, re-wired |
| `Web.config` settings | `appsettings.json` + env + secrets | config model change; secret externalization |
| log4net LogicalThreadContext | ILogger + scopes | provider/idiom change |
| IIS-hosted | Kestrel + container | deployment change |

### Data Migration

None (no data owned). Configuration values migrate to `appsettings`/secrets.

## Dependencies

### Depends On (migrate these first)

- None — this is the foundation (Phase 0/Wave 1).

### Depended Upon By

- All features — DI, routing, config, hosting.

## Risks

- **High** — total bootstrap rewrite; subtle DI lifetime differences (per-lifetime-scope vs scoped) can change behavior. Mitigation: mirror `eShopPorted` registrations; integration smoke tests.
- **High** — `BinaryFormatter` in `eShopLegacy.Utilities` cannot be carried to modern .NET (see Reference Data feature). Mitigation: retire/replace.
- **Medium** — secret/connection-string externalization for cloud. Mitigation: Key Vault / env config.

## Priority

- **Business Value**: Critical (enabler)
- **Usage Frequency**: N/A (foundation)
- **Migration Complexity**: L
- **Recommended Wave**: 1 (Foundation — must be first)
