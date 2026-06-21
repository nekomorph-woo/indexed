/**
 * WorkspaceWizard — 首次启动 / 新建工作区向导。
 *
 * 两种模式：
 * - 打开已有：选已存在的 indexed 目录（有 VERSION 文件）
 * - 新建：从 .app 内嵌 baseline 释放到空目录 + 跑 init
 *
 * onDone 在 set_current_workspace 成功后被调用，触发 AppShell 重新渲染进主界面。
 */
import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";
import { Button, Card, Field, inputStyle } from "@/components/ui";

type Mode = "open" | "create";

interface Props {
  onDone: () => void;
}

export function WorkspaceWizard({ onDone }: Props) {
  const [mode, setMode] = useState<Mode>("create");
  const [targetDir, setTargetDir] = useState("");
  const [gitMode, setGitMode] = useState<"local" | "remote">("remote");
  const [remoteUrl, setRemoteUrl] = useState("");
  const [nick, setNick] = useState("Xi酱");
  const [addr, setAddr] = useState("您");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pick = async () => {
    const sel = await open({ directory: true, multiple: false });
    if (typeof sel === "string") {
      setTargetDir(sel);
      setError(null);
    }
  };

  const start = async () => {
    if (!targetDir) {
      setError("请先选择目录");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      if (mode === "create") {
        // 释放基线 + init + 注册工作区 + 切换
        await invoke("release_baseline", { targetDir });
        await invoke("init_workspace", {
          targetDir,
          mode: gitMode,
          remoteUrl: gitMode === "remote" ? remoteUrl || null : null,
          nick,
          addr,
        });
      }
      // 验证目录确实是 indexed 工作区（含 VERSION）
      await invoke("set_current_workspace", { path: targetDir });
      onDone();
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
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--ix-bg)",
        padding: 24,
      }}
    >
      <Card style={{ padding: 28, width: "100%", maxWidth: 560 }}>
        <h2 style={{ margin: "0 0 4px", fontSize: 18, fontWeight: 600 }}>
          欢迎使用 indexed
        </h2>
        <p style={{ margin: "0 0 20px", color: "var(--ix-text-muted)", fontSize: 13 }}>
          {mode === "create"
            ? "选择一个空目录作为新工作区，将释放 .app 内嵌基线并初始化"
            : "选择一个已存在的 indexed 工作区目录"}
        </p>

        {/* 模式切换 */}
        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
          <ModeButton active={mode === "create"} onClick={() => setMode("create")}>
            新建工作区
          </ModeButton>
          <ModeButton active={mode === "open"} onClick={() => setMode("open")}>
            打开已有
          </ModeButton>
        </div>

        {/* 目录选择 */}
        <Field label="工作区目录" required hint="空目录（新建）或已有 indexed 目录（打开）">
          <div style={{ display: "flex", gap: 8 }}>
            <input
              style={{ ...inputStyle, flex: 1 }}
              value={targetDir}
              placeholder="/Users/you/indexed"
              onChange={(e) => setTargetDir(e.target.value)}
              disabled={busy}
            />
            <Button variant="default" onClick={pick} disabled={busy}>
              浏览...
            </Button>
          </div>
        </Field>

        {/* 新建时的 init 配置 */}
        {mode === "create" && (
          <div style={{ marginTop: 16, padding: 16, background: "var(--ix-surface-alt)", borderRadius: "var(--ix-radius-sm)" }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ix-text-muted)", marginBottom: 10 }}>
              初始化配置
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Field label="Git 模式">
                <div style={{ display: "flex", gap: 12, paddingTop: 6 }}>
                  <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, cursor: "pointer" }}>
                    <input
                      type="radio"
                      checked={gitMode === "local"}
                      onChange={() => setGitMode("local")}
                      disabled={busy}
                    />
                    local
                  </label>
                  <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, cursor: "pointer" }}>
                    <input
                      type="radio"
                      checked={gitMode === "remote"}
                      onChange={() => setGitMode("remote")}
                      disabled={busy}
                    />
                    remote
                  </label>
                </div>
              </Field>
              {gitMode === "remote" && (
                <Field label="Remote URL">
                  <input
                    style={inputStyle}
                    value={remoteUrl}
                    placeholder="git@github.com:you/your-indexed.git"
                    onChange={(e) => setRemoteUrl(e.target.value)}
                    disabled={busy}
                  />
                </Field>
              )}
              <Field label="助手昵称">
                <input
                  style={inputStyle}
                  value={nick}
                  onChange={(e) => setNick(e.target.value)}
                  disabled={busy}
                />
              </Field>
              <Field label="对用户称呼">
                <input
                  style={inputStyle}
                  value={addr}
                  onChange={(e) => setAddr(e.target.value)}
                  disabled={busy}
                />
              </Field>
            </div>
          </div>
        )}

        {error && (
          <div
            style={{
              marginTop: 14,
              padding: "10px 12px",
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

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 18 }}>
          <Button variant="primary" onClick={start} disabled={busy || !targetDir}>
            {busy ? "处理中…" : mode === "create" ? "释放基线 + 初始化" : "打开工作区"}
          </Button>
        </div>
      </Card>
    </div>
  );
}

function ModeButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        flex: 1,
        padding: "10px 12px",
        fontSize: 13,
        fontWeight: active ? 600 : 400,
        color: active ? "var(--ix-primary)" : "var(--ix-text-muted)",
        background: active
          ? "color-mix(in srgb, var(--ix-primary) 10%, transparent)"
          : "transparent",
        border: `1px solid ${active ? "var(--ix-primary)" : "var(--ix-border)"}`,
        borderRadius: "var(--ix-radius-sm)",
        cursor: "pointer",
      }}
    >
      {children}
    </button>
  );
}
