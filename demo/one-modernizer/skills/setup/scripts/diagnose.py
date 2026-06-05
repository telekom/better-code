#!/usr/bin/env python3
"""Diagnose and fix the one-modernizer plugin environment.

Checks Python, venv, CLI, host, OS, output style. Automatically installs
what's missing where possible. Exits 0 if everything is OK after fixes.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Pinned graphify engine version (published as `graphifyy` on PyPI).
# Keep in sync with hooks/scripts/setup.py.
GRAPHIFYY_VERSION = "0.7.10"


def detect_os():
    s = platform.system()
    return {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}.get(s, s.lower())


def detect_host():
    if os.getenv("JETBRAINS_IDE"):
        return "jetbrains"
    if os.getenv("TERM_PROGRAM") == "vscode" or os.getenv("VSCODE_PID"):
        return "vscode"
    if os.getenv("CLAUDE_PLUGIN_ROOT"):
        return "claude-code"
    return "unknown"


def is_windows():
    return detect_os() == "windows"


def venv_bin(venv_path: Path, name: str) -> Path:
    if is_windows():
        return venv_path / "Scripts" / (name + ".exe")
    return venv_path / "bin" / name


# --- Checks + Auto-fix ---


def fix_python() -> dict:
    v = sys.version_info
    if v >= (3, 10):
        return {"ok": True, "version": f"{v.major}.{v.minor}.{v.micro}"}

    return {
        "ok": False,
        "version": f"{v.major}.{v.minor}.{v.micro}",
        "error": f"Python 3.10+ required (found {v.major}.{v.minor}).",
        "action": "Install from https://python.org/downloads/ — cannot auto-fix.",
    }


def fix_venv() -> dict:
    data_dir = os.getenv("CLAUDE_PLUGIN_DATA")
    if not data_dir:
        return {
            "ok": False,
            "error": "CLAUDE_PLUGIN_DATA not set.",
            "action": "Cannot create venv without plugin data dir.",
        }

    venv_path = Path(data_dir) / "venv"
    pip = venv_bin(venv_path, "pip")
    cli = venv_bin(venv_path, "one-modernizer")

    if not venv_path.exists():
        print("  Creating venv...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    if not cli.exists():
        print("  Installing one-modernizer CLI (graphifyy)...", file=sys.stderr)
        subprocess.run(
            [
                str(pip),
                "install",
                "--quiet",
                "--force-reinstall",
                f"graphifyy=={GRAPHIFYY_VERSION}",
            ],
            check=True,
        )
        # Create symlink (graphify → one-modernizer)
        graphify = venv_bin(venv_path, "graphify")
        if graphify.exists() and not cli.exists():
            cli.symlink_to(graphify)

    if cli.exists():
        return {"ok": True, "path": str(venv_path), "cli": str(cli)}

    return {
        "ok": False,
        "error": "CLI install failed.",
        "action": f"Check network access to PyPI for graphifyy=={GRAPHIFYY_VERSION}",
    }


def fix_git() -> dict:
    git = shutil.which("git")
    if not git:
        return {
            "ok": False,
            "error": "git not in PATH.",
            "action": "Install git for your OS.",
        }
    return {"ok": True, "path": git}


def fix_windows_longpaths() -> dict:
    if not is_windows():
        return {"ok": True, "skipped": True}

    result = subprocess.run(
        ["git", "config", "--get", "core.longpaths"],
        capture_output=True,
        text=True,
    )
    if result.stdout.strip().lower() == "true":
        return {"ok": True}

    print("  Enabling git long paths...", file=sys.stderr)
    subprocess.run(["git", "config", "--global", "core.longpaths", "true"], check=True)
    return {"ok": True, "fixed": True}


def fix_output_style() -> dict:
    plugin_root = os.getenv("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        return {"ok": False, "error": "CLAUDE_PLUGIN_ROOT not set."}

    style_path = Path(plugin_root) / "output-styles" / "goal-driven.md"
    if style_path.exists():
        return {"ok": True, "path": str(style_path)}

    return {
        "ok": False,
        "error": "output-styles/goal-driven.md missing.",
        "action": "File should exist in the plugin repo — check git status.",
    }


def main():
    host = detect_host()
    os_name = detect_os()

    results = {
        "os": os_name,
        "host": host,
        "python": fix_python(),
        "venv": fix_venv(),
        "git": fix_git(),
        "windows_longpaths": fix_windows_longpaths(),
        "output_style": fix_output_style(),
    }

    issues = []
    for name, result in results.items():
        if (
            isinstance(result, dict)
            and not result.get("ok", True)
            and not result.get("skipped")
        ):
            issues.append({"check": name, **result})

    print("# one-modernizer setup")
    print("")
    print(
        f"OS: {os_name} ({platform.machine()})  |  Host: {host}  |  Python: {sys.version_info.major}.{sys.version_info.minor}"
    )
    print("")

    if not issues:
        print("All checks passed. Environment ready.")
    else:
        print(f"{len(issues)} issue(s) could not be auto-fixed:")
        print("")
        for issue in issues:
            print(
                f"  [{issue['check']}] {issue.get('error', '')} → {issue.get('action', '')}"
            )

    if host == "unknown":
        print("")
        print(
            "Host not recognized as Claude Code. Hooks and output-styles won't apply."
        )

    # Persist for other scripts
    data_dir = os.getenv("CLAUDE_PLUGIN_DATA")
    if data_dir:
        out = Path(data_dir) / "diagnostics.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    sys.exit(0 if not issues else 1)


if __name__ == "__main__":
    main()
