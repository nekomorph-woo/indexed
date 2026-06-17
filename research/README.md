# research — 专题调研

> 完整规范见 [`CLAUDE.md`](../CLAUDE.md) §3.4、§5.2、[`.claude/rules/research.md`](../.claude/rules/research.md)。

每个主题一个子目录（kebab-case），例如 `passkey/`。

## 目录结构

| 子目录 | 内容 |
|--------|------|
| `docs/` | FAQ、方案说明、对外 HTML/Markdown（**必填**） |
| `design/` | 交互/视觉说明；可选 `design-language.md`（有设计/HTML 选型时） |
| `assets/` | 图片等静态资源（有素材时） |

- 轻量专题：仅文档调研时只需 `docs/`；`design/`、`assets/` 按需再建。
- **禁止**在 `research/<topic>/` 根堆文件；**禁止** `research` 下再套 `research`。
