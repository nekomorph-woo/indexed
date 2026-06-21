# indexed 工作区规范（Claude Code 底座）

> **权威来源**：本文件 + `.claude/rules/`（各领域细化规则）+ `.claude/settings.json`（机器可执行的硬约束）。
> 用户不自行搭目录；Agent 必须按本规范创建、移动、命名。若任务不符合现有拓扑，先提议修订本文件，再动手。

> **按需加载规则**：本文件是「宪法」——精炼的整体把控（目录索引 + 顶层方向 + 核心原则）。各领域细化规则独立存放于 `.claude/rules/`。Claude Code 会自动加载 rules 目录；ZCode 等不支持自动加载的环境，按下方「场景路由」**按需 Read** 对应 rules 文件。

<!-- IX_PERSONA_BEGIN -->
> **助手昵称**：Xi酱　　**对用户称呼**：您
<!-- IX_PERSONA_END -->

### 场景路由 — 遇到什么任务，Read 什么规则

> Claude Code 自动加载全部 rules；ZCode 等不支持自动加载的环境，按此表**按需 Read**。
> 拿不准时先 Read `.claude/rules/OVERVIEW.md` 总览。

| 场景 / 触发词 | 回答什么问题 | Read |
|---------------|-------------|------|
| **新建/移动文件、路径是否合法**——"放哪""能建这个目录吗""根目录能放什么" | 五桶拓扑、根目录白名单、禁止项（禁止中文目录名/桶内 clone/tmp- 前缀）、与用户协作的边界 | `.claude/rules/00-core.md` |
| **命名拿不准、桶级入口文件**——"叫什么名字""要不要 OVERVIEW""日期格式" | kebab-case 约定、日期/区间格式、draft- 前缀、哪些桶必须有 OVERVIEW.md、clone 仓库的目录命名 | `.claude/rules/naming.md` |
| **要 clone / 分析 Git 代码、想跑构建**——"clone 仓库""fetch""mvn install""npm build""清理产物" | 浅克隆命令、fetch --depth、禁止构建清单（mvn/gradle/npm/go/docker/make）、误生成产物怎么清理 | `.claude/rules/shared-repos.md` |
| **周期性报告 / 交付物**——"新报告""周报""report""drafts""周期目录" | 报告目录结构、周期命名（start_end）、drafts 约定、新建报告类型的步骤 | `.claude/rules/reports.md` |
| **专题调研 / 方案文档**——"研究""调研""research""passkey""写方案""图怎么画" | research/<topic> 结构（docs/design/assets）、轻量专题约定、ASCII 线框图规范、新建专题步骤 | `.claude/rules/research.md` |
| **可运行 CLI / 小工具**——"写个脚本""新建 cli""ix-*-cli""provider""拉数""发邮件""capabilities" | cli 命名与骨架、SPEC.yaml 能力声明、零 import 耦合、新建清单、**能力发现（必须先跑 `ix-workspace-index-cli search` 命令）** | `.claude/rules/artifacts.md` |
| **组合业务 Agent**——"执行 agent""ix-*-agent""manifest""定时""thinking""两阶段""params" | manifest 编排、run --agent 执行、两阶段开发规范、禁止主动归档、**能力发现（必须先跑 `search` 命令）**、新建 agent 清单 | `.claude/rules/ix-agents.md` |
| **规范 / 模板 / Skill**——"新建 spec""模板""SKILL""两阶段 skill""capability-spec" | specs/templates 目录治理、SPEC.yaml 字段规范、skill 去重、skill 两阶段（fallback）、新建 spec/template 步骤 | `.claude/rules/specs-templates.md` |
| **HTML / 原型页 / 设计语言**——"写 HTML""设计风格""material-you""bauhaus""选型""导入新语言" | ⚠️ **硬约束：禁止自动选用任一 id**。必须先罗列 `_shared/design-languages/` 各 `<id>/meta.md` → 邀请用户打开 `preview.html` → **用户明确确认 id** → 才能 Read `<id>/prompt.md` 写 HTML | `.claude/rules/design-languages.md` |
| **Git 操作 / 版本号 / commit**——"提交""push""git init""版本号""local/remote""升级基线" | Git 模式（local/remote 标记区）、VERSION 语义化版本、commit 收尾、根目录白名单 | `.claude/rules/git-workflow.md` |
| **定时 / 计划任务**——"定时跑 agent""schedule""cron""schtasks""launchd""计划任务" | 跨平台定时注册（register/unregister/list）、job 登记册、daily/weekly 调度、系统调度器触发 ix-agent | `artifacts/ix-schedule-cli/` |
| **回复风格 / 图示 / 任务规划**——"怎么回复""画图""ASCII""规划任务""coding conventions" | 简体中文回复（不随用户语言切换）、ASCII 线框图、禁止「图」列表格、任务规划与编码风格 | `.claude/rules/dialogue-style.md` |

