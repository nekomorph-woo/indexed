# indexed 框架审查 Findings

> **生成**：2026-06-21
> **方法**：4 个 subagent 并行审查（规则矛盾 / LLM 执行断裂 / 驱动能力 / harness 自愈）的交叉验证合并
> **范围**：整个 indexed 工作区，**不含 `ix-gui/`**
> **性质**：**临时审查产物**，逐一解决后应删除或归档到 `research/framework-audit/`
> **⚠️ 根目录白名单 exception**：本文件位于根目录（白名单仅 `CLAUDE.md`/`VERSION`/`.gitignore`/`.claude/` + 5 工作桶 + `ix-gui/`），属于 meta-work 临时产物，**解决完后请删除**

---

## 进度追踪表

| ID | 严重度 | 简述 | 状态 |
|----|--------|------|------|
| P0-1 | 🔴 high | deny 全局裸命令，ix-gui 被误伤 | ✅ |
| P0-2 | 🔴 high | deny 清单不全（漏 pip/cargo/tauri/yarn/pnpm/deno/swc） | ✅ |
| P0-3 | 🔴 high | deny 只挡 Bash，Write/Edit 无拦截 | ✅ |
| P1-1 | 🟠 high | ix-gui 在 §6/00-core/git-workflow 全部漏同步 | ✅ |
| P1-2 | 🟡 medium | 术语漂移：桶/工作桶/业务桶/框架设施 | ✅ |
| P1-3 | 🟡 medium | §3 章节编号断裂（3.2/3.3/3.9/3.10 缺） | ✅ |
| P1-4 | 🟡 medium | §5 章节编号断裂（5.1/5.7/5.8 缺） | ✅ |
| P2-1 | 🔴 high | 零 PreToolUse/PostToolUse hooks | ✅ |
| P2-2 | 🟡 medium | audit 只查 4 项静态治理 | ✅ |
| P2-3 | 🟡 medium | runs 产出零反哺、零可观测性 | ✅ |
| P2-4 | 🟡 medium | sync/audit/VERSION 全是被动 invoked | ✅ |
| P3-1 | 🟠 high | 两阶段流程的「停止」无机器兜底 | ⬜ |
| P3-2 | 🟠 high | §6 vs §5.4 协作边界自相矛盾 | ⬜ |
| P3-3 | 🟠 high | search 必须先跑——反 LLM 默认 | ⬜ |
| P3-4 | 🟡 medium | 禁自动选用设计语言——反 LLM 默认 | ⬜ |
| P3-5 | 🟡 medium | 「用户明确要求才做 X」无判定标准 | ⬜ |
| P3-6 | 🟡 medium | skill「待迁移」状态模糊 | ⬜ |
| P4-1 | 🟠 medium | 业务样本为零（0 user cli、0 agent） | ⬜ |
| P4-2 | 🟡 medium | §7 文件索引漏列严重 | ⬜ |
| P4-3 | 🟠 high | §3.7 spec 类别登记滞后（capability/、overview/） | ⬜ |
| P4-4 | 🟢 low | registry.md L40 仍写「README.md」 | ⬜ |
| P5-1 | 🟡 medium | 根目录 README.md 仍存在但 §8 说已迁移 | ⬜ |
| P5-2 | 🟡 medium | _shared/design-references/ 零规则提及 | ⬜ |
| P5-3 | 🟡 medium | templates/ix-agents/OVERVIEW.md 与 §3.1.1 矛盾 | ⬜ |
| P5-4 | 🟡 medium | 场景路由表触发词重叠 | ⬜ |
| P5-5 | 🟡 medium | §4 决策树前两个分支文本重复 | ⬜ |
| P5-6 | 🟢 low | research.md sync 步骤未在 §5.3/§5.4 主清单 | ⬜ |
| P5-7 | 🟢 low | §2 拓扑树 research 块缩进错位 | ⬜ |
| P5-8 | 🟢 low | .claude/rules/OVERVIEW.md 残留 workspace-readmes 标签 | ⬜ |
| P5-9 | 🟢 low | 模板无 new 子命令脚手架 | ⬜ |

---

## P0 · 机器层承诺与文本层承诺直接冲突（ix-gui 必炸）

### ✅ P0-1 settings.json deny 全局裸命令，与 §5.5.4「ix-gui 豁免」直接矛盾
**命中 4 次**（维度 1/2/3 独立得出同样结论，可信度极高）

- **声称**：CLAUDE.md §2.ix-gui + §5.5.4 注脚「deny 规则不含 ix-gui/ 路径」「ix-gui 可 cargo build/npm install/tauri dev」
- **实际**：`.claude/settings.json` 全是 `Bash(npm install:*)` 这种**无路径前缀的纯命令模式**，全局生效
- **后果**：用户按规则在 `ix-gui/web/` 下跑 `npm install` 会被自己的硬约束拦截，整个 GUI 开发流水线启动即崩
- **修复方向**：改为路径限定模式（如 cwd-not-in 或 allow-in 二级规则）

