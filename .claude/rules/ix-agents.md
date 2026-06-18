# ix-agents — 组合业务 Agent

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §3.6、§5.4。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 编排与执行

- **编排**：仅 **`manifest.yaml`**（`params` + 顺序 `steps`）。
- **执行**：**`artifacts/ix-agent-run-cli`**（TUI 与定时 **同一条命令**）；`thinking` 由 run-cli 调 **`claude -p`** + manifest `prompt`。

| 说明 | 约定 |
|------|------|
| **用途** | 多步组合；`tool` = Shell / `ix-*-cli`；`thinking` = `claude -p` 落盘 `work/thinking/` |
| **命名** | 桶 **`ix-agents/`**；应用 **`ix-<business>-agent`** |
| **路径** | 每次 **`runs/<run-id>/`**（北京时间隔离）；跨 run 默认 **`config/`** |
| **执行命令** | `python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent` |
| **母版 / 新建** | `_shared/templates/ix-agents/` + ix-agent 两阶段流程 |
| **耦合** | tool：**Shell** 调 `ix-*-cli` 或 agent `scripts/`；禁止 import artifacts |
| **发现** | [`ix-agents/registry.md`](../../ix-agents/registry.md) → 本文件 |

## 禁止与允许

**禁止**：
- `orchestrate.py`（流程写死在 Python）
- agent 根下无 run 隔离的 `work/`/`output/`
- agent 内自编排 import
- **未经用户明确要求，禁止在 manifest 中增加归档到 `reports/` 的 step**——agent 产出默认留在 `runs/<run-id>/output/`；只有用户明确说「归档」「存到 reports」「生成报告交付物」时才加归档 step

**允许**：`ix-agent-run-cli` 为 thinking 调用 `claude -p`（Claude Code 自动化路径）。

## 新建 `ix-<business>-agent`

1. 命名 `ix-<business>-agent`；从 [`_shared/templates/ix-agents/`](_shared/templates/ix-agents/) 复制母版
2. 业务只写入 `manifest.yaml`、`config/`、可选 `scripts/`
3. 建 **`SPEC.yaml`**（能力声明真相源；字段规范见 `capability-spec.spec.md`）
4. 跑 `python artifacts/ix-workspace-index-cli/main.py sync`（自动同步索引到 `IX_USER_*` 标记区）+ `audit --check`
5. **禁止** `orchestrate.py`

## 执行（TUI 与定时相同）

```bash
python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent [--set k=v] [--trigger scheduled] [--resume --run-id <id>]
```

由 run-cli 创建 `runs/<run-id>/`、顺序执行 steps、更新 `run.yaml`。Claude Code 中 **Shell 运行上述命令并监督**，不在对话内逐步手写 manifest。

- thinking step 默认执行器为 **`claude -p`**（Claude Code CLI）；可通过 `--llm-executor`、`IX_LLM_EXECUTOR`、`defaults.yaml` 的 `llm_executor` 覆盖。
- 详细执行器与配置见 [`artifacts/ix-agent-run-cli/SPEC.yaml`](../../artifacts/ix-agent-run-cli/SPEC.yaml) 或 [`artifacts/OVERVIEW.md`](../../artifacts/OVERVIEW.md) §基线 CLI 深度说明。

## 两阶段开发规范（核心）

ix-*-agent 是与用户交互的主要载体。用户不会记得每个 agent 需要哪些入参、哪些有默认值。
**两阶段**让 agent 对用户友好：先展示需求，等用户确认，再执行。

数据源：`manifest.yaml` 的 `params` 字段（`required` / `prompt` / `default` / `default_from`）。

### 阶段 A — 展示需求，等用户确认

用户说「执行 ix-foo-agent」但**未给齐输入**时：

1. **Read** `ix-agents/ix-foo-agent/manifest.yaml` 的 `params` 段
2. **Read** `ix-agents/ix-foo-agent/config/defaults.yaml`（若有）——标注哪些参数已获默认值
3. 向用户展示需求清单：

   ```
   ix-foo-agent 需要以下输入：

   | 参数 | 必填 | 说明 | 当前值 |
   |------|------|------|--------|
   | primary_input | ✅ | 请提供本次运行的主要输入 | （需用户提供） |
   | window_days | — | 分析窗口（天） | 7（默认） |
   ```

4. **停止**。等用户补充缺失的必填项或确认默认值。

> 关键：**不要**在缺参数时直接跑 run-cli 导致报错退出。阶段 A 的职责是让用户清楚地知道「需要提供什么」，然后等。

### 阶段 B — 用户给齐后执行

用户补充了缺失项（或确认默认值）后：

1. 将用户提供的值通过 `--set key=value` 传给 run-cli
2. 执行 `python artifacts/ix-agent-run-cli/main.py run --agent ix-foo-agent --set primary_input=xxx --set window_days=14`
3. 监督 `runs/<run-id>/` 产出

### 设计要点

- `manifest.yaml` 的 `params[].prompt` 是给用户看的提示文案——**必须写清楚业务含义**，不能只写参数名
- `params[].default` / `default_from` 让常用场景开箱即用（用户只需确认，不必每次重填）
- 阶段 A 的展示格式不强制，但必须让用户一眼看出：哪些必须提供、哪些已有默认、当前值是什么
- 定时场景（`--trigger scheduled`）跳过两阶段——参数全部从 `config/defaults.yaml` 或 schedule job 配置获取

## 定时（硬约束）

`ix-*-agent` 的定时 **仅**指 [`ix-agents/schedule/`](../../ix-agents/schedule/)（`registry.yaml` + `invoke-job.ps1` / `main.py schedule run`）。

- **禁止** Agent 自行创建其它计划任务、`schtasks` 或 per-agent 定时脚本。
- 定时执行器由 `thinking.py` 默认值（`claude-p`）决定；如需显式可控，在 schedule 作业中设 `IX_LLM_EXECUTOR=claude-p`。

## 发现（业务 Agent 前先做）

需组合业务 Agent 时，**先 Read** [`ix-agents/registry.md`](../../ix-agents/registry.md)，按意图匹配已有 `ix-*-agent`；勿重复造。

新建 cli/agent 后跑 `python artifacts/ix-workspace-index-cli/main.py sync`，自动把 SPEC.yaml 同步到薄索引的 `IX_USER_*` 标记区（框架区不动）。
