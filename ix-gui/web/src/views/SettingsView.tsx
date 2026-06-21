/**
 * 设置页 —— 工作区切换（M7.4）+ 主题切换（M2）+ 零侵入铁律说明。
 */
import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";
import { Badge, Button, Card, EmptyState, Spinner } from "@/components/ui";
import { designLanguageList } from "@/theme/designLanguages";
import { useThemeStore } from "@/theme/themeStore";

interface WorkspaceEntry {
  path: string;
  is_current: boolean;
  version: string | null;
  exists: boolean;
}

export function SettingsView() {
  const { current, setTheme } = useThemeStore();
  const [workspaces, setWorkspaces] = useState<WorkspaceEntry[] | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    invoke<WorkspaceEntry[]>("list_workspaces")
      .then(setWorkspaces)
      .catch((e) => setError(String(e)));
  }, [reloadKey]);

  const refresh = () => setReloadKey((k) => k + 1);

  const openExisting = async () => {
    const sel = await open({ directory: true, multiple: false });
    if (typeof sel !== "string") return;
    setBusy(true);
    setError(null);
    try {
      await invoke("set_current_workspace", { path: sel });
      setTimeout(() => window.location.reload(), 200);
    } catch (e: unknown) {
      const msg = typeof e === "object" && e && "message" in e
        ? String((e as { message: unknown }).message)
        : String(e);
      setError(msg);
      setBusy(false);
    }
  };

  const switchTo = async (path: string) => {
    setBusy(true);
    setError(null);
    try {
      await invoke("set_current_workspace", { path });
      setTimeout(() => window.location.reload(), 200);
    } catch (e: unknown) {
      const msg = typeof e === "object" && e && "message" in e
        ? String((e as { message: unknown }).message)
        : String(e);
      setError(msg);
      setBusy(false);
    }
  };

  const remove = async (path: string) => {
    try {
      await invoke("remove_workspace", { path });
      refresh();
    } catch (e: unknown) {
      setError(String(e));
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, overflowY: "auto", height: "100%" }}>
      {/* 工作区段 */}
      <Card style={{ padding: 18 }}>
        <div style={{ display: "flex", alignItems: "center", marginBottom: 8 }}>
          <h3 style={{ margin: 0, fontSize: 16 }}>📁 工作区</h3>
          <div style={{ flex: 1 }} />
          <Button size="sm" variant="ghost" onClick={refresh}>
            刷新
          </Button>
          <div style={{ width: 8 }} />
          <Button size="sm" variant="primary" onClick={openExisting} disabled={busy}>
            打开其他工作区
          </Button>
        </div>
        <p style={{ margin: "0 0 14px", fontSize: 13, color: "var(--ix-text-muted)" }}>
          最近打开的工作区列表。切换会触发整页 reload（重置前端所有 state，PTY/Channel 等）。
        </p>

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

        {workspaces === null ? (
          <Spinner />
        ) : workspaces.length === 0 ? (
          <EmptyState icon="📂" title="无已注册工作区" hint="点「打开其他工作区」添加" />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {workspaces.map((w) => (
              <div
                key={w.path}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "10px 12px",
                  background: w.is_current ? "color-mix(in srgb, var(--ix-primary) 8%, transparent)" : "transparent",
                  border: `1px solid ${w.is_current ? "var(--ix-primary)" : "var(--ix-border)"}`,
                  borderRadius: "var(--ix-radius-sm)",
                }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span
                      className="ix-mono"
                      style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: w.is_current ? "var(--ix-primary)" : "var(--ix-text)",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                      title={w.path}
                    >
                      {w.path}
                    </span>
                    {w.is_current && <Badge tone="primary">当前</Badge>}
                    {w.version && <Badge tone="neutral">v{w.version}</Badge>}
                    {!w.exists && <Badge tone="danger">已删除</Badge>}
                  </div>
                </div>
                {!w.is_current && (
                  <>
                    {w.exists && (
                      <Button size="sm" variant="default" onClick={() => switchTo(w.path)} disabled={busy}>
                        打开
                      </Button>
                    )}
                    <Button size="sm" variant="ghost" onClick={() => remove(w.path)} disabled={busy}>
                      移除
                    </Button>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* 主题皮肤段 */}
      <Card style={{ padding: 18 }}>
        <h3 style={{ margin: "0 0 4px", fontSize: 16 }}>🎨 主题皮肤</h3>
        <p style={{ margin: "0 0 16px", fontSize: 13, color: "var(--ix-text-muted)" }}>
          来自 indexed <code className="ix-mono">_shared/design-languages/</code> 的设计语言库。选中后立即应用到整个界面。
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
          {designLanguageList.map((dl) => {
            const active = current === dl.id;
            return (
              <div
                key={dl.id}
                onClick={() => setTheme(dl.id)}
                style={{
                  cursor: "pointer",
                  border: active ? "2px solid var(--ix-primary)" : "1px solid var(--ix-border)",
                  borderRadius: "var(--ix-radius)",
                  overflow: "hidden",
                  transition: "all 0.2s var(--ix-easing)",
                }}
              >
                <div style={{ display: "flex", height: 48 }}>
                  <div style={{ flex: 2, background: dl.tokens.bg }} />
                  <div style={{ flex: 1, background: dl.tokens.primary }} />
                  <div style={{ flex: 1, background: dl.tokens.accent }} />
                  <div style={{ flex: 1, background: dl.tokens.surface }} />
                </div>
                <div style={{ padding: "8px 12px", background: "var(--ix-surface)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: active ? "var(--ix-primary)" : "var(--ix-text)" }}>
                      {dl.id}
                    </span>
                    {active && <Badge tone="primary">当前</Badge>}
                  </div>
                  <div style={{ fontSize: 11, color: "var(--ix-text-muted)" }}>{dl.name}</div>
                  <div style={{ display: "flex", gap: 4, marginTop: 4, flexWrap: "wrap" }}>
                    {dl.tags.slice(0, 3).map((t) => (
                      <span key={t} style={{ fontSize: 10, color: "var(--ix-text-muted)", background: "var(--ix-surface-alt)", padding: "1px 6px", borderRadius: "var(--ix-radius-pill)" }}>
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* 零侵入铁律段 */}
      <Card style={{ padding: 18 }}>
        <h3 style={{ margin: "0 0 4px", fontSize: 16 }}>⚖️ 零侵入铁律</h3>
        <p style={{ margin: "0 0 12px", fontSize: 13, color: "var(--ix-text-muted)" }}>
          GUI 对工作区的字节级改动 = claude code 做同样的事。两种方式并存互通。
        </p>
        <ol style={{ margin: 0, paddingLeft: 20, fontSize: 13, color: "var(--ix-text)", lineHeight: 1.8 }}>
          <li>GUI 不发明 claude code 不认识的文件格式或目录结构</li>
          <li>GUI 不直接创建资产 —— 创建走「可见终端里的 claude」（单一写入源）</li>
          <li>GUI 只做两件事：只读展示（文件系统）+ 调用既有 CLI（subprocess）</li>
          <li>ix-gui/ 自身的代码除外（是 GUI 实现，不被当业务桶）</li>
        </ol>
        <div style={{ marginTop: 12, padding: 12, background: "var(--ix-surface-alt)", borderRadius: "var(--ix-radius-sm)", fontSize: 12, color: "var(--ix-text-muted)" }}>
          详见 <code className="ix-mono">ix-gui/OVERVIEW.md</code> §零侵入铁律 + 三边界
        </div>
      </Card>

      {/* 阶段信息 */}
      <Card style={{ padding: 18 }}>
        <h3 style={{ margin: "0 0 4px", fontSize: 16 }}>📦 当前阶段</h3>
        <p style={{ margin: "0 0 8px", fontSize: 13, color: "var(--ix-text-muted)" }}>
          阶段 2 ✅：Tauri+Rust（PtyBridge + CliRunner + WorkspaceIo）+ macOS 打包
        </p>
        <p style={{ margin: 0, fontSize: 13, color: "var(--ix-text-muted)" }}>
          阶段 3 ✅：工作区 wizard + 多工作区切换 + 基线升级引导
        </p>
      </Card>
    </div>
  );
}
