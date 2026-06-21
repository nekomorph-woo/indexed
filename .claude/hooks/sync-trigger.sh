#!/usr/bin/env bash
# PostToolUse: SPEC.yaml/manifest.yaml 落盘后自动 sync 索引。
# 配套：CLAUDE.md §3.4/§3.5（capabilities.md/registry.md 同步机制）
# 协议：Claude Code PostToolUse hook；fail open（sync 失败不阻断 LLM 工作）。

set -uo pipefail

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"

# 仅在 SPEC.yaml 或 manifest.yaml 落盘时触发
case "$FILE_PATH" in
  */SPEC.yaml|*/manifest.yaml)
    # 找到项目根（cwd 上溯到含 CLAUDE.md）
    CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"
    PROJECT_ROOT="$CWD"
    while [ "$PROJECT_ROOT" != "/" ] && [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; do
      PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
    done

    # 仅在工作区内、且 sync CLI 存在时触发
    if [ -f "$PROJECT_ROOT/artifacts/ix-workspace-index-cli/main.py" ]; then
      cd "$PROJECT_ROOT" || exit 0
      # 探测 python 解释器（python3 优先，python 回退）
      PYTHON_BIN="$(command -v python3 || command -v python || true)"
      if [ -z "$PYTHON_BIN" ]; then
        echo "⚠️  未找到 python 解释器，跳过自动 sync" >&2
        exit 0
      fi
      if "$PYTHON_BIN" artifacts/ix-workspace-index-cli/main.py sync >/dev/null 2>&1; then
        echo "💡 已自动 sync 索引（触发：${FILE_PATH##*/}）" >&2
      else
        echo "⚠️  sync 失败，请手动运行：$PYTHON_BIN artifacts/ix-workspace-index-cli/main.py sync" >&2
      fi
    fi
    ;;
esac

exit 0
