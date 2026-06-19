#!/usr/bin/env python3
"""ix-init-cli — indexed 工作区初始化与基线更新。

子命令：
    init    交互式初始化（git 模式 + 昵称/称呼）
    update  从新基线目录更新框架文件（保护用户区）
    status  查看当前初始化状态
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import (
    BASELINE_CLIS,
    CLAUDE_MD,
    GIT_WORKFLOW_RULE,
    INDEXED_ROOT,
    INIT_MARKER,
    MARKER_FILES,
    USER_BUCKETS,
    VERSION_FILE,
)
from markers import extract_all_user_zones, get_zone, replace_zone, restore_user_zones

_TZ = ZoneInfo("Asia/Shanghai")

GIT_MODE_CONTENT = {
    "local": "**当前模式：`local`**\n\n纯本地版本库，不推送远端。commit 后仅说明结果，**不**提示 push。",
    "remote": "**当前模式：`remote`**\n\n含远端（如 GitHub）。commit 后可 push。",
}

PERSONA_DEFAULT = "> **助手昵称**：Xi酱　　**对用户称呼**：您\n"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _run_git(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git"] + args, cwd=str(INDEXED_ROOT), capture_output=True, text=True
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def _safe_copy(src: Path, dst: Path) -> bool:
    """安全复制：源=目标时跳过，否则 copy2。返回是否实际复制。"""
    try:
        if src.resolve() == dst.resolve():
            return False
        shutil.copy2(src, dst)
        return True
    except (OSError, shutil.SameFileError):
        return False


def _git_initialized() -> bool:
    return (INDEXED_ROOT / ".git").is_dir()


def _detect_git_mode() -> str:
    if not GIT_WORKFLOW_RULE.is_file():
        return "uninitialized"
    block = get_zone(GIT_WORKFLOW_RULE.read_text(encoding="utf-8"), "GIT_MODE")
    if not block:
        return "uninitialized"
    for mode in ("local", "remote"):
        if f"`{mode}`" in block:
            return mode
    return "uninitialized"


def _detect_persona() -> tuple[str, str]:
    """返回 (昵称, 称呼)。"""
    if not CLAUDE_MD.is_file():
        return ("Xi酱", "您")
    block = get_zone(CLAUDE_MD.read_text(encoding="utf-8"), "PERSONA")
    if not block:
        return ("Xi酱", "您")
    nick = "Xi酱"
    addr = "您"
    import re
    nm = re.search(r"昵称[：:]\s*(\S+)", block)
    am = re.search(r"称呼[：:]\s*(\S+)", block)
    if nm:
        nick = nm.group(1)
    if am:
        addr = am.group(1)
    return (nick, addr)


def _write_git_mode(mode: str) -> bool:
    content = GIT_MODE_CONTENT.get(mode)
    if content is None:
        return False
    text = GIT_WORKFLOW_RULE.read_text(encoding="utf-8")
    text = replace_zone(text, "GIT_MODE", "\n" + content + "\n")
    GIT_WORKFLOW_RULE.write_text(text, encoding="utf-8")
    return True


def _write_persona(nick: str, addr: str) -> bool:
    content = f"> **助手昵称**：{nick}　　**对用户称呼**：{addr}\n"
    text = CLAUDE_MD.read_text(encoding="utf-8")
    text = replace_zone(text, "PERSONA", "\n" + content + "\n")
    CLAUDE_MD.write_text(text, encoding="utf-8")
    return True


def _write_init_marker(mode: str, nick: str, addr: str) -> None:
    ts = datetime.now(_TZ).strftime("%Y-%m-%d %H:%M:%S")
    INIT_MARKER.write_text(
        f"initialized_at: {ts}\nmode: {mode}\nnick: {nick}\naddr: {addr}\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    print("indexed 初始化\n")

    # --- persona ---
    nick = args.nick
    addr = args.addr
    if nick is None or addr is None:
        print("  助手昵称（回车=默认 Xi酱）:")
        nick = input("  > ").strip() or "Xi酱"
        print("  对用户的称呼（回车=默认 您）:")
        addr = input("  > ").strip() or "您"
    print(f"  → 昵称: {nick}，称呼: {addr}\n")

    # --- git mode ---
    mode = args.mode
    if mode is None:
        print("  Git 模式:")
        print("    1) local  — 纯本地版本库，不推送远端")
        print("    2) remote — 含远端（如 GitHub），可 push")
        choice = input("  选择 [1/2]: ").strip()
        mode = "remote" if choice == "2" else "local"
    print(f"  → 模式: {mode}\n")

    # --- 1. git init ---
    if not _git_initialized():
        print("[1/4] git init ...")
        code, out = _run_git(["init"])
        if code != 0:
            print(f"[error] git init 失败: {out}", file=sys.stderr)
            return 1
        print(f"  ✓ {out}")
    else:
        print("[1/4] git 已初始化，跳过")

    # --- 2. remote ---
    if mode == "remote":
        url = args.remote_url
        if url is None:
            url = input("[2/4] 远端 URL（留空跳过）: ").strip() or None
        if url:
            code, out = _run_git(["remote", "add", "origin", url])
            if code != 0 and "already exists" in out:
                _run_git(["remote", "set-url", "origin", url])
            print(f"  ✓ origin: {url}")
        else:
            print("  → 跳过远端（后续可 git remote add origin <url>）")
    else:
        print("[2/4] local 模式，无需远端")

    # --- 3+4. 改写规则标记区 + 标记文件（事务保护）---
    print("[3/4] 改写规则 ...")
    old_git_text = GIT_WORKFLOW_RULE.read_text(encoding="utf-8") if GIT_WORKFLOW_RULE.is_file() else ""
    old_claude_text = CLAUDE_MD.read_text(encoding="utf-8") if CLAUDE_MD.is_file() else ""
    try:
        _write_git_mode(mode)
        _write_persona(nick, addr)
        print("  ✓ git-workflow.md / CLAUDE.md 已更新")

        print("[4/4] 写入初始化标记 ...")
        _write_init_marker(mode, nick, addr)
        print(f"  ✓ {INIT_MARKER.name}")
    except (OSError, KeyboardInterrupt) as e:
        # 回滚：恢复标记区原状，删除可能半写的 init marker
        print(f"\n[error] 初始化中断（{e}），正在回滚标记区 ...", file=sys.stderr)
        if old_git_text:
            GIT_WORKFLOW_RULE.write_text(old_git_text, encoding="utf-8")
        if old_claude_text:
            CLAUDE_MD.write_text(old_claude_text, encoding="utf-8")
        if INIT_MARKER.exists():
            INIT_MARKER.unlink()
        print("[error] 已回滚。请重新运行 init。", file=sys.stderr)
        return 1

    print(f"\n[done] indexed 已初始化（模式 {mode}，昵称 {nick}，称呼 {addr}）")
    return 0


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

def cmd_update(args: argparse.Namespace) -> int:
    src = Path(args.source).resolve()
    if not src.is_dir():
        print(f"[error] 源目录不存在: {src}", file=sys.stderr)
        return 1
    if not (src / "VERSION").is_file():
        print(f"[error] {src} 不像 indexed 基线（无 VERSION）", file=sys.stderr)
        return 1

    cur_ver = VERSION_FILE.read_text(encoding="utf-8").strip().split("\n")[0] if VERSION_FILE.is_file() else "?"
    new_ver = (src / "VERSION").read_text(encoding="utf-8").strip().split("\n")[0]
    print(f"update: {cur_ver} → {new_ver}\n")

    covered: list[str] = []
    protected: list[str] = []
    skipped: list[str] = []

    # --- 1. 标记区文件：抽用户区 → 覆盖 → 回灌 ---
    print("[1/3] 标记区文件（保护用户区）...")
    for rel in ("CLAUDE.md", ".claude/rules/git-workflow.md",
                "artifacts/capabilities.md", "artifacts/OVERVIEW.md",
                "ix-agents/registry.md", "ix-agents/OVERVIEW.md",
                "research/OVERVIEW.md"):
        dst = INDEXED_ROOT / rel
        src_f = src / rel
        if not src_f.is_file():
            continue
        user_zones = extract_all_user_zones(dst)
        _safe_copy(src_f, dst)
        n = restore_user_zones(dst, user_zones)
        protected.append(f"{rel}" + (f"（恢复 {n} 个用户区）" if n else ""))
        # 告警：用户区非空但回灌数不足 → 新基线缺少标记区，用户区被丢弃
        if user_zones and n < len(user_zones):
            lost = len(user_zones) - n
            print(
                f"  [warn] {rel}：{lost} 个用户标记区在新基线中未找到对应位置，"
                f"已被覆盖（用户区内容丢失）",
                file=sys.stderr,
            )
    print(f"  ✓ {len(protected)} 个标记区文件已更新（用户区已保护）")

    # --- 2. 纯框架文件：直接覆盖 ---
    print("[2/3] 纯框架文件...")
    # .claude/（除 git-workflow.md）
    claude_src = src / ".claude"
    if claude_src.is_dir():
        for f in claude_src.rglob("*"):
            if f.is_file() and f.name != "git-workflow.md":
                rel = f.relative_to(src)
                dst = INDEXED_ROOT / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if _safe_copy(f, dst):
                    covered.append(str(rel))
    # _shared/
    shared_src = src / "_shared"
    if shared_src.is_dir():
        for f in shared_src.rglob("*"):
            if f.is_file() and "repos" not in f.parts:
                rel = f.relative_to(src)
                dst = INDEXED_ROOT / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if _safe_copy(f, dst):
                    covered.append(str(rel))
    # artifacts/ix-*-cli（仅基线 4 个，见 config.py BASELINE_CLIS）
    for cli in BASELINE_CLIS:
        cli_src = src / "artifacts" / cli
        if cli_src.is_dir():
            for f in cli_src.rglob("*"):
                if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc":
                    rel = f.relative_to(src)
                    dst = INDEXED_ROOT / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if _safe_copy(f, dst):
                        covered.append(str(rel))
    # VERSION
    if _safe_copy(src / "VERSION", VERSION_FILE):
        covered.append("VERSION")
    # .gitignore
    if (src / ".gitignore").is_file():
        if _safe_copy(src / ".gitignore", INDEXED_ROOT / ".gitignore"):
            covered.append(".gitignore")
    print(f"  ✓ {len(covered)} 个框架文件已覆盖")

    # --- 3. 用户内容跳过 ---
    print("[3/3] 用户内容保留...")
    for bucket in USER_BUCKETS:
        d = INDEXED_ROOT / bucket
        if d.is_dir():
            items = [x.name for x in d.iterdir() if x.name != "OVERVIEW.md"]
            if items:
                skipped.append(f"{bucket}/（{len(items)} 个用户条目）")
    user_clis = [x.name for x in (INDEXED_ROOT / "artifacts").iterdir()
                 if x.is_dir() and x.name.startswith("ix-") and x.name not in BASELINE_CLIS]
    if user_clis:
        skipped.append(f"artifacts/（用户 cli: {', '.join(user_clis)}）")
    user_agents = [x.name for x in (INDEXED_ROOT / "ix-agents").iterdir()
                   if x.is_dir() and x.name.startswith("ix-") and x.name.endswith("-agent")]
    if user_agents:
        skipped.append(f"ix-agents/（用户 agent: {', '.join(user_agents)}）")
    if skipped:
        for s in skipped:
            print(f"  → 保留 {s}")
    else:
        print("  → 无用户内容")

    # --- 摘要 ---
    print(f"\n[done] indexed 已更新到 {new_ver}")
    print(f"  标记区文件保护: {len(protected)}")
    print(f"  框架文件覆盖: {len(covered)}")
    print(f"  用户内容保留: {len(skipped)}")
    print(f"\n建议跑 `python artifacts/ix-workspace-index-cli/main.py sync` 同步索引。")
    return 0


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def cmd_status(_: argparse.Namespace) -> int:
    ver = VERSION_FILE.read_text(encoding="utf-8").strip().split("\n")[0] if VERSION_FILE.is_file() else "?"
    mode = _detect_git_mode()
    nick, addr = _detect_persona()
    print(f"版本: {ver}")
    print(f"Git 模式: {mode}")
    print(f"昵称: {nick}")
    print(f"称呼: {addr}")
    print(f"git init: {'是' if _git_initialized() else '否'}")
    if INIT_MARKER.is_file():
        print(f"初始化: {INIT_MARKER.read_text(encoding='utf-8').strip()}")
    else:
        print("初始化: 未初始化（运行 init）")
    if _git_initialized() and mode == "remote":
        code, out = _run_git(["remote", "-v"])
        if out:
            print(f"远端:\n{out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="indexed 工作区初始化与基线更新")
    sub = parser.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("init", help="初始化（git 模式 + 昵称/称呼）")
    pi.add_argument("--mode", choices=("local", "remote"))
    pi.add_argument("--remote-url")
    pi.add_argument("--nick", help="助手昵称（默认 Xi酱）")
    pi.add_argument("--addr", help="对用户称呼（默认 您）")
    pi.set_defaults(func=cmd_init)

    pu = sub.add_parser("update", help="从新基线目录更新框架文件")
    pu.add_argument("source", help="新基线解压后的目录路径")
    pu.set_defaults(func=cmd_update)

    ps = sub.add_parser("status", help="查看当前状态")
    ps.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
