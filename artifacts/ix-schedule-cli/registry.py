"""registry.yaml 读写：job 的增删查改。"""

from __future__ import annotations

import re
from pathlib import Path

from config import REGISTRY_PATH

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _load_yaml_file(path: Path) -> dict:
    """读 YAML 文件；无 PyYAML 时用简易解析（仅提取顶层 jobs 列表的 id 字段）。"""
    if not path.is_file():
        return {"jobs": []}
    if yaml is not None:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if "jobs" not in data:
            data["jobs"] = []
        return data
    # 降级：简易解析（足够 list/get_job 工作；add/remove/update 需 PyYAML）
    raw = path.read_text(encoding="utf-8")
    jobs = []
    current_job: dict | None = None
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("- id:"):
            if current_job:
                jobs.append(current_job)
            current_job = {"id": line.split("id:", 1)[1].strip()}
        elif current_job and ":" in line and not line.startswith("#"):
            key, _, val = line.partition(":")
            current_job[key.strip()] = val.strip().strip('"').strip("'")
    if current_job:
        jobs.append(current_job)
    return {"jobs": jobs}


def _save_yaml_file(path: Path, data: dict) -> None:
    """保存 YAML 文件；无 PyYAML 时报错（写操作需要完整 YAML 序列化）。"""
    if yaml is not None:
        path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
    else:
        raise RuntimeError(
            "写 registry.yaml 需要 PyYAML。请运行 pip install pyyaml"
        )


def load_registry() -> dict:
    """加载 registry.yaml；不存在则返回空骨架。"""
    return _load_yaml_file(REGISTRY_PATH)


def save_registry(data: dict) -> None:
    """保存 registry.yaml。"""
    _save_yaml_file(REGISTRY_PATH, data)


def list_jobs(enabled_only: bool = False) -> list[dict]:
    """列出所有 job。"""
    data = load_registry()
    jobs = data.get("jobs", [])
    if enabled_only:
        jobs = [j for j in jobs if j.get("enabled", True)]
    return jobs


def get_job(job_id: str) -> dict | None:
    """按 ID 查找 job。"""
    for job in list_jobs():
        if job.get("id") == job_id:
            return job
    return None


def update_job(job_id: str, **fields) -> bool:
    """更新 job 的字段，返回是否找到并更新。"""
    data = load_registry()
    for job in data["jobs"]:
        if job.get("id") == job_id:
            job.update(fields)
            save_registry(data)
            return True
    return False


def add_job(job: dict) -> None:
    """添加 job。"""
    data = load_registry()
    data["jobs"].append(job)
    save_registry(data)


def remove_job(job_id: str) -> bool:
    """删除 job，返回是否找到并删除。"""
    data = load_registry()
    original = len(data["jobs"])
    data["jobs"] = [j for j in data["jobs"] if j.get("id") != job_id]
    if len(data["jobs"]) < original:
        save_registry(data)
        return True
    return False
