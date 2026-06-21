#!/usr/bin/env bash
# 路径守卫：拦截中文目录名、越界路径、根目录白名单违规。
# 配套：CLAUDE.md §2.1（禁止项）+ §6（协作边界：根目录新增文件）
# 协议：Claude Code PreToolUse hook；stdin JSON {tool_name, tool_input, cwd}；exit 2 + stderr 拦截。

set -uo pipefail

# IX_GUI_ENABLED=1：开发仓库 + .app baseline（CLI/GUI 用户都装了 GUI 框架设施）
# IX_GUI_ENABLED=0：CLI-only 包打包时 sed 改（CLI 用户工作区不含 ix-gui/）
IX_GUI_ENABLED=1

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"

# 无 file_path（理论上不会发生，但兜底）
[ -z "$FILE_PATH" ] && exit 0

# 系统配置路径豁免（Claude Code 内置：plans/projects/rules/memory/teams/tasks/plugins 等）
# 这些路径不属于 indexed 工作区，path-guard 不约束
case "$FILE_PATH" in
  "$HOME/.claude/"*) exit 0 ;;
  /tmp/*) exit 0 ;;
esac

CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"

# 找到含 CLAUDE.md 的项目根（cwd 上溯）
PROJECT_ROOT="$CWD"
while [ "$PROJECT_ROOT" != "/" ] && [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; do
  PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done

deny() {
  echo "🛑 $1" >&2
  echo "   路径：$FILE_PATH" >&2
  exit 2
}

# 1. 中文目录/文件名检测（CJK 统一表意文字 U+4E00-U+9FFF，UTF-8 字节序列 e4-e9 + 80-bf + 80-bf）
if printf '%s' "$FILE_PATH" | LC_ALL=C grep -qE $'[\xe4-\xe9][\x80-\xbf][\x80-\xbf]'; then
  deny "禁止中文目录/文件名（CLAUDE.md §3.1：仅允许英文 kebab-case）"
fi

# 2. 越界检测：必须在项目根内（允许 PROJECT_ROOT 本身及子树）
case "$FILE_PATH" in
  "$PROJECT_ROOT"|"$PROJECT_ROOT"/*) ;;
  *) deny "禁止越界写入（不在工作区 $PROJECT_ROOT 内）" ;;
esac

# 3. 根目录白名单：直接子项仅允许 5 桶 + (ix-gui/?) + .claude/ + 元文件 + 临时 _findings.md
REL="${FILE_PATH#$PROJECT_ROOT}"
# 去掉前导 /
REL="${REL#/}"

# 若 REL 不含 /，说明是根目录直接文件
if [ "${REL}" = "${REL%%/*}" ]; then
  case "${REL}" in
    CLAUDE.md|VERSION|.gitignore|_findings.md|.indexed-baseline-version|.indexed-migrations.log|.indexed-update-check.json|README-cli.md) ;;
    *) deny "禁止在根目录新建文件: ${REL} (白名单: CLAUDE.md/VERSION/.gitignore + .claude/ + 5 桶)" ;;
  esac
else
  # 取一级子目录，根据 IX_GUI_ENABLED 决定 ix-gui 是否算合法桶
  TOP="${REL%%/*}"
  if [ "$IX_GUI_ENABLED" = "1" ]; then
    case "${TOP}" in
      _shared|reports|research|artifacts|ix-agents|ix-gui|.claude|.git) ;;
      *) deny "禁止在根目录新建桶: ${TOP}/ (仅允许 _shared/reports/research/artifacts/ix-agents/ix-gui/.claude/)" ;;
    esac
  else
    case "${TOP}" in
      _shared|reports|research|artifacts|ix-agents|.claude|.git) ;;
      *) deny "禁止在根目录新建桶: ${TOP}/ (仅允许 _shared/reports/research/artifacts/ix-agents/.claude/)" ;;
    esac
  fi
fi

exit 0
