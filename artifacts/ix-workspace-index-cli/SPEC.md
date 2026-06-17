# ix-workspace-index-cli — SPEC

> 索引一致性审计。机器可读能力声明见 [`SPEC.yaml`](SPEC.yaml)。

indexed 工作区 **索引一致性审计**：以各 `ix-*-cli` / `ix-*-agent` 的 `SPEC.yaml` 为真相源，检查 `capabilities.md`、`registry.md`、桶级 `README.md` 是否漂移。

## 命令

```powershell
# 人类可读报告 + Agent 同步提示
python artifacts/ix-workspace-index-cli/main.py audit

# JSON（Agent 阶段 B 收尾用）
python artifacts/ix-workspace-index-cli/main.py audit --json

# CI / 收尾门禁：有 error 则退出码 1
python artifacts/ix-workspace-index-cli/main.py audit --check

# 仅列出发现
python artifacts/ix-workspace-index-cli/main.py list
```

## 何时跑

| 时机 | 谁执行 |
|------|--------|
| 新建或显著变更 `ix-*-cli` / `ix-*-agent` 后 | Agent **同任务内**（commit 前） |
| ix-agent 阶段 B 创建 agent 完成后 | Agent |
| 用户说「审计索引」「同步 capabilities」 | Agent |

**脚本只诊断，不改文件**；根据 `audit --json` 的 `issues` 与 `agent_sync_hints`，由 Agent 更新 `capabilities.md`、`registry.md`、桶级 README。

## 检查项

- 每个 `ix-*-cli` / `ix-*-agent` 目录是否有 `SPEC.yaml`
- SPEC.yaml 声明的 cli/agent 是否在 `capabilities.md` / `registry.md` 薄索引登记
- 薄索引是否指向已删除目录（孤儿登记）
- agent 的 `has_thinking`、steps 摘要是否与 `manifest.yaml` + `SPEC.yaml` 一致
- 各模块是否具备 `SPEC.md`（人类可读说明）

## 依赖

```bash
pip install -r requirements.txt
```

（`pyyaml`，用于解析 `SPEC.yaml` 与 `manifest.yaml`。）
