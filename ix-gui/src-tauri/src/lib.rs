//! ix-gui Tauri 应用入口。
//!
//! Builder 注册：
//! - tauri-plugin-pty（M4）
//! - AppState（workspace_root 改 RwLock 支持 M7 切换）
//! - WorkspaceIo 8 command（M2）
//! - CliRunner 4 command（M3）
//! - Workspaces 多工作区管理（M7.1）
//! - Baseline 释放/初始化/升级（M7.2）
//!
//! 启动 setup：读 ~/Library/Application Support/indexed/workspaces.json
//! 的 current，决定初始 workspace_root；不存在则前端进 wizard（M7.3）。

mod cli;
mod error;
mod models;
mod state;
mod workspaces;
mod workspace;

use state::AppState;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_pty::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            // 读 workspaces.json，决定初始 workspace_root
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
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
