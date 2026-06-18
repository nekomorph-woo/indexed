# overview-bucket — 桶级 OVERVIEW.md 规范

> **适用范围**：五个工作桶的 OVERVIEW.md——`artifacts/`、`ix-agents/`、`research/`、`reports/`。
> 共性要求见 `overview-common.spec.md`；本文件定义桶级 OVERVIEW 的额外要求。

## 额外必选

### 目录结构说明

每个桶的 OVERVIEW 必须说明该桶的目录结构约定（子目录命名、周期格式等）：

```markdown
## 目录结构

reports/
└── <report-type>/
    ├── OVERVIEW.md
    └── <周期>/
        ├── drafts/
        └── <final>.md
```

### 新建/维护指导

用户在该桶内新增条目时的步骤清单：

```markdown
## 新建清单

1. 确认目录不存在
2. 创建骨架
3. 更新索引
4. 跑 sync / audit
```

## 条件必选

### 能力索引表 + 标记区（仅 artifacts + ix-agents）

`artifacts/OVERVIEW.md` 和 `ix-agents/OVERVIEW.md` 额外承担**能力薄索引**职责，含 scanner sync 写入的标记区：

```markdown
## 工具索引 — 框架内置

<!-- IX_FRAMEWORK_CLI_INDEX_BEGIN -->
| 工具 | 说明 | ... |
<!-- IX_FRAMEWORK_CLI_INDEX_END -->

## 工具索引 — 用户自建

<!-- IX_USER_CLI_INDEX_BEGIN -->
<!-- sync 自动维护 -->
<!-- IX_USER_CLI_INDEX_END -->
```

- `IX_FRAMEWORK_*`：基线维护，update 时覆盖
- `IX_USER_*`：sync 自动写入，update 时保护

**仅这两个桶有标记区**。research/reports 不含标记区（它们不含能力索引）。

### 与其它桶关系表（仅组合型桶）

`artifacts` 和 `ix-agents` 是"组合型"桶，需要声明与其它桶的依赖关系。research/reports 不需要。

## 各桶的特定内容指引

| 桶 | 额外推荐段落 |
|----|-------------|
| `artifacts/` | 标准骨架、基线 CLI 深度说明（占位符/update 规则等） |
| `ix-agents/` | manifest 编排说明、两阶段执行命令、定时（待设计） |
| `research/` | 专题子目录结构（docs/design/assets） |
| `reports/` | 周期格式、draft- 前缀约定、禁止项 |
