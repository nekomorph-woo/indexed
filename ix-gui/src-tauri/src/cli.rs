//! CliRunner 命令实现（4 个）。
//!
//! 通过 subprocess 调用 Python CLI（artifacts/ix-*-cli/main.py）：
//! - run_agent: 流式 Channel（spawn ix-agent-run-cli，逐行解析 JSON Lines → CliEvent）
//! - audit:     一次性 JSON（ix-workspace-index-cli audit --json）
//! - sync:      文本判断（ix-workspace-index-cli sync，看是否 "无变更"）
//! - init_status: 文本解析（ix-init-cli status）

use crate::error::{AppError, Result};
use crate::models::{
    AuditReport, CliEvent, GitMode, InitStatus, RunAgentRequest, RunTrigger, StepStatus, SyncResult,
};
use crate::state::AppState;
use std::process::Stdio;
use tauri::ipc::Channel;
use tauri::State;
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command;

// ─────────────────────────────────────────────────────
// run_agent（流式）
// ─────────────────────────────────────────────────────

#[tauri::command]
pub async fn run_agent(
    req: RunAgentRequest,
    state: State<'_, AppState>,
    on_event: Channel<CliEvent>,
) -> Result<()> {
    let run_cli = state
        .workspace_root
        .join("artifacts/ix-agent-run-cli/main.py");

    if !run_cli.is_file() {
        let _ = on_event.send(CliEvent::Error {
            message: format!("ix-agent-run-cli/main.py 不存在: {}", run_cli.display()),
        });
        return Err(AppError::NotFound(run_cli.to_string_lossy().to_string()));
    }

    let mut cmd = Command::new("python3");
    cmd.arg(&run_cli)
        .arg("run")
        .arg("--agent")
        .arg(&req.agent)
        .current_dir(&state.workspace_root)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);

    for (k, v) in &req.params {
        cmd.arg("--set").arg(format!("{}={}", k, json_value_to_str(v)));
    }
    if let Some(trigger) = &req.trigger {
        cmd.arg("--trigger").arg(match trigger {
            RunTrigger::Manual => "manual",
            RunTrigger::Scheduled => "scheduled",
        });
    }
    if let Some(rid) = &req.resume_run_id {
        cmd.arg("--resume").arg("--run-id").arg(rid);
    }

    let mut child = cmd.spawn()?;
    let stdout = child.stdout.take().expect("stdout piped");
    let stderr = child.stderr.take().expect("stderr piped");

    // stdout → JSON Lines → CliEvent
    let stdout_reader = BufReader::new(stdout);
    let mut stdout_lines = stdout_reader.lines();
    while let Ok(Some(line)) = stdout_lines.next_line().await {
        match serde_json::from_str::<CliEvent>(&line) {
            Ok(event) => {
                let _ = on_event.send(event);
            }
            Err(_) => {
                // 非 JSON 行（runner.py 残留 print 或调试输出）：作为 stdout 透传
                let _ = on_event.send(CliEvent::Stdout { line });
            }
        }
    }

    // stderr → CliEvent::Stderr
    let stderr_reader = BufReader::new(stderr);
    let mut stderr_lines = stderr_reader.lines();
    while let Ok(Some(line)) = stderr_lines.next_line().await {
        let _ = on_event.send(CliEvent::Stderr { line });
    }

    let status = child.wait().await?;
    if !status.success() {
        let _ = on_event.send(CliEvent::Error {
            message: format!("进程退出码 {}", status.code().unwrap_or(-1)),
        });
    }
    Ok(())
}

fn json_value_to_str(v: &serde_json::Value) -> String {
    match v {
        serde_json::Value::String(s) => s.clone(),
        other => other.to_string(),
    }
}

// ─────────────────────────────────────────────────────
// audit / sync / init_status（一次性）
// ─────────────────────────────────────────────────────

