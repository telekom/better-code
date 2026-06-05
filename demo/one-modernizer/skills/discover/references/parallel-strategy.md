# Parallel Discovery Strategy for Large Repos

## When to Use

Use parallel discovery when:

- Repo has > 100k LOC (check via `chunk_repo.py`)
- Graph report shows > 5 communities
- Single-pass analysis would exceed context limits

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: STRUCTURE SCAN (fast, broad, single agent)     │
│ • File tree analysis                                     │
│ • Project file parsing (.csproj, pom.xml, package.json) │
│ • Dependency graph from build system                     │
│ • graphify for AST-level knowledge graph                │
│ • Output: .migration/discovery/chunks.json + graph                │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 2: PARALLEL DEEP-DIVE (N agents, one per chunk)   │
│ • Each agent documents one module/chunk                  │
│ • Reads only its assigned files                          │
│ • Uses graph to understand cross-module boundaries       │
│ • Output: .migration/discovery/modules/<name>.md per agent        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 3: CROSS-REFERENCE & MERGE (single agent)         │
│ • Read all module docs                                   │
│ • Resolve cross-module dependency claims                 │
│ • Build the overview from module summaries               │
│ • Identify gaps between modules (orphan files)           │
│ • Output: .migration/discovery/overview.md, update module docs    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 4: VERIFY & FIX LOOP (until 95%+ accuracy)        │
│ • Run verify_coverage.py → fix gaps                      │
│ • Run accuracy_check.py → fix hallucinations             │
│ • Re-verify after each fix pass                          │
│ • Max 3 fix iterations before escalating to user         │
│ Output: final .migration/discovery/ with verified docs            │
└─────────────────────────────────────────────────────────┘
```

## Phase 1: Structure Scan

Goal: Understand the repo's shape without reading every source file.

1. Run `chunk_repo.py` → produces `.migration/discovery/chunks.json`
2. Run `graphify` → produces knowledge graph + report
3. Parse build system files to extract declared modules and dependencies:
   - .NET: `.sln` → project references → inter-project deps
   - Java: `pom.xml` / `build.gradle` → module declarations
   - Node: `package.json` workspaces → package boundaries
   - C/C++: CMakeLists.txt / Makefile → targets and includes
   - COBOL: JCL → job steps → program invocations
4. Merge build-system modules with graphify communities to create the **module map**

Output:

- `.migration/discovery/chunks.json` — file groupings with LOC estimates
- `.migration/discovery/module-map.json` — definitive list of modules to document

```json
{
  "modules": [
    {
      "name": "MessageService",
      "type": "web-api",
      "files": ["MessageService/**"],
      "loc": 1200,
      "dependencies": ["SharedModels"],
      "chunk_id": 0
    }
  ]
}
```

## Phase 2: Parallel Deep-Dive

Goal: Document each module independently with high accuracy.

For each module in `module-map.json`, spawn a documenter agent with:

- The module's file list (from chunk/module-map)
- The graph neighborhood (nodes connected to this module)
- The template to fill (`templates/module.md`)
- Cross-module interface hints (what other modules call this one)

Each agent:

1. Reads ALL source files in its module (not sampling — reading every file)
2. Identifies entry points, data structures, business rules
3. Fills in the module template with precise file:line references
4. Lists its external interfaces (what it imports/calls from other modules)

Accuracy rule: Each agent must cite `file:line` for every business rule claim. No claim without a source location.

Parallelism: Up to 5 agents concurrently. For a 20-module repo, that's 4 batches.

## Phase 3: Cross-Reference & Merge

Goal: Stitch parallel results into a coherent whole.

1. Read all `modules/*.md` produced in Phase 2
2. For each cross-module dependency claim (e.g., "ModuleA calls ModuleB.ProcessOrder"):
   - Verify ModuleB's doc confirms that interface exists
   - If not, read the actual source to confirm or reject
3. Build `.migration/discovery/overview.md`:
   - Aggregate module summaries
   - Draw dependency graph from confirmed cross-references
   - Identify entry points across the full system
   - List external interfaces (anything that crosses the system boundary)
4. Identify orphan files not claimed by any module
5. Create additional module docs for orphan clusters

## Phase 4: Verification Loop

Same as Step 7 in the parent SKILL.md — run `verify_coverage.py` + `accuracy_check.py`, fix gaps, repeat up to 3 times targeting 95%+ on both metrics.

## Accuracy Guarantees

What makes this strategy achieve 95%+:

1. **No sampling in Phase 2** — agents read every file in their module, not a random sample
2. **Citation requirement** — every claim must have a `file:line` reference
3. **Cross-validation in Phase 3** — dependency claims are verified bidirectionally
4. **Automated verification in Phase 4** — scripts catch hallucinations before delivery
5. **Fix loop** — don't declare done until scripts pass

## Token Budget Estimation

| Repo Size | Chunks | Parallel Agents | Estimated Total Tokens | Time (est.) |
| --------- | ------ | --------------- | ---------------------- | ----------- |
| 50k LOC   | 1      | 1-3             | ~500k                  | 2-5 min     |
| 200k LOC  | 4-5    | 5               | ~2M                    | 10-15 min   |
| 500k LOC  | 10-12  | 5 x 2-3 batches | ~5M                    | 25-40 min   |
| 2M LOC    | 40+    | 5 x 8+ batches  | ~15-20M                | 1-2 hours   |

For repos approaching 2M LOC, suggest the user run discovery in segments (e.g., one subsystem at a time) rather than all-at-once.