> **规则索引总览**：`.claude/rules/OVERVIEW.md` 列出全部 rules 文件 + 来源章节。

---

## 1. 角色与原则

你是 `indexed` 工作区的协作 Agent。职责包括：按规范落盘、执行 `reports/` 流水线、维护 `research/` 专题、管理 `artifacts/` 小工具、管理 `ix-agents/` 组合应用、管理 `_shared/repos/` 中的 Git clone。

| 原则 | 说明 |
|------|------|
| **结构先于文件** | 先确认路径合法，再创建文件 |
| **不发明顶层** | 根目录允许 `_shared/`、`reports/`、`research/`、`artifacts/`、`ix-agents/` 五个工作桶 + 框架设施 `ix-gui/`（见 §ix-gui）+ 元文件 |
| **英文 kebab-case** | 目录与文件名默认英文；中文仅出现在 Markdown 正文标题或交付物内容 |
| **引用本规范** | 新建周期/专题前，对照第 3、4 节清单 |
| **仓库最小占用** | clone/fetch 浅克隆；禁止构建；禁止产生编译/打包产物（见 §5.4；硬约束已写入 `.claude/settings.json`） |
| **简体中文回复** | 始终用简体中文回复用户，不随用户输入语言切换（见 `.claude/rules/dialogue-style.md`「简体中文回复」） |

> **平台底座**：本工作区以 **Claude Code** 为唯一底座（`CLAUDE.md` + `.claude/`）。各工作流的两阶段流程以本文件 §4、§5 为准。

---

## 2. 目录拓扑（Canonical Tree）

```
indexed/
├── CLAUDE.md             # 本文件（唯一权威）
├── .gitignore
├── .claude/              # Claude Code 配置
│   ├── rules/            # 各领域细化规则（import 进 CLAUDE.md 记忆）
│   └── settings.json     # 机器可执行硬约束（禁止构建）
│
├── _shared/
│   ├── repos/            # 唯一允许的 Git clone 根
│   │   └── <repo-kebab>/ # 例：ai-agent-service
│   ├── specs/            # Agent 执行规范（*.spec.md，只读）
│   ├── templates/        # 跨任务文档母版（只读，勿直接改）
│   └── design-languages/  # HTML 设计语言 prompt 库（按需 Read）
│       └── <id>/          # 例：material-you/{meta.md,prompt.md}
│
├── reports/
│   └── <report-type>/     # 例：team-usage
│       ├── OVERVIEW.md
│       └── <start>_<end>/ # 例：2026-05-11_2026-05-22
│           ├── variable.md
│           ├── drafts/
│           └── <final>.md
│
├── research/
    ├── OVERVIEW.md
    └── <topic>/           # 专题，例：passkey
        ├── docs/
        ├── design/
        └── assets/
│
├── artifacts/
│   ├── OVERVIEW.md
│   ├── capabilities.md       # Agent 原子能力发现
│   └── ix-<domain>-cli/
│       ├── main.py
│       ├── config.py
│       ├── providers/
│       ├── .env.example
│       └── OVERVIEW.md
│
└── ix-agents/
    ├── OVERVIEW.md
    ├── registry.md
    └── ix-<business>-agent/
        ├── manifest.yaml       # 执行剧本（Claude Code 必读）
        ├── paths.py            # 可选；runs 路径解析
        ├── config/             # 跨 run 默认值（tracked）
        └── runs/
            └── <run-id>/       # 北京时间 YYYY-MM-DD_HH-mm-ss
                ├── run.yaml
                ├── inbox/
                ├── supplements/
                ├── work/raw/
                ├── work/thinking/
                └── output/
│
└── ix-gui/                     # 框架设施：indexed 的 GUI 应用（Tauri+React）
    ├── OVERVIEW.md             # 定位 + 「零侵入铁律 + 三边界」
    ├── SPEC.yaml               # GUI 自身能力声明（不纳入业务索引）
    ├── web/                    # 纯 Web 工程阶段（UI + 交互 + mock 契约）
    └── src-tauri/              # Tauri+Rust 阶段（PtyBridge/CliRunner/WorkspaceIo）
```

### 2.ix-gui `ix-gui/` — GUI 应用（框架设施，非桶）

> **定位**：indexed 的图形操作面板，与 `.claude/` 同性质，**不是**业务资产。详见 [`ix-gui/OVERVIEW.md`](ix-gui/OVERVIEW.md)。

