# 3. Data Strategy

## Status

Accepted

## Context

The feature owns three tables (`Catalog`, `CatalogBrand`, `CatalogType`) plus the
`catalog_hilo` sequence, all in one SQL Server database (`CatalogDb`). Ids are
application-assigned via HiLo with `DatabaseGenerated(None)` (BR-011, BR-016), so id
continuity matters across the migration. Brand/Type are reference data shared with other
features but written here during seeding.

## Decision

Keep a **single shared schema** owned by `catalog-service` (single-writer for these
tables). Migrate data via **bulk-ETL**: repoint EF Core at the existing `CatalogDb` (or
bulk-load rows into a fresh Azure SQL instance) and **preserve current sequence values**
so HiLo allocation continues without id collisions. Schema evolution moves to **EF Core
Migrations** (replacing EF6 `CreateDatabaseIfNotExists` + raw `CREATE SEQUENCE` scripts).
Cross-feature reads of brands/types use the **shared schema** within the monolith (no API
hop needed while co-located).

## Consequences

- **Easier**: no schema redesign, no dual-write complexity, lowest-risk data move for a Refactor; id ranges preserved.
- **Easier**: EF Core Migrations give versioned, repeatable schema changes.
- **Harder**: HiLo behavior must be re-implemented carefully (EF Core HiLo or explicit sequence) to match the 10-per-batch semantics and avoid gaps under scale-out (see ADR 005 / spec unknown #4).
- **Tradeoff**: shared schema couples future services; if Reference Data is later extracted to its own service, a database seam/API will be required. PostgreSQL migration deferred — would add type-mapping work (`decimal`, sequences) for marginal benefit now.
