#!/usr/bin/env python3
"""ix-schedule-cli — 跨平台定时执行器（Windows schtasks / macOS launchd）。

子命令：
    register   注册 job 到系统调度器
    unregister 从系统调度器移除 job
    list       列出 registry 里的 job
    run        手动触发 job（调 ix-agent-run-cli）
    status     查看平台 + 已注册任务
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from config import AGENT_RUN_CLI, INDEXED_ROOT, LOGS_DIR, REGISTRY_PATH, _PKG
from registry import get_job, list_jobs, update_job
from providers import get_provider, supported_platform


def _build_run_command(job_id: str) -> str:
    """构建系统调度器触发时执行的命令（Windows schtasks /TR 格式）。"""
    python = sys.executable
    main_py = str(_PKG / "main.py")
    return f'"{python}" "{main_py}" run --job-id {job_id}'


def cmd_register(args: argparse.Namespace) -> int:
    job = get_job(args.job_id)
    if not job:
        print(f"[error] registry 中未找到 job: {args.job_id}", file=sys.stderr)
        print(f"        请先在 {REGISTRY_PATH} 中登记 job", file=sys.stderr)
        return 1

    if not job.get("enabled", True):
        print(f"[error] job {args.job_id} 已禁用（enabled: false），无法注册", file=sys.stderr)
        return 1

    provider = get_provider()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # macOS 用 ProgramArguments 数组，Windows 用命令字符串
        if hasattr(provider, "get_run_command_args"):
            python_path = sys.executable
            main_py = str(_PKG / "main.py")
            run_args = provider.get_run_command_args(python_path, main_py, args.job_id)
            task_name = provider.register(job, run_args)
        else:
            run_cmd = _build_run_command(args.job_id)
            task_name = provider.register(job, run_cmd)
    except Exception as e:
        print(f"[error] 注册失败: {e}", file=sys.stderr)
        return 1

    update_job(args.job_id, registered=True, platform_task_name=task_name)
    print(f"[done] job {args.job_id} 已注册到 {supported_platform()}")
    print(f"  任务名: {task_name}")
    sched = job.get("schedule", {})
    print(f"  调度: {sched.get('kind', 'daily')} @ {sched.get('time', '09:00')}")
    return 0


def cmd_unregister(args: argparse.Namespace) -> int:
    job = get_job(args.job_id)
    if not job:
        print(f"[error] registry 中未找到 job: {args.job_id}", file=sys.stderr)
        return 1

    task_name = job.get("platform_task_name", "")
    if not task_name:
        print(f"[warn] job {args.job_id} 未注册过（无 platform_task_name）")
        update_job(args.job_id, registered=False, platform_task_name="")
        return 0

    provider = get_provider()
    try:
        provider.unregister(task_name)
    except Exception as e:
        print(f"[warn] 注销时出错（可能已不存在）: {e}", file=sys.stderr)

    update_job(args.job_id, registered=False, platform_task_name="")
    print(f"[done] job {args.job_id} 已从系统调度器移除")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    jobs = list_jobs(enabled_only=args.enabled_only)
    if not jobs:
        print(f"（registry 为空，在 {REGISTRY_PATH} 中登记 job）")
        return 0
    print(f"registry: {REGISTRY_PATH}\n")
    print(f"{'ID':<25} {'Agent':<25} {'调度':<20} {'启用':<5} {'已注册':<6}")
    print("-" * 85)
    for job in jobs:
        sched = job.get("schedule", {})
        kind = sched.get("kind", "?")
        time = sched.get("time", "?")
        days = ""
        if kind == "weekly" and sched.get("weekdays"):
            days = f" [{','.join(sched['weekdays'])}]"
        sched_str = f"{kind} @ {time}{days}"
        print(
            f"{job.get('id', '?'):<25} "
            f"{job.get('agent', '?'):<25} "
            f"{sched_str:<20} "
            f"{'是' if job.get('enabled', True) else '否':<5} "
            f"{'是' if job.get('registered', False) else '否':<6}"
        )
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """手动触发 job（系统调度器也会调这个子命令）。"""
    job = get_job(args.job_id)
    if not job:
        print(f"[error] registry 中未找到 job: {args.job_id}", file=sys.stderr)
        return 1

    agent = job.get("agent", "")
    if not agent:
        print(f"[error] job {args.job_id} 未指定 agent", file=sys.stderr)
        return 1

    params = job.get("params", {})
    params_json = json.dumps(params, ensure_ascii=False) if params else "{}"

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] 定时触发 job={args.job_id} → agent={agent}")

    cmd = [
        sys.executable, "-u",  # -u: unbuffered（launchd 无 TTY 时不卡缓冲）
        str(AGENT_RUN_CLI),
        "run",
        "--agent", agent,
        "--trigger", "scheduled",
        "--params-json", params_json,
    ]

    try:
        # 用 Popen + 实时转发避免 launchd 下 subprocess stdout 死锁
        proc = subprocess.Popen(
            cmd,
            cwd=str(INDEXED_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in proc.stdout:
            print(line, end="", flush=True)
        proc.wait()
        return proc.returncode
    except FileNotFoundError:
        print(f"[error] 找不到 ix-agent-run-cli: {AGENT_RUN_CLI}", file=sys.stderr)
        return 1


def cmd_status(_: argparse.Namespace) -> int:
    print(f"平台: {supported_platform()}")
    print(f"registry: {REGISTRY_PATH}")
    print(f"agent-run-cli: {AGENT_RUN_CLI}")
    print()

    provider = get_provider()
    tasks = provider.list_tasks()
    if not tasks:
        print("系统调度器: 无已注册的 indexed 任务")
    else:
        print(f"系统调度器: {len(tasks)} 个已注册任务")
        for t in tasks:
            print(f"  - {t['name']} (id: {t.get('id', '?')})")

    # registry 概览
    jobs = list_jobs()
    if jobs:
        print(f"\nregistry: {len(jobs)} 个 job")
    else:
        print("\nregistry: 空")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ix-schedule-cli — 跨平台定时执行器"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pr = sub.add_parser("register", help="注册 job 到系统调度器")
    pr.add_argument("--job-id", required=True, help="registry.yaml 中的 job ID")
    pr.set_defaults(func=cmd_register)

    pu = sub.add_parser("unregister", help="从系统调度器移除 job")
    pu.add_argument("--job-id", required=True)
    pu.set_defaults(func=cmd_unregister)

    pl = sub.add_parser("list", help="列出 registry 里的 job")
    pl.add_argument("--enabled-only", action="store_true")
    pl.set_defaults(func=cmd_list)

    prun = sub.add_parser("run", help="手动触发 job（调 ix-agent-run-cli）")
    prun.add_argument("--job-id", required=True)
    prun.set_defaults(func=cmd_run)

    ps = sub.add_parser("status", help="查看平台 + 已注册任务")
    ps.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
