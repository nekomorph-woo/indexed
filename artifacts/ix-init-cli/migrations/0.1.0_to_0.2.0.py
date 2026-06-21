"""0.1.0 → 0.2.0 迁移：示例（占位）

这是 indexed 第一个 migration，用于演示接口规范。当 0.2.0 有实际 breaking changes
时，在本文件实现 migrate() 逻辑。

常见 migration 任务示例：
- manifest.yaml 字段重命名（如 default_from 格式变化）
- SPEC.yaml 字段增加/删除
- 文件结构变化（如 _shared/specs 子目录调整）
- 删除已废弃的 cli 子命令参数
- 用户内容格式调整（如 reports/<type>/<周期>/variable.md 字段变化）
"""

from __future__ import annotations

from pathlib import Path

VERSION_FROM = "0.1.0"
VERSION_TO = "0.2.0"


def describe() -> str:
    """返回 changelog 说明（用户看到的破坏性变更）。"""
    return """0.1.0 → 0.2.0：（占位 migration，无实际变更）

这是 indexed 第一个 migration，用于演示接口规范。
当 0.2.0 真正发布且有 breaking changes 时，在本文件实现 migrate() 逻辑。"""


def check(workspace_root: Path) -> list[str]:
    """前置检查（dry-run）。返回受影响用户文件清单（相对工作区根的路径）。

    update 命令会聚合所有 migration 的 check() 结果，让用户看到「升级会影响哪些文件」。
    """
    # 占位：0.1.0 → 0.2.0 无 breaking change
    return []


def migrate(workspace_root: Path) -> list[str]:
    """执行迁移。返回变更说明列表（每个元素一行说明，写入 .indexed-migrations.log）。

    实际迁移逻辑示例（注释，未启用）：

        # manifest.yaml default_from 格式调整
        for manifest in workspace_root.glob("ix-agents/*/manifest.yaml"):
            data = yaml.safe_load(manifest.read_text())
            changed = False
            for p in data.get("params") or []:
                if p.get("default_from", "").startswith("config/"):
                    p["default_from"] = p["default_from"][len("config/"):]
                    changed = True
            if changed:
                manifest.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
                changes.append(f"{manifest.parent.name}: default_from 格式调整")
    """
    return ["（无操作）0.1.0 → 0.2.0 占位 migration"]


def verify(workspace_root: Path) -> list[str]:
    """自验证。返回问题清单（空 list = 通过；非空 = 中止 update）。

    示例（如果 migrate 改了 default_from 格式）：

        problems = []
        for manifest in workspace_root.glob("ix-agents/*/manifest.yaml"):
            data = yaml.safe_load(manifest.read_text())
            for p in data.get("params") or []:
                if p.get("default_from", "").startswith("config/"):
                    problems.append(f"{manifest.parent.name}: 仍有 config/ 前缀")
        return problems
    """
    # 占位：无变更，无验证
    return []
