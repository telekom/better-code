# 7. Security

## Status

Accepted

## Context

The legacy feature enforces anti-forgery tokens and `[Bind]` allow-lists on POSTs
(BR-012) but has **no authentication/authorization** — anyone reaching the site can edit
the catalog. It serves a binary `BinaryFormatter` payload elsewhere in the bounded context
(Reference Data feature) which is a known insecure-deserialization risk, and the DB
connection string sits in `Web.config`.

## Decision

- Keep **anti-forgery** protection on all state-changing actions; replace `[Bind]` allow-lists with **explicit request DTOs** (`CatalogItemEditRequest`) to prevent overposting.
- Add **authentication + authorization** for the admin UI (e.g., Microsoft Entra ID / cookie auth) as a platform concern — the catalog admin must not be anonymous in production.
- **Externalize secrets**: connection strings and keys via environment variables + **Azure Key Vault**, never in source/`appsettings`.
- Do **not** carry `BinaryFormatter` forward (tracked in the Reference Data feature) — relevant because it shares the bounded context.
- Enforce HTTPS and standard security headers at the host.

## Consequences

- **Easier**: removes anonymous write access and overposting risk; secrets out of source control.
- **Harder**: introduces an auth dependency and login flow that did not exist before (new infra + UX); must coordinate with the platform feature.
- **Tradeoff**: auth provider choice deferred to the Application Platform feature; this ADR mandates that it exists, not which one.
