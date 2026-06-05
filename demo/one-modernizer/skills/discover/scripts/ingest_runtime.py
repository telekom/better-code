#!/usr/bin/env python3
"""Ingest operational/runtime data and normalize into activity scores.

Usage: python3 ingest_runtime.py [project-root] --file <path> --type <apm|awr|coverage|log_frequency>

Input formats:
- apm: CSV with columns (endpoint, hit_count, avg_response_ms, p99_ms, error_rate)
- awr: CSV with columns (sql_id, executions, elapsed_time_ms, buffer_gets, table_name)
- coverage: CSV with columns (file, lines_total, lines_covered, branch_total, branch_covered)
- log_frequency: CSV with columns (program_name, daily_executions, last_execution_date)

Output: .migration/runtime/usage-profile.json
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime


def load_csv(file_path: Path) -> list[dict]:
    content = file_path.read_text(encoding="utf-8", errors="replace")
    reader = csv.DictReader(content.splitlines())
    return [row for row in reader]


def process_apm(rows: list[dict]) -> dict:
    """Process APM/endpoint data."""
    endpoints = []
    for row in rows:
        endpoints.append(
            {
                "endpoint": row.get("endpoint", ""),
                "hit_count": int(row.get("hit_count", 0) or 0),
                "avg_response_ms": float(row.get("avg_response_ms", 0) or 0),
                "p99_ms": float(row.get("p99_ms", 0) or 0),
                "error_rate": float(row.get("error_rate", 0) or 0),
            }
        )
    endpoints.sort(key=lambda x: -x["hit_count"])
    total_hits = sum(e["hit_count"] for e in endpoints)
    return {
        "type": "apm",
        "total_endpoints": len(endpoints),
        "total_hits": total_hits,
        "endpoints": endpoints,
        "hot_paths": [e["endpoint"] for e in endpoints[:20]],
    }


def process_awr(rows: list[dict]) -> dict:
    """Process Oracle AWR/ASH data."""
    statements = []
    table_activity = {}
    for row in rows:
        stmt = {
            "sql_id": row.get("sql_id", ""),
            "executions": int(row.get("executions", 0) or 0),
            "elapsed_time_ms": float(row.get("elapsed_time_ms", 0) or 0),
            "buffer_gets": int(row.get("buffer_gets", 0) or 0),
        }
        statements.append(stmt)
        table = row.get("table_name", "")
        if table:
            table_activity.setdefault(table, {"executions": 0, "total_elapsed_ms": 0})
            table_activity[table]["executions"] += stmt["executions"]
            table_activity[table]["total_elapsed_ms"] += stmt["elapsed_time_ms"]

    statements.sort(key=lambda x: -x["elapsed_time_ms"])
    return {
        "type": "awr",
        "total_statements": len(statements),
        "top_by_elapsed": statements[:20],
        "table_activity": dict(
            sorted(table_activity.items(), key=lambda x: -x[1]["executions"])
        ),
    }


def process_coverage(rows: list[dict]) -> dict:
    """Process code coverage data."""
    files = []
    total_lines = 0
    covered_lines = 0
    for row in rows:
        lt = int(row.get("lines_total", 0) or 0)
        lc = int(row.get("lines_covered", 0) or 0)
        total_lines += lt
        covered_lines += lc
        files.append(
            {
                "file": row.get("file", ""),
                "lines_total": lt,
                "lines_covered": lc,
                "line_coverage_pct": round(lc / lt * 100, 1) if lt else 0,
            }
        )
    files.sort(key=lambda x: x["line_coverage_pct"])
    return {
        "type": "coverage",
        "total_files": len(files),
        "total_lines": total_lines,
        "covered_lines": covered_lines,
        "overall_coverage_pct": round(covered_lines / total_lines * 100, 1)
        if total_lines
        else 0,
        "zero_coverage_files": [
            f["file"] for f in files if f["line_coverage_pct"] == 0
        ],
        "files": files,
    }


def process_log_frequency(rows: list[dict]) -> dict:
    """Process program execution frequency from logs."""
    programs = []
    for row in rows:
        programs.append(
            {
                "program": row.get("program_name", ""),
                "daily_executions": int(row.get("daily_executions", 0) or 0),
                "last_execution": row.get("last_execution_date", ""),
            }
        )
    programs.sort(key=lambda x: -x["daily_executions"])

    # Flag potentially dead programs (no execution in 90+ days)
    today = datetime.now()
    dead_candidates = []
    for p in programs:
        if p["last_execution"]:
            try:
                last = datetime.strptime(p["last_execution"], "%Y-%m-%d")
                if (today - last).days > 90:
                    dead_candidates.append(p["program"])
            except ValueError:
                pass
        elif p["daily_executions"] == 0:
            dead_candidates.append(p["program"])

    return {
        "type": "log_frequency",
        "total_programs": len(programs),
        "active_programs": sum(1 for p in programs if p["daily_executions"] > 0),
        "hot_programs": [p["program"] for p in programs[:20]],
        "dead_candidates": dead_candidates,
        "programs": programs,
    }


PROCESSORS = {
    "apm": process_apm,
    "awr": process_awr,
    "coverage": process_coverage,
    "log_frequency": process_log_frequency,
}


def main():
    if "--file" not in sys.argv or "--type" not in sys.argv:
        print(
            "Usage: python3 ingest_runtime.py [root] --file <path> --type <apm|awr|coverage|log_frequency>"
        )
        sys.exit(1)

    root_arg = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "--file" else "."
    root = Path(root_arg).resolve()

    file_idx = sys.argv.index("--file")
    input_path = Path(sys.argv[file_idx + 1]).resolve()

    type_idx = sys.argv.index("--type")
    data_type = sys.argv[type_idx + 1].lower()

    if data_type not in PROCESSORS:
        print(
            f"ERROR: Unknown type '{data_type}'. Supported: {list(PROCESSORS.keys())}"
        )
        sys.exit(1)

    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    print(f"Processing {data_type} from {input_path.name}...", file=sys.stderr)
    rows = load_csv(input_path)
    print(f"  Loaded {len(rows)} rows", file=sys.stderr)

    result = PROCESSORS[data_type](rows)

    # Save to .migration/runtime/
    out_dir = root / ".migration" / "discovery" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Merge into usage profile
    profile_path = out_dir / "usage-profile.json"
    profile = {}
    if profile_path.exists():
        profile = json.loads(profile_path.read_text(encoding="utf-8"))

    profile[data_type] = result
    profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

    print("\n# Runtime Data Ingestion")
    print("")
    print(f"**Type**: {data_type}")
    print(f"**Rows**: {len(rows)}")
    if data_type == "apm":
        print(f"**Total hits**: {result['total_hits']:,}")
        print(f"**Hot paths**: {len(result['hot_paths'])}")
    elif data_type == "awr":
        print(f"**Tables with activity**: {len(result['table_activity'])}")
    elif data_type == "coverage":
        print(f"**Overall coverage**: {result['overall_coverage_pct']}%")
        print(f"**Zero-coverage files**: {len(result['zero_coverage_files'])}")
    elif data_type == "log_frequency":
        print(
            f"**Active programs**: {result['active_programs']}/{result['total_programs']}"
        )
        print(f"**Dead candidates**: {len(result['dead_candidates'])}")
    print(f"\nOutput: {profile_path}")


if __name__ == "__main__":
    main()
