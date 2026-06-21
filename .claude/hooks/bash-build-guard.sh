#!/usr/bin/env bash
# Bash 构建命令守卫：ix-gui/ 下放行；其它路径拦截全生态构建命令。
# 配套：CLAUDE.md §2.ix-gui（ix-gui 框架设施豁免）+ §5.4.4（_shared/repos/ 最小存储原则）
# 协议：Claude Code PreToolUse hook；stdin JSON {tool_name, tool_input, cwd}；exit 2 + stderr 拦截。

set -uo pipefail

INPUT="$(cat)"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

# 找到含 CLAUDE.md 的项目根（cwd 上溯）
PROJECT_ROOT="$CWD"
while [ "$PROJECT_ROOT" != "/" ] && [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; do
  PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done

# ix-gui 豁免：在 ix-gui/ 子树内放行所有命令（自有应用设施，可构建）
case "$CWD" in
  "$PROJECT_ROOT/ix-gui"|"$PROJECT_ROOT/ix-gui"/*) exit 0 ;;
esac
# cwd 不在 ix-gui 子树时，检查命令是否明确 cd / --prefix / 路径引用 ix-gui 子树
# （例：`cd ix-gui/web && npm install`、`npm --prefix ix-gui/web install`）
case "$CMD" in
  *"ix-gui/web"*|*"ix-gui/src-tauri"*) exit 0 ;;
esac

# 全生态构建命令禁止清单（_shared/repos/ 最小存储原则）
# 命中即拦截；命令前后必须是空格或字符串边界，避免误伤（如 npm-install.sh 这类文件名）
if printf '%s' "$CMD" | grep -qE '(^|[[:space:]/])(npm install|npm run build|npm ci|pnpm install|pnpm build|pnpm ci|yarn install|yarn build|bun install|bun build|bunx |mvn |./mvnw|gradle |./gradlew|cargo build|cargo run|cargo install|cargo test|rustup install|pip install|pip3 install|pipx install|poetry install|poetry add|uv sync|uv pip|go build|go install|tauri build|tauri dev|flutter build|flutter pub|docker build|docker-compose build|make |cmake |composer install|bundle install|gem install|mix deps|rebar3 compile|deno install|deno bundle|deno compile|swc |esbuild |webpack |rollup |vite build|parcel build)([[:space:]]|$)'; then
  echo "🛑 禁止构建命令（_shared/repos/ 最小存储原则；CLAUDE.md §5.4.4）。ix-gui/ 下豁免。" >&2
  echo "   命令：$CMD" >&2
  exit 2
fi

exit 0
