#!/usr/bin/env python3
"""ix-agent-run-cli — 按 manifest 统一执行 ix-*-agent（tool + thinking）。"""

from __future__ import annotations

import argparse
import json
import sys

from runner import execute
from schedule import get_job, list_jobs


def _parse_set(items: list[str]) -> dict:
    out = {}
    for item in items:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"--set 需要 key=value，收到: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _cmd_schedule(args: argparse.Namespace) -> int:
    if args.schedule_cmd == "list":
        jobs = list_jobs(enabled_only=args.enabled_only)
        if not jobs:
            print("(registry.yaml jobs 为空)")
            return 0
        for j in jobs:
            flag = "" if j.get("enabled", True) else " [disabled]"
            print(f"{j.get('id')}{flag}\tagent={j.get('agent')}")
        return 0
    if args.schedule_cmd == "run":
        job = get_job(args.job_id)
        if not job.get("enabled", True):
            print(f"job {args.job_id} enabled=false，跳过")
            return 0
        agent = job.get("agent")
        if not agent:
            print(f"job {args.job_id} 缺少 agent", file=sys.stderr)
            return 1
        overrides = dict(job.get("params") or {})
        run_dir = execute(
            agent_id=agent,
            run_id=None,
            resume=False,
            param_overrides=overrides,
            trigger="scheduled",
            llm_bin=args.llm_bin,
            llm_executor=getattr(args, "llm_executor", None),
            dry_run=args.dry_run,
        )
        print(f"完成: {run_dir}")
        return 0
    print("未知 schedule 子命令", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="按 ix-*-agent/manifest.yaml 执行 steps（tool 子进程；thinking 调 claude -p）",
    )
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="执行单个 agent manifest")
    run_p.add_argument("--agent", required=True, help="agent 目录名，如 ix-weekly-metrics-agent")
    run_p.add_argument("--run-id", help="指定 run-id；默认新建")
    run_p.add_argument("--resume", action="store_true", help="从已有 run 的 next_step 续跑")
    run_p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="覆盖 params")
    run_p.add_argument(
        "--params-json",
        help="JSON 对象字符串，合并到 params",
    )
    run_p.add_argument(
        "--trigger",
        choices=("manual", "scheduled"),
        default="manual",
        help="写入 run.yaml.trigger",
    )
    run_p.add_argument("--llm-bin", help="Claude Code CLI 可执行文件路径（默认 PATH 中的 claude，或 IX_CLAUDE_BIN）")
    run_p.add_argument(
        "--llm-executor",
        default="claude-p",
        help=argparse.SUPPRESS,
    )
    run_p.add_argument("--dry-run", action="store_true", help="只打印将执行的步骤，不调用 shell/agent")

    sch_p = sub.add_parser(
        "schedule",
        help="ix-agents 专用定时（仅读 ix-agents/schedule/registry.yaml）",
    )
    sch_sub = sch_p.add_subparsers(dest="schedule_cmd", required=True)
    sch_list = sch_sub.add_parser("list", help="列出已登记 jobs")
    sch_list.add_argument("--enabled-only", action="store_true")
    sch_run = sch_sub.add_parser("run", help="执行已登记 job（--trigger scheduled）")
    sch_run.add_argument("--job-id", required=True)
    sch_run.add_argument("--llm-bin")
    sch_run.add_argument("--dry-run", action="store_true")

    # 兼容：无子命令时视为 run --agent（旧用法）
    parser.add_argument("--agent", help=argparse.SUPPRESS)
    parser.add_argument("--run-id", help=argparse.SUPPRESS)
    parser.add_argument("--resume", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--set", action="append", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--params-json", help=argparse.SUPPRESS)
    parser.add_argument("--trigger", choices=("manual", "scheduled"), default="manual", help=argparse.SUPPRESS)
    parser.add_argument("--llm-bin", help=argparse.SUPPRESS)
    parser.add_argument("--llm-executor", default="claude-p", help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.command == "schedule":
        return _cmd_schedule(args)

    # 子命令 run 或旧式全局 --agent
    agent = getattr(args, "agent", None)
    if args.command == "run":
        agent = args.agent
    elif not agent:
        parser.error("请使用: main.py run --agent <id>  或  main.py schedule run --job-id <id>")

    overrides = _parse_set(getattr(args, "set", None) or [])
    pj = getattr(args, "params_json", None)
    if pj:
        overrides.update(json.loads(pj))

    try:
        run_dir = execute(
            agent_id=agent,
            run_id=getattr(args, "run_id", None),
            resume=getattr(args, "resume", False),
            param_overrides=overrides,
            trigger=getattr(args, "trigger", "manual"),
            llm_bin=getattr(args, "llm_bin", None),
            llm_executor=getattr(args, "llm_executor", None),
            dry_run=getattr(args, "dry_run", False),
        )
    except (FileNotFoundError, KeyError, RuntimeError, ValueError) as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    print(f"完成: {run_dir}")
    print(f"output: {run_dir / 'output'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
