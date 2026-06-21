import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 纯 Web 阶段：Vite dev server，bb-browser 端到端验证
// 阶段 2（Tauri）会换成 Tauri 的 vite 配置，但 src/ 不动
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "127.0.0.1",
    // mock 数据走 src/api/mock，无需后端
  },
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});
