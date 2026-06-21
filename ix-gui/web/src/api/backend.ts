/**
 * Backend 切换点。
 * web 阶段：mockBackend
 * Tauri 阶段：替换为 tauriBackend（调 invoke/event），本文件是唯一要改的地方。
 */
import { mockBackend } from "./mock/backend";

export const backend = mockBackend;
export type { Backend, WorkspaceApi, CliApi, PtyApi } from "./contract";
