# 设计语言导入（ui-design）

> **用户母版**：`_shared/templates/design-languages/design-language-intake.template.md`  
> **产出**：`_shared/design-languages/<id>/{meta.md,prompt.md,preview.html}` + 更新索引  
> **触发**：`.claude/rules/design-languages.md`

## 1. 触发条件

用户消息满足**任一**即执行本 spec：

- 粘贴外部 **设计语言 / design token** 全文并要求入库、新增、导入
- 使用 intake 母版并含「原始 prompt」
- 明确：新增设计语言、导入 design language

**不触发**：未提供可落盘 prompt 正文。

## 2. 输入

| 字段 | 必填 | 说明 |
|------|------|------|
| 原始 prompt | ✅ | 全文 |
| 建议 id | ❌ | kebab-case |
| 显示名称 | ❌ | 人类可读名 |
| 来源 | ❌ | 写入 `meta.md` |

**已取消**：「设为全局默认」—— indexed **无**全局默认设计语言。

## 3. 分析

1. 识别系统名称、版本、与已有 id 是否重复
2. 推导 id（kebab-case）；冲突则询问覆盖或 `<id>-2`
3. 提取：标签、场景关键词、token 摘要（供 `meta.md` 罗列与排序）
4. 禁止重复创建已存在的 `material-you` 等同名库

## 4. 落盘规范

### 4.1 目录

```
_shared/design-languages/<id>/
├── meta.md       # 含标签、场景关键词、Token 摘要、预览说明
├── prompt.md     # 规范化全文
└── preview.html  # 与 preview-page.template.html 相同结构，应用本语言 token
```

### 4.2 `prompt.md`

- 保留用户 token 数值；最小结构整理（见 routing spec 旧版约定）
- 文首可选：`<!-- design-language-id: <id> -->`

### 4.3 `meta.md`

- 对齐 `material-you/meta.md`（含 **标签**、**场景关键词**、**Token 摘要**）
- `状态: ready`
- **不要**「默认」字段

### 4.4 `preview.html`

1. 以 `_shared/templates/design-languages/preview-page.template.html` 为结构**唯一准绳**（区块：色彩、字体、按钮、卡片、输入框）
2. 用本语言 prompt 中的色、字、圆角、阴影等替换 `:root` 与组件样式
3. 参考 `material-you/preview.html` 的实现粒度
4. 标题与 banner 使用 `meta.md` 中的名称与 id

### 4.5 索引

1. `_shared/design-languages/README.md` 表格新增一行（含预览列）
2. `_shared/design-languages/index.html` 新增一张卡片（链到 `<id>/preview.html`）
3. `design-language-routing.spec.md` §6 表新增一行（可选，目录为准）

## 5. 完成后回复

- 新 `id`、路径
- 场景与 token 摘要
- 预览：`_shared/design-languages/<id>/preview.html` 与总览 `index.html`
- 写业务 HTML 前须在对话中**确认选用**该 id（见 routing spec §3）

## 6. 禁止

- 只写 `prompt.md` 而不做 `preview.html`
- 在 templates 目录长期存放用户粘贴正文
- 设置全局默认或自动选用新语言

## 7. 参考

| 文件 | 用途 |
|------|------|
| `material-you/` | meta + preview + prompt 范例 |
| `preview-page.template.html` | 预览结构母版 |
| `design-language-routing.spec.md` | 选型流程 |
