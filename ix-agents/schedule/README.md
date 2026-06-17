# ix-agents 专用定时（唯一入口）

> **硬约束**：本工作区内凡 **`ix-*-agent` 的定时**，仅指本目录机制。  
> **禁止** Agent 或用户通过其它路径为 ix-*-agent 建定时（见下表）。

## 允许 / 禁止

| ✅ 允许 | ❌ 禁止 |
|--------|--------|
| 在 [`registry.yaml`](registry.yaml) **登记** `jobs[]` | 为某个 agent 单独写 `cron.ps1` / `daily.bat` 并挂任务计划程序 |
| 用 [`invoke-job.ps1`](invoke-job.ps1) `-JobId <id>` 执行已登记任务 | 在 `ix-*-agent/` 目录内建 `schedule/`、`cron.yaml` 等第二套定时 |
| 用 [`register-windows-task.ps1`](register-windows-task.ps1) 将**已登记** job 注册到 Windows 任务计划程序 | 直接 `schtasks /Create` 指向任意其它脚本 |
| OS 调度器只调用上述两个脚本之一 | 在 `artifacts/`、`reports/` 等为 ix-agent 另建定时入口 |
| 业务执行仍走 `artifacts/ix-agent-run-cli` | 定时里绕过 manifest 自写编排 |

## 文件

| 文件 | 作用 |
|------|------|
| `registry.yaml` | **唯一机读登记册**（job id → agent、params、enabled） |
| `invoke-job.ps1` | 按 `-JobId` 调用 `ix-agent-run-cli`（`--trigger scheduled`） |
| `register-windows-task.ps1` | 将登记 job 注册为 Windows 任务（任务动作**仅**指向 `invoke-job.ps1`） |

## 登记新定时（Agent / 用户）

1. 在 `registry.yaml` 的 `jobs` 追加一项（参考 [`job.entry.example.yaml`](job.entry.example.yaml)）。
2. 确认对应 `ix-*-agent` 的 manifest 已就绪。
3. （可选）运行注册脚本：
   ```powershell
   .\ix-agents\schedule\register-windows-task.ps1 -JobId <job-id>
   ```
4. **不要**新建其它计划任务或脚本。

## Windows 任务命名

统一前缀：`indexed-ix-<job-id>`（由 `register-windows-task.ps1` 生成）。

## 与手动执行的关系

定时与 TUI 使用**同一条**执行链：

`invoke-job.ps1` → `ix-agent-run-cli/main.py --agent ...`

规范：[`CLAUDE.md`](../../CLAUDE.md) §3.6 · [`.claude/rules/ix-agents.md`](../../.claude/rules/ix-agents.md) · ix-agent 两阶段流程（skill 待迁移）
