#!/usr/bin/env python3
"""indexed 索引审计：以 SPEC.yaml 为真相源，校验薄索引页（capabilities.md / registry.md）一致性。"""

from __future__ import annotations

import argparse
import json
import sys

from scanner import WORKSPACE_ROOT, audit_index, audit_governance, discover_agents, discover_clis, manifest_snapshot, search_capabilities, sync_indexes


def _cli_row(c) -> dict:
    return {
        "name": c.name,
        "subcommands": c.subcommands,
        "has_spec_yaml": c.has_spec_yaml,
    }


def cmd_audit(args: argparse.Namespace) -> int:
    clis, agents, issues = audit_index()
    gov_issues = audit_governance()
    issues.extend(gov_issues)
    errors = [i for i in issues if i.level == "error"]
    warns = [i for i in issues if i.level == "warn"]
    ok = not errors

    payload = {
        "ok": ok,
        "workspace": str(WORKSPACE_ROOT),
        "clis": [_cli_row(c) for c in clis],
        "agents": [{"name": a.name, **manifest_snapshot(a)} for a in agents],
        "issues": [
            {"level": i.level, "code": i.code, "message": i.message, "target": i.target}
            for i in issues
        ],
        "agent_info": {a.name: manifest_snapshot(a) for a in agents},
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_human(clis, agents, issues, errors, warns)

    return 1 if args.check and not ok else 0


def _print_human(clis, agents, issues, errors, warns) -> None:
    print(f"indexed 索引审计 @ {WORKSPACE_ROOT}\n")
    print("## 磁盘发现\n")
    print("| CLI | 子命令 | SPEC.yaml |")
    print("|-----|--------|-----------|")
    for c in clis:
        subs = ", ".join(c.subcommands) or "—"
        print(f"| {c.name} | {subs} | {'yes' if c.has_spec_yaml else 'no'} |")
    print()
    print("| Agent | thinking | 步骤摘要 |")
    print("|-------|----------|----------|")
    for a in agents:
        print(
            f"| {a.name} | {'是' if a.has_thinking else '否'} | "
            f"{manifest_snapshot(a)['steps_summary'] or '—'} |"
        )
    print()
    if not issues:
        print("[ok] 未发现索引漂移（SPEC.yaml 与薄索引页一致）\n")
        return
    print(f"## 问题（error {len(errors)} / warn {len(warns)}）\n")
    for i in issues:
        mark = "ERR" if i.level == "error" else "WARN"
        tgt = f" `{i.target}`" if i.target else ""
        print(f"- {mark} **{i.code}**{tgt}: {i.message}")
    print()
    if agents:
        print("## Agent 同步提示（供更新 registry 薄索引）\n")
        for a in agents:
            snap = manifest_snapshot(a)
            print(f"### {a.name}")
            print(f"- has_thinking: {'是' if snap['has_thinking'] else '否'}")
            print(f"- steps: {snap['steps_summary']}")
            print(f"- required_params: {', '.join(snap['required_params']) or '—'}")
            if snap.get("research"):
                print(f"- research: `{snap['research']}`")
            print()


def cmd_list(_: argparse.Namespace) -> int:
    for c in discover_clis():
        print(f"cli\t{c.name}\t{','.join(c.subcommands)}\tspec={'yes' if c.has_spec_yaml else 'no'}")
    for a in discover_agents():
        print(f"agent\t{a.name}\tthinking={a.has_thinking}\tspec={'yes' if a.has_spec_yaml else 'no'}")
    return 0


def cmd_sync(_: argparse.Namespace) -> int:
    """把用户 cli/agent 的 SPEC.yaml 同步到薄索引的 IX_USER_* 标记区。"""
    results = sync_indexes()
    if not results:
        print("[sync] 无变更（用户区已是最新）")
        return 0
    print(f"[sync] 已同步 {len(results)} 个文件的 IX_USER_* 标记区:")
    for fname, count in results.items():
        print(f"  ✓ {fname}（{count} 个用户条目）")
    return 0



def cmd_search(args: argparse.Namespace) -> int:
    """按意图关键词搜索 cli/agent 能力（渐进式发现第 1 步）。"""
    result = search_capabilities(args.query)
    if result["total"] == 0:
        print(f'[search] 未找到匹配「{args.query}」的 cli/agent')
        print('  → 可能需要新建。见 .claude/rules/artifacts.md')
        return 0
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(f'[search] 「{args.query}」匹配 {result["total"]} 个结果：\n')
    if result["clis"]:
        print("CLI:")
        for c in result["clis"]:
            print(f"  {c['name']:<25} {c['one_liner']}")
            print(f"  {'':25} 意图: {', '.join(c['intents'][:3])}")
            print(f"  {'':25} 详情: {c['spec']}")
            print()
    if result["agents"]:
        print("Agent:")
        for a in result["agents"]:
            print(f"  {a['name']:<25} {a['one_liner']}")
            print(f"  {'':25} 意图: {', '.join(a['intents'][:3])}")
            print(f"  {'':25} 详情: {a['spec']}")
            print()
    print("→ Read SPEC.yaml 获取命令/输入/输出详情")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="indexed 索引一致性审计（SPEC.yaml 为真相源）")
    sub = parser.add_subparsers(dest="command", required=True)

    pa = sub.add_parser("audit", help="校验 SPEC.yaml 与薄索引页一致性")
    pa.add_argument("--json", action="store_true", help="输出 JSON（供 Agent 消费）")
    pa.add_argument("--check", action="store_true", help="存在 error 时退出码 1")
    pa.set_defaults(func=cmd_audit)

    pl = sub.add_parser("list", help="列出已发现的 cli/agent")
    pl.set_defaults(func=cmd_list)

    ps = sub.add_parser("sync", help="把用户 SPEC.yaml 同步到薄索引 IX_USER_* 标记区")
    ps.set_defaults(func=cmd_sync)

    psearch = sub.add_parser("search", help="按意图关键词搜索 cli/agent 能力（渐进式发现第 1 步）")
    psearch.add_argument("query", help="意图关键词，如 '拉数' '定时' '审计'")
    psearch.add_argument("--json", action="store_true", help="输出 JSON")
    psearch.set_defaults(func=cmd_search)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
