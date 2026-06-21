# ix-gui — indexed 的图形操作面板

> **定位**：indexed 工作区的 GUI 应用（Tauri 2.x + React + TypeScript）。**不是**业务资产，是**框架设施**——与 `.claude/` 同性质，服务于整个工作区的可视化与操作。

> **规范关系**：本桶由 CLAUDE.md §2/§4 授权新增；遵守下方「零侵入铁律」。

---

## ⚖️ 零侵入铁律（不可违反）

GUI 落到 indexed 工作区的任何字节级改动，必须与「claude code 在终端里做同样的事」产生的改动**完全等价、可互换、互相兼容**。

由此推出**四条硬约束**：

1. **GUI 不发明** claude code 不认识的文件格式或目录结构
2. **GUI 不创建**资产（agent/cli）——创建一律走「可见终端里的 claude」（单一写入源）。GUI 的「新建」只能是 prompt 生成器，把用户输入拼成一句话塞进终端，由 claude 落盘
3. **GUI 只做两件事**：只读展示（文件系统）+ 调用既有 CLI（subprocess）
4. **ix-gui/ 自身的代码除外**（Cargo.toml / package.json / Rust / TS 是 GUI 自己的实现，不被当业务桶审计/索引）

### 并存保证

```
同一个 indexed 工作区
   ├─ GUI 方式        ── 资产树 + 可见终端(PTY claude) + 表单执行(run-cli)
   └─ 纯 claude code  ── iTerm 里 cd indexed && claude（原有工作流原样保留）

两者读写同一个工作区，产物 100% 互通：
  • GUI 跑的 run → claude code 能看到、能 resume
  • claude code 建的 agent → GUI 资产树自动出现、能执行
```

---

## 🚧 三边界处理

### 边界 1 — `ix-gui/` 桶的边界声明

`ix-gui/` 是**框架设施**（同 `.claude/`），不是业务桶。claude code 读 CLAUDE.md 时应知道：
- 不把 `ix-gui/` 纳入 `capabilities.md` / `registry.md` 索引
- 不把 `ix-gui/` 里的 `.ts` / `.rs` / `.py` 当成 `ix-*-cli` 管理
- 该桶的 `OVERVIEW.md` / `SPEC.yaml` 仅供 GUI 自身维护，不参与工作区审计

> 此声明已写入 CLAUDE.md §2/§4（本次修订一并完成）。

### 边界 2 — §5.4.4 构建禁令的豁免

CLAUDE.md §5.4.4 禁止 `npm build` / `cargo build` 等构建命令——针对的是 `_shared/repos/` 内的 clone 仓库。`ix-gui/` 作为 indexed **自有应用设施**，不受 §5.4.4 约束，可在其目录内执行构建（`cargo build` / `npm install` / `tauri dev`）。

> 已在 CLAUDE.md §5.4.4 显式标注豁免边界（本次修订一并完成）。

### 边界 3 — 创建资产的单写入源

GUI 的「新建 agent/cli」**只做 prompt 生成器**，绝不直接写 manifest/SPEC：

```
用户填 GUI 表单（业务名/需求）
  → GUI 拼一句自然语言："帮我建个周报 agent，primary_input=..., window_days=7"
  → 塞进可见终端的 claude
  → claude 按规范创建（单一写入源）
  → 资产树自动刷新
```

绝不走「GUI 表单直接写文件」那条路——那会引入双写入源，破坏并存。

---

## 🏗️ 技术架构（混合）

```
┌──────────────────────────────────────────────────────────────┐
│                     Tauri 2.x 应用                            │
│  ┌─ React 前端 (webview) ──────────────────────────────────┐ │
│  │  资产树(只读) + 主区选项卡                                │ │
│  │    ├ 会话页 <TerminalPanel>   xterm.js（可见、可打字）   │ │
│  │    ├ Agents页 <AgentList> + <AgentRunForm>              │ │
│  │    ├ Runs页   <RunBrowser>                               │ │
│  │    ├ 索引页   <IndexDashboard>                           │ │
│  │    └ 设置页   <SettingsView>（主题切换 + 零侵入说明）    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          ↕ Tauri IPC                         │
│  ┌─ Rust 后端 (src-tauri) ─────────────────────────────────┐ │
│  │  PtyBridge (portable-pty) ↔ 交互式 claude                │ │
│  │  CliRunner  (tokio::proc)  → run-cli / audit / sync      │ │
│  │  WorkspaceIo             → 读 manifest/SPEC/runs         │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**两条 claude 通路，物理隔离**：

| 通路 | 跑什么 | 技术 | 可见性 | 用途 |
|---|---|---|---|---|
| A. 可见终端 | 交互式 `claude` TUI | portable-pty + xterm.js | ✅ 用户直接看/打字 | 沟通、**创建**资产 |
| B. 执行引擎内部 | `claude -p`（headless） | run-cli 内部 subprocess | ❌ 完全不可见 | thinking step（GUI 不介入） |

---

## 📐 渐进实施（当前阶段）

```
阶段 1（当前）：纯 Web
  • Vite + React + TS，UI 与交互逻辑全部完成
  • Mock 后端契约（模拟 PtyBridge/CliRunner/WorkspaceIo 的返回）
  • bb-browser 端到端验证
  • 用户人工验收

阶段 2（验收后）：Tauri + Rust
  • 把 mock 换成真实 Rust 实现
  • xterm.js + portable-pty 接可见终端
  • 打包分发
```

---

## 📁 目录结构（规划）

```
ix-gui/
├── OVERVIEW.md              # 本文件
├── SPEC.yaml                # GUI 自身能力声明
├── web/                     # 阶段 1 纯 Web 工程（当前）
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── App.tsx
│   │   ├── views/           # 会话/Agents/Runs/索引
│   │   ├── components/      # 资产树/表单/卡片
│   │   ├── api/             # 契约层（web mock）
│   │   ├── types/           # manifest/SPEC/run.yaml 类型
│   │   └── theme/           # 复用 design-languages 的 token
│   └── src/api/mock/       # 模拟数据（真实 manifest/agent 样本）
└── src-tauri/               # 阶段 2 Rust（验收后再建）
```

---

## 📖 相关规范

- CLAUDE.md §2（桶拓扑）、§4（决策树）、§5.3（ix-agent 两阶段）、§5.4.4（构建禁令）
- `.claude/rules/ix-agents.md`（manifest/两阶段）
- `.claude/rules/artifacts.md`（cli 骨架）
- `_shared/specs/capability/capability-spec.spec.md`（SPEC.yaml 字段）
- `_shared/design-languages/`（主题 token 来源）
