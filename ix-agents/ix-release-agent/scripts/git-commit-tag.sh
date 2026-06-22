#!/usr/bin/env bash
# git commit + tag v<version>
# 用法：bash git-commit-tag.sh <version>
# 调用方：ix-release-agent git_commit_tag step

set -euo pipefail

VERSION="$1"
[ -z "$VERSION" ] && { echo "[error] 用法: git-commit-tag.sh <version>"; exit 1; }

cd "$(git rev-parse --show-toplevel)"

# git add（不 add runs/ 等运行时产物，由 .gitignore 控制）
git add -A

# commit（如无变化则跳过）
if git diff --cached --quiet; then
  echo "[git-commit-tag] 无变化需要 commit"
else
  git commit -m "release: v${VERSION}"
fi

# tag（如已存在则跳过）
if git rev-parse "v${VERSION}" >/dev/null 2>&1; then
  echo "[git-commit-tag] tag v${VERSION} 已存在（跳过）"
else
  git tag "v${VERSION}"
  echo "[git-commit-tag] ✓ tag v${VERSION} created"
fi
