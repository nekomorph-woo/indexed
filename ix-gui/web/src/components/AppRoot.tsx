/**
 * AppRoot — 启动入口的 workspace 守卫。
 *
 * 流程：
 *   1. 调 has_current_workspace 检测是否有当前工作区
 *   2. 有 → 渲染 AppShell（主界面）
 *   3. 无 → 渲染 WorkspaceWizard
 *   4. Wizard 完成（onDone）→ 触发 reloadKey 重渲染 → AppShell 出现
 *
 * 版本比对（M7.5）：AppShell 启动后异步比对 workspace VERSION vs baseline
 * VERSION，不同则弹 UpgradeDialog。
 */
import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { AppShell } from "./AppShell";
import { WorkspaceWizard } from "@/views/WorkspaceWizard";
import { UpgradeDialog } from "./UpgradeDialog";
import { Spinner } from "./ui";

type Phase = "loading" | "wizard" | "main";

export function AppRoot() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [upgrade, setUpgrade] = useState<{ from: string; to: string } | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    invoke<boolean>("has_current_workspace")
      .then((has) => setPhase(has ? "main" : "wizard"))
      .catch(() => setPhase("wizard"));
  }, [reloadKey]);

  // main 阶段才比对版本（wizard 阶段无 workspace_root）
  useEffect(() => {
    if (phase !== "main") return;
    Promise.all([
      invoke<string | null>("get_workspace_version"),
      invoke<string | null>("get_baseline_version"),
    ])
      .then(([ws, bl]) => {
        if (ws && bl && ws !== bl) {
          setUpgrade({ from: ws, to: bl });
        }
      })
      .catch(() => {});
  }, [phase, reloadKey]);

  if (phase === "loading") {
    return (
      <div
        style={{
          height: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--ix-bg)",
        }}
      >
        <Spinner size={28} />
      </div>
    );
  }

  if (phase === "wizard") {
    return (
      <WorkspaceWizard
        onDone={() => {
          setReloadKey((k) => k + 1);
        }}
      />
    );
  }

  return (
    <>
      <AppShell key={reloadKey} />
      {upgrade && (
        <UpgradeDialog
          from={upgrade.from}
          to={upgrade.to}
          onClose={() => setUpgrade(null)}
          onUpgraded={() => {
            setUpgrade(null);
            setReloadKey((k) => k + 1);
          }}
        />
      )}
    </>
  );
}
