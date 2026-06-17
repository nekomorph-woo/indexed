# ix-<business>-agent

> **编排**：[`manifest.yaml`](manifest.yaml)  
> **执行**（TUI 与定时相同）：
> ```powershell
> python artifacts/ix-agent-run-cli/main.py --agent ix-<business>-agent
> ```  
> **注册**：[`../registry.md`](../registry.md)

## 目录

| 路径 | 作用 |
|------|------|
| `manifest.yaml` | params + steps（`tool` \| `thinking`） |
| `config/defaults.yaml` | 跨 run 默认参数 |
| `paths.py` | 可选路径 helper |
| `scripts/` | 可选，本 agent 专用脚本（tool Shell 调用） |
| `runs/<run-id>/` | 当次产物（gitignore） |

## runs 结构

| 子路径 | 用途 |
|--------|------|
| `run.yaml` | 参数、`steps_completed`、`status`、`next_step` |
| `inbox/` | 本次输入文件 |
| `work/raw/` | tool 中间产物 |
| `work/thinking/` | thinking 结论（`claude -p` 写入） |
| `output/` | 最终交付 |

## 参数

见 `manifest.yaml` 的 `params` 与 `config/defaults.yaml`。

示例：

```powershell
python artifacts/ix-agent-run-cli/main.py --agent ix-<business>-agent --set primary_input=...
```

续跑：

```powershell
python artifacts/ix-agent-run-cli/main.py --agent ix-<business>-agent --run-id <id> --resume
```
