#!/usr/bin/env python3
"""Detect test directories, frameworks, fixtures, and estimate coverage.

Usage: python3 test_inventory.py [project-root]

Outputs: .migration/test-inventory.json
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _constants import IGNORE_DIRS, SOURCE_EXTENSIONS

TEST_DIR_PATTERNS = {
    "test",
    "tests",
    "spec",
    "specs",
    "tst",
    "__tests__",
    "test_",
    "unittest",
    "integration",
    "e2e",
}

TEST_FILE_PATTERNS = [
    re.compile(r"test_\w+\.\w+$", re.IGNORECASE),
    re.compile(r"\w+_test\.\w+$", re.IGNORECASE),
    re.compile(r"\w+Test\.\w+$"),
    re.compile(r"\w+Tests\.\w+$"),
    re.compile(r"\w+Spec\.\w+$"),
    re.compile(r"\w+\.spec\.\w+$", re.IGNORECASE),
    re.compile(r"\w+\.test\.\w+$", re.IGNORECASE),
    re.compile(r"tst\w+\.\w+$", re.IGNORECASE),
]

FIXTURE_PATTERNS = {
    "fixtures",
    "testdata",
    "test_data",
    "golden",
    "expected",
    "snapshots",
    "__snapshots__",
    "mocks",
    "stubs",
}

FRAMEWORK_INDICATORS = {
    "JUnit": [re.compile(r"import\s+org\.junit"), re.compile(r"@Test")],
    "pytest": [re.compile(r"import\s+pytest"), re.compile(r"def\s+test_")],
    "unittest": [
        re.compile(r"import\s+unittest"),
        re.compile(r"class\s+\w+\(.*TestCase"),
    ],
    "gtest": [re.compile(r"#include\s+[<\"]gtest"), re.compile(r"TEST(_F)?\s*\(")],
    "Catch2": [re.compile(r"#include\s+[<\"]catch"), re.compile(r"TEST_CASE\s*\(")],
    "RSpec": [re.compile(r"require\s+['\"]rspec"), re.compile(r"describe\s+")],
    "Jest": [re.compile(r"describe\s*\("), re.compile(r"it\s*\(.*=>")],
    "Mocha": [re.compile(r"require\s*\(\s*['\"]mocha"), re.compile(r"describe\s*\(")],
    "xUnit": [re.compile(r"using\s+Xunit"), re.compile(r"\[Fact\]")],
    "NUnit": [re.compile(r"using\s+NUnit"), re.compile(r"\[Test\]")],
    "zUnit": [re.compile(r"ZUNIT", re.IGNORECASE)],
    "COBOLUnit": [re.compile(r"COBOLUNIT|COBUNIT", re.IGNORECASE)],
    "Go testing": [re.compile(r"import\s+\"testing\""), re.compile(r"func\s+Test\w+")],
}


def is_test_file(path: Path) -> bool:
    """Determine if a file is a test file by name or location."""
    name = path.name
    for pattern in TEST_FILE_PATTERNS:
        if pattern.match(name):
            return True
    for part in path.parts:
        if part.lower() in TEST_DIR_PATTERNS:
            return True
    return False


def detect_frameworks(root: Path) -> dict[str, int]:
    """Detect test frameworks by scanning file contents."""
    frameworks = defaultdict(int)
    scanned = 0
    max_scan = 200

    for f in root.rglob("*"):
        if scanned >= max_scan:
            break
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if not f.is_file() or f.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if not is_test_file(f):
            continue

        try:
            content = f.read_text(encoding="utf-8", errors="replace")[:5000]
        except OSError:
            continue

        scanned += 1
        for framework, patterns in FRAMEWORK_INDICATORS.items():
            for pattern in patterns:
                if pattern.search(content):
                    frameworks[framework] += 1
                    break

    return dict(frameworks)


def find_fixtures(root: Path) -> list[dict]:
    """Find test fixture/golden file directories."""
    fixtures = []
    for d in root.rglob("*"):
        if not d.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in d.parts):
            continue
        if d.name.lower() in FIXTURE_PATTERNS:
            file_count = sum(1 for f in d.rglob("*") if f.is_file())
            fixtures.append(
                {
                    "path": str(d.relative_to(root)),
                    "type": d.name.lower(),
                    "file_count": file_count,
                }
            )
    return fixtures


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"Scanning {root.name} for test assets...", file=sys.stderr)

    all_source = []
    test_files = []
    prod_files = []

    for f in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if not f.is_file() or f.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        all_source.append(f)
        if is_test_file(f):
            test_files.append(f)
        else:
            prod_files.append(f)

    # Detect frameworks
    frameworks = detect_frameworks(root)

    # Find fixtures
    fixtures = find_fixtures(root)

    # Estimate which prod files have corresponding tests
    prod_with_tests = set()
    test_stems = {
        f.stem.lower()
        .replace("test_", "")
        .replace("_test", "")
        .replace("test", "")
        .replace("spec", "")
        for f in test_files
    }
    for f in prod_files:
        if f.stem.lower() in test_stems:
            prod_with_tests.add(str(f.relative_to(root)))

    # Coverage by directory
    coverage_by_dir = defaultdict(lambda: {"total": 0, "tested": 0})
    for f in prod_files:
        rel = f.relative_to(root)
        dir_key = rel.parts[0] if len(rel.parts) > 1 else "."
        coverage_by_dir[dir_key]["total"] += 1
        if str(rel) in prod_with_tests:
            coverage_by_dir[dir_key]["tested"] += 1

    # Build inventory
    inventory = {
        "summary": {
            "total_source_files": len(all_source),
            "test_files": len(test_files),
            "production_files": len(prod_files),
            "prod_files_with_tests": len(prod_with_tests),
            "estimated_coverage_pct": round(
                len(prod_with_tests) / len(prod_files) * 100, 1
            )
            if prod_files
            else 0,
        },
        "frameworks": frameworks,
        "fixtures": fixtures,
        "coverage_by_directory": {k: v for k, v in sorted(coverage_by_dir.items())},
        "untested_directories": [
            k for k, v in coverage_by_dir.items() if v["tested"] == 0 and v["total"] > 3
        ],
    }

    # Output
    out_dir = root / ".migration" / "discovery"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "test-inventory.json"
    out_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")

    # Print summary
    s = inventory["summary"]
    print("\n# Test Asset Inventory")
    print("")
    print(f"**Total source files**: {s['total_source_files']}")
    print(f"**Test files**: {s['test_files']}")
    print(f"**Production files**: {s['production_files']}")
    print(f"**Files with corresponding tests**: {s['prod_files_with_tests']}")
    print(f"**Estimated coverage**: {s['estimated_coverage_pct']}%")
    print("")
    if frameworks:
        print("## Frameworks Detected")
        for fw, count in sorted(frameworks.items(), key=lambda x: -x[1]):
            print(f"  - {fw} ({count} files)")
        print()
    if fixtures:
        print("## Fixture Directories")
        for fix in fixtures:
            print(f"  - {fix['path']} ({fix['file_count']} files)")
        print()
    if inventory["untested_directories"]:
        print("## Untested Directories (0% coverage)")
        for d in inventory["untested_directories"]:
            print(f"  - {d}/")
    print(f"\nOutput: {out_path}")


if __name__ == "__main__":
    main()
