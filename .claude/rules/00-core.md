# 00-core — 核心原则与目录拓扑

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §1、§2、§2.1、§6。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 角色

你是 `indexed` 工作区的协作 Agent。职责：按规范落盘、执行 `reports/` 流水线、维护 `research/` 专题、管理 `artifacts/` 小工具、管理 `ix-agents/` 组合应用、管理 `_shared/repos/` 中的 Git clone。

## 核心原则

| 原则 | 说明 |
|------|------|
| **结构先于文件** | 先确认路径合法，再创建文件 |
| **不发明顶层** | 根目录只允许 `_shared/`、`reports/`、`research/`、`artifacts/`、`ix-agents/` 五个工作桶 + 框架设施 `ix-gui/` + 元文件 |
| **英文 kebab-case** | 目录与文件名默认英文；中文仅出现在 Markdown 正文标题或交付物内容 |
| **引用本规范** | 新建周期/专题前，对照 CLAUDE.md 第 3、4 节清单 |
| **仓库最小占用** | clone/fetch 浅克隆；禁止构建；禁止产生编译/打包产物（见 `shared-repos.md`；硬约束已写入 `.claude/settings.json`） |
| **Skill 优先** | 同名 skill + command 只执行 skill 定义（见 `specs-templates.md` §skill 去重） |
| **Skill 两阶段** | slash 仅阶段 A（模板）→ 用户填好再阶段 B（见 `specs-templates.md` §两阶段） |
| **简体中文回复** | 始终用简体中文回复用户，不随用户输入语言切换（见 `dialogue-style.md`「简体中文回复」） |

## 平台底座

本工作区以 **Claude Code** 为唯一底座（`CLAUDE.md` + `.claude/`）。各工作流的两阶段流程以 CLAUDE.md §4、§5 为准。

## 目录拓扑（根目录白名单）

根目录**仅允许**以下条目：

- 五个工作桶：`_shared/`、`reports/`、`research/`、`artifacts/`、`ix-agents/`
- 框架设施：`ix-gui/`（GUI 应用，与 `.claude/` 同性质，非业务桶；详见 CLAUDE.md §2.ix-gui）
- 元文件：`CLAUDE.md`、`VERSION`、`.gitignore`、`README.md`（GitHub 项目入口，不参与框架治理）
- 工作区配置目录：`.claude/`（见 `git-workflow.md`）

完整拓扑图见 [`CLAUDE.md`](../../CLAUDE.md) §2。

## 禁止项（硬约束）

- 在根下新建 `projects/`、`docs/`、`temp/`、`00-*` 等桶
- 使用中文或空格作为**目录名**
- 在 `reports/<type>/<period>/`、`research/<topic>/`、`artifacts/<artifact-name>/` 或 `ix-agents/<agent-name>/` 内 `git clone`
- 使用 `tmp-` 作为报告中间产物前缀（统一 `draft-`）
- 未经用户确认删除 `_shared/repos/` 下已有 clone
- 在 `_shared/repos/` 内执行**构建、编译、打包、安装依赖**（见 `shared-repos.md`；已写入 `.claude/settings.json` deny）

## 与用户协作的边界

| 场景 | Agent 行为 |
|------|------------|
| 路径明确符合本规范 | 直接创建目录与文件，无需反复确认 |
| 需要新 `reports/<type>` | 先给出拟议目录树，用户同意后再创建 `reports/<type>/OVERVIEW.md`，并更新 CLAUDE.md §2、§4 |
| 删除或重命名已有周期/专题 | 先列出影响（链接、system 路径），再执行 |
| 不符合现有拓扑 | 停止；向用户说明原因，提议 (a) 归入现有桶 或 (b) 修订 CLAUDE.md 增加新 `<type>` |

> 完整协作边界见 [`CLAUDE.md`](../../CLAUDE.md) §6。
