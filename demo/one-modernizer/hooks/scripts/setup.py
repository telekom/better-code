#!/usr/bin/env python3
"""Install the one-modernizer CLI (graphifyy engine) into the plugin venv.

The knowledge-graph engine is the published `graphifyy` package
(https://github.com/safishamsi/graphify). It is installed from PyPI rather than
vendored, so this plugin stays small and tracks a pinned upstream version.
Reinstalls automatically when GRAPHIFYY_VERSION changes.
"""

import os
import subprocess
import sys
from pathlib import Path

# Pinned graphify engine version. Bump after testing against a newer release.
GRAPHIFYY_VERSION = "0.7.10"

data_dir = Path(os.environ["CLAUDE_PLUGIN_DATA"])

venv = data_dir / "venv"
marker = data_dir / "graphifyy-version.txt"

if marker.exists() and marker.read_text(encoding="utf-8").strip() == GRAPHIFYY_VERSION:
    sys.exit(0)

subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
pip = venv / "bin" / "pip"
subprocess.run(
    [str(pip), "install", "--quiet", "--force-reinstall", f"graphifyy=={GRAPHIFYY_VERSION}"],
    check=True,
)

graphify_bin = venv / "bin" / "graphify"
link = venv / "bin" / "one-modernizer"
link.unlink(missing_ok=True)
link.symlink_to(graphify_bin)

marker.write_text(GRAPHIFYY_VERSION, encoding="utf-8")
