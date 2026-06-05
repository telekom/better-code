#!/usr/bin/env python3
"""Partition a large repo into digestible chunks for LLM processing.

Usage: python3 chunk_repo.py [project-root] [--max-loc 50000]

For repos with 2M+ LOC, a single-pass analysis is impractical.
This script:
1. Scans the repo structure
2. Groups files by directory/module/namespace
3. Estimates token cost per chunk
4. Outputs a chunking plan that the discover skill can process sequentially

Output: .migration/chunks.json with ordered list of chunks to process.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from _constants import IGNORE_DIRS, SOURCE_EXTENSIONS

DEFAULT_MAX_LOC = 50000  # ~50k lines per chunk, roughly 150k tokens


def count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in open(path, encoding="utf-8", errors="ignore"))
    except (OSError, UnicodeDecodeError):
        return 0


def scan_repo(root: Path) -> dict[str, list[dict]]:
    """Group source files by top-level directory."""
    groups = defaultdict(list)
    for f in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if not f.is_file() or f.suffix.lower() not in SOURCE_EXTENSIONS:
            continue

        rel = f.relative_to(root)
        parts = rel.parts
        # Group by first meaningful directory level
        if len(parts) > 1:
            group_key = parts[0]
        else:
            group_key = "."

        loc = count_lines(f)
        groups[group_key].append(
            {
                "path": str(rel),
                "loc": loc,
                "extension": f.suffix.lower(),
            }
        )

    return dict(groups)


def create_chunks(groups: dict, max_loc: int) -> list[dict]:
    """Create chunks that fit within the LOC budget."""
    chunks = []
    chunk_id = 0

    for group_name, files in sorted(
        groups.items(), key=lambda x: -sum(f["loc"] for f in x[1])
    ):
        group_loc = sum(f["loc"] for f in files)

        if group_loc <= max_loc:
            # Entire group fits in one chunk
            chunks.append(
                {
                    "id": chunk_id,
                    "name": group_name,
                    "files": [f["path"] for f in files],
                    "loc": group_loc,
                    "file_count": len(files),
                    "estimated_tokens": group_loc * 3,
                }
            )
            chunk_id += 1
        else:
            # Split group into sub-chunks by subdirectory
            subgroups = defaultdict(list)
            for f in files:
                parts = Path(f["path"]).parts
                if len(parts) > 2:
                    sub_key = f"{parts[0]}/{parts[1]}"
                else:
                    sub_key = group_name
                subgroups[sub_key].append(f)

            current_chunk_files = []
            current_loc = 0

            for sub_name, sub_files in sorted(subgroups.items()):
                sub_loc = sum(f["loc"] for f in sub_files)

                if current_loc + sub_loc > max_loc and current_chunk_files:
                    chunks.append(
                        {
                            "id": chunk_id,
                            "name": f"{group_name} (part {chunk_id})",
                            "files": [f["path"] for f in current_chunk_files],
                            "loc": current_loc,
                            "file_count": len(current_chunk_files),
                            "estimated_tokens": current_loc * 3,
                        }
                    )
                    chunk_id += 1
                    current_chunk_files = []
                    current_loc = 0

                current_chunk_files.extend(sub_files)
                current_loc += sub_loc

            if current_chunk_files:
                chunks.append(
                    {
                        "id": chunk_id,
                        "name": f"{group_name} (part {chunk_id})"
                        if group_loc > max_loc
                        else group_name,
                        "files": [f["path"] for f in current_chunk_files],
                        "loc": current_loc,
                        "file_count": len(current_chunk_files),
                        "estimated_tokens": current_loc * 3,
                    }
                )
                chunk_id += 1

    return chunks


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    max_loc = DEFAULT_MAX_LOC
    if "--max-loc" in sys.argv:
        idx = sys.argv.index("--max-loc")
        max_loc = int(sys.argv[idx + 1])

    print(f"Scanning {root.name}...", file=sys.stderr)
    groups = scan_repo(root)

    total_files = sum(len(files) for files in groups.values())
    total_loc = sum(f["loc"] for files in groups.values() for f in files)

    print(
        f"Found {total_files} source files, {total_loc:,} LOC across {len(groups)} top-level groups",
        file=sys.stderr,
    )

    chunks = create_chunks(groups, max_loc)

    # Write chunking plan
    migration_dir = root / ".migration" / "discovery"
    migration_dir.mkdir(parents=True, exist_ok=True)

    output = {
        "project": root.name,
        "total_files": total_files,
        "total_loc": total_loc,
        "max_loc_per_chunk": max_loc,
        "chunk_count": len(chunks),
        "estimated_total_tokens": total_loc * 3,
        "chunks": chunks,
    }

    out_path = migration_dir / "chunks.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    # Print summary
    print("# Chunking Plan")
    print("")
    print(f"**Project**: {root.name}")
    print(f"**Total LOC**: {total_loc:,}")
    print(f"**Total files**: {total_files}")
    print(f"**Chunks**: {len(chunks)}")
    print(f"**Max LOC/chunk**: {max_loc:,}")
    print(f"**Estimated total tokens**: {total_loc * 3:,}")
    print("")
    print("## Chunks (ordered by size)")
    print("")
    for chunk in sorted(chunks, key=lambda c: -c["loc"]):
        print(
            f"  {chunk['id']:3d}. {chunk['name']:<40} {chunk['loc']:>8,} LOC  ({chunk['file_count']} files)"
        )

    print(f"\nPlan saved to: {out_path}")


if __name__ == "__main__":
    main()
