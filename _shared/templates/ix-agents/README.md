# ix-agents 模板

新建 `ix-agents/ix-<business>-agent/` 时从本目录复制。完整流程见 ix-agent 两阶段（`.claude/rules/ix-agents.md`；skill 待迁移）。

| 母版 | 复制到 |
|------|--------|
| `manifest.template.yaml` | `manifest.yaml` |
| `defaults.template.yaml` | `config/defaults.yaml` |
| `agent-readme.template.md` | `README.md` |
| `gitignore.template` | `.gitignore` |
| `paths.template.py` | `paths.py`（推荐） |

**执行**（勿建 `orchestrate.py`）：

```powershell
python artifacts/ix-agent-run-cli/main.py --agent ix-<business>-agent
```

定时：仅 [`ix-agents/schedule/`](../../../ix-agents/schedule/)（[`README`](../../../ix-agents/schedule/README.md)）；勿用已废弃的 `schedule-task.example.ps1`

规范：[`CLAUDE.md`](../../CLAUDE.md) §3.6
