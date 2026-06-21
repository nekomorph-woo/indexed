/**
 * 会话页 —— 真实可见终端（M4）。
 *
 * 用 xterm.js 渲染 + tauri-plugin-pty 跑交互式 claude。
 * 用户直接打字，cwd = indexed 根，claude 按 CLAUDE.md 创建资产/沟通。
 * 这是「创建资产」与「日常沟通」的主场（单一写入源，零侵入铁律）。
 *
 * 设计：useEffect 内完成 xterm/PTY/双向绑定/ResizeObserver 的生命周期管理。
 * 卸载时统一 dispose，避免 PTY 泄漏。
 */
import { useEffect, useRef, useState } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { invoke } from "@tauri-apps/api/core";
import "@xterm/xterm/css/xterm.css";
import { backend } from "@/api/backend";
import { Badge, Button } from "@/components/ui";

type TermStatus = "init" | "running" | "error" | "noclaude";

interface CleanupHandles {
  inputDisp?: { dispose: () => void };
  resizeDisp?: { dispose: () => void };
}

export function TerminalView() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<TermStatus>("init");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;
    let disposed = false;
    let sessionId: string | null = null;
    let unsubData: (() => void) | null = null;
    let term: Terminal | null = null;
    let fitAddon: FitAddon | null = null;
    let resizeObs: ResizeObserver | null = null;
    const handles: CleanupHandles = {};

    (async () => {
      // 创建 xterm.js Terminal
      term = new Terminal({
        fontFamily: "var(--ix-font-mono)",
        fontSize: 13,
        theme: {
          background: "#1e1e2e",
          foreground: "#cdd6f4",
          cursor: "#f5e0dc",
          selectionBackground: "#585b7066",
        },
        cursorBlink: true,
        scrollback: 5000,
        convertEol: true,
      });
      fitAddon = new FitAddon();
      term.loadAddon(fitAddon);
      term.open(containerRef.current!);
      try {
        fitAddon.fit();
      } catch {
        // 初次 fit 可能因容器不可见失败
      }

      term.writeln("\x1b[36mindexed · 可见终端\x1b[0m");
      term.writeln("\x1b[90mcwd = indexed 根；输入 claude 进入交互\x1b[0m");
      term.writeln("");

      // 拿 workspace_root 作为 cwd
      let cwd = "/";
      try {
        cwd = await invoke<string>("get_workspace_root");
      } catch {
        // fallback：根目录
      }

      // 启动 PTY
      try {
        const result = await backend.pty.spawn({
          cwd,
          command: "claude",
          cols: term.cols,
          rows: term.rows,
        });
        if (disposed) {
          backend.pty.kill(result.sessionId);
          return;
        }
        sessionId = result.sessionId;
        setStatus("running");

        // PTY → term
        unsubData = backend.pty.onData(sessionId, (data) => {
          if (!disposed) term?.write(data);
        });

        // term → PTY
        handles.inputDisp = term.onData((data) => {
          if (sessionId) backend.pty.input(sessionId, data);
        });
        handles.resizeDisp = term.onResize(({ cols, rows }) => {
          if (sessionId) backend.pty.resize(sessionId, cols, rows);
        });

        // 容器 resize → fit
        if (containerRef.current) {
          resizeObs = new ResizeObserver(() => {
            if (fitAddon && !disposed) {
              try {
                fitAddon.fit();
              } catch {
                // 忽略瞬时 fit 错误
              }
            }
          });
          resizeObs.observe(containerRef.current);
        }
      } catch (e) {
        if (disposed) return;
        const msg = e instanceof Error ? e.message : String(e);
        if (msg.includes("claude") || msg.includes("not found") || msg.includes("No such file")) {
          setStatus("noclaude");
          setErrorMsg(msg);
          term.writeln("");
          term.writeln(`\x1b[31m⚠ ${msg}\x1b[0m`);
          term.writeln("\x1b[90m请先装 Claude Code CLI：npm i -g @anthropic-ai/claude-code\x1b[0m");
        } else {
          setStatus("error");
          setErrorMsg(msg);
          term.writeln(`\x1b[31m✗ PTY 启动失败: ${msg}\x1b[0m`);
        }
      }
    })();

    return () => {
      disposed = true;
      handles.inputDisp?.dispose();
      handles.resizeDisp?.dispose();
      resizeObs?.disconnect();
      unsubData?.();
      if (sessionId) backend.pty.kill(sessionId);
      term?.dispose();
    };
  }, [reloadKey]);

  const reconnect = () => {
    setStatus("init");
    setErrorMsg("");
    setReloadKey((k) => k + 1);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>
      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          padding: "8px 0",
          marginBottom: 4,
        }}
      >
        {status === "running" && <Badge tone="success">真实 PTY</Badge>}
        {status === "init" && <Badge tone="warning">启动中</Badge>}
        {status === "noclaude" && <Badge tone="danger">claude 未装</Badge>}
        {status === "error" && <Badge tone="danger">错误</Badge>}
        <span style={{ fontSize: 13, color: "var(--ix-text-muted)" }}>
          可见终端 · xterm.js + portable-pty · cwd=indexed 根
        </span>
        <div style={{ flex: 1 }} />
        {status !== "running" && status !== "init" && (
          <Button size="sm" variant="ghost" onClick={reconnect} title="重连">
            重连
          </Button>
        )}
      </div>

      <div
        key={reloadKey}
        ref={containerRef}
        style={{
          flex: 1,
          minHeight: 0,
          background: "#1e1e2e",
          borderRadius: "var(--ix-radius-sm)",
          padding: 8,
          overflow: "hidden",
        }}
      />

      {status === "error" && (
        <div style={{ marginTop: 8, fontSize: 13, color: "var(--ix-danger)" }}>
          错误详情：{errorMsg}
        </div>
      )}
    </div>
  );
}
