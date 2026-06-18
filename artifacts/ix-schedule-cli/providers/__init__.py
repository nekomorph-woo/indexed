"""跨平台 provider 分发：按 platform.system() 选择对应实现。"""

from __future__ import annotations

import platform


def get_provider():
    """返回当前平台的 provider 模块。"""
    system = platform.system()
    if system == "Windows":
        from . import windows
        return windows
    elif system == "Darwin":
        from . import macos
        return macos
    raise RuntimeError(
        f"不支持的平台: {system}。ix-schedule-cli 仅支持 Windows 和 macOS。"
    )


def supported_platform() -> str:
    """返回当前平台友好名（用于 status 展示）。"""
    system = platform.system()
    if system == "Windows":
        return "Windows"
    elif system == "Darwin":
        return "macOS"
    return system
