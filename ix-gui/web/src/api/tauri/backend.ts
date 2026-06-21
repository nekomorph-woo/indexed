/**
 * TauriBackend —— Tauri+Rust 阶段的真实后端实现。
 *
 * 业务代码不直接 import 本文件；通过 `api/backend.ts` 的 export 间接使用。
 * 阶段切换（M2 → M5）只改 `backend.ts` 的 export，本文件逐步完善：
 *   - M2（当前）：workspace 完整（8 个 invoke）；cli/pty fallback 到 mockBackend
 *   - M3：cli 用 invoke + Channel 流式（删 mockBackend.cli 引用）
 *   - M4：pty 用 tauri-pty 包（删 mockBackend.pty 引用）
 *   - M5：backend.ts 改 export tauriBackend（删 mockBackend 引用）
 */
import { invoke } from "@tauri-apps/api/core";
import type { Backend, CliApi, PtyApi, WorkspaceApi } from "@/api/contract";
import { mockBackend } from "@/api/mock/backend";

// ─────────────────────────────────────────────────────
// WorkspaceIo（M2 已实现）
// ─────────────────────────────────────────────────────

const workspace: WorkspaceApi = {
  listAgents: () => invoke("list_agents"),
  listClis: () => invoke("list_clis"),
  readManifest: (agent) => invoke("read_manifest", { agent }),
  readAgentSpec: (agent) => invoke("read_agent_spec", { agent }),
  readCliSpec: (cli) => invoke("read_cli_spec", { cli }),
  listRuns: (agent) => invoke("list_runs", { agent }),
  readRun: (agent, runId) => invoke("read_run", { agent, runId }),
  readWorkspaceTree: () => invoke("read_workspace_tree"),
};

// ─────────────────────────────────────────────────────
// CliRunner（M3 实现流式 Channel 桥接）
//
// M2 阶段暂用 mock，保留 import 占位；M3 替换为 invoke + Channel 实现。
// ─────────────────────────────────────────────────────

const cli: CliApi = mockBackend.cli;

// ─────────────────────────────────────────────────────
// PtyBridge（M4 用 tauri-plugin-pty）
//
// M2 阶段暂用 mock；M4 替换为 spawn/onData 封装。
// ─────────────────────────────────────────────────────

const pty: PtyApi = mockBackend.pty;

export const tauriBackend: Backend = { workspace, cli, pty };
