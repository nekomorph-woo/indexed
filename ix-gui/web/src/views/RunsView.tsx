/**
 * Runs 浏览视图 —— 读 ix-agents/<agent>/runs/<id>/ 的 run.yaml + 产出文件。
 * 纯只读（零侵入铁律）。展示 run 的状态、参数、output/thinking/raw 文件。
 */
import { useEffect, useState } from "react";
import { backend } from "@/api/backend";
import type { AgentInfo, RunSummary, RunDetail } from "@/types/indexed";
import { Badge, Card, EmptyState, Spinner, StatusDot, Tabs } from "@/components/ui";

function fmtDate(iso: string) {
  try {
    return new Date(iso).toLocaleString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

function FileViewer({ file }: { file: NonNullable<RunDetail["outputFiles"]>[number] }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 12px",
          background: "var(--ix-surface-alt)",
          borderRadius: "var(--ix-radius-sm) var(--ix-radius-sm) 0 0",
          fontSize: 12,
          fontWeight: 600,
        }}
      >
        <span>{file.ext === ".md" ? "📝" : file.ext === ".json" ? "🔧" : "📃"}</span>
        <span className="ix-mono">{file.relPath}</span>
        <span style={{ color: "var(--ix-text-muted)", fontWeight: 400 }}>{(file.size / 1024).toFixed(1)} KB</span>
      </div>
      <pre
        className="ix-mono"
        style={{
          margin: 0,
          padding: 14,
          background: "var(--ix-surface)",
          borderRadius: "0 0 var(--ix-radius-sm) var(--ix-radius-sm)",
          maxHeight: 360,
          overflow: "auto",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          color: "var(--ix-text)",
          lineHeight: 1.55,
        }}
      >
        {file.content ?? "(二进制或过大，无法预览)"}
      </pre>
    </div>
  );
}

function RunDetailPanel({ agentName, runId }: { agentName: string; runId: string }) {
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState("output");

  useEffect(() => {
    setDetail(null);
    setErr(null);
    backend.workspace
      .readRun(agentName, runId)
      .then(setDetail)
      .catch((e) => setErr(String(e)));
  }, [agentName, runId]);

  if (err) return <div style={{ padding: 16, color: "var(--ix-danger)" }}>加载失败: {err}</div>;
  if (!detail)
    return (
      <div style={{ padding: 16 }}>
        <Spinner />
      </div>
    );

  const tabs = [
    { id: "output", label: `产出 (${detail.outputFiles.length})` },
    { id: "thinking", label: `Thinking (${detail.thinkingFiles.length})` },
    { id: "raw", label: `Raw (${detail.rawFiles.length})` },
    { id: "meta", label: "run.yaml" },
  ];

  const files = tab === "output" ? detail.outputFiles : tab === "thinking" ? detail.thinkingFiles : tab === "raw" ? detail.rawFiles : [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12, height: "100%", minHeight: 0 }}>
      <Card style={{ padding: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
          <StatusDot status={detail.status} />
          <span className="ix-mono" style={{ fontWeight: 600 }}>{detail.run_id}</span>
          <Badge tone={detail.status === "completed" ? "success" : detail.status === "failed" ? "danger" : "warning"}>
            {detail.status}
          </Badge>
          <Badge tone="neutral">{detail.trigger}</Badge>
          <span style={{ color: "var(--ix-text-muted)", fontSize: 12 }}>{fmtDate(detail.started_at)}</span>
        </div>
        {detail.next_step && (
          <div style={{ fontSize: 12, color: "var(--ix-danger)" }}>中断于 step: {detail.next_step}（可 resume）</div>
        )}
      </Card>

      <Tabs tabs={tabs} active={tab} onChange={setTab} />

      <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
        {tab === "meta" ? (
          <Card style={{ padding: 14 }}>
            <pre className="ix-mono" style={{ margin: 0, whiteSpace: "pre-wrap", color: "var(--ix-text)" }}>
              {JSON.stringify(
                {
                  run_id: detail.run_id,
                  agent_id: detail.agent_id,
                  trigger: detail.trigger,
                  status: detail.status,
                  next_step: detail.next_step,
                  started_at: detail.started_at,
                  params: detail.params,
                  steps_completed: detail.steps_completed,
                },
                null,
                2,
              )}
            </pre>
          </Card>
        ) : files.length === 0 ? (
          <EmptyState icon="📭" title="无文件" hint="该 run 在此分类下没有产出文件" />
        ) : (
          files.map((f) => <FileViewer key={f.relPath} file={f} />)
        )}
      </div>
    </div>
  );
}

