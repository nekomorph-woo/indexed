#!/usr/bin/env bash
# Claude Code SessionStart hook：检查 indexed 基线版本
#
# 行为：
#   - 24h 缓存（.indexed-update-check.json，ix-init-cli 内部管理）
#   - 无新版 / 网络失败 / 不在 indexed 工作区 → 静默 exit 0（不阻塞 Claude 启动）
#   - 有新版 → stdout 提示（Claude Code 显示给用户）
#
# 协议：Claude Code SessionStart hook；stdin JSON {cwd}；exit 0（永不阻塞）

set -uo pipefail

# 找到含 CLAUDE.md 的项目根（cwd 上溯）
CWD="$(jq -r '.cwd // empty' 2>/dev/null)"
[ -z "$CWD" ] && CWD="$(pwd)"

PROJECT_ROOT="$CWD"
while [ "$PROJECT_ROOT" != "/" ] && [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; do
  PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done

# 不在 indexed 工作区（无 CLAUDE.md 或无 VERSION）→ 静默
[ ! -f "$PROJECT_ROOT/VERSION" ] && exit 0
[ ! -f "$PROJECT_ROOT/artifacts/ix-init-cli/main.py" ] && exit 0

# 跑 check-update（24h 缓存内置；输出 stdout 给 Claude Code 显示）
cd "$PROJECT_ROOT" && python3 artifacts/ix-init-cli/main.py check-update 2>/dev/null

# 永远 exit 0（即使 check-update 失败也不阻塞 Claude 启动）
exit 0
