//! 应用全局状态。
//!
//! AppState.workspace_root 是所有 WorkspaceIo 命令的相对根。
//! 解析优先级：
//!   1. IX_WORKSPACE_ROOT 环境变量（测试 / 自定义）
//!   2. CARGO_MANIFEST_DIR 反推（src-tauri/ → ix-gui/ → indexed/）
//! 生产期 .app 不在源码树内，需要「切换工作区」UI（M5 后做）覆盖。

use std::path::PathBuf;

pub struct AppState {
    pub workspace_root: PathBuf,
}

impl Default for AppState {
    fn default() -> Self {
        Self::new()
    }
}

impl AppState {
    pub fn new() -> Self {
        let root = std::env::var("IX_WORKSPACE_ROOT")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                let manifest_dir = env!("CARGO_MANIFEST_DIR");
                PathBuf::from(manifest_dir)
                    .parent()
                    .expect("ix-gui/src-tauri/ 应有父目录 ix-gui/")
                    .parent()
                    .expect("ix-gui/ 应有父目录 indexed/")
                    .to_path_buf()
            });
        Self { workspace_root: root }
    }
}
