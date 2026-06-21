/**
 * Mock 数据 —— 形态严格遵循 indexed 规范。
 * 这些样本用于 web 阶段驱动 UI；Tauri 阶段会被真实文件系统读取取代。
 * 所有样本都是从 capability-spec.spec.md / manifest.template.yaml / run-yaml.example.yaml
 * 派生出的合规结构。
 */
import type {
  AgentInfo,
  AuditReport,
  CliInfo,
  Manifest,
  AgentSpec,
  CliSpec,
  RunSummary,
  RunDetail,
} from "@/types/indexed";
import type { SyncResult, InitStatus, TreeNode } from "@/api/contract";

// ── 真实的 indexed CLI（基线 4 个，来自 capabilities.md 标记区） ──

export const mockClis: CliInfo[] = [
  {
    name: "ix-agent-run-cli",
    domain: "组合 agent 执行器",
    one_liner: "按 manifest 执行 tool + thinking（claude -p）流水线",
    status: "implemented",
    subcommands: ["run", "schedule list", "schedule run"],
    has_spec_yaml: true,
  },
  {
    name: "ix-schedule-cli",
    domain: "跨平台定时",
    one_liner: "schtasks/launchd 注册 + 触发 ix-agent",
    status: "implemented",
    subcommands: ["register", "unregister", "list", "run"],
    has_spec_yaml: true,
  },
  {
    name: "ix-workspace-index-cli",
    domain: "索引审计",
    one_liner: "audit / list / sync（SPEC.yaml 与薄索引一致性）",
    status: "implemented",
    subcommands: ["audit", "list", "sync"],
    has_spec_yaml: true,
  },
  {
    name: "ix-init-cli",
    domain: "工作区初始化",
    one_liner: "init / update / status",
    status: "implemented",
    subcommands: ["init", "update", "status"],
    has_spec_yaml: true,
  },
];

// ── 用户自建 agent 样本（演示用；真实 ix-agents/ 当前为空） ──

export const mockAgents: AgentInfo[] = [
  {
    name: "ix-weekly-report-agent",
    domain: "周报生成",
    one_liner: "Metabase 拉数 → 语义分析 → 报告",
    status: "implemented",
    has_thinking: true,
    has_manifest: true,
    stepsSummary: "export_primary → analyze_semantic → write_report",
    requiredParams: ["primary_input"],
    recentRunCount: 3,
  },
  {
    name: "ix-rollout-audit-agent",
    domain: "上线单据审计",
    one_liner: "审批信号 → Wiki 文档 → 测试审计 → 报告",
    status: "implemented",
    has_thinking: true,
    has_manifest: true,
    stepsSummary: "fetch_messages → prepare_raw → render_report",
    requiredParams: ["report_title", "recent_client_versions"],
    recentRunCount: 1,
  },
];

const weeklyManifest: Manifest = {
  id: "ix-weekly-report-agent",
  research: "research/weekly-metrics",
  params: [
    {
      name: "primary_input",
      required: true,
      prompt: "请提供本次运行的主要输入（Metabase Question 链接或 ID）",
      default_from: "config/defaults.yaml#primary_input",
    },
    {
      name: "window_days",
      required: false,
      prompt: "分析窗口（天）",
      default: 7,
    },
  ],
  artifacts: ["ix-metabase-cli:question", "ix-agent-run-cli:audit"],
  steps: [
    {
      id: "export_primary",
      type: "tool",
      description: "导出主数据到 work/raw",
      tool: "shell",
      command:
        "python3 {artifacts_root}/ix-metabase-cli/main.py question --url \"{params.primary_input}\" -O {work_raw}",
      expects: ["work/raw/*.csv"],
    },
    {
      id: "analyze_semantic",
      type: "thinking",
      description: "语义分析（ix-agent-run-cli 调 claude -p）",
      inputs: ["work/raw/*.csv"],
      prompt:
        "你是业务分析助手。基于 inputs 中的数据，结合窗口 {params.window_days} 天：\n1. 归纳关键变化与异常\n2. 按条目列出结论与依据\n3. 给出可操作建议",
      output: "work/thinking/analyze_semantic.md",
    },
    {
      id: "write_report",
      type: "tool",
      description: "将 thinking 结论复制为最终报告",
      tool: "write",
      from: "work/thinking/analyze_semantic.md",
      to: "output/report.md",
    },
  ],
};

