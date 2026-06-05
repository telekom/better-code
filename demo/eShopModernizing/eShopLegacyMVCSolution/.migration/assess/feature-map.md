# Feature Map — eShopLegacyMVC

The app is a single bounded context (**Catalog Management**). It decomposes into 5
business features. The automated extractor misfired on this small codebase, so features
were derived manually from the discovery module docs.

| Feature | Business capability | Constituent modules |
| ------- | ------------------- | ------------------- |
| Catalog Item Management | CRUD admin UI for products (browse/create/edit/delete, paging, validation) | web-controllers, catalog-services, domain-model, views-and-static |
| Reference Data (Brands & Types) + Web API | Read brands/types; expose via `api/Brands`, `api/Files`; UI dropdowns | web-controllers, catalog-services, domain-model, shared-utilities |
| Product Imagery | Serve item pictures over HTTP; import picture sets on seed | web-controllers, data-persistence-seeding |
| Catalog Data Seeding & Initialization | Create DB, run sequences, seed from hardcoded/CSV/ZIP | data-persistence-seeding, domain-model |
| Application Platform (cross-cutting) | Hosting, DI, routing, config, logging, telemetry | app-bootstrap-config, shared-utilities |

Reference target: **eShopPorted** (in-repo ASP.NET Core + EF Core port of this context).

```mermaid
graph TD
    subgraph CIM[Catalog Item Management]
        WC1[web-controllers]
        CS1[catalog-services]
        DM1[domain-model]
        V1[views-and-static]
    end
    subgraph REF[Reference Data + Web API]
        WC2[web-controllers]
        CS2[catalog-services]
        SU[shared-utilities]
    end
    subgraph IMG[Product Imagery]
        PC[web-controllers: PicController]
        SEED1[data-persistence-seeding: pictures]
    end
    subgraph SEED[Data Seeding & Init]
        DPS[data-persistence-seeding]
        HL[domain-model: HiLo]
    end
    subgraph PLAT[Application Platform]
        BOOT[app-bootstrap-config]
        SU2[shared-utilities]
    end

    CIM --> PLAT
    REF --> PLAT
    IMG --> PLAT
    SEED --> PLAT
    CIM --> SEED
    IMG --> SEED
    REF --> CIM
```
