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
INIT_MARKER = INDEXED_ROOT / ".indexed-initialized"

# 标记区文件（update 时需要保护用户区）
MARKER_FILES = [
    CLAUDE_MD,
    GIT_WORKFLOW_RULE,
    INDEXED_ROOT / "artifacts" / "capabilities.md",
    INDEXED_ROOT / "artifacts" / "OVERVIEW.md",
    INDEXED_ROOT / "ix-agents" / "registry.md",
    INDEXED_ROOT / "ix-agents" / "OVERVIEW.md",
    INDEXED_ROOT / "research" / "OVERVIEW.md",
]

# 基线 cli 目录名（update 时整体覆盖；用户 cli 不动）
BASELINE_CLIS = {"ix-agent-run-cli", "ix-workspace-index-cli", "ix-init-cli"}

# 用户内容目录（update 时整体跳过）
USER_BUCKETS = {"research", "reports"}
