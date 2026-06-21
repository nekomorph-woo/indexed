/**
 * AppShell —— 主框架。
 * 布局：左侧资产树（只读，所有视图共享）+ 顶部导航（视图切换 + 主题 + 状态）
 *
 * 设计取舍：资产树常驻左侧（indexed 的结构是 GUI 的导航地图），
 * 主区按视图切换。会话/Agents/Runs/索引/设置 五个视图。
 */
import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { AssetTree } from "./AssetTree";
import { AgentsView } from "@/views/AgentsView";
import { RunsView } from "@/views/RunsView";
import { IndexDashboard } from "@/views/IndexDashboard";
import { TerminalView } from "@/views/TerminalView";
import { SettingsView } from "@/views/SettingsView";
import { useThemeStore, applyTheme } from "@/theme/themeStore";
import { backend } from "@/api/backend";
import type { InitStatus } from "@/api/contract";
import { Badge } from "./ui";
import { UpdateAvailableDialog } from "./UpdateAvailableDialog";

type ViewId = "terminal" | "agents" | "runs" | "index" | "settings";

interface UpdateInfo {
  current_version: string;
  latest_version: string;
  has_update: boolean;
  changelog: string;
  release_url: string;
}

const NAV: { id: ViewId; label: string; icon: string }[] = [
  { id: "terminal", label: "会话", icon: "💬" },
  { id: "agents", label: "Agents", icon: "🤖" },
  { id: "runs", label: "Runs", icon: "📦" },
  { id: "index", label: "索引", icon: "🔍" },
  { id: "settings", label: "设置", icon: "⚙️" },
];

export function AppShell() {
  const [view, setView] = useState<ViewId>("terminal");
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [init, setInit] = useState<InitStatus | null>(null);
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [showUpdateDialog, setShowUpdateDialog] = useState(false);
  const current = useThemeStore((s) => s.current);

  // 应用主题（设计语言 token → CSS 变量）
  useEffect(() => {
    applyTheme(current);
  }, [current]);

  // 加载工作区状态（顶部状态条）
  useEffect(() => {
    backend.cli.initStatus().then(setInit).catch(() => {});
  }, []);

  // 启动异步检查 GitHub Release（force=false 用 24h 缓存）
  useEffect(() => {
    invoke<UpdateInfo>("check_for_updates", { force: false })
      .then((info) => {
        if (info.has_update) setUpdateInfo(info);
      })
      .catch(() => {});  // 静默失败（网络问题不阻塞主界面）
  }, []);

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      {/* 左侧：资产树 */}
      <aside
        style={{
          width: "var(--ix-sidebar-w)",
          borderRight: "1px solid var(--ix-border)",
          background: "var(--ix-surface)",
          display: "flex",
          flexDirection: "column",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            height: "var(--ix-header-h)",
            display: "flex",
            alignItems: "center",
            padding: "0 14px",
            borderBottom: "1px solid var(--ix-border)",
            gap: 8,
          }}
        >
          <span style={{ fontSize: 18 }}>🗂️</span>
          <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: 0.3 }}>indexed</span>
          {init && (
            <span className="ix-mono" style={{ fontSize: 12, color: "var(--ix-text-muted)", marginLeft: "auto" }}>
              v{init.version}
            </span>
          )}
        </div>
        <div style={{ flex: 1, overflow: "hidden" }}>
          <AssetTree onSelect={setSelectedAsset} />
        </div>
        {selectedAsset && (
          <div
            className="ix-mono"
            style={{
              padding: "6px 12px",
              borderTop: "1px solid var(--ix-border)",
              fontSize: 12,
              color: "var(--ix-text-muted)",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
            title={selectedAsset || "indexed/"}
          >
            {selectedAsset || "indexed/"}
          </div>
        )}
      </aside>

      {/* 右侧：主区 */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        {/* 顶部导航 */}
        <header
          style={{
            height: "var(--ix-header-h)",
            display: "flex",
            alignItems: "center",
            borderBottom: "1px solid var(--ix-border)",
            padding: "0 16px",
            gap: 4,
            background: "var(--ix-surface)",
          }}
        >
          {NAV.map((n) => (
            <button
              key={n.id}
              onClick={() => setView(n.id)}
              style={{
                background: view === n.id ? "var(--ix-surface-alt)" : "transparent",
                border: "none",
                borderRadius: "var(--ix-radius-pill)",
                padding: "6px 14px",
                fontSize: 14,
                fontWeight: view === n.id ? 600 : 400,
                color: view === n.id ? "var(--ix-primary)" : "var(--ix-text-muted)",
                display: "flex",
                alignItems: "center",
                gap: 6,
                transition: "all 0.2s var(--ix-easing)",
              }}
            >
              <span style={{ fontSize: 15 }}>{n.icon}</span>
              {n.label}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          {updateInfo && (
            <button
              onClick={() => setShowUpdateDialog(true)}
              title={`新版 v${updateInfo.latest_version} 可用（点击查看）`}
              style={{
                background: "var(--ix-primary)",
                color: "#fff",
                border: "none",
                borderRadius: "var(--ix-radius-pill)",
                padding: "4px 10px",
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 4,
              }}
            >
              🆕 v{updateInfo.latest_version}
            </button>
          )}
          {init && (
            <>
              <Badge tone={init.gitMode === "remote" ? "success" : "neutral"}>{init.gitMode}</Badge>
              <span style={{ fontSize: 13, color: "var(--ix-text-muted)" }}>
                {init.nick} · {init.addr}
              </span>
            </>
          )}
        </header>

        {/* 视图区 */}
        <div className="ix-fade-in" key={view} style={{ flex: 1, overflow: "hidden", padding: 16, minHeight: 0 }}>
          {view === "terminal" && <TerminalView />}
          {view === "agents" && <AgentsView />}
          {view === "runs" && <RunsView />}
          {view === "index" && <IndexDashboard />}
          {view === "settings" && <SettingsView />}
        </div>
      </main>

      {showUpdateDialog && updateInfo && (
        <UpdateAvailableDialog
          currentVersion={updateInfo.current_version}
          latestVersion={updateInfo.latest_version}
          changelog={updateInfo.changelog}
          releaseUrl={updateInfo.release_url}
          onClose={() => setShowUpdateDialog(false)}
        />
      )}
    </div>
  );
}