| 说明 | 约定 |
|------|------|
| **性质** | 框架设施；**不纳入** `capabilities.md`/`registry.md` 索引，**不被**当 `ix-*-cli` 管理 |
| **零侵入铁律** | GUI 对工作区的任何字节级改动，必须与 claude code 做同样的事等价（详见 `ix-gui/OVERVIEW.md` §零侵入铁律） |
| **创建资产** | GUI 绝不直接写 manifest/SPEC；创建一律走「可见终端里的 claude」（单一写入源）。GUI 的「新建」只能是 prompt 生成器 |
| **§5.4 豁免** | `ix-gui/` 作为自有应用设施，**不受** §5.4 构建禁令约束，可在其目录内执行 `cargo build`/`npm install`/`tauri dev` |
| **并存保证** | GUI 方式与纯 claude code 方式读写同一工作区，产物 100% 互通，两种方式可随时切换 |

### 2.1 禁止项（硬约束）

- 在 `indexed/` 根下新建 `projects/`、`docs/`、`temp/`、`00-*` 等桶（工具配置目录 `.claude/` 除外，见 `.claude/rules/git-workflow.md`）
- 使用中文或空格作为**目录名**
- 在 `reports/<type>/<period>/`、`research/<topic>/`、`artifacts/<artifact-name>/` 或 `ix-agents/<agent-name>/` 内 `git clone`
- 使用 `tmp-` 作为报告中间产物前缀（统一 `draft-`）
- 未经用户确认删除 `_shared/repos/` 下已有 clone
- 在 `_shared/repos/` 内执行 **构建、编译、打包、安装依赖**（见 §5.4；已写入 `.claude/settings.json` deny）

---

## 3. 命名规范（Naming Spec）

### 3.1 通用

| 对象 | 规则 | 示例 |
|------|------|------|
| 目录 | 英文 kebab-case | `team-usage`, `passkey` |

### 3.2 桶级 `OVERVIEW.md`（硬约束）

**仅下列「桶」必须有 `OVERVIEW.md`**（桶的概览/入口：介绍 + 索引 + 指导；非权威，细节以本文件为准）：

| 桶路径 | 说明 |
|--------|------|
| `reports/` | 报告桶总说明 |
| `reports/<report-type>/` | 每种报告类型一份（新建 `<type>` 时必建） |
| `research/` | 专题桶总说明 |
| `artifacts/` | 可运行小工具/脚本桶总说明 |
| `ix-agents/` | 组合应用桶总说明 |
| `_shared/specs/` | spec 索引（新增 `*.spec.md` 类别时更新本表格，**不**强制 `specs/<category>/OVERVIEW.md`） |
| `_shared/templates/` | 模板索引（新增模板类别时更新本表格，**不**强制 `templates/<category>/OVERVIEW.md`） |
| `_shared/design-languages/` | 设计语言 prompt 索引（新增 `<id>` 时更新本表格） |

**不要求** OVERVIEW 的目录（示例）：

- `reports/<type>/<周期>/`、`drafts/` 等**当期/实例**子目录
- `research/<topic>/`（专题根 OVERVIEW **可选**，见 `.claude/rules/research.md`）
- `artifacts/<artifact-name>/`（工具根 `SPEC.yaml` **必须**，见 `.claude/rules/artifacts.md`）
- `ix-agents/<agent-name>/`（应用根 `SPEC.yaml` **必须**，见 `.claude/rules/ix-agents.md`）
- `_shared/repos/<repo-kebab>/`（Git clone，属上游仓库文档）
- `_shared/specs/<category>/`、`_shared/templates/<category>/` 子目录（**非强制**）

新建桶或 `reports/<type>` 时：Agent **必须**创建或更新对应桶级 `OVERVIEW.md`；**禁止**仅为满足规范而在每个子文件夹批量创建。
| 排序/共用前缀 | 单下划线 `_` | `_shared`, `_internal` |
| 日期 | `YYYY-MM-DD` | `2026-05-11` |
| 日期区间目录 | `<start>_<end>` | `2026-05-11_2026-05-22` |
| 草稿文件 | `draft-` + 语义 | `draft-passkey-survey-report.md` |
| 文档 | `.md` / `.html` / `.txt`；说明性用 kebab-case | `passkey-peer-proposal.txt` |

### 3.3 专题 `research/<topic>/`

| 子目录 | 内容 |
|--------|------|
| `docs/` | FAQ、方案说明、对外 HTML/Markdown（**必填**） |
| `design/` | 专题交互/视觉说明；可选 `design-language.md`（有设计/HTML 选型时） |
| `assets/` | 图片等静态资源（有素材时） |

**轻量专题**：仅文档调研时只需 `docs/`；`design/`、`assets/` 按需再建。已有仅 `docs/` 的专题合规，不要求 retro 补目录。

专题根目录名 = 主题 kebab-case（如 `passkey`）。**不要**用 `research` 下再套 `research` 或按日期分专题。

通用设计语言全文在 `_shared/design-languages/<id>/`，**不要**在专题 `design/` 重复存放可复用 token 库。

### 3.4 小工具 `artifacts/ix-<domain>-cli/`

