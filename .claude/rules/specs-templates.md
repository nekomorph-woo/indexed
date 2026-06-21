# specs-templates — 规范、模板与 Skill 治理

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §3.6、§3.7、§5.5、§5.6、§5.7、§5.8。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## Agent 规范 `_shared/specs/`

spec 目录 **只放规范**；禁止在 spec 上直接填写某次评审的业务结论。

| 类型 | 文件 | 说明 |
|------|------|------|
| UI 设计语言路由 | `ui-design/design-language-routing.spec.md` | HTML 选型 |
| UI 设计语言导入 | `ui-design/design-language-import.spec.md` | 粘贴 prompt → 新建 `<id>/` |

**新增 spec 类别**：
1. 在 `_shared/specs/<category>/` 新建 `*.spec.md`
2. 更新 `_shared/specs/OVERVIEW.md` 与 CLAUDE.md §3.6
3. 配套 skill 须符合下方「两阶段」；rule 见本文件 §两阶段
4. **不强制**该子目录单独 `OVERVIEW.md`（见 `naming.md`）

## 文档模板 `_shared/templates/`

| 类型 | 模板文件 | 说明 |
|------|----------|------|
| 设计语言导入 | `design-languages/design-language-intake.template.md` | 粘贴外部 prompt |
| 设计语言元数据 | `design-languages/meta.template.md` | 导入产出 `meta.md` 结构参考 |
| ix-*-agent 母版 | `ix-agents/manifest.template.yaml` 等 | 新建 `ix-agents/ix-<business>-agent/` |

**新增模板类别**：
1. 在 `_shared/templates/<category>/` 新建 `*.template.md`
2. 更新 `_shared/templates/OVERVIEW.md` 与 CLAUDE.md §3.7
3. 若需专用 rule，在 `.claude/rules/` 增加指向该目录的说明
4. **不强制**该子目录单独 `OVERVIEW.md`（见 `naming.md`）

## 修改跨周期规范

- **Spec / 示例**：在 `_shared/specs/<category>/` 维护；**禁止**写入当期 draft/定稿。
- **模板**：在 `_shared/templates/<category>/` 维护。
- 周期报告**不再**使用 `reports/<type>/_pipeline/` 或每期 `system.md`。

## Skill 去重

同名 skill + command **只执行 skill 定义**；不重复跑 command。slash 由 skill 承接。

## Skill 两阶段（必选）

凡新增或改版 skill，**必须**实现：

| 阶段 | 要求 |
|------|------|
| **A** | `/name` 且无齐全输入时：列 `_shared/repos/`（若涉及 Git）→ 给**可复制模板** → **停止** |
| **B** | 用户粘贴模板或一次给齐输入 → Read spec → 自动建目录/文件 → 产出 |

- 在 skill 顶部 `description` 写明两阶段。
- 参考实现：`ix-agent`。

### 现有 skill 齐全输入速查

| Skill | 阶段 B 齐全输入 |
|-------|-----------------|
| `ix-agent` | 新建：`动作：新建` + `business`；执行：`动作：执行` + `agent` |
