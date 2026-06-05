# Test Asset Inventory & Migration Validation Readiness

## Test Coverage Summary

| Metric | Value |
| ------ | ----- |
| Total source files | 119 (solution, per `test_inventory.py`) |
| Test files | 0 |
| Production files with tests | 0 |
| Estimated coverage | 0.0% |

## Test Frameworks Detected

| Framework | Files Using | Language | Notes |
| --------- | ----------- | -------- | ----- |
| (none) | 0 | — | No xUnit/NUnit/MSTest project in the solution |

## Fixture/Golden File Assets

| Directory | Type | File Count | Description |
| --------- | ---- | ---------- | ----------- |
| `src/eShopLegacyMVC/Setup/` | fixtures (seed) | 4 | `CatalogTypes.csv`, `CatalogBrands.csv`, `CatalogItems.csv`, `CatalogItems.zip` — usable as seed/golden data |
| `src/eShopLegacyMVC/Pics/` | fixtures (images) | many | item pictures referenced by `PictureFileName` |
| `Models/Infrastructure/PreconfiguredData.cs` | golden (code) | 1 | deterministic 12 items / 5 brands / 4 types — ideal oracle |

## Coverage Gaps (Untested Modules)

| Module/Directory | Files | Risk Assessment |
| ---------------- | ----- | --------------- |
| `src/eShopLegacyMVC` (all) | ~22 | high — no regression safety net for any path |
| `eShopPorted` (all) | ~20 | high — port has no tests either |
| `data-persistence-seeding` (CSV parsing) | 9 | high — most complex logic, many throw paths, untested |

## Integration Test Infrastructure

| Component | Exists? | Location | Notes |
| --------- | ------- | -------- | ----- |
| Test database | n (implicit) | LocalDB | `UseMockData=true` gives a DB-free in-memory mode usable for tests |
| Mock services | y | `Services/CatalogServiceMock.cs` | full `ICatalogService` in-memory impl — ready-made test double |
| CI pipeline | n (in this solution) | — | repo root has GitLab CI for the demo, not unit tests |
| Performance tests | n | — | no baselines |

## Migration Validation Strategy

### Pre-Migration Baseline

- [ ] Capture current test pass/fail status — none exist; establish characterization tests first.
- [ ] Record performance baselines for `Catalog/Index` pagination and `items/{id}/pic`.
- [ ] Snapshot the seeded dataset from `PreconfiguredData` as the golden oracle.
- [ ] Document expected behavior for price/stock validation and HiLo id allocation.

### Post-Migration Validation

- [ ] Run new characterization suite against migrated (eShopPorted-style) code.
- [ ] Compare catalog CRUD responses field-for-field against legacy output.
- [ ] Verify HiLo/identity id continuity for existing rows.
- [ ] Confirm `api/Files` replacement contract (JSON) against documented consumers.
- [ ] Performance comparison against captured baselines.

### Gaps Requiring New Tests

| Area | What's Missing | Priority | Effort |
| ---- | -------------- | -------- | ------ |
| catalog-services | unit tests for CRUD + pagination (use `CatalogServiceMock`) | high | 1–2 days |
| data-persistence-seeding | CSV parse/validation + error-path tests | high | 2–3 days |
| web-controllers | controller action tests (model validation, 400/404) | medium | 1–2 days |
| domain-model | HiLo concurrency + Price regex tests | medium | 1 day |
| api contracts | characterization of `api/Brands`, `api/Files` | medium | 1 day |
