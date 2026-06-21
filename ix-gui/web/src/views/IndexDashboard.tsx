/**
 * 索引仪表盘 —— 调 ix-workspace-index-cli audit/sync，展示一致性结果。
 * 零侵入：audit 是只读诊断；sync 写薄索引 IX_USER_* 标记区（indexed 原生能力，非 GUI 发明）。
 */
import { useState } from "react";
import { backend } from "@/api/backend";
import type { AuditReport, AuditIssue } from "@/types/indexed";
import type { SyncResult, InitStatus } from "@/api/contract";
import { Badge, Button, Card, Spinner } from "@/components/ui";

function IssueRow({ issue }: { issue: AuditIssue }) {
  const tone = issue.level === "error" ? "danger" : "warning";
  return (
    <div
      style={{
        display: "flex",
        gap: 10,
        padding: "10px 12px",
        borderLeft: `3px solid ${issue.level === "error" ? "var(--ix-danger)" : "var(--ix-warning)"}`,
        background: "var(--ix-surface)",
        borderRadius: "0 var(--ix-radius-sm) var(--ix-radius-sm) 0",
        marginBottom: 6,
        fontSize: 14,
      }}
    >
      <Badge tone={tone}>{issue.level.toUpperCase()}</Badge>
      <div>
        <div style={{ fontWeight: 600 }}>
          {issue.code}
          {issue.target && <span className="ix-mono" style={{ color: "var(--ix-text-muted)", fontWeight: 400, marginLeft: 8 }}>{issue.target}</span>}
        </div>
        <div style={{ color: "var(--ix-text-muted)", marginTop: 2 }}>{issue.message}</div>
      </div>
    </div>
  );
}

