#!/usr/bin/env python3
"""Shared module for reading/writing .migration/index.json.

The index tracks the full pipeline state across all skills:
- Which skills have run and their status
- Output paths for each step
- Which features are being migrated
- Current pipeline stage per feature

Every skill imports this to find predecessor outputs and register its own.

Usage:
    from migration_index import MigrationIndex

    idx = MigrationIndex(project_root)
    # Read state
    discovery_path = idx.get_output("discover", "graphify-out")
    # Update state
    idx.set_step_status("assess", "completed")
    idx.set_output("assess", "features", ".migration/assess/features/")
    idx.save()
"""

import json
import sys
from pathlib import Path
from datetime import datetime


_PIPELINE_ORDER = [
    "discover",
    "assess",
    "decompose",
    "architect",
    "implement",
    "validate",
]


class MigrationIndex:
    def __init__(self, project_root: Path | str = "."):
        self.root = Path(project_root).resolve()
        self.path = self.root / ".migration" / "index.json"
        self._data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return self._default()

    def _default(self) -> dict:
        return {
            "version": "1.0",
            "project_root": str(self.root),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "pipeline": {
                step: {"status": "pending", "outputs": {}} for step in _PIPELINE_ORDER
            },
            "features": {},
            "active_feature": None,
        }

    def save(self):
        self._data["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    # --- Pipeline state ---

    def get_step_status(self, step: str) -> str:
        return self._data["pipeline"].get(step, {}).get("status", "pending")

    def set_step_status(self, step: str, status: str):
        if step not in self._data["pipeline"]:
            self._data["pipeline"][step] = {"status": status, "outputs": {}}
        self._data["pipeline"][step]["status"] = status
        self._data["pipeline"][step]["completed_at"] = (
            datetime.utcnow().isoformat() + "Z"
        )

    def get_output(self, step: str, key: str) -> str | None:
        return self._data["pipeline"].get(step, {}).get("outputs", {}).get(key)

    def set_output(self, step: str, key: str, path: str):
        if step not in self._data["pipeline"]:
            self._data["pipeline"][step] = {"status": "pending", "outputs": {}}
        self._data["pipeline"][step]["outputs"][key] = path

    # --- Feature registry ---

    def register_feature(
        self, name: str, modules: list[str] | None = None, strategy: str | None = None
    ):
        if name not in self._data["features"]:
            self._data["features"][name] = {
                "registered_at": datetime.utcnow().isoformat() + "Z",
                "modules": modules or [],
                "strategy": strategy,
                "stage": "assessed",
                "artifacts": {},
            }
        else:
            if modules:
                self._data["features"][name]["modules"] = modules
            if strategy:
                self._data["features"][name]["strategy"] = strategy

    def set_feature_stage(self, name: str, stage: str):
        if name in self._data["features"]:
            self._data["features"][name]["stage"] = stage

    def set_feature_artifact(self, name: str, key: str, path: str):
        if name in self._data["features"]:
            self._data["features"][name]["artifacts"][key] = path

    def get_feature_artifact(self, name: str, key: str) -> str | None:
        return self._data["features"].get(name, {}).get("artifacts", {}).get(key)

    def get_active_feature(self) -> str | None:
        return self._data.get("active_feature")

    def set_active_feature(self, name: str):
        self._data["active_feature"] = name

    def list_features(self) -> dict:
        return self._data.get("features", {})

    # --- Convenience ---

    def get_target_dir(self, feature: str) -> str | None:
        return self.get_feature_artifact(feature, "target_dir")

    def get_spec(self, feature: str) -> str | None:
        return self.get_feature_artifact(feature, "spec_json")

    def get_blueprint(self, feature: str) -> str | None:
        return self.get_feature_artifact(feature, "blueprint_json")

    def get_mapping(self, feature: str) -> str | None:
        return self.get_feature_artifact(feature, "mapping_json")

    def summary(self) -> str:
        lines = ["# Migration Pipeline State", ""]
        for step in _PIPELINE_ORDER:
            status = self.get_step_status(step)
            icon = {"completed": "✓", "in_progress": "→", "failed": "✗"}.get(
                status, "○"
            )
            lines.append(f"  {icon} {step}: {status}")
        lines.append("")
        features = self.list_features()
        if features:
            lines.append(f"## Features ({len(features)})")
            for name, info in features.items():
                lines.append(
                    f"  - {name}: {info.get('stage', '?')} ({info.get('strategy', '?')})"
                )
        return "\n".join(lines)


def init_index(project_root: str = "."):
    """CLI entry point: initialize or display index."""
    idx = MigrationIndex(project_root)
    if not idx.path.exists():
        idx.save()
        print(f"Created: {idx.path}", file=sys.stderr)
    print(idx.summary())


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    init_index(root)
