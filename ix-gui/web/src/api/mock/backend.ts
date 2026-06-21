/**
 * MockBackend —— web 阶段的后端实现。
 * 严格实现 contract.ts 的 Backend 接口，返回 fixtures 的数据。
 * Tauri 阶段会被 TauriBackend 取代，业务代码零改动（只换 backend.ts 的导出）。
 */
import type { Backend, RunAgentRequest, PtySpawnRequest } from "@/api/contract";
import type { CliEvent, RunDetail, RunSummary } from "@/types/indexed";
import {
  mockAgents,
  mockClis,
  mockManifests,
  mockAgentSpecs,
  mockCliSpecs,
  mockRuns,
  mockRunDetails,
  mockAudit,
  mockSync,
  mockInit,
  mockTree,
} from "./fixtures";

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

const workspace = {
  async listAgents() {
    await delay(120);
    return mockAgents;
  },
  async listClis() {
    await delay(100);
    return mockClis;
  },
  async readManifest(agent: string) {
    await delay(80);
    const m = mockManifests[agent];
    if (!m) throw new Error(`未找到 manifest: ${agent}`);
    return m;
  },
  async readAgentSpec(agent: string) {
    await delay(80);
    const s = mockAgentSpecs[agent];
    if (!s) throw new Error(`未找到 SPEC.yaml: ${agent}`);
    return s;
  },
  async readCliSpec(cli: string) {
    await delay(80);
    const s = mockCliSpecs[cli];
    if (!s) throw new Error(`未找到 SPEC.yaml: ${cli}`);
    return s;
  },
  async listRuns(agent: string) {
    await delay(100);
    return (mockRuns[agent] ?? []) as RunSummary[];
  },
  async readRun(agent: string, runId: string) {
    await delay(100);
    const key = `${agent}/${runId}`;
    const d = mockRunDetails[key];
    if (d) return d as RunDetail;
    // 没有详细 mock 的 run，退回到 summary 级别的空详情
    const summary = (mockRuns[agent] ?? []).find((r) => r.run_id === runId);
    if (!summary) throw new Error(`未找到 run: ${agent}/${runId}`);
    return {
      ...summary,
      params: {},
      outputFiles: [],
      thinkingFiles: [],
      rawFiles: [],
    } as RunDetail;
  },
  async readWorkspaceTree() {
    await delay(120);
    return mockTree;
  },
};

const cli = {
  async *runAgent(req: RunAgentRequest): AsyncIterable<CliEvent> {
    // 模拟 run-cli 的流式输出
    const runId = `2026-06-20_${new Date().toTimeString().slice(0, 8).replace(/:/g, "-")}`;
    yield { kind: "started", run_id: runId, agent_id: req.agent };
    yield { kind: "stdout", line: `indexed run @ ${new Date().toISOString()}` };
    yield { kind: "stdout", line: `agent: ${req.agent}  trigger: ${req.trigger ?? "manual"}` };

    const manifest = mockManifests[req.agent];
    if (!manifest) {
      yield { kind: "error", message: `未找到 manifest: ${req.agent}` };
      return;
    }

    for (const step of manifest.steps) {
      yield { kind: "step", step_id: step.id, status: "running" };
      const desc =
        step.description ??
        (step.type === "thinking" ? "语义分析（claude -p）" : step.tool === "shell" ? "执行 shell" : "复制文件");
      yield { kind: "stdout", line: `[${step.id}] ${desc}` };
      if (step.type === "tool" && step.tool === "shell") {
        // 显示脱敏后的命令（截断）
        const cmd = "command" in step ? step.command.slice(0, 96) : "";
        yield { kind: "stdout", line: `  $ ${cmd}${("command" in step && step.command.length > 96) ? "..." : ""}` };
      }
      if (step.type === "thinking") {
        yield { kind: "stdout", line: `  ⟳ thinking（claude -p，用户不可见）...` };
        await delay(900);
      } else {
        await delay(500);
      }
      yield { kind: "stdout", line: `  ✓ ${step.id} done` };
      yield { kind: "step", step_id: step.id, status: "done" };
    }

    yield { kind: "status", status: "completed" };
    yield {
      kind: "finished",
      run_id: runId,
      exit_code: 0,
      run_dir: `ix-agents/${req.agent}/runs/${runId}`,
    };
  },
  async audit() {
    await delay(200);
    return mockAudit;
  },
  async sync() {
    await delay(300);
    return mockSync;
  },
  async initStatus() {
    await delay(100);
    return mockInit;
  },
};

// PtyApi 在 web 阶段是占位（没有真实 PTY）；
// 会话页会用一个「终端模拟器」组件假装回显，让交互可验证
const pty = {
  async spawn(_req: PtySpawnRequest) {
    await delay(50);
    return { sessionId: `mock-${Date.now()}` };
  },
  async input(_sessionId: string, _data: string) {
    // no-op（web 阶段终端是前端自洽的占位）
  },
  async resize(_sessionId: string, _cols: number, _rows: number) {},
  async kill(_sessionId: string) {},
  onData(_sessionId: string, _cb: (data: string) => void) {
    return () => {};
  },
};

export const mockBackend: Backend = { workspace, cli, pty };
