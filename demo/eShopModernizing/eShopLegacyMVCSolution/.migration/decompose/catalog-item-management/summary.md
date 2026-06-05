# Decomposition Summary: Catalog Item Management

## Overview

- **Migration Strategy**: Refactor
- **Target Platform**: .NET 8 / ASP.NET Core MVC + EF Core
- **Modules Analyzed**: 4 (web-controllers, catalog-services, domain-model, views-and-static)
- **Source Files Read**: CatalogController.cs, CatalogService.cs, CatalogServiceMock.cs, CatalogItem.cs, CatalogBrand.cs, CatalogType.cs, CatalogDBContext.cs, CatalogItemHiLoGenerator.cs, PaginatedItemsViewModel.cs

## Extraction Counts

| Category        | Count |
| --------------- | ----- |
| Business Rules  | 17    |
| Data Structures | 4     |
| Sequence Flows  | 5     |
| Error Handlers  | 4     |
| Test Cases      | 18    |
| Unknowns        | 4     |

## Business Rules (Plain English)

### Validations
1. BR-001: Name is required.
2. BR-002: Price positive, ≤ 1,000,000, max two decimals, currency.
3. BR-003: AvailableStock between 0 and 10,000,000.
4. BR-004: RestockThreshold between 0 and 10,000,000.
5. BR-005: MaxStockThreshold between 0 and 10,000,000.
6. BR-006: Details/Edit/Delete require a non-null id (else 400).

### Calculations
1. BR-008: Paginated listing — order by Id, Skip/Take, eager-load brand+type.
2. BR-009: TotalPages = ceil(count / pageSize).
3. BR-016: HiLo allocates 10 ids per DB sequence fetch.

### State Transitions
1. BR-011: New item Id assigned from HiLo before insert (app-assigned id).
2. BR-015: Update marks entity Modified and saves.
3. BR-017: Delete removes the item then redirects.

### Routing / Authorization / Transformations
1. BR-007: Non-existent id → 404.
2. BR-010: PictureUri computed per item from the pic route (not stored).
3. BR-012: Anti-forgery token + bound allow-list (overposting protection).
4. BR-013: Persist only when ModelState valid, else redisplay form.
5. BR-014: New item defaults PictureFileName to 'dummy.png'.

## Data Structures

| Structure | Fields | Used By Rules | Source |
| --------- | ------ | ------------- | ------ |
| CatalogItem | 14 | BR-001..017 | src/eShopLegacyMVC/Models/CatalogItem.cs:6-63 |
| CatalogBrand | 2 | BR-008 | src/eShopLegacyMVC/Models/CatalogBrand.cs:8-12 |
| CatalogType | 2 | BR-008 | src/eShopLegacyMVC/Models/CatalogType.cs:8-12 |
| PaginatedItemsViewModel | 5 | BR-008, BR-009 | src/eShopLegacyMVC/ViewModel/PaginatedItemsViewModel.cs:6-26 |

## Critical Flows

| Flow | Steps | Trigger | Errors |
| ---- | ----- | ------- | ------ |
| FLOW-001 Browse catalog | 4 | GET /Catalog/Index | 0 |
| FLOW-002 View details | 3 | GET /Catalog/Details/{id} | 2 |
| FLOW-003 Create item | 4 | POST /Catalog/Create | 1 |
| FLOW-004 Edit item | 4 | POST /Catalog/Edit | 1 |
| FLOW-005 Delete item | 3 | POST /Catalog/Delete/{id} | 0 |

## Test Coverage

- **Rules with tests**: 17/17 (100%)
- **Flows with tests**: 5/5 (100%)
- **Boundary tests**: 4 (TC-004, TC-005, TC-006, TC-008)
- **Negative tests**: 6 (TC-001, TC-003, TC-007, TC-009, TC-010, TC-018)

## Unknowns & Ambiguities

| # | Description | Source | Impact |
| --- | --------- | ------ | ------ |
| 1 | Price regex allows repeated decimal groups (looser than intended) | CatalogItem.cs:22 | Target may preserve or tighten validation; edge-input behavior differs |
| 2 | No optimistic concurrency / SaveChanges error handling | CatalogService.cs:58-67 | Last-write-wins on concurrent edits; may need rowversion/ETag |
| 3 | Mock mutates shared static seed lists per call | CatalogServiceMock.cs:73-82 | Cross-request state bleed in mock/test mode |
| 4 | HiLo id state cached in a process singleton | CatalogItemHiLoGenerator.cs:12-14 | Scale-out id gaps/contention; choose EF Core HiLo vs identity |

## Diagrams

See `diagrams.md` for: sequence diagrams (FLOW-001/003 and the id-based GET/POST flows),
an entity-relationship diagram, and a create/edit validation activity diagram. No
standalone state machine — the entity has no multi-state status field.
