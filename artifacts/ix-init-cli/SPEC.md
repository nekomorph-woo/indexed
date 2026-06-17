# ix-init-cli — SPEC

> indexed 工作区初始化器。机器可读能力声明见 [`SPEC.yaml`](SPEC.yaml)。

indexed 作为基线交付给真实用户时，用户需要选定自己的 Git 模式。本 CLI 交互式完成：

1. **`git init`**（若尚未初始化）
2. **改写 `.claude/rules/git-workflow.md`** 的 `IX_GIT_MODE` 标记区，设为 `local` 或 `remote`
3. **remote 模式**可选配置远端 URL（`git remote add origin`）

## 用法

```bash
# 交互式（推荐首次使用）
python artifacts/ix-init-cli/main.py init

# 直接指定模式
python artifacts/ix-init-cli/main.py init --mode local
python artifacts/ix-init-cli/main.py init --mode remote --remote-url git@github.com:user/indexed.git

# 查看当前状态
python artifacts/ix-init-cli/main.py status
```

## 两种模式

| 模式 | 行为 |
|------|------|
| `local` | 纯本地版本库；commit 后不提示 push |
| `remote` | 含远端；commit 后可 push；需配置 origin |

## 标记区机制

`git-workflow.md` 内有：

```
<!-- IX_GIT_MODE_BEGIN -->
**当前模式：`uninitialized`**
...
<!-- IX_GIT_MODE_END -->
```

本 CLI 只替换标记区**之间**的内容，文件其余部分不动。可重复运行切换模式。

## 依赖

无第三方依赖（纯 Python 标准库）。
