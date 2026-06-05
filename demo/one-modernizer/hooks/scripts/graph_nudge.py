#!/usr/bin/env python3
"""PreToolUse hook: nudge Claude to use the knowledge graph instead of grepping."""

import json
import sys
from pathlib import Path


def main():
    try:
        data = json.load(sys.stdin)
        cmd = data.get("tool_input", data).get("command", "")
    except Exception:
        return

    search_keywords = ("grep", "rg ", "find ", "fd ")
    if not any(kw in cmd for kw in search_keywords):
        return

    graph = Path(".migration/discovery/graphify-out/graph.json")
    if not graph.exists():
        return

    nudge = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "one-modernizer: Knowledge graph exists at .migration/discovery/graphify-out/graph.json. "
                "Use one-modernizer CLI for precise navigation instead of grepping: "
                'one-modernizer query "<question>" --graph .migration/discovery/graphify-out/graph.json, '
                'one-modernizer path "A" "B" --graph .migration/discovery/graphify-out/graph.json, '
                'one-modernizer explain "<concept>" --graph .migration/discovery/graphify-out/graph.json. '
                "Also read .migration/discovery/graphify-out/GRAPH_REPORT.md for god nodes and community structure."
            ),
        }
    }
    print(json.dumps(nudge))


if __name__ == "__main__":
    main()
