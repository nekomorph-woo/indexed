# ix-agents

> **权威规范**：[`CLAUDE.md`](../CLAUDE.md) §3.6、§5.4 + [`.claude/rules/ix-agents.md`](../.claude/rules/ix-agents.md)  
> **新建 / 执行流程**：ix-agent 两阶段（`.claude/rules/ix-agents.md`；skill 待迁移）  
> **统一执行器**：[`artifacts/ix-agent-run-cli/`](../artifacts/ix-agent-run-cli/)  
> **应用发现**：[`registry.md`](registry.md)

组合多个 `artifacts/ix-*-cli` 的业务 Agent；**流程编排在 manifest，执行在 run-cli**。

## 与其它桶

| 桶 | 角色 |
|----|------|
| `artifacts/ix-*-cli` | 原子 CLI（tool step） |
| **`artifacts/ix-agent-run-cli`** | 读 manifest，顺序跑 tool + thinking（`claude -p`） |
| **`ix-agents/ix-*-agent/`** | `manifest.yaml` + `config/` + `runs/` |
| `research/` | WHY |
| `reports/` | 长期定稿（从 `runs/.../output/` 归档） |

## 执行方式（TUI = 定时）

```powershell
# 工作区根目录
python artifacts/ix-agent-run-cli/main.py --agent ix-<business>-agent
```

Claude Code 中说「执行 agent」→ Agent 运行**上述同一条命令**并汇报结果（见 [`.claude/rules/ix-agents.md`](../.claude/rules/ix-agents.md)）。

## 目录作用（每个 agent）

| 路径 | 说明 |
|------|------|
| `manifest.yaml` | **唯一编排**：params、steps（`tool` \| `thinking`） |
| `config/defaults.yaml` | 跨 run 默认参数 |
| `README.md` | 本 agent 说明与示例 |
| `paths.py` | 可选路径 helper |
| `scripts/` | 可选，仅本 agent 的 glue（tool Shell 调用） |
| `runs/<run-id>/` | 当次产物（gitignore） |

## runs 时间隔离

每次运行：`runs/YYYY-MM-DD_HH-mm-ss/` → `run.yaml` · `inbox/` · `work/raw/` · `work/thinking/` · `output/`

## 新建 agent

ix-agent 流程或说「新建 lc agent」→ 阶段 B 从 [`_shared/templates/ix-agents/`](../_shared/templates/ix-agents/) 复制 → 更新 [`registry.md`](registry.md)。

## 定时（专用 — 硬约束）

**凡本桶 agent 的定时，仅通过 [`schedule/`](schedule/)**；禁止在 agent 目录或其它桶自建计划任务。

- 说明：[`schedule/README.md`](schedule/README.md)
- 登记：[`schedule/registry.yaml`](schedule/registry.yaml)
- 执行：`invoke-job.ps1 -JobId <id>`
- 注册 Windows 任务：`schedule/register-windows-task.ps1 -JobId <id>`

## 应用索引 — 框架内置

<!-- IX_FRAMEWORK_AGENT_INDEX_BEGIN -->
<!-- 框架内置 agent 索引行（基线维护，update 时覆盖） -->
<!-- IX_FRAMEWORK_AGENT_INDEX_END -->

## 应用索引 — 用户自建

<!-- IX_USER_AGENT_INDEX_BEGIN -->
<!-- 用户自建 agent 由 sync 自动维护 -->
<!-- IX_USER_AGENT_INDEX_END -->
