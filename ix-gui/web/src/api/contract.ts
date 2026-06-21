/**
 * 前后端契约层。
 *
 * 业务代码只 import 本文件的接口（listAgents / readManifest / runAgent / ...）。
 * 实现由 `backend.ts` 提供，它根据环境切换 mock / 真实后端：
 *   - web 阶段：MockBackend（src/api/mock/*）
 *   - Tauri 阶段：TauriBackend（调 invoke / event）
 *
 * Rust 侧（阶段 2）必须实现与这里 1:1 对应的 Tauri command：
 *   WorkspaceIo: list_agents / list_clis / read_manifest / read_agent_spec
 *                / read_cli_spec / list_runs / read_run / read_workspace_tree
 *   CliRunner:   run_agent / audit / sync / init_status
 *   PtyBridge:   pty_spawn / pty_input / pty_resize / pty_kill (+ event pty-data)
 */

import type {
  AgentInfo,
  AuditReport,
  CliInfo,
  Manifest,
  AgentSpec,
  CliSpec,
  RunSummary,
  RunDetail,
  CliEvent,
} from "@/types/indexed";

export interface WorkspaceApi {
  listAgents(): Promise<AgentInfo[]>;
  listClis(): Promise<CliInfo[]>;
  readManifest(agent: string): Promise<Manifest>;
  readAgentSpec(agent: string): Promise<AgentSpec>;
  readCliSpec(cli: string): Promise<CliSpec>;
  listRuns(agent: string): Promise<RunSummary[]>;
  readRun(agent: string, runId: string): Promise<RunDetail>;
  readWorkspaceTree(): Promise<TreeNode>;
}

export interface CliApi {
  /**
   * 执行 agent。返回异步迭代器，逐个 yield CliEvent（阶段 B）。
   * 两阶段中的「阶段 A：展示需求」由 UI 直接用 readManifest 渲染表单完成，
   * 本方法只负责阶段 B（用户确认后真正执行）。
   */
  runAgent(req: RunAgentRequest): AsyncIterable<CliEvent>;
  audit(): Promise<AuditReport>;
  sync(): Promise<SyncResult>;
  initStatus(): Promise<InitStatus>;
}

export interface PtyApi {
  /** 启动一个可见终端会话（阶段 2：PTY 跑交互式 claude） */
  spawn(req: PtySpawnRequest): Promise<{ sessionId: string }>;
  /** 用户在 xterm.js 输入 → 写入 PTY */
  input(sessionId: string, data: string): Promise<void>;
  resize(sessionId: string, cols: number, rows: number): Promise<void>;
  kill(sessionId: string): Promise<void>;
  /** 订阅 PTY 输出流（阶段 2：portable-pty reader） */
  onData(sessionId: string, cb: (data: string) => void): () => void;
}

// ── 请求/响应 DTO ──

export interface RunAgentRequest {
  agent: string;
  /** 参数覆盖（= 阶段 A 表单收集的值） */
  params: Record<string, unknown>;
  trigger?: "manual" | "scheduled";
  resumeRunId?: string;
}

export interface SyncResult {
  syncedFiles: { file: string; count: number }[];
  changed: boolean;
}

export interface InitStatus {
  version: string;
  gitMode: "local" | "remote" | "uninitialized";
  nick: string;
  addr: string;
  gitInitialized: boolean;
  remote?: string;
}

export interface PtySpawnRequest {
  cwd: string; // indexed 根
  command?: string; // 默认 "claude"
  cols?: number;
  rows?: number;
}

export interface TreeNode {
  name: string;
  path: string; // 相对 indexed 根
  kind: "bucket" | "dir" | "file";
  children?: TreeNode[];
}

/** 组合后端：业务代码通过它访问所有能力 */
export interface Backend {
  workspace: WorkspaceApi;
  cli: CliApi;
  pty: PtyApi;
}
