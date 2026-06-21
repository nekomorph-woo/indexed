#!/usr/bin/env python3
"""ix-init-cli — indexed 工作区初始化与基线更新。

子命令：
    init    交互式初始化（git 模式 + 昵称/称呼）
    update  从新基线目录更新框架文件（保护用户区）
    status  查看当前初始化状态
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import (
    BASELINE_CLIS,
    BASELINE_VERSION_FILE,
    CLAUDE_MD,
    GIT_WORKFLOW_RULE,
    INDEXED_ROOT,
    MIGRATIONS_LOG,
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
    # 跳过 markdown 加粗标记 ** 匹配「昵称**：value」或「昵称：value」
    nm = re.search(r"昵称[\*]*[：:]\s*(\S+)", block)
    am = re.search(r"称呼[\*]*[：:]\s*(\S+)", block)
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


def _write_baseline_version() -> None:
    """写 .indexed-baseline-version（迁移水位线，update 时用）。

    mode/persona 不在这里——它们在 git-workflow.md 的 GIT_MODE 标记区。
    """
    version = VERSION_FILE.read_text(encoding="utf-8").strip().split("\n")[0]
    BASELINE_VERSION_FILE.write_text(version + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Migration 链（M9.3）
# ---------------------------------------------------------------------------

def _parse_version(s: str) -> tuple[int, ...]:
    """'0.1.0' → (0, 1, 0)；非法格式返回 ()。"""
    try:
        return tuple(int(x) for x in s.strip().split("."))
    except ValueError:
        return ()


def _is_newer(a: str, b: str) -> bool:
    """a 是否比 b 新（semver 比较）。解析失败保守返回 False。"""
    pa, pb = _parse_version(a), _parse_version(b)
    if not pa or not pb:
        return False
    return pa > pb


def _load_migrations() -> dict[tuple[str, str], object]:
    """扫描 migrations/ 目录，加载所有 migration 模块。

    返回 {(VERSION_FROM, VERSION_TO): module}。非法 migration 跳过并 warn。
    """
    mig_dir = INDEXED_ROOT / "artifacts" / "ix-init-cli" / "migrations"
    if not mig_dir.is_dir():
        return {}
    result: dict[tuple[str, str], object] = {}
    pattern = re.compile(r"^(.+)_to_(.+)\.py$")
    for py in sorted(mig_dir.glob("*_to_*.py")):
        if py.name == "__init__.py":
            continue
        m = pattern.match(py.name)
        if not m:
            continue
        vf, vt = m.group(1), m.group(2)
        try:
            spec = importlib.util.spec_from_file_location(
                f"migration_{vf}_to_{vt}", py
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            required = (
                "VERSION_FROM", "VERSION_TO",
                "describe", "check", "migrate", "verify",
            )
            if not all(hasattr(mod, attr) for attr in required):
                print(f"[warn] migration 缺接口: {py.name}（跳过）", file=sys.stderr)
                continue
            if mod.VERSION_FROM != vf or mod.VERSION_TO != vt:  # type: ignore[attr-defined]
                print(
                    f"[warn] migration 文件名与 VERSION_FROM/TO 不一致: {py.name}（跳过）",
                    file=sys.stderr,
                )
                continue
            result[(vf, vt)] = mod
        except Exception as e:
            print(f"[warn] migration 加载失败: {py.name}（{e}）", file=sys.stderr)
    return result


def _compute_migration_chain(
    cur: str,
    new: str,
    all_migrations: dict[tuple[str, str], object],
) -> list[object] | None:
    """计算从 cur 到 new 的 migration 链。

    - 返回 migration module 列表（顺序：cur → ... → new）
    - 链不完整（中间有缺环）返回 None
    - 防环（visited set）
    """
    if cur == new:
        return []
    chain: list[object] = []
    current = cur
    visited: set[str] = set()
    while current != new:
        if current in visited:
            return None  # 环
        visited.add(current)
        next_step = None
        # 优先匹配直接到 new 的
        if (current, new) in all_migrations:
            next_step = all_migrations[(current, new)]
        else:
            # 找 current → next，next 比 current 新且不超 new
            for (vf, vt), mod in all_migrations.items():
                if vf != current:
                    continue
                if _is_newer(vt, current) and not _is_newer(vt, new):
                    if next_step is None or _is_newer(vt, next_step.VERSION_TO):  # type: ignore[attr-defined]
                        next_step = mod
        if next_step is None:
            return None  # 缺环
        chain.append(next_step)
        current = next_step.VERSION_TO  # type: ignore[attr-defined]
    return chain


def _append_migration_log(entries: list[dict]) -> None:
    """追加迁移记录到 .indexed-migrations.log（append-only）。"""
    tz = ZoneInfo("Asia/Shanghai")
    with MIGRATIONS_LOG.open("a", encoding="utf-8") as f:
        for entry in entries:
            ts = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            changes_str = "; ".join(entry["changes"]) if entry["changes"] else "(无变更)"
            f.write(f"{ts} {entry['from']} → {entry['to']}: {changes_str}\n")


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

        print("[4/4] 写入基线版本水位线 ...")
        _write_baseline_version()
        print(f"  ✓ {BASELINE_VERSION_FILE.name}")
    except (OSError, KeyboardInterrupt) as e:
        # 回滚：恢复标记区原状，删除可能半写的 baseline version
        print(f"\n[error] 初始化中断（{e}），正在回滚标记区 ...", file=sys.stderr)
        if old_git_text:
            GIT_WORKFLOW_RULE.write_text(old_git_text, encoding="utf-8")
        if old_claude_text:
            CLAUDE_MD.write_text(old_claude_text, encoding="utf-8")
        if BASELINE_VERSION_FILE.exists():
            BASELINE_VERSION_FILE.unlink()
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

    # cur_ver 优先从 .indexed-baseline-version 读（迁移水位线），fallback VERSION
    if BASELINE_VERSION_FILE.is_file():
        cur_ver = BASELINE_VERSION_FILE.read_text(encoding="utf-8").strip()
    elif VERSION_FILE.is_file():
        cur_ver = VERSION_FILE.read_text(encoding="utf-8").strip()
    else:
        cur_ver = "?"
    new_ver = (src / "VERSION").read_text(encoding="utf-8").strip()

    # 版本检查：拒绝同级 + 拒绝降级
    if cur_ver == new_ver:
        print(f"[update] 当前版本已是 {new_ver}（无需更新）")
        return 0
    if cur_ver != "?" and not _is_newer(new_ver, cur_ver):
        print(
            f"[error] 不支持降级或同级更新（当前 {cur_ver} → 目标 {new_ver}）",
            file=sys.stderr,
        )
        return 1

    print(f"update: {cur_ver} → {new_ver}\n")

    # migration 链计算 + 显示 changelog + 交互式确认
    all_migrations = _load_migrations()
    chain = _compute_migration_chain(cur_ver, new_ver, all_migrations)
    if chain is None:
        print(
            f"[error] migration 链不完整（{cur_ver} → {new_ver} 中间有缺环）",
            file=sys.stderr,
        )
        print(f"       已有 migrations: {sorted(all_migrations.keys())}", file=sys.stderr)
        return 1

    migration_entries: list[dict] = []
    if chain:
        print(f"[migration] 需要 {len(chain)} 次迁移：\n")
        for m in chain:
            print(f"═══ {m.VERSION_FROM} → {m.VERSION_TO} ═══")
            print(m.describe())
            affected = m.check(INDEXED_ROOT)
            if affected:
                print(f"\n影响 {len(affected)} 个用户文件：")
                for f in affected[:5]:
                    print(f"  - {f}")
                if len(affected) > 5:
                    print(f"  ... 还有 {len(affected) - 5} 个")
            print()

        if not args.yes:
            confirm = input(
                f"确认从 {cur_ver} 升级到 {new_ver}（含 {len(chain)} 次迁移）？[y/N] "
            ).strip().lower()
            if confirm != "y":
                print("[update] 已取消")
                return 0

        # 顺序跑 migrations + 自验证
        print(f"[migration] 开始执行 {len(chain)} 次迁移...\n")
        for m in chain:
            print(f"  [migrate] {m.VERSION_FROM} → {m.VERSION_TO}...")
            changes = m.migrate(INDEXED_ROOT)
            migration_entries.append({
                "from": m.VERSION_FROM,
                "to": m.VERSION_TO,
                "changes": changes,
            })
            problems = m.verify(INDEXED_ROOT)
            if problems:
                print(f"  [error] {m.VERSION_TO} 验证失败：", file=sys.stderr)
                for p in problems:
                    print(f"    - {p}", file=sys.stderr)
                _append_migration_log(migration_entries)
                print(
                    f"\n[update] 已中止。工作区处于中间状态（{cur_ver} → {m.VERSION_TO}）。",
                    file=sys.stderr,
                )
                print(
                    "建议检查 .indexed-migrations.log 已跑的迁移；修复后重跑 update。",
                    file=sys.stderr,
                )
                return 1
        print()

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

    # --- 更新水位线 + 追加迁移历史 ---
    BASELINE_VERSION_FILE.write_text(new_ver + "\n", encoding="utf-8")
    if migration_entries:
        _append_migration_log(migration_entries)

    # --- 摘要 ---
    print(f"\n[done] {cur_ver} → {new_ver} 升级完成")
    print(f"  迁移次数: {len(migration_entries)}")
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
    if BASELINE_VERSION_FILE.is_file():
        print(f"基线版本: {BASELINE_VERSION_FILE.read_text(encoding='utf-8').strip()}")
    else:
        print("基线版本: 未初始化（运行 init）")
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

    pu = sub.add_parser("update", help="从新基线目录更新框架文件（含 migration 链）")
    pu.add_argument("source", help="新基线解压后的目录路径")
    pu.add_argument("--yes", "-y", action="store_true", help="跳过交互式确认（用于脚本/CI）")
    pu.set_defaults(func=cmd_update)

    ps = sub.add_parser("status", help="查看当前状态")
    ps.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
