//! ix-gui Tauri 应用入口。
//!
//! Builder 注册：
//! - tauri-plugin-pty（M4）
//! - tauri-plugin-dialog（M7.3 wizard 选目录）
//! - AppState（workspace_root 改 RwLock 支持 M7 切换）
//! - WorkspaceIo 8 command（M2）
//! - CliRunner 4 command（M3）
//! - Workspaces 多工作区管理（M7.1）
//! - Baseline 释放/初始化/升级（M7.2）
//!
//! 启动 setup：
//! 1. 注入 shell PATH（macOS GUI app 启动 PATH 是 launchd 的，不含
//!    nvm/asdf/homebrew，PTY 找不到 claude binary）
//! 2. 读 ~/Library/Application Support/indexed/workspaces.json 的 current，
//!    决定初始 workspace_root；不存在则前端进 wizard（M7.3）

mod cli;
mod error;
mod models;
mod state;
mod updates;
mod workspaces;
mod workspace;

use state::AppState;
use tauri::Manager;

/// macOS GUI app 启动时 PATH 是 launchd 的（/usr/bin:/bin:/usr/sbin:/sbin），
/// 不含 nvm/asdf/homebrew 等动态路径。跑 zsh -lic 拿用户 shell 完整 PATH
/// 注入 std::env::set_var，让后续 PTY/subprocess 都能找到 claude 等 binary。
///
/// Linux 用 bash -lc；Windows 暂不处理（用户手动配置 PATH）。
fn inject_shell_path() {
    let shell = if cfg!(target_os = "macos") {
        "zsh"
    } else {
        "bash"
    };
    let result = std::process::Command::new(shell)
        .args(["-lic", "echo $PATH"])
        .output();

    if let Ok(output) = result {
        if output.status.success() {
            let shell_path = String::from_utf8_lossy(&output.stdout).trim().to_string();
            if !shell_path.is_empty() {
                let existing = std::env::var("PATH").unwrap_or_default();
                // 用户 shell 的 PATH 优先（含 nvm/asdf），原有 PATH 作为 fallback
                let merged = if existing.is_empty() {
                    shell_path.clone()
                } else {
                    format!("{}:{}", shell_path, existing)
                };
                std::env::set_var("PATH", &merged);
                eprintln!("[setup] PATH 注入完成（shell 优先，原 PATH 兜底）");
            }
        } else {
            eprintln!(
                "[setup] shell PATH 获取失败（{} 退出码 {}），保留原 PATH",
                shell,
                output.status.code().unwrap_or(-1)
            );
        }
    } else {
        eprintln!("[setup] 找不到 {}，保留原 PATH", shell);
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_pty::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            // 1. 注入 shell PATH（让 PTY 找到 claude binary）
            inject_shell_path();
            // 2. 读 workspaces.json，决定初始 workspace_root
            let initial = workspaces::startup_current(&app.handle());
            app.manage(AppState::new(initial));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // WorkspaceIo（M2）
            workspace::list_agents,
            workspace::list_clis,
            workspace::read_manifest,
            workspace::read_agent_spec,
            workspace::read_cli_spec,
            workspace::list_runs,
            workspace::read_run,
            workspace::read_workspace_tree,
            workspace::get_workspace_root,
            workspace::get_workspace_version,
            // CliRunner（M3）
            cli::run_agent,
            cli::audit,
            cli::sync,
            cli::init_status,
            // Workspaces（M7.1）
            workspaces::list_workspaces,
            workspaces::add_workspace,
            workspaces::remove_workspace,
            workspaces::set_current_workspace,
            workspaces::has_current_workspace,
            // Baseline（M7.2）
            workspace::get_baseline_dir,
            workspace::get_baseline_version,
            workspace::release_baseline,
            workspace::init_workspace,
            workspace::upgrade_baseline,
            // 检查更新（M11.1）
            updates::check_for_updates,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
