#!/usr/bin/env python3
"""Detect build system and attempt compilation.

Usage: python3 validate_build.py <project-dir>

Auto-detects: Maven, Gradle, Go, .NET, Python, Node/TypeScript.
Reports build status and errors.
"""

import json
import subprocess
import sys
from pathlib import Path


BUILD_SYSTEMS = [
    {"name": "gradle", "detect": "build.gradle", "cmd": "./gradlew build -x test -q"},
    {
        "name": "gradle-kts",
        "detect": "build.gradle.kts",
        "cmd": "./gradlew build -x test -q",
    },
    {"name": "maven", "detect": "pom.xml", "cmd": "mvn compile -q"},
    {"name": "go", "detect": "go.mod", "cmd": "go build ./..."},
    {"name": "dotnet-sln", "detect": "*.sln", "cmd": "dotnet build --no-restore -q"},
    {
        "name": "dotnet-csproj",
        "detect": "*.csproj",
        "cmd": "dotnet build --no-restore -q",
    },
    {
        "name": "python",
        "detect": "pyproject.toml",
        "cmd": "python -m compileall -q src/",
    },
    {"name": "node-ts", "detect": "tsconfig.json", "cmd": "npx tsc --noEmit"},
    {"name": "node", "detect": "package.json", "cmd": "npm run build --if-present"},
]


def detect_build_system(project_dir: Path) -> dict | None:
    for system in BUILD_SYSTEMS:
        pattern = system["detect"]
        if "*" in pattern:
            if list(project_dir.glob(pattern)):
                return system
        elif (project_dir / pattern).exists():
            return system
    return None


def run_build(project_dir: Path, cmd: str) -> dict:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=300,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Build timed out (5min)",
        }
    except Exception as e:
        return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e)}


def count_errors(output: str) -> int:
    error_patterns = ["error:", "ERROR", "FAILED", "Error:", "error["]
    count = 0
    for line in output.split("\n"):
        if any(p in line for p in error_patterns):
            count += 1
    return count


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_build.py <project-dir>", file=sys.stderr)
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.exists():
        print(f"ERROR: Directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    system = detect_build_system(project_dir)
    if system is None:
        for subdir in sorted(project_dir.iterdir()):
            if subdir.is_dir():
                system = detect_build_system(subdir)
                if system:
                    project_dir = subdir
                    break

    if system is None:
        print("ERROR: No recognized build system found", file=sys.stderr)
        print(json.dumps({"status": "UNKNOWN", "error": "No build system detected"}))
        sys.exit(1)

    print(f"Detected: {system['name']}", file=sys.stderr)
    print(f"Running: {system['cmd']}", file=sys.stderr)

    result = run_build(project_dir, system["cmd"])
    error_count = count_errors(result["stderr"] + result["stdout"])

    output = {
        "status": "PASS" if result["success"] else "FAIL",
        "build_system": system["name"],
        "command": system["cmd"],
        "errors": error_count,
        "output": result["stderr"][:3000] if not result["success"] else "",
    }

    print(json.dumps(output, indent=2))

    if result["success"]:
        print("\n## Build: PASS ✓", file=sys.stderr)
    else:
        print(f"\n## Build: FAIL ✗ ({error_count} errors)", file=sys.stderr)
        if result["stderr"]:
            print(result["stderr"][:1000], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
