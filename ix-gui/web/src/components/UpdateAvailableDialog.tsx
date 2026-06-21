/**
 * UpdateAvailableDialog — GitHub Release 新版可用提示（M11.4）。
 *
 * 与 UpgradeDialog 不同：
 * - UpgradeDialog：工作区基线升级（调 upgrade_baseline，跑 migration）
 * - UpdateAvailableDialog：.app 自身有新版（用户去 GitHub 下载新 .dmg）
 *
 * 触发源：AppShell 启动调 check_for_updates（GitHub Release API），
 * 有新版时 header 显示 badge，点击打开本 dialog。
 */
import { Button } from "./ui";

interface Props {
  currentVersion: string;
  latestVersion: string;
  changelog: string;
  releaseUrl: string;
  onClose: () => void;
}

export function UpdateAvailableDialog({
  currentVersion,
  latestVersion,
  changelog,
  releaseUrl,
  onClose,
}: Props) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          background: "var(--ix-surface)",
          borderRadius: "var(--ix-radius)",
          padding: 24,
          maxWidth: 560,
          maxHeight: "85vh",
          boxShadow: "var(--ix-shadow-hover)",
          border: "1px solid var(--ix-border)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h3 style={{ margin: "0 0 8px", fontSize: 16, fontWeight: 600 }}>
          🆕 indexed 新版可用
        </h3>
        <div style={{ fontSize: 13, color: "var(--ix-text-muted)", marginBottom: 16 }}>
          <div style={{ marginBottom: 4 }}>
            当前 .app 版本：<code style={{ color: "var(--ix-text)" }}>v{currentVersion}</code>
          </div>
          <div>
            GitHub 最新版本：<code style={{ color: "var(--ix-primary)" }}>v{latestVersion}</code>
          </div>
        </div>

        {changelog && (
          <div
            className="ix-mono"
            style={{
              marginBottom: 12,
              padding: 10,
              fontSize: 12,
              background: "var(--ix-bg)",
              color: "var(--ix-text)",
              borderRadius: "var(--ix-radius-sm)",
              border: "1px solid var(--ix-border)",
              whiteSpace: "pre-wrap",
              maxHeight: 220,
              overflowY: "auto",
              lineHeight: 1.5,
            }}
          >
            {changelog}
          </div>
        )}

        <div
          style={{
            padding: 10,
            background: "var(--ix-surface-alt)",
            borderRadius: "var(--ix-radius-sm)",
            fontSize: 13,
            color: "var(--ix-text-muted)",
            marginBottom: 16,
            lineHeight: 1.6,
          }}
        >
          下载新 .app 替换当前版本，启动后 UpgradeDialog 会引导你升级工作区基线。
          用户内容（reports/research/repos/自建 cli/agent）保留。
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: "auto" }}>
          <Button variant="ghost" onClick={onClose}>
            稍后
          </Button>
          <Button variant="primary" onClick={() => window.open(releaseUrl, "_blank")}>
            下载新版本
          </Button>
        </div>
      </div>
    </div>
  );
}
