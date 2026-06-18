# reports — 周期性报告与交付物

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §3、§4、§5。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 报告目录结构

```
reports/
└── <report-type>/        # 报告类型（kebab-case）
    ├── OVERVIEW.md       # 该类型的说明（新建 <type> 时必建）
    └── <周期或实例>/      # 如 <start>_<end> 或 YYYY-MM-DD_HH-mm
        ├── drafts/        # 中间产物（draft- 前缀）
        └── <final>.md     # 最终交付
```

## 通用约定

| 项 | 约定 |
|----|------|
| 报告类型名 | 英文 kebab-case（如 `team-usage`） |
| 周期目录 | `<start>_<end>`（日期 `YYYY-MM-DD`）或时间戳 `YYYY-MM-DD_HH-mm`（北京时间） |
| 中间产物 | `drafts/` 子目录，`draft-` 前缀；**禁止** `tmp-` 前缀 |
| 周期变量 | 若需每期变量，放 `variable.md`；`检索时间` 与周期目录名一致 |
| 最终报告 | 周期目录根；命名见各类型 spec |

## 新建报告类型

1. 先与用户确认拟议目录树
2. 创建 `reports/<type>/OVERVIEW.md`
3. 更新 CLAUDE.md §2 目录树、§4 决策树
4. 按需在 `_shared/specs/<category>/` 建 spec、`_shared/templates/<category>/` 建母版
5. 跑 `python artifacts/ix-workspace-index-cli/main.py audit --check`（确认桶级 OVERVIEW 一致性）

## 新建一期报告

1. 建 `reports/<type>/<周期>/drafts/`
2. 中间产物只写入 `drafts/`
3. 合并为最终报告，放周期目录根

## 禁止

- 在周期目录创建 `system.md`
- 使用 `reports/<type>/_pipeline/`（已废弃）
- 在 `reports/` 内 `git clone`
