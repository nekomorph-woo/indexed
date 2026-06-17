# 设计语言路由（ui-design）

> **prompt 库**：`_shared/design-languages/<id>/`  
> **触发**：`.claude/rules/design-languages.md`  
> **禁止**：全局默认某一种语言；禁止未选型就读取 `prompt.md`

## 1. 范围

在 indexed 内**首次**创建或大幅改版业务 **静态 HTML** 时，须先完成 **设计语言选型**（§3），再 Read 对应 `prompt.md` 并写代码。

HTML 落盘路径：

- `research/**/docs/*.html`
- `reports/**/docs/*.html`

## 2. 库内文件（每种 `<id>/`）

| 文件 | 用途 |
|------|------|
| `meta.md` | 标签、场景关键词、token 摘要（罗列与排序，**不**含全文 prompt） |
| `preview.html` | 与其它 id **结构相同**的预览页（仅视觉 token 不同） |
| `prompt.md` | 完整设计语言（**用户确认 id 后**才 Read） |

总览入口：`_shared/design-languages/index.html`（链接到各 `preview.html`）

预览结构母版：`_shared/templates/design-languages/preview-page.template.html`

## 3. 选型流程（硬约束）

### 3.1 何时可跳过罗列

仅当**本条消息**已明确 `language_id`（如「用 material-you 写 HTML」）时，可直接 Read `prompt.md` 并写业务 HTML。

否则**必须先选型**，不得默认 `material-you` 或任一 id。

### 3.2 Agent 罗列步骤

1. **枚举**：扫描 `_shared/design-languages/*/`，仅 `meta.md` 中 `状态: ready` 的 id
2. **读元数据**：每个 id 只 Read `meta.md`（禁止为罗列而 Read 全部 `prompt.md`）
3. **收集上下文**（用于排序，非自动选中）：
   - 用户本条描述（B2B、消费端、暗色、表格密集等）
   - 可选：`research/<topic>/design/design-language.md` 内 `preferred:`（见 §4）
4. **排序推荐**（分高在前，见 §5）
5. **输出给用户**（Markdown 表或列表），每项含：
   - `id`、显示名称
   - 1～2 行场景 + token 摘要（来自 meta）
   - **预览路径**（绝对或工作区内路径）：`_shared/design-languages/<id>/preview.html`
6. **邀请预览**：
   - 打开总览 `_shared/design-languages/index.html`，或逐个打开上表预览链接
   - 请用户回复选用的 `id` 后再继续写 HTML
7. **停止**：未收到用户确认的 `id` 前，不 Read `prompt.md`、不写业务 `docs/*.html`

### 3.3 用户确认后

1. Read `_shared/design-languages/<id>/prompt.md`
2. 将业务 HTML 写入当前任务 `docs/`
3. 可选：HTML 注释 `<!-- design-language: <id> -->`

## 4. 专题偏好（仅影响排序）

路径：`research/<topic>/design/design-language.md` 或 `reports/<type>/design/design-language.md`

```markdown
preferred: material-you
reason: Passkey 对外说明，偏消费端；**须用户确认后**才使用。
```

- `preferred:` **不**等于自动选中，只给 §5 排序加分
- 废弃：单独写 `id:` 并视为强制默认（已取消）

## 5. 推荐排序规则

对每条 ready 语言计算建议分（Agent 心算即可，写入回复时可标「推荐」）：

| 因素 | 分值 |
|------|------|
| `meta.md` 场景关键词与用户描述匹配（每条） | +3 |
| `meta.md` 标签与用户描述匹配（每条） | +2 |
| 专题 `preferred:` 与该 id 一致 | +5 |
| 用户本条已点名 id | 置顶，并询问是否确认 |

**禁止**：因库内仅有一种语言、或历史习惯，自动选用 `material-you`。

## 6. 语言索引表

| id | 预览 | prompt |
|----|------|--------|
| `material-you` | `material-you/preview.html` | `material-you/prompt.md` |
| `bauhaus` | `bauhaus/preview.html` | `bauhaus/prompt.md` |
| `newsprint` | `newsprint/preview.html` | `newsprint/prompt.md` |
| `flat-design` | `flat-design/preview.html` | `flat-design/prompt.md` |
| `hand-drawn` | `hand-drawn/preview.html` | `hand-drawn/prompt.md` |
| `industrial-skeuomorphism` | `industrial-skeuomorphism/preview.html` | `industrial-skeuomorphism/prompt.md` |

完整列表以 `_shared/design-languages/` 子目录为准；新增见 import spec。Agent 在新增/导入后**同步更新** `index.html` 中对应卡片。

## 7. 新增语言

[`design-language-import.spec.md`](design-language-import.spec.md)：须同时产出 `meta.md`、`prompt.md`、`preview.html`（结构对齐 preview 母版），并更新 `index.html`。

## 8. 分工

| 位置 | 内容 |
|------|------|
| `_shared/design-languages/<id>/` | 库 + 预览 |
| `research/<topic>/design/design-language.md` | 专题 `preferred`（排序提示） |
| 业务 HTML | `research|reports/**/docs/*.html` |
