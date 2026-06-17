# capability-spec — SPEC.yaml 字段规范

> **用途**：每个 `ix-*-cli` / `ix-*-agent` 目录必须含一个 `SPEC.yaml`，作为该工具**能力的机器可读真相源**。scanner 以它为准校验薄索引页（`capabilities.md` / `registry.md`）；大模型可一次 Read 聚合后的清单快速知道系统能力，无需逐一翻阅工具内部。

## 设计原则

- **分布式**：每个 cli/agent 自带 SPEC.yaml，就近维护（工具变了改自己的 SPEC，不碰中心文件）。
- **真相源**：SPEC.yaml 是能力的唯一真相；`capabilities.md`/`registry.md` 是**派生的薄索引**，只做「意图 → 名 + 一句话」映射。
- **机器友好**：YAML 结构化，scanner 可解析、可聚合为 JSON 供 `audit --json` 输出。

---

## cli 的 SPEC.yaml schema

路径：`artifacts/ix-<domain>-cli/SPEC.yaml`

```yaml
# 必填
name: ix-metabase-cli          # 目录名（kebab-case）
domain: Metabase 数据导出       # 领域一句话
one_liner: Question/Card → CSV # 能力一句话
status: implemented            # implemented | planned | deprecated
intents:                       # 供 capabilities.md 意图匹配；可多条
  - "Metabase、Question、报表导出、CSV"

# 命令清单（至少 1 个）
commands:
  - name: question             # 子命令名
    inputs:                    # 输入参数示例（非穷举）
      - "--question-id 3798"
      - "--url <浏览器 Question 链接>"
    outputs: "CSV 文件（--output / ./output/）"
    example: "python main.py question --question-id 3798"

# 可选
credentials:                   # 需要的环境变量
  - METABASE_BASE_URL
  - METABASE_USERNAME
depends_on: []                 # shell 串联的其它 ix-*-cli（非 import）
research: research/xxx/        # 关联调研（可选）
notes: ""                      # 补充说明（可选）
```

### 字段约束

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `name` | ✅ | string | 等于目录名 |
| `domain` | ✅ | string | 领域，≤20 字 |
| `one_liner` | ✅ | string | 能力，≤30 字 |
| `status` | ✅ | enum | `implemented`/`planned`/`deprecated` |
| `intents` | ✅ | string[] | 意图关键词，≥1 条 |
| `commands` | ✅ | object[] | 命令清单，≥1 |
| `commands[].name` | ✅ | string | 子命令名 |
| `commands[].inputs` | ✅ | string[] | 输入示例 |
| `commands[].outputs` | ✅ | string | 输出说明 |
| `commands[].example` | ✅ | string | 典型命令 |
| `credentials` | ❌ | string[] | 环境变量名 |
| `depends_on` | ❌ | string[] | 依赖的 ix-*-cli |
| `research` | ❌ | string | 关联 research 路径 |
| `notes` | ❌ | string | 补充 |

---

## agent 的 SPEC.yaml schema

路径：`ix-agents/ix-<business>-agent/SPEC.yaml`

```yaml
# 必填
name: ix-rollout-audit-agent
domain: 上线单据审计
one_liner: 审批信号 → Wiki 文档 → 测试审计 → 报告
status: implemented
intents:
  - "上线单据审计、部署文档、rollout"

# 执行参数
params_required: [report_title, recent_client_versions]
params_optional: [chat_query, senders, start, end]

# 流水线
has_thinking: true             # 是否含 thinking（claude -p）step
steps:                         # step id 序列
  - fetch_messages
  - prepare_raw
  - render_report

# 可选
schedule_safe: true            # 是否适合无人值守定时
schedule_note: "全自动；Wiki 扫描较慢"
research: research/xxx/
```

### 字段约束

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `name` | ✅ | string | 等于目录名 |
| `domain` | ✅ | string | 业务领域 |
| `one_liner` | ✅ | string | 能力一句话 |
| `status` | ✅ | enum | 同 cli |
| `intents` | ✅ | string[] | 意图关键词 |
| `params_required` | ✅ | string[] | 必填参数（可空数组） |
| `params_optional` | ❌ | string[] | 可选参数 |
| `has_thinking` | ✅ | bool | 是否含 thinking step |
| `steps` | ✅ | string[] | step id 序列 |
| `schedule_safe` | ❌ | bool | 定时安全性 |
| `schedule_note` | ❌ | string | 定时说明 |
| `research` | ❌ | string | 关联 research |

---

## 维护流程

1. **新建 cli/agent**：从本规范复制 schema 填写 `SPEC.yaml`
2. **变更能力**：改自己的 `SPEC.yaml`，同步更新薄索引页
3. **校验**：`python artifacts/ix-workspace-index-cli/main.py audit` 会比对 SPEC.yaml 与薄索引页一致性
4. **大模型发现**：先 Read `capabilities.md`/`registry.md` 薄索引匹配意图 → 再 Read 对应 `SPEC.yaml` 取详情
