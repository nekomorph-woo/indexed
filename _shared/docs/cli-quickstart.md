# indexed CLI-only 快速开始

> 本指南面向 **CLI-only 用户**（不用 GUI，纯终端工作流）。如果您用 macOS GUI，请下载 `indexed.app`。

---

## 1. 解压

```bash
tar xzf indexed-cli-<ver>.tar.gz -C ~/  &&  cd ~/indexed
```

## 2. 初始化工作区（选一种）

### 本地模式（不推送远端）

```bash
python artifacts/ix-init-cli/main.py init --mode local --nick Xi酱 --addr 您
```

### 远端模式（推 GitHub）

```bash
python artifacts/ix-init-cli/main.py init \
  --mode remote \
  --remote-url git@github.com:you/your-indexed.git \
  --nick Xi酱 \
  --addr 您
```

> init 命令会：创建 `.git`（如果还没有）、改写 `.claude/rules/git-workflow.md` 的 `GIT_MODE` 标记区、写入 persona 信息、生成 `.indexed-initialized` 标记。

## 3. 验证

```bash
python artifacts/ix-workspace-index-cli/main.py audit --check
```

期望输出：`[ok] 未发现索引漂移`

## 4. 开始使用

### 用 Claude Code 打开本目录

```bash
claude
```

Claude 会自动读 `CLAUDE.md`（顶层宪法）+ `.claude/rules/`（各领域细化规则），按规范操作工作区。

### 常用 CLI

```bash
# 查询能力
python artifacts/ix-workspace-index-cli/main.py search "意图关键词"

# 执行 agent（两阶段：先 params 看输入清单，再 run）
python artifacts/ix-agent-run-cli/main.py params --agent ix-<business>-agent
python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent

# 看最近执行
python artifacts/ix-agent-run-cli/main.py stats --last 20

# 索引审计
python artifacts/ix-workspace-index-cli/main.py audit --json
```

## 5. 升级基线

下载新版 tar.gz，解压到临时目录：

```bash
tar xzf indexed-cli-<new-ver>.tar.gz -C /tmp/
```

跑 update（保护用户内容、覆盖框架文件）：

```bash
python artifacts/ix-init-cli/main.py update /tmp/indexed/
```

跑 sync 同步索引：

```bash
python artifacts/ix-workspace-index-cli/main.py sync
```

清理临时目录：

```bash
rm -rf /tmp/indexed
```

## 6. 退出 / 重置

- 删除 `.indexed-initialized` 重新 init（切换 mode / persona）
- 用户内容（`reports/<type>/<周期>/`、`research/<topic>/`、自建 cli/agent）永不丢，update 也会保护

---

## 相关文档

- [`CLAUDE.md`](CLAUDE.md) — 工作区顶层宪法（场景路由表 + 五桶拓扑）
- [`.claude/rules/`](.claude/rules/) — 各领域细化规则
- [`artifacts/capabilities.md`](artifacts/capabilities.md) — CLI 能力索引
- [`ix-agents/registry.md`](ix-agents/registry.md) — Agent 索引
- [`_shared/specs/`](_shared/specs/) — SPEC.yaml 字段规范等
