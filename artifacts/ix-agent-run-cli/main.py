#!/usr/bin/env python3
"""ix-agent-run-cli — 按 manifest 统一执行 ix-*-agent（tool + thinking）。

定时功能已移至 ix-schedule-cli（artifacts/ix-schedule-cli/）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from config import INDEXED_ROOT, IX_AGENTS_ROOT
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


def cmd_stats(args: argparse.Namespace) -> int:
    """聚合 runs/ 历史，输出最近 N 次执行状态（P2-3 反哺）。"""
    if not IX_AGENTS_ROOT.is_dir():
        print("[stats] 未发现 ix-agents/ 目录")
        return 0

    records: list[dict] = []
    for agent_dir in sorted(IX_AGENTS_ROOT.iterdir()):
        if not agent_dir.is_dir() or not agent_dir.name.startswith("ix-"):
            continue
        if args.agent and agent_dir.name != args.agent:
            continue
        # 优先读 last-run.json（快），没有则扫 runs/（慢）
        last_run_file = agent_dir / "last-run.json"
        if last_run_file.is_file() and not args.agent:
            try:
                data = json.loads(last_run_file.read_text(encoding="utf-8"))
                records.append({
                    "agent": agent_dir.name,
                    "run_id": data.get("run_id", "?"),
                    "status": data.get("status", "?"),
                    "started_at": data.get("started_at", "?"),
                    "ended_at": data.get("ended_at", "?"),
                    "duration_seconds": data.get("duration_seconds"),
                    "steps_completed": data.get("steps_completed", 0),
                    "steps_total": data.get("steps_total", 0),
                    "failed_at_step": data.get("failed_at_step"),
                })
                continue
            except (json.JSONDecodeError, OSError):
                pass
        # 扫描 runs/*/run.yaml（全量历史）
        runs_dir = agent_dir / "runs"
        if not runs_dir.is_dir():
            continue
        for run_dir in sorted(runs_dir.iterdir()):
            run_yaml = run_dir / "run.yaml"
            if not run_yaml.is_file():
                continue
            try:
                data = yaml.safe_load(run_yaml.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            records.append({
                "agent": agent_dir.name,
                "run_id": data.get("run_id", run_dir.name),
                "status": data.get("status", "?"),
                "started_at": data.get("started_at", "?"),
                "ended_at": data.get("completed_at", "?"),
                "duration_seconds": None,
                "steps_completed": len(data.get("steps_completed") or []),
                "steps_total": 0,
                "failed_at_step": data.get("next_step"),
            })

    if not records:
        print(f"[stats] 无执行历史（{args.agent or '所有 agent'} 的 runs/ 为空）")
        return 0

    # 按开始时间倒序
    records.sort(key=lambda r: r["started_at"] or "", reverse=True)
    n = args.last if args.last > 0 else 10
    records = records[:n]

    print(f"最近 {len(records)} 次执行：\n")
    print(f"{'Agent':<25} {'Run ID':<22} {'Status':<11} {'Started':<20} {'Steps':<10} {'Failed':<15}")
    print("-" * 110)
    for r in records:
        started = (r["started_at"] or "?")[:19]
        steps = f"{r['steps_completed']}/{r['steps_total']}" if r["steps_total"] else str(r["steps_completed"])
        failed = r["failed_at_step"] or "-"
        print(
            f"{r['agent']:<25} {r['run_id']:<22} {r['status']:<11} "
            f"{started:<20} {steps:<10} {failed:<15}"
        )

    success = sum(1 for r in records if r["status"] == "completed")
    failed = sum(1 for r in records if r["status"] == "failed")
    rate = (success / len(records)) * 100 if records else 0
    print(f"\n成功率: {success}/{len(records)}（{rate:.0f}%）；失败: {failed}")
    return 0


# 模板文件 → 目标文件 映射（脚手架用）
_AGENT_TEMPLATE_MAP = {
    "manifest.template.yaml": "manifest.yaml",
    "SPEC.template.yaml": "SPEC.yaml",
    "defaults.template.yaml": "config/defaults.yaml",
    "gitignore.template": ".gitignore",
    "paths.template.py": "paths.py",
    "OVERVIEW.md": "OVERVIEW.md",  # 直接复制
}
# run-yaml.example.yaml 是 run.yaml 结构说明文档，由 run-cli 执行时创建真实 run.yaml，不复制

_KEBAB_BUSINESS_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def cmd_new(args: argparse.Namespace) -> int:
    """脚手架：从 _shared/templates/ix-agents/ 复制并替换 <business> 占位符。"""
    business = args.business
    if not _KEBAB_BUSINESS_RE.match(business):
        print(f"[error] --business 必须是 kebab-case（[a-z0-9]+(-[a-z0-9]+)*）: {business}", file=sys.stderr)
        return 1

    agent_name = f"ix-{business}-agent"
    agent_dir = IX_AGENTS_ROOT / agent_name
    if agent_dir.exists():
        print(f"[error] agent 已存在: {agent_dir}", file=sys.stderr)
        return 1

    template_dir = INDEXED_ROOT / "_shared" / "templates" / "ix-agents"
    if not template_dir.is_dir():
        print(f"[error] 模板目录不存在: {template_dir}", file=sys.stderr)
        return 1

    # 创建目录结构
    agent_dir.mkdir(parents=True)
    (agent_dir / "config").mkdir(exist_ok=True)
    (agent_dir / "runs").mkdir(exist_ok=True)

    # 复制 + 替换占位符
    for src_name, dst_name in _AGENT_TEMPLATE_MAP.items():
        src = template_dir / src_name
        if not src.is_file():
            continue
        content = src.read_text(encoding="utf-8")
        content = content.replace("<business>", business)
        dst = agent_dir / dst_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")

    print(f"✅ 已创建 {agent_name}")
    print(f"   目录: {agent_dir.relative_to(INDEXED_ROOT)}")
    print()
    print("下一步:")
    print(f"  1. 跑 search 确认无重复能力:")
    print(f"     python artifacts/ix-workspace-index-cli/main.py search \"<意图关键词>\"")
    print(f"  2. 编辑 manifest.yaml 填 params/steps")
    print(f"  3. 编辑 SPEC.yaml 填 intents/one_liner/domain")
    print(f"  4. 跑 sync 同步索引（PostToolUse hook 会自动触发；或手动跑）")
    print(f"  5. 跑 params 展示输入清单（两阶段 A）:")
    print(f"     python artifacts/ix-agent-run-cli/main.py params --agent {agent_name}")
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

    pstats = sub.add_parser("stats", help="聚合 runs/ 历史，输出最近 N 次执行状态（P2-3 反哺）")
    pstats.add_argument("--agent", help="限定某个 agent（默认全部）")
    pstats.add_argument("--last", type=int, default=10, help="显示最近 N 次（默认 10；--agent 指定时扫描全量）")
    pstats.set_defaults(func="stats")

    pnew = sub.add_parser("new", help="脚手架：从模板创建新 ix-*-agent 目录")
    pnew.add_argument("--business", required=True, help="业务名（kebab-case），如 foo → ix-foo-agent")
    pnew.set_defaults(func="new")

    args = parser.parse_args()

    if args.func == "params":
        return cmd_params(args)

    if args.func == "stats":
        return cmd_stats(args)

    if args.func == "new":
        return cmd_new(args)

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
