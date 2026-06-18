# artifacts

> **权威规范**：[`CLAUDE.md`](../CLAUDE.md) §3.5、§5.3 + [`.claude/rules/artifacts.md`](../.claude/rules/artifacts.md)  
> **Agent 能力发现**：[`capabilities.md`](capabilities.md)（做大应用/流水线前 **先 Read**，按意图匹配模块）  
> 新建 artifact 时 Agent **直接按 rule 执行**，无需重复解释架构。

可运行 **CLI 小工具**（默认命名 **`ix-<domain>-cli`**）。

## 与其它桶

| 桶 | 放什么 |
|----|--------|
| `research/` | 调研文档（WHY） |
| **`artifacts/`** | 可执行 CLI（HOW） |
| `_shared/repos/` | 只读 clone（参考源码，禁止改/构建） |
| `reports/` | 报告定稿 |

## 命名

- 默认：**`ix-<domain>-cli`** → `ix-metabase-cli`、`ix-mail-cli`
- 同域新能力 → 同目录加 `providers/` + 子命令
- 新域 → 新 artifact；**禁止**跨 artifact `import`

## 标准骨架

```
artifacts/ix-<domain>-cli/
├── main.py              # 子命令入口
├── config.py            # 环境变量 / .env
├── session.py           # 可选：登录、连接
├── providers/<name>.py  # 一种能力；provider 间零互引
├── requirements.txt
├── .env.example
├── .gitignore           # .env、output/、__pycache__/
└── README.md            # 必须
```

## 新建清单（Agent 默认）

1. `artifacts/ix-<domain>-cli/` 不存在 → 按骨架创建
2. 至少一个子命令 + 可观察成功
3. 更新**本文件**索引表与 **[`capabilities.md`](capabilities.md)**（意图速查 + 能力卡片）
4. 不写 `.env` 真实密钥进 Git

## 工具索引 — 框架内置

<!-- IX_FRAMEWORK_CLI_INDEX_BEGIN -->
| 工具 | 子命令 | 说明 |
|------|--------|------|
| [`ix-agent-run-cli/`](ix-agent-run-cli/) | `main.py --agent …` | 统一执行 `ix-*-agent` manifest（TUI 与定时同命令） |
| [`ix-workspace-index-cli/`](ix-workspace-index-cli/) | `audit` / `list` / `sync` | capabilities/registry 与磁盘一致性审计 |
| [`ix-init-cli/`](ix-init-cli/) | `init` / `update` / `status` | 工作区初始化（git 模式）+ 基线更新 |
<!-- IX_FRAMEWORK_CLI_INDEX_END -->

## 工具索引 — 用户自建

<!-- IX_USER_CLI_INDEX_BEGIN -->
<!-- 用户自建 cli 的索引行由 sync 自动维护 -->
<!-- IX_USER_CLI_INDEX_END -->

**串联（零 import）**：

```bash
python ix-metabase-cli/main.py question --question-id 3798
python ix-mail-cli/main.py send --to a@x.com --subject "报表" --attach ix-metabase-cli/output/xxx.csv
```
