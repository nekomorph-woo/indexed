/**
 * UpgradeDialog — 基线升级引导。
 *
 * 启动时检测到 workspace VERSION < baseline VERSION 时弹出。
 * 调用 upgrade_baseline → ix-init-cli update <baseline> + 自动 sync。
 */
import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Button } from "./ui";

interface Props {
  from: string;
  to: string;
  onClose: () => void;
  onUpgraded: () => void;
}

export function UpgradeDialog({ from, to, onClose, onUpgraded }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upgrade = async () => {
    setBusy(true);
    setError(null);
    try {
      await invoke("upgrade_baseline");
      onUpgraded();
    } catch (e: unknown) {
      const msg = typeof e === "object" && e && "message" in e
        ? String((e as { message: unknown }).message)
        : String(e);
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

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
          maxWidth: 480,
          boxShadow: "var(--ix-shadow-hover)",
          border: "1px solid var(--ix-border)",
        }}
      >
        <h3 style={{ margin: "0 0 8px", fontSize: 16, fontWeight: 600 }}>
          发现基线更新
        </h3>
        <div style={{ fontSize: 13, color: "var(--ix-text-muted)", marginBottom: 16 }}>
          <div style={{ marginBottom: 4 }}>
            当前工作区基线：<code style={{ color: "var(--ix-text)" }}>v{from}</code>
          </div>
          <div>
            .app 内嵌基线：<code style={{ color: "var(--ix-primary)" }}>v{to}</code>
          </div>
        </div>

        <div
          style={{
            padding: 12,
            background: "var(--ix-surface-alt)",
            borderRadius: "var(--ix-radius-sm)",
            fontSize: 13,
            color: "var(--ix-text-muted)",
            marginBottom: 16,
            lineHeight: 1.6,
          }}
        >
          升级会保护用户内容（reports/research/repos/自建 cli/agent），
          仅覆盖框架文件（CLAUDE.md/.claude/_shared/基线 cli）。
          升级后自动跑 sync 同步索引。
        </div>

        {error && (
          <div
            style={{
              marginBottom: 12,
              padding: "8px 10px",
              fontSize: 13,
              color: "var(--ix-danger)",
              background: "color-mix(in srgb, var(--ix-danger) 8%, transparent)",
              borderRadius: "var(--ix-radius-sm)",
              wordBreak: "break-word",
            }}
          >
            {error}
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
          <Button variant="ghost" onClick={onClose} disabled={busy}>
            稍后
          </Button>
          <Button variant="primary" onClick={upgrade} disabled={busy}>
            {busy ? "升级中…" : "升级基线"}
          </Button>
        </div>
      </div>
    </div>
  );
}
