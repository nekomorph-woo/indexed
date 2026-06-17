# research — 专题调研

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §3.4、§5.2。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 专题 `research/<topic>/`

| 子目录 | 内容 |
|--------|------|
| `docs/` | FAQ、方案说明、对外 HTML/Markdown（**必填**） |
| `design/` | 专题交互/视觉说明；可选 `design-language.md`（有设计/HTML 选型时） |
| `assets/` | 图片等静态资源（有素材时） |

- **轻量专题**：仅文档调研时只需 `docs/`；`design/`、`assets/` 按需再建。已有仅 `docs/` 的专题合规，不要求 retro 补目录。
- 专题根目录名 = 主题 kebab-case（如 `passkey`）。**不要**用 `research` 下再套 `research` 或按日期分专题。
- 通用设计语言全文在 `_shared/design-languages/<id>/`，**不要**在专题 `design/` 重复存放可复用 token 库。

### 新建专题

1. 确认 `research/<topic>/` 不存在；`<topic>` 为 kebab-case
2. 至少创建 `docs/`；有设计稿或图片时再建 `design/`、`assets/`（轻量专题不强制后两者）
3. 文档按上表落入对应子目录；**禁止**在 `research/<topic>/` 根堆文件

## 图示规范（通用方案文档）

- 架构/流程/交互用 **`###`/`####` 分节 + fenced code block ASCII 线框图**。
- **禁止**「图」列表格（即不要用表格罗列图片）。
- 通用对话/图示风格见 `dialogue-style.md`。
