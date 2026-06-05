# Web Controllers (MVC + Web API)

## Purpose

The HTTP entry layer of eShopLegacyMVC. Renders the catalog admin UI (server-side
Razor) and exposes a small set of HTTP/Web API endpoints. All controllers are thin:
they receive `ICatalogService` via constructor injection (Autofac) and delegate every
domain operation to it, then return a `View`, a file, or a serialized payload.

## Source Files

| File | Language | Lines | Role |
| ---- | -------- | ----- | ---- |
| `src/eShopLegacyMVC/Controllers/CatalogController.cs` | C# | 165 | primary — MVC CRUD UI for catalog items |
| `src/eShopLegacyMVC/Controllers/PicController.cs` | C# | 91 | primary — serves item picture bytes |
| `src/eShopLegacyMVC/Controllers/WebApi/BrandsController.cs` | C# | 51 | primary — Web API for brands |
| `src/eShopLegacyMVC/Controllers/WebApi/FilesController.cs` | C# | 44 | primary — Web API returning BinaryFormatter stream |
| `src/eShopLegacyMVC/Controllers/Api/CatalogController.cs` | C# | 14 | helper — stub "Hello World" endpoint (`CatalogController2`) |

## Data Structures

- `CatalogItem`, `CatalogBrand`, `CatalogType` — domain entities consumed/returned (defined in domain-model).
- `PaginatedItemsViewModel<CatalogItem>` — paging envelope returned to `Index` view (`src/eShopLegacyMVC/ViewModel/PaginatedItemsViewModel.cs`).
- `FilesController.BrandDTO` — `[Serializable]` projection `{int Id, string Brand}` (`src/eShopLegacyMVC/Controllers/WebApi/FilesController.cs:38-43`).

## Data Flow

### Inbound

- Browser → MVC routes (`Catalog/{action}/{id}`, default `Catalog/Index`) → `CatalogController` (`src/eShopLegacyMVC/Controllers/CatalogController.cs:22`).
- Browser `<img>` → attribute route `items/{catalogItemId:int}/pic` → `PicController.Index` (`src/eShopLegacyMVC/Controllers/PicController.cs:24-25`).
- HTTP client → `api/Brands`, `api/Brands/{id}`, `api/Files` → Web API controllers.

### Outbound

- All controllers → `ICatalogService` (in-process call).
- `PicController` → filesystem read of `~/Pics/{PictureFileName}` (`src/eShopLegacyMVC/Controllers/PicController.cs:38-44`).

## Business Rules

| # | Rule | Source Location | Confidence |
| --- | ---- | --------------- | ---------- |
| 1 | Default page size is 10, page index 0 | `src/eShopLegacyMVC/Controllers/CatalogController.cs:22` | clear |
| 2 | `Details/Edit/Delete` with null id → HTTP 400; not-found item → HTTP 404 | `src/eShopLegacyMVC/Controllers/CatalogController.cs:34-42,80-88,117-125` | clear |
| 3 | Create/Edit/Delete POST require anti-forgery token; explicit `[Bind(Include=...)]` allow-list against overposting | `src/eShopLegacyMVC/Controllers/CatalogController.cs:60-62,98-100,132-134` | clear |
| 4 | `PictureUri` is computed per item from the `GetPicRouteTemplate` route (not stored) | `src/eShopLegacyMVC/Controllers/CatalogController.cs:160-163` | clear |
| 5 | `catalogItemId <= 0` rejected with HTTP 400 before lookup | `src/eShopLegacyMVC/Controllers/PicController.cs:29-32` | clear |
| 6 | Picture MIME type derived from file extension; unknown → `application/octet-stream` | `src/eShopLegacyMVC/Controllers/PicController.cs:52-88` | clear |
| 7 | `BrandsController.Delete` is a no-op ("demo only — don't actually delete"), always returns 200 | `src/eShopLegacyMVC/Controllers/WebApi/BrandsController.cs:48-49` | clear |

## Dependencies

### Calls (downstream)

- `ICatalogService` — every catalog read/write (catalog-services module).
- `eShopLegacy.Utilities.Serializing` — `FilesController` binary serialization (`src/eShopLegacyMVC/Controllers/WebApi/FilesController.cs:29`).
- `System.IO.File` / `Server.MapPath` — `PicController` filesystem access.

### Called by (upstream)

- ASP.NET MVC/Web API routing pipeline (app-bootstrap-config module).

## External Interfaces

| Type | Target | Details |
| ---- | ------ | ------- |
| HTTP (HTML) | Browser | Razor views, server-rendered |
| HTTP (file) | Browser | image bytes, MIME from extension |
| Web API | HTTP clients | `api/Brands` JSON; `api/Files` BinaryFormatter octet-stream |
| File I/O | `~/Pics/*` | synchronous `ReadAllBytes`, no explicit error handling on missing file |

## Complexity Assessment

**Rating**: Moderate

**Justification**: ~365 LOC across 5 files. Logic is mostly straightforward delegation
and validation; the only branching density is `PicController`'s MIME switch. The
`FilesController` BinaryFormatter usage is a migration hotspot (see unknowns).

## Unknowns

- `CatalogController2` (`Api/CatalogController.cs`) returns a static "Hello World!" — appears to be a scaffolding stub / dead endpoint.
- `PicController.Index` does not guard against a missing file on disk after the item is found (`File.ReadAllBytes` would throw) — see unknowns.md.
