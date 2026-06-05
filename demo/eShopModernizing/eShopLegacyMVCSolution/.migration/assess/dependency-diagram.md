# Migration Dependency & Sequence Diagrams

Dependencies are evidence-based from per-feature "Depends On" analysis (the automated
edge detector returned 0 because features share modules). Arrows point from a feature to
the feature it **depends on** (must migrate first).

## 1. Feature Dependency Graph (color-coded by wave)

> Wave 1 = enablers (red), Wave 2 = core (blue), Wave 3 = imagery (green).

```mermaid
graph TD
    PLAT[Application Platform<br/>Wave 1]
    SEED[Data Seeding & Init<br/>Wave 1]
    ITEM[Catalog Item Management<br/>Wave 2]
    REF[Reference Data + Web API<br/>Wave 2]
    IMG[Product Imagery<br/>Wave 3]

    SEED --> PLAT
    ITEM --> PLAT
    ITEM --> SEED
    REF --> PLAT
    REF --> ITEM
    IMG --> PLAT
    IMG --> ITEM
    IMG --> SEED

    classDef w1 fill:#ffd6d6,stroke:#c0392b;
    classDef w2 fill:#d6e4ff,stroke:#2c3e9e;
    classDef w3 fill:#d8f5d8,stroke:#1e8449;
    class PLAT,SEED w1;
    class ITEM,REF w2;
    class IMG w3;
```

## 2. Migration Timeline (waves & parallelism)

```mermaid
gantt
    title eShopLegacyMVC Migration Waves
    dateFormat  X
    axisFormat %s
    section Phase 0
    Foundation (host, CI/CD, tests, storage)   :p0, 0, 3
    section Wave 1 (enablers)
    Application Platform        :w1a, after p0, 3
    Data Seeding & Init         :w1b, after p0, 3
    section Wave 2 (core)
    Catalog Item Management     :w2a, after w1a, 3
    Reference Data + Web API    :w2b, after w2a, 2
    section Wave 3 (imagery)
    Product Imagery             :w3a, after w2a, 2
    section Decommission
    Cutover & legacy shutdown   :dc, after w2b, 2
```

## 3. Feature → Module Mapping

```mermaid
graph LR
    subgraph PLAT[Application Platform]
        m1[app-bootstrap-config]
        m2[shared-utilities]
    end
    subgraph SEED[Data Seeding & Init]
        m3[data-persistence-seeding]
        m4[domain-model: HiLo/Context]
    end
    subgraph ITEM[Catalog Item Management]
        m5[web-controllers: CatalogController]
        m6[catalog-services]
        m7[domain-model: CatalogItem]
        m8[views-and-static]
    end
    subgraph REF[Reference Data + Web API]
        m9[web-controllers: Brands/Files]
        m10[domain-model: Brand/Type]
        m11[shared-utilities: Serializing]
    end
    subgraph IMG[Product Imagery]
        m12[web-controllers: PicController]
        m13[data-persistence-seeding: pictures]
    end
```