### ✅ P0-2 deny 清单不全，_shared/repos/ 仍可漏过构建
- §5.5.4 表格漏了 `pip install`、`cargo build`、`tauri dev`、`pnpm install`、`yarn install`、`deno`、`swc` 等
- deny 是枚举式不是策略式，跟不上生态

### ✅ P0-3 deny 只挡 Bash，Write/Edit/MultiEdit 全程无拦截
- LLM 用 Write 工具直接写中文目录名 / 根目录新建 `projects/` —— 完全零拦截

---

## P1 · ix-gui 引入后的系统性漂移（主文件承认、细化文件按五桶写）

### ✅ P1-1 根目录白名单在 5 处互相打架

| 位置 | 是否承认 ix-gui/ |
|------|-----------------|
| CLAUDE.md §1 L43 / §2 / §2.ix-gui | ✅ |
| CLAUDE.md §6「根目录新增文件」 | ❌ 漏 |
| `.claude/rules/00-core.md` L14/L30 | ❌ 漏 |
| `.claude/rules/git-workflow.md` L41/L51 | ❌ 漏 |
| CLAUDE.md §8「框架设施桶」 | 用词不一致 |

**后果**：路由命中 00-core.md 时，LLM 会判定 ix-gui/ 是非法桶

### ✅ P1-2 术语漂移：「桶」「工作桶」「业务桶」「框架设施」「框架设施桶」
LLM 在分类判断时无依据，是 P1-1 的根因

### ✅ P1-3 §3 章节编号断裂
§3.1.1 → §3.4（缺 3.2/3.3）；§3.8 → §3.11（缺 3.9/3.10）
**命中 2 次**。LLM 易误判规范不完整或自己补编造

### ✅ P1-4 §5 工作流编号断裂
§5 缺 5.1、5.7、5.8。但 §5 标题写「必须按序执行」——LLM 会去找 5.1 在哪

---

## P2 · harness 三层全部缺失（纸面治理）

### ✅ P2-1 零 PreToolUse/PostToolUse hooks（最致命裸奔点）
- `.claude/settings.json` **无 hooks 段**，无 `.claude/hooks/`、无 `.github/`、无 pre-commit
- 所有"违规检测→反馈→修复"闭环都是软约束文字

### ✅ P2-2 audit 只查 4 项静态治理
**命中 2 次**。当前 `audit_governance` 检查：关键词重复、CLAUDE.md 行数、§交叉引用、桶级 README 存在性

**检测不到**：中文目录名、根目录白名单违规、SPEC.yaml 字段类型错误、命名违规、`tmp-` 前缀、产物生成

### ✅ P2-3 runs/<run-id>/ 产出零反哺、零可观测性
- runs 在 `.gitignore`，run.yaml 只被 --resume 读，无聚合统计
- agent 反复失败无人知晓；capabilities 是否真被复用无从度量；"search 跳过直接造轮子"完全不可检测

### ✅ P2-4 sync/audit/VERSION 全是被动 invoked
- 无 commit hook、无定时任务、规则未硬性要求落盘后必跑
- SPEC.yaml 改了不跑 sync → 薄索引长期漂移

---

## P3 · LLM 执行断裂点（规则 vs LLM 默认行为）

### ☐ P3-1 两阶段流程的「停止」无机器兜底
**命中 2 次**（维度 2 high + 维度 4 high 零 hooks 根因）
- §5.4 阶段 A 要求"展示需求→**停止**"，但 LLM 默认倾向是"完成任务"
- 没有任何 hook 在展示 params 后阻止 LLM 直接 --set 跑掉

### ☐ P3-2 §6 vs §5.4 协作边界自相矛盾
- §6 表格：「Shell run --agent...；收集缺失 params」← 倾向直接跑+遇错补参
- §5.4：「执行前必读两阶段，先停」← 倾向先停问

### ☐ P3-3 search 必须先跑——反 LLM 默认
- LLM 默认倾向 `ls artifacts/` 或 `grep capabilities.md`，**不会主动跑 Python CLI 做意图搜索**
- 且"找不到该新建"的相似度阈值未定义

### ☐ P3-4 禁自动选用设计语言——反 LLM 默认
LLM 写 HTML 时默认会"挑一个合适的"，规则要求"罗列库+邀请预览+等用户确认"是强反默认，无机器兜底

### ☐ P3-5 「用户明确要求才做 X」无判定标准
ix-agents.md 禁主动归档，但"明确要求"的阈值未定义

