# registry — Agent 应用薄索引（Agent 发现用）

> **何时 Read**：组合业务、多步分析、定时报表 Agent——先于 `artifacts/capabilities.md`。
> **如何执行**：`python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent`（TUI 与定时相同）。
> **如何新建**：ix-agent 两阶段流程（见 [`.claude/rules/ix-agents.md`](../.claude/rules/ix-agents.md)；skill 待迁移）。

> **能力详情**：每个 agent 的完整能力声明在其目录下的 `SPEC.yaml`（真相源）。本文件只做意图→应用的薄映射。
> 规范：[`capability-spec.spec.md`](../_shared/specs/capability/capability-spec.spec.md) · [`CLAUDE.md`](../CLAUDE.md) §3.6

---

## 按意图速查 — 框架内置

<!-- IX_FRAMEWORK_AGENT_INDEX_BEGIN -->
<!-- 框架内置 agent 索引行（基线维护，update 时覆盖） -->
<!-- IX_FRAMEWORK_AGENT_INDEX_END -->

## 按意图速查 — 用户自建

<!-- IX_USER_AGENT_INDEX_BEGIN -->
| 用户意图或关键词 | 应用 | 一句话 | 详情 |
|------------------|------|--------|------|
| 发版、release、打包发布、bump version、新版本 | `ix-release-agent` | indexed 基线发版全流程编排（migration + bump + bundle + build + commit/tag + release） | [`SPEC.yaml`](ix-release-agent/SPEC.yaml) |
<!-- IX_USER_AGENT_INDEX_END -->

---

## Agent 决策流程

```
组合业务？
  ├─ Read 本 registry → 有匹配 ix-*-agent
  │     → ix-agent-run-cli run --agent ...
  ├─ 无 → Read artifacts/capabilities.md（原子 cli）
  └─ 仍无 → ix-agent 两阶段流程新建（.claude/rules/ix-agents.md）
```

---

## 维护

新建/变更后：在 agent 目录建/改 `SPEC.yaml` → 跑 `python artifacts/ix-workspace-index-cli/main.py sync`（自动同步到本文件「意图速查」与 [`OVERVIEW.md`](OVERVIEW.md) 的 IX_USER_AGENT_INDEX 标记区）。
跑 `python artifacts/ix-workspace-index-cli/main.py audit --check` 校验一致性。
**定时**：见 [`ix-schedule-cli`](../artifacts/ix-schedule-cli/)（跨平台定时执行器）。
