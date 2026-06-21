//! 错误类型 + Result 别名。
//!
//! Tauri command 的返回 Result<T, AppError>，AppError 实现了 Serialize
//! 让前端能拿到结构化的错误信息（不是 Rust 的 Debug dump）。

use serde::{Serialize, Serializer};
use thiserror::Error;

pub type Result<T> = std::result::Result<T, AppError>;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("IO 错误: {0}")]
    Io(#[from] std::io::Error),

    #[error("YAML 解析错误: {0}")]
    Yaml(#[from] serde_yaml::Error),

    #[error("JSON 解析错误: {0}")]
    Json(#[from] serde_json::Error),

    #[error("路径不存在: {0}")]
    NotFound(String),

    #[error("路径遍历错误: {0}")]
    Walkdir(#[from] walkdir::Error),

    #[error("{0}")]
    Other(String),
}

impl From<anyhow::Error> for AppError {
    fn from(e: anyhow::Error) -> Self {
        AppError::Other(e.to_string())
    }
}

// Tauri 2 要求错误类型实现 Serialize；用 message 字段降级为字符串
#[derive(Serialize)]
struct SerializedError {
    message: String,
}

impl Serialize for AppError {
    fn serialize<S: Serializer>(&self, s: S) -> std::result::Result<S::Ok, S::Error> {
        SerializedError { message: self.to_string() }.serialize(s)
    }
}
