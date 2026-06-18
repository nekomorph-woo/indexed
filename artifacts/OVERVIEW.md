# artifacts

> **权威规范**：[`CLAUDE.md`](../CLAUDE.md) §3.5、§5.3 + [`.claude/rules/artifacts.md`](../.claude/rules/artifacts.md)  
> **Agent 能力发现**：[`capabilities.md`](capabilities.md)（做大应用/流水线前 **先 Read**，按意图匹配模块）  
> 新建 artifact 时 Agent **直接按 rule 执行**，无需重复解释架构。

可运行 **CLI 小工具**（默认命名 **`ix-<domain>-cli`**）。每个 cli 的能力声明在自身目录的 **`SPEC.yaml`**（机器真相源，scanner 读它做审计/sync）。

## 与其它桶

| 桶 | 放什么 |
|----|--------|
| `research/` | 调研文档（WHY） |
| **`artifacts/`** | 可执行 CLI（HOW） |
| `_shared/repos/` | 只读 clone（参考源码，禁止改/构建） |
| `reports/` | 报告定稿 |

## 命名

- 默认：**`ix-<domain>-cli`** → `ix-metabase-cli`、`ix-mail-cli`
- 同域新能力 → 同目录加 `providers/` + 子命令
- 新域 → 新 artifact；**禁止**跨 artifact `import`

## 标准骨架

```
artifacts/ix-<domain>-cli/
├── main.py              # 子命令入口
├── config.py            # 环境变量 / .env
├── session.py           # 可选：登录、连接
├── providers/<name>.py  # 一种能力；provider 间零互引
├── SPEC.yaml            # 机器可读能力声明（真相源，必须）
├── requirements.txt
├── .env.example
└── .gitignore           # .env、output/、__pycache__/
```

> cli 不需要单独的人类可读文档——用户询问时 AI 读 `SPEC.yaml` 并解释即可。

## 新建清单（Agent 默认）

1. `artifacts/ix-<domain>-cli/` 不存在 → 按骨架创建
2. 至少一个子命令 + 可观察成功
3. 建 **`SPEC.yaml`**（字段规范见 [`capability-spec.spec.md`](../_shared/specs/capability/capability-spec.spec.md)）
4. 更新**本文件**索引表与 **[`capabilities.md`](capabilities.md)**
5. 跑 `python artifacts/ix-workspace-index-cli/main.py sync` 同步索引
6. 不写 `.env` 真实密钥进 Git

## 工具索引 — 框架内置

<!-- IX_FRAMEWORK_CLI_INDEX_BEGIN -->
| 工具 | 子命令 | 说明 |
|------|--------|------|
| [`ix-agent-run-cli/`](ix-agent-run-cli/) | `run --agent …` | 统一执行 `ix-*-agent` manifest（TUI 与定时同命令） |
| [`ix-workspace-index-cli/`](ix-workspace-index-cli/) | `audit` / `list` / `sync` | capabilities/registry 与磁盘一致性审计 + 索引同步 |
| [`ix-init-cli/`](ix-init-cli/) | `init` / `update` / `status` | 工作区初始化（git 模式 + 昵称）+ 基线更新 |
<!-- IX_FRAMEWORK_CLI_INDEX_END -->

## 工具索引 — 用户自建

<!-- IX_USER_CLI_INDEX_BEGIN -->
<!-- 用户自建 cli 的索引行由 sync 自动维护 -->
<!-- IX_USER_CLI_INDEX_END -->

---

## 基线 CLI 深度说明

> 以下内容原分散在各 cli 的 SPEC.md 中，现统一归档于此（SPEC.md 已删除，SPEC.yaml 是唯一能力真相源）。

### ix-agent-run-cli

**thinking 执行器**：thinking step 固定调用 Claude Code CLI：`claude -p <prompt> --dangerously-skip-permissions`，`cwd` 设为 run 目录。`run.yaml` 记录 `llm_executor` 字段，`--resume` 时自动恢复。

**与 ix-agents 的关系**：

| 组件 | 职责 |
|------|------|
| `manifest.yaml` | 编排：params、steps 顺序、thinking prompt |
| `config/defaults.yaml` | 跨 run 默认参数 |
| `runs/<run-id>/` | 当次产物与 `run.yaml` 状态 |
| **ix-agent-run-cli** | 读 manifest，顺序执行，写 `run.yaml` |

**占位符**（manifest 的 `command` / `prompt` 可用）：

`{run_id}` `{work_raw}` `{work_thinking}` `{run_output}` `{run_inbox}` `{artifacts_root}` `{workspace_root}` `{agent_root}` `{params.<name>}`

### ix-init-cli

**两种 Git 模式**：

| 模式 | 行为 |
|------|------|
| `local` | 纯本地版本库；commit 后不提示 push |
| `remote` | 含远端；commit 后可 push；需配置 origin |

**个性化**：init 时设置助手昵称（默认 `Xi酱`）和对用户称呼（默认 `您`），写入 CLAUDE.md 的 `IX_PERSONA` 标记区。

**基线更新（update）三类处理**：

| 类别 | 文件 | 行为 |
|------|------|------|
| 标记区保护 | capabilities.md / registry.md / 桶 OVERVIEW / CLAUDE.md / git-workflow.md | 抽取用户标记区 → 覆盖 → 回灌（不丢用户内容） |
| 框架覆盖 | .claude/rules/、_shared/、基线 3 个 ix-*-cli、VERSION、.gitignore | 直接覆盖 |
| 用户跳过 | research/、reports/、用户自建 cli/agent、_shared/repos/ | 整体跳过 |

**标记区机制**：`<!-- IX_<NAME>_BEGIN -->...<!-- IX_<NAME>_END -->` 之间的内容可被 init/update 精确改写，文件其余部分不动。

### ix-workspace-index-cli

**何时跑**：

| 时机 | 谁执行 |
|------|--------|
| 新建或显著变更 `ix-*-cli` / `ix-*-agent` 后 | Agent 同任务内（commit 前） |
| ix-agent 阶段 B 创建 agent 完成后 | Agent |
| 用户说「审计索引」「同步 capabilities」 | Agent |

**audit 只诊断不写文件**；**sync 会写**——把用户 SPEC.yaml 自动同步到薄索引的 `IX_USER_*` 标记区。

**检查项**：SPEC.yaml 存在性、薄索引覆盖与孤儿检测、agent 的 has_thinking/steps 与 manifest 一致性。
