# capabilities — CLI 能力薄索引（Agent 发现用）

> **何时 Read 本文件**：任务里可能出现 **拉数、发邮件、导出、审计** 等可执行需求时。
> 先按下方「意图速查」匹配已有 `ix-*-cli`，再 Read 对应 `SPEC.yaml` 取命令/输入/输出详情。
> 勿等用户口述模块名，勿重复造轮子。

> **能力详情**：每个 cli 的完整能力声明在其目录下的 `SPEC.yaml`（真相源）。本文件只做意图→模块的薄映射。
> 规范：[`capability-spec.spec.md`](../_shared/specs/capability/capability-spec.spec.md) · [`CLAUDE.md`](../CLAUDE.md) §3.5

---

## 按意图 / 关键词速查

| 用户意图或关键词 | 模块 | 一句话 | 详情 |
|------------------|------|--------|------|
| 执行 ix-*-agent、manifest 编排、tool+thinking 流水线 | `ix-agent-run-cli` | 按 manifest 执行 tool + thinking（claude -p） | [`SPEC.yaml`](ix-agent-run-cli/SPEC.yaml) |
| 定时跑组合 agent | `ix-agents/schedule/` + `ix-agent-run-cli schedule run` | 读 registry.yaml 执行 job | [`SPEC.yaml`](ix-agent-run-cli/SPEC.yaml) |
| 索引审计、capabilities/registry 漂移检测 | `ix-workspace-index-cli` | 以 SPEC.yaml 为真相校验一致性 | [`SPEC.yaml`](ix-workspace-index-cli/SPEC.yaml) |
| 初始化 indexed、选定 git 模式（local/remote） | `ix-init-cli` | 交互式 git init + 改写规则模式 | [`SPEC.yaml`](ix-init-cli/SPEC.yaml) |


---

## Agent 决策流程

```
任务需要可执行能力（非纯文档）？
  ├─ 组合多步业务 → Read ix-agents/registry.md → ix-agent-run-cli --agent ...
  ├─ 否（纯文档）→ research/ 或 reports/
  └─ 原子能力 → Read 本文件「意图速查」
        ├─ 有匹配 → Read 对应 SPEC.yaml → shell 串联 / 调用 CLI
        ├─ 同域缺子命令 → 同 artifact 加 providers/ + 子命令
        └─ 无匹配 → 新建 ix-<domain>-cli（.claude/rules/artifacts.md）→ 建 SPEC.yaml → 更新本文件
```

---

## 维护（新建或变更 cli 时）

1. 在 cli 目录建/改 `SPEC.yaml`（规范见 `capability-spec.spec.md`）
2. 在本文件「意图速查」补一行
3. 更新 [`artifacts/README.md`](README.md) 工具索引表
4. 运行 `python artifacts/ix-workspace-index-cli/main.py audit --check` 校验一致性
