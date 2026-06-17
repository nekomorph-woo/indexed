"""ix-agents/schedule/registry.yaml — list / run registered jobs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from config import INDEXED_ROOT

SCHEDULE_DIR = INDEXED_ROOT / "ix-agents" / "schedule"
REGISTRY_PATH = SCHEDULE_DIR / "registry.yaml"


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.is_file():
        raise FileNotFoundError(f"未找到 {REGISTRY_PATH}")
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def list_jobs(*, enabled_only: bool = False) -> list[dict[str, Any]]:
    jobs = load_registry().get("jobs") or []
    if enabled_only:
        jobs = [j for j in jobs if j.get("enabled", True)]
    return jobs


def get_job(job_id: str) -> dict[str, Any]:
    for job in list_jobs():
        if job.get("id") == job_id:
            return job
    raise KeyError(f"registry 中未找到 job id: {job_id}")
