#!/usr/bin/env bash
# 创建 GitHub Release：上传 tar.gz + .dmg + changelog（从 git log 生成）
# 用法：bash github-release.sh <version>
# 调用方：ix-release-agent github_release step

set -euo pipefail

VERSION="$1"
[ -z "$VERSION" ] && { echo "[error] 用法: github-release.sh <version>"; exit 1; }

cd "$(git rev-parse --show-toplevel)"

# 检查 gh CLI
if ! command -v gh >/dev/null 2>&1; then
  echo "[error] 未找到 gh CLI。请装 GitHub CLI 或手动创建 Release。"
  echo "        下载：https://cli.github.com/"
  exit 1
fi

# 检查登录状态
if ! gh auth status >/dev/null 2>&1; then
  echo "[error] gh 未登录。请跑 gh auth login。"
  exit 1
fi

# 找产物
TARBALL=$(ls artifacts/ix-bundle-cli/output/indexed-cli-${VERSION}.tar.gz 2>/dev/null | head -1 || true)
DMG=$(ls ix-gui/src-tauri/target/release/bundle/dmg/indexed_${VERSION}_*.dmg 2>/dev/null | head -1 || true)

if [ -z "$TARBALL" ]; then
  echo "[error] tarball 缺失：artifacts/ix-bundle-cli/output/indexed-cli-${VERSION}.tar.gz"
  echo "        跑 ix-bundle-cli cli-bundle 或 ix-release-agent --set skip_bundle=false"
  exit 1
fi
if [ -z "$DMG" ]; then
  echo "[error] dmg 缺失：ix-gui/src-tauri/target/release/bundle/dmg/indexed_${VERSION}_*.dmg"
  echo "        跑 tauri build 或 ix-release-agent --set skip_bundle=false"
  exit 1
fi

# 生成 changelog（从上一个 tag 到 v<version>）
PREV_TAG=$(git describe --tags --abbrev=0 "v${VERSION}^" 2>/dev/null || echo "")
CHANGELOG_FILE=$(mktemp)
trap 'rm -f "$CHANGELOG_FILE"' EXIT

if [ -n "$PREV_TAG" ]; then
  git log "${PREV_TAG}..v${VERSION}" --pretty=format:"- %s" > "$CHANGELOG_FILE"
else
  git log "v${VERSION}" --pretty=format:"- %s" -n 50 > "$CHANGELOG_FILE"
fi

# 创建 release
gh release create "v${VERSION}" \
  --title "v${VERSION}" \
  --notes-file "$CHANGELOG_FILE" \
  "$TARBALL" \
  "$DMG"

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "nekomorph-woo/indexed")
echo "[github-release] ✓ v${VERSION} released"
echo "  tarball: $TARBALL"
echo "  dmg: $DMG"
echo "  url: https://github.com/${REPO}/releases/tag/v${VERSION}"