export function RunsView() {
  const [agents, setAgents] = useState<AgentInfo[] | null>(null);
  const [agent, setAgent] = useState<string | null>(null);
  const [runs, setRuns] = useState<RunSummary[] | null>(null);
  const [runId, setRunId] = useState<string | null>(null);

  useEffect(() => {
    backend.workspace.listAgents().then(setAgents);
  }, []);

  useEffect(() => {
    setRuns(null);
    setRunId(null);
    if (agent) backend.workspace.listRuns(agent).then(setRuns);
  }, [agent]);

  if (!agents) return <div style={{ padding: 24 }}><Spinner /></div>;
  if (agents.length === 0)
    return <EmptyState icon="📦" title="没有 agent，自然也没有 runs" hint="先创建一个 agent 并执行" />;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "200px 240px 1fr", gap: 12, height: "100%", minHeight: 0 }}>
      <Card style={{ padding: 8, overflowY: "auto" }}>
        <div style={{ padding: "8px 10px", fontSize: 12, fontWeight: 600, color: "var(--ix-text-muted)" }}>Agent</div>
        {agents.map((a) => (
          <div
            key={a.name}
            onClick={() => setAgent(a.name)}
            style={{
              padding: "8px 12px",
              borderRadius: "var(--ix-radius-sm)",
              cursor: "pointer",
              fontSize: 12,
              fontWeight: 500,
              background: agent === a.name ? "color-mix(in srgb, var(--ix-primary) 14%, transparent)" : "transparent",
              color: agent === a.name ? "var(--ix-primary)" : "var(--ix-text)",
            }}
          >
            {a.name}
          </div>
        ))}
      </Card>

      <Card style={{ padding: 8, overflowY: "auto" }}>
        <div style={{ padding: "8px 10px", fontSize: 12, fontWeight: 600, color: "var(--ix-text-muted)" }}>Runs</div>
        {!agent && <div style={{ padding: 12, fontSize: 12, color: "var(--ix-text-muted)" }}>← 先选 agent</div>}
        {agent && !runs && <div style={{ padding: 12 }}><Spinner /></div>}
        {runs &&
          (runs.length === 0 ? (
            <div style={{ padding: 12, fontSize: 12, color: "var(--ix-text-muted)" }}>该 agent 无历史 run</div>
          ) : (
            runs.map((r) => (
              <div
                key={r.run_id}
                onClick={() => setRunId(r.run_id)}
                style={{
                  padding: "8px 12px",
                  borderRadius: "var(--ix-radius-sm)",
                  cursor: "pointer",
                  marginBottom: 4,
                  background: runId === r.run_id ? "color-mix(in srgb, var(--ix-primary) 14%, transparent)" : "transparent",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                  <StatusDot status={r.status} />
                  <span className="ix-mono" style={{ fontSize: 11, fontWeight: 600 }}>
                    {r.run_id}
                  </span>
                </div>
                <div style={{ fontSize: 11, color: "var(--ix-text-muted)" }}>
                  {r.steps_completed.length}/{r.steps_total} steps · {fmtDate(r.started_at).slice(5, 16)}
                </div>
              </div>
            ))
          ))}
      </Card>

      <div style={{ overflow: "hidden" }}>
        {!runId ? (
          <EmptyState icon="📦" title="选择一个 run" hint="查看它的产出、thinking 与原始数据" />
        ) : (
          <RunDetailPanel agentName={agent!} runId={runId} key={runId} />
        )}
      </div>
    </div>
  );
}
