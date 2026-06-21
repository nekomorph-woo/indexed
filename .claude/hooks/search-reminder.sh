#!/usr/bin/env bash
# PreToolUse: 新建 ix-*-cli/SPEC.yaml 或 ix-*-agent/manifest.yaml 时提醒先跑 search。
# 配套：CLAUDE.md §5 前置检查 + .claude/rules/artifacts.md §能力发现
# 协议：纯提醒（exit 0），不阻塞 LLM 创建文件。

set -uo pipefail

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"

# 仅在新建 cli 的 SPEC.yaml 或 agent 的 manifest.yaml 时触发
case "$FILE_PATH" in
  */artifacts/ix-*-cli/SPEC.yaml|*/ix-agents/ix-*-agent/manifest.yaml)
    cat >&2 <<'EOF'
⚠️ 即将新建 cli/agent。规则要求（CLAUDE.md §5 前置检查）：新建前必须先跑能力发现，避免重复造轮子：

    python artifacts/ix-workspace-index-cli/main.py search "<意图关键词>"

- 若 search 返回已有能力 → 扩展该 cli 的 providers/ 或该 agent 的 config/，不新建目录
- 若 search 无匹配 → 继续新建，并在 commit message 注明「search 无匹配，确认新建」
EOF
    ;;
esac

exit 0
