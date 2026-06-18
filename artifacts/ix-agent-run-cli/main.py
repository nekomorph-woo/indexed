#!/usr/bin/env python3
"""ix-agent-run-cli — 按 manifest 统一执行 ix-*-agent（tool + thinking）。

定时功能已移至 ix-schedule-cli（artifacts/ix-schedule-cli/）。
"""

from __future__ import annotations

import argparse
import json
import sys

from config import IX_AGENTS_ROOT
from runner import execute, load_manifest, load_defaults


def _parse_set(items: list[str]) -> dict:
    out = {}
    for item in items:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"--set 需要 key=value，收到: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def cmd_params(args: argparse.Namespace) -> int:
    """阶段 A：读 manifest params + defaults，展示参数需求清单。

    AI（或用户）执行 agent 前先跑这个，了解需要哪些输入。
    """
    agent = args.agent
    agent_root = IX_AGENTS_ROOT / agent
    if not agent_root.is_dir():
        print(f"[error] agent 目录不存在: {agent_root}", file=sys.stderr)
        return 1

    manifest = load_manifest(agent)
    defaults = load_defaults(agent_root)
    raw_params = manifest.get("params") or []

    if not raw_params:
        print(f"{agent} 无参数声明（manifest params 为空）")
        return 0

    if args.json:
        # JSON 输出（供 AI 程序化消费）
        result = []
        for spec in raw_params:
            name = spec.get("name", "")
            required = spec.get("required", False)
            prompt = spec.get("prompt", "")
            default = spec.get("default")
            default_from = spec.get("default_from")
            current = default
            if default_from:
                # 从 defaults.yaml 提取
                key_parts = default_from.split("#", 1)
                if len(key_parts) == 2 and key_parts[1] in defaults:
                    current = defaults[key_parts[1]]
            if name in defaults:
                current = defaults[name]
            result.append({
                "name": name,
                "required": required,
                "prompt": prompt,
                "current": current,
                "has_default": current is not None,
            })
        print(json.dumps({"agent": agent, "params": result}, ensure_ascii=False, indent=2))
    else:
        # 人类可读表格
        print(f"{agent} 需要以下输入：\n")
        print(f"{'参数':<20} {'必填':<5} {'说明':<35} {'当前值':<25}")
        print("-" * 90)
        for spec in raw_params:
            name = spec.get("name", "")
            required = "✅" if spec.get("required") else "—"
            prompt = spec.get("prompt", "")[:33]
            default = spec.get("default")
            default_from = spec.get("default_from")
            current = default
            source = "(default)"
            if default_from:
                key_parts = default_from.split("#", 1)
                if len(key_parts) == 2 and key_parts[1] in defaults:
                    current = defaults[key_parts[1]]
                    source = f"(from {default_from})"
            if name in defaults:
                current = defaults[name]
                source = "(from defaults.yaml)"
            if current is None and spec.get("required"):
                current_str = "（需用户提供）"
            elif current is None:
                current_str = "—"
            else:
                current_str = f"{current} {source}"
            print(f"{name:<20} {required:<5} {prompt:<35} {current_str:<25}")

        missing = [s.get("name") for s in raw_params
                   if s.get("required") and not s.get("default")
                   and not s.get("default_from")
                   and s.get("name") not in defaults]
        if missing:
            print(f"\n⚠️  缺失必填参数（无默认值）: {', '.join(missing)}")
            print("   请通过 --set key=value 或 --params-json 提供")
        else:
            print("\n✅ 所有必填参数都有值（默认或 defaults.yaml）")
    return 0


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
    run_p.set_defaults(func="run")

    pp = sub.add_parser("params", help="阶段 A：展示 agent 的参数需求清单（不执行）")
    pp.add_argument("--agent", required=True, help="agent 目录名")
    pp.add_argument("--json", action="store_true", help="输出 JSON（供 AI 消费）")
    pp.set_defaults(func="params")

    args = parser.parse_args()

    if args.func == "params":
        return cmd_params(args)

    # run 命令
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
