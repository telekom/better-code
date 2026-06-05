#!/usr/bin/env python3
"""Validate architecture output for completeness and consistency.

Usage: python3 validate_architecture.py <architect-output-dir> [decompose-dir]
       e.g.: python3 validate_architecture.py .migration/architect/order-management/ .migration/decompose/order-management/

Checks:
- Every rule/flow/data-model/error in spec.json has an entry in mapping.json
- Every service in blueprint.json has at least one flow assigned
- Every data structure is owned by exactly one service
- ADR files have all required sections
- Service names are consistent across blueprint, mapping, and scaffold
"""

import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  ERROR: Invalid JSON in {path.name}: {e}", file=sys.stderr)
        return None


def validate_adrs(adrs_dir: Path) -> list[str]:
    """Check ADR files have required sections."""
    errors = []
    required_sections = {"status", "context", "decision", "consequences"}

    if not adrs_dir.exists():
        errors.append("adrs/ directory not found")
        return errors

    adr_files = sorted(adrs_dir.glob("*.md"))
    if not adr_files:
        errors.append("No ADR files found in adrs/")
        return errors

    for adr_file in adr_files:
        content = adr_file.read_text(encoding="utf-8", errors="replace").lower()
        sections_found = set()
        for line in content.split("\n"):
            if line.startswith("## "):
                section = line[3:].strip()
                sections_found.add(section)

        missing = required_sections - sections_found
        if missing:
            errors.append(
                f"ADR {adr_file.name}: missing sections: {', '.join(sorted(missing))}"
            )

    return errors


def validate(architect_dir: Path, decompose_dir: Path | None = None) -> dict:
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {},
    }

    blueprint = load_json(architect_dir / "blueprint.json")
    mapping = load_json(architect_dir / "mapping.json")
    scaffold = load_json(architect_dir / "scaffold.json")

    if blueprint is None:
        results["valid"] = False
        results["errors"].append("blueprint.json not found or invalid")
    if mapping is None:
        results["valid"] = False
        results["errors"].append("mapping.json not found or invalid")

    if not results["valid"]:
        return results

    # Load spec.json from decompose if available
    spec = None
    if decompose_dir:
        spec = load_json(decompose_dir / "spec.json")

    # Collect service names from blueprint
    blueprint_services = {s["name"] for s in blueprint.get("services", [])}
    results["stats"]["services"] = len(blueprint_services)

    # Check every service has at least one flow
    for service in blueprint.get("services", []):
        if not service.get("handles_flows"):
            results["warnings"].append(
                f"Service '{service['name']}' has no flows assigned"
            )

    # Check data ownership (each structure owned by exactly one service)
    data_owners = {}
    for service in blueprint.get("services", []):
        for data_name in service.get("owns_data", []):
            if data_name in data_owners:
                results["errors"].append(
                    f"Data '{data_name}' owned by both '{data_owners[data_name]}' and '{service['name']}'"
                )
                results["valid"] = False
            else:
                data_owners[data_name] = service["name"]

    # Check mapping service names match blueprint
    mapping_services = set()
    for category in (
        "rules",
        "data_model",
        "flows",
        "errors",
        "interfaces",
        "test_cases",
    ):
        for item in mapping.get(category, []):
            svc = item.get("target_service", "")
            if svc:
                mapping_services.add(svc)

    unknown_services = mapping_services - blueprint_services
    if unknown_services:
        results["errors"].append(
            f"Mapping references services not in blueprint: {', '.join(sorted(unknown_services))}"
        )
        results["valid"] = False

    # Check mapping completeness against spec.json
    if spec:
        spec_rule_ids = {r["id"] for r in spec.get("business_rules", [])}
        spec_flow_ids = {f["id"] for f in spec.get("flows", [])}
        spec_data_names = {d["name"] for d in spec.get("data_model", [])}
        spec_error_ids = {e["id"] for e in spec.get("errors", [])}

        mapped_rule_ids = {r["spec_id"] for r in mapping.get("rules", [])}
        mapped_flow_ids = {f["spec_id"] for f in mapping.get("flows", [])}
        mapped_data_names = {d["spec_name"] for d in mapping.get("data_model", [])}
        mapped_error_ids = {e["spec_id"] for e in mapping.get("errors", [])}

        unmapped_rules = spec_rule_ids - mapped_rule_ids
        unmapped_flows = spec_flow_ids - mapped_flow_ids
        unmapped_data = spec_data_names - mapped_data_names
        unmapped_errors = spec_error_ids - mapped_error_ids

        results["stats"]["rules_mapped"] = (
            f"{len(mapped_rule_ids)}/{len(spec_rule_ids)}"
        )
        results["stats"]["flows_mapped"] = (
            f"{len(mapped_flow_ids)}/{len(spec_flow_ids)}"
        )
        results["stats"]["data_mapped"] = (
            f"{len(mapped_data_names)}/{len(spec_data_names)}"
        )
        results["stats"]["errors_mapped"] = (
            f"{len(mapped_error_ids)}/{len(spec_error_ids)}"
        )

        if unmapped_rules:
            results["errors"].append(
                f"Unmapped rules: {', '.join(sorted(unmapped_rules))}"
            )
            results["valid"] = False
        if unmapped_flows:
            results["errors"].append(
                f"Unmapped flows: {', '.join(sorted(unmapped_flows))}"
            )
            results["valid"] = False
        if unmapped_data:
            results["warnings"].append(
                f"Unmapped data structures: {', '.join(sorted(unmapped_data))}"
            )
        if unmapped_errors:
            results["warnings"].append(
                f"Unmapped errors: {', '.join(sorted(unmapped_errors))}"
            )
    else:
        results["stats"]["rules_mapped"] = (
            f"{len(mapping.get('rules', []))} (no spec to verify against)"
        )
        results["stats"]["flows_mapped"] = f"{len(mapping.get('flows', []))}"

    # Check scaffold consistency with mapping
    if scaffold:
        scaffold_services = {s["name"] for s in scaffold.get("services", [])}
        missing_scaffold = blueprint_services - scaffold_services
        if missing_scaffold:
            results["warnings"].append(
                f"Services in blueprint but not in scaffold: {', '.join(sorted(missing_scaffold))}"
            )

    # Validate ADRs
    adr_errors = validate_adrs(architect_dir / "adrs")
    for err in adr_errors:
        results["errors"].append(err)
        results["valid"] = False

    results["stats"]["adrs"] = (
        len(list((architect_dir / "adrs").glob("*.md")))
        if (architect_dir / "adrs").exists()
        else 0
    )

    return results


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 validate_architecture.py <architect-dir> [decompose-dir]",
            file=sys.stderr,
        )
        sys.exit(1)

    architect_dir = Path(sys.argv[1]).resolve()
    decompose_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

    if not architect_dir.exists():
        print(f"ERROR: Directory not found: {architect_dir}", file=sys.stderr)
        sys.exit(1)

    results = validate(architect_dir, decompose_dir)

    print(f"\n# Architecture Validation: {architect_dir.name}")
    print("")
    print("## Stats")
    for key, val in results["stats"].items():
        print(f"  - {key}: {val}")
    print()

    if results["errors"]:
        print(f"## Errors ({len(results['errors'])})")
        for err in results["errors"]:
            print(f"  ✗ {err}")
        print()

    if results["warnings"]:
        print(f"## Warnings ({len(results['warnings'])})")
        for warn in results["warnings"]:
            print(f"  ⚠ {warn}")
        print()

    if results["valid"]:
        print("## Result: VALID ✓")
    else:
        print("## Result: INVALID ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()
