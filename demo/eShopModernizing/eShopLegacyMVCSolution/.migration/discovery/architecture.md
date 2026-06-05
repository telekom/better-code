# eShopLegacyMVC — Architecture Diagrams

Diagrams use only evidenced interactions from the source. Each has both a Mermaid and a
PlantUML block.

## 1. System Context

The eShopLegacyMVC web app as a single box with its external actors and systems.

```mermaid
graph LR
    Operator([Operator / Browser])
    ApiClient([HTTP API Client])
    App[eShopLegacyMVC<br/>ASP.NET MVC 5 app]
    DB[(SQL Server LocalDB<br/>CatalogDb)]
    FS[/Filesystem<br/>~/Pics, Setup/*/]
    AI[[Azure Application Insights]]

    Operator -->|HTTP HTML/forms| App
    ApiClient -->|HTTP api/*| App
    App -->|EF6 + raw SQL| DB
    App -->|read images / CSV+ZIP| FS
    App -->|telemetry HTTPS| AI
```

```plantuml
@startuml
left to right direction
actor "Operator / Browser" as Operator
actor "HTTP API Client" as ApiClient
rectangle "eShopLegacyMVC\n(ASP.NET MVC 5)" as App
database "SQL Server LocalDB\nCatalogDb" as DB
folder "Filesystem\n~/Pics, Setup/*" as FS
cloud "Azure Application Insights" as AI

Operator --> App : HTTP HTML/forms
ApiClient --> App : HTTP api/*
App --> DB : EF6 + raw SQL
App --> FS : read images / CSV+ZIP
App --> AI : telemetry (HTTPS)
@enduml
```

## 2. Service / Component Interactions

Internal components and the calls between them (protocol/mechanism labelled).

```mermaid
graph TD
    subgraph Web Layer
      CC[CatalogController]
      PC[PicController]
      BC[BrandsController]
      FC[FilesController]
    end
    subgraph Services
      ISvc{{ICatalogService}}
      Svc[CatalogService]
      Mock[CatalogServiceMock]
    end
    subgraph Domain/Data
      Ctx[CatalogDBContext]
      HiLo[CatalogItemHiLoGenerator]
      Init[CatalogDBInitializer]
      Pre[PreconfiguredData]
    end
    Util[Serializing<br/>BinaryFormatter]
    DB[(SQL Server)]

    CC -->|in-proc| ISvc
    PC -->|in-proc| ISvc
    BC -->|in-proc| ISvc
    FC -->|in-proc| ISvc
    FC -->|serialize| Util
    ISvc -. UseMockData=false .-> Svc
    ISvc -. UseMockData=true .-> Mock
    Svc -->|LINQ| Ctx
    Svc -->|next id| HiLo
    Mock -->|seed| Pre
    Init -->|seed+DDL| Ctx
    HiLo -->|NEXT VALUE FOR| DB
    Ctx -->|EF6| DB
    PC -->|ReadAllBytes| FSimg[/~/Pics/]
```

```plantuml
@startuml
package "Web Layer" {
  [CatalogController]
  [PicController]
  [BrandsController]
  [FilesController]
}
package "Services" {
  interface ICatalogService
  [CatalogService]
  [CatalogServiceMock]
}
package "Domain/Data" {
  [CatalogDBContext]
  [CatalogItemHiLoGenerator]
  [CatalogDBInitializer]
  [PreconfiguredData]
}
[Serializing] 
database "SQL Server" as DB

[CatalogController] --> ICatalogService
[PicController] --> ICatalogService
[BrandsController] --> ICatalogService
[FilesController] --> ICatalogService
[FilesController] --> [Serializing]
ICatalogService ..> [CatalogService] : UseMockData=false
ICatalogService ..> [CatalogServiceMock] : UseMockData=true
[CatalogService] --> [CatalogDBContext]
[CatalogService] --> [CatalogItemHiLoGenerator]
[CatalogServiceMock] --> [PreconfiguredData]
[CatalogDBInitializer] --> [CatalogDBContext]
[CatalogItemHiLoGenerator] --> DB : NEXT VALUE FOR
[CatalogDBContext] --> DB : EF6
@enduml
```

## 3. Main Request Flows

### 3a. Browse catalog (`GET /Catalog/Index`)

