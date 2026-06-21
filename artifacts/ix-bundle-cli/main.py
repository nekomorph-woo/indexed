#!/usr/bin/env python3
"""ix-bundle-cli — 生成 indexed 的可分发产物。

两个子命令：
- cli-bundle: 生成 dist/indexed-cli-<ver>.tar.gz（CLI-only 用户解压 + init）
- app-bundle: 生成 .app 内嵌基线目录（被 tauri.conf.json bundle.resources 引用）

打包前自动跑 sync + audit --check 确保索引一致。
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from config import (
    APP_BUNDLE_EXTRA,
    ARTIFACTS_ROOT,
    BASELINE_FILES,
    INDEXED_ROOT,
    VERSION_FILE,
    is_skipped,
)


def read_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def run_sync_and_audit() -> int:
    """打包前跑 sync + audit --check，确保索引一致。"""
    sync_cli = ARTIFACTS_ROOT / "ix-workspace-index-cli" / "main.py"
    print("[bundle] 跑 sync 同步索引…")
    rc = subprocess.call([sys.executable, str(sync_cli), "sync"], cwd=INDEXED_ROOT)
    if rc != 0:
        print(f"[bundle][error] sync 失败（退出码 {rc}）", file=sys.stderr)
        return rc
    print("[bundle] 跑 audit --check 校验一致性…")
    rc = subprocess.call(
        [sys.executable, str(sync_cli), "audit", "--check"], cwd=INDEXED_ROOT
    )
    if rc != 0:
        print(f"[bundle][error] audit --check 失败（退出码 {rc}）", file=sys.stderr)
    return rc


def copy_path(src: Path, dst: Path) -> None:
    """复制 src 到 dst，按 SKIP_DIRS/FILES 过滤。"""
    if src.is_file():
        if is_skipped(src.name, is_dir=False):
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return
    if not src.is_dir():
        return
    for entry in src.iterdir():
        if is_skipped(entry.name, is_dir=entry.is_dir()):
            continue
        rel = entry.relative_to(src)
        sub_dst = dst / rel
        if entry.is_dir():
            sub_dst.mkdir(parents=True, exist_ok=True)
            copy_path(entry, sub_dst)
        else:
            sub_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry, sub_dst)


def copy_baseline_to(tmp_root: Path, include_app_extras: bool) -> None:
    """把基线清单复制到 tmp_root（保持相对路径结构）。"""
    whitelist = list(BASELINE_FILES)
    if include_app_extras:
        whitelist.extend(APP_BUNDLE_EXTRA)
    for rel in whitelist:
        src = INDEXED_ROOT / rel
        if not src.exists():
            # 基线白名单里有但磁盘不存在（如 .claude/skills 未建）→ 跳过
            continue
        dst = tmp_root / rel
        copy_path(src, dst)


def write_readme_cli(target_dir: Path) -> None:
    """把 CLI-only 引导写到 target/README-cli.md（临时目录根）。

    源文件位于 _shared/docs/cli-quickstart.md（避免根目录污染），
    打包时复制到 tarball 根作为 README-cli.md。
    """
    src = INDEXED_ROOT / "_shared" / "docs" / "cli-quickstart.md"
    if src.is_file():
        shutil.copy2(src, target_dir / "README-cli.md")


def clear_user_zones(target_dir: Path) -> None:
    """清空临时目录里所有 IX_USER_* 标记区内容（确保不打包用户内容）。

    标记区格式：<!-- IX_USER_X_BEGIN --> ... <!-- IX_USER_X_END -->
    清空 = 保留 BEGIN/END 注释，删除中间内容。

    清空后在临时目录里重新跑 sync，让 IX_USER_* 区只反映基线 cli/agent
    （sync 基于临时目录的磁盘状态重新生成）。
    """
    import re

    pattern = re.compile(
        r"(<!--\s*IX_USER_[A-Z_]+_BEGIN\s*-->)(.*?)(<!--\s*IX_USER_[A-Z_]+_END\s*-->)",
        re.DOTALL,
    )

    for md_file in target_dir.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = pattern.sub(
            lambda m: f"{m.group(1)}\n<!-- 用户区已清空（打包时） -->\n{m.group(3)}",
            text,
        )
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")

    # 在临时目录里重新 sync：让 IX_USER_* 区只反映磁盘上的基线 cli/agent。
    # 这样解压后 audit 看到的 capabilities.md/registry.md 与磁盘一致。
    sync_cli = target_dir / "artifacts" / "ix-workspace-index-cli" / "main.py"
    if sync_cli.is_file():
        subprocess.call(
            [sys.executable, str(sync_cli), "sync"],
            cwd=target_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def make_tarball(src_dir: Path, output_file: Path) -> None:
    """打包 src_dir 为 tar.gz（src_dir 内容直接放在 indexed/ 子目录下）。"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(src_dir, arcname="indexed")


