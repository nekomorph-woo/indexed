import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite dev server：被 tauri.conf.json 的 beforeDevCommand 调用，
// 供 cargo tauri dev 期间 Tauri webview 加载（devUrl: http://localhost:5173）。
// 单独 npm run dev 也能跑（仅 UI 静态预览，所有 invoke 会失败——
// 业务代码 import 自 @tauri-apps/api，浏览器环境无 window.__TAURI_INTERNALS__）。
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "127.0.0.1",
  },
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});
