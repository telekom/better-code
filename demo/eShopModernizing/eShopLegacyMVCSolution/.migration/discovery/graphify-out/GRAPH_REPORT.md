# Graph Report - eShopLegacyMVCSolution  (2026-06-03)

## Corpus Check
- 121 files · ~716,212 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1330 nodes · 3572 edges · 66 communities (52 shown, 14 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4ab40a4e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]

## God Nodes (most connected - your core abstractions)
1. `CatalogDBInitializer` - 19 edges
2. `c()` - 15 edges
3. `P()` - 14 edges
4. `CatalogController` - 14 edges
5. `CatalogServiceMock` - 13 edges
6. `CatalogService` - 13 edges
7. `getBoundaries()` - 13 edges
8. `s()` - 13 edges
9. `getBoundaries()` - 13 edges
10. `getBoundaries()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `FilesController` --references--> `ICatalogService`  [EXTRACTED]
  eShopPorted/Controllers/Api/FilesController.cs → src/eShopLegacyMVC/Controllers/WebApi/BrandsController.cs
- `BrandsController` --references--> `ICatalogService`  [EXTRACTED]
  eShopPorted/Controllers/Api/BrandsController.cs → src/eShopLegacyMVC/Controllers/WebApi/BrandsController.cs
- `CatalogServiceMock` --inherits--> `ICatalogService`  [EXTRACTED]
  src/eShopLegacyMVC/Services/CatalogServiceMock.cs → src/eShopLegacyMVC/Controllers/WebApi/BrandsController.cs
- `CatalogService` --inherits--> `ICatalogService`  [EXTRACTED]
  src/eShopLegacyMVC/Services/CatalogService.cs → src/eShopLegacyMVC/Controllers/WebApi/BrandsController.cs
- `PicController` --references--> `ICatalogService`  [EXTRACTED]
  src/eShopLegacyMVC/Controllers/PicController.cs → src/eShopLegacyMVC/Controllers/WebApi/BrandsController.cs

## Communities (66 total, 14 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (85): Alert(), allowedAttribute(), applyStyle(), applyStyleOnLoad(), arrow(), attachToScrollParents(), Button(), Carousel() (+77 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (81): addCombinator(), addGetHookIf(), addHandle(), addToPrefiltersOrTransports(), adjustCSS(), adoptValue(), ajaxConvert(), ajaxExtend() (+73 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (65): applyStyle(), applyStyleOnLoad(), arrow(), attachToScrollParents(), BEHAVIORS, clockwise(), computeAutoPlacement(), computeStyle() (+57 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (67): addCombinator(), addGetHookIf(), addHandle(), adjustCSS(), adoptValue(), assert(), boxModelAdjustment(), buildFragment() (+59 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (63): applyStyle(), applyStyleOnLoad(), arrow(), attachToScrollParents(), clockwise(), computeAutoPlacement(), computeStyle(), defineProperties() (+55 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (63): applyStyle(), applyStyleOnLoad(), arrow(), attachToScrollParents(), clockwise(), computeAutoPlacement(), computeStyle(), defineProperties() (+55 more)

### Community 6 - "Community 6"
Cohesion: 0.1
Nodes (57): $(), a(), ae(), at(), be(), C(), ce(), ct() (+49 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (43): _(), a(), ae(), b(), be(), c(), ce(), d() (+35 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (45): a(), ae(), at(), b(), be(), ce(), D(), de() (+37 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (17): bool, CatalogDBContext, CatalogItemHiLoGenerator, CreateDatabaseIfNotExists, CatalogDBInitializer, eShopLegacyMVC.Models.Infrastructure, CatalogItem, eShopLegacyMVC.Models (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (44): attachToScrollParents(), computeAutoPlacement(), find(), findCommonOffsetParent(), findIndex(), getArea(), getBordersSize(), getBoundaries() (+36 more)

### Community 11 - "Community 11"
Cohesion: 0.15
Nodes (43): attachToScrollParents(), computeAutoPlacement(), find(), findCommonOffsetParent(), findIndex(), getArea(), getBordersSize(), getBoundaries() (+35 more)

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (43): attachToScrollParents(), computeAutoPlacement(), find(), findCommonOffsetParent(), findIndex(), getArea(), getBordersSize(), getBoundaries() (+35 more)

### Community 13 - "Community 13"
Cohesion: 0.2
Nodes (43): _(), a(), b(), be(), c(), ce(), d(), de() (+35 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (41): a(), ae(), bn(), Bt(), c(), ce(), ee(), fe() (+33 more)

### Community 15 - "Community 15"
Cohesion: 0.3
Nodes (27): _(), a(), b(), c(), d(), e(), f(), g() (+19 more)

### Community 16 - "Community 16"
Cohesion: 0.28
Nodes (26): A(), b(), c(), d(), e(), f(), g(), h() (+18 more)

### Community 17 - "Community 17"
Cohesion: 0.31
Nodes (24): a(), b(), c(), D(), g(), h(), i(), j() (+16 more)

### Community 18 - "Community 18"
Cohesion: 0.34
Nodes (24): a(), b(), c(), E(), g(), h(), i(), j() (+16 more)

### Community 19 - "Community 19"
Cohesion: 0.17
Nodes (22): Alert(), allowedAttribute(), Button(), Carousel(), Collapse(), _createClass(), _defineProperties(), _defineProperty() (+14 more)

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (19): Callbacks, code:js (var reference = document.querySelector('.my-button');), code:js (const reference = document.querySelector('.my-button');), code:js (function applyReactStyle(data) {), Copyright and license, Credits, Dist targets, Installation (+11 more)

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (16): addStyleSheet(), contains(), createDocumentFragment(), createElement(), getElements(), getExpandoData(), is(), isEventSupported() (+8 more)

### Community 22 - "Community 22"
Cohesion: 0.33
Nodes (16): addStyleSheet(), contains(), createDocumentFragment(), createElement(), getElements(), getExpandoData(), is(), isEventSupported() (+8 more)

### Community 23 - "Community 23"
Cohesion: 0.13
Nodes (9): BrandsController, eShopPorted.Controllers, CatalogController2, eShopLegacyMVC.Controllers.Api, BrandDTO, eShopPorted.Controllers, FilesController, Controller (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.15
Nodes (4): List, CatalogServiceMock, eShopLegacyMVC.Services, eShopPorted.Services

### Community 25 - "Community 25"
Cohesion: 0.26
Nodes (12): BaseModifier, Behavior, Boundary, Data, ModifierFn, Modifiers, Offset, Placement (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.2
Nodes (3): CatalogController, eShopLegacyMVC.Controllers, eShopPorted.Controllers

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (4): IDisposable, eShopLegacyMVC.Services, eShopPorted.Services, ICatalogService

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (7): CatalogBrandConfig, eShopPorted.Models.Config, CatalogItemConfig, eShopPorted.Models.Config, CatalogTypeConfig, eShopPorted.Models.Config, IEntityTypeConfiguration

### Community 29 - "Community 29"
Cohesion: 0.32
Nodes (10): d(), e(), i(), l(), n(), o(), r(), s() (+2 more)

### Community 30 - "Community 30"
Cohesion: 0.32
Nodes (10): appendModelPrefix(), escapeAttributeValue(), getModelPrefix(), onError(), onErrors(), onReset(), onSuccess(), setValidationValues() (+2 more)

### Community 31 - "Community 31"
Cohesion: 0.36
Nodes (9): a(), c(), i(), l(), n(), o(), r(), s() (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (6): ApiController, BrandsController, eShopLegacyMVC.Controllers.WebApi, BrandDTO, eShopLegacyMVC.Controllers.WebApi, FilesController

### Community 33 - "Community 33"
Cohesion: 0.27
Nodes (4): DbContext, CatalogDBContext, eShopLegacyMVC.Models, eShopPorted.Models

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (3): eShopLegacyMVC.Models.Infrastructure, eShopPorted.Models.Infrastructure, PreconfiguredData

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (4): eShopLegacyMVC.Controllers, eShopPorted.Controllers, PicController, ILog

### Community 36 - "Community 36"
Cohesion: 0.32
Nodes (3): MvcApplication, HttpApplication, IContainer

### Community 37 - "Community 37"
Cohesion: 0.33
Nodes (3): Migration, eShopPorted.Migrations, Initial

### Community 38 - "Community 38"
Cohesion: 0.4
Nodes (3): ActivityIdHelper, eShopLegacyMVC, WebRequestInfo

### Community 39 - "Community 39"
Cohesion: 0.33
Nodes (4): int, CatalogItemHiLoGenerator, eShopLegacyMVC.Models, object

### Community 42 - "Community 42"
Cohesion: 0.4
Nodes (3): CatalogDBContextModelSnapshot, eShopPorted.Migrations, ModelSnapshot

### Community 43 - "Community 43"
Cohesion: 0.6
Nodes (3): delegate(), handle(), handler()

### Community 44 - "Community 44"
Cohesion: 0.4
Nodes (3): CatalogBrand, eShopLegacyMVC.Models, eShopPorted.Models

### Community 46 - "Community 46"
Cohesion: 0.4
Nodes (3): eShopLegacyMVC.ViewModel, eShopPorted.ViewModel, PaginatedItemsViewModel

### Community 47 - "Community 47"
Cohesion: 0.4
Nodes (3): CatalogType, eShopLegacyMVC.Models, eShopPorted.Models

## Knowledge Gaps
- **64 isolated node(s):** `eShopPorted`, `eShopPorted`, `eShopPorted.Services`, `List`, `eShopPorted.Services` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PicController` connect `Community 35` to `Community 9`, `Community 23`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `ICatalogService` connect `Community 23` to `Community 32`, `Community 35`, `Community 9`, `Community 24`, `Community 26`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **What connects `eShopPorted`, `eShopPorted`, `eShopPorted.Services` to the rest of the system?**
  _64 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._