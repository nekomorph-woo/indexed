//! ix-gui Tauri 应用入口。
//!
//! Builder 注册：
//! - tauri-plugin-pty（M4 启用 PTY）
//! - AppState（workspace_root）
//! - WorkspaceIo 8 个 command
//! - CliRunner 4 个 command（M3 加）
//!
//! 阶段 2 渐进：
//! - M2（当前）：workspace 全部 + 占位 cli（panic 提示「M3 实现」）
//! - M3：cli 全部实现
//! - M4：pty 用插件实现
//! - M5：删 mockBackend 引用，全切换 tauriBackend

mod cli;
mod error;
mod models;
mod state;
mod workspace;

use state::AppState;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_pty::init())
        .manage(AppState::new())
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
            // CliRunner（M3）
            cli::run_agent,
            cli::audit,
            cli::sync,
            cli::init_status,
            // PtyBridge（M4 用插件，无需 command）
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