def cmd_cli_bundle(args: argparse.Namespace) -> int:
    """生成 dist/indexed-cli-<ver>.tar.gz。"""
    version = read_version()
    output_dir = Path(args.output).resolve()
    print(f"[cli-bundle] 版本 {version}，输出目录 {output_dir}")

    rc = run_sync_and_audit()
    if rc != 0:
        return rc

    with tempfile.TemporaryDirectory(prefix="ix-bundle-") as tmp:
        tmp_root = Path(tmp) / "indexed"
        tmp_root.mkdir(parents=True)

        print("[cli-bundle] 复制基线内容…")
        copy_baseline_to(tmp_root, include_app_extras=False)
        write_readme_cli(tmp_root)
        clear_user_zones(tmp_root)

        output_file = output_dir / f"indexed-cli-{version}.tar.gz"
        print(f"[cli-bundle] 打包 → {output_file}")
        make_tarball(tmp_root, output_file)

    size_kb = output_file.stat().st_size // 1024
    print(f"[cli-bundle] ✅ 完成（{size_kb} KB）")
    return 0


def cmd_app_bundle(args: argparse.Namespace) -> int:
    """生成 .app 内嵌基线目录（默认 ix-gui/src-tauri/baseline/）。"""
    output_dir = Path(args.output).resolve()
    print(f"[app-bundle] 输出目录 {output_dir}")

    rc = run_sync_and_audit()
    if rc != 0:
        return rc

    if output_dir.exists():
        print(f"[app-bundle] 清理旧目录 {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    print("[app-bundle] 复制基线内容（含 ix-gui 定位文档）…")
    copy_baseline_to(output_dir, include_app_extras=True)
    write_readme_cli(output_dir)
    clear_user_zones(output_dir)

    # 验证关键文件
    version_file = output_dir / "VERSION"
    if not version_file.is_file():
        print("[app-bundle][error] 缺少 VERSION 文件", file=sys.stderr)
        return 1
    version = version_file.read_text(encoding="utf-8").strip()
    print(f"[app-bundle] ✅ 完成（baseline version={version}）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ix-bundle-cli — 生成 indexed 的可分发产物（tar.gz / .app 内嵌基线）"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    cli = sub.add_parser("cli-bundle", help="生成 indexed-cli-<ver>.tar.gz（CLI-only 用户）")
    cli.add_argument(
        "--output",
        default=str(ARTIFACTS_ROOT / "ix-bundle-cli" / "output"),
        help="输出目录（默认 artifacts/ix-bundle-cli/output/）",
    )
    cli.set_defaults(func=cmd_cli_bundle)

    app = sub.add_parser("app-bundle", help="生成 .app 内嵌基线目录（默认 ix-gui/src-tauri/baseline/）")
    app.add_argument(
        "--output",
        default="ix-gui/src-tauri/baseline",
        help="输出目录（默认 ix-gui/src-tauri/baseline/）",
    )
    app.set_defaults(func=cmd_app_bundle)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
