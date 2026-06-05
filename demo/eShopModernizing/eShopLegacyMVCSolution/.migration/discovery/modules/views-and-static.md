# Views & Static Assets

## Purpose

Server-side Razor views for the catalog admin UI plus the client-side static assets
(Bootstrap, jQuery, validation, custom CSS). The views are rendered by `CatalogController`
and the shared layout.

## Source Files

| File | Language | Role |
| ---- | -------- | ---- |
| `src/eShopLegacyMVC/Views/Catalog/Index.cshtml` | Razor | catalog list page |
| `src/eShopLegacyMVC/Views/Catalog/CatalogTable.cshtml` | Razor | partial — items table |
| `src/eShopLegacyMVC/Views/Catalog/Details.cshtml` | Razor | item detail |
| `src/eShopLegacyMVC/Views/Catalog/Create.cshtml` | Razor | create form |
| `src/eShopLegacyMVC/Views/Catalog/Edit.cshtml` | Razor | edit form |
| `src/eShopLegacyMVC/Views/Catalog/Delete.cshtml` | Razor | delete confirm |
| `src/eShopLegacyMVC/Views/Shared/_Layout.cshtml` | Razor | master layout |
| `src/eShopLegacyMVC/Views/Shared/Error.cshtml` | Razor | error page |
| `src/eShopLegacyMVC/Views/_ViewStart.cshtml` | Razor | layout binding |
| `src/eShopLegacyMVC/Views/Web.config` | XML | Razor view engine config |
| `src/eShopLegacyMVC/Scripts/*.js` | JS | jQuery, bootstrap, validation, modernizr (vendor) |
| `src/eShopLegacyMVC/Content/*.css` | CSS | bootstrap + custom/base/site styles |

## Data Flow

### Inbound

- `CatalogController` actions pass `PaginatedItemsViewModel<CatalogItem>` / `CatalogItem` + `ViewBag` SelectLists for Brand/Type to views.

### Outbound

- Rendered HTML to browser; bundles referenced via `BundleConfig` names.

## Business Rules

| # | Rule | Source Location | Confidence |
| --- | ---- | --------------- | ---------- |
| 1 | Create/Edit forms bind `CatalogBrandId`/`CatalogTypeId` from `ViewBag` SelectLists | `src/eShopLegacyMVC/Controllers/CatalogController.cs:52-53,90-91` | clear |
| 2 | Item images sourced from computed `PictureUri` (PicController route) | `src/eShopLegacyMVC/Controllers/CatalogController.cs:160-163` | clear |
| 3 | Bundles: jquery, jqueryval, modernizr, bootstrap, css | `src/eShopLegacyMVC/App_Start/BundleConfig.cs:10-29` | clear |

## Dependencies

### Called by (upstream)

- web-controllers (`CatalogController`), MVC view engine.

### Calls (downstream)

- Bundles defined in app-bootstrap-config (`BundleConfig`).

## External Interfaces

| Type | Target | Details |
| ---- | ------ | ------- |
| HTTP (HTML/CSS/JS) | Browser | server-rendered Razor + static bundles |

## Complexity Assessment

**Rating**: Simple

**Justification**: Standard CRUD Razor scaffolding plus vendored front-end libraries.
No business logic in views beyond display binding. JS/CSS are third-party and account
for the bulk of file count but carry no domain logic.

## Unknowns

- Vendored JS/CSS versions (jQuery, bootstrap) may need refresh on migration but are not domain-critical.
