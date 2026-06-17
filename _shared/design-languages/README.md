# design-languages

跨专题 **HTML / 原型页** 设计语言库。**无全局默认**；写业务 HTML 前须用户选定 `id`。

| 入口 | 路径 |
|------|------|
| 总览（浏览器） | [`index.html`](index.html) |
| 路由 / 选型 | [`../specs/ui-design/design-language-routing.spec.md`](../specs/ui-design/design-language-routing.spec.md) |
| 导入 | [`../specs/ui-design/design-language-import.spec.md`](../specs/ui-design/design-language-import.spec.md) |
| 预览结构母版 | [`../templates/design-languages/preview-page.template.html`](../templates/design-languages/preview-page.template.html) |

## 索引

| id | 预览 | 说明 | 状态 |
|----|------|------|------|
| `material-you` | [`material-you/preview.html`](material-you/preview.html) | Material Design 3 / Material You | ready |
| `bauhaus` | [`bauhaus/preview.html`](bauhaus/preview.html) | 包豪斯几何构成、原色块面、硬阴影 | ready |
| `newsprint` | [`newsprint/preview.html`](newsprint/preview.html) | 报刊编辑、衬线层级、网格线、新闻纸质感 | ready |
| `flat-design` | [`flat-design/preview.html`](flat-design/preview.html) | 扁平色块、无阴影、SaaS/海报式分区 | ready |
| `hand-drawn` | [`hand-drawn/preview.html`](hand-drawn/preview.html) | 手绘歪边、便签/草稿、硬阴影剪纸 | ready |
| `industrial-skeuomorphism` | [`industrial-skeuomorphism/preview.html`](industrial-skeuomorphism/preview.html) | 工业新拟态、控制台、安全橙、双阴影 | ready |

## 每种语言目录

| 文件 | 用途 |
|------|------|
| `meta.md` | 标签、场景、token 摘要（Agent 罗列排序用） |
| `preview.html` | 与其它 id **结构相同**的样例页 |
| `prompt.md` | 全文（用户确认 id 后 Read） |

## 新增

粘贴 prompt → [`design-language-intake.template.md`](../templates/design-languages/design-language-intake.template.md) → import spec → 自动含 `preview.html` 并更新 `index.html`。

规范：[`CLAUDE.md`](../../CLAUDE.md) §3.11
