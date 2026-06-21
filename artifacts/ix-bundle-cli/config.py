"""ix-bundle-cli 路径与基线清单常量。"""

from __future__ import annotations

from pathlib import Path

# indexed 仓库根（artifacts/ix-bundle-cli/ → artifacts/ → indexed/）
ARTIFACTS_ROOT = Path(__file__).resolve().parent.parent
INDEXED_ROOT = ARTIFACTS_ROOT.parent

VERSION_FILE = INDEXED_ROOT / "VERSION"

# 基线必含清单（CLI-only 用户拿到这些就能跑起来）。
# 用「白名单」而非「黑名单」：复制时只 copy 这些路径，其他一律跳过。
# 路径相对 INDEXED_ROOT；目录用尾部 / 标识（实际写 'dir/'）。
BASELINE_FILES = [
    # 根元文件
    "CLAUDE.md",
    "VERSION",
    ".gitignore",
    # .claude/ 配置（rules / settings / hooks / skills）
    ".claude/rules",
    ".claude/settings.json",
    ".claude/hooks",
    ".claude/skills",
    ".claude/plugins",
    # _shared 规范/模板/设计语言
    "_shared/specs",
    "_shared/templates",
    "_shared/design-languages",
    # 基线 5 个 CLI（含自身）
    "artifacts/ix-agent-run-cli",
    "artifacts/ix-workspace-index-cli",
    "artifacts/ix-init-cli",
    "artifacts/ix-schedule-cli",
    "artifacts/ix-bundle-cli",
    # artifacts 桶级元文件
    "artifacts/OVERVIEW.md",
    "artifacts/capabilities.md",
    # ix-agents 桶级（不含用户 agent 子目录）
    "ix-agents/OVERVIEW.md",
    "ix-agents/registry.md",
    # reports / research 桶级 OVERVIEW（骨架）
    "reports/OVERVIEW.md",
    "research/OVERVIEW.md",
]

# app-bundle 额外保留（让 .app 内嵌基线知道 GUI 框架设施定位）
APP_BUNDLE_EXTRA = [
    "ix-gui/OVERVIEW.md",
    "ix-gui/SPEC.yaml",
]

# 复制时跳过的子目录名（即使白名单目录内也要剔除）
SKIP_DIRS = {
    "__pycache__",
    "node_modules",
    "target",
    "dist",
    ".vite",
    ".git",
    "runs",  # ix-agents/<agent>/runs/ 执行历史
    "output",  # artifacts/*/output/
}

# 复制时跳过的文件名模式
SKIP_FILES = {
    ".DS_Store",
    ".env",
    ".indexed-initialized",
}

SKIP_FILE_SUFFIXES = (
    ".pyc",
    ".pyo",
    ".tsbuildinfo",
)


def is_skipped(name: str, is_dir: bool) -> bool:
    """复制时是否跳过该条目。"""
    if is_dir:
        return name in SKIP_DIRS
    if name in SKIP_FILES:
        return True
    if name.endswith(SKIP_FILE_SUFFIXES):
        return True
    if name.startswith(".env."):  # .env.local / .env.prod 等
        return True
    return False
