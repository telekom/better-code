#!/usr/bin/env python3
"""Extract business features from discovery output.

Reads graph communities and module docs to produce a preliminary
feature → modules mapping. The LLM refines this afterward.

Usage: python3 extract_features.py [project-root]

Outputs: .migration/assess/feature-map.json
"""

import json
import re
import sys
from pathlib import Path


def parse_graph_report(report_path: Path) -> list[dict]:
    """Extract communities from GRAPH_REPORT.md."""
    if not report_path.exists():
        return []

    content = report_path.read_text(encoding="utf-8", errors="replace")
    communities = []
    current_community = None

    for line in content.split("\n"):
        community_match = re.match(
            r"#{2,3}\s+(?:Community|Cluster)\s*(\d+)", line, re.IGNORECASE
        )
        if community_match:
            if current_community:
                communities.append(current_community)
            current_community = {
                "id": int(community_match.group(1)),
                "members": [],
                "label": "",
            }
            continue

        if current_community is None:
            continue

        member_match = re.match(r"\s*[-*]\s+`?([^`\n]+)`?", line)
        if member_match:
            current_community["members"].append(member_match.group(1).strip())

    if current_community:
        communities.append(current_community)

    return communities


def parse_module_purposes(modules_dir: Path) -> dict[str, str]:
    """Extract purpose from each module doc."""
    purposes = {}
    if not modules_dir.exists():
        return purposes

    for f in sorted(modules_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="replace")
        purpose = ""
        in_purpose = False
        for line in content.split("\n"):
            if line.strip().lower().startswith("## purpose"):
                in_purpose = True
                continue
            if in_purpose:
                if line.startswith("## "):
                    break
                if line.strip():
                    purpose += line.strip() + " "
        purposes[f.stem] = purpose.strip()

    return purposes


def parse_index(index_path: Path) -> list[dict]:
    """Read module list from index.json."""
    if not index_path.exists():
        return []
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        return data.get("modules", [])
    except (json.JSONDecodeError, KeyError):
        return []


def build_features(
    communities: list[dict], purposes: dict[str, str], modules: list[dict]
) -> list[dict]:
    """Map communities to preliminary feature candidates."""
    features = []
    assigned_modules = set()

    for comm in communities:
        if not comm["members"]:
            continue

        purpose_hints = []
        member_names = []
        for member in comm["members"]:
            clean = member.split("/")[-1].replace(".md", "").replace("_", "-")
            member_names.append(clean)
            if clean in purposes and purposes[clean]:
                purpose_hints.append(purposes[clean][:200])
            assigned_modules.add(clean)

        feature_name = f"feature-{comm['id']}"
        if purpose_hints:
            words = " ".join(purpose_hints).lower()
            if any(kw in words for kw in ("auth", "login", "token", "session")):
                feature_name = "authentication"
            elif any(kw in words for kw in ("bill", "payment", "invoice", "charge")):
                feature_name = "billing"
            elif any(kw in words for kw in ("report", "dashboard", "analytics")):
                feature_name = "reporting"
            elif any(kw in words for kw in ("order", "cart", "checkout")):
                feature_name = "order-management"
            elif any(kw in words for kw in ("batch", "job", "schedule", "nightly")):
                feature_name = "batch-processing"
            elif any(kw in words for kw in ("notification", "email", "sms", "alert")):
                feature_name = "notifications"
            elif any(
                kw in words for kw in ("user", "profile", "account", "registration")
            ):
                feature_name = "user-management"
            elif any(
                kw in words for kw in ("data", "etl", "transform", "load", "extract")
            ):
                feature_name = "data-pipeline"
            elif any(kw in words for kw in ("api", "gateway", "endpoint", "service")):
                feature_name = "api-gateway"
            elif any(kw in words for kw in ("config", "setting", "parameter")):
                feature_name = "configuration"

        features.append(
            {
                "name": feature_name,
                "modules": member_names,
                "purpose_hints": purpose_hints[:5],
                "community_id": comm["id"],
            }
        )

    unassigned = []
    for mod in modules:
        mod_name = mod.get("name", "")
        if mod_name and mod_name not in assigned_modules:
            unassigned.append(mod_name)

    if unassigned:
        features.append(
            {
                "name": "unassigned",
                "modules": unassigned,
                "purpose_hints": ["Modules not yet assigned to a community/feature"],
                "community_id": -1,
            }
        )

    return features


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    discovery_dir = root / ".migration" / "discovery"

    if not discovery_dir.exists():
        print(
            "ERROR: .migration/discovery/ not found. Run discover first.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Extracting business features from discovery output...", file=sys.stderr)

    communities = parse_graph_report(discovery_dir / "graphify-out" / "GRAPH_REPORT.md")
    purposes = parse_module_purposes(discovery_dir / "modules")
    modules = parse_index(discovery_dir / "index.json")

    features = build_features(communities, purposes, modules)

    out_dir = root / ".migration" / "assess"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "feature-map.json"
    output = {
        "features": features,
        "total_modules": len(modules),
        "assigned_modules": sum(
            len(f["modules"]) for f in features if f["name"] != "unassigned"
        ),
        "unassigned_modules": sum(
            len(f["modules"]) for f in features if f["name"] == "unassigned"
        ),
    }
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("\n# Feature Extraction", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"**Features identified**: {len(features)}", file=sys.stderr)
    print(f"**Total modules**: {len(modules)}", file=sys.stderr)
    print(f"**Assigned**: {output['assigned_modules']}", file=sys.stderr)
    print(f"**Unassigned**: {output['unassigned_modules']}", file=sys.stderr)
    print("", file=sys.stderr)
    for f in features:
        print(f"- **{f['name']}** ({len(f['modules'])} modules)", file=sys.stderr)
    print(f"\nOutput: {out_path}", file=sys.stderr)
    print(
        "\nReview and refine feature names/groupings before proceeding.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
