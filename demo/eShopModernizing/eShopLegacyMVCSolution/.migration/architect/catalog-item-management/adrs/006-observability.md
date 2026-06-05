# 6. Observability

## Status

Accepted

## Context

The legacy app uses log4net with per-request `activityid`/`requestinfo` context and the
classic Application Insights HTTP modules (discovery: app-bootstrap-config). ASP.NET Core
has no `System.Web` HTTP-module pipeline; observability must be re-established on the
modern stack.

## Decision

Adopt **`Microsoft.Extensions.Logging` (ILogger)** with structured logs and logging scopes
to carry correlation ids (replacing log4net `LogicalThreadContext`). Use **OpenTelemetry**
for distributed tracing and metrics, exporting to **Azure Application Insights** (modern
SDK). Instrument ASP.NET Core and EF Core. Emit a correlation/trace id on every request
and include it in error responses.

## Consequences

- **Easier**: vendor-portable telemetry (OTel), first-class tracing of HTTP + EF calls, structured queryable logs.
- **Easier**: works in containers/cloud without IIS modules.
- **Harder**: existing log4net appender configuration is not carried over; log queries/dashboards must be rebuilt.
- Minimal code cost — instrumentation is mostly configuration in `Program.cs`.