const rolloutManifest: Manifest = {
  id: "ix-rollout-audit-agent",
  params: [
    {
      name: "report_title",
      required: true,
      prompt: "报告标题",
    },
    {
      name: "recent_client_versions",
      required: true,
      prompt: "近期客户端版本号（逗号分隔）",
    },
    {
      name: "window_days",
      required: false,
      prompt: "分析窗口（天）",
      default: 14,
    },
  ],
  steps: [
    {
      id: "fetch_messages",
      type: "tool",
      description: "拉取审批/IM 消息",
      tool: "shell",
      command: "python3 {artifacts_root}/ix-im-cli/main.py fetch --window {params.window_days}",
      expects: ["work/raw/messages.json"],
    },
    {
      id: "prepare_raw",
      type: "tool",
      description: "整理原始数据",
      tool: "shell",
      command: "python3 scripts/prepare.py {params.recent_client_versions}",
    },
    {
      id: "render_report",
      type: "thinking",
      description: "生成审计报告",
      inputs: ["work/raw/*.json"],
      prompt: "你是上线审计助手。标题：{params.report_title}。",
      output: "work/thinking/render_report.md",
    },
  ],
};

export const mockManifests: Record<string, Manifest> = {
  "ix-weekly-report-agent": weeklyManifest,
  "ix-rollout-audit-agent": rolloutManifest,
};

export const mockAgentSpecs: Record<string, AgentSpec> = {
  "ix-weekly-report-agent": {
    name: "ix-weekly-report-agent",
    domain: "周报生成",
    one_liner: "Metabase 拉数 → 语义分析 → 报告",
    status: "implemented",
    intents: ["周报", "weekly", "metrics", "Metabase"],
    params_required: ["primary_input"],
    params_optional: ["window_days"],
    has_thinking: true,
    steps: ["export_primary", "analyze_semantic", "write_report"],
    schedule_safe: true,
    schedule_note: "全自动；Metabase 导出较慢",
    research: "research/weekly-metrics",
  },
  "ix-rollout-audit-agent": {
    name: "ix-rollout-audit-agent",
    domain: "上线单据审计",
    one_liner: "审批信号 → Wiki 文档 → 测试审计 → 报告",
    status: "implemented",
    intents: ["上线", "rollout", "审计", "deploy"],
    params_required: ["report_title", "recent_client_versions"],
    params_optional: ["window_days"],
    has_thinking: true,
    steps: ["fetch_messages", "prepare_raw", "render_report"],
    schedule_safe: false,
    research: "research/rollout-audit",
  },
};

export const mockCliSpecs: Record<string, CliSpec> = {
  "ix-agent-run-cli": {
    name: "ix-agent-run-cli",
    domain: "组合 agent 执行器",
    one_liner: "按 manifest 执行 tool + thinking（claude -p）流水线",
    status: "implemented",
    intents: ["执行 ix-*-agent", "manifest 编排", "tool+thinking 流水线"],
    commands: [
      {
        name: "run",
        inputs: ["--agent ix-<business>-agent", "--set key=value", "--params-json '{...}'", "--resume --run-id <id>"],
        outputs: "ix-agents/<agent>/runs/<run-id>/",
        example: "python main.py run --agent ix-foo-agent",
      },
    ],
    credentials: [],
    depends_on: [],
    notes: "thinking step 调用 Claude Code CLI（claude -p --dangerously-skip-permissions）",
  },
};

// ── Run 样本 ──

export const mockRuns: Record<string, RunSummary[]> = {
  "ix-weekly-report-agent": [
    {
      run_id: "2026-06-18_15-30-00",
      agent_id: "ix-weekly-report-agent",
      status: "completed",
      trigger: "manual",
      started_at: "2026-06-18T15:30:00+08:00",
      steps_completed: ["export_primary", "analyze_semantic", "write_report"],
      steps_total: 3,
      next_step: null,
    },
    {
      run_id: "2026-06-15_09-12-33",
      agent_id: "ix-weekly-report-agent",
      status: "completed",
      trigger: "scheduled",
      started_at: "2026-06-15T09:12:33+08:00",
      steps_completed: ["export_primary", "analyze_semantic", "write_report"],
      steps_total: 3,
      next_step: null,
    },
    {
      run_id: "2026-06-08_09-10-02",
      agent_id: "ix-weekly-report-agent",
      status: "failed",
      trigger: "scheduled",
      started_at: "2026-06-08T09:10:02+08:00",
      steps_completed: ["export_primary"],
      steps_total: 3,
      next_step: "analyze_semantic",
    },
  ],
  "ix-rollout-audit-agent": [
    {
      run_id: "2026-06-17_14-00-00",
      agent_id: "ix-rollout-audit-agent",
      status: "completed",
      trigger: "manual",
      started_at: "2026-06-17T14:00:00+08:00",
      steps_completed: ["fetch_messages", "prepare_raw", "render_report"],
      steps_total: 3,
      next_step: null,
    },
  ],
};

