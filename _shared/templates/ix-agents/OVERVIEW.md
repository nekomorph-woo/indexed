# ix-agents 模板

新建 `ix-agents/ix-<business>-agent/` 时从本目录复制。完整流程见 ix-agent 两阶段（`.claude/rules/ix-agents.md`；skill 待迁移）。

| 母版 | 复制到 |
|------|--------|
| `manifest.template.yaml` | `manifest.yaml` |
| `SPEC.template.yaml` | `SPEC.yaml`（能力声明真相源） |
| `defaults.template.yaml` | `config/defaults.yaml` |
| `gitignore.template` | `.gitignore` |
| `paths.template.py` | `paths.py`（推荐） |

**执行**（勿建 `orchestrate.py`）：

```powershell
python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent
```

定时：见 [`ix-schedule-cli`](../../../artifacts/ix-schedule-cli/)（跨平台定时执行器，已从 ix-agents 移出）

规范：[`CLAUDE.md`](../../CLAUDE.md) §3.6
