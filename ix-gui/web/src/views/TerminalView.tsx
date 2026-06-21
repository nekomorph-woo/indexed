/**
 * 会话页 —— 可见终端。
 *
 * 【web 阶段】：前端自洽的终端占位。本地模拟回显，让交互与布局可验证。
 *   明确标注「web 占位」，绝不假装是真 claude（诚实标注边界）。
 *
 * 【Tauri 阶段】：换 xterm.js + backend.pty（portable-pty 跑交互式 claude）。
 *   用户直接打字，claude 按 CLAUDE.md 创建资产/沟通。这是「创建」的唯一写入源（零侵入铁律）。
 *
 * 组件结构已按 xterm.js 接入设计：TerminalViewport 接收 data 回调、
 * input 走 backend.pty.input，Tauri 阶段只换实现不换结构。
 */
import { useEffect, useRef, useState } from "react";
import { backend } from "@/api/backend";
import { Badge, Button } from "@/components/ui";

interface Line {
  text: string;
  kind: "in" | "out" | "system" | "tool";
}

/** web 阶段的本地回显模拟器——演示交互形态，Tauri 阶段删除 */
function localEcho(input: string): Line[] {
  const out: Line[] = [{ text: `> ${input}`, kind: "in" }];
  if (/^(建|创建|新建|help|帮我)/.test(input.trim())) {
    out.push({ text: "✻ (web 占位回显) 收到。Tauri 阶段这里会是真实 claude 的响应。", kind: "system" });
    out.push({ text: "  在真实环境，claude 会读 CLAUDE.md + rules，按规范创建文件。", kind: "out" });
    out.push({ text: "  ⏺ Read CLAUDE.md", kind: "tool" });
    out.push({ text: "  ⏺ Read .claude/rules/ix-agents.md", kind: "tool" });
    out.push({ text: "  ⏺ Edit ix-agents/ix-new-agent/manifest.yaml", kind: "tool" });
  } else if (input.trim() === "") {
    // no-op
  } else {
    out.push({ text: `(web 占位回显) 你说了：「${input}」`, kind: "system" });
    out.push({ text: "  真实环境：claude 会理解意图并调用工具/落盘。", kind: "out" });
  }
  return out;
}

export function TerminalView() {
  const [lines, setLines] = useState<Line[]>([
    { text: "indexed · 可见终端（web 占位）", kind: "system" },
    { text: "Tauri 阶段：xterm.js + portable-pty 跑交互式 claude，cwd = indexed 根", kind: "system" },
    { text: "这里是「创建资产」与「日常沟通」的主场（单一写入源，零侵入铁律）", kind: "system" },
    { text: "", kind: "system" },
  ]);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [histIdx, setHistIdx] = useState(-1);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [lines]);

  const submit = async () => {
    const text = input;
    if (!text.trim()) return;
    setHistory((h) => [...h, text]);
    setHistIdx(-1);
    setLines((prev) => [...prev, ...localEcho(text)]);
    setInput("");
    // web 阶段：本地回显；Tauri 阶段会调 backend.pty.input(sessionId, text + "\n")
    await backend.pty.input("web-placeholder", text);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      submit();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (history.length === 0) return;
      const idx = histIdx === -1 ? history.length - 1 : Math.max(0, histIdx - 1);
      setHistIdx(idx);
      setInput(history[idx]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (histIdx === -1) return;
      const idx = histIdx + 1;
      if (idx >= history.length) {
        setHistIdx(-1);
        setInput("");
      } else {
        setHistIdx(idx);
        setInput(history[idx]);
      }
    }
  };

  const colorFor = (k: Line["kind"]) =>
    k === "in" ? "var(--ix-text)" : k === "system" ? "var(--ix-text-muted)" : k === "tool" ? "var(--ix-accent)" : "var(--ix-text)";

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "8px 0", marginBottom: 4 }}>
        <Badge tone="warning">web 占位</Badge>
        <span style={{ fontSize: 13, color: "var(--ix-text-muted)" }}>
          可见终端 · 交互可验证 · Tauri 阶段接真实 claude（PTY）
        </span>
        <div style={{ flex: 1 }} />
        <Button size="sm" variant="ghost" onClick={() => setLines([])} title="清屏">
          清屏
        </Button>
        <Button size="sm" variant="ghost" onClick={() => inputRef.current?.focus()}>
          聚焦输入
        </Button>
      </div>

      <div
        ref={scrollRef}
        className="ix-mono"
        onClick={() => inputRef.current?.focus()}
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: "auto",
          background: "var(--ix-surface-alt)",
          borderRadius: "var(--ix-radius-sm)",
          padding: 14,
          lineHeight: 1.6,
          cursor: "text",
        }}
      >
        {lines.map((l, i) => (
          <div key={i} style={{ color: colorFor(l.kind), whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
            {l.text || "\u00a0"}
          </div>
        ))}
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ color: "var(--ix-primary)" }}>❯</span>
          <input
            ref={inputRef}
            autoFocus
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            className="ix-mono"
            placeholder="对 Claude 说话（例：帮我建个周报 agent）..."
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              color: "var(--ix-text)",
              fontSize: 14,
              fontFamily: "var(--ix-font-mono)",
            }}
          />
        </div>
      </div>
    </div>
  );
}