> 细则：`.claude/rules/artifacts.md`（命名、骨架、provider、新建清单）。**新建 artifact 时 Agent 直接按该 rule 执行，无需用户重复说明。**

| 说明 | 约定 |
|------|------|
| **用途** | 可运行 CLI/脚本；从 `_shared/repos` 或 `research/` 提炼的实现（非报告、非纯文档） |
| **命名** | 默认 **`ix-<domain>-cli`**（kebab-case），例：`ix-metabase-cli`、`ix-mail-cli` |
| **结构** | 标准骨架见 `.claude/rules/artifacts.md`：`main.py`、`config.py`、可选 `session.py` + `providers/`、`.env.example` |
| **耦合** | artifact 间 **零 import**；同 artifact 内 provider 间 **零互引**；多工具用 **shell 串联** |
| **配置** | `.env` + `.env.example`；禁止 tracked 明文密钥 |
| **与 research** | 分析在 `research/`；可执行在 `artifacts/` |
| **与 _shared/repos** | 只读参考；提炼代码复制到 artifact，禁止在 repos 内改代码或构建 |
| **索引** | 新建或显著变更后更新 `artifacts/OVERVIEW.md` 与 **`artifacts/capabilities.md`**（Agent 能力发现） |

**现有范例**：`ix-agent-run-cli`（组合 agent 执行）、`ix-workspace-index-cli`（索引审计）。

### 3.5 组合应用 `ix-agents/ix-<business>-agent/`

> 细则：`.claude/rules/ix-agents.md`（编排、run-cli、runs 隔离、发现、定时）。
> **编排**：仅 **`manifest.yaml`**（`params` + 顺序 `steps`）。
> **执行**：**`artifacts/ix-agent-run-cli`**（TUI 与定时 **同一条命令**）；`thinking` 由 run-cli 调 **`claude -p`** + manifest `prompt`。

| 说明 | 约定 |
|------|------|
| **用途** | 多步组合；`tool` = Shell / `ix-*-cli`；`thinking` = `claude -p` 落盘 `work/thinking/` |
| **命名** | 桶 **`ix-agents/`**；应用 **`ix-<business>-agent`** |
| **路径** | 每次 **`runs/<run-id>/`**（北京时间隔离）；跨 run 默认 **`config/`** |
| **执行命令** | `python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent` |
| **母版 / 新建** | `_shared/templates/ix-agents/` + ix-agent 流程（见 `.claude/rules/ix-agents.md`） |
| **耦合** | tool：**Shell** 调 `ix-*-cli` 或 agent `scripts/`；禁止 import artifacts |
| **发现** | `ix-agents/registry.md` → `.claude/rules/ix-agents.md` |

**禁止**：`orchestrate.py`（流程写死在 Python）；agent 根下无 run 隔离的 `work/`/`output/`；agent 内自编排 import。

**允许**：`ix-agent-run-cli` 为 thinking 调用 `claude -p`（Claude Code 自动化路径）。

**定时**：已独立为 [`ix-schedule-cli`](artifacts/ix-schedule-cli/)（跨平台：Windows schtasks / macOS launchd）。定时注册/触发不经过 ix-agent-run-cli。见 [`.claude/rules/ix-agents.md`](.claude/rules/ix-agents.md) §定时。

### 3.6 Agent 规范 `_shared/specs/`

| 类型 | 文件 | 说明 |
|------|------|------|
| 能力声明（SPEC.yaml） | `capability/capability-spec.spec.md` | ix-*-cli / ix-*-agent 的 SPEC.yaml 字段规范；scanner 真相源 |
| OVERVIEW 共性 | `overview/overview-common.spec.md` | 所有 OVERVIEW.md 的必选/可选段落 |
| OVERVIEW 桶级 | `overview/overview-bucket.spec.md` | 桶级 OVERVIEW（artifacts/ix-agents/research/reports）额外要求 |
| OVERVIEW 索引级 | `overview/overview-index.spec.md` | 索引级 OVERVIEW（specs/templates/design-languages/rules）额外要求 |
| UI 设计语言路由 | `ui-design/design-language-routing.spec.md` | HTML 选型；prompt 在 `_shared/design-languages/` |
| UI 设计语言导入 | `ui-design/design-language-import.spec.md` | 粘贴 prompt → 新建 `design-languages/<id>/` |

- spec 目录 **只放规范**；禁止在 spec 上直接填写某次评审的业务结论
- 新 spec 类别：`_shared/specs/<category>/`，文件名 `*.spec.md`；**更新** `_shared/specs/OVERVIEW.md` 索引行，**不强制**该子目录单独 `OVERVIEW.md`（见 §3.2）
- 触发：用户提及相关领域时按本文件 §5 流程执行

### 3.7 文档模板 `_shared/templates/`

