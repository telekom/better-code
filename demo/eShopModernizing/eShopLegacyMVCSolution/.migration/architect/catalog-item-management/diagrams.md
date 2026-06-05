# Architecture Diagrams (C4) — Catalog Item Management (catalog-service)

Only elements present in `blueprint.json` are shown.

## 1. C4 Context

```mermaid
graph TD
    Operator([Catalog Operator])
    Catalog[catalog-service<br/>ASP.NET Core 8 MVC]
    DB[(Azure SQL<br/>CatalogDb)]
    AI[[Application Insights]]
    Operator -->|HTTPS / HTML| Catalog
    Catalog -->|EF Core| DB
    Catalog -->|telemetry| AI
```

```plantuml
@startuml
actor "Catalog Operator" as Operator
rectangle "catalog-service\n(ASP.NET Core 8 MVC)" as Catalog
database "Azure SQL\nCatalogDb" as DB
cloud "Application Insights" as AI
Operator --> Catalog : HTTPS / HTML
Catalog --> DB : EF Core
Catalog --> AI : telemetry
@enduml
```

## 2. C4 Container

```mermaid
graph TD
    Operator([Operator]) -->|HTTPS| Web[catalog-service container<br/>Kestrel + MVC]
    Web -->|EF Core / TDS| DB[(Azure SQL: Catalog, CatalogBrand, CatalogType, catalog_hilo)]
    Web -->|OTel| AI[[Application Insights]]
    Web -->|secrets| KV[[Azure Key Vault]]
```

```plantuml
@startuml
actor Operator
node "catalog-service container\n(Kestrel + MVC)" as Web
database "Azure SQL\nCatalog/Brand/Type/catalog_hilo" as DB
cloud "Application Insights" as AI
cloud "Azure Key Vault" as KV
Operator --> Web : HTTPS
Web --> DB : EF Core / TDS
Web --> AI : OpenTelemetry
Web --> KV : secrets
@enduml
```

## 3. C4 Component — catalog-service internals

```mermaid
graph TD
    CC[CatalogController<br/>controller]
    VAL[CatalogItemValidator<br/>validation]
    SVC[CatalogService : ICatalogService<br/>application]
    DOM[CatalogItem / CatalogBrand / CatalogType<br/>domain]
    VM[PaginatedItemsViewModel<br/>view model]
    REPO[CatalogRepository + CatalogDbContext<br/>infrastructure]
    IDG[CatalogIdGenerator<br/>infrastructure]
    MW[GlobalExceptionHandlerMiddleware]
    CC --> VAL
    CC --> SVC
    CC --> VM
    SVC --> DOM
    SVC --> REPO
    SVC --> IDG
    REPO --> DOM
    MW -.wraps.-> CC
```

```plantuml
@startuml
component CatalogController
component CatalogItemValidator
component "CatalogService : ICatalogService" as CatalogService
component "Domain entities" as Domain
component PaginatedItemsViewModel
component "CatalogRepository + CatalogDbContext" as Repo
component CatalogIdGenerator
component GlobalExceptionHandlerMiddleware
CatalogController --> CatalogItemValidator
CatalogController --> CatalogService
CatalogController --> PaginatedItemsViewModel
CatalogService --> Domain
CatalogService --> Repo
CatalogService --> CatalogIdGenerator
Repo --> Domain
GlobalExceptionHandlerMiddleware ..> CatalogController
@enduml
```

## 4. Data Flow — Create item (FLOW-003)

```mermaid
sequenceDiagram
    participant O as Operator
    participant C as CatalogController
    participant V as CatalogItemValidator
    participant S as CatalogService
    participant G as CatalogIdGenerator
    participant R as CatalogRepository
    participant DB as Azure SQL
    O->>C: POST /Catalog/Create (anti-forgery, CatalogItemEditRequest)
    C->>V: validate (BR-001..005)
    alt valid
        C->>S: CreateCatalogItem
        S->>G: GetNextId (BR-016, NEXT VALUE FOR catalog_hilo)
        G->>DB: sequence fetch (every 10th)
        S->>R: Add + SaveChanges
        R->>DB: INSERT
        C-->>O: 302 -> /Catalog
    else invalid
        C-->>O: redisplay form (ERR-003)
    end
```

```plantuml
@startuml
actor Operator
Operator -> CatalogController : POST /Catalog/Create
CatalogController -> CatalogItemValidator : validate
alt valid
  CatalogController -> CatalogService : CreateCatalogItem
  CatalogService -> CatalogIdGenerator : GetNextId
  CatalogIdGenerator -> "Azure SQL" : NEXT VALUE FOR catalog_hilo
  CatalogService -> CatalogRepository : Add + SaveChanges
  CatalogRepository -> "Azure SQL" : INSERT
  CatalogController --> Operator : 302 /Catalog
else invalid
  CatalogController --> Operator : redisplay form
end
@enduml
```

## 5. Deployment

```mermaid
graph TD
    subgraph Cloud[Azure / Kubernetes]
        Pod[catalog-service<br/>container :8080]
        SQL[(Azure SQL Database)]
        AI[[Application Insights]]
        KV[[Key Vault]]
    end
    LB[Ingress / App Gateway] --> Pod
    Pod --> SQL
    Pod --> AI
    Pod --> KV
```

```plantuml
@startuml
node "Ingress / App Gateway" as LB
node "catalog-service container :8080" as Pod
database "Azure SQL Database" as SQL
cloud "Application Insights" as AI
cloud "Key Vault" as KV
LB --> Pod
Pod --> SQL
Pod --> AI
Pod --> KV
@enduml
```
