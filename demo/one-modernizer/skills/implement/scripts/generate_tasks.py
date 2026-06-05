#!/usr/bin/env python3
"""Generate ordered implementation tasks from architect output.

Reads implementation specs (or mapping.json + scaffold.json) and produces
an ordered task list respecting layer dependencies.

Usage: python3 generate_tasks.py <implement-dir>
       e.g.: python3 generate_tasks.py .migration/implement/order-management/

Outputs: tasks.json in the same directory.
"""

import json
import sys
from pathlib import Path


LAYER_ORDER = {
    "infrastructure": 0,
    "data": 1,
    "domain": 2,
    "api": 3,
    "cross-cutting": 4,
    "test": 5,
    "contract": 6,
}

TYPE_TO_LAYER = {
    "infra": "infrastructure",
    "config": "infrastructure",
    "migration": "data",
    "entity": "data",
    "repository": "data",
    "service": "domain",
    "exception": "domain",
    "dto": "api",
    "controller": "api",
    "event": "api",
    "middleware": "cross-cutting",
    "test": "test",
    "contract": "contract",
}


def load_specs(implement_dir: Path) -> list[dict]:
    """Load implementation specs from specs/ directory."""
    specs_dir = implement_dir / "specs"
    specs = []
    if specs_dir.exists():
        for f in sorted(specs_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                specs.append(data)
            except json.JSONDecodeError:
                continue
    return specs


def load_mapping_and_scaffold(implement_dir: Path) -> tuple[dict | None, dict | None]:
    """Fallback: load from architect output if specs don't exist."""
    feature_name = implement_dir.name
    architect_dir = implement_dir.parents[1] / "architect" / feature_name

    mapping = None
    scaffold = None

    mapping_path = architect_dir / "mapping.json"
    if mapping_path.exists():
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    scaffold_path = architect_dir / "scaffold.json"
    if scaffold_path.exists():
        scaffold = json.loads(scaffold_path.read_text(encoding="utf-8"))

    return mapping, scaffold


def generate_from_specs(specs: list[dict]) -> list[dict]:
    """Generate tasks from implementation specs."""
    tasks = []
    task_id = 1
    class_to_task = {}

    for spec in specs:
        service = spec.get("service", "unknown")
        for cls in spec.get("classes", []):
            layer = TYPE_TO_LAYER.get(cls.get("layer", "domain"), "domain")
            spec_refs = []
            for method in cls.get("methods", []):
                spec_refs.extend(method.get("implements", []))

            tid = f"T-{task_id:03d}"
            class_to_task[cls["name"]] = tid

            depends_on = []
            for dep in cls.get("dependencies", []):
                if dep in class_to_task:
                    depends_on.append(class_to_task[dep])

            tasks.append(
                {
                    "id": tid,
                    "type": cls.get("layer", "service"),
                    "description": f"Generate {cls['name']}",
                    "target_file": cls.get("file", f"{service}/src/{cls['name']}"),
                    "spec_refs": spec_refs if spec_refs else [cls["name"]],
                    "depends_on": depends_on,
                    "service": service,
                    "layer": layer,
                    "priority": LAYER_ORDER.get(layer, 3),
                }
            )
            task_id += 1

    return tasks


def generate_from_mapping(mapping: dict, scaffold: dict | None) -> list[dict]:
    """Generate tasks from mapping.json (fallback if specs don't exist)."""
    tasks = []
    task_id = 1
    entity_tasks = {}

    for item in mapping.get("data_model", []):
        tid = f"T-{task_id:03d}"
        entity_tasks[item["spec_name"]] = tid
        tasks.append(
            {
                "id": tid,
                "type": "entity",
                "description": f"Generate entity {item['target_entity']}",
                "target_file": f"{item['target_service']}/src/{item['target_entity']}.java",
                "spec_refs": [item["spec_name"]],
                "depends_on": [],
                "service": item["target_service"],
                "layer": "data",
                "priority": 1,
            }
        )
        task_id += 1

    for item in mapping.get("data_model", []):
        tid = f"T-{task_id:03d}"
        tasks.append(
            {
                "id": tid,
                "type": "repository",
                "description": f"Generate repository for {item['target_entity']}",
                "target_file": f"{item['target_service']}/src/{item['target_entity']}Repository.java",
                "spec_refs": [item["spec_name"]],
                "depends_on": [entity_tasks.get(item["spec_name"], "")],
                "service": item["target_service"],
                "layer": "data",
                "priority": 1,
            }
        )
        task_id += 1

    for item in mapping.get("rules", []):
        tid = f"T-{task_id:03d}"
        tasks.append(
            {
                "id": tid,
                "type": "service",
                "description": f"Generate {item['target_class']}.{item['target_method']}",
                "target_file": f"{item['target_service']}/src/{item['target_class']}.java",
                "spec_refs": [item["spec_id"]],
                "depends_on": [],
                "service": item["target_service"],
                "layer": "domain",
                "priority": 2,
            }
        )
        task_id += 1

    for item in mapping.get("flows", []):
        tid = f"T-{task_id:03d}"
        tasks.append(
            {
                "id": tid,
                "type": "controller",
                "description": f"Generate handler for {item.get('target_endpoint', item['spec_id'])}",
                "target_file": f"{item['target_service']}/src/{item['target_handler'].split('.')[0]}.java",
                "spec_refs": [item["spec_id"]],
                "depends_on": [],
                "service": item["target_service"],
                "layer": "api",
                "priority": 3,
            }
        )
        task_id += 1

    for item in mapping.get("test_cases", []):
        tid = f"T-{task_id:03d}"
        tasks.append(
            {
                "id": tid,
                "type": "test",
                "description": f"Generate test {item['target_test_class']}.{item['target_test_method']}",
                "target_file": f"tests/{item['target_test_class']}.java",
                "spec_refs": [item["spec_id"]],
                "depends_on": [],
                "service": item.get("target_service", "shared"),
                "layer": "test",
                "priority": 5,
            }
        )
        task_id += 1

    return tasks


def sort_tasks(tasks: list[dict]) -> list[dict]:
    """Sort by priority then resolve dependency ordering."""
    tasks.sort(key=lambda t: (t["priority"], t["id"]))

    ordered = []
    placed_ids = set()
    remaining = list(tasks)

    while remaining:
        progress = False
        next_remaining = []
        for task in remaining:
            deps = set(task.get("depends_on", [])) - {""}
            if deps <= placed_ids:
                ordered.append(task)
                placed_ids.add(task["id"])
                progress = True
            else:
                next_remaining.append(task)
        remaining = next_remaining
        if not progress:
            ordered.extend(remaining)
            break

    return ordered


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_tasks.py <implement-dir>", file=sys.stderr)
        sys.exit(1)

    implement_dir = Path(sys.argv[1]).resolve()
    if not implement_dir.exists():
        print(f"ERROR: Directory not found: {implement_dir}", file=sys.stderr)
        sys.exit(1)

    specs = load_specs(implement_dir)

    if specs:
        tasks = generate_from_specs(specs)
    else:
        mapping, scaffold = load_mapping_and_scaffold(implement_dir)
        if mapping is None:
            print(
                "ERROR: No specs/ directory and no mapping.json found.", file=sys.stderr
            )
            sys.exit(1)
        tasks = generate_from_mapping(mapping, scaffold)

    tasks = sort_tasks(tasks)

    services = sorted({t["service"] for t in tasks})
    output = {
        "feature": implement_dir.name,
        "total_tasks": len(tasks),
        "services": services,
        "tasks": tasks,
    }

    out_path = implement_dir / "tasks.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"\n# Task Generation: {implement_dir.name}", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"**Total tasks**: {len(tasks)}", file=sys.stderr)
    print(f"**Services**: {', '.join(services)}", file=sys.stderr)
    print("", file=sys.stderr)
    by_layer = {}
    for t in tasks:
        by_layer.setdefault(t["layer"], []).append(t)
    for layer in sorted(by_layer, key=lambda ly: LAYER_ORDER.get(ly, 99)):
        print(f"  {layer}: {len(by_layer[layer])} tasks", file=sys.stderr)
    print(f"\nOutput: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
