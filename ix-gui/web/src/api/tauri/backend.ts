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
import { Channel, invoke } from "@tauri-apps/api/core";
import type { Backend, CliApi, PtyApi, RunAgentRequest, WorkspaceApi } from "@/api/contract";
import type { CliEvent } from "@/types/indexed";
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
// CliRunner（M3 已实现）
//
// run_agent 用 Tauri v2 Channel 流式：每次 invoke 携带一个 Channel<CliEvent>
// 作为 onEvent 参数；Rust 端 on_event.send(CliEvent) 推送，前端 onmessage 接收。
// 这里把 Channel 适配为 TS AsyncIterable<CliEvent>，业务代码用 for-await 消费。
// ─────────────────────────────────────────────────────

const cli: CliApi = {
  async *runAgent(req: RunAgentRequest): AsyncIterable<CliEvent> {
    const channel = new Channel<CliEvent>();
    const queue: CliEvent[] = [];
    let resolveNext: ((v: IteratorResult<CliEvent>) => void) | null = null;
    let finished = false;

    channel.onmessage = (msg) => {
      if (resolveNext) {
        const r = resolveNext;
        resolveNext = null;
        r({ value: msg, done: false });
      } else {
        queue.push(msg);
      }
    };

    // invoke 返回 Promise（Rust 端 return Ok(()) 时 resolve）
    const invokePromise = invoke("run_agent", { req, onEvent: channel })
      .then(() => {
        finished = true;
        if (resolveNext) {
          const r = resolveNext;
          resolveNext = null;
          r({ value: undefined, done: true });
        }
      })
      .catch((e: unknown) => {
        // invoke 失败（Rust 端返回 Err）：作为 error event 推送
        const errMsg = e instanceof Error ? e.message : String(e);
        queue.push({ kind: "error", message: errMsg });
        finished = true;
        if (resolveNext) {
          const r = resolveNext;
          resolveNext = null;
          r({ value: undefined, done: true });
        }
      });

    while (!finished || queue.length > 0) {
      if (queue.length > 0) {
        yield queue.shift() as CliEvent;
      } else {
        const next = await new Promise<IteratorResult<CliEvent>>((res) => {
          resolveNext = res;
        });
        if (next.done) break;
        yield next.value as CliEvent;
      }
    }

    await invokePromise;
  },
  audit: () => invoke("audit"),
  sync: () => invoke("sync"),
  initStatus: () => invoke("init_status"),
};

// ─────────────────────────────────────────────────────
// PtyBridge（M4 用 tauri-plugin-pty）
//
// M3 阶段暂用 mock；M4 替换为 spawn/onData 封装。
// ─────────────────────────────────────────────────────

const pty: PtyApi = mockBackend.pty;

export const tauriBackend: Backend = { workspace, cli, pty };
