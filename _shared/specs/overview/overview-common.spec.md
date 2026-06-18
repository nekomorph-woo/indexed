# overview-common — OVERVIEW.md 共性规范

> **适用范围**：indexed 工作区所有层级的 `OVERVIEW.md`（桶级、索引级、子目录级）。
> 本文件定义所有 OVERVIEW.md **必须共有**的段落。桶类型特定的额外要求见 `overview-bucket.spec.md` / `overview-index.spec.md`。

## 设计定位

OVERVIEW.md 是**所在目录的概览/入口页**——混合介绍 + 索引 + 指导。它不是纯索引（像 capabilities.md），也不是纯规范（像 CLAUDE.md）。它是人类和 AI 进入某个目录时**第一个该读的文件**。

## 必选段落（所有 OVERVIEW.md 都要有）

### 1. H1 标题

```markdown
# <目录名>
```

或带语义说明：`# artifacts — 可运行 CLI 小工具`。

### 2. 一句话定位

紧跟 H1，用 `>` 引用块或正文一句话说清"这个目录是做什么的"：

```markdown
> 可运行 **CLI 小工具**（默认命名 `ix-<domain>-cli`）。
```

### 3. 权威规范引用

指向 CLAUDE.md 对应章节 + `.claude/rules/<x>.md`：

```markdown
> **权威规范**：[`CLAUDE.md`](../CLAUDE.md) §3.5 + [`.claude/rules/artifacts.md`](../.claude/rules/artifacts.md)
```

OVERVIEW.md **不是权威**——它是指引入口，细节以 CLAUDE.md / rules 为准。

## 可选段落（按需）

| 段落 | 何时用 | 示例 |
|------|--------|------|
| 与其它桶关系表 | 该桶依赖或关联其它桶时 | artifacts、ix-agents |
| 目录结构树 | 该桶有约定的子结构时 | reports、research |
| 新建/维护指导 | 用户会在该桶内新增条目时 | 所有桶 |
| 执行命令 | 该桶涉及 CLI 执行时 | artifacts、ix-agents |
| 深度说明 | cli 的机制/契约需要展开解释时 | artifacts §基线 CLI 深度说明 |

## 禁止

- **禁止**写入单次任务的业务结论（OVERVIEW 是跨周期可复用的入口）
- **禁止**复制 CLAUDE.md / rules 的全文（只引用，不重复——避免漂移）
- **禁止**把 OVERVIEW.md 当作 SPEC（能力声明用 SPEC.yaml，不用 OVERVIEW）

## 与 SPEC.yaml 的关系

| 文件 | 性质 | 谁读 |
|------|------|------|
| `OVERVIEW.md` | 桶/目录的概览入口（介绍+索引+指导） | 人类 + AI |
| `SPEC.yaml` | 单个 cli/agent 的机器能力真相 | scanner + AI（用户询问时解释给人） |

OVERVIEW.md **不替代** SPEC.yaml——前者是桶级概览，后者是模块级能力声明。
