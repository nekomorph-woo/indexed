"""thinking step：渲染 prompt 并调用 Claude Code CLI（claude -p）。"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from placeholders import build_context, resolve_run_path, substitute

# ---------------------------------------------------------------------------
# 执行器注册表
# ---------------------------------------------------------------------------

_EXECUTORS: dict[str, dict[str, Any]] = {
    "claude-p": {
        "resolve_bin": lambda cfg, env: cfg or env or shutil.which("claude"),
        "build_cmd": lambda exe, prompt, workspace: [
            exe, "-p", prompt,
            "--dangerously-skip-permissions",
        ],
        "cwd": lambda workspace: str(workspace),
        "env_key": "IX_CLAUDE_BIN",
        "not_found_msg": (
            "未找到 `claude`（Claude Code CLI）。"
            "请安装 Claude Code 并确保在 PATH 中，或设置环境变量 IX_CLAUDE_BIN。"
        ),
    },
}


# ---------------------------------------------------------------------------
# Prompt 渲染
# ---------------------------------------------------------------------------

def render_thinking_prompt(
    *,
    step: dict[str, Any],
    manifest: dict[str, Any],
    run_dir: Path,
    agent_root: Path,
    artifacts_root: Path,
    workspace_root: Path,
    run_id: str,
    params: dict[str, Any],
) -> str:
    ctx = build_context(
        run_id=run_id,
        agent_root=agent_root,
        run_dir=run_dir,
        artifacts_root=artifacts_root,
        workspace_root=workspace_root,
        params=params,
    )
    inputs = step.get("inputs") or []
    input_lines: list[str] = []
    for pattern in inputs:
        rel = substitute(str(pattern), ctx)
        p = Path(rel)
        if p.is_absolute():
            paths = [p] if p.is_file() else []
        else:
            paths = sorted(run_dir.glob(rel))
        if not paths:
            raise FileNotFoundError(f"thinking inputs 无匹配文件: {pattern} -> {rel}")
        for p in paths:
            input_lines.append(f"- {p.resolve()}")

    business = substitute((step.get("prompt") or "").strip(), ctx)
    output_rel = step.get("output") or f"work/thinking/{step['id']}.md"
    output_path = resolve_run_path(run_dir, substitute(output_rel, ctx))

    return "\n".join(
        [
            "你是 ix-agents 的 thinking 执行器。严格按下列要求完成分析并落盘。",
            "",
            f"【agent】{manifest.get('id', agent_root.name)}",
            f"【run_id】{run_id}",
            f"【step_id】{step['id']}",
            "",
            "【本次参数】",
            *[f"- {k}: {v}" for k, v in params.items()],
            "",
            "【必读输入文件】（请先 Read 再分析）",
            *input_lines,
            "",
            "【分析要求】",
            business,
            "",
            "【硬性交付】",
            f"1. 将完整分析写入文件（必须创建父目录）：{output_path}",
            "2. 文件须非空，建议含：结论、依据、建议",
            f"3. 除 {run_dir} 下本次 run 目录外，不要修改其它路径",
        ]
    )


# ---------------------------------------------------------------------------
# 执行器调用
# ---------------------------------------------------------------------------

def run_agent_print(
    prompt: str,
    *,
    workspace_root: Path,
    llm_bin: str | None = None,
    llm_executor: str | None = None,
    dry_run: bool = False,
) -> None:
    """按 llm_executor 配置调用对应的 LLM CLI 子进程。"""
    executor = llm_executor or "claude-p"
    spec = _EXECUTORS.get(executor)
    if not spec:
        raise ValueError(f"未知 llm_executor: {executor}，可选: {list(_EXECUTORS)}")

    # 解析可执行文件：cfg 参数 > 环境变量 > PATH
    env_val = os.environ.get(spec["env_key"])
    exe = spec["resolve_bin"](llm_bin, env_val)
    if not exe:
        raise RuntimeError(spec["not_found_msg"])
    if dry_run:
        return

    cmd = spec["build_cmd"](exe, prompt, workspace_root)
    cwd = spec["cwd"](workspace_root)
    proc = subprocess.run(cmd, cwd=cwd, text=True)
    if proc.returncode != 0:
        # claude -p 在 Windows 上可能返回非 0 即使执行成功；
        # 由下游输出文件校验兜底（runner.py）
        print(
            f"[warn] {executor} 退出码 {proc.returncode}，"
            "将继续检查输出文件",
            flush=True,
        )
