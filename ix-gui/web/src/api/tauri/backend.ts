/**
 * TauriBackend —— Tauri+Rust 阶段的真实后端实现（M2-M5 全部完成）。
 *
 * 业务代码不直接 import 本文件；通过 `api/backend.ts` 的 export 间接使用。
 * backend.ts（M5）已切换为 export tauriBackend；mock 代码仅保留用于测试。
 */
import { Channel, invoke } from "@tauri-apps/api/core";
import { spawn } from "tauri-pty";
import type { Backend, CliApi, PtyApi, PtySpawnRequest, RunAgentRequest, WorkspaceApi } from "@/api/contract";
import type { CliEvent } from "@/types/indexed";

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
// PtyBridge（M4 已实现 — 封装 tauri-plugin-pty）
//
// 用 tauri-plugin-pty 插件（Rust 端 portable-pty）。前端 spawn 拿到 pty
// 句柄；onData 订阅输出；write/resize/kill 控制。
// ─────────────────────────────────────────────────────

type PtyHandle = ReturnType<typeof spawn>;

class TauriPty implements PtyApi {
  private sessions = new Map<string, PtyHandle>();

  async spawn(req: PtySpawnRequest) {
    const sessionId = `pty-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const pty = spawn(req.command ?? "claude", [], {
      cwd: req.cwd,
      cols: req.cols ?? 80,
      rows: req.rows ?? 24,
    });
    this.sessions.set(sessionId, pty);
    return { sessionId };
  }

  async input(sessionId: string, data: string) {
    this.sessions.get(sessionId)?.write(data);
  }

  async resize(sessionId: string, cols: number, rows: number) {
    this.sessions.get(sessionId)?.resize(cols, rows);
  }

  async kill(sessionId: string) {
    const pty = this.sessions.get(sessionId);
    if (pty) {
      pty.kill();
      this.sessions.delete(sessionId);
    }
  }

  onData(sessionId: string, cb: (data: string) => void): () => void {
    const pty = this.sessions.get(sessionId);
    if (!pty) return () => {};
    // tauri-pty 的 onData 接收 Uint8Array，返回 IDisposable
    const decoder = new TextDecoder();
    const disposable = pty.onData((e: Uint8Array) => cb(decoder.decode(e)));
    return () => disposable.dispose();
  }
}

const pty: PtyApi = new TauriPty();

export const tauriBackend: Backend = { workspace, cli, pty };
