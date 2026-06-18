# design-languages — 设计语言库与选型

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §3.11。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 设计语言库 `_shared/design-languages/`

| 文件 | 路径 | 说明 |
|------|------|------|
| 桶索引 | `OVERVIEW.md` | id → 目录 |
| 总览页 | `index.html` | 浏览器打开，链到各 `preview.html` |
| 元数据 | `<id>/meta.md` | 标签、场景、token 摘要（罗列排序） |
| 预览页 | `<id>/preview.html` | 结构与其它 id 相同，仅 token 不同 |
| Prompt 全文 | `<id>/prompt.md` | 用户**确认 id 后** Read |
| 预览母版 | `templates/design-languages/preview-page.template.html` | 导入时生成 preview 的结构准绳 |
| 路由规范 | `_shared/specs/ui-design/design-language-routing.spec.md` | **无全局默认**；先罗列预览、用户选型 |
| 导入规范 | `_shared/specs/ui-design/design-language-import.spec.md` | 粘贴 prompt → meta + prompt + preview |
| 填写母版 | `_shared/templates/design-languages/design-language-intake.template.md` | 用户粘贴区 |

## 约束

- 库内 **只放**可复用语言参考，禁止写入单次专题业务结论。
- 写业务 HTML：**禁止**自动选用任一 id；须罗列库 + 邀请打开 `preview.html` → 用户确认 `id`。
- 专题偏好：`design-language.md` 内 `preferred:` 仅影响推荐排序（**非**自动选中）。
- HTML 产出：当前任务下的 `docs/*.html`（`research` 或 `reports`）。
- 通用设计语言全文在 `_shared/design-languages/<id>/`，**不要**在专题 `design/` 重复存放可复用 token 库。

## 选型流程

```
用户要求写 HTML / 原型页
│
├─ 1. Read 路由规范：_shared/specs/ui-design/design-language-routing.spec.md
├─ 2. 罗列库内各 <id>/meta.md（标签、场景、token 摘要）
├─ 3. 邀请用户浏览器打开 index.html / <id>/preview.html 预览
├─ 4. 用户确认 id（禁止自动选中）
├─ 5. 确认后 Read <id>/prompt.md
└─ 6. 产出到当前任务 docs/*.html
```

## 导入新语言

粘贴外部 prompt → 见导入规范 `_shared/specs/ui-design/design-language-import.spec.md` + 填写母版 → 分析并新建 `<id>/{meta.md, prompt.md, preview.html}`。
