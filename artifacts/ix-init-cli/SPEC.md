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

## 个性化（昵称 / 称呼）

init 时设置助手昵称（默认 `Xi酱`）和对用户称呼（默认 `您`），写入 CLAUDE.md 的 `IX_PERSONA` 标记区。AI 读 CLAUDE.md 时自然看到，用于个性化交互。

## 基线更新（update）

```bash
# 下载新版本 zip → 解压 → 更新
python artifacts/ix-init-cli/main.py update /path/to/indexed-new
```

update 的行为：
- **标记区文件保护**：capabilities.md / registry.md / 桶 README / CLAUDE.md / git-workflow.md → 抽取用户标记区 → 覆盖 → 回灌（不丢用户内容）
- **框架文件覆盖**：.claude/rules/、_shared/、基线 3 个 ix-*-cli、VERSION、.gitignore
- **用户内容跳过**：research/、reports/、用户自建 cli/agent、_shared/repos/
- 完成后建议跑 `ix-workspace-index-cli sync` 同步索引

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
