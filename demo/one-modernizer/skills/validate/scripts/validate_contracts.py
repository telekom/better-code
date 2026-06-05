#!/usr/bin/env python3
"""Validate API and event contracts against blueprint.

Usage: python3 validate_contracts.py <project-dir> [blueprint-path]

Checks:
- OpenAPI spec exists and covers all REST endpoints from blueprint
- Event schemas exist for all published/consumed events
- Proto files exist for gRPC services
"""

import json
import sys
from pathlib import Path


def find_file(project_dir: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        matches = list(project_dir.rglob(pattern))
        if matches:
            return matches[0]
    return None


def load_blueprint(blueprint_path: Path) -> dict | None:
    if not blueprint_path.exists():
        return None
    try:
        return json.loads(blueprint_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def check_openapi(project_dir: Path, blueprint: dict) -> dict:
    openapi_file = find_file(
        project_dir, ["openapi.yaml", "openapi.yml", "openapi.json", "swagger.yaml"]
    )

    expected_endpoints = []
    for service in blueprint.get("services", []):
        for api in service.get("apis", []):
            expected_endpoints.append(
                f"{api.get('method', 'GET')} {api.get('path', '/')}"
            )

    if not expected_endpoints:
        return {"status": "N/A", "reason": "No REST endpoints in blueprint"}

    if openapi_file is None:
        return {
            "status": "MISSING",
            "expected_endpoints": len(expected_endpoints),
            "file": None,
        }

    content = openapi_file.read_text(encoding="utf-8", errors="replace")
    covered = sum(1 for ep in expected_endpoints if ep.split(" ")[1] in content)

    return {
        "status": "PASS" if covered == len(expected_endpoints) else "PARTIAL",
        "file": str(openapi_file.relative_to(project_dir)),
        "covered": covered,
        "total": len(expected_endpoints),
    }


def check_events(project_dir: Path, blueprint: dict) -> dict:
    expected_events = []
    for service in blueprint.get("services", []):
        for event in service.get("events_published", []):
            expected_events.append(event.get("name", ""))
        for event in service.get("events_consumed", []):
            expected_events.append(event.get("name", ""))

    if not expected_events:
        return {"status": "N/A", "reason": "No events in blueprint"}

    schema_file = find_file(
        project_dir, ["*.avsc", "asyncapi.yaml", "asyncapi.yml", "events.json"]
    )

    if schema_file is None:
        return {
            "status": "MISSING",
            "expected_events": len(expected_events),
            "file": None,
        }

    content = schema_file.read_text(encoding="utf-8", errors="replace")
    covered = sum(1 for ev in expected_events if ev.lower() in content.lower())

    return {
        "status": "PASS" if covered == len(expected_events) else "PARTIAL",
        "file": str(schema_file.relative_to(project_dir)),
        "covered": covered,
        "total": len(expected_events),
    }


def check_proto(project_dir: Path, blueprint: dict) -> dict:
    api_style = blueprint.get("tech_stack", {}).get("api_style", "")
    if "grpc" not in api_style.lower():
        return {"status": "N/A", "reason": "Not a gRPC service"}

    proto_files = list(project_dir.rglob("*.proto"))
    if not proto_files:
        return {"status": "MISSING", "file": None}

    return {
        "status": "PASS",
        "files": [str(f.relative_to(project_dir)) for f in proto_files],
    }


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 validate_contracts.py <project-dir> [blueprint-path]",
            file=sys.stderr,
        )
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()

    blueprint_path = None
    if len(sys.argv) > 2:
        blueprint_path = Path(sys.argv[2]).resolve()
    else:
        candidates = list(project_dir.rglob("blueprint.json")) + list(
            Path(".migration").rglob("blueprint.json")
        )
        if candidates:
            blueprint_path = candidates[0]

    if blueprint_path is None or not blueprint_path.exists():
        print(
            "WARNING: No blueprint.json found. Cannot validate contracts fully.",
            file=sys.stderr,
        )
        blueprint = {"services": []}
    else:
        blueprint = load_blueprint(blueprint_path) or {"services": []}

    openapi = check_openapi(project_dir, blueprint)
    events = check_events(project_dir, blueprint)
    proto = check_proto(project_dir, blueprint)

    report = {"openapi": openapi, "events": events, "proto": proto}
    print(json.dumps(report, indent=2))

    print("\n# Contract Validation", file=sys.stderr)
    print(f"  OpenAPI: {openapi['status']}", file=sys.stderr)
    print(f"  Events:  {events['status']}", file=sys.stderr)
    print(f"  Proto:   {proto['status']}", file=sys.stderr)

    has_missing = any(r["status"] == "MISSING" for r in [openapi, events, proto])
    if has_missing:
        print("\n  ⚠ Missing contracts detected — generate them.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
