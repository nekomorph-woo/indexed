"""标记区（marker zone）操作：抽取、回灌、改写。

标记区格式：
    <!-- IX_<NAME>_BEGIN -->
    ...内容...
    <!-- IX_<NAME>_END -->

用于在文件中划定「可被 update 覆盖/保留」的区域。
"""

from __future__ import annotations

import re
from pathlib import Path

# 匹配 <!-- IX_<NAME>_BEGIN --> ... <!-- IX_<NAME>_END -->
_ZONE_RE = re.compile(
    r"(<!--\s*IX_(\w+)_BEGIN\s*-->)([\s\S]*?)(<!--\s*IX_\2_END\s*-->)"
)


def extract_zones(text: str) -> dict[str, str]:
    """从文本中提取所有标记区，返回 {ZONE_NAME: 内容}（不含 BEGIN/END 标签本身）。"""
    zones: dict[str, str] = {}
    for m in _ZONE_RE.finditer(text):
        name = m.group(2)
        content = m.group(3)
        zones[name] = content
    return zones


def get_zone(text: str, zone_name: str) -> str | None:
    """获取指定标记区的内容（不含标签），不存在返回 None。"""
    zones = extract_zones(text)
    return zones.get(zone_name)


def replace_zone(text: str, zone_name: str, new_content: str) -> str:
    """替换指定标记区的内容（保留 BEGIN/END 标签）。若不存在则返回原文。"""
    pattern = re.compile(
        r"(<!--\s*IX_" + re.escape(zone_name) + r"_BEGIN\s*-->)([\s\S]*?)(<!--\s*IX_"
        + re.escape(zone_name) + r"_END\s*-->)"
    )
    return pattern.sub(
        lambda m: m.group(1) + new_content + m.group(3), text, count=1
    )


def extract_all_user_zones(file_path: Path) -> dict[str, str]:
    """从文件中提取所有用户标记区（USER / PERSONA / GIT_MODE）的内容。

    这些是 update 时需要保护的区域。
    """
    if not file_path.is_file():
        return {}
    text = file_path.read_text(encoding="utf-8")
    zones = extract_zones(text)
    # 保护所有 USER_*、PERSONA、GIT_MODE 标记区
    return {
        name: content
        for name, content in zones.items()
        if name.startswith("USER_") or name in ("PERSONA", "GIT_MODE")
    }


def restore_user_zones(file_path: Path, user_zones: dict[str, str]) -> int:
    """把用户标记区内容回灌到文件。返回成功回灌的数量。

    成功 = 新文件中存在对应的标记区（内容相同也算成功，因为说明没丢失）。
    """
    if not file_path.is_file():
        return 0
    text = file_path.read_text(encoding="utf-8")
    existing_zones = extract_zones(text)
    count = 0
    changed = False
    for name, content in user_zones.items():
        if name not in existing_zones:
            continue
        count += 1
        new_text = replace_zone(text, name, content)
        if new_text != text:
            text = new_text
            changed = True
    if changed:
        file_path.write_text(text, encoding="utf-8")
    return count
