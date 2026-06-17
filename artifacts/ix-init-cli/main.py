#!/usr/bin/env python3
"""ix-init-cli — 初始化 indexed 工作区的 Git 属性与规则模式。

交互式选定 Git 模式（local / remote），据用户意愿：
  1. git init（若尚未初始化）
  2. 改写 .claude/rules/git-workflow.md 的标记区（IX_GIT_MODE_BEGIN/END）
  3. remote 模式可选配置远端 URL

用法：
    python artifacts/ix-init-cli/main.py init          # 交互式
    python artifacts/ix-init-cli/main.py init --mode local
    python artifacts/ix-init-cli/main.py init --mode remote --remote-url <url>
    python artifacts/ix-init-cli/main.py status        # 查看当前模式
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from config import CLAUDE_MD, GIT_WORKFLOW_RULE, GITIGNORE, INDEXED_ROOT, RULES_DIR, VERSION_FILE

# git-workflow.md 标记区正则
_MODE_BLOCK_RE = re.compile(
    r"(<!-- IX_GIT_MODE_BEGIN -->)([\s\S]*?)(<!-- IX_GIT_MODE_END -->)"
)

# 各模式的标记区内容
_MODE_CONTENT = {
    "local": """**当前模式：`local`**

纯本地版本库，不推送远端。commit 后仅说明结果，**不**提示 push。""",
    "remote": """**当前模式：`remote`**

含远端（如 GitHub）。commit 后可 push。""",
    "uninitialized": """**当前模式：`uninitialized`**

> 尚未初始化。运行 `python artifacts/ix-init-cli/main.py init` 选定模式，本段会被自动改写。""",
}


def _detect_current_mode() -> str:
    """从 git-workflow.md 标记区读当前模式。"""
    if not GIT_WORKFLOW_RULE.is_file():
        return "uninitialized"
    text = GIT_WORKFLOW_RULE.read_text(encoding="utf-8")
    m = _MODE_BLOCK_RE.search(text)
    if not m:
        return "uninitialized"
    block = m.group(2)
    for mode in ("local", "remote"):
        if f"`{mode}`" in block:
            return mode
    return "uninitialized"


def _rewrite_mode_block(mode: str) -> bool:
    """改写 git-workflow.md 的标记区为指定模式。返回是否成功。"""
    if not GIT_WORKFLOW_RULE.is_file():
        print(f"[error] 找不到 {GIT_WORKFLOW_RULE}", file=sys.stderr)
        return False
    text = GIT_WORKFLOW_RULE.read_text(encoding="utf-8")
    new_content = _MODE_CONTENT.get(mode)
    if new_content is None:
        print(f"[error] 未知模式: {mode}", file=sys.stderr)
        return False
    new_block = f"<!-- IX_GIT_MODE_BEGIN -->\n{new_content}\n<!-- IX_GIT_MODE_END -->"
    if _MODE_BLOCK_RE.search(text):
        text = _MODE_BLOCK_RE.sub(lambda _: new_block, text)
    else:
        print("[warn] git-workflow.md 缺少 IX_GIT_MODE 标记区，追加到文件末尾", file=sys.stderr)
        text = text.rstrip() + "\n\n" + new_block + "\n"
    GIT_WORKFLOW_RULE.write_text(text, encoding="utf-8")
    return True


def _git_initialized() -> bool:
    return (INDEXED_ROOT / ".git").is_dir()


def _run_git(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
    ["git"] + args,
        cwd=str(INDEXED_ROOT),
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def cmd_init(args: argparse.Namespace) -> int:
    mode = args.mode
    if mode is None:
        # 交互式
        print("indexed Git 模式初始化\n")
        print("  1) local  — 纯本地版本库，不推送远端")
        print("  2) remote — 含远端（如 GitHub），可 push")
        print()
        choice = input("请选择 [1/2]: ").strip()
        mode = "remote" if choice == "2" else "local"
        print(f"  → 已选: {mode}\n")

    if mode not in ("local", "remote"):
        print(f"[error] 模式必须是 local 或 remote， got {mode}", file=sys.stderr)
        return 1

    # 1. git init（若未初始化）
    if not _git_initialized():
        print("[1/3] git init ...")
        code, out = _run_git(["init"])
        if code != 0:
            print(f"[error] git init 失败: {out}", file=sys.stderr)
            return 1
        print(f"  ✓ {out}")
    else:
        print("[1/3] git 已初始化，跳过")

    # 2. 改写 git-workflow.md 标记区
    print(f"[2/3] 改写 git-workflow.md → 模式 {mode} ...")
    if _rewrite_mode_block(mode):
        print(f"  ✓ {GIT_WORKFLOW_RULE.name} 已更新")
    else:
        return 1

    # 3. remote 模式：配置远端
    if mode == "remote":
        remote_url = args.remote_url
        if remote_url is None:
            remote_url = input("[3/3] 远端 URL（留空跳过）: ").strip() or None
        if remote_url:
            code, out = _run_git(["remote", "add", "origin", remote_url])
            if code == 0:
                print(f"  ✓ 已添加远端 origin: {remote_url}")
            elif "already exists" in out:
                code, out = _run_git(["remote", "set-url", "origin", remote_url])
                print(f"  ✓ 已更新远端 origin: {remote_url}")
            else:
                print(f"  [warn] 配置远端失败: {out}", file=sys.stderr)
        else:
            print("  → 跳过远端配置（后续可 git remote add origin <url>）")
    else:
        print("[3/3] local 模式，无需远端配置")

    print(f"\n[done] indexed Git 模式已初始化为: {mode}")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    mode = _detect_current_mode()
    git_ok = _git_initialized()
    print(f"Git 模式: {mode}")
    print(f"git init: {'是' if git_ok else '否'}")
    if git_ok and mode == "remote":
        code, out = _run_git(["remote", "-v"])
        print(f"远端:\n{out}" if out else "远端: （未配置）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="初始化 indexed 工作区的 Git 属性与规则模式"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("init", help="初始化或切换 Git 模式")
    pi.add_argument("--mode", choices=("local", "remote"), help="直接指定模式（跳过交互）")
    pi.add_argument("--remote-url", help="remote 模式的远端 URL")
    pi.set_defaults(func=cmd_init)

    ps = sub.add_parser("status", help="查看当前 Git 模式")
    ps.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
