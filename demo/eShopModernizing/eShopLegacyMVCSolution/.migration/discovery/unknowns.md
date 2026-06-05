# Unknowns & Clarifications Needed

> Discovery ran in "just figure it out" mode — no interactive SME clarification.
> Ambiguities are recorded here with confidence levels for follow-up.

## Ambiguous Logic

| # | Location | Code | Question | Status |
| --- | -------- | ---- | -------- | ------ |
| 1 | `Controllers/Api/CatalogController.cs:6-12` | `CatalogController2.Index` returns `{Message="Hello World!"}` | Is this a live endpoint or scaffolding to delete? | open |
| 2 | `Services/CatalogServiceMock.cs:73-82` | `ComposeCatalogItems` mutates items from static `PreconfiguredData` lists | Intended shared mutation, or latent cross-request bug in mock mode? | open |
| 3 | `Models/Infrastructure/CatalogDBInitializer.cs:339-354` | `AddCatalogItemPictures` deletes all `~/Pics` files then unzips | Is destructive wipe acceptable on every customization seed? | open |
| 4 | `Controllers/WebApi/BrandsController.cs:48-49` | Delete is a no-op returning 200 | Should the real system actually delete, or is 200-without-effect the contract? | open |

## Undocumented Business Rules

| # | Location | Observed Behavior | Assumed Intent | Confidence |
| --- | -------- | ----------------- | -------------- | ---------- |
| 1 | `Models/CatalogItemHiLoGenerator.cs:11-33` | Hands out 10 ids per DB sequence fetch from a process singleton | Reduce DB round-trips for id allocation | medium |
| 2 | `Models/CatalogDBContext.cs:63-65` | `CatalogItem.Id` is app-assigned (`DatabaseGeneratedOption.None`) | Ids come from HiLo, not IDENTITY | high |
| 3 | `Models/CatalogItem.cs:22-25` | Price regex allows repeated decimal groups (`(\.\d{0,2})*`) | Likely intended single 2-dp decimal; regex is loose | medium |
| 4 | `Controllers/PicController.cs:38-44` | Reads `~/Pics/{PictureFileName}` with no existence check after item found | Assumes picture file always present on disk | medium |

## Dead Code Candidates

| # | Location | Reason | Safe to Remove? |
| --- | -------- | ------ | --------------- |
| 1 | `Controllers/Api/CatalogController.cs:1-14` (`CatalogController2`) | static stub, no apparent caller | needs-verification |
| 2 | `eShopLegacy.Utilities/Serializing.cs:14-21` (`DeserializeBinary`) | no in-solution caller found | needs-verification |

## Missing Context

| # | Reference | Where Found | What's Needed |
| --- | --------- | ----------- | ------------- |
| 1 | Production connection string | `Web.config:12`, `Web.Release.config` | actual prod DB target / secret source |
| 2 | `api/Files` binary consumers | `Controllers/WebApi/FilesController.cs:29-35` | who deserializes the BinaryFormatter payload externally |
| 3 | Relationship to `eShopPorted` | `eShopPorted/` project | is it the sanctioned target or a spike? |
| 4 | `Setup/CatalogItems.zip` contents/provenance | `Setup/` | source-of-truth for production pictures |

## Assumptions Made

| # | Assumption | Basis | Impact if Wrong |
| --- | ---------- | ----- | --------------- |
| 1 | `src/eShopLegacyMVC` is the migration source of record | scope selection + canonical sample layout | docs target wrong project |
| 2 | App is operator/admin-facing (no anonymous public catalog) | CRUD-only UI, no auth/cart code | security/sizing assumptions shift |
| 3 | Single-instance deployment assumed for HiLo singleton | in-process id cache | scale-out may need id-allocation rework |
| 4 | No automated tests exist | `test_inventory.py` found 0 | migration lacks regression safety net |