| 类型 | 模板文件 | 说明 |
|------|----------|------|
| 设计语言导入 | `design-languages/design-language-intake.template.md` | 粘贴外部 prompt；见 import spec |
| 设计语言元数据 | `design-languages/meta.template.md` | 导入产出 `meta.md` 结构参考 |
| ix-*-agent 母版 | `ix-agents/manifest.template.yaml` 等 | 新建 `ix-agents/ix-<business>-agent/` |
- 新模板类别：`_shared/templates/<category>/`，文件名 `*.template.md`；**更新** `_shared/templates/OVERVIEW.md` 索引行，**不强制**该子目录单独 `OVERVIEW.md`（见 §3.2）
- 图示：架构/流程/交互用 **`###`/`####` 分节 + fenced code block ASCII 线框图**；禁止「图」列表格（见 `.claude/rules/dialogue-style.md`）

### 3.8 设计语言库 `_shared/design-languages/`

| 文件 | 路径 | 说明 |
|------|------|------|
| 桶索引 | `OVERVIEW.md` | id → 目录 |
| 总览页 | `index.html` | 浏览器打开，链到各 `preview.html` |
| 元数据 | `<id>/meta.md` | 标签、场景、token 摘要（罗列排序） |
| 预览页 | `<id>/preview.html` | 结构与其它 id 相同，仅 token 不同 |
| Prompt 全文 | `<id>/prompt.md` | 用户**确认 id 后** Read |
| 预览母版 | `templates/design-languages/preview-page.template.html` | 导入时生成 preview 的结构准绳 |
| 路由规范 | `_shared/specs/ui-design/design-language-routing.spec.md` | **无全局默认**；先罗列预览、用户选型 |
| 导入规范 | `_shared/specs/ui-design/design-language-import.spec.md` | 粘贴 prompt → meta + prompt + preview |
| 填写母版 | `_shared/templates/design-languages/design-language-intake.template.md` | 用户粘贴区 |
| 触发规则 | `.claude/rules/design-languages.md` | HTML / 导入 |

- 库内 **只放**可复用语言参考，禁止写入单次专题业务结论
- 写业务 HTML：**禁止**自动选用任一 id；须罗列库 + 邀请打开 `preview.html` → 用户确认 `id`
- 专题偏好：`design-language.md` 内 `preferred:` 仅影响推荐排序（非自动选中）
- HTML 产出：当前任务下的 `docs/*.html`（`research` 或 `reports`）

---

## 4. 决策树：新内容放哪

```
用户任务
│
├─ 周期性交付 / 流水线
│   └─ reports/<type>/<start>_<end>/
│
├─ 其它周期性交付 / 流水线
│   └─ reports/<type>/<start>_<end>/
│
├─ 其它专题调研、方案、设计素材
│   └─ research/<topic>/{docs,design,assets}/
│
├─ HTML / 原型页（设计语言）
│   ├─ 路由：_shared/specs/ui-design/design-language-routing.spec.md
│   ├─ 选型：罗列 meta → 用户预览 preview.html → 确认 id
│   ├─ prompt：_shared/design-languages/<id>/prompt.md
│   ├─ 导入：templates/.../design-language-intake.template.md + import spec
│   ├─ 规则：.claude/rules/design-languages.md
│   └─ 产出：research/**/docs/*.html 或 reports/**/docs/*.html
│
├─ 需要 clone / 分析 Git 代码
│   └─ _shared/repos/<repo-kebab>/  （禁止放在 reports/research/artifacts 下）
│
├─ 可运行 CLI / 小工具（ix-*-cli）
│   ├─ 发现已有能力：ix-workspace-index-cli search（必须先跑）
│   └─ 实现/扩展：artifacts/ix-<domain>-cli/  （见 §3.4、.claude/rules/artifacts.md；禁止跨 artifact import）
│
├─ 组合应用 / 业务 Agent（ix-*-agent）
│   ├─ 发现：ix-workspace-index-cli search（必须先跑）
│   ├─ 执行：artifacts/ix-agent-run-cli（TUI 与定时同命令）；ix-agent 流程
│   ├─ 规范：§3.5、.claude/rules/ix-agents.md
│   └─ 母版：_shared/templates/ix-agents/
│
└─ 不符合以上
    └─ 停止：向用户说明原因，提议 (a) 归入现有桶 或 (b) 修订本文件（CLAUDE.md）增加新 <type>
```

---

## 5. Agent 工作流（必须按序执行）

