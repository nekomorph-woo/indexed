"""ix-init-cli 路径解析。"""

from __future__ import annotations

from pathlib import Path

_PKG = Path(__file__).resolve().parent
INDEXED_ROOT = _PKG.parent.parent
RULES_DIR = INDEXED_ROOT / ".claude" / "rules"
GIT_WORKFLOW_RULE = RULES_DIR / "git-workflow.md"
CLAUDE_MD = INDEXED_ROOT / "CLAUDE.md"
VERSION_FILE = INDEXED_ROOT / "VERSION"
GITIGNORE = INDEXED_ROOT / ".gitignore"
