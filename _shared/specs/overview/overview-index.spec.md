# overview-index — 索引级 OVERVIEW.md 规范

> **适用范围**：索引/参考型目录的 OVERVIEW.md——`_shared/specs/`、`_shared/templates/`、`_shared/design-languages/`、`.claude/rules/`。
> 共性要求见 `overview-common.spec.md`；本文件定义索引级 OVERVIEW 的额外要求。

## 设计定位

索引级 OVERVIEW 的核心职责是**条目发现**——让读者一眼看到该目录下有哪些条目、每个条目做什么。

## 额外必选

### 条目清单表

必须有一张表列出该目录下所有条目：

```markdown
## 现有规范

| 类别 | 文件 | 说明 |
|------|------|------|
| 能力声明 | `capability/capability-spec.spec.md` | SPEC.yaml 字段规范 |
| UI 设计 | `ui-design/design-language-routing.spec.md` | HTML 选型 |
```

表至少含三列：类别/名称、文件路径、一句话说明。

### 新建条目维护指导

新增条目时的步骤：

```markdown
## 新增类别

1. 在 `<category>/` 新建文件
2. 更新本文件清单表
3. 更新 CLAUDE.md 对应章节
```

## 与桶级 OVERVIEW 的区别

| 维度 | 桶级（overview-bucket） | 索引级（overview-index） |
|------|------------------------|-------------------------|
| 核心职责 | 桶概览 + 新建指导 + 可能含标记区 | 条目发现 + 清单 |
| 标记区 | 仅 artifacts + ix-agents 有 | 无 |
| 目录结构树 | 必选 | 不要求（索引目录结构简单） |
| 与其它桶关系 | 组合型桶必选 | 不要求 |

## 各索引目录的特定内容

| 目录 | 清单内容 |
|------|----------|
| `_shared/specs/` | spec 文件（类别 + 文件 + 说明） |
| `_shared/templates/` | 模板文件（类别 + 目录 + 说明） |
| `_shared/design-languages/` | 设计语言 id（id + 标签 + 场景） |
| `.claude/rules/` | 规则文件（文件 + 领域 + 来源章节） |
