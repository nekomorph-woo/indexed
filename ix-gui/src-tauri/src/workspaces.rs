//! 工作区注册表（多工作区切换 + 持久化）。
//!
//! 持久化位置：~/Library/Application Support/indexed/workspaces.json
//! 结构：{ recent: [path...], current: <path> | null }
//!
//! 所有命令通过 AppHandle 拿 config_dir，无 workspace_root 依赖。

use crate::state::AppState;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::{AppHandle, Manager, State};

#[derive(Serialize, Deserialize, Default, Clone)]
pub struct WorkspacesConfig {
    #[serde(default)]
    pub recent: Vec<String>,
    #[serde(default)]
    pub current: Option<String>,
}

#[derive(Serialize, Clone)]
pub struct WorkspaceEntry {
    pub path: String,
    pub is_current: bool,
    /// 工作区的 VERSION 文件内容（若存在）
    pub version: Option<String>,
    /// 工作区是否仍存在磁盘上（用户可能外部删除）
    pub exists: bool,
}

fn config_path(app: &AppHandle) -> Option<PathBuf> {
    app.path().app_config_dir().ok().map(|d| d.join("workspaces.json"))
}

fn read_config(app: &AppHandle) -> WorkspacesConfig {
    let Some(p) = config_path(app) else {
        return WorkspacesConfig::default();
    };
    if !p.is_file() {
        return WorkspacesConfig::default();
    }
    serde_json::from_str(&std::fs::read_to_string(p).unwrap_or_default()).unwrap_or_default()
}

fn write_config(app: &AppHandle, cfg: &WorkspacesConfig) -> Result<(), String> {
    let p = config_path(app).ok_or_else(|| "无法定位 app_config_dir".to_string())?;
    let parent = p.parent().ok_or_else(|| "config dir 无父目录".to_string())?;
    std::fs::create_dir_all(parent).map_err(|e| format!("创建 config dir 失败: {e}"))?;
    let body = serde_json::to_string_pretty(cfg).map_err(|e| e.to_string())?;
    std::fs::write(&p, body).map_err(|e| format!("写 workspaces.json 失败: {e}"))?;
    Ok(())
}

#[tauri::command]
pub async fn list_workspaces(app: AppHandle) -> Result<Vec<WorkspaceEntry>, String> {
    let cfg = read_config(&app);
    let current = cfg.current.clone();
    let entries = cfg
        .recent
        .iter()
        .map(|p| {
            let path_buf = PathBuf::from(p);
            let exists = path_buf.is_dir();
            let version = if exists {
                std::fs::read_to_string(path_buf.join("VERSION"))
                    .ok()
                    .map(|s| s.trim().to_string())
            } else {
                None
            };
            WorkspaceEntry {
                path: p.clone(),
                is_current: Some(p.clone()) == current,
                version,
                exists,
            }
        })
        .collect();
    Ok(entries)
}

#[tauri::command]
pub async fn add_workspace(app: AppHandle, path: String) -> Result<(), String> {
    let mut cfg = read_config(&app);
    cfg.recent.retain(|p| p != &path);
    cfg.recent.insert(0, path);
    write_config(&app, &cfg)
}

#[tauri::command]
pub async fn remove_workspace(app: AppHandle, path: String) -> Result<(), String> {
    let mut cfg = read_config(&app);
    cfg.recent.retain(|p| p != &path);
    if cfg.current.as_deref() == Some(path.as_str()) {
        cfg.current = None;
    }
    write_config(&app, &cfg)
}

#[tauri::command]
pub async fn set_current_workspace(
    app: AppHandle,
    state: State<'_, AppState>,
    path: String,
) -> Result<(), String> {
    let path_buf = PathBuf::from(&path);
    if !path_buf.is_dir() {
        return Err(format!("目录不存在: {path}"));
    }
    let mut cfg = read_config(&app);
    cfg.current = Some(path.clone());
    cfg.recent.retain(|p| p != &path);
    cfg.recent.insert(0, path);
    write_config(&app, &cfg)?;
    state.set_root(path_buf);
    Ok(())
}

#[tauri::command]
pub async fn has_current_workspace(app: AppHandle) -> Result<bool, String> {
    let cfg = read_config(&app);
    Ok(cfg
        .current
        .as_ref()
        .map(|p| PathBuf::from(p).is_dir())
        .unwrap_or(false))
}

/// 启动时调用：读 workspaces.json 的 current，返回 Some(path) 仅当目录仍存在
pub fn startup_current(app: &AppHandle) -> Option<PathBuf> {
    let cfg = read_config(app);
    cfg.current
        .filter(|p| PathBuf::from(p).is_dir())
        .map(PathBuf::from)
}
