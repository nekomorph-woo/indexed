# ix-agent-run-cli — SPEC

> 组合 agent 执行器。机器可读能力声明见 [`SPEC.yaml`](SPEC.yaml)。

按 `ix-agents/ix-<business>-agent/manifest.yaml` **统一执行**组合流水线：

- **`type: tool`** — Shell 调 `artifacts/ix-*-cli` 或 agent 私有脚本；`write` / `copy` 整理文件
- **`type: thinking`** — 渲染 manifest 中的 `prompt`，调用 Claude Code CLI（`claude -p`），产出写入 `runs/<run-id>/work/thinking/`

TUI 对话执行与定时任务 / CI **使用同一条命令**，流程只维护 manifest。

## 依赖

```powershell
pip install -r requirements.txt
```

本机需已安装 **Claude Code CLI** 并在 PATH 中（或设置 `IX_CLAUDE_BIN`）。

## 用法

```powershell
# 新建 run 并跑完全部 steps（推荐子命令）
python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent

# 覆盖参数
python ...main.py run --agent ix-foo-agent --set primary_input=https://... --set window_days=14

# 指定 claude 可执行文件路径
python ...main.py run --agent ix-foo-agent --llm-bin /usr/local/bin/claude

# 定时任务（须先在 ix-agents/schedule/registry.yaml 登记）
python ...main.py schedule list
python ...main.py schedule run --job-id <job-id>

# 续跑
python ...main.py run --agent ix-foo-agent --run-id 2026-06-01_09-00-01 --resume

# 预览（不实际执行）
python ...main.py run --agent ix-foo-agent --dry-run
```

## thinking 执行器

thinking step 固定调用 **Claude Code CLI**：`claude -p <prompt> --dangerously-skip-permissions`，`cwd` 设为 run 目录。

`run.yaml` 会记录 `llm_executor` 字段，`--resume` 时自动恢复。

## 与 ix-agents 的关系

| 组件 | 职责 |
|------|------|
| `manifest.yaml` | 编排：params、steps 顺序、thinking prompt |
| `config/defaults.yaml` | 跨 run 默认参数 |
| `runs/<run-id>/` | 当次产物与 `run.yaml` 状态 |
| **本 CLI** | 读 manifest，顺序执行，写 `run.yaml` |

**禁止**在 agent 目录使用旧版 `orchestrate.py`（流程写死在 Python）。见 [`CLAUDE.md`](../../CLAUDE.md) §3.6、[`.claude/rules/ix-agents.md`](../../.claude/rules/ix-agents.md)。

## 占位符

manifest 的 `command` / `prompt` 可用：

`{run_id}` `{work_raw}` `{work_thinking}` `{run_output}` `{run_inbox}` `{artifacts_root}` `{workspace_root}` `{agent_root}` `{params.<name>}`

## 规范

- [`CLAUDE.md`](../../CLAUDE.md) §3.6
- [`.claude/rules/ix-agents.md`](../../.claude/rules/ix-agents.md)
- 能力声明：[`SPEC.yaml`](SPEC.yaml)（真相源）
- 新建 agent：ix-agent 两阶段流程（见 `.claude/rules/ix-agents.md`；skill 待迁移）
