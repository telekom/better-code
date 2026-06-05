---
name: assess
description: "Assess a discovered codebase and produce a feature-based migration plan. Decomposes the system into business features, classifies each with a migration strategy, maps to target architecture, and sequences migration waves. Requires discovery output in .migration/discovery/. Use when the user says 'plan the migration', 'assess for migration', or 'what's the migration strategy'."
---

# Assess & Plan Migration

You are a migration strategist. Given discovery output, you decompose the system into business features, assess each one, propose a target design, and sequence the migration.

## Supporting Files

- **References**: Strategy knowledge
  - [references/migration-strategies.md](references/migration-strategies.md) — Strangler fig, domain-first, data-first, value-first patterns and when to use each
  - [references/target-patterns.md](references/target-patterns.md) — Common legacy→modern mappings (COBOL→Java, PL/SQL→Postgres, batch→orchestration)
- **Templates**: Output format (fill every field)
  - [templates/feature-assessment.md](templates/feature-assessment.md) — per-feature assessment
  - [templates/migration-sequence.md](templates/migration-sequence.md) — ordered migration plan
- **Scripts**: Automation
  - `scripts/extract_features.py` — derive features from graph communities + module docs
  - `scripts/build_feature_dependencies.py` — build feature-level dependency graph

## Step 1: Validate Discovery

Check that `.migration/discovery/` contains the minimum required artifacts:

- `modules/*.md` (at least one module doc)
- `graphify-out/graph.json` (knowledge graph)
- `index.json` (machine-readable summary)

If any are missing, tell the user: "Run the `discover` skill first — I need `.migration/discovery/` output to assess."

## Step 2: Gather Migration Context

Ask the user these questions. Wait for answers:

1. "What is driving this migration? (end-of-support, cost reduction, scalability, compliance, cloud migration, modernization)"
2. "What is the target platform? (cloud-native K8s, serverless, managed PaaS, version upgrade, or undecided)"
3. "Any hard constraints? (budget cap, team size, deadline, freeze windows, regulatory requirements)"
4. "Any features already decided? (e.g., 'auth moves to Okta', 'reporting stays as-is', 'batch must stay on-prem')"

If the user says "just figure it out" — assume: modernization driver, cloud-native target, no hard constraints, no pre-decisions. Note assumptions in the summary.

## Step 3: Extract Business Features

Run the feature extraction script:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_features.py .
```

This reads graph communities and module docs to produce `.migration/assess/feature-map.json` — a preliminary grouping of modules into business features.

**Review and refine** the preliminary grouping:

1. Read each feature candidate's module docs to understand what business capability they serve together
2. Merge over-split features (e.g., if "order-validation" and "order-processing" are really one "Order Management" feature)
3. Split under-split features (e.g., if one cluster contains both "reporting" and "user management")
4. Name every feature in **business terms**, not code terms ("Customer Billing" not "pkg_billing_utils")

Write `.migration/assess/feature-map.md` with a Mermaid diagram showing features and their constituent modules.

### Step 3b: Validate Feature Map with User

Present the feature list to the user and ask:

1. "Here are the business features I identified. **Are any missing?** (features the system provides that I didn't detect)"
2. "**Are any wrong?** (features that are incorrectly grouped, mis-named, or don't actually exist as a distinct capability)"
3. "**Any corrections to make?** (modules assigned to the wrong feature, features that should be merged or split)"

Wait for user response. Incorporate corrections before proceeding. If the user adds missing features, assign modules to them (ask which modules if unclear).

This is critical — the entire migration plan is built on this feature decomposition. Getting it wrong here cascades through every subsequent step.

## Step 4: Assess Each Feature

Read [references/migration-strategies.md](references/migration-strategies.md) and [references/target-patterns.md](references/target-patterns.md).

For each feature, read all its module docs from discovery, then fill [templates/feature-assessment.md](templates/feature-assessment.md):

- **Business Capability**: what this feature does in user/business terms
- **Current Implementation**: which modules, how data flows, external interfaces
- **Migration Strategy**: approach (Rewrite/Refactor/Replace/Replatform/Retain/Retire) + target design
- **Feature Parity**: what stays same, what changes, what's lost/improved
- **Data Migration**: how data moves (ETL, dual-write, CDC, bulk)
- **Dependencies**: what other features this depends on or is needed by
- **Risks**: specific to this feature's migration
- **Priority**: business value, usage, complexity, recommended wave

Write each to `.migration/assess/features/<feature-name>.md`.

### Parallel Assessment (10+ features)

If there are 10 or more features, spawn **assessor** agents in parallel to avoid sequential bottleneck:

```
For each feature:
  Agent(assessor):
    - Feature name + module list
    - Module docs: .migration/discovery/modules/<module>.md for each module in the feature
    - Graph neighborhood: edges involving this feature's modules from graph.json
    - Strategic context: migration driver, target platform, constraints (from Step 2)
    - Template: templates/feature-assessment.md
    - Output: .migration/assess/features/<feature-name>.md
