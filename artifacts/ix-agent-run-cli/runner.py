"""按 manifest 顺序执行 tool / thinking steps。"""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

from config import ARTIFACTS_ROOT, INDEXED_ROOT, agent_dir, manifest_path
from placeholders import build_context, resolve_run_path, substitute
from thinking import render_thinking_prompt, run_agent_print

_TZ = ZoneInfo("Asia/Shanghai")


def new_run_id(runs_dir: Path) -> str:
    base = datetime.now(_TZ).strftime("%Y-%m-%d_%H-%M-%S")
    rid = base
    n = 2
    while (runs_dir / rid).exists():
        rid = f"{base}-{n}"
        n += 1
    return rid


def ensure_run_tree(run_dir: Path) -> None:
    for sub in ("inbox", "supplements", "work/raw", "work/thinking", "output"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def load_manifest(agent_id: str) -> dict[str, Any]:
    path = manifest_path(agent_id)
    if not path.is_file():
        raise FileNotFoundError(f"未找到 manifest: {path}")
    data = load_yaml(path)
    if data.get("id") and data["id"] != agent_id:
        raise ValueError(f"manifest id={data['id']} 与 --agent {agent_id} 不一致")
    data.setdefault("id", agent_id)
    return data


def load_defaults(agent_root: Path) -> dict[str, Any]:
    p = agent_root / "config" / "defaults.yaml"
    if p.is_file():
        return load_yaml(p) or {}
    return {}


def merge_params(
    manifest: dict[str, Any],
    defaults: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    params: dict[str, Any] = dict(defaults)
    agent_root = agent_dir(manifest["id"])
    for spec in manifest.get("params") or []:
        name = spec["name"]
        if name in params:
            continue
        if "default_from" in spec:
            ref = spec["default_from"]
            if "#" in ref:
                file_part, key = ref.split("#", 1)
                file_path = agent_root / file_part
                file_data = load_yaml(file_path) if file_path.is_file() else {}
                if key in (file_data or {}):
                    params[name] = file_data[key]
                    continue
        if "default" in spec:
            params[name] = spec["default"]
    params.update(overrides)
    for spec in manifest.get("params") or []:
        name = spec["name"]
        if spec.get("required") and name not in params:
            raise KeyError(f"缺少必填参数: {name}（config/defaults.yaml / --set）")
    return params


def check_expects(run_dir: Path, patterns: list[str]) -> None:
    for pat in patterns:
        rel = pat.replace("\\", "/")
        # 绝对路径：直接检查文件是否存在
        if rel.startswith("/"):
            if not Path(rel).exists():
                raise FileNotFoundError(f"expects 未满足: {pat}")
        else:
            hits = list(run_dir.glob(rel))
            if not hits:
                raise FileNotFoundError(f"expects 未满足: {pat}")


def run_tool_step(
    step: dict[str, Any],
    *,
    ctx: dict[str, str],
    run_dir: Path,
    dry_run: bool,
) -> None:
    tool = step.get("tool", "shell")
    if tool == "shell":
        cmd = substitute(step["command"].strip(), ctx)
        if dry_run:
            print(f"[dry-run] shell: {cmd[:200]}...")
            return
        # 用 Popen + 实时转发避免无 TTY 环境（launchd/cron）下 stdout 死锁
        proc = subprocess.Popen(
            cmd, shell=True, cwd=ctx["workspace_root"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        for line in proc.stdout:
            print(line, end="", flush=True)
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"tool step {step['id']} shell 退出码 {proc.returncode}")
    elif tool in ("write", "copy"):
        src = resolve_run_path(run_dir, substitute(step["from"], ctx))
        dst = resolve_run_path(run_dir, substitute(step["to"], ctx))
        if not src.is_file():
            raise FileNotFoundError(f"{tool} 源文件不存在: {src}")
        if dry_run:
            print(f"[dry-run] {tool}: {src} -> {dst}")
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        raise ValueError(f"不支持的 tool 类型: {tool}")

    expects = step.get("expects") or []
    if expects and not dry_run:
        check_expects(run_dir, [substitute(p, ctx) for p in expects])


def run_thinking_step(
    step: dict[str, Any],
    *,
    manifest: dict[str, Any],
    agent_root: Path,
    run_dir: Path,
    run_id: str,
    params: dict[str, Any],
    llm_bin: str | None,
    llm_executor: str | None = None,
    dry_run: bool,
) -> None:
    prompt = render_thinking_prompt(
        step=step,
        manifest=manifest,
        run_dir=run_dir,
        agent_root=agent_root,
        artifacts_root=ARTIFACTS_ROOT,
        workspace_root=INDEXED_ROOT,
        run_id=run_id,
        params=params,
    )
    prompt_file = run_dir / "work" / f".prompt-{step['id']}.txt"
    if not dry_run:
        prompt_file.write_text(prompt, encoding="utf-8")
    # step 级 llm_executor 覆盖全局默认
    effective_executor = step.get("llm_executor") or llm_executor
    run_agent_print(
        prompt,
        workspace_root=INDEXED_ROOT,
        llm_bin=llm_bin,
        llm_executor=effective_executor,
        dry_run=dry_run,
    )
    output_rel = step.get("output") or f"work/thinking/{step['id']}.md"
    ctx = build_context(
        run_id=run_id,
        agent_root=agent_root,
        run_dir=run_dir,
        artifacts_root=ARTIFACTS_ROOT,
        workspace_root=INDEXED_ROOT,
        params=params,
    )
    out = resolve_run_path(run_dir, substitute(output_rel, ctx))
    if dry_run:
        return
    if not out.is_file() or out.stat().st_size == 0:
        raise RuntimeError(f"thinking 输出缺失或为空: {out}")


def execute(
    *,
    agent_id: str,
    run_id: str | None,
    resume: bool,
    param_overrides: dict[str, Any],
    trigger: str,
    llm_bin: str | None,
    llm_executor: str | None = None,
    dry_run: bool,
) -> Path:
    manifest = load_manifest(agent_id)
    agent_root = agent_dir(agent_id)
    runs_dir = agent_root / "runs"

    if run_id and resume:
        run_dir = runs_dir / run_id
        if not run_dir.is_dir():
            raise FileNotFoundError(f"run 不存在: {run_dir}")
        state = load_yaml(run_dir / "run.yaml")
        params = state.get("params") or {}
        params.update(param_overrides)
        completed = set(state.get("steps_completed") or [])
        # resume 时从 run.yaml 恢复 llm_executor
        llm_executor = state.get("llm_executor") or llm_executor
    else:
        run_id = run_id or new_run_id(runs_dir)
        run_dir = runs_dir / run_id
        if not dry_run:
            ensure_run_tree(run_dir)
        defaults = load_defaults(agent_root)
        params = merge_params(manifest, defaults, param_overrides)
        completed = set()
        # 解析 llm_executor：CLI > env > defaults.yaml > 硬编码 "claude-p"
        if llm_executor is None:
            llm_executor = os.environ.get("IX_LLM_EXECUTOR") or defaults.get("llm_executor")
        state = {
            "run_id": run_id,
            "started_at": datetime.now(_TZ).isoformat(),
            "agent_id": agent_id,
            "trigger": trigger,
            "status": "running",
            "llm_executor": llm_executor,
            "params": params,
            "steps_completed": [],
            "next_step": None,
        }
        if not dry_run:
            save_yaml(run_dir / "run.yaml", state)

    steps = manifest.get("steps") or []
    if not steps:
        raise ValueError("manifest.steps 为空")

    for step in steps:
        sid = step["id"]
        if sid in completed:
            continue
        stype = step.get("type")
        # tool step 的 params 做 shlex.quote（防 shell 注入）；thinking step 用原文（prompt 可读）
        ctx = build_context(
            run_id=run_id,
            agent_root=agent_root,
            run_dir=run_dir,
            artifacts_root=ARTIFACTS_ROOT,
            workspace_root=INDEXED_ROOT,
            params=params,
            quote_params=(stype == "tool"),
        )
        state["next_step"] = sid
        if not dry_run:
            save_yaml(run_dir / "run.yaml", state)

        try:
            if stype == "tool":
                run_tool_step(step, ctx=ctx, run_dir=run_dir, dry_run=dry_run)
            elif stype == "thinking":
                run_thinking_step(
                    step,
                    manifest=manifest,
                    agent_root=agent_root,
                    run_dir=run_dir,
                    run_id=run_id,
                    params=params,
                    llm_bin=llm_bin,
                    llm_executor=llm_executor,
                    dry_run=dry_run,
                )
            else:
                raise ValueError(f"未知 step type: {stype}")
        except Exception:
            state["status"] = "failed"
            if not dry_run:
                save_yaml(run_dir / "run.yaml", state)
            raise

        completed.add(sid)
        state["steps_completed"] = list(completed)  # 保持执行顺序，不用 sorted()
        state["next_step"] = None
        if not dry_run:
            save_yaml(run_dir / "run.yaml", state)

    state["status"] = "completed"
    if not dry_run:
        save_yaml(run_dir / "run.yaml", state)
    return run_dir
