# one-modernizer

A Claude Code plugin for **legacy code modernization** — discover, document, and
migrate any codebase through a structured, evidence-driven pipeline.

Each stage is a [Skill](https://docs.claude.com/en/docs/claude-code/skills) that
consumes the previous stage's output, so the work compounds instead of restarting:

```
discover → assess → decompose → architect → implement → validate
```

| Stage | What it produces |
|-------|------------------|
| **discover** | Knowledge graph + per-module docs with `file:line` citations in `.migration/discovery/` |
| **assess** | Feature inventory, migration strategy, risk and dependency map |
| **decompose** | Per-feature specs (business rules, data model, flows) |
| **architect** | Target architecture: services, layers, ADRs, blueprints |
| **implement** | Generated code against the spec, verified file-by-file |
| **validate** | Build/contract/quality gates on the migrated output |

## How it works

- **Skills** drive each pipeline stage (`skills/<stage>/SKILL.md`).
- **Agents** (`agents/`) are spawned in parallel for scale — one `documenter` per
  module, one `assessor` per feature, etc.
- **Hooks** (`hooks/`) keep pipeline state coherent: they install the engine on
  session start, nudge you toward the knowledge graph, and checkpoint progress.
- The **knowledge-graph engine** is [`graphifyy`](https://github.com/safishamsi/graphify),
  installed from PyPI (not vendored). It turns a folder of code into a queryable
  graph the skills read from. See [Attribution](#attribution).

## Quickstart

1. Install the plugin in Claude Code (add this repo as a plugin source).
2. On first use, run the setup skill — it creates a venv and installs the engine:

   ```
   /setup
   ```

   This installs `graphifyy` from PyPI and exposes it as the `one-modernizer` CLI
   inside the plugin venv. Requires **Python 3.10+**.
3. Start a migration by invoking the first stage:

   ```
   /discover
   ```

   Then follow the pipeline through to `validate`.

The engine version is pinned in `hooks/scripts/setup.py`
(`GRAPHIFYY_VERSION`); bump it there after testing a newer release.

## Repository layout

```
.claude-plugin/   plugin manifest
agents/           parallel sub-agents (documenter, assessor, decomposer, …)
hooks/            session + pipeline hooks and their tests
output-styles/    goal-driven output style
skills/           the six pipeline stages
```

## Requirements

- Claude Code (plugin host)
- Python 3.10+
- Network access to PyPI for the `graphifyy` engine
- Optional: an LLM API key for graph enrichment (AST extraction works without one)

## Attribution

The knowledge-graph engine is **graphifyy** by Safi Shamsi, MIT-licensed and
installed as a dependency from PyPI. It is not bundled in this repository.
See <https://github.com/safishamsi/graphify> and `NOTICE` for details.
