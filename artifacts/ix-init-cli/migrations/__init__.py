"""ix-init-cli migrations package.

每个 migration 脚本命名：`<VERSION_FROM>_to_<VERSION_TO>.py`（如 `0.1.0_to_0.2.0.py`）。

统一接口（每个 migration 必须实现）：

    VERSION_FROM: str                          # 源版本（如 "0.1.0"）
    VERSION_TO: str                            # 目标版本（如 "0.2.0"）
    describe() -> str                          # 返回 changelog 说明
    check(workspace_root: Path) -> list[str]   # 前置检查（dry-run，受影响文件清单）
    migrate(workspace_root: Path) -> list[str] # 执行迁移（变更说明）
    verify(workspace_root: Path) -> list[str]  # 自验证（空 list = 通过）

ix-init-cli update 通过 `compute_migration_chain(cur, new)` 计算从 cur 到 new 的
migration 链（必须连续，不允许缺环），顺序跑 check → 用户确认 → migrate → verify。

migration 失败时中止整个 update；已跑的 migration 记录到 .indexed-migrations.log，
重跑 update 时跳过已记录的（基于 VERSION_FROM → VERSION_TO 配对去重）。
"""
