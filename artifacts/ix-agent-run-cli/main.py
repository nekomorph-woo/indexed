#!/usr/bin/env python3
"""ix-agent-run-cli — 按 manifest 统一执行 ix-*-agent（tool + thinking）。

定时功能已移至 ix-schedule-cli（artifacts/ix-schedule-cli/）。
"""

from __future__ import annotations

import argparse
import json
import sys

from runner import execute


def _parse_set(items: list[str]) -> dict:
    out = {}
    for item in items:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"--set 需要 key=value，收到: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="按 ix-*-agent/manifest.yaml 执行 steps（tool 子进程；thinking 调 claude -p）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

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

    args = parser.parse_args()

    agent = args.agent

    overrides = _parse_set(args.set or [])
    pj = getattr(args, "params_json", None)
    if pj:
        overrides.update(json.loads(pj))

    try:
        run_dir = execute(
            agent_id=agent,
            run_id=args.run_id,
            resume=args.resume,
            param_overrides=overrides,
            trigger=args.trigger,
            llm_bin=args.llm_bin,
            llm_executor=args.llm_executor,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, KeyError, RuntimeError, ValueError) as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    print(f"完成: {run_dir}")
    print(f"output: {run_dir / 'output'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
