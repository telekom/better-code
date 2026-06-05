# Feature: Product Imagery

## Business Capability

Serves catalog item pictures to the browser (`GET /items/{id}/pic`) and imports a picture
set into the app during customization seeding. Each catalog item references a
`PictureFileName`; the UI builds image URLs from a named route.

## Current Implementation

### Modules

| Module | Role | Complexity | Source |
| ------ | ---- | ---------- | ------ |
| web-controllers | primary (PicController) | Moderate | discovery/modules/web-controllers.md |
| data-persistence-seeding | support (AddCatalogItemPictures) | Complex | discovery/modules/data-persistence-seeding.md |

### Data Flow

Browser `<img>` → named route `items/{catalogItemId:int}/pic` → `PicController.Index` →
`ICatalogService.FindCatalogItem` → reads `~/Pics/{PictureFileName}` via
`File.ReadAllBytes` → returns `File(buffer, mime)` with MIME derived from extension
(`Controllers/PicController.cs:25-49`). Seeding (customization mode) wipes `~/Pics` then
unzips `Setup/CatalogItems.zip` into it (`Models/Infrastructure/CatalogDBInitializer.cs:339-354`).

### External Interfaces

| Type | Target | Protocol | Notes |
| ---- | ------ | -------- | ----- |
| File | `~/Pics/*` | local FS | synchronous read; no missing-file guard after item found |
| File | `Setup/CatalogItems.zip` | local FS | destructive: deletes all `~/Pics` first |
| Screen | Browser | HTTP (image) | MIME by extension; unknown → octet-stream |

## Migration Strategy

### Approach: Refactor + Replatform (move blob storage off local disk)

### Target Design

Port `PicController` to an ASP.NET Core endpoint. **Replatform** the picture store from
the local `~/Pics` folder to object storage (Azure Blob Storage / S3) so the app is
stateless and cloud/container-friendly. Replace the destructive folder-wipe import with
idempotent blob uploads. Add a missing-blob guard (return 404 instead of throwing).

### Feature Parity

| Current Behavior | Target Behavior | Gap/Change |
| ---------------- | --------------- | ---------- |
| Reads local `~/Pics` file | Reads object storage blob | storage backend change; URL strategy |
| `ReadAllBytes` throws if file missing | 404 on missing blob | bug fix |
| Seed wipes folder then unzips | Idempotent blob upload | non-destructive import |
| MIME by extension switch | same or content-type from blob metadata | minor |

### Data Migration

One-time bulk upload of existing `~/Pics` images (and `Setup/CatalogItems.zip` contents)
into the target bucket/container, keyed by `PictureFileName`.

## Dependencies

### Depends On (migrate these first)

- Application Platform — hosting/DI/config (storage connection).
- Catalog Item Management — item lookup + `PictureUri` route generation.
- Catalog Data Seeding & Initialization — picture import path lives in the initializer.

### Depended Upon By

- Catalog Item Management — item views render these image URLs.

## Risks

- **Medium** — statefulness: local-disk dependency blocks horizontal scaling/containers. Mitigation: object storage as above.
- **Low** — destructive `~/Pics` wipe on seed could delete operator-added images. Mitigation: idempotent upload, no delete.

## Priority

- **Business Value**: Medium
- **Usage Frequency**: High (every catalog page renders images)
- **Migration Complexity**: M
- **Recommended Wave**: 3
