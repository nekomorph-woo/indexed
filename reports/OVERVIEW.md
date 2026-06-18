# reports — 周期性报告与交付物

> 完整规范见 [`CLAUDE.md`](../CLAUDE.md) §3、§4、§5、[`.claude/rules/reports.md`](../.claude/rules/reports.md)。

## 目录结构

```
reports/
└── <report-type>/        # 报告类型（kebab-case）
    ├── OVERVIEW.md        # 该类型的说明（新建 <type> 时必建）
    └── <周期或实例>/      # 如 <start>_<end> 或 YYYY-MM-DD_HH-mm
        ├── drafts/        # 中间产物（draft- 前缀）
        └── <final>.md     # 最终交付
```

## 通用约定

- 报告类型名：英文 kebab-case
- 周期目录：`<start>_<end>`（日期 `YYYY-MM-DD`）或时间戳（北京时间）
- 中间产物：`drafts/` 子目录，`draft-` 前缀；**禁止** `tmp-`
- **禁止**在周期目录创建 `system.md`；**禁止**使用 `_pipeline/`
