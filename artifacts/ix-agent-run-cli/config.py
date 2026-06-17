"""工作区与 agent 路径解析。"""

from __future__ import annotations

from pathlib import Path

_PKG = Path(__file__).resolve().parent
INDEXED_ROOT = _PKG.parent.parent
IX_AGENTS_ROOT = INDEXED_ROOT / "ix-agents"
ARTIFACTS_ROOT = INDEXED_ROOT / "artifacts"


def agent_dir(agent_id: str) -> Path:
    return IX_AGENTS_ROOT / agent_id


def manifest_path(agent_id: str) -> Path:
    return agent_dir(agent_id) / "manifest.yaml"
