#!/usr/bin/env python3
"""PreToolUse hook: enforce implement skill checkpoints.

When the implement skill is active (detected by .migration/implement/ existing),
nudge the LLM to follow required checkpoints before proceeding.
"""

import json
import sys
from pathlib import Path


def find_implement_dir() -> Path | None:
    migration = Path(".migration/implement")
    if not migration.exists():
        return None
    features = [d for d in migration.iterdir() if d.is_dir()]
    return features[0] if features else None


def check_gates(impl_dir: Path) -> str | None:
    constitution = impl_dir / "constitution.md"
    specs_dir = impl_dir / "specs"
    clarifications = impl_dir / "clarifications.json"
    tasks = impl_dir / "tasks.json"
    task_log = impl_dir / "task-log.json"

    if not constitution.exists():
        return (
            "CHECKPOINT: constitution.md does not exist yet. "
            "You MUST write the constitution (Phase 1, Step 2) before generating any code. "
            "Define naming conventions, layer responsibilities, and quality rules first."
        )

    # Phase 3 (Clarify) only required after Phase 2 (Specify) has produced specs
    if (
        specs_dir.exists()
        and list(specs_dir.glob("*.json"))
        and not clarifications.exists()
    ):
        return (
            "CHECKPOINT: clarifications.json does not exist yet. "
            "You MUST resolve ambiguities (Phase 3) before proceeding to planning/tasks."
        )

    if clarifications.exists() and not tasks.exists():
        if specs_dir.exists() and list(specs_dir.glob("*.json")):
            return (
                "CHECKPOINT: tasks.json does not exist. "
                "Run scripts/generate_tasks.py to produce the ordered task list (Phase 5, Step 6) "
                "before generating code files."
            )

    if tasks.exists() and not task_log.exists():
        return (
            "CHECKPOINT: task-log.json does not exist yet. "
            "Initialize the task log before executing tasks."
        )

    return None


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input", data)
        command = tool_input.get("command", "")
    except Exception:
        return

    if "implement" not in command and "target/" not in command:
        impl_dir = find_implement_dir()
        if impl_dir is None:
            return

    impl_dir = find_implement_dir()
    if impl_dir is None:
        return

    nudge = check_gates(impl_dir)
    if nudge:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": f"one-modernizer implement: {nudge}",
            }
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
