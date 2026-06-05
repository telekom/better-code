# Conference Demo — Modernizing eShop with one-modernizer

A self-contained demo bundle: the **one-modernizer** Claude Code plugin plus a
real legacy .NET app to migrate (**eShopModernizing**). Everything needed to run
the pipeline live is in this folder.

```
demo/
├── one-modernizer/    the plugin (discover → assess → decompose → architect → implement → validate)
└── eShopModernizing/  the migration target (Microsoft sample, .git stripped)
```

## The story (what we show)

The legacy app is a backoffice **Product Catalog** CRUD built on ASP.NET MVC
(.NET Framework) over SQL Server. We don't migrate the whole thing live — we pick
**one cohesive feature** and take it end-to-end through the pipeline, producing
real artifacts at each gate.

**Recommended feature to abstract: Catalog Item Management.** It's a clean
vertical slice in `eShopLegacyMVCSolution/src/eShopLegacyMVC`:

| Layer | Files |
|-------|-------|
| Controller | `Controllers/CatalogController.cs`, `Controllers/Api/CatalogController.cs` |
| Service | `Services/CatalogService.cs`, `Services/ICatalogService.cs` |
| Domain | `Models/CatalogItem.cs`, `CatalogBrand.cs`, `CatalogType.cs` |
| Data | `Models/CatalogDBContext.cs`, `Infrastructure/CatalogDBInitializer.cs` |

Small enough to finish in a session, real enough to be convincing.

## Prerequisites

- **Claude Code** (the plugin host)
- **Python 3.10+** (the plugin creates a venv and installs the `graphifyy` engine from PyPI)
- Network access to PyPI
- *Optional:* an LLM API key (`ANTHROPIC_API_KEY`) for graph enrichment — AST
  extraction works without one, so the demo runs offline-ish if needed.

## Run order

> Each step is a plugin skill invoked in Claude Code from inside the
> `eShopModernizing/` directory. Each consumes the previous step's output in
> `.migration/`.

1. **Install the plugin.** Point Claude Code at `demo/one-modernizer` as a plugin
   source (or copy it into your plugins dir).

2. **`/setup`** — creates the venv, installs `graphifyy`, exposes the
   `one-modernizer` CLI. Confirm it reports *ready*.

3. **`/discover`** — scan the legacy MVC app, build the knowledge graph, produce
   `.migration/discovery/` (module docs with `file:line` citations, overview,
   architecture diagrams). *Talking point: context — the graph is the "why".*

4. **`/assess`** — feature inventory + migration strategy + risk/dependency map.
   This is where the **Catalog** feature is selected as the migration unit.
   *Talking point: routing decision + risk, no fake precision.*

5. **`/decompose`** — extract business rules, data model, and flows for the
   Catalog feature into a spec. *Talking point: the spec is the contract.*

6. **`/architect`** — design the target (service layers, ADRs, blueprint/mapping).
   *Talking point: pattern choice — service vs skill vs subagent.*

7. **`/implement`** — generate the modern .NET code one file at a time, verified
   against the spec (see `one-modernizer/skills/implement/references/code-patterns/dotnet.md`).
   *Talking point: artifact-first output, traceability.*

8. **`/validate`** — run build / contract / quality gates and the review gate.
   *Talking point: deterministic testing + LLM-as-judge.*

All pipeline output lands under `eShopModernizing/.migration/` and is safe to
delete between dry-runs.

## Resetting between runs

```bash
rm -rf eShopModernizing/.migration
```

## Notes

- `eShopModernizing/` is a copy of the Microsoft sample with its `.git/` removed,
  so it won't fight your outer repo. Its own `LICENSE` is preserved.
- The engine version is pinned in `one-modernizer/hooks/scripts/setup.py`
  (`GRAPHIFYY_VERSION`). Bump after testing a newer release.
- This plugin is .NET-focused by design for this demo; the discovery engine still
  handles many languages, but the implement-stage code patterns ship only `dotnet.md`.
