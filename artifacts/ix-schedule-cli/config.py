"""ix-schedule-cli 路径解析。"""

from __future__ import annotations

from pathlib import Path
import sys

_PKG = Path(__file__).resolve().parent
INDEXED_ROOT = _PKG.parent.parent
ARTIFACTS_ROOT = INDEXED_ROOT / "artifacts"
IX_AGENTS_ROOT = INDEXED_ROOT / "ix-agents"
AGENT_RUN_CLI = ARTIFACTS_ROOT / "ix-agent-run-cli" / "main.py"
REGISTRY_PATH = _PKG / "registry.yaml"
LOGS_DIR = _PKG / "logs"


def is_on_external_volume() -> bool:
    """检测 INDEXED_ROOT 是否在外部卷（/Volumes/）上。

    macOS TCC 会阻止 launchd 进程访问外部卷上的文件，
    导致定时任务注册后无法执行。
    """
    return "/Volumes/" in str(INDEXED_ROOT) or "/mnt/" in str(INDEXED_ROOT) or "/media/" in str(INDEXED_ROOT)