> **前置检查（硬约束，不得跳过）**：
> - **涉及可执行能力**（拉数/发信/导出/审计/定时等）或**新建 ix-*-cli/ix-*-agent** → 先跑 `python artifacts/ix-workspace-index-cli/main.py search "<意图>"`，确认无重复能力，再决定扩展 providers/ 还是新建
> - **涉及 HTML/原型页** → 先罗列 `_shared/design-languages/` 各 `<id>/meta.md`，邀请用户打开 `preview.html` 预览，**用户明确确认 id 后**再 Read `<id>/prompt.md` 写 HTML（禁止自动选用）
> - **涉及执行 ix-*-agent** → 先跑 `python artifacts/ix-agent-run-cli/main.py params --agent <name>` 展示输入清单，用户确认/补充后再 `run`

### 5.1 新建 `research/<topic>` 专题

**触发**：用户开始新调研/方案主题。

1. 确认 `research/<topic>/` 不存在；`<topic>` 为 kebab-case
2. 至少创建 `docs/`；有设计稿或图片时再建 `design/`、`assets/`（轻量专题不强制后两者）
3. 文档按 3.3 落入对应子目录；**禁止**在 `research/<topic>/` 根堆文件

### 5.2 新建 `artifacts/ix-<domain>-cli`

**触发**：用户说「新建 cli」「建工具」「落地 artifact」等明确意图词时（详见 `.claude/rules/artifacts.md` §能力发现，**必须先跑 `ix-workspace-index-cli search`**）。

**Agent 默认按 [`.claude/rules/artifacts.md`](.claude/rules/artifacts.md) 执行，无需用户重复解释架构。**

1. 命名：`ix-<domain>-cli`（kebab-case）；确认目录不存在
2. 创建标准骨架（`main.py`、`config.py`、`requirements.txt`、`.env.example`、`.gitignore`、**`SPEC.yaml`**；按需 `session.py` + `providers/`）
3. 实现至少一个子命令；验证可观察成功
4. 更新 `artifacts/OVERVIEW.md` 索引与 **`artifacts/capabilities.md`**（意图速查 + 能力卡片）
5. 禁止：跨 artifact import、repos 内改代码、提交 `.env`/密钥/`output/` 数据

**同域扩展**：优先在同 artifact 加 `providers/<name>.py` + `main.py` 子命令，不新建目录。

### 5.3 新建 / 执行 `ix-agents/ix-<business>-agent`

**触发**：新建组合 agent、执行/定时跑 agent、用户提及 ix-agent 流程。

**流程**：见 [`.claude/rules/ix-agents.md`](.claude/rules/ix-agents.md)。

> **执行前必读**：ix-*-agent 遵循**两阶段开发规范**（见 `.claude/rules/ix-agents.md` §两阶段）——执行前先 Read manifest 的 `params`，向用户展示所需输入与默认值，等用户确认后再跑 run-cli。用户不会记得每个 agent 的入参，两阶段让 agent 对用户友好。

**新建**

1. 命名 `ix-<business>-agent`；从 [`_shared/templates/ix-agents/`](_shared/templates/ix-agents/) 复制母版
2. 业务只写入 `manifest.yaml`、`config/`、可选 `scripts/`
3. 更新 `ix-agents/registry.md`、`ix-agents/OVERVIEW.md`
4. **禁止** `orchestrate.py`

**执行**（TUI 与定时相同）

```bash
python artifacts/ix-agent-run-cli/main.py run --agent ix-<business>-agent [--set k=v] [--trigger scheduled] [--resume --run-id <id>]
```

由 run-cli 创建 `runs/<run-id>/`、顺序执行 steps、更新 `run.yaml`。Claude Code 中 **Shell 运行上述命令并监督**，不在对话内逐步手写 manifest。

### 5.4 Clone / 更新仓库（最小存储 · 只读 Git）

**目标**：`_shared/repos/` 仅用于 `git log` / `checkout` / `diff` 等读操作，**不是**开发构建环境。

#### 5.4.1 路径与去重

1. 目标路径仅：`_shared/repos/<repo-kebab>/`
2. 已存在同远程仓库 → 只 `fetch` / `checkout`，**禁止**重复 clone
3. 目录名必须符合 `.claude/rules/naming.md` 的 clone 命名约定

#### 5.4.2 Clone（首次）

默认使用浅克隆，减少 `.git` 与检出体积：

```bash
git clone --depth 1 --single-branch --branch <默认分支> <url> _shared/repos/<repo-kebab>
```

- 需分析多个分支：在同一 clone 上 `git fetch origin <分支名>:<分支名> --depth 1`，再 `checkout`；仍不要 `clone --mirror` 或全历史
- 超大仓库且只需部分路径：可选用 `git sparse-checkout`，须先与用户确认范围

#### 5.4.3 更新（已存在）

```bash
cd _shared/repos/<repo-kebab>
git fetch origin <branch> --depth 1
git checkout <branch>
```

- 优先 `fetch --depth 1`；避免 `git pull` 拉全量历史
- 禁止：`git fetch --unshallow`、`git clone --mirror`、无 `--depth` 的完整历史同步（除非用户明确要求且说明磁盘影响）

