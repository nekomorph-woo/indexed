//! 应用全局状态。
//!
//! AppState.workspace_root 是所有 WorkspaceIo/CliRunner 命令的相对根。
//! 用 RwLock<PathBuf> 支持「切换工作区」UI 改写。
//!
//! 启动时从 ~/Library/Application Support/indexed/workspaces.json 读
//! current；不存在则 workspace_root 为空（PathBuf::default()），前端进 wizard。

use std::path::PathBuf;
use std::sync::RwLock;

pub struct AppState {
    workspace_root: RwLock<PathBuf>,
}

impl Default for AppState {
    fn default() -> Self {
        Self::new(None)
    }
}

impl AppState {
    pub fn new(initial: Option<PathBuf>) -> Self {
        Self {
            workspace_root: RwLock::new(initial.unwrap_or_default()),
        }
    }

    /// 当前 workspace_root 的克隆。空 PathBuf 表示未设置（前端进 wizard）。
    pub fn root(&self) -> PathBuf {
        self.workspace_root.read().unwrap().clone()
    }

    pub fn has_root(&self) -> bool {
        let guard = self.workspace_root.read().unwrap();
        !guard.as_os_str().is_empty() && guard.is_dir()
    }

    /// 切换工作区（设置页 / wizard / 启动时调用）
    pub fn set_root(&self, new_root: PathBuf) {
        *self.workspace_root.write().unwrap() = new_root;
    }
}
