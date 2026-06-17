# _shared/templates — 文档母版索引

> 跨任务可复用的文档母版（`*.template.md` / `*.template.yaml`）。
> 与 **`_shared/specs/`**（流程规范）职责不同，见 [`../specs/README.md`](../specs/README.md)。
> 规范：[`CLAUDE.md`](../../CLAUDE.md) §3.8

## 现有母版

| 类别 | 目录 | 说明 |
|------|------|------|
| ix-*-agent 母版 | `ix-agents/` | manifest / defaults / paths / SPEC 等，新建组合 agent 时复制 |
| 设计语言导入 | `design-languages/` | intake / meta / preview-page 母版 |

## 新增模板类别

1. 在 `_shared/templates/<category>/` 新建 `*.template.md`
2. 更新本索引表
3. 更新 CLAUDE.md §3.8
