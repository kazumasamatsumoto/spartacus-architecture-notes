#!/bin/bash
# 保守ブランチを移行ブランチへ取り込む(26 章 26.4)
#   保守 = リポジトリ直下に bin/・config/(現行構成のまま)
#   移行 = core-customize/hybris/ 配下(CCv2 構成)
# 使い方: sync-maintenance.sh <保守の ref>   例: sync-maintenance.sh origin/main
set -eu
PREFIX=core-customize/hybris
ALLOWED_ROOT='^(core-customize|js-storefront)$'          # 移行側のリポジトリ直下に置いてよい名前
ALLOWED_CC='^(hybris|manifest\.json)$'                    # core-customize/ 直下に置いてよい名前
LEDGER_PATHS=('bin/custom/*/web/*' '*.jsp' '*.tag' '*.tld' 'config/*.properties' 'config/localextensions.xml')   # 保守の旧パスで書く

check(){
  local bad
  bad=$(git ls-tree --name-only HEAD | grep -Ev "$ALLOWED_ROOT" || true)
  [ -z "$bad" ] || { echo "NG: リポジトリ直下に想定外: $bad(-X subtree の付け忘れ、または保守側の新しいトップレベル)"; return 1; }
  bad=$(git ls-tree --name-only HEAD:core-customize | grep -Ev "$ALLOWED_CC" || true)
  [ -z "$bad" ] || { echo "NG: core-customize/ 直下に想定外: $bad(接頭辞の間違い)"; return 1; }
  echo "OK: 直下と core-customize/ 直下は想定どおり"
}
[ "${1:-}" = --check ] && { check; exit $?; }
[ "$(git rev-parse --abbrev-ref HEAD)" = migration ] || { echo "migration ブランチで実行する"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "作業ツリーが汚れている"; exit 1; }
SRC=${1:?保守の ref を指定}

echo "== 移植台帳(今回入る保守コミットのうち、web 層と設定を触ったもの)"
git --no-pager log --no-merges --format='%h %ad %s' --date=short "HEAD..$SRC" -- "${LEDGER_PATHS[@]}"

echo "== git merge --no-ff -X subtree=$PREFIX $SRC"
if ! git merge --no-ff --no-edit -X "subtree=$PREFIX" "$SRC"; then
  echo "衝突を解いて commit したあと、$0 --check で確認する"; exit 1
fi
check
