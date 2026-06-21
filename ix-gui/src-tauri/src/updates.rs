//! 检查更新（M11.1）。
//!
//! 不直接调 GitHub API（不引入 reqwest 等重依赖），而是 subprocess 调
//! ix-init-cli check-update --json，parse stdout。
//!
//! 符合零侵入铁律：GUI 只做只读展示 + 调用既有 CLI。

use crate::error::{AppError, Result};
use crate::models::InitStatus; // 复用既有 import 路径风格
use crate::state::AppState;
use serde::{Deserialize, Serialize};
use tauri::State;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateInfo {
    pub current_version: String,
    pub latest_version: String,
    pub has_update: bool,
    pub changelog: String,
    pub release_url: String,
}

/// 检查 GitHub Release 是否有新版基线。
///
/// `force=true` 跳过 24h 缓存（用户主动点「检查更新」按钮时）。
/// `force=false` 用缓存（启动时自动检查，快速返回）。
#[tauri::command]
pub async fn check_for_updates(
    state: State<'_, AppState>,
    force: Option<bool>,
) -> Result<UpdateInfo> {
    let workspace_root = state.root();
    let init_cli = workspace_root.join("artifacts/ix-init-cli/main.py");
    if !init_cli.is_file() {
        return Err(AppError::NotFound(format!(
            "工作区无 ix-init-cli: {}",
            init_cli.display()
        )));
    }

    let mut cmd = tokio::process::Command::new("python3");
    cmd.arg(&init_cli)
        .arg("check-update")
        .arg("--json")
        .current_dir(&workspace_root)
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .kill_on_drop(true);

    if force.unwrap_or(false) {
        cmd.arg("--force");
    }

    let output = cmd.output().await?;
    let stdout = String::from_utf8_lossy(&output.stdout);
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(AppError::Other(format!(
            "ix-init-cli check-update 退出码 {}: {}",
            output.status.code().unwrap_or(-1),
            stderr.trim()
        )));
    }

    let info: UpdateInfo = serde_json::from_str(&stdout).map_err(|e| {
        AppError::Other(format!("解析 check-update 输出失败: {e}\nstdout: {stdout}"))
    })?;

    Ok(info)
}

// 抑制未使用 import 警告（M11 扩展时可能用 InitStatus）
#[allow(dead_code)]
fn _types_marker(_: InitStatus) {}
