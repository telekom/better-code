#!/usr/bin/env python3
"""Cross-reference runtime data with static graph to identify dead code.

Usage: python3 dead_code_analysis.py [project-root]

Input:
- .migration/discovery/runtime/usage-profile.json (from ingest_runtime.py)
- .migration/discovery/graphify-out/graph.json (from graphify)

Output: .migration/runtime/dead-code-candidates.md
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


def load_runtime_programs(profile: dict) -> dict[str, dict]:
    """Extract program activity from runtime profile."""
    programs = {}

    # From log_frequency
    log_data = profile.get("log_frequency", {})
    for p in log_data.get("programs", []):
        name = p["program"].upper()
        programs[name] = {
            "daily_executions": p["daily_executions"],
            "last_execution": p.get("last_execution", ""),
            "source": "log_frequency",
        }

    # From APM
    apm_data = profile.get("apm", {})
    for e in apm_data.get("endpoints", []):
        name = e["endpoint"].upper()
        programs[name] = {
            "daily_executions": e["hit_count"],
            "last_execution": "",
            "source": "apm",
        }

    return programs


def load_graph_programs(graph: dict) -> dict[str, dict]:
    """Extract program/module nodes from the knowledge graph."""
    nodes = graph.get("nodes", [])
    edges = graph.get("links", graph.get("edges", []))

    # Build inbound edge count per node
    inbound = defaultdict(int)
    for edge in edges:
        target = edge.get("target", "")
        if edge.get("relation") in ("call", "executes", "calls_proc"):
            inbound[target] += 1

    programs = {}
    for node in nodes:
        nid = node.get("id", "")
        label = node.get("label", "")
        source_file = node.get("source_file", "")
        if source_file and not label.startswith(("CICS:", "DBMS_", "UTL_")):
            programs[label.upper()] = {
                "node_id": nid,
                "label": label,
                "source_file": source_file,
                "inbound_calls": inbound.get(nid, 0),
            }

    return programs


def classify_dead_code(graph_programs: dict, runtime_programs: dict) -> dict:
    """Classify each program into liveness categories."""
    confirmed_dead = []
    likely_dead = []
    uncertain = []
    active = []

    for name, info in graph_programs.items():
        runtime = runtime_programs.get(name)
        has_runtime = runtime is not None and runtime["daily_executions"] > 0
        has_callers = info["inbound_calls"] > 0

        if has_runtime:
            active.append({**info, "daily_executions": runtime["daily_executions"]})
        elif not has_callers:
            confirmed_dead.append(info)
        elif not has_runtime and has_callers:
            # Has static callers but no runtime evidence — maybe the callers are also dead
            likely_dead.append(info)
        else:
            uncertain.append(info)

    return {
        "confirmed_dead": sorted(confirmed_dead, key=lambda x: x["label"]),
        "likely_dead": sorted(likely_dead, key=lambda x: x["label"]),
        "uncertain": sorted(uncertain, key=lambda x: x["label"]),
        "active": sorted(active, key=lambda x: -x["daily_executions"]),
    }


def generate_report(
    classification: dict, graph_programs: dict, runtime_programs: dict
) -> str:
    """Generate markdown report."""
    lines = ["# Dead Code Analysis\n"]

    total = len(graph_programs)
    confirmed = len(classification["confirmed_dead"])
    likely = len(classification["likely_dead"])
    active = len(classification["active"])

    lines.append("## Summary\n")
    lines.append("| Category | Count | % of Total |")
    lines.append("| -------- | ----- | ---------- |")
    lines.append(
        f"| Active (confirmed runtime) | {active} | {active * 100 // total if total else 0}% |"
    )
    lines.append(
        f"| Confirmed dead (no runtime, no callers) | {confirmed} | {confirmed * 100 // total if total else 0}% |"
    )
    lines.append(
        f"| Likely dead (no runtime, has static callers) | {likely} | {likely * 100 // total if total else 0}% |"
    )
    lines.append(
        f"| Uncertain | {len(classification['uncertain'])} | {len(classification['uncertain']) * 100 // total if total else 0}% |"
    )
    lines.append("")

    if classification["confirmed_dead"]:
        lines.append("## Confirmed Dead Code\n")
        lines.append("No runtime activity AND no inbound call edges in the graph.\n")
        lines.append("| Program | Source File |")
        lines.append("| ------- | ----------- |")
        for item in classification["confirmed_dead"][:50]:
            lines.append(f"| {item['label']} | `{item['source_file']}` |")
        if len(classification["confirmed_dead"]) > 50:
            lines.append(
                f"\n... and {len(classification['confirmed_dead']) - 50} more\n"
            )
        lines.append("")

    if classification["likely_dead"]:
        lines.append("## Likely Dead Code\n")
        lines.append(
            "No runtime activity but has static call references (callers may also be dead).\n"
        )
        lines.append("| Program | Source File | Static Callers |")
        lines.append("| ------- | ----------- | -------------- |")
        for item in classification["likely_dead"][:30]:
            lines.append(
                f"| {item['label']} | `{item['source_file']}` | {item['inbound_calls']} |"
            )
        lines.append("")

    if classification["active"]:
        lines.append("## Most Active (Top 20)\n")
        lines.append("| Program | Daily Executions | Source File |")
        lines.append("| ------- | ---------------- | ----------- |")
        for item in classification["active"][:20]:
            lines.append(
                f"| {item['label']} | {item['daily_executions']:,} | `{item['source_file']}` |"
            )
        lines.append("")

    lines.append("## Recommendation\n")
    lines.append(
        f"- **Retire**: {confirmed} confirmed dead programs can likely be excluded from migration"
    )
    lines.append(
        f"- **Verify**: {likely} likely-dead programs need manual confirmation before exclusion"
    )
    lines.append(
        f"- **Prioritize**: Top {min(20, active)} active programs should be migrated first"
    )
    lines.append("")

    return "\n".join(lines)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    profile_path = root / ".migration" / "discovery" / "runtime" / "usage-profile.json"
    graph_path = root / ".migration" / "discovery" / "graphify-out" / "graph.json"

    if not profile_path.exists():
        print(
            "ERROR: .migration/runtime/usage-profile.json not found. Run ingest_runtime.py first."
        )
        sys.exit(1)

    if not graph_path.exists():
        print(
            "ERROR: .migration/discovery/graphify-out/graph.json not found. Run graphify extract first."
        )
        sys.exit(1)

    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    graph = json.loads(graph_path.read_text(encoding="utf-8"))

    runtime_programs = load_runtime_programs(profile)
    graph_programs = load_graph_programs(graph)

    print(f"Runtime programs: {len(runtime_programs)}", file=sys.stderr)
    print(f"Graph programs: {len(graph_programs)}", file=sys.stderr)

    classification = classify_dead_code(graph_programs, runtime_programs)
    report = generate_report(classification, graph_programs, runtime_programs)

    out_path = root / ".migration" / "discovery" / "runtime" / "dead-code-candidates.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