#[tauri::command]
pub async fn audit(state: State<'_, AppState>) -> Result<AuditReport> {
    let report = run_json_cli::<AuditReport>(&state.workspace_root, "ix-workspace-index-cli", &["audit", "--json"]).await?;
    Ok(report)
}

#[tauri::command]
pub async fn sync(state: State<'_, AppState>) -> Result<SyncResult> {
    let out = run_text_cli(&state.workspace_root, "ix-workspace-index-cli", &["sync"]).await?;
    // sync 输出形如 "[sync] 无变更（用户区已是最新）" 或 "[sync] 已更新 X 个文件"
    let changed = !out.contains("无变更");
    let synced_files = parse_sync_count(&out);
    Ok(SyncResult {
        synced_files,
        changed,
    })
}

#[tauri::command]
pub async fn init_status(state: State<'_, AppState>) -> Result<InitStatus> {
    let out = run_text_cli(&state.workspace_root, "ix-init-cli", &["status"]).await?;
    parse_init_status(&out)
}

// ─────────────────────────────────────────────────────
// subprocess helpers
// ─────────────────────────────────────────────────────

async fn run_json_cli<T: serde::de::DeserializeOwned>(
    workspace_root: &std::path::Path,
    cli_name: &str,
    args: &[&str],
) -> Result<T> {
    let out = run_text_cli(workspace_root, cli_name, args).await?;
    Ok(serde_json::from_str(&out)?)
}

async fn run_text_cli(
    workspace_root: &std::path::Path,
    cli_name: &str,
    args: &[&str],
) -> Result<String> {
    let cli_path = workspace_root.join("artifacts").join(cli_name).join("main.py");
    if !cli_path.is_file() {
        return Err(AppError::NotFound(cli_path.to_string_lossy().to_string()));
    }

    let mut cmd = Command::new("python3");
    cmd.arg(&cli_path)
        .args(args)
        .current_dir(workspace_root)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);

    let output = cmd.output().await?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(AppError::Other(format!(
            "{} {} 退出码 {}: {}",
            cli_name,
            args.join(" "),
            output.status.code().unwrap_or(-1),
            stderr.trim()
        )));
    }
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

// ─────────────────────────────────────────────────────
// 文本解析 helpers（sync / init_status）
// ─────────────────────────────────────────────────────

fn parse_sync_count(out: &str) -> Vec<crate::models::SyncedFile> {
    // 当前 ix-workspace-index-cli sync 输出不含详细 file 清单
    // 简化：无变更 → 空；有变更 → 至少一项占位（changed=true 已表明语义）
    if out.contains("无变更") {
        vec![]
    } else {
        vec![crate::models::SyncedFile {
            file: "artifacts/capabilities.md".to_string(),
            count: 0,
        }]
    }
}

fn parse_init_status(out: &str) -> Result<InitStatus> {
    let mut version = String::from("?");
    let mut git_mode = GitMode::Uninitialized;
    let mut nick = String::from("?");
    let mut addr = String::from("?");
    let mut git_initialized = false;
    let mut remote: Option<String> = None;

    for line in out.lines() {
        let line = line.trim();
        if let Some(v) = line.strip_prefix("版本:") {
            version = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("Git 模式:") {
            git_mode = match v.trim() {
                "remote" => GitMode::Remote,
                "local" => GitMode::Local,
                _ => GitMode::Uninitialized,
            };
        } else if let Some(v) = line.strip_prefix("昵称:") {
            nick = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("称呼:") {
            addr = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("git init:") {
            git_initialized = v.trim() == "是";
        } else if line.starts_with("origin\t") {
            // 取第一行 origin
            if remote.is_none() {
                remote = Some(line.to_string());
            }
        }
    }

    Ok(InitStatus {
        version,
        git_mode,
        nick,
        addr,
        git_initialized,
        remote,
    })
}

// 抑制未使用警告（StepStatus 等 M3 不直接用，但保留对齐前端契约）
#[allow(dead_code)]
fn _types_marker(_: StepStatus) {}
