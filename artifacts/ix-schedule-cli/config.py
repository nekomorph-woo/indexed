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
