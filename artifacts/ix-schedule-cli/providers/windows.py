"""Windows provider：通过 schtasks 注册/注销/查询定时任务。"""

from __future__ import annotations

import subprocess
import sys

# 星期映射（schtasks 用 MON/TUE/WED/THU/FRI/SAT/SUN）
WEEKDAY_MAP = {
    "MON": "MON", "TUE": "TUE", "WED": "WED", "THU": "THU",
    "FRI": "FRI", "SAT": "SAT", "SUN": "SUN",
}

PLATFORM_NAME = "Windows"
TASK_PREFIX = "indexed-"


def _schtasks(args: list[str]) -> tuple[int, str]:
    """执行 schtasks 命令，返回 (returncode, output)。"""
    proc = subprocess.run(
        ["schtasks"] + args,
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def register(job: dict, run_command: str) -> str:
    """注册 job 到 Windows 任务计划程序。返回系统任务名。

    run_command: 系统调度器触发时执行的完整命令
    job: {id, schedule: {kind, time, weekdays}}
    """
    job_id = job["id"]
    task_name = f"{TASK_PREFIX}{job_id}"
    sched = job.get("schedule", {})
    kind = sched.get("kind", "daily")
    time = sched.get("time", "09:00")

    args = [
        "/Create",
        f"/TN", task_name,
        f"/TR", run_command,
        "/F",  # 强制覆盖
    ]

    if kind == "weekly":
        weekdays = sched.get("weekdays", ["MON"])
        day_str = ",".join(WEEKDAY_MAP.get(d, d) for d in weekdays)
        args.extend(["/SC", "WEEKLY", "/D", day_str, "/ST", time])
    else:
        args.extend(["/SC", "DAILY", "/ST", time])

    code, out = _schtasks(args)
    if code != 0:
        raise RuntimeError(f"schtasks 注册失败: {out}")
    return task_name


def unregister(task_name: str) -> None:
    """从 Windows 任务计划程序移除。"""
    code, out = _schtasks(["/Delete", f"/TN", task_name, "/F"])
    if code != 0 and "无法找到" not in out and "cannot find" not in out.lower():
        raise RuntimeError(f"schtasks 注销失败: {out}")


def list_tasks() -> list[dict]:
    """列出已注册的 indexed 任务。"""
    code, out = _schtasks(["/Query", "/FO", "CSV", "/NH"])
    if code != 0:
        return []
    tasks = []
    for line in out.strip().splitlines():
        parts = line.split('","')
        if len(parts) >= 1:
            name = parts[0].strip('"')
            if name.startswith(TASK_PREFIX):
                tasks.append({"name": name, "id": name[len(TASK_PREFIX):]})
    return tasks
