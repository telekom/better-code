#!/usr/bin/env python3
"""Verify that .migration/ docs cover all source files in the repo.

Usage: python3 verify_coverage.py [project-root]

Outputs a coverage report showing:
- Which source files are referenced in module docs
- Which source files are NOT referenced (gaps)
- Coverage percentage per directory
- Suggested modules that may be missing documentation
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from _constants import IGNORE_DIRS, SOURCE_EXTENSIONS

CONFIG_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".conf",
    ".config",
    ".csproj",
    ".sln",
    ".pom",
    ".gradle",
}


def find_source_files(root: Path) -> list[Path]:
    files = []
    for f in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if f.is_file() and f.suffix.lower() in SOURCE_EXTENSIONS:
            files.append(f.relative_to(root))
    return sorted(files)


def find_referenced_files(migration_dir: Path) -> set[str]:
    referenced = set()
    if not migration_dir.exists():
        return referenced
    for doc in migration_dir.rglob("*.md"):
        content = doc.read_text(encoding="utf-8", errors="ignore")
        # Match file paths in various formats
        # e.g., `src/main.cs`, src/main.cs, "src/main.cs"
        patterns = [
            r"`([^`]+\.\w+)`",
            r"\| *([^\|]+\.\w+) *\|",
            r"(?:^|\s)([\w/\\.-]+\.\w+)(?:\s|$|:)",
        ]
        for pat in patterns:
            for match in re.findall(pat, content):
                cleaned = match.strip().strip("`\"'")
                if "/" in cleaned or "\\" in cleaned:
                    referenced.add(cleaned.replace("\\", "/"))
    return referenced


def check_graph_coverage(migration_dir: Path) -> dict:
    graph_path = migration_dir / "graphify-out" / "graph.json"
    if not graph_path.exists():
        return {"exists": False, "nodes": 0, "edges": 0, "files_in_graph": set()}
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("links", data.get("edges", []))
    files_in_graph = set()
    for node in nodes:
        sf = node.get("source_file", "")
        if sf:
            files_in_graph.add(sf)
    return {
        "exists": True,
        "nodes": len(nodes),
        "edges": len(edges),
        "files_in_graph": files_in_graph,
    }


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    migration_dir = root / ".migration" / "discovery"

    if not migration_dir.exists():
        print(
            "ERROR: .migration/ directory not found. Run /one-modernizer:discover first."
        )
        sys.exit(1)

    source_files = find_source_files(root)
    referenced = find_referenced_files(migration_dir)
    graph_info = check_graph_coverage(migration_dir)

    # Calculate coverage
    covered = set()
    uncovered = set()
    for f in source_files:
        f_str = str(f).replace("\\", "/")
        if (
            f_str in referenced
            or f_str in graph_info.get("files_in_graph", set())
            or any(f_str.endswith(r) or r.endswith(f_str) for r in referenced)
        ):
            covered.add(f_str)
        else:
            uncovered.add(f_str)

    total = len(source_files)
    coverage_pct = (len(covered) / total * 100) if total else 0

    # Group uncovered by directory
    uncovered_by_dir = defaultdict(list)
    for f in sorted(uncovered):
        parts = f.split("/")
        dir_key = parts[0] if len(parts) > 1 else "."
        uncovered_by_dir[dir_key].append(f)

    # Output report
    print("# Coverage Report")
    print("")
    print(f"**Project**: {root.name}")
    print(f"**Total source files**: {total}")
    print(f"**Covered in docs**: {len(covered)}")
    print(f"**Not covered**: {len(uncovered)}")
    print(f"**Coverage**: {coverage_pct:.1f}%")
    print("")

    if graph_info["exists"]:
        print("## Graph Stats")
        print(f"- Nodes: {graph_info['nodes']}")
        print(f"- Edges: {graph_info['edges']}")
        print(f"- Files in graph: {len(graph_info['files_in_graph'])}")
        print("")

    if uncovered_by_dir:
        print("## Uncovered Files (potential gaps)")
        print("")
        for dir_name, files in sorted(
            uncovered_by_dir.items(), key=lambda x: -len(x[1])
        ):
            print(f"### {dir_name}/ ({len(files)} files)")
            for f in files[:10]:
                print(f"  - {f}")
            if len(files) > 10:
                print(f"  - ... and {len(files) - 10} more")
            print()

    # Check for module docs
    modules_dir = migration_dir / "modules"
    if modules_dir.exists():
        module_docs = list(modules_dir.glob("*.md"))
        print("## Module Documentation")
        print(f"- Module docs found: {len(module_docs)}")
        for doc in sorted(module_docs):
            content = doc.read_text(encoding="utf-8", errors="ignore")
            empty_sections = content.count("{{")
            print(
                f"  - {doc.name} {'⚠️ has unfilled templates' if empty_sections > 0 else '✓'}"
            )
    else:
        print("## ⚠️  No modules/ directory found in .migration/")

    # Summary
    print("\n## Verdict")
    if coverage_pct >= 90:
        print(f"✓ Good coverage ({coverage_pct:.0f}%)")
    elif coverage_pct >= 70:
        print(
            f"⚠️  Partial coverage ({coverage_pct:.0f}%) — review uncovered files above"
        )
    else:
        print(
            f"✗ Low coverage ({coverage_pct:.0f}%) — significant portions of the codebase are undocumented"
        )

    sys.exit(0 if coverage_pct >= 70 else 1)


if __name__ == "__main__":
    main()
