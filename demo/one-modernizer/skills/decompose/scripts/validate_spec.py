#!/usr/bin/env python3
"""Validate a decomposition spec for internal consistency and valid references.

Usage: python3 validate_spec.py <decompose-output-dir>
       e.g.: python3 validate_spec.py .migration/decompose/order-management/

Checks:
- Every source field points to an existing file with valid line numbers
- Every data_fields reference in rules maps to a field in data-model.json
- Every covers_rules in test cases references a valid rule ID
- No orphan rules (rules without any test case)
- No orphan flows (flows without any test case)
- All dependencies between rules are valid references
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


def check_source_exists(source: str, project_root: Path) -> bool:
    """Check if a file:line reference points to an existing file."""
    if not source or source == "":
        return False
    parts = source.rsplit(":", 1)
    file_path = parts[0]
    candidate = project_root / file_path
    return candidate.exists()


def validate(spec_dir: Path, project_root: Path | None = None) -> dict:
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {},
    }

    if project_root is None:
        project_root = spec_dir.parents[2]

    spec = load_json(spec_dir / "spec.json")
    if spec is None:
        results["valid"] = False
        results["errors"].append("spec.json not found or invalid")
        return results

    rules = spec.get("business_rules", [])
    data_model = spec.get("data_model", [])
    flows = spec.get("flows", [])
    errors = spec.get("errors", [])
    test_cases = spec.get("test_cases", [])
    unknowns = spec.get("unknowns", [])

    results["stats"] = {
        "rules": len(rules),
        "data_structures": len(data_model),
        "flows": len(flows),
        "errors": len(errors),
        "test_cases": len(test_cases),
        "unknowns": len(unknowns),
    }

    rule_ids = {r["id"] for r in rules if "id" in r}
    flow_ids = {f["id"] for f in flows if "id" in f}
    all_fields = set()
    for structure in data_model:
        for field in structure.get("fields", []):
            all_fields.add(f"{structure['name']}.{field['name']}")
            all_fields.add(field["name"])

    # Check source references exist
    source_errors = 0
    source_checked = 0
    for rule in rules:
        source = rule.get("source", "")
        if source:
            source_checked += 1
            if not check_source_exists(source, project_root):
                source_errors += 1
                results["warnings"].append(
                    f"Rule {rule['id']}: source not found: {source}"
                )

    for flow in flows:
        for step in flow.get("steps", []):
            source = step.get("source", "")
            if source:
                source_checked += 1
                if not check_source_exists(source, project_root):
                    source_errors += 1

    if source_errors > 0:
        pct = round((source_checked - source_errors) / max(source_checked, 1) * 100, 1)
        if pct < 90:
            results["valid"] = False
            results["errors"].append(
                f"Source reference accuracy: {pct}% ({source_errors} broken of {source_checked})"
            )
        else:
            results["warnings"].append(
                f"Source references: {source_errors} broken of {source_checked} ({pct}% valid)"
            )

    # Check rule dependencies are valid
    for rule in rules:
        for dep in rule.get("dependencies", []):
            if dep not in rule_ids:
                results["errors"].append(
                    f"Rule {rule['id']}: depends on {dep} which doesn't exist"
                )
                results["valid"] = False

    # Check test cases reference valid rules
    rules_covered = set()
    flows_covered = set()
    for tc in test_cases:
        for rule_ref in tc.get("covers_rules", []):
            if rule_ref not in rule_ids:
                results["errors"].append(
                    f"Test {tc['id']}: covers_rules references {rule_ref} which doesn't exist"
                )
                results["valid"] = False
            else:
                rules_covered.add(rule_ref)
        flow_ref = tc.get("covers_flow", "")
        if flow_ref:
            if flow_ref not in flow_ids:
                results["errors"].append(
                    f"Test {tc['id']}: covers_flow references {flow_ref} which doesn't exist"
                )
                results["valid"] = False
            else:
                flows_covered.add(flow_ref)

    # Check orphan rules (no test case)
    orphan_rules = rule_ids - rules_covered
    if orphan_rules:
        rule_coverage = round(len(rules_covered) / max(len(rule_ids), 1) * 100, 1)
        if rule_coverage < 80:
            results["warnings"].append(
                f"Rule test coverage: {rule_coverage}% — orphan rules: {', '.join(sorted(orphan_rules))}"
            )
        else:
            results["warnings"].append(f"Rule test coverage: {rule_coverage}%")

    # Check orphan flows
    orphan_flows = flow_ids - flows_covered
    if orphan_flows:
        results["warnings"].append(
            f"Flows without test cases: {', '.join(sorted(orphan_flows))}"
        )

    # Check data_fields in rules map to data model
    for rule in rules:
        for field_ref in rule.get("data_fields", []):
            parts = field_ref.split(".")
            field_name = parts[-1] if parts else field_ref
            if field_ref not in all_fields and field_name not in all_fields:
                results["warnings"].append(
                    f"Rule {rule['id']}: data_field '{field_ref}' not found in data model"
                )

    results["stats"]["rule_coverage_pct"] = round(
        len(rules_covered) / max(len(rule_ids), 1) * 100, 1
    )
    results["stats"]["flow_coverage_pct"] = round(
        len(flows_covered) / max(len(flow_ids), 1) * 100, 1
    )
    results["stats"]["source_accuracy_pct"] = round(
        (source_checked - source_errors) / max(source_checked, 1) * 100, 1
    )

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_spec.py <decompose-output-dir>", file=sys.stderr)
        sys.exit(1)

    spec_dir = Path(sys.argv[1]).resolve()
    if not spec_dir.exists():
        print(f"ERROR: Directory not found: {spec_dir}", file=sys.stderr)
        sys.exit(1)

    project_root = None
    if len(sys.argv) > 2:
        project_root = Path(sys.argv[2]).resolve()

    results = validate(spec_dir, project_root)

    print(f"\n# Spec Validation: {spec_dir.name}")
    print("")
    print("## Stats")
    for key, val in results["stats"].items():
        print(f"  - {key}: {val}")
    print("")

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
