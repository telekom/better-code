---
name: setup
description: "Install and validate the one-modernizer environment. Creates venv, installs the CLI, detects host/OS. Run on first use or when something seems broken."
---

# Setup Environment

Checks the environment and installs what's missing.

## Step 1: Diagnose & Install

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/diagnose.py
```

Auto-fixes:

| Check              | Action                       |
| ------------------ | ---------------------------- |
| venv missing       | Creates it                   |
| CLI not installed  | Installs graphifyy from PyPI |
| Windows long paths | Enables via git config       |

Cannot auto-fix (reports to user):

| Check                                | User action needed      |
| ------------------------------------ | ----------------------- |
| Python < 3.10                        | Install from python.org |
| output-styles/goal-driven.md missing | Check git status        |

## Step 2: Confirm

One-line status: ready or list of unresolved issues.
