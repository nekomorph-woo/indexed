# shared-repos — Git 仓库：最小存储 · 只读

> **来源**：[`CLAUDE.md`](../../CLAUDE.md) §5.4。本文件是其细化展开，冲突时以 CLAUDE.md 为准。

## 目标

`_shared/repos/` 仅用于 `git log` / `checkout` / `diff` 等读操作（如使用统计报告），**不是**开发构建环境。

## 路径与去重

1. 目标路径仅：`_shared/repos/<repo-kebab>/`
2. 已存在同远程仓库 → 只 `fetch` / `checkout`，**禁止**重复 clone
3. 目录名必须符合 `naming.md` 的仓库映射表

## Clone（首次）

默认使用浅克隆，减少 `.git` 与检出体积：

```bash
git clone --depth 1 --single-branch --branch <默认分支> <url> _shared/repos/<repo-kebab>
```

- 需分析多个分支：在同一 clone 上 `git fetch origin <分支名>:<分支名> --depth 1`，再 `checkout`；仍不要 `clone --mirror` 或全历史
- 超大仓库且只需部分路径：可选用 `git sparse-checkout`，须先与用户确认范围

## 更新（已存在）

```bash
cd _shared/repos/<repo-kebab>
git fetch origin <branch> --depth 1
git checkout <branch>
```

- 优先 `fetch --depth 1`；避免 `git pull` 拉全量历史
- 禁止：`git fetch --unshallow`、`git clone --mirror`、无 `--depth` 的完整历史同步（除非用户明确要求且说明磁盘影响）

## 禁止的构建与产物（硬约束）

**不得执行**（含但不限于；已写入 `.claude/settings.json` 的 deny 权限）：

| 生态 | 禁止命令示例 |
|------|----------------|
| Java/Maven | `mvn compile` / `package` / `install` / `verify` |
| Java/Gradle | `gradle build` / `assemble` |
| Node | `npm install` / `npm run build` / `pnpm build` / `yarn` |
| Go | `go build` |
| 其它 | `docker build`、`make`、`./mvnw`、`./gradlew` |

**不得故意生成或保留**本地构建产物目录/文件，例如：

`target/`、`build/`、`dist/`、`out/`、`node_modules/`、`.gradle/`、`*.jar`、`*.war`、`*.class`（工作区检出中的已跟踪源码除外）

## 误生成产物的清理

若发现上述目录（且为未跟踪或本地生成）：

1. **不要**先跑构建去「验证」
2. 在仓库根执行：`git clean -fdX`（仅删除 ignore 规则内的文件）或手动删除明确为产物的目录
3. 向用户简要说明删除了哪些路径

## 与报告流水线的关系

报告统计仅需 **Git 历史与 numstat**，**不需要**也不应为了报告而编译项目。若缺少依赖导致无法「理解」某段代码，用阅读源码与 `git show`，不要 `mvn install`。