### ☐ P3-6 skill「待迁移」状态模糊
规则多处说"skill 尚未迁移为 .claude/skills/"，但 §5.11 又讲 skill 两阶段，场景路由表也指 specs-templates.md。LLM 不知道当前 skill 到底存不存在

---

## P4 · 驱动能力异常点（基础设施可信、业务实例零样本）

### ☐ P4-1 业务样本为零（最关键 gap）
**命中 2 次**（维度 3 medium + 维度 4 medium 同根因）
- artifacts/ 只有 4 个框架 cli（run/index/workspace/schedule），**零业务 cli**
- ix-agents/ 下**零个业务 agent 目录**，`audit` 显示「0 agent」
- 两阶段交互、thinking 产出校验、sync 首次写入都未走过实战

### ☐ P4-2 §7 文件索引自称「只列实际存在的文件」但漏列严重
- 漏列 `_shared/specs/capability/`、`_shared/specs/overview/`（已存在）
- 漏列 `ix-gui/`、`ix-init-cli`、`ix-schedule-cli`

### ☐ P4-3 §3.7 spec 类别登记滞后于磁盘
只登记 ui-design，实际有 capability/、overview/ 两个类别 4 个 spec 文件未登记

### ☐ P4-4 registry.md L40 仍写「更新 README.md」（应为 OVERVIEW.md）
SPEC vs README 迁移本身干净，但 registry 残留旧术语

---

## P5 · 其他漂移与断裂

### ☐ P5-1 根目录 README.md 仍存在但 §8 说已迁移到 SPEC.md，且不在白名单
LLM 不知该删该留

### ☐ P5-2 _shared/design-references/ 目录存在但零规则提及
LLM 可能误判为未跟踪产物尝试清理

### ☐ P5-3 _shared/templates/ix-agents/OVERVIEW.md 实际存在但 §3.1.1 说"templates 子目录非强制"
规则与实际不一致，LLM 可能误判该 OVERVIEW 非法并尝试删除

### ☐ P5-4 场景路由表触发词重叠
「新建文件」同时命中 00-core+naming+research；「两阶段/params」过于宽泛会误命中

### ☐ P5-5 §4 决策树前两个分支文本几乎一字不差
"周期性交付" vs "其它周期性交付"——LLM 困惑

### ☐ P5-6 research.md sync 步骤未在 §5.3/§5.4 主清单
按 CLAUDE.md 主清单走会漏跑 sync

### ☐ P5-7 §2 拓扑树 research 块缩进错位
4 空格 vs 其他桶 2 空格 → ASCII 树视觉断裂

### ☐ P5-8 .claude/rules/OVERVIEW.md 残留 workspace-readmes 旧标签

### ☐ P5-9 模板无 new 子命令脚手架
business 占位符全靠手改

---

## 最致命的 3 个根因（修这些能同时收敛一大片 finding）

### 🔴 根因 1：deny 用了「全局裸命令」而非「路径限定」模式
**一次修复可收敛**：P0-1、P0-2、P0-3、P1-1 部分

settings.json 应改为路径限定模式（如 `Bash(npm install:*):cwd-not-in:ix-gui/**`），让 ix-gui 真正豁免、_shared/repos 真正全生态覆盖

### 🔴 根因 2：零 PreToolUse/PostToolUse hooks
**一次引入可收敛**：P2-1、P2-2 部分、P3-1、P3-3、P3-4、P5-1

至少需要三类 hook：
- `PreToolUse(Write/Edit/MultiEdit)` 校验路径（白名单、命名、桶归属）
- `PreToolUse(Bash)` 拦截构建命令
- `PostToolUse` 在落盘 SPEC.yaml 后自动 sync

### 🔴 根因 3：ix-gui 漂移是一次未完成的规范同步
**一次同步可收敛**：P1-1、P1-2、P1-3、P1-4、P4-2、P4-3、P5-1/2/3/5/6/8

§8 修订记录说「2026-06-20 新增 ix-gui 框架设施桶」，但规范同步只走到 CLAUDE.md §1/§2 就停了——§3、§6、§7、所有 .claude/rules/、settings.json 全部未跟上。这是一次**半截子的规范演进**

---

## 其他独立建议

- **P4-1 业务样本为零**：建议先建一个 end-to-end 示例 agent（如 `ix-echo-agent` 或 `ix-team-usage-agent`），把两阶段流程、thinking、sync、audit 四条链路实战跑通一次——当前是「实现但未被业务验证」状态
- **P3-2 §6 vs §5.4 协作边界矛盾**：把 §6 表格「执行 ix-agent」一行改写为「**先 Read manifest params，按两阶段流程执行**」，与 §5.4 对齐
- **P3-6 skill 状态**：明确「当前态」一段——「skill 暂不可用，遇到 skill 需求时按 CLAUDE.md §5 流程而非 .claude/skills/」
