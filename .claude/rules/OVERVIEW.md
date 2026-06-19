# .claude/rules — 各领域细化规则索引

本目录存放 indexed 工作区**各领域细化规则**，是从 [`CLAUDE.md`](../../CLAUDE.md) 各章节提取整理而来，与 CLAUDE.md 一致、不冲突。

## 记忆机制

CLAUDE.md 用「场景路由表」指向下列规则文件。Claude Code 自动加载 rules 目录；ZCode 等按场景路由按需 Read 对应规则。

## 规则文件

| 文件 | 领域 | 来源（CLAUDE.md 章节） | 备注 |
|------|------|------------------------|------------------------|
| [`00-core.md`](00-core.md) | 核心原则、目录拓扑、禁止项、根目录白名单 | §1、§2、§2.1、§6 | indexed-core、workspace-readmes |
| [`naming.md`](naming.md) | 命名规范、桶级 README | §3.1、§3.1.1 | workspace-readmes |
| [`shared-repos.md`](shared-repos.md) | Git 仓库浅克隆、禁止构建、产物清理 | §5.5 | shared-repos |
| [`reports.md`](reports.md) | 周期性报告目录结构与通用约定 | §3、§4、§5 | — |
| [`research.md`](research.md) | 专题调研、图示规范 | §3.4、§5.2 | — |
| [`artifacts.md`](artifacts.md) | ix-*-cli 命名、骨架、新建清单、capabilities 发现 | §3.5、§5.3 | artifacts、artifacts-discovery |
| [`ix-agents.md`](ix-agents.md) | manifest 编排、run-cli、runs 隔离、发现、定时约束 | §3.6、§5.4 | ix-agents、ix-agents-discovery、ix-agent、ix-agents-schedule |
| [`specs-templates.md`](specs-templates.md) | specs / templates 治理、skill 去重与两阶段 | §3.7、§3.8、§5.6、§5.9、§5.10、§5.11 | skills-invocation-dedup、skills-two-phase |
| [`design-languages.md`](design-languages.md) | 设计语言库、选型、导入 | §3.11 | ui-design-languages、design-language-import |
| [`git-workflow.md`](git-workflow.md) | Git 模式（local/remote）、版本号、工作区配置 | §6 | 由 ix-init-cli 初始化 |
| [`dialogue-style.md`](dialogue-style.md) | 简体中文回复、ASCII 线框图、图示规范、任务规划 | §1（简体中文）、§3.8（图示） | dialogue-style、coding-conventions |

## 维护原则

- 本目录规则**源自** CLAUDE.md，是其在各领域的细化展开；若两者出现冲突，以 [`CLAUDE.md`](../../CLAUDE.md) 为准。
- 新增领域规则时：在本表补一行，并在 CLAUDE.md 场景路由表补对应行。
- 文件名：英文 kebab-case，`<nn>-<domain>.md`（前两位数字用于阅读排序）。
- **禁止**在本目录写入单次任务的业务结论；规则须可跨周期复用。