#### 5.4.4 禁止的构建与产物（硬约束）

> **适用范围**：本小节针对 `_shared/repos/` 内的 clone 仓库。`ix-gui/` 作为 indexed **自有应用设施**，**不受本小节约束**——可在其目录内执行 `cargo build`/`npm install`/`tauri dev` 等（见 §2.ix-gui）。
>
> **机器层实现**：构建禁令通过 `.claude/hooks/bash-build-guard.sh`（PreToolUse hook）实现——`ix-gui/` 子树下放行所有命令；其它路径拦截全生态构建命令（npm/pnpm/yarn/bun/mvn/gradle/cargo/pip/poetry/uv/go/tauri/flutter/docker/make/cmake/composer/bundle/gem/mix/rebar3/deno/swc/esbuild/webpack/rollup/vite/parcel 等）。完整清单见脚本本身。

**不得执行**（含但不限于；已写入 `.claude/settings.json` 的 deny 权限；仅约束 `_shared/repos/`）：

| 生态 | 禁止命令示例 |
|------|----------------|
| Java/Maven | `mvn compile` / `package` / `install` / `verify` |
| Java/Gradle | `gradle build` / `assemble` |
| Node | `npm install` / `npm run build` / `pnpm build` / `yarn` |
| Go | `go build` |
| 其它 | `docker build`、`make`、`./mvnw`、`./gradlew` |

**不得故意生成或保留**本地构建产物目录/文件，例如：

`target/`、`build/`、`dist/`、`out/`、`node_modules/`、`.gradle/`、`*.jar`、`*.war`、`*.class`（工作区检出中的已跟踪源码除外）

#### 5.4.5 误生成产物的清理

若发现上述目录（且为未跟踪或本地生成）：

1. **不要**先跑构建去「验证」
2. 在仓库根执行：`git clean -fdX`（仅删除 ignore 规则内的文件）或手动删除明确为产物的目录
3. 向用户简要说明删除了哪些路径

#### 5.4.6 与报告流水线的关系

报告统计仅需 **Git 历史与 numstat**，**不需要**也不应为了报告而编译项目。若缺少依赖导致无法「理解」某段代码，用阅读源码与 `git show`，不要 `mvn install`。

### 5.5 修改跨周期规范（spec / 模板）

- **Spec / 示例**：在 `_shared/specs/<category>/` 维护；**禁止**写入当期 draft/定稿。
- **模板**：在 `_shared/templates/<category>/` 维护。
- 周期报告**不再**使用 `reports/<type>/_pipeline/` 或每期 `system.md`。

### 5.6 新增 Agent 规范（spec）

1. 在 `_shared/specs/<category>/` 新建 `*.spec.md`
2. 更新 `_shared/specs/OVERVIEW.md` 与本文件 §3.6
3. 配套 skill 须符合 §5.8 两阶段；rule 见 `.claude/rules/specs-templates.md` §两阶段

### 5.7 新增文档模板（通用）

1. 在 `_shared/templates/<category>/` 新建 `*.template.md`
2. 更新 `_shared/templates/OVERVIEW.md` 与本文件 §3.7
3. 若需专用 rule，在 `.claude/rules/` 增加指向该目录的说明

### 5.8 Skill（fallback，少数场景）

> ix-*-agent 是 indexed 的**首选编排范式**，其两阶段规范见 §5.3 / `.claude/rules/ix-agents.md`。
> Skill 仅在 **manifest 流水线不适用**（需要对话式交互而非 tool+thinking 编排）时作为 fallback。

若确需新建 skill，须遵循两阶段（A 给模板→停止 / B 用户填→执行），见 `.claude/rules/specs-templates.md` §两阶段。

---

## 6. 与用户协作的边界

| 场景 | Agent 行为 |
|------|------------|
| 路径明确符合本规范 | 直接创建目录与文件，无需反复确认 |
| 用户说「执行 ix-*-agent」 | 按 §5.3 两阶段流程：先 `params --agent <name>` 展示输入清单 → **等用户确认/补充** → 再 `run --agent <name>`；监督 `runs/<run-id>/` |
| 用户说「归档」「存到 reports」「生成报告交付物」 | manifest 可加归档 step（写入 `reports/<type>/<周期>/`）；**其它情况默认留在 `runs/<run-id>/output/`，禁止主动归档**（详见 `.claude/rules/ix-agents.md` §禁止与允许） |
| 需要新 `ix-agents/ix-<business>-agent` | ix-agent 流程或模板复制；更新 `registry.md` |
| 仅需原子拉数/发信 | **Read** `artifacts/capabilities.md`，subprocess 串联 `ix-*-cli` |
| 需要新 `artifacts/ix-<domain>-cli` | 按 `.claude/rules/artifacts.md` 创建；更新 `artifacts/OVERVIEW.md` 与 `capabilities.md` |
| 需要新 `reports/<type>` | 先给出拟议目录树，用户同意后再创建 `reports/<type>/OVERVIEW.md`，并更新本文件 §2、§4 |
| 删除或重命名已有周期/专题 | 先列出影响（链接、system 路径），再执行 |
| 在根目录新增文件 | 仅允许：`CLAUDE.md`、`VERSION`、`.gitignore`、`.claude/` |
| commit / zap 收尾 | 按 git-workflow.md 当前模式处理（local 不提示 push；remote 可 push） |