export function IndexDashboard() {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [init, setInit] = useState<InitStatus | null>(null);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const refresh = async () => {
    setLoadingAudit(true);
    setErr(null);
    try {
      const [r, i] = await Promise.all([backend.cli.audit(), backend.cli.initStatus()]);
      setReport(r);
      setInit(i);
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoadingAudit(false);
    }
  };

  const doSync = async () => {
    setSyncing(true);
    try {
      setSyncResult(await backend.cli.sync());
      await refresh();
    } catch (e) {
      setErr(String(e));
    } finally {
      setSyncing(false);
    }
  };

  if (!report && !loadingAudit) {
    return (
      <div style={{ padding: 24 }}>
        <Button variant="primary" onClick={refresh}>
          ⟳ 运行索引审计
        </Button>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, overflowY: "auto", height: "100%" }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
        <Button variant="primary" onClick={refresh} disabled={loadingAudit}>
          {loadingAudit ? <Spinner size={14} /> : "⟳"} 重新审计
        </Button>
        <Button onClick={doSync} disabled={syncing || !report}>
          {syncing ? <Spinner size={14} /> : "↻"} 同步索引（sync）
        </Button>
        {report && (
          <Badge tone={report.ok ? "success" : "danger"}>{report.ok ? "索引一致" : "存在 error"}</Badge>
        )}
        {syncResult && (
          <span style={{ fontSize: 13, color: "var(--ix-success)" }}>
            ✓ 已同步 {syncResult.syncedFiles.length} 个文件的 IX_USER_* 标记区
          </span>
        )}
        {err && <span style={{ fontSize: 13, color: "var(--ix-danger)" }}>{err}</span>}
      </div>

      {/* 工作区状态卡片 */}
      {init && (
        <Card style={{ padding: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ix-text-muted)", marginBottom: 10 }}>
            工作区状态（ix-init-cli status）
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, fontSize: 14 }}>
            <div>
              <div style={{ color: "var(--ix-text-muted)", fontSize: 12 }}>版本</div>
              <div style={{ fontWeight: 600 }} className="ix-mono">{init.version}</div>
            </div>
            <div>
              <div style={{ color: "var(--ix-text-muted)", fontSize: 12 }}>Git 模式</div>
              <div style={{ fontWeight: 600 }}>
                <Badge tone={init.gitMode === "uninitialized" ? "warning" : "primary"}>{init.gitMode}</Badge>
              </div>
            </div>
            <div>
              <div style={{ color: "var(--ix-text-muted)", fontSize: 12 }}>昵称 / 称呼</div>
              <div style={{ fontWeight: 600 }}>{init.nick} / {init.addr}</div>
            </div>
            <div>
              <div style={{ color: "var(--ix-text-muted)", fontSize: 12 }}>Git</div>
              <div style={{ fontWeight: 600 }}>{init.gitInitialized ? "已初始化" : "未初始化"}</div>
            </div>
          </div>
        </Card>
      )}

      {report && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            {/* CLI 列表 */}
            <Card style={{ padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ix-text-muted)", marginBottom: 10 }}>
                发现的 CLI（{report.clis.length}）
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ color: "var(--ix-text-muted)", textAlign: "left" }}>
                    <th style={{ padding: "4px 8px", borderBottom: "1px solid var(--ix-border)" }}>模块</th>
                    <th style={{ padding: "4px 8px", borderBottom: "1px solid var(--ix-border)" }}>子命令</th>
                    <th style={{ padding: "4px 8px", borderBottom: "1px solid var(--ix-border)" }}>SPEC</th>
                  </tr>
                </thead>
                <tbody>
                  {report.clis.map((c) => (
                    <tr key={c.name}>
                      <td className="ix-mono" style={{ padding: "6px 8px", borderBottom: "1px solid var(--ix-border)" }}>{c.name}</td>
                      <td style={{ padding: "6px 8px", borderBottom: "1px solid var(--ix-border)", color: "var(--ix-text-muted)" }}>
                        {c.subcommands.join(", ") || "—"}
                      </td>
                      <td style={{ padding: "6px 8px", borderBottom: "1px solid var(--ix-border)" }}>
                        {c.has_spec_yaml ? <Badge tone="success">有</Badge> : <Badge tone="danger">缺</Badge>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>

            {/* Agent 列表 */}
            <Card style={{ padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ix-text-muted)", marginBottom: 10 }}>
                发现的 Agent（{report.agents.length}）
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ color: "var(--ix-text-muted)", textAlign: "left" }}>
                    <th style={{ padding: "4px 8px", borderBottom: "1px solid var(--ix-border)" }}>应用</th>
                    <th style={{ padding: "4px 8px", borderBottom: "1px solid var(--ix-border)" }}>thinking</th>
                    <th style={{ padding: "4px 8px", borderBottom: "1px solid var(--ix-border)" }}>步骤</th>
                  </tr>
                </thead>
                <tbody>
                  {report.agents.map((a) => (
                    <tr key={a.name}>
                      <td className="ix-mono" style={{ padding: "6px 8px", borderBottom: "1px solid var(--ix-border)" }}>{a.name}</td>
                      <td style={{ padding: "6px 8px", borderBottom: "1px solid var(--ix-border)" }}>
                        {a.has_thinking ? <Badge tone="primary">是</Badge> : <Badge tone="neutral">否</Badge>}
                      </td>
                      <td style={{ padding: "6px 8px", borderBottom: "1px solid var(--ix-border)", color: "var(--ix-text-muted)" }}>
                        {a.steps_summary || "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          </div>

          {/* 问题列表 */}
          <Card style={{ padding: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ix-text-muted)", marginBottom: 10 }}>
              审计问题（{report.issues.length}）
            </div>
            {report.issues.length === 0 ? (
              <div style={{ color: "var(--ix-success)", fontSize: 14, padding: 8 }}>✓ 未发现索引漂移</div>
            ) : (
              report.issues.map((i, idx) => <IssueRow key={idx} issue={i} />)
            )}
          </Card>
        </>
      )}
    </div>
  );
}
