"""扫描 indexed 内 ix-*-cli / ix-*-agent 运行时真相。

真相源：各 cli/agent 目录下的 SPEC.yaml（机器可读能力声明）。
薄索引页（capabilities.md / registry.md）是派生物，本模块校验其与 SPEC.yaml 的一致性。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = WORKSPACE_ROOT / "artifacts"
AGENTS_DIR = WORKSPACE_ROOT / "ix-agents"
RESEARCH_DIR = WORKSPACE_ROOT / "research"
SHARED_SPECS_DIR = WORKSPACE_ROOT / "_shared" / "specs"
SHARED_TEMPS_DIR = WORKSPACE_ROOT / "_shared" / "templates"
RULES_DIR = WORKSPACE_ROOT / ".claude" / "rules"
CLAUDE_MD = WORKSPACE_ROOT / "CLAUDE.md"
CAPABILITIES_PATH = ARTIFACTS_DIR / "capabilities.md"
REGISTRY_PATH = AGENTS_DIR / "registry.md"
ARTIFACTS_README = ARTIFACTS_DIR / "OVERVIEW.md"
AGENTS_README = AGENTS_DIR / "OVERVIEW.md"

CLI_DIR_RE = re.compile(r"^ix-.+-cli$")
AGENT_DIR_RE = re.compile(r"^ix-.+-agent$")
SUBPARSER_RE = re.compile(r'\.add_parser\(\s*["\']([^"\']+)["\']')
# 薄索引页中匹配 cli/agent 名出现（任何形式：代码、链接、表格）
CLI_NAME_RE = re.compile(r"\b(ix-[a-z0-9]+(?:-[a-z0-9]+)*-cli)\b")
AGENT_NAME_RE = re.compile(r"\b(ix-[a-z0-9]+(?:-[a-z0-9]+)*-agent)\b")


@dataclass
class CliInfo:
    name: str
    path: Path
    subcommands: list[str] = field(default_factory=list)
    has_spec_yaml: bool = False
    spec: dict[str, Any] | None = None  # SPEC.yaml 解析结果


@dataclass
class AgentInfo:
    name: str
    path: Path
    step_ids: list[str] = field(default_factory=list)
    step_types: dict[str, str] = field(default_factory=dict)
    has_thinking: bool = False
    required_params: list[str] = field(default_factory=list)
    research: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    has_spec_yaml: bool = False
    spec: dict[str, Any] | None = None


@dataclass
class IndexIssue:
    level: str  # error | warn
    code: str
    message: str
    target: str | None = None


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """读 SPEC.yaml；无 PyYAML 时用简易解析提取关键字段（name/status）。"""
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8", errors="replace")
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    # 降级：简易解析（足够判断 name、status 存在性）
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        m = re.match(r"^(\w+):\s*(\S+)", line)
        if m:
            data[m.group(1)] = m.group(2)
    return data if data else None


def discover_clis() -> list[CliInfo]:
    out: list[CliInfo] = []
    if not ARTIFACTS_DIR.is_dir():
        return out
    for d in sorted(ARTIFACTS_DIR.iterdir()):
        if not d.is_dir() or not CLI_DIR_RE.match(d.name):
            continue
        main_py = d / "main.py"
        subs: list[str] = []
        if main_py.is_file():
            text = main_py.read_text(encoding="utf-8", errors="replace")
            subs = sorted(set(SUBPARSER_RE.findall(text)))
        spec = _load_yaml(d / "SPEC.yaml")
        out.append(
            CliInfo(
                name=d.name,
                path=d,
                subcommands=subs,
                has_spec_yaml=spec is not None,
                spec=spec,
            )
        )
    return out


def discover_agents() -> list[AgentInfo]:
    out: list[AgentInfo] = []
    if not AGENTS_DIR.is_dir():
        return out
    for d in sorted(AGENTS_DIR.iterdir()):
        if not d.is_dir() or not AGENT_DIR_RE.match(d.name):
            continue
        manifest = d / "manifest.yaml"
        info = AgentInfo(name=d.name, path=d)
        if manifest.is_file():
            _load_manifest(manifest, info)
        spec = _load_yaml(d / "SPEC.yaml")
        info.has_spec_yaml = spec is not None
        info.spec = spec
        out.append(info)
    return out


def _load_manifest(path: Path, info: AgentInfo) -> None:
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(raw) or {}
    else:
        data = _manifest_fallback(raw)
    info.research = data.get("research")
    for spec in data.get("params") or []:
        if isinstance(spec, dict) and spec.get("required"):
            info.required_params.append(str(spec.get("name", "")))
    for ref in data.get("artifacts") or []:
        info.artifact_refs.append(str(ref))
    for step in data.get("steps") or []:
        if not isinstance(step, dict):
            continue
        sid = str(step.get("id", ""))
        if not sid:
            continue
        stype = str(step.get("type", "tool"))
        info.step_ids.append(sid)
        info.step_types[sid] = stype
        if stype == "thinking":
            info.has_thinking = True


def _manifest_fallback(raw: str) -> dict:
    """无 PyYAML 时仅解析 steps 的 id/type。"""
    steps = []
    for m in re.finditer(
        r"- id:\s*(\S+)\s*\n\s*type:\s*(\w+)",
        raw,
    ):
        steps.append({"id": m.group(1), "type": m.group(2)})
    research = None
    rm = re.search(r"^research:\s*(\S+)\s*$", raw, re.M)
    if rm:
        research = rm.group(1)
    return {"steps": steps, "research": research, "params": [], "artifacts": []}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _names_in_text(text: str, pattern: re.Pattern[str]) -> set[str]:
    """从文本中提取所有匹配的 cli/agent 名（排除占位符）。"""
    names = set(pattern.findall(text))
    return {n for n in names if "<" not in n}


def audit_index() -> tuple[list[CliInfo], list[AgentInfo], list[IndexIssue]]:
    """以 SPEC.yaml 为真相源，校验薄索引页与磁盘一致性。"""
    clis = discover_clis()
    agents = discover_agents()
    issues: list[IndexIssue] = []

    cap_text = _read(CAPABILITIES_PATH)
    reg_text = _read(REGISTRY_PATH)

    cap_cli_names = _names_in_text(cap_text, CLI_NAME_RE)
    reg_agent_names = _names_in_text(reg_text, AGENT_NAME_RE)

    cli_by_name = {c.name: c for c in clis}
    agent_by_name = {a.name: a for a in agents}

    # --- CLI 校验 ---
    for c in clis:
        # SPEC.yaml 是能力真相源，必须有
        if not c.has_spec_yaml:
            issues.append(
                IndexIssue("error", "cli_missing_spec_yaml", f"{c.name} 缺少 SPEC.yaml（能力真相源）", c.name)
            )
        # 必须出现在 capabilities.md 薄索引
        if c.name not in cap_cli_names:
            issues.append(
                IndexIssue(
                    "error",
                    "cli_missing_in_capabilities",
                    f"{c.name} 未出现在 capabilities.md 薄索引",
                    c.name,
                )
            )

    # capabilities.md 孤儿登记（指向不存在的 cli）
    for name in cap_cli_names:
        if name not in cli_by_name:
            issues.append(
                IndexIssue(
                    "error",
                    "capabilities_stale_cli",
                    f"capabilities.md 登记了不存在的目录 {name}",
                    name,
                )
            )

    # --- Agent 校验 ---
    for a in agents:
        if not a.has_spec_yaml:
            issues.append(
                IndexIssue("error", "agent_missing_spec_yaml", f"{a.name} 缺少 SPEC.yaml（能力真相源）", a.name)
            )
        if a.name not in reg_agent_names:
            issues.append(
                IndexIssue(
                    "error",
                    "agent_missing_in_registry",
                    f"{a.name} 未出现在 registry.md 薄索引",
                    a.name,
                )
            )

    # registry.md 孤儿登记
    for name in reg_agent_names:
        if name not in agent_by_name:
            issues.append(
                IndexIssue(
                    "error",
                    "registry_stale_agent",
                    f"registry.md 登记了不存在的目录 {name}",
                    name,
                )
            )

    return clis, agents, issues


# ---------------------------------------------------------------------------
# 规范治理审计（spec-governance）
# ---------------------------------------------------------------------------

_GOVERNANCE_KEYWORDS: dict[str, list[str]] = {
    "禁止构建": ["禁止构建", "禁止编译", "禁止打包", "禁止安装依赖"],
    "禁止 mermaid": ["禁止 mermaid"],
    "禁止 orchestrate": ["禁止 orchestrate", "禁止 `orchestrate"],
}


def _collect_rule_files() -> list[Path]:
    """收集所有 .claude/rules/*.md 和 CLAUDE.md。"""
    files = list(RULES_DIR.glob("*.md"))
    if CLAUDE_MD.is_file():
        files.append(CLAUDE_MD)
    return files


def _keyword_count(files: list[Path], phrase: str) -> list[tuple[str, int]]:
    counts: list[tuple[str, int]] = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        n = text.count(phrase)
        if n > 0:
            counts.append((f.name, n))
    return counts


def _check_duplicate_keywords(files: list[Path], issues: list[IndexIssue]) -> None:
    for label, phrases in _GOVERNANCE_KEYWORDS.items():
        for phrase in phrases:
            hits = _keyword_count(files, phrase)
            hits = [(name, cnt) for name, cnt in hits if Path(name).stem != "spec-governance"]
            file_count = len(hits)
            if file_count >= 4:
                file_names = ", ".join(h[0] for h in hits)
                issues.append(
                    IndexIssue(
                        "warn",
                        "governance_duplicate_keyword",
                        f"「{phrase}」出现在 {file_count} 个文件（{file_names}），考虑统一到权威文件",
                        None,
                    )
                )


def _check_claude_md_length(issues: list[IndexIssue]) -> None:
    """CLAUDE.md 行数 >300 告警。"""
    if not CLAUDE_MD.is_file():
        return
    lines = CLAUDE_MD.read_text(encoding="utf-8", errors="replace").splitlines()
    line_count = len(lines)
    if line_count > 300:
        issues.append(
            IndexIssue(
                "warn",
                "governance_claude_md_too_long",
                f"CLAUDE.md 共 {line_count} 行，超过 300 行建议精简",
                "CLAUDE.md",
            )
        )


def _check_cross_refs(files: list[Path], issues: list[IndexIssue]) -> None:
    """检查 rule 中「见 §X.Y」引用是否指向 CLAUDE.md 中的有效章节。"""
    if not CLAUDE_MD.is_file():
        return
    claude_text = CLAUDE_MD.read_text(encoding="utf-8", errors="replace")
    section_re = re.compile(r"^#{2,4}\s+(\d+(?:\.\d+)?)\b", re.M)
    valid_sections = set(section_re.findall(claude_text))

    ref_re = re.compile(r"§(\d+(?:\.\d+)?)")
    for f in files:
        if f == CLAUDE_MD:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for m in ref_re.finditer(text):
            section = m.group(1)
            if section not in valid_sections:
                issues.append(
                    IndexIssue(
                        "error",
                        "governance_invalid_xref",
                        f"{f.name} 引用「§{section}」但 CLAUDE.md 中无此章节",
                        f.name,
                    )
                )


def _check_shared_paths(issues: list[IndexIssue]) -> None:
    """检查桶级 README 是否存在。"""
    bucket_readmes = [
        WORKSPACE_ROOT / "reports" / "OVERVIEW.md",
        WORKSPACE_ROOT / "research" / "OVERVIEW.md",
        WORKSPACE_ROOT / "artifacts" / "OVERVIEW.md",
        WORKSPACE_ROOT / "ix-agents" / "OVERVIEW.md",
        SHARED_SPECS_DIR / "OVERVIEW.md",
        SHARED_TEMPS_DIR / "OVERVIEW.md",
        WORKSPACE_ROOT / "_shared" / "design-languages" / "OVERVIEW.md",
    ]
    for p in bucket_readmes:
        if not p.is_file():
            rel = p.relative_to(WORKSPACE_ROOT)
            issues.append(
                IndexIssue(
                    "warn",
                    "governance_missing_bucket_readme",
                    f"桶级 README 缺失: {rel}",
                    str(rel),
                )
            )


def audit_governance() -> list[IndexIssue]:
    issues: list[IndexIssue] = []
    rule_files = _collect_rule_files()
    _check_duplicate_keywords(rule_files, issues)
    _check_claude_md_length(issues)
    _check_cross_refs(rule_files, issues)
    _check_shared_paths(issues)
    return issues


def steps_summary(agent: AgentInfo) -> str:
    parts = []
    for sid in agent.step_ids:
        st = agent.step_types.get(sid, "tool")
        if st == "thinking":
            parts.append(f"{sid}(thinking)")
        elif sid.startswith("publish") or sid == "archive_report":
            continue
        else:
            parts.append(sid.replace("_", "-"))
    return " → ".join(parts)


def manifest_snapshot(agent: AgentInfo) -> dict:
    return {
        "required_params": agent.required_params,
        "has_thinking": agent.has_thinking,
        "steps_summary": steps_summary(agent),
        "step_ids": agent.step_ids,
        "research": agent.research,
        "artifacts": agent.artifact_refs,
        "has_spec_yaml": agent.has_spec_yaml,
    }


# ---------------------------------------------------------------------------
# sync：把 SPEC.yaml 真相同步到薄索引的 IX_USER_* 标记区
# ---------------------------------------------------------------------------

# 基线 cli（框架内置，不在用户区登记）
BASELINE_CLIS = {"ix-agent-run-cli", "ix-workspace-index-cli", "ix-init-cli", "ix-schedule-cli"}

_ZONE_RE = re.compile(
    r"(<!--\s*IX_(\w+)_BEGIN\s*-->)([\s\S]*?)(<!--\s*IX_\2_END\s*-->)"
)


def _replace_zone(text: str, zone_name: str, new_content: str) -> str:
    pattern = re.compile(
        r"(<!--\s*IX_" + re.escape(zone_name) + r"_BEGIN\s*-->)([\s\S]*?)(<!--\s*IX_"
        + re.escape(zone_name) + r"_END\s*-->)"
    )
    return pattern.sub(lambda m: m.group(1) + new_content + m.group(3), text, count=1)


def _spec_field(spec: dict | None, key: str, default: str = "") -> str:
    """从 SPEC.yaml 取字段，降级时返回 default。"""
    if not spec:
        return default
    val = spec.get(key, default)
    return str(val) if val is not None else default


def _gen_cli_rows(user_clis: list[CliInfo]) -> str:
    """根据用户 cli 的 SPEC.yaml 生成索引表行（markdown）。"""
    if not user_clis:
        return "<!-- 用户自建 cli 的索引行由 sync 自动维护 -->\n"
    lines = ["| 用户意图或关键词 | 模块 | 一句话 | 详情 |",
             "|------------------|------|--------|------|"]
    for c in user_clis:
        one_liner = _spec_field(c.spec, "one_liner", c.name)
        first_intent = ""
        if c.spec and isinstance(c.spec.get("intents"), list) and c.spec["intents"]:
            first_intent = str(c.spec["intents"][0])
        lines.append(
            f"| {first_intent or c.name} | `{c.name}` | {one_liner} | "
            f"[`SPEC.yaml`]({c.name}/SPEC.yaml) |"
        )
    return "\n".join(lines) + "\n"


def _gen_agent_rows(user_agents: list[AgentInfo]) -> str:
    """根据用户 agent 的 SPEC.yaml 生成索引表行。"""
    if not user_agents:
        return "<!-- 用户自建 agent 由 sync 自动维护 -->\n"
    lines = ["| 用户意图或关键词 | 应用 | 一句话 | 详情 |",
             "|------------------|------|--------|------|"]
    for a in user_agents:
        one_liner = _spec_field(a.spec, "one_liner", a.name)
        first_intent = ""
        if a.spec and isinstance(a.spec.get("intents"), list) and a.spec["intents"]:
            first_intent = str(a.spec["intents"][0])
        lines.append(
            f"| {first_intent or a.name} | `{a.name}` | {one_liner} | "
            f"[`SPEC.yaml`]({a.name}/SPEC.yaml) |"
        )
    return "\n".join(lines) + "\n"


def sync_indexes() -> dict[str, int]:
    """把用户 cli/agent 的 SPEC.yaml 同步到薄索引的 IX_USER_* 标记区。

    返回 {文件名: 写入行数} 的摘要。
    """
    all_clis = discover_clis()
    all_agents = discover_agents()
    user_clis = [c for c in all_clis if c.name not in BASELINE_CLIS and c.spec]
    user_agents = [a for a in all_agents if a.spec]

    results: dict[str, int] = {}

    # capabilities.md → IX_USER_CLI_INDEX
    cap_path = ARTIFACTS_DIR / "capabilities.md"
    if cap_path.is_file():
        text = cap_path.read_text(encoding="utf-8")
        rows = _gen_cli_rows(user_clis)
        new_text = _replace_zone(text, "USER_CLI_INDEX", "\n" + rows)
        if new_text != text:
            cap_path.write_text(new_text, encoding="utf-8")
            results["capabilities.md"] = len(user_clis)

    # artifacts/OVERVIEW.md → IX_USER_CLI_INDEX
    art_readme = ARTIFACTS_DIR / "OVERVIEW.md"
    if art_readme.is_file():
        text = art_readme.read_text(encoding="utf-8")
        rows = _gen_cli_rows(user_clis)
        new_text = _replace_zone(text, "USER_CLI_INDEX", "\n" + rows)
        if new_text != text:
            art_readme.write_text(new_text, encoding="utf-8")
            if "OVERVIEW.md" not in results:
                results["artifacts/OVERVIEW.md"] = len(user_clis)

    # registry.md → IX_USER_AGENT_INDEX
    reg_path = AGENTS_DIR / "registry.md"
    if reg_path.is_file():
        text = reg_path.read_text(encoding="utf-8")
        rows = _gen_agent_rows(user_agents)
        new_text = _replace_zone(text, "USER_AGENT_INDEX", "\n" + rows)
        if new_text != text:
            reg_path.write_text(new_text, encoding="utf-8")
            results["registry.md"] = len(user_agents)

    # ix-agents/OVERVIEW.md → IX_USER_AGENT_INDEX
    agents_readme = AGENTS_DIR / "OVERVIEW.md"
    if agents_readme.is_file():
        text = agents_readme.read_text(encoding="utf-8")
        rows = _gen_agent_rows(user_agents)
        new_text = _replace_zone(text, "USER_AGENT_INDEX", "\n" + rows)
        if new_text != text:
            agents_readme.write_text(new_text, encoding="utf-8")
            if "ix-agents/OVERVIEW.md" not in results:
                results["ix-agents/OVERVIEW.md"] = len(user_agents)

    # research/OVERVIEW.md → IX_USER_TOPICS
    research_overview = RESEARCH_DIR / "OVERVIEW.md"
    if research_overview.is_file() and RESEARCH_DIR.is_dir():
        # 扫描 research 下的专题目录（排除 OVERVIEW.md 等非目录文件）
        topics = []
        if RESEARCH_DIR.is_dir():
            topics = sorted([
                d.name for d in RESEARCH_DIR.iterdir()
                if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("_")
            ])
        if topics:
            lines = ["| 专题 | 说明 |", "|------|------|"]
            for topic in topics:
                lines.append(f"| `{topic}/` | （见专题内 docs/） |")
            rows = "\n".join(lines) + "\n"
        else:
            rows = "<!-- 用户专题由 sync 自动维护 -->\n"
        text = research_overview.read_text(encoding="utf-8")
        new_text = _replace_zone(text, "USER_TOPICS", "\n" + rows)
        if new_text != text:
            research_overview.write_text(new_text, encoding="utf-8")
            results["research/OVERVIEW.md"] = len(topics)

    return results
