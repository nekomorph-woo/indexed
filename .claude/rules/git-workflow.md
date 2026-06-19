# git-workflow — Git 模式与工作区配置

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §6。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## Git 模式

indexed 支持两种 Git 模式，由 `ix-init-cli` 初始化时选定（见下方标记区）：

* **`local`**：纯本地版本库，不推送远端。commit 后仅说明结果，**不**提示 push。

* **`remote`**：含远端（如 GitHub）。commit 后可 push。

<!-- IX_GIT_MODE_BEGIN -->

**当前模式：`remote`**

含远端（如 GitHub）。commit 后可 push。

<!-- IX_GIT_MODE_END -->

> **ix-init-cli 通过上面的** **`GIT_MODE`** **标记区定位并改写本段**，仅替换标记区内容，不动文件其余部分。

## 禁止（与模式无关）

* **禁止**在 `_shared/repos/` 内执行构建类操作（见 `shared-repos.md`；已写入 `.claude/settings.json` deny）。

* 若 `research/<topic>` 或某个 `ix-*-agent` 需要 clone 上游仓库，由**它们自己**在就近文档/manifest 记录仓库映射；CLAUDE.md 和本文件不登记具体仓库。

## 版本号

根目录 `VERSION` 文件标记 indexed 版本（语义化版本）。迭代时递增：

* 主版本号：不兼容的结构性变更（桶拓扑、规范范式重构）

* 次版本号：向后兼容的能力新增（新 spec、新 rule、新 cli 模板）

* 修订号：向后兼容的修复与订正

## 工作区配置目录

根目录允许的工作区/工具配置目录（除五个工作桶 + 元文件外）：

| 目录         | 用途                                                |
| ---------- | ------------------------------------------------- |
| `.claude/` | Claude Code 配置：`rules/`、`settings.json`、`skills/` |

这些目录**不**属于「工作桶」，禁止在其中放业务交付物。

## 根目录白名单（重申）

仅允许：`CLAUDE.md`、`VERSION`、`.gitignore`、`.claude/`，以及五个工作桶（`_shared/`、`reports/`、`research/`、`artifacts/`、`ix-agents/`）。
