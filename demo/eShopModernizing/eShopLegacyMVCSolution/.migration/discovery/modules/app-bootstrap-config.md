# Application Bootstrap & Configuration

## Purpose

Wires the ASP.NET application at startup: Autofac dependency injection, MVC + Web API
routing, global filters, bundling, EF database initialization, per-request logging
context, and session tracking. Also holds the `Web.config` that drives runtime behavior.

## Source Files

| File | Language | Lines | Role |
| ---- | -------- | ----- | ---- |
| `src/eShopLegacyMVC/Global.asax.cs` | C# | 115 | primary — `MvcApplication` lifecycle + DI container |
| `src/eShopLegacyMVC/Modules/ApplicationModule.cs` | C# | 40 | primary — Autofac registrations |
| `src/eShopLegacyMVC/App_Start/RouteConfig.cs` | C# | 20 | config — MVC routes |
| `src/eShopLegacyMVC/App_Start/WebApiConfig.cs` | C# | 19 | config — Web API routes |
| `src/eShopLegacyMVC/App_Start/BundleConfig.cs` | C# | 32 | config — script/style bundles |
| `src/eShopLegacyMVC/App_Start/FilterConfig.cs` | C# | 13 | config — global `HandleErrorAttribute` |
| `src/eShopLegacyMVC/Web.config` | XML | 119 | config — connection string, app settings, modules |
| `src/eShopLegacyMVC/log4Net.xml` | XML | — | config — log4net appenders/levels |
| `src/eShopLegacyMVC/ApplicationInsights.config` | XML | — | config — App Insights telemetry |

## Data Structures

- `MvcApplication : HttpApplication` — holds the Autofac `IContainer` (`src/eShopLegacyMVC/Global.asax.cs:21-25`).
- `ActivityIdHelper`, `WebRequestInfo` — log4net context value providers (`src/eShopLegacyMVC/Global.asax.cs:95-114`).
- `ApplicationModule : Autofac.Module` — ctor takes `useMockData` flag (`src/eShopLegacyMVC/Modules/ApplicationModule.cs:8-15`).

## Data Flow

### Inbound

- IIS → `Application_Start` (`src/eShopLegacyMVC/Global.asax.cs:27-36`); per request → `Application_BeginRequest` (`:47-55`); per session → `Session_Start` (`:41-45`).

### Outbound

- Builds DI graph; sets MVC + Web API dependency resolvers; conditionally sets EF initializer.

## Business Rules

| # | Rule | Source Location | Confidence |
| --- | ---- | --------------- | ---------- |
| 1 | `UseMockData` chooses `CatalogServiceMock` (SingleInstance) vs `CatalogService` (per-lifetime-scope) | `src/eShopLegacyMVC/Modules/ApplicationModule.cs:18-29` | clear |
| 2 | `CatalogDBContext`/`CatalogDBInitializer` per-lifetime-scope; `CatalogItemHiLoGenerator` SingleInstance | `src/eShopLegacyMVC/Modules/ApplicationModule.cs:31-38` | clear |
| 3 | EF initializer registered only when `UseMockData=false` | `src/eShopLegacyMVC/Global.asax.cs:83-91` | clear |
| 4 | Controllers + API controllers auto-registered from executing assembly | `src/eShopLegacyMVC/Global.asax.cs:64-66` | clear |
| 5 | MVC default route → `Catalog/Index`; attribute routes enabled | `src/eShopLegacyMVC/App_Start/RouteConfig.cs:10-17` | clear |
| 6 | Web API route `api/{controller}/{id}` + attribute routes | `src/eShopLegacyMVC/App_Start/WebApiConfig.cs:10-17` | clear |
| 7 | Per-request log4net `activityid`/`requestinfo` properties set | `src/eShopLegacyMVC/Global.asax.cs:50-54` | clear |
| 8 | Session stores `MachineName` + `SessionStartTime` | `src/eShopLegacyMVC/Global.asax.cs:41-45` | clear |

## Configuration Values (Web.config)

| Key | Value | Effect | Location |
| --- | ----- | ------ | -------- |
| `CatalogDBContext` (conn str) | LocalDB `Microsoft.eShopOnContainers.Services.CatalogDb` | EF target DB | `src/eShopLegacyMVC/Web.config:12` |
| `UseMockData` | `false` | mock vs EF service | `src/eShopLegacyMVC/Web.config:19` |
| `UseCustomizationData` | `false` | CSV/ZIP seed vs hardcoded | `src/eShopLegacyMVC/Web.config:20` |
| `targetFramework` | 4.7.2 (compile) / 4.6.1 (httpRuntime) | .NET Framework target | `src/eShopLegacyMVC/Web.config:31-32` |
| Application Insights / TelemetryCorrelation modules | registered | request telemetry | `src/eShopLegacyMVC/Web.config:34-37,86-93` |

## Dependencies

### Calls (downstream)

- Autofac, Autofac.Integration.Mvc/WebApi; log4net; EF `Database.SetInitializer`.
- Registers all types from catalog-services, domain-model, data-persistence-seeding.

### Called by (upstream)

- IIS / ASP.NET runtime.

## External Interfaces

| Type | Target | Details |
| ---- | ------ | ------- |
| DB | SQL Server LocalDB | connection string in Web.config |
| Telemetry | Azure Application Insights | `ApplicationInsights.config` + HTTP modules |
| Logging | log4net | configured via assembly/config |

## Complexity Assessment

**Rating**: Moderate

**Justification**: Small in LOC but high in architectural significance — every binding,
route, and runtime switch lives here. Heavy reliance on .NET Framework-only constructs
(`HttpApplication`, `System.Web`, IIS modules) makes this the primary porting surface.

## Unknowns

- `Web.Debug.config` / `Web.Release.config` transforms not deeply analyzed; production connection string source unknown. See unknowns.md.
