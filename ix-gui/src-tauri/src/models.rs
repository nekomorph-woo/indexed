//! 数据传输对象（DTO）—— 与前端 types/indexed.ts 1:1 对齐。
//!
//! 序列化字段名全部 snake_case，对齐 TS snake_case 命名。
//! CliEvent / ManifestStep 用 serde tagged enum，对应 TS 的 discriminated union。

use serde::{Deserialize, Serialize};

// ─────────────────────────────────────────────────────
// SPEC.yaml（CliSpec / AgentSpec）
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SpecStatus {
    Implemented,
    Planned,
    Deprecated,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CliSpecCommand {
    pub name: String,
    #[serde(default)]
    pub inputs: Vec<String>,
    #[serde(default)]
    pub outputs: String,
    #[serde(default)]
    pub example: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CliSpec {
    pub name: String,
    pub domain: String,
    pub one_liner: String,
    pub status: SpecStatus,
    #[serde(default)]
    pub intents: Vec<String>,
    #[serde(default)]
    pub commands: Vec<CliSpecCommand>,
    #[serde(default)]
    pub credentials: Vec<String>,
    #[serde(default)]
    pub depends_on: Vec<String>,
    #[serde(default)]
    pub research: Option<String>,
    #[serde(default)]
    pub notes: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentSpec {
    pub name: String,
    pub domain: String,
    pub one_liner: String,
    pub status: SpecStatus,
    #[serde(default)]
    pub intents: Vec<String>,
    #[serde(default)]
    pub params_required: Vec<String>,
    #[serde(default)]
    pub params_optional: Vec<String>,
    pub has_thinking: bool,
    #[serde(default)]
    pub steps: Vec<String>,
    #[serde(default)]
    pub schedule_safe: Option<bool>,
    #[serde(default)]
    pub schedule_note: Option<String>,
    #[serde(default)]
    pub research: Option<String>,
}

// ─────────────────────────────────────────────────────
// manifest.yaml
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ManifestParam {
    pub name: String,
    #[serde(default)]
    pub required: Option<bool>,
    #[serde(default)]
    pub prompt: Option<String>,
    #[serde(default)]
    pub default: Option<serde_json::Value>,
    #[serde(default, rename = "default_from")]
    pub default_from: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ManifestStep {
    Tool {
        id: String,
        #[serde(default)]
        description: Option<String>,
        tool: ToolKind,
        #[serde(default)]
        command: Option<String>,
        #[serde(default)]
        expects: Vec<String>,
        #[serde(default)]
        from: Option<String>,
        #[serde(default)]
        to: Option<String>,
    },
    Thinking {
        id: String,
        #[serde(default)]
        description: Option<String>,
        #[serde(default)]
        inputs: Vec<String>,
        prompt: String,
        #[serde(default)]
        output: Option<String>,
        #[serde(default = "default_executor", rename = "llm_executor")]
        llm_executor: Option<String>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ToolKind {
    Shell,
    Write,
    Copy,
}

fn default_executor() -> Option<String> {
    None
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Manifest {
    pub id: String,
    #[serde(default)]
    pub research: Option<String>,
    #[serde(default)]
    pub params: Vec<ManifestParam>,
    #[serde(default)]
    pub artifacts: Vec<String>,
    pub steps: Vec<ManifestStep>,
}

// ─────────────────────────────────────────────────────
// run.yaml
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RunStatus {
    Running,
    Completed,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RunTrigger {
    Manual,
    Scheduled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunYaml {
    pub run_id: String,
    pub started_at: String,
    pub agent_id: String,
    pub trigger: RunTrigger,
    pub status: RunStatus,
    pub next_step: Option<String>,
    #[serde(default, rename = "llm_executor")]
    pub llm_executor: Option<String>,
    #[serde(default)]
    pub params: serde_json::Map<String, serde_json::Value>,
    #[serde(default)]
    pub steps_completed: Vec<String>,
}

// ─────────────────────────────────────────────────────
// GUI 视图模型（聚合多个文件）
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentInfo {
    pub name: String,
    pub domain: String,
    pub one_liner: String,
    pub status: SpecStatus,
    pub has_thinking: bool,
    pub has_manifest: bool,
    pub steps_summary: String,
    pub required_params: Vec<String>,
    #[serde(default)]
    pub recent_run_count: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CliInfo {
    pub name: String,
    pub domain: String,
    pub one_liner: String,
    pub status: SpecStatus,
    pub subcommands: Vec<String>,
    pub has_spec_yaml: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunSummary {
    pub run_id: String,
    pub agent_id: String,
    pub status: RunStatus,
    pub trigger: RunTrigger,
    pub started_at: String,
    pub steps_completed: Vec<String>,
    pub steps_total: i64,
    pub next_step: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunArtifactFile {
    #[serde(rename = "relPath")]
    pub rel_path: String,
    pub name: String,
    pub size: u64,
    #[serde(default)]
    pub content: Option<String>,
    pub ext: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunDetail {
    #[serde(flatten)]
    pub summary: RunSummary,
    pub params: serde_json::Map<String, serde_json::Value>,
    #[serde(rename = "outputFiles")]
    pub output_files: Vec<RunArtifactFile>,
    #[serde(rename = "thinkingFiles")]
    pub thinking_files: Vec<RunArtifactFile>,
    #[serde(rename = "rawFiles")]
    pub raw_files: Vec<RunArtifactFile>,
}

// ─────────────────────────────────────────────────────
// 资产树
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TreeNodeKind {
    Bucket,
    Dir,
    File,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TreeNode {
    pub name: String,
    pub path: String,
    pub kind: TreeNodeKind,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub children: Vec<TreeNode>,
}

// ─────────────────────────────────────────────────────
// CliEvent（run_agent 流式事件）
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum StepStatus {
    Running,
    Done,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum CliEvent {
    Started {
        #[serde(rename = "run_id")]
        run_id: String,
        #[serde(rename = "agent_id")]
        agent_id: String,
    },
    Stdout {
        line: String,
    },
    Stderr {
        line: String,
    },
    Step {
        #[serde(rename = "step_id")]
        step_id: String,
        status: StepStatus,
    },
    Status {
        status: RunStatus,
    },
    Finished {
        #[serde(rename = "run_id")]
        run_id: String,
        #[serde(rename = "exit_code")]
        exit_code: i32,
        #[serde(rename = "run_dir")]
        run_dir: String,
    },
    Error {
        message: String,
    },
}

// ─────────────────────────────────────────────────────
// Audit / Sync / Init
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum IssueLevel {
    Error,
    Warn,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditIssue {
    pub level: IssueLevel,
    pub code: String,
    pub message: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub target: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditAgentEntry {
    pub name: String,
    pub has_thinking: bool,
    pub steps_summary: String,
    pub required_params: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub research: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditCliEntry {
    pub name: String,
    pub subcommands: Vec<String>,
    pub has_spec_yaml: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditReport {
    pub ok: bool,
    pub workspace: String,
    pub clis: Vec<AuditCliEntry>,
    pub agents: Vec<AuditAgentEntry>,
    pub issues: Vec<AuditIssue>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncedFile {
    pub file: String,
    pub count: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncResult {
    #[serde(rename = "syncedFiles")]
    pub synced_files: Vec<SyncedFile>,
    pub changed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum GitMode {
    Local,
    Remote,
    Uninitialized,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InitStatus {
    pub version: String,
    #[serde(rename = "gitMode")]
    pub git_mode: GitMode,
    pub nick: String,
    pub addr: String,
    #[serde(rename = "gitInitialized")]
    pub git_initialized: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub remote: Option<String>,
}

// ─────────────────────────────────────────────────────
// 请求 DTO
// ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Deserialize)]
pub struct RunAgentRequest {
    pub agent: String,
    #[serde(default)]
    pub params: serde_json::Map<String, serde_json::Value>,
    #[serde(default)]
    pub trigger: Option<RunTrigger>,
    #[serde(default, rename = "resumeRunId")]
    pub resume_run_id: Option<String>,
}
