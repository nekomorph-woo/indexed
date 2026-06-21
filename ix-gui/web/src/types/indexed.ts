/**
 * indexed 工作区的精确契约类型。
 * 来源：CLAUDE.md §3.5/§3.6、capability-spec.spec.md、manifest.template.yaml、run-yaml.example.yaml
 * 这些类型是 GUI 对 indexed 文件的解读模型，绝不反向定义 indexed（零侵入铁律）。
 */

// ─────────────────────────────────────────────────────────────
// manifest.yaml（ix-agents/ix-<business>-agent/manifest.yaml）
// ─────────────────────────────────────────────────────────────

/** manifest.params[] 的单个参数声明 */
export interface ManifestParam {
  name: string;
  required?: boolean;
  /** 给用户看的提示文案（必须写清业务含义） */
  prompt?: string;
  default?: unknown;
  /** 形如 "config/defaults.yaml#key" */
  default_from?: string;
}

/** manifest.steps[] 的 step。type 决定其余字段 */
export type ManifestStep = ToolShellStep | ToolWriteStep | ThinkingStep;

interface StepBase {
  id: string;
  type: "tool" | "thinking";
  description?: string;
}

export interface ToolShellStep extends StepBase {
  type: "tool";
  tool: "shell";
  command: string;
  expects?: string[];
}

export interface ToolWriteStep extends StepBase {
  type: "tool";
  tool: "write" | "copy";
  from: string;
  to: string;
}

export interface ThinkingStep extends StepBase {
  type: "thinking";
  inputs?: string[];
  prompt: string;
  output?: string;
  /** step 级覆盖执行器 */
  llm_executor?: string;
}

export interface Manifest {
  id: string;
  research?: string;
  params: ManifestParam[];
  artifacts?: string[];
  steps: ManifestStep[];
}

// ─────────────────────────────────────────────────────────────
// SPEC.yaml（artifacts/ix-*-cli/SPEC.yaml 与 ix-agents/ix-*/SPEC.yaml）
// ─────────────────────────────────────────────────────────────

export type SpecStatus = "implemented" | "planned" | "deprecated";

export interface CliSpecCommand {
  name: string;
  inputs: string[];
  outputs: string;
  example: string;
}

/** artifacts/ix-<domain>-cli/SPEC.yaml */
export interface CliSpec {
  name: string;
  domain: string;
  one_liner: string;
  status: SpecStatus;
  intents: string[];
  commands: CliSpecCommand[];
  credentials?: string[];
  depends_on?: string[];
  research?: string;
  notes?: string;
}

/** ix-agents/ix-<business>-agent/SPEC.yaml */
export interface AgentSpec {
  name: string;
  domain: string;
  one_liner: string;
  status: SpecStatus;
  intents: string[];
  params_required: string[];
  params_optional?: string[];
  has_thinking: boolean;
  steps: string[];
  schedule_safe?: boolean;
  schedule_note?: string;
  research?: string;
}

// ─────────────────────────────────────────────────────────────
// run.yaml（ix-agents/<agent>/runs/<run-id>/run.yaml）
// ─────────────────────────────────────────────────────────────

export type RunStatus = "running" | "completed" | "failed";
export type RunTrigger = "manual" | "scheduled";

export interface RunYaml {
  run_id: string;
  started_at: string; // ISO8601 带时区
  agent_id: string;
  trigger: RunTrigger;
  status: RunStatus;
  next_step: string | null;
  llm_executor?: string;
  params: Record<string, unknown>;
  steps_completed: string[];
}

// ─────────────────────────────────────────────────────────────
// GUI 视图模型（聚合多个文件，供视图直接消费）
// ─────────────────────────────────────────────────────────────

export interface AgentInfo {
  name: string; // 目录名 ix-<business>-agent
  domain: string;
  one_liner: string;
  status: SpecStatus;
  has_thinking: boolean;
  has_manifest: boolean;
  stepsSummary: string;
  requiredParams: string[];
  recentRunCount: number;
}

export interface CliInfo {
  name: string; // 目录名 ix-<domain>-cli
  domain: string;
  one_liner: string;
  status: SpecStatus;
  subcommands: string[];
  has_spec_yaml: boolean;
}

export interface RunSummary {
  run_id: string;
  agent_id: string;
  status: RunStatus;
  trigger: RunTrigger;
  started_at: string;
  steps_completed: string[];
  steps_total: number;
  next_step: string | null;
}

/** run 的完整详情（含产出文件） */
export interface RunDetail extends RunSummary {
  params: Record<string, unknown>;
  outputFiles: RunArtifactFile[];
  thinkingFiles: RunArtifactFile[];
  rawFiles: RunArtifactFile[];
}

export interface RunArtifactFile {
  /** 相对 run 目录的路径，如 output/report.md */
  relPath: string;
  name: string;
  size: number;
  /** 文件内容（文本）或 null（二进制/过大） */
  content: string | null;
  ext: string;
}

// ─────────────────────────────────────────────────────────────
// 索引审计（ix-workspace-index-cli audit --json 的产出）
// ─────────────────────────────────────────────────────────────

export type IssueLevel = "error" | "warn";

export interface AuditIssue {
  level: IssueLevel;
  code: string;
  message: string;
  target?: string;
}

export interface AuditReport {
  ok: boolean;
  workspace: string;
  clis: { name: string; subcommands: string[]; has_spec_yaml: boolean }[];
  agents: {
    name: string;
    has_thinking: boolean;
    steps_summary: string;
    required_params: string[];
    research?: string;
  }[];
  issues: AuditIssue[];
}

// ─────────────────────────────────────────────────────────────
// 执行流（CliRunner 调 run-cli 的流式事件）
// ─────────────────────────────────────────────────────────────

export type CliEvent =
  | { kind: "started"; run_id: string; agent_id: string }
  | { kind: "stdout"; line: string }
  | { kind: "stderr"; line: string }
  | { kind: "step"; step_id: string; status: "running" | "done" | "failed" }
  | { kind: "status"; status: RunStatus }
  | { kind: "finished"; run_id: string; exit_code: number; run_dir: string }
  | { kind: "error"; message: string };
