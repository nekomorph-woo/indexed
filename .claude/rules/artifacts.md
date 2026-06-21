# artifacts — 可运行 CLI / 小工具

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §3.4、§5.2。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 约定

| 说明 | 约定 |
|------|------|
| **用途** | 可运行 CLI/脚本；从 `_shared/repos` 或 `research/` 提炼的实现（非报告、非纯文档） |
| **命名** | 默认 **`ix-<domain>-cli`**（kebab-case），例：`ix-metabase-cli`、`ix-mail-cli` |
| **结构** | 标准骨架：`main.py`、`config.py`、可选 `session.py` + `providers/`、`.env.example` |
| **耦合** | artifact 间 **零 import**；同 artifact 内 provider 间 **零互引**；多工具用 **shell 串联** |
| **配置** | `.env` + `.env.example`；禁止 tracked 明文密钥 |
| **与 research** | 分析在 `research/`；可执行在 `artifacts/` |
| **与 _shared/repos** | 只读参考；提炼代码复制到 artifact，禁止在 repos 内改代码或构建 |
| **索引** | 新建或显著变更后更新 `artifacts/OVERVIEW.md` 与 **`artifacts/capabilities.md`**（Agent 能力发现） |

## 标准骨架

新建 `artifacts/ix-<domain>-cli/` 必备：

```
ix-<domain>-cli/
├── main.py          # 入口 + argparse 子命令
├── config.py        # 路径与环境变量解析
├── requirements.txt
├── .env.example
├── .gitignore       # 忽略 output/、.env、__pycache__/
├── SPEC.yaml        # 机器可读能力声明（真相源，必须）
├── [session.py]     # 可选；会话/认证
└── [providers/]     # 可选；多源 provider（互不 import）
```

## 新建 artifact 清单

1. 命名：`ix-<domain>-cli`（kebab-case）；确认目录不存在
2. 创建标准骨架（上表）；按需 `session.py` + `providers/`
3. 实现至少一个子命令；验证可观察成功
4. 在 cli 目录建 **`SPEC.yaml`**（能力声明真相源；字段规范见 `capability-spec.spec.md`）
5. 跑 `python artifacts/ix-workspace-index-cli/main.py sync`（自动同步索引到 `IX_USER_*` 标记区）+ `audit --check`（校验一致性）
6. 禁止：跨 artifact import、repos 内改代码、提交 `.env`/密钥/`output/` 数据

**同域扩展**：优先在同 artifact 加 `providers/<name>.py` + `main.py` 子命令，不新建目录。

## 能力发现（做大应用前必须先做）

**硬性要求**：任务涉及可执行能力（拉数、发邮件、导出、审计、定时等）时，**必须先跑 search 命令**，不要直接搜目录或等用户口述模块名：

```bash
python artifacts/ix-workspace-index-cli/main.py search "意图关键词"
```

- search 读所有 SPEC.yaml 的 intents 字段做意图匹配，返回名称+一句话+SPEC 路径
- **有匹配** → Read 对应 SPEC.yaml 取命令/输入/输出详情 → shell 串联复用
- **无匹配** → 新建 ix-<domain>-cli（见下方新建清单）
- 勿重复造轮子：同域已有能力就扩展 providers/，不新建 cli

## 现有范例

- `ix-agent-run-cli`：组合 agent 执行（manifest 编排）
- `ix-workspace-index-cli`：索引审计（capabilities/registry 与磁盘一致性）
