# Decomposition Diagrams — Catalog Item Management

All diagrams trace to `spec.json` / `flows.json` / `data-model.json`.

## 1. Sequence — FLOW-001 Browse catalog (paginated listing)

```mermaid
sequenceDiagram
    participant B as Browser
    participant C as CatalogController
    participant S as CatalogService
    participant DB as CatalogDBContext/SQL
    B->>C: GET /Catalog/Index?pageSize&pageIndex
    C->>S: GetCatalogItemsPaginated(pageSize,pageIndex)
    S->>DB: count + Skip/Take Include(Brand,Type) order by Id
    DB-->>S: items + total
    S-->>C: PaginatedItemsViewModel
    C->>C: compute PictureUri per item (BR-010)
    C-->>B: Index view
```

```plantuml
@startuml
actor Browser
Browser -> CatalogController : GET /Catalog/Index
CatalogController -> CatalogService : GetCatalogItemsPaginated
CatalogService -> "CatalogDBContext/SQL" : count + Skip/Take Include
"CatalogDBContext/SQL" --> CatalogService : items + total
CatalogService --> CatalogController : PaginatedItemsViewModel
CatalogController -> CatalogController : compute PictureUri (BR-010)
CatalogController --> Browser : Index view
@enduml
```

## 2. Sequence — FLOW-003 Create catalog item

```mermaid
sequenceDiagram
    participant B as Browser
    participant C as CatalogController
    participant S as CatalogService
    participant H as HiLoGenerator
    participant DB as SQL
    B->>C: POST /Catalog/Create (anti-forgery, [Bind])
    C->>C: validate token + model (BR-001..005,012,013)
    alt ModelState valid
        C->>S: CreateCatalogItem(item)
        S->>H: GetNextSequenceValue(db) (BR-011,016)
        H->>DB: NEXT VALUE FOR catalog_hilo (every 10th)
        H-->>S: id
        S->>DB: INSERT + SaveChanges
        C-->>B: redirect Index
    else invalid
        C-->>B: redisplay Create view (ERR-003)
    end
```

```plantuml
@startuml
actor Browser
Browser -> CatalogController : POST /Catalog/Create
CatalogController -> CatalogController : validate token+model
alt ModelState valid
  CatalogController -> CatalogService : CreateCatalogItem
  CatalogService -> HiLoGenerator : GetNextSequenceValue
  HiLoGenerator -> SQL : NEXT VALUE FOR catalog_hilo (every 10th)
  CatalogService -> SQL : INSERT + SaveChanges
  CatalogController --> Browser : redirect Index
else invalid
  CatalogController --> Browser : redisplay Create view
end
@enduml
```

## 3. Sequence — FLOW-002 / 004 / 005 (Details, Edit, Delete by id)

```mermaid
sequenceDiagram
    participant B as Browser
    participant C as CatalogController
    participant S as CatalogService
    participant DB as SQL
    B->>C: GET/POST with id
    C->>C: id null? -> 400 (BR-006/ERR-001)
    C->>S: FindCatalogItem(id)
    S->>DB: SELECT Include(Brand,Type)
    DB-->>S: item or null
    alt not found
        C-->>B: 404 (BR-007/ERR-002)
    else found
        C->>S: (Edit) Update / (Delete) Remove + SaveChanges
        C-->>B: view or redirect Index
    end
```

```plantuml
@startuml
actor Browser
Browser -> CatalogController : GET/POST with id
CatalogController -> CatalogController : id null? -> 400
CatalogController -> CatalogService : FindCatalogItem(id)
CatalogService -> SQL : SELECT Include
SQL --> CatalogService : item / null
alt not found
  CatalogController --> Browser : 404
else found
  CatalogController -> CatalogService : Update/Remove + SaveChanges
  CatalogController --> Browser : view / redirect
end
@enduml
```

## 4. Entity Relationship Diagram

```mermaid
erDiagram
    CATALOGITEM }o--|| CATALOGBRAND : "CatalogBrandId"
    CATALOGITEM }o--|| CATALOGTYPE : "CatalogTypeId"
    CATALOGITEM {
        int Id PK
        string Name
        decimal Price
        string PictureFileName
        int CatalogBrandId FK
        int CatalogTypeId FK
        int AvailableStock
        int RestockThreshold
        int MaxStockThreshold
        bool OnReorder
    }
    CATALOGBRAND {
        int Id PK
        string Brand
    }
    CATALOGTYPE {
        int Id PK
        string Type
    }
```

```plantuml
@startuml
entity CatalogItem {
  * Id : int <<PK>>
  Name : string
  Price : decimal
  PictureFileName : string
  CatalogBrandId : int <<FK>>
  CatalogTypeId : int <<FK>>
  AvailableStock : int
  RestockThreshold : int
  MaxStockThreshold : int
  OnReorder : bool
}
entity CatalogBrand { * Id : int <<PK>> \n Brand : string }
entity CatalogType { * Id : int <<PK>> \n Type : string }
CatalogBrand ||--o{ CatalogItem
CatalogType ||--o{ CatalogItem
@enduml
```

## 5. Activity — Create/Edit validation branching (BR-013)

```plantuml
@startuml
start
:receive POST (anti-forgery + bound fields);
if (ModelState valid?) then (yes)
  if (Create?) then (yes)
    :assign Id from HiLo (BR-011);
    :insert + SaveChanges;
  else (Edit)
    :mark Modified + SaveChanges (BR-015);
  endif
  :redirect to Index;
else (no)
  :repopulate Brand/Type SelectLists;
  :redisplay form with errors (ERR-003);
endif
stop
@enduml
```

> No standalone state-machine diagram: the feature has create/update/delete lifecycle
> transitions (BR-011, BR-015, BR-017) but no multi-state status field to model.
