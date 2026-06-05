#!/usr/bin/env python3
"""PreToolUse hook (Skill matcher): inject pipeline state when our skills are triggered.

When any one-modernizer skill is invoked, reads .migration/index.json and injects
the full pipeline state as additionalContext — so the skill knows what's been done,
where outputs live, and what feature is active.
"""

import json
import sys
from pathlib import Path


OUR_SKILLS = {"discover", "assess", "decompose", "architect", "implement", "validate"}


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input", data)
        skill_name = tool_input.get("skill", "")
    except Exception:
        return

    # Only fire for our skills (handle "one-modernizer:skillname" format too)
    clean_name = skill_name.split(":")[-1] if ":" in skill_name else skill_name
    if clean_name not in OUR_SKILLS:
        return

    index_path = Path(".migration/index.json")
    if not index_path.exists():
        # No index yet — inject a hint to create one
        nudge = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    "one-modernizer pipeline: No .migration/index.json found. "
                    "This is the first run. After completing this skill, "
                    "create .migration/index.json to track pipeline state for subsequent skills. "
                    "Use the MigrationIndex class from skills/discover/scripts/migration_index.py."
                ),
            }
        }
        print(json.dumps(nudge))
        return

    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    # Build context string with relevant state for the triggered skill
    lines = ["## Pipeline State (from .migration/index.json)"]
    lines.append("")

    # Pipeline progress
    pipeline = index.get("pipeline", {})
    step_order = [
        "discover",
        "assess",
        "decompose",
        "architect",
        "implement",
        "validate",
    ]
    for step in step_order:
        info = pipeline.get(step, {})
        status = info.get("status", "pending")
        icon = {"completed": "✓", "in_progress": "→", "failed": "✗"}.get(status, "○")
        lines.append(f"  {icon} {step}: {status}")
        outputs = info.get("outputs", {})
        if outputs:
            for key, path in outputs.items():
                lines.append(f"      {key}: {path}")

    # Active feature
    active = index.get("active_feature")
    if active:
        lines.append("")
        lines.append(f"**Active feature**: {active}")

    # Feature artifacts
    features = index.get("features", {})
    if features:
        lines.append("")
        lines.append(f"## Features ({len(features)})")
        for name, info in features.items():
            stage = info.get("stage", "?")
            strategy = info.get("strategy", "?")
            lines.append(f"  - **{name}**: stage={stage}, strategy={strategy}")
            artifacts = info.get("artifacts", {})
            if artifacts:
                for key, path in artifacts.items():
                    lines.append(f"      {key}: {path}")

    # Predecessor outputs relevant to the current skill
    lines.append("")
    lines.append(f"## Relevant Paths for `{clean_name}`")

    if clean_name == "assess":
        disc_out = pipeline.get("discover", {}).get("outputs", {})
        if disc_out:
            lines.append(f"  Discovery output: {disc_out}")

    elif clean_name == "decompose":
        if active and active in features:
            feat = features[active]
            assess_path = feat.get("artifacts", {}).get("assessment")
            if assess_path:
                lines.append(f"  Feature assessment: {assess_path}")

    elif clean_name == "architect":
        if active and active in features:
            feat = features[active]
            spec_path = feat.get("artifacts", {}).get("spec_json")
            if spec_path:
                lines.append(f"  Spec JSON: {spec_path}")

    elif clean_name == "implement":
        if active and active in features:
            feat = features[active]
            for key in ("spec_json", "blueprint_json", "mapping_json", "scaffold_json"):
                path = feat.get("artifacts", {}).get(key)
                if path:
                    lines.append(f"  {key}: {path}")

    elif clean_name == "validate":
        if active and active in features:
            feat = features[active]
            target_dir = feat.get("artifacts", {}).get("target_dir")
            if target_dir:
                lines.append(f"  Generated project: {target_dir}")
            else:
                lines.append(
                    "  ⚠ No target_dir registered — search ./target/ or ask user"
                )
            for key in ("spec_json", "blueprint_json"):
                path = feat.get("artifacts", {}).get(key)
                if path:
                    lines.append(f"  {key}: {path}")

    # Instructions
    lines.append("")
    lines.append("**After completing this skill**, update .migration/index.json:")
    lines.append(f"  - Set pipeline.{clean_name}.status = 'completed'")
    lines.append(
        f"  - Set pipeline.{clean_name}.outputs.<key> = <path> for each output produced"
    )
    if clean_name in ("decompose", "architect", "implement"):
        lines.append(
            f"  - Update features.{active or '<name>'}.artifacts with new paths"
        )
        lines.append(
            f"  - Update features.{active or '<name>'}.stage = '{clean_name}d'"
        )

    context = "\n".join(lines)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
