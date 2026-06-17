"""manifest / command 占位符替换。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _param_lookup(params: dict[str, Any], key: str) -> str:
    if key not in params:
        raise KeyError(f"manifest 引用了未提供的参数: {key}")
    return str(params[key])


def build_context(
    *,
    run_id: str,
    agent_root: Path,
    run_dir: Path,
    artifacts_root: Path,
    workspace_root: Path,
    params: dict[str, Any],
) -> dict[str, str]:
    ctx = {
        "run_id": run_id,
        "agent_root": str(agent_root),
        "workspace_root": str(workspace_root),
        "artifacts_root": str(artifacts_root),
        "run_dir": str(run_dir),
        "work_raw": str(run_dir / "work" / "raw"),
        "work_thinking": str(run_dir / "work" / "thinking"),
        "run_output": str(run_dir / "output"),
        "run_inbox": str(run_dir / "inbox"),
    }
    for k, v in params.items():
        ctx[f"params.{k}"] = str(v)
    return ctx


_PARAM_RE = re.compile(r"\{params\.([a-zA-Z0-9_]+)\}")


def substitute(text: str, ctx: dict[str, str]) -> str:
    def repl_param(m: re.Match[str]) -> str:
        key = f"params.{m.group(1)}"
        if key not in ctx:
            raise KeyError(f"占位符 {{{key}}} 无对应值")
        return ctx[key]

    out = _PARAM_RE.sub(repl_param, text)
    for name, value in sorted(ctx.items(), key=lambda x: -len(x[0])):
        if name.startswith("params."):
            continue
        out = out.replace("{" + name + "}", value)
    if "{" in out and "}" in out:
        unknown = re.findall(r"\{[a-zA-Z0-9_.]+\}", out)
        if unknown:
            raise KeyError(f"未解析占位符: {', '.join(sorted(set(unknown)))}")
    return out


def resolve_run_path(run_dir: Path, rel: str) -> Path:
    p = Path(rel)
    if p.is_absolute():
        return p
    return (run_dir / rel).resolve()