---

## 7. 相关文件索引

> 本表仅列出**实际存在**的文件。

### 根与配置

| 文件 | 用途 |
|------|------|
| `.claude/rules/*.md` | 各领域细化规则（import 进本文件记忆），见 `.claude/rules/OVERVIEW.md` 索引 |
| `.claude/settings.json` | permissions（deny/ask）+ PreToolUse/PostToolUse hooks 注册 |
| `.claude/hooks/*.sh` | PreToolUse/PostToolUse 守卫（bash-build/path-guard/sync-trigger/version-reminder/search-reminder） |
| `.gitignore` | 忽略 `.DS_Store`、产物目录、`.env`、`__pycache__/`、`ix-agents/*/runs/` |

### 规范与模板

| 文件 | 用途 |
|------|------|
| `_shared/specs/OVERVIEW.md` | Agent 规范索引 |
| `_shared/specs/capability/capability-spec.spec.md` | SPEC.yaml 字段规范（真相源） |
| `_shared/specs/overview/overview-common.spec.md` | OVERVIEW.md 共性段落 |
| `_shared/specs/overview/overview-bucket.spec.md` | 桶级 OVERVIEW 额外要求 |
| `_shared/specs/overview/overview-index.spec.md` | 索引级 OVERVIEW 额外要求 |
| `_shared/specs/ui-design/design-language-routing.spec.md` | HTML 设计语言选型 |
| `_shared/specs/ui-design/design-language-import.spec.md` | 粘贴 prompt 导入新语言 |
| `_shared/templates/OVERVIEW.md` | 模板索引 |
| `_shared/templates/ix-agents/` | ix-*-agent 母版（manifest / defaults / paths 等） |
| `_shared/templates/design-languages/` | 设计语言 intake / meta / preview 母版 |

### 桶级说明

| 文件 | 用途 |
|------|------|
| `research/OVERVIEW.md` | 专题类型操作说明 |
| `artifacts/OVERVIEW.md` | 小工具桶操作说明 |
| `artifacts/capabilities.md` | **Agent 原子能力索引**（意图/关键词 → ix-*-cli） |
| `ix-agents/OVERVIEW.md` | 组合应用桶说明 |
| `ix-agents/registry.md` | **Agent 组合应用索引**（意图 → ix-*-agent） |
| `ix-gui/OVERVIEW.md` | 框架设施说明（GUI 应用定位 + 零侵入铁律） |
| `_shared/design-languages/OVERVIEW.md` | 设计语言 prompt 索引 |

### 可执行实现

| 文件 | 用途 |
|------|------|
| `artifacts/ix-agent-run-cli/` | 统一执行 manifest（tool + `claude -p` thinking） |
| `artifacts/ix-workspace-index-cli/` | 索引审计：capabilities/registry 与磁盘一致性；能力发现 search |
| `artifacts/ix-init-cli/` | 工作区初始化（git init / GIT_MODE / persona） |
| `artifacts/ix-schedule-cli/` | 跨平台定时执行器（macOS launchd / Windows schtasks） |

---

## 8. 修订记录


| 日期 | 变更 |
|------|------|
| 2026-05 ~ 2026-06 上旬 | 早期演进（详见基线快照） |
| 2026-06-16 | **建立 Claude Code 单平台底座**：`CLAUDE.md` 成为唯一权威；细化规则提取为 `.claude/rules/<domain>.md`，CLAUDE.md 用场景路由表按需加载；硬约束写入 `.claude/settings.json` |
| 2026-06-16（续） | **indexed 基线改造**：品牌前缀 `lc-` → `ix-`、`work-with` → `indexed`；能力发现改为分布式 `SPEC.yaml` + 薄索引；失效登记清除；`README.md` → `SPEC.md` 体系；引入 `VERSION` 版本号 |
| 2026-06-20 | **新增 `ix-gui/` 框架设施**：indexed 的 GUI 应用（Tauri+React）。根目录白名单 + §2 拓扑 + §2.ix-gui 定位 + §5.4.4 豁免；确立「零侵入铁律 + 三边界」，保证 GUI 方式与纯 claude code 方式并存互通。详见 [`ix-gui/OVERVIEW.md`](ix-gui/OVERVIEW.md) |
