# Migration Sequence — eShopLegacyMVC

## Overall Strategy: Hybrid (Refactor/Replatform a single-context monolith, layered bottom-up)

eShopLegacyMVC is one small bounded context (Catalog) with ~1,500 LOC of sound, thin
business logic and an in-repo target blueprint (`eShopPorted`, ASP.NET Core + EF Core).
Domain decomposition is therefore trivial; the real ordering constraint is **technical
layering** — the host/DI/config foundation and data/id-allocation must exist before the
features that sit on them. Execution can optionally run strangler-style (new ASP.NET Core
app behind a reverse proxy, route-by-route cutover) since the surface is small enough to
also support a single clean cutover.

> Automated `build_feature_dependencies.py` reported 0 cross-feature edges because
> features deliberately share modules (e.g. `web-controllers`, `domain-model`); the
> dependencies below are evidence-based from the per-feature "Depends On" analysis.

## Phase 0: Foundation

Target platform and safety net before any feature moves.

- [ ] Stand up .NET 8 ASP.NET Core project skeleton (mirror `eShopPorted` structure)
- [ ] Container build (Dockerfile) + CI/CD pipeline
- [ ] Externalize config: `appsettings.json` + env vars + secret store (Key Vault) for the connection string
- [ ] **Establish the missing test safety net** — characterization tests using `CatalogServiceMock` / `UseMockData=true` (discovery found 0 tests)
- [ ] Provision target SQL Server (managed) and object storage (Blob/S3) for pictures
- [ ] Optional: reverse proxy/facade in front of legacy for strangler-style cutover

## Phase 1: Foundation Features — Enablers

| Feature | Strategy | Complexity | Why Now |
| ------- | -------- | ---------- | ------- |
| Application Platform | Rewrite | L | Host/DI/routing/config — everything depends on it; no ASP.NET Core equivalent for `System.Web`/`Global.asax` |
| Catalog Data Seeding & Initialization | Rewrite | L | Owns schema + HiLo id allocation; EF6 initializer has no EF Core equivalent; must precede all data features |

**Unblocks**: every user-facing feature (they need the host + a seeded DB + working id allocation).
**Parallel**: Platform and Seeding can be built largely in parallel, integrated at the host-startup seam.
**Duration signal**: medium–long (substrate rewrite + id-continuity care).
**Rollback**: legacy app remains the system of record; new app not yet serving traffic.

## Phase 2: Core Business Features

| Feature | Strategy | Complexity | Why Now |
| ------- | -------- | ---------- | ------- |
| Catalog Item Management | Refactor | M | Core capability; logic is thin and portable; depends only on Platform + Seeding |
| Reference Data (Brands & Types) + Web API | Refactor (reads) / Replace (api/Files) | S–M | Enables item editing dropdowns; carries the `BinaryFormatter` retirement |

**Unblocks**: full catalog CRUD on the modern stack; deprecation of legacy endpoints.
**Parallel**: the two features touch shared services — sequence Item Management slightly ahead, then Reference Data; or one team, back-to-back.
**Duration signal**: medium.
**Rollback**: per-route cutover (strangler) — revert the route to legacy; data unchanged.
**Decision required**: `api/Files` BinaryFormatter contract — confirm external consumers, then replace with JSON or retire (unknowns.md #2).

## Phase 3: Imagery & Statelessness

| Feature | Strategy | Complexity | Why Now |
| ------- | -------- | ---------- | ------- |
| Product Imagery | Refactor + Replatform | M | Move pictures off local `~/Pics` to object storage so the app is stateless/scalable; depends on Item Management + Seeding import path |

**Unblocks**: horizontal scaling / containerized multi-instance deployment.
**Parallel**: image bulk-upload (data move) can run concurrently with code port.
**Duration signal**: short–medium.
**Rollback**: keep serving images from legacy `~/Pics` route until blob path verified.

## Phase N: Decommission

- Confirm no traffic to legacy routes for an agreed window (e.g. 14 days) via App Insights.
- Archive legacy `~/Pics` and `Setup/` artifacts; retain DB backup per policy.
- DNS/reverse-proxy cutover to the ASP.NET Core app as system of record.
- Point of no return: after legacy DB writes stop and the new app is sole writer.
- Decommission `eShopLegacyMVC` IIS site and `eShopLegacy.Utilities` (BinaryFormatter) assembly.

## Open Decisions

| # | Decision | Owner | Blocks |
| --- | -------- | ----- | ------ |
| 1 | `api/Files` BinaryFormatter: replace (JSON) or retire? | API owner | Reference Data feature |
| 2 | `BrandsController.Delete` no-op: implement real delete or remove route? | Product | Reference Data feature |
| 3 | Id strategy: EF Core HiLo vs DB IDENTITY (preserve current sequence values) | Data/DBA | Seeding feature |
| 4 | Single cutover vs strangler-style route-by-route | Architecture | Phase 0 facade scope |
| 5 | Confirm `eShopPorted` is the sanctioned blueprint vs a spike | Architecture | target design |
