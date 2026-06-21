#!/usr/bin/env bash
# PostToolUse: CLAUDE.md / .claude/rules/*.md 落盘后提醒递增 VERSION + 更新 §8 修订记录。
# 配套：.claude/rules/git-workflow.md §版本号 + CLAUDE.md §8 修订记录
# 协议：Claude Code PostToolUse hook；纯提醒，不阻断。

set -uo pipefail

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"

case "$FILE_PATH" in
  */CLAUDE.md)
    cat >&2 <<'EOF'
💡 已修改 CLAUDE.md（权威规范）。请评估是否递增 VERSION：
   - 主版本号：结构性变更（桶拓扑/规范范式重构）
   - 次版本号：能力新增（新 spec/rule/cli 模板）
   - 修订号：修复订正
   并同步 CLAUDE.md §8 修订记录。详见 .claude/rules/git-workflow.md §版本号。
EOF
    ;;
  */.claude/rules/*.md)
    echo "💡 已修改 .claude/rules/。若涉及规范演进，请同步检查 VERSION 与 CLAUDE.md §8 修订记录。" >&2
    ;;
esac

exit 0
