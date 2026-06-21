/**
 * Backend 切换点（M5 已切换）。
 *
 * 当前：tauriBackend（Rust 端 WorkspaceIo + CliRunner + tauri-plugin-pty）
 * 业务代码通过本文件 export 的 backend 访问所有能力。
 *
 * mock 代码保留在 ./mock/，仅用于：
 *   - 写测试时复用 mock 数据
 *   - 阶段 1 验收回退调试
 * 主 export 不再 import mockBackend。
 *
 * 若将来需要双模式（纯 web demo + Tauri），可改为：
 *   const isTauri = "__TAURI_INTERNALS__" in window;
 *   export const backend = isTauri ? tauriBackend : mockBackend;
 */
import { tauriBackend } from "./tauri/backend";

export const backend = tauriBackend;
export type { Backend, WorkspaceApi, CliApi, PtyApi } from "./contract";