const weeklyRunDetail: RunDetail = {
  ...mockRuns["ix-weekly-report-agent"][0],
  params: { primary_input: "https://metabase.example.com/question/3798", window_days: 7 },
  outputFiles: [
    {
      relPath: "output/report.md",
      name: "report.md",
      size: 2840,
      ext: ".md",
      content:
        "# 周报 — 2026-06-12 ~ 2026-06-18\n\n## 关键变化\n\n- DAU 较上周 +12.3%\n- 新用户转化漏斗第 2 步流失率上升 5pp\n\n## 异常\n\n- 6/16 14:00-15:00 API 错误率 spike（0.2% → 1.8%）\n\n## 建议\n\n1. 排查 6/16 API 异常根因\n2. 优化漏斗第 2 步引导文案\n",
    },
  ],
  thinkingFiles: [
    {
      relPath: "work/thinking/analyze_semantic.md",
      name: "analyze_semantic.md",
      size: 1520,
      ext: ".md",
      content:
        "## 语义分析\n\n基于 work/raw/*.csv（7 天窗口）：\n\n**结论**\n1. DAU 增长健康，主要受新功能上线驱动\n2. 漏斗流失集中在 Android 端\n\n**依据**\n- Android 端第 2 步流失率 23%（iOS 14%）\n- 6/16 错误率 spike 与部署 v3.2.1 时间重合\n",
    },
  ],
  rawFiles: [
    {
      relPath: "work/raw/audit-result.json",
      name: "audit-result.json",
      size: 4200,
      ext: ".json",
      content: '{\n  "ok": true,\n  "clis": [],\n  "issues": []\n}\n',
    },
  ],
};

export const mockRunDetails: Record<string, RunDetail> = {
  "ix-weekly-report-agent/2026-06-18_15-30-00": weeklyRunDetail,
};

// ── 审计 / 同步 / 初始化 ──

export const mockAudit: AuditReport = {
  ok: true,
  workspace: "/Volumes/Under_M2/morphiiouo/indexed",
  clis: mockClis.map((c) => ({
    name: c.name,
    subcommands: c.subcommands,
    has_spec_yaml: c.has_spec_yaml,
  })),
  agents: mockAgents.map((a) => ({
    name: a.name,
    has_thinking: a.has_thinking,
    steps_summary: a.stepsSummary,
    required_params: a.requiredParams,
  })),
  issues: [
    {
      level: "warn",
      code: "STALE_INDEX",
      message: "ix-weekly-report-agent 存在于磁盘但未在 registry.md 用户区登记",
      target: "ix-agents/registry.md",
    },
  ],
};

export const mockSync: SyncResult = {
  syncedFiles: [
    { file: "artifacts/capabilities.md", count: 2 },
    { file: "ix-agents/registry.md", count: 2 },
  ],
  changed: true,
};

export const mockInit: InitStatus = {
  version: "0.1.0",
  gitMode: "remote",
  nick: "Xi酱",
  addr: "您",
  gitInitialized: true,
  remote: "origin\tgit@github.com:user/indexed.git (fetch)",
};

// ── 资产树 ──

