#!/usr/bin/env python3
"""indexed 索引审计：以 SPEC.yaml 为真相源，校验薄索引页（capabilities.md / registry.md）一致性。"""

from __future__ import annotations

import argparse
import json
import sys

from scanner import WORKSPACE_ROOT, audit_index, audit_governance, discover_agents, discover_clis, manifest_snapshot


def _cli_row(c) -> dict:
    return {
        "name": c.name,
        "subcommands": c.subcommands,
        "has_spec_yaml": c.has_spec_yaml,
        "has_spec_md": c.has_spec_md,
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
        "agent_sync_hints": {a.name: manifest_snapshot(a) for a in agents},
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_human(clis, agents, issues, errors, warns)

    return 1 if args.check and not ok else 0


def _print_human(clis, agents, issues, errors, warns) -> None:
    print(f"indexed 索引审计 @ {WORKSPACE_ROOT}\n")
    print("## 磁盘发现\n")
    print("| CLI | 子命令 | SPEC.yaml | SPEC.md |")
    print("|-----|--------|-----------|---------|")
    for c in clis:
        subs = ", ".join(c.subcommands) or "—"
        print(f"| {c.name} | {subs} | {'yes' if c.has_spec_yaml else 'no'} | {'yes' if c.has_spec_md else 'no'} |")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="indexed 索引一致性审计（SPEC.yaml 为真相源）")
    sub = parser.add_subparsers(dest="command", required=True)

    pa = sub.add_parser("audit", help="校验 SPEC.yaml 与薄索引页一致性")
    pa.add_argument("--json", action="store_true", help="输出 JSON（供 Agent 消费）")
    pa.add_argument("--check", action="store_true", help="存在 error 时退出码 1")
    pa.set_defaults(func=cmd_audit)

    pl = sub.add_parser("list", help="列出已发现的 cli/agent")
    pl.set_defaults(func=cmd_list)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
