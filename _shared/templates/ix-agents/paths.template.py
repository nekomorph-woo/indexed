"""路径解析 — 复制到 ix-agents/ix-<business>-agent/paths.py。

供文档与可选 helper；执行入口为 artifacts/ix-agent-run-cli/main.py。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config"
RUNS = ROOT / "runs"
INDEXED_ROOT = ROOT.parent.parent
ARTIFACTS_ROOT = INDEXED_ROOT / "artifacts"

_TZ = ZoneInfo("Asia/Shanghai")


def new_run_id() -> str:
    """北京时间 run-id：YYYY-MM-DD_HH-mm-ss；同秒冲突由调用方加 -2。"""
    return datetime.now(_TZ).strftime("%Y-%m-%d_%H-%M-%S")


def run_dir(run_id: str) -> Path:
    return RUNS / run_id


def run_yaml(run_id: str) -> Path:
    return run_dir(run_id) / "run.yaml"


def run_inbox(run_id: str) -> Path:
    return run_dir(run_id) / "inbox"


def run_supplements(run_id: str) -> Path:
    return run_dir(run_id) / "supplements"


def run_work_raw(run_id: str) -> Path:
    return run_dir(run_id) / "work" / "raw"


def run_work_thinking(run_id: str) -> Path:
    return run_dir(run_id) / "work" / "thinking"


def run_output(run_id: str) -> Path:
    return run_dir(run_id) / "output"


def ensure_run_tree(run_id: str) -> Path:
    """创建当次 run 目录树。"""
    base = run_dir(run_id)
    for p in (
        run_inbox(run_id),
        run_supplements(run_id),
        run_work_raw(run_id),
        run_work_thinking(run_id),
        run_output(run_id),
    ):
        p.mkdir(parents=True, exist_ok=True)
    return base
