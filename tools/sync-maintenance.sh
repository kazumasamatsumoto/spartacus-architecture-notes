#!/bin/bash
# 保守ブランチを移行ブランチへ取り込む(保守 = 現行構成、移行 = core-customize/ 配下)
# 使い方: sync-maintenance.sh <保守の ref>   例: sync-maintenance.sh origin/main
set -eu
SRC=${1:?保守の ref を指定}
PREFIX=core-customize
ALLOWED_ROOT='^(core-customize|js-storefront|README\.md|\.github)$'   # 移行側のルート直下に置いてよい名前
WEB_PATHS=('hybris/bin/custom/*/web/*' '*.jsp' '*.tag' '*.tld' 'hybris/config/*.properties')

[ "$(git rev-parse --abbrev-ref HEAD)" = migration ] || { echo "migration ブランチで実行する"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "作業ツリーが汚れている"; exit 1; }

echo "== 移植台帳(保守の旧パスで、今回入る web 層・設定の変更)"
git --no-pager log --format='%h %ad %s' --date=short "HEAD..$SRC" -- "${WEB_PATHS[@]}"

echo "== merge -X subtree=$PREFIX $SRC"
git merge --no-ff --no-edit -X "subtree=$PREFIX" "$SRC" || { echo "衝突を解いて commit したあと、もう一度このスクリプトの確認部分を流す"; exit 1; }

echo "== 確認: ルート直下に許可していない名前が無いこと"
bad=$(git ls-tree --name-only HEAD | grep -Ev "$ALLOWED_ROOT" || true)
[ -z "$bad" ] || { echo "ルート直下に想定外: $bad  (-X subtree の付け忘れか、保守側の新しいトップレベル)"; exit 1; }
echo OK
