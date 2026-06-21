/**
 * Agents 视图 —— indexed §5.4 两阶段开发规范的表单化实现。
 *
 * 阶段 A（展示需求）：读 manifest.params 自动渲染表单，标注必填/默认值/提示文案
 * 阶段 B（执行）：用户填齐 → CliRunner.runAgent → 流式显示 step 进度
 *
 * 这里把 claude code 在对话里做的两阶段，搬成 GUI 表单。完全离线、确定、可复现。
 */
import { useEffect, useRef, useState } from "react";
import { backend } from "@/api/backend";
import type { AgentInfo, Manifest, CliEvent, ManifestParam } from "@/types/indexed";
import { Badge, Button, Card, EmptyState, Field, Spinner, inputStyle } from "@/components/ui";

function paramDefault(p: ManifestParam): { value: string; source: string } {
  if ("default" in p && p.default !== undefined) return { value: String(p.default), source: "默认" };
  if (p.default_from) return { value: "", source: `从 ${p.default_from}` };
  return { value: "", source: p.required ? "需用户提供" : "可选" };
}

function AgentRunForm({ agent, manifest }: { agent: AgentInfo; manifest: Manifest }) {
  const [values, setValues] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    for (const p of manifest.params) {
      const d = paramDefault(p);
      init[p.name] = d.value;
    }
    return init;
  });
  const [running, setRunning] = useState(false);
  const [events, setEvents] = useState<CliEvent[]>([]);
  const [stepStates, setStepStates] = useState<Record<string, "running" | "done" | "failed">>({});
  const [finalStatus, setFinalStatus] = useState<string | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  const missing = manifest.params.filter((p) => p.required && !values[p.name]);

  const run = async () => {
    if (missing.length > 0 || running) return;
    setRunning(true);
    setEvents([]);
    setStepStates({});
    setFinalStatus(null);
    const params: Record<string, unknown> = {};
    for (const p of manifest.params) {
      if (values[p.name] !== "") {
        params[p.name] = /^\d+$/.test(values[p.name]) ? Number(values[p.name]) : values[p.name];
      }
    }
    try {
      for await (const ev of backend.cli.runAgent({ agent: agent.name, params, trigger: "manual" })) {
        setEvents((prev) => [...prev, ev]);
        if (ev.kind === "step") setStepStates((s) => ({ ...s, [ev.step_id]: ev.status }));
        if (ev.kind === "status") setFinalStatus(ev.status);
        if (ev.kind === "error") setFinalStatus(`错误: ${ev.message}`);
        requestAnimationFrame(() => {
          if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
        });
      }
    } catch (e) {
      setFinalStatus(`异常: ${e}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, minWidth: 0 }}>
      {/* 阶段 A：需求表单 */}
      <Card style={{ padding: 18 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <h3 style={{ margin: 0, fontSize: 16 }}>{agent.name}</h3>
          <Badge tone="primary">{agent.domain}</Badge>
          {agent.has_thinking && <Badge tone="neutral">含 thinking</Badge>}
        </div>
        <p style={{ margin: "4px 0 16px", color: "var(--ix-text-muted)", fontSize: 13 }}>
          {agent.one_liner} · {agent.stepsSummary}
        </p>

        <div style={{ fontSize: 12, color: "var(--ix-text-muted)", marginBottom: 10, fontWeight: 600 }}>
          执行参数（阶段 A：确认输入后执行）
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          {manifest.params.map((p) => {
            const d = paramDefault(p);
            return (
              <Field
                key={p.name}
                label={p.name}
                required={p.required}
                hint={`${p.prompt ?? ""}${d.source ? `（${d.source}）` : ""}`}
              >
                <input
                  style={inputStyle}
                  value={values[p.name]}
                  placeholder={d.source === "需用户提供" ? "必填" : d.value || ""}
                  onChange={(e) => setValues((v) => ({ ...v, [p.name]: e.target.value }))}
                  disabled={running}
                />
              </Field>
            );
          })}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 16 }}>
          <Button variant="primary" onClick={run} disabled={missing.length > 0 || running}>
            {running ? <Spinner size={14} /> : "▶"} 执行
          </Button>
          {missing.length > 0 && (
            <span style={{ fontSize: 12, color: "var(--ix-danger)" }}>
              缺少必填项：{missing.map((m) => m.name).join(", ")}
            </span>
          )}
          {!running && finalStatus && (
            <span style={{ fontSize: 13, color: finalStatus === "completed" ? "var(--ix-success)" : "var(--ix-danger)" }}>
              {finalStatus === "completed" ? "✓ 完成" : finalStatus}
            </span>
          )}
        </div>
      </Card>

      {/* step 进度 */}
      <Card style={{ padding: 18 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--ix-text-muted)", marginBottom: 12 }}>
          步骤流水线
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {manifest.steps.map((s, i) => {
            const st = stepStates[s.id];
            return (
              <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 13 }}>
                <span
                  style={{
                    width: 22,
                    height: 22,
                    borderRadius: "var(--ix-radius-pill)",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 11,
                    background: st === "done" ? "var(--ix-success)" : st === "failed" ? "var(--ix-danger)" : "var(--ix-surface-alt)",
                    color: st === "done" || st === "failed" ? "#fff" : "var(--ix-text-muted)",
                  }}
                >
                  {st === "done" ? "✓" : st === "failed" ? "✕" : i + 1}
                </span>
                <span style={{ fontWeight: 500, minWidth: 160 }}>{s.id}</span>
                <span style={{ color: "var(--ix-text-muted)" }}>{s.description ?? s.type}</span>
                <Badge tone="neutral">{s.type === "thinking" ? "thinking" : "tool"}</Badge>
                {st === "running" && <Spinner size={12} />}
              </div>
            );
          })}
        </div>
      </Card>

      {/* 流式日志 */}
      {events.length > 0 && (
        <Card style={{ padding: 0, overflow: "hidden" }}>
          <div style={{ padding: "10px 14px", borderBottom: "1px solid var(--ix-border)", fontSize: 12, fontWeight: 600, color: "var(--ix-text-muted)" }}>
            执行日志（run-cli stdout）
          </div>
          <div
            ref={logRef}
            className="ix-mono"
            style={{
              padding: 14,
              maxHeight: 280,
              overflowY: "auto",
              background: "var(--ix-surface-alt)",
              color: "var(--ix-text)",
              lineHeight: 1.55,
            }}
          >
            {events.map((ev, i) => {
              if (ev.kind === "stdout" || ev.kind === "stderr")
                return (
                  <div key={i} style={{ color: ev.kind === "stderr" ? "var(--ix-danger)" : "inherit", whiteSpace: "pre-wrap" }}>
                    {ev.line}
                  </div>
                );
              if (ev.kind === "finished")
                return (
                  <div key={i} style={{ color: "var(--ix-success)", marginTop: 6 }}>
                    ── 完成 · run_dir: {ev.run_dir} · exit {ev.exit_code} ──
                  </div>
                );
              if (ev.kind === "started")
                return (
                  <div key={i} style={{ color: "var(--ix-primary)" }}>
                    ── 开始 · run_id: {ev.run_id} ──
                  </div>
                );
              return null;
            })}
          </div>
        </Card>
      )}
    </div>
  );
}

export function AgentsView() {
  const [agents, setAgents] = useState<AgentInfo[] | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [loadingManifest, setLoadingManifest] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    backend.workspace.listAgents().then(setAgents).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!selected) {
      setManifest(null);
      return;
    }
    setLoadingManifest(true);
    backend.workspace
      .readManifest(selected)
      .then(setManifest)
      .catch((e) => setError(String(e)))
      .finally(() => setLoadingManifest(false));
  }, [selected]);

  if (error) return <div style={{ padding: 24, color: "var(--ix-danger)" }}>加载失败: {error}</div>;
  if (!agents) return <div style={{ padding: 24 }}><Spinner /></div>;
  if (agents.length === 0)
    return (
      <EmptyState
        icon="🤖"
        title="还没有自定义 agent"
        hint="在「会话」页对 Claude 说「帮我建个 xxx agent」即可创建（创建走 Claude，GUI 不直接写）"
      />
    );

  const sel = agents.find((a) => a.name === selected);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 16, height: "100%", minHeight: 0 }}>
      {/* agent 列表 */}
      <Card style={{ padding: 8, overflowY: "auto" }}>
        <div style={{ padding: "8px 10px", fontSize: 12, fontWeight: 600, color: "var(--ix-text-muted)" }}>
          自定义 Agents
        </div>
        {agents.map((a) => (
          <div
            key={a.name}
            onClick={() => setSelected(a.name)}
            style={{
              padding: "10px 12px",
              borderRadius: "var(--ix-radius-sm)",
              cursor: "pointer",
              background: selected === a.name ? "color-mix(in srgb, var(--ix-primary) 14%, transparent)" : "transparent",
              border: "1px solid transparent",
              marginBottom: 4,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: selected === a.name ? "var(--ix-primary)" : "var(--ix-text)" }}>
                {a.name}
              </span>
              {a.recentRunCount > 0 && (
                <span style={{ fontSize: 11, color: "var(--ix-text-muted)" }}>· {a.recentRunCount} runs</span>
              )}
            </div>
            <div style={{ fontSize: 12, color: "var(--ix-text-muted)" }}>{a.one_liner}</div>
          </div>
        ))}
      </Card>

      {/* 选中 agent 的表单 */}
      <div style={{ overflowY: "auto", paddingRight: 4 }}>
        {!selected && <EmptyState icon="👈" title="选择左侧的 agent" hint="选中后展示执行表单与步骤流水线" />}
        {selected && loadingManifest && <Spinner />}
        {selected && sel && manifest && <AgentRunForm agent={sel} manifest={manifest} key={selected} />}
      </div>
    </div>
  );
}
