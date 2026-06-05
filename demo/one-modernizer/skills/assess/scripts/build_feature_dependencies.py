#!/usr/bin/env python3
"""Build feature-level dependency graph from module-level graph.

Reads feature-map.json and graph.json to determine which features
depend on which other features.

Usage: python3 build_feature_dependencies.py [project-root]

Outputs: .migration/assess/feature-dependencies.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def load_feature_map(assess_dir: Path) -> dict:
    """Load feature-map.json."""
    path = assess_dir / "feature-map.json"
    if not path.exists():
        print(
            "ERROR: feature-map.json not found. Run extract_features.py first.",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def load_graph(discovery_dir: Path) -> dict:
    """Load graph.json."""
    path = discovery_dir / "graphify-out" / "graph.json"
    if not path.exists():
        print("ERROR: graph.json not found.", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def build_module_to_feature(feature_map: dict) -> dict[str, str]:
    """Map each module name to its feature."""
    mapping = {}
    for feature in feature_map.get("features", []):
        for module in feature["modules"]:
            mapping[module.lower()] = feature["name"]
    return mapping


def extract_dependencies(graph: dict, module_to_feature: dict) -> list[dict]:
    """Find cross-feature edges in the graph."""
    edges = graph.get("links", graph.get("edges", []))
    nodes_by_id = {}
    for node in graph.get("nodes", []):
        nodes_by_id[node["id"]] = node.get("label", node["id"])

    cross_feature_edges = defaultdict(lambda: defaultdict(list))

    dependency_relations = frozenset(  # noqa: F841
        {
            "call",
            "calls",
            "imports",
            "includes",
            "sql_access",
            "executes",
            "calls_proc",
            "calls_builtin",
            "fires_on",
            "reads_dataset",
            "writes_dataset",
            "cics_command",
        }
    )

    for edge in edges:
        relation = edge.get("relation", "")
        if relation in ("contains", "contains_step"):
            continue

        source_id = edge.get("source", "")
        target_id = edge.get("target", "")

        source_label = nodes_by_id.get(source_id, source_id).lower()
        target_label = nodes_by_id.get(target_id, target_id).lower()

        source_feature = module_to_feature.get(source_label)
        target_feature = module_to_feature.get(target_label)

        if not source_feature or not target_feature:
            continue
        if source_feature == target_feature:
            continue

        cross_feature_edges[source_feature][target_feature].append(relation)

    dependencies = []
    for from_feature, targets in sorted(cross_feature_edges.items()):
        for to_feature, relations in sorted(targets.items()):
            relation_summary = ", ".join(sorted(set(relations)))
            dependencies.append(
                {
                    "from": from_feature,
                    "to": to_feature,
                    "relations": list(set(relations)),
                    "count": len(relations),
                    "reason": f"{from_feature} → {to_feature} via: {relation_summary}",
                }
            )

    return dependencies


def find_leaf_features(features: list[dict], dependencies: list[dict]) -> list[str]:
    """Features with no outgoing dependencies — can migrate first."""
    all_features = {f["name"] for f in features}
    has_dependency = {d["from"] for d in dependencies}
    return sorted(all_features - has_dependency)


def find_root_features(features: list[dict], dependencies: list[dict]) -> list[str]:
    """Features nothing depends on — can migrate last."""
    all_features = {f["name"] for f in features}
    is_depended_on = {d["to"] for d in dependencies}
    return sorted(all_features - is_depended_on)


def topological_sort(features: list[dict], dependencies: list[dict]) -> list[list[str]]:
    """Layer features by dependency depth (parallel waves)."""
    all_names = {f["name"] for f in features}
    dep_map = defaultdict(set)
    for d in dependencies:
        if d["from"] in all_names and d["to"] in all_names:
            dep_map[d["from"]].add(d["to"])

    layers = []
    placed = set()

    while len(placed) < len(all_names):
        layer = []
        for name in sorted(all_names - placed):
            unmet = dep_map[name] - placed
            if not unmet:
                layer.append(name)
        if not layer:
            layer = sorted(all_names - placed)[:1]
        placed.update(layer)
        layers.append(layer)

    return layers


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    assess_dir = root / ".migration" / "assess"
    discovery_dir = root / ".migration" / "discovery"

    feature_map = load_feature_map(assess_dir)
    graph = load_graph(discovery_dir)

    module_to_feature = build_module_to_feature(feature_map)
    features = feature_map.get("features", [])
    dependencies = extract_dependencies(graph, module_to_feature)
    layers = topological_sort(features, dependencies)
    leaves = find_leaf_features(features, dependencies)
    roots = find_root_features(features, dependencies)

    output = {
        "edges": dependencies,
        "layers": [{"wave": i, "features": layer} for i, layer in enumerate(layers)],
        "leaf_features": leaves,
        "root_features": roots,
        "total_cross_feature_edges": len(dependencies),
    }

    out_path = assess_dir / "feature-dependencies.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("\n# Feature Dependencies", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"**Cross-feature dependencies**: {len(dependencies)}", file=sys.stderr)
    print(f"**Migration waves** (by dependency depth): {len(layers)}", file=sys.stderr)
    print("", file=sys.stderr)
    print("## Suggested Wave Order", file=sys.stderr)
    for i, layer in enumerate(layers):
        print(f"  Wave {i}: {', '.join(layer)}", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        f"**Leaf features** (no dependencies, can start first): {', '.join(leaves) or 'none'}",
        file=sys.stderr,
    )
    print(
        f"**Root features** (nothing depends on them, can go last): {', '.join(roots) or 'none'}",
        file=sys.stderr,
    )
    print(f"\nOutput: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