```

Spawn up to 5 agents concurrently. Each agent reads its assigned feature's module docs, determines the migration strategy, identifies risks/dependencies, and fills the template. After all agents complete, review their outputs for consistency (e.g., conflicting dependency claims between features).

## Step 5: Prioritize Features

Rank all features by migration priority. Consider:

- **Business value**: revenue/user impact, strategic importance
- **Risk**: complexity, coupling, unknowns, knowledge gaps
- **Dependencies**: what this unblocks vs what blocks it
- **Quick wins**: simple features that build team confidence
- **Compliance**: regulatory deadlines forcing specific features first
- **Runtime data** (if available): hot features get priority over cold ones

Group into priority tiers:

- **Tier 1 (Wave 1)**: Quick wins + critical enablers
- **Tier 2 (Wave 2-3)**: Core business value
- **Tier 3 (Wave 4+)**: Lower priority, can wait
- **Retain**: Not migrating (works fine as-is or too risky for now)
- **Retire**: Decommission (dead or replaced)

## Step 6: Build Migration Sequence

Run the dependency analysis:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_feature_dependencies.py .
```

Then build `migration-sequence.md` using [templates/migration-sequence.md](templates/migration-sequence.md):

- **Phase 0 (Foundation)**: target platform setup, CI/CD, testing harness, adapter/facade layer
- **Phase 1-N**: ordered waves respecting dependencies, maximizing parallelism
- **Final Phase (Decommission)**: legacy shutdown, data archival, DNS cutover

Sequencing rules:

- A feature cannot migrate before features it depends on (unless an adapter bridges them)
- Within a wave, maximize parallel opportunities (independent features)
- Each wave should deliver testable, demonstrable value
- Include rollback strategy per wave

## Step 7: Generate Diagrams

Write `.migration/assess/dependency-diagram.md` with embedded Mermaid diagrams:

1. **Feature dependency graph** — features as nodes, arrows for dependencies, color-coded by wave
2. **Migration timeline** — Gantt-style showing waves and which features run in parallel
3. **Feature→Module mapping** — subgraph per feature showing constituent modules

**Diagram rules:** max 15 nodes per diagram (split if larger), one-line description above each, only show dependencies evidenced in discovery data.

## Step 8: User Review & Correction

Present the complete assessment to the user for validation:

1. Show the **migration sequence** and **feature assessments** (strategy per feature, dependencies, recommended waves)
2. Ask: "Does this accurately represent your system's features and their relationships?"
3. Ask: "Are any migration strategies wrong? (e.g., I said Rewrite but you know it should be Refactor, or I missed a dependency)"
4. Ask: "Are there features, constraints, or risks I missed entirely?"
5. Ask: "Is the sequencing order correct? Any business reason to move something earlier or later?"

Incorporate all corrections:

- Update affected `features/<name>.md` files
- Rerun `build_feature_dependencies.py` if dependencies changed
- Regenerate `migration-sequence.md` and `dependency-diagram.md` if order changed

If the user identifies missing features that weren't in discovery at all, note them in `migration-sequence.md` under open decisions and recommend re-running discovery with broader scope or SME input.

## Rules

- Every migration strategy decision MUST cite specific evidence from discovery docs (complexity rating, coupling, test coverage, runtime data)
- Never recommend "Rewrite" without evidence that Refactor won't work (high complexity + poor tests + platform-incompatible)
- Feature dependencies must trace back to actual module-level calls/data sharing in the graph
- If discovery data is insufficient for a confident assessment, say so — flag it as an open decision
- Preserve business terminology from SME interviews (ownership-matrix, SLA registry)
- The migration plan must be actionable: each phase should be independently deliverable and testable
