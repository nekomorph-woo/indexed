# _shared/specs — Agent 规范索引

> 仅放可跨周期复用的规范（`*.spec.md`）；禁止写入单次任务的业务结论。
> 规范：[`CLAUDE.md`](../../CLAUDE.md) §3.7

## 现有规范

| 类别 | 文件 | 说明 |
|------|------|------|
| 能力声明（SPEC.yaml） | `capability/capability-spec.spec.md` | ix-*-cli / ix-*-agent 的 SPEC.yaml 字段规范；scanner 真相源 |
| UI 设计语言路由 | `ui-design/design-language-routing.spec.md` | HTML 选型；prompt 在 `_shared/design-languages/` |
| UI 设计语言导入 | `ui-design/design-language-import.spec.md` | 粘贴 prompt → 新建 `design-languages/<id>/` |

## 新增 spec 类别

1. 在 `_shared/specs/<category>/` 新建 `*.spec.md`
2. 更新本索引表
3. 更新 CLAUDE.md §3.7
