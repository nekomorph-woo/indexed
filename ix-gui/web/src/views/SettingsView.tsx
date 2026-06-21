/**
 * 设置页 —— 主题切换（复用 design-languages）+ 零侵入铁律说明。
 * 主题数据来自 _shared/design-languages/<id>/meta.md 的 Token 摘要（见 theme/designLanguages.ts）。
 */
import { designLanguageList } from "@/theme/designLanguages";
import { useThemeStore } from "@/theme/themeStore";
import { Badge, Card } from "@/components/ui";

export function SettingsView() {
  const { current, setTheme } = useThemeStore();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, overflowY: "auto", height: "100%" }}>
      <Card style={{ padding: 18 }}>
        <h3 style={{ margin: "0 0 4px", fontSize: 16 }}>主题皮肤</h3>
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
                {/* token 色板预览 */}
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

      <Card style={{ padding: 18 }}>
        <h3 style={{ margin: "0 0 4px", fontSize: 16 }}>当前阶段</h3>
        <p style={{ margin: "0 0 8px", fontSize: 13, color: "var(--ix-text-muted)" }}>
          阶段 1（纯 Web）：UI + 交互 + mock 契约，bb-browser 验证
        </p>
        <p style={{ margin: 0, fontSize: 13, color: "var(--ix-text-muted)" }}>
          阶段 2（Tauri + Rust）：PtyBridge(portable-pty) + CliRunner(tokio) + WorkspaceIo + 打包
        </p>
      </Card>
    </div>
  );
}
