#!/usr/bin/env python3
"""Tests for hook scripts: graph_nudge, implement_checkpoint, inject_pipeline_state."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent


def run_hook(script_name: str, stdin_data: dict, cwd: str | None = None) -> dict | None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name)],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.stdout.strip():
        return json.loads(result.stdout)
    return None


# --- graph_nudge tests ---


def test_graph_nudge_no_grep():
    out = run_hook("graph_nudge.py", {"tool_input": {"command": "ls -la"}})
    assert out is None


def test_graph_nudge_grep_no_graph(tmp_path):
    out = run_hook(
        "graph_nudge.py", {"tool_input": {"command": "grep foo bar"}}, cwd=str(tmp_path)
    )
    assert out is None


def test_graph_nudge_grep_with_graph(tmp_path):
    graph_dir = tmp_path / ".migration" / "discovery" / "graphify-out"
    graph_dir.mkdir(parents=True)
    (graph_dir / "graph.json").write_text("{}")

    out = run_hook(
        "graph_nudge.py", {"tool_input": {"command": "grep foo bar"}}, cwd=str(tmp_path)
    )
    assert out is not None
    assert "additionalContext" in out["hookSpecificOutput"]
    assert "one-modernizer" in out["hookSpecificOutput"]["additionalContext"]


def test_graph_nudge_malformed_stdin():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "graph_nudge.py")],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


# --- implement_checkpoint tests ---


def test_checkpoint_no_migration_dir(tmp_path):
    out = run_hook(
        "implement_checkpoint.py",
        {"tool_input": {"command": "echo hello"}},
        cwd=str(tmp_path),
    )
    assert out is None


def test_checkpoint_missing_constitution(tmp_path):
    impl_dir = tmp_path / ".migration" / "implement" / "feature-x"
    impl_dir.mkdir(parents=True)

    out = run_hook(
        "implement_checkpoint.py",
        {"tool_input": {"command": "echo implement"}},
        cwd=str(tmp_path),
    )
    assert out is not None
    assert "constitution.md" in out["hookSpecificOutput"]["additionalContext"]


def test_checkpoint_has_constitution_no_specs(tmp_path):
    impl_dir = tmp_path / ".migration" / "implement" / "feature-x"
    impl_dir.mkdir(parents=True)
    (impl_dir / "constitution.md").write_text("# Constitution")

    out = run_hook(
        "implement_checkpoint.py",
        {"tool_input": {"command": "echo implement"}},
        cwd=str(tmp_path),
    )
    # No specs dir yet, so clarifications not required
    assert out is None


def test_checkpoint_has_specs_no_clarifications(tmp_path):
    impl_dir = tmp_path / ".migration" / "implement" / "feature-x"
    specs_dir = impl_dir / "specs"
    specs_dir.mkdir(parents=True)
    (impl_dir / "constitution.md").write_text("# Constitution")
    (specs_dir / "service.json").write_text("{}")

    out = run_hook(
        "implement_checkpoint.py",
        {"tool_input": {"command": "echo implement"}},
        cwd=str(tmp_path),
    )
    assert out is not None
    assert "clarifications.json" in out["hookSpecificOutput"]["additionalContext"]


def test_checkpoint_all_gates_pass(tmp_path):
    impl_dir = tmp_path / ".migration" / "implement" / "feature-x"
    specs_dir = impl_dir / "specs"
    specs_dir.mkdir(parents=True)
    (impl_dir / "constitution.md").write_text("# Constitution")
    (specs_dir / "service.json").write_text("{}")
    (impl_dir / "clarifications.json").write_text("{}")
    (impl_dir / "tasks.json").write_text("{}")
    (impl_dir / "task-log.json").write_text("{}")

    out = run_hook(
        "implement_checkpoint.py",
        {"tool_input": {"command": "echo implement"}},
        cwd=str(tmp_path),
    )
    assert out is None


# --- inject_pipeline_state tests ---


def test_inject_non_our_skill():
    out = run_hook("inject_pipeline_state.py", {"tool_input": {"skill": "some-other"}})
    assert out is None


def test_inject_no_index(tmp_path):
    out = run_hook(
        "inject_pipeline_state.py",
        {"tool_input": {"skill": "discover"}},
        cwd=str(tmp_path),
    )
    assert out is not None
    assert (
        "No .migration/index.json found"
        in out["hookSpecificOutput"]["additionalContext"]
    )


def test_inject_with_index(tmp_path):
    migration_dir = tmp_path / ".migration"
    migration_dir.mkdir()
    index = {
        "pipeline": {
            "discover": {
                "status": "completed",
                "outputs": {"graph": ".migration/discovery/graphify-out/graph.json"},
            }
        },
        "features": {},
        "active_feature": None,
    }
    (migration_dir / "index.json").write_text(json.dumps(index))

    out = run_hook(
        "inject_pipeline_state.py",
        {"tool_input": {"skill": "assess"}},
        cwd=str(tmp_path),
    )
    assert out is not None
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "discover: completed" in ctx


def test_inject_malformed_stdin():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "inject_pipeline_state.py")],
        input="{{broken",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
