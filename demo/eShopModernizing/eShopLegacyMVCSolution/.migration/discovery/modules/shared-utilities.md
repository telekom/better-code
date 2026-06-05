# Shared Utilities (eShopLegacy.Utilities)

## Purpose

A tiny shared class library referenced by the web project. It provides binary
serialization helpers used by `FilesController` to stream a brand list to clients.

## Source Files

| File | Language | Lines | Role |
| ---- | -------- | ----- | ---- |
| `eShopLegacy.Utilities/Serializing.cs` | C# | 24 | primary — BinaryFormatter wrapper |
| `eShopLegacy.Utilities/Properties/AssemblyInfo.cs` | C# | ~30 | config — assembly metadata |

## Data Structures

- `Serializing` — `SerializeBinary(object) : Stream` and `DeserializeBinary(Stream) : object`, both using `System.Runtime.Serialization.Formatters.Binary.BinaryFormatter` (`eShopLegacy.Utilities/Serializing.cs:5-23`).

## Data Flow

### Inbound

- `FilesController.Get` passes a `List<BrandDTO>` to `SerializeBinary` (`src/eShopLegacyMVC/Controllers/WebApi/FilesController.cs:29-33`).

### Outbound

- Returns a `MemoryStream` consumed as `StreamContent` in the HTTP response.

## Business Rules

| # | Rule | Source Location | Confidence |
| --- | ---- | --------------- | ---------- |
| 1 | Serialize resets stream to position 0 before returning | `eShopLegacy.Utilities/Serializing.cs:10-12` | clear |
| 2 | Deserialize seeks to 0 before reading | `eShopLegacy.Utilities/Serializing.cs:18-20` | clear |

## Dependencies

### Called by (upstream)

- `FilesController` (web-controllers).

### Calls (downstream)

- `System.Runtime.Serialization.Formatters.Binary.BinaryFormatter` (BCL).

## External Interfaces

None directly (in-process helper).

## Complexity Assessment

**Rating**: Simple

**Justification**: 24 LOC, no branching. However it is a **high-risk migration item**:
`BinaryFormatter` is obsolete and removed/blocked in modern .NET (.NET 5+) due to
insecure-deserialization vulnerabilities. The `api/Files` contract must be redesigned
(e.g., JSON) during modernization.

## Unknowns

- No known consumer deserializes the `api/Files` payload within this solution — the wire contract's external clients are unknown. See unknowns.md.