export const mockTree: TreeNode = {
  name: "indexed",
  path: "",
  kind: "bucket",
  children: [
    {
      name: "artifacts",
      path: "artifacts",
      kind: "bucket",
      children: [
        { name: "capabilities.md", path: "artifacts/capabilities.md", kind: "file" },
        { name: "OVERVIEW.md", path: "artifacts/OVERVIEW.md", kind: "file" },
        {
          name: "ix-agent-run-cli",
          path: "artifacts/ix-agent-run-cli",
          kind: "dir",
          children: [
            { name: "main.py", path: "artifacts/ix-agent-run-cli/main.py", kind: "file" },
            { name: "runner.py", path: "artifacts/ix-agent-run-cli/runner.py", kind: "file" },
            { name: "thinking.py", path: "artifacts/ix-agent-run-cli/thinking.py", kind: "file" },
            { name: "SPEC.yaml", path: "artifacts/ix-agent-run-cli/SPEC.yaml", kind: "file" },
          ],
        },
        {
          name: "ix-init-cli",
          path: "artifacts/ix-init-cli",
          kind: "dir",
          children: [
            { name: "main.py", path: "artifacts/ix-init-cli/main.py", kind: "file" },
            { name: "config.py", path: "artifacts/ix-init-cli/config.py", kind: "file" },
          ],
        },
        {
          name: "ix-workspace-index-cli",
          path: "artifacts/ix-workspace-index-cli",
          kind: "dir",
          children: [{ name: "main.py", path: "artifacts/ix-workspace-index-cli/main.py", kind: "file" }],
        },
      ],
    },
    {
      name: "ix-agents",
      path: "ix-agents",
      kind: "bucket",
      children: [
        { name: "registry.md", path: "ix-agents/registry.md", kind: "file" },
        { name: "OVERVIEW.md", path: "ix-agents/OVERVIEW.md", kind: "file" },
        {
          name: "ix-weekly-report-agent",
          path: "ix-agents/ix-weekly-report-agent",
          kind: "dir",
          children: [
            { name: "manifest.yaml", path: "ix-agents/ix-weekly-report-agent/manifest.yaml", kind: "file" },
            { name: "SPEC.yaml", path: "ix-agents/ix-weekly-report-agent/SPEC.yaml", kind: "file" },
            { name: "paths.py", path: "ix-agents/ix-weekly-report-agent/paths.py", kind: "file" },
          ],
        },
        {
          name: "ix-rollout-audit-agent",
          path: "ix-agents/ix-rollout-audit-agent",
          kind: "dir",
          children: [
            { name: "manifest.yaml", path: "ix-agents/ix-rollout-audit-agent/manifest.yaml", kind: "file" },
            { name: "SPEC.yaml", path: "ix-agents/ix-rollout-audit-agent/SPEC.yaml", kind: "file" },
          ],
        },
      ],
    },
    {
      name: "_shared",
      path: "_shared",
      kind: "bucket",
      children: [
        {
          name: "design-languages",
          path: "_shared/design-languages",
          kind: "dir",
          children: [
            "material-you",
            "bauhaus",
            "newsprint",
            "flat-design",
            "hand-drawn",
            "industrial-skeuomorphism",
          ].map((id) => ({
            name: id,
            path: `_shared/design-languages/${id}`,
            kind: "dir" as const,
            children: [
              { name: "meta.md", path: `_shared/design-languages/${id}/meta.md`, kind: "file" as const },
              { name: "preview.html", path: `_shared/design-languages/${id}/preview.html`, kind: "file" as const },
            ],
          })),
        },
        {
          name: "specs",
          path: "_shared/specs",
          kind: "dir",
          children: [{ name: "capability", path: "_shared/specs/capability", kind: "dir" }],
        },
        {
          name: "templates",
          path: "_shared/templates",
          kind: "dir",
          children: [{ name: "ix-agents", path: "_shared/templates/ix-agents", kind: "dir" }],
        },
      ],
    },
    {
      name: "reports",
      path: "reports",
      kind: "bucket",
      children: [],
    },
    {
      name: "research",
      path: "research",
      kind: "bucket",
      children: [
        { name: "OVERVIEW.md", path: "research/OVERVIEW.md", kind: "file" },
      ],
    },
    {
      name: "ix-gui",
      path: "ix-gui",
      kind: "dir",
      children: [
        { name: "OVERVIEW.md", path: "ix-gui/OVERVIEW.md", kind: "file" },
        { name: "SPEC.yaml", path: "ix-gui/SPEC.yaml", kind: "file" },
        {
          name: "web",
          path: "ix-gui/web",
          kind: "dir",
          children: [
            { name: "package.json", path: "ix-gui/web/package.json", kind: "file" },
            { name: "vite.config.ts", path: "ix-gui/web/vite.config.ts", kind: "file" },
            { name: "index.html", path: "ix-gui/web/index.html", kind: "file" },
          ],
        },
      ],
    },
  ],
};
