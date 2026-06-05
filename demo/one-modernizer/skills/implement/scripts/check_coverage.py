#!/usr/bin/env python3
"""Check implementation coverage against spec.json.

Verifies that all spec items have corresponding generated code.

Usage: python3 check_coverage.py <implement-dir>
       e.g.: python3 check_coverage.py .migration/implement/order-management/

Reads: spec.json (from decompose), task-log.json (from implement)
Outputs: coverage-report.json
"""

import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_coverage.py <implement-dir>", file=sys.stderr)
        sys.exit(1)

    implement_dir = Path(sys.argv[1]).resolve()
    feature_name = implement_dir.name

    decompose_dir = implement_dir.parents[1] / "decompose" / feature_name
    spec = load_json(decompose_dir / "spec.json")
    if spec is None:
        print(
            f"ERROR: spec.json not found at {decompose_dir / 'spec.json'}",
            file=sys.stderr,
        )
        sys.exit(1)

    task_log = load_json(implement_dir / "task-log.json")
    tasks = load_json(implement_dir / "tasks.json")

    spec_rules = {r["id"] for r in spec.get("business_rules", [])}
    spec_flows = {f["id"] for f in spec.get("flows", [])}
    spec_tests = {t["id"] for t in spec.get("test_cases", [])}
    spec_data = {d["name"] for d in spec.get("data_model", [])}
    spec_errors = {e["id"] for e in spec.get("errors", [])}

    covered_refs = set()
    completed_tasks = 0
    failed_tasks = 0

    if task_log and "entries" in task_log:
        for entry in task_log["entries"]:
            if entry.get("status") == "completed":
                completed_tasks += 1
                for ref in entry.get("spec_refs", []):
                    covered_refs.add(ref)
            elif entry.get("status") == "failed":
                failed_tasks += 1
    elif tasks:
        for task in tasks.get("tasks", []):
            for ref in task.get("spec_refs", []):
                covered_refs.add(ref)
            completed_tasks += 1

    covered_rules = spec_rules & covered_refs
    covered_flows = spec_flows & covered_refs
    covered_tests = spec_tests & covered_refs
    covered_data = spec_data & covered_refs
    covered_errors = spec_errors & covered_refs

    def pct(covered, total):
        return round(len(covered) / max(len(total), 1) * 100, 1)

    report = {
        "feature": feature_name,
        "summary": {
            "total_tasks": tasks.get("total_tasks", 0) if tasks else 0,
            "completed": completed_tasks,
            "failed": failed_tasks,
        },
        "coverage": {
            "rules": {
                "covered": len(covered_rules),
                "total": len(spec_rules),
                "pct": pct(covered_rules, spec_rules),
            },
            "flows": {
                "covered": len(covered_flows),
                "total": len(spec_flows),
                "pct": pct(covered_flows, spec_flows),
            },
            "tests": {
                "covered": len(covered_tests),
                "total": len(spec_tests),
                "pct": pct(covered_tests, spec_tests),
            },
            "data": {
                "covered": len(covered_data),
                "total": len(spec_data),
                "pct": pct(covered_data, spec_data),
            },
            "errors": {
                "covered": len(covered_errors),
                "total": len(spec_errors),
                "pct": pct(covered_errors, spec_errors),
            },
        },
        "uncovered": {
            "rules": sorted(spec_rules - covered_refs),
            "flows": sorted(spec_flows - covered_refs),
            "tests": sorted(spec_tests - covered_refs),
            "data": sorted(spec_data - covered_refs),
            "errors": sorted(spec_errors - covered_refs),
        },
    }

    out_path = implement_dir / "coverage-report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n# Implementation Coverage: {feature_name}")
    print("")
    print("## Summary")
    print(f"  Tasks: {completed_tasks} completed, {failed_tasks} failed")
    print("")
    print("## Coverage")
    for category, data in report["coverage"].items():
        bar = "█" * int(data["pct"] / 5) + "░" * (20 - int(data["pct"] / 5))
        print(
            f"  {category:8s}: {bar} {data['pct']}% ({data['covered']}/{data['total']})"
        )
    print()

    total_uncovered = sum(len(v) for v in report["uncovered"].values())
    if total_uncovered > 0:
        print(f"## Uncovered Items ({total_uncovered})")
        for category, items in report["uncovered"].items():
            if items:
                print(f"  {category}: {', '.join(items[:10])}")
                if len(items) > 10:
                    print(f"    ... and {len(items) - 10} more")
    else:
        print("## Coverage: 100% ✓")

    print(f"\nOutput: {out_path}")

    all_pcts = [d["pct"] for d in report["coverage"].values()]
    avg_coverage = sum(all_pcts) / len(all_pcts) if all_pcts else 0
    if avg_coverage < 100:
        sys.exit(1)


if __name__ == "__main__":
    main()
