# naming — 命名规范与桶级 README

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §3.1、§3.2。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 通用命名

| 对象 | 规则 | 示例 |
|------|------|------|
| 目录 | 英文 kebab-case | `team-usage`, `passkey` |
| 排序/共用前缀 | 单下划线 `_` | `_shared`, `_internal` |
| 日期 | `YYYY-MM-DD` | `2026-05-11` |
| 日期区间目录 | `<start>_<end>` | `2026-05-11_2026-05-22` |
| 草稿文件 | `draft-` + 语义 | `draft-aiagentservice-develop_app_960-report.md` |
| 文档 | `.md` / `.html` / `.txt`；说明性用 kebab-case | `passkey-peer-proposal.txt` |

- 目录与文件名默认英文；中文**仅**出现在 Markdown 正文标题或交付物内容中。
- **禁止**使用中文或空格作为目录名。

## 桶级 OVERVIEW.md（硬约束）

**仅下列「桶」必须有 `OVERVIEW.md`**（桶的概览/入口：介绍 + 索引 + 指导；非权威，细节以 CLAUDE.md 为准）：

| 桶路径 | 说明 |
|--------|------|
| `reports/` | 报告桶总说明 |
| `reports/<report-type>/` | 每种报告类型一份（新建 `<type>` 时必建） |
| `research/` | 专题桶总说明 |
| `artifacts/` | 可运行小工具/脚本桶总说明 |
| `ix-agents/` | 组合应用桶总说明 |
| `_shared/specs/` | spec 索引（新增 `*.spec.md` 类别时更新本表格，**不**强制 `specs/<category>/OVERVIEW.md`） |
| `_shared/templates/` | 模板索引（新增模板类别时更新本表格，**不**强制 `templates/<category>/OVERVIEW.md`） |
| `_shared/design-languages/` | 设计语言 prompt 索引（新增 `<id>` 时更新本表格） |

**不要求** OVERVIEW 的目录（示例）：

- `reports/<type>/<周期>/`、`drafts/` 等**当期/实例**子目录
- `research/<topic>/`（专题根 OVERVIEW **可选**，见 `research.md`）
- `artifacts/<artifact-name>/`（工具根 `SPEC.yaml` **必须**，见 `artifacts.md`）
- `ix-agents/<agent-name>/`（应用根 `SPEC.yaml` **必须**，见 `ix-agents.md`）
- `_shared/repos/<repo-kebab>/`（Git clone，属上游仓库文档）
- `_shared/specs/<category>/`、`_shared/templates/<category>/` 子目录（**非强制**）

新建桶或 `reports/<type>` 时：Agent **必须**创建或更新对应桶级 `OVERVIEW.md`；**禁止**仅为满足规范而在每个子文件夹批量创建。

## Git 仓库 clone 命名

- `_shared/repos/` 是唯一允许的 clone 根；目录名 kebab-case（如 `ai-agent-service`）。
- **具体仓库登记不由本文件维护**——哪个 research 或 ix-agent 需要 clone，就由它在自己的文档/manifest 里就近记录仓库映射。本文件只约束命名格式。
