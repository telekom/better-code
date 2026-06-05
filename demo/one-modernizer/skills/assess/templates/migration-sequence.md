# Migration Sequence

## Overall Strategy: {{Strangler Fig / Domain-First / Data-First / Value-First / Hybrid}}

{{Why this strategy fits this system — 2-3 sentences citing system characteristics}}

## Phase 0: Foundation

{{Shared infrastructure, target platform setup, CI/CD pipeline, testing harness, adapter/facade layer}}

- [ ] {{prerequisite task}}
- [ ] {{prerequisite task}}

## Phase 1: {{Wave Name}} — Quick Wins

| Feature  | Strategy | Complexity   | Why Now           |
| -------- | -------- | ------------ | ----------------- |
| {{name}} | {{R}}    | {{S/M/L/XL}} | {{justification}} |

**Unblocks**: {{what becomes possible after this phase completes}}
**Parallel**: {{features within this phase that can migrate concurrently}}
**Duration signal**: {{short / medium / long}}
**Rollback**: {{how to revert if this phase fails}}

## Phase 2: {{Wave Name}} — Core Value

| Feature  | Strategy | Complexity   | Why Now           |
| -------- | -------- | ------------ | ----------------- |
| {{name}} | {{R}}    | {{S/M/L/XL}} | {{justification}} |

**Unblocks**: {{what becomes possible}}
**Parallel**: {{concurrent opportunities}}
**Duration signal**: {{short / medium / long}}
**Rollback**: {{revert strategy}}

## Phase N: Decommission

- Legacy shutdown sequence
- Data archival plan (what to keep, retention period, format)
- DNS/routing cutover
- Rollback window definition (point of no return)
- Monitoring: confirm no traffic to legacy for N days before final shutdown