```mermaid
sequenceDiagram
    participant B as Browser
    participant C as CatalogController
    participant S as CatalogService
    participant X as CatalogDBContext
    participant D as SQL Server
    B->>C: GET /Catalog/Index?pageSize&pageIndex
    C->>S: GetCatalogItemsPaginated(size,index)
    S->>X: LINQ (Include Brand,Type; Skip/Take)
    X->>D: SELECT ... ORDER BY Id
    D-->>X: rows
    X-->>S: List<CatalogItem>
    S-->>C: PaginatedItemsViewModel
    C->>C: AddUriPlaceHolder (compute PictureUri)
    C-->>B: View(paginated)
```

```plantuml
@startuml
actor Browser
Browser -> CatalogController : GET /Catalog/Index
CatalogController -> CatalogService : GetCatalogItemsPaginated
CatalogService -> CatalogDBContext : LINQ Skip/Take Include
CatalogDBContext -> "SQL Server" : SELECT
"SQL Server" --> CatalogDBContext : rows
CatalogDBContext --> CatalogService : List<CatalogItem>
CatalogService --> CatalogController : PaginatedItemsViewModel
CatalogController --> Browser : View
@enduml
```

### 3b. Create item (`POST /Catalog/Create`)

```mermaid
sequenceDiagram
    participant B as Browser
    participant C as CatalogController
    participant S as CatalogService
    participant H as HiLoGenerator
    participant D as SQL Server
    B->>C: POST Create (anti-forgery, [Bind])
    alt ModelState valid
        C->>S: CreateCatalogItem(item)
        S->>H: GetNextSequenceValue(db)
        H->>D: NEXT VALUE FOR catalog_hilo (every 10th)
        H-->>S: id
        S->>D: INSERT + SaveChanges
        C-->>B: Redirect Index
    else invalid
        C-->>B: View(item) with SelectLists
    end
```

```plantuml
@startuml
actor Browser
Browser -> CatalogController : POST /Catalog/Create
alt ModelState valid
  CatalogController -> CatalogService : CreateCatalogItem
  CatalogService -> CatalogItemHiLoGenerator : GetNextSequenceValue
  CatalogItemHiLoGenerator -> "SQL Server" : NEXT VALUE FOR (every 10th)
  CatalogService -> "SQL Server" : INSERT + SaveChanges
  CatalogController --> Browser : Redirect Index
else invalid
  CatalogController --> Browser : View(item)
end
@enduml
```

### 3c. Serve picture (`GET /items/{id}/pic`)

```mermaid
sequenceDiagram
    participant B as Browser
    participant P as PicController
    participant S as CatalogService
    participant F as Filesystem ~/Pics
    B->>P: GET /items/{id}/pic
    P->>S: FindCatalogItem(id)
    S-->>P: item (or null)
    alt item found
        P->>F: ReadAllBytes(~/Pics/PictureFileName)
        F-->>P: bytes
        P-->>B: File(bytes, mime-from-extension)
    else not found
        P-->>B: 404
    end
```

```plantuml
@startuml
actor Browser
Browser -> PicController : GET /items/{id}/pic
PicController -> CatalogService : FindCatalogItem(id)
CatalogService --> PicController : item / null
alt found
  PicController -> Filesystem : ReadAllBytes(~/Pics/..)
  Filesystem --> PicController : bytes
  PicController --> Browser : File(bytes, mime)
else
  PicController --> Browser : 404
end
@enduml
```

## 4. Data Flow (seed / startup)

```mermaid
graph LR
    Start[Application_Start] --> DI[Autofac container]
    Start --> Init{UseMockData?}
    Init -- false --> SetInit[SetInitializer CatalogDBInitializer]
    SetInit --> Seed[Seed on first DB access]
    Seed --> Seq[Run 3 sequence .sql]
    Seq --> Src{UseCustomizationData?}
    Src -- false --> Pre[PreconfiguredData lists]
    Src -- true --> CSV[Setup/*.csv]
    Src -- true --> ZIP[Setup/CatalogItems.zip -> ~/Pics]
    Pre --> DB[(SQL Server)]
    CSV --> DB
    Init -- true --> MockMem[In-memory PreconfiguredData]
```

```plantuml
@startuml
[Application_Start] --> [Autofac container]
[Application_Start] --> [SetInitializer] : UseMockData=false
[SetInitializer] --> [Seed]
[Seed] --> [Run sequence .sql]
[Run sequence .sql] --> [PreconfiguredData] : UseCustomizationData=false
[Run sequence .sql] --> [Setup CSV/ZIP] : UseCustomizationData=true
[PreconfiguredData] --> [SQL Server]
[Setup CSV/ZIP] --> [SQL Server]
@enduml
```
