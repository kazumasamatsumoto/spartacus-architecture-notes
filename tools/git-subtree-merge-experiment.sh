#!/bin/bash
# 26 章 26.4 の実験 H: 保守は現行構成(直下に hybris/)のまま、移行は core-customize/ 配下で開発するとき、保守の変更を -X subtree で取り込めるか
# 使い方: bash tools/git-subtree-merge-experiment.sh [作業ディレクトリ]  (省略時は mktemp -d。macOS の sed -i '' を使う)
set -u
W=${1:-$(mktemp -d)}/work; rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_AUTHOR_NAME=dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=dev GIT_COMMITTER_EMAIL=dev@example.com
g(){ git -c init.defaultBranch=main -c core.pager=cat -c advice.mergeConflict=false "$@"; }
mk(){ mkdir -p "$(dirname "$1")"; printf '%s\n' "${@:2}" > "$1"; }
res(){ grep -E 'CONFLICT|Merge made|Already|fatal' | sed 's/^/  /'; }
F=hybris/bin/custom/xfacades/src/PriceFacade.java
g init -q r; cd r
mk $F 'class PriceFacade {' '  int price(int base) {' '    return base;' '  }' '  int tax(int b) {' '    return b / 10;' '  }' '}'
mk hybris/bin/custom/xstorefront/web/src/C.java 'class C {' '  boolean ok(int q){ return q <= 99; }' '}'
mk hybris/bin/custom/xold/src/Old.java 'class Old {}'
mk hybris/config/localextensions.xml '<extensions>' "  <extension name='xfacades'/>" "  <extension name='xstorefront'/>" '</extensions>'
mk hybris/config/local.properties 'a=1' 'b=2'
mk .gitignore '*.class'
mk build/deploy-onprem.sh 'echo deploy'
g add -A; g commit -qm "maint: initial (current layout)"

echo "### 移行側: 構成変更だけのコミット(中身は変えない)"
g switch -qc migration
mkdir core-customize; g mv hybris build .gitignore core-customize/; g commit -qm "MIG-0 move everything into core-customize/ (git mv only)"
g ls-tree --name-only HEAD | sed 's/^/  root: /'
mk js-storefront/x 'x'; mk core-customize/manifest.json '{}'; g add -A; g commit -qm "MIG-1 add js-storefront and manifest.json"
sed -i '' 's#return b / 10;#return b * 10 / 100;#' core-customize/$F; g commit -qam "MIG-2 change tax() in facade"
g tag MIG

echo; echo "### 保守側: 色々な変更"
g switch -q main
sed -i '' 's/return base;/return Math.max(base, 0);/' $F; g commit -qam "MNT-201 modify facade"
mk hybris/bin/custom/xnew/src/New.java 'class New {}'; mk hybris/bin/custom/xfacades/src/Util.java 'class Util {}'; g add -A; g commit -qm "MNT-202 add new extension and new file"
g rm -q -r hybris/bin/custom/xold; g commit -qm "MNT-203 delete xold"
g mv hybris/bin/custom/xstorefront/web/src/C.java hybris/bin/custom/xstorefront/web/src/CartController.java; g commit -qm "MNT-204 rename controller"
sed -i '' 's/echo deploy/echo deploy v2/' build/deploy-onprem.sh; sed -i '' 's/\*.class/*.class\n*.log/' .gitignore; g commit -qam "MNT-205 change root-level files"
g tag MNT

echo; echo "=== H1. 素の git merge(オプションなし)"
g switch -q migration; g merge --no-edit main 2>&1 | res
echo "  ルート直下に hybris/ ができたか:"; g ls-files hybris | head -3 | sed 's/^/    /'; g ls-files -u | cut -f2 | sort -u | sed 's/^/    unmerged: /'
g merge --abort 2>/dev/null; g reset -q --hard MIG

echo; echo "=== H2. git merge -X subtree=core-customize"
g merge --no-edit -X subtree=core-customize main 2>&1 | res
echo "  ルート直下の hybris/ (空なら正しい):"; g ls-files hybris | sed 's/^/    /'
echo "  結果のファイル:"; g ls-files core-customize | sed 's/^/    /'
echo "  Facade の中身(両方の変更):"; grep -E 'Math.max|100' core-customize/$F | sed 's/^/    /'
echo "  .gitignore:"; cat core-customize/.gitignore | sed 's/^/    /'
g tag H2

echo; echo "=== H3. 2 回目の取り込み(保守がさらに変更)"
g switch -q main; sed -i '' 's/a=1/a=10/' hybris/config/local.properties; g commit -qam "MNT-206 property"; g switch -q migration
g merge --no-edit -X subtree=core-customize main 2>&1 | res; cat core-customize/hybris/config/local.properties | sed 's/^/    /'
echo "  2 回目以降をオプションなしで merge してしまうと:"
g switch -q main; mk hybris/bin/custom/xnew2/src/N.java 'class N {}'; g add -A; g commit -qm "MNT-207 add xnew2"; g switch -q migration
g tag BEFORE_H3b; g merge --no-edit main 2>&1 | res; g ls-files hybris | sed 's/^/    root に出たファイル: /'; g merge --abort 2>/dev/null; g reset -q --hard BEFORE_H3b
g merge --no-edit -X subtree=core-customize main 2>&1 | res

echo; echo "=== H4. 両側が同じ行を変更"
g switch -q main; sed -i '' 's/b=2/b=3/' hybris/config/local.properties; g commit -qam "MNT-208 b=3"
g switch -q migration; sed -i '' 's/b=2/b=99/' core-customize/hybris/config/local.properties; g commit -qam "MIG-3 b=99"
g merge --no-edit -X subtree=core-customize main 2>&1 | res
echo "  衝突の解決(ここでは移行側を採用)して commit"; g checkout -q --ours core-customize/hybris/config/local.properties; g add -A; g commit -q --no-edit; g log -1 --format='    %h %s'

echo; echo "=== H5. 移行側が保守のファイルを削除済み(build/deploy-onprem.sh)で、保守がそれを変更"
g rm -q core-customize/build/deploy-onprem.sh; g commit -qm "MIG-4 drop onprem script"
g switch -q main; sed -i '' 's/v2/v3/' build/deploy-onprem.sh; g commit -qam "MNT-209 deploy v3"; g switch -q migration
g merge --no-edit -X subtree=core-customize main 2>&1 | res; g merge --abort

echo; echo "=== H6. 履歴の見え方(移行ブランチ上)"
echo "  新パスだけで log:"; g log --format='    %h %s' -- core-customize/$F
echo "  旧パスと新パスの両方で log:"; g log --format='    %h %s' -- $F core-customize/$F
echo "  移植台帳(保守の旧パスで web 層): MNT のうち migration に未取り込みのもの"
g switch -q main; mk hybris/bin/custom/xstorefront/web/webroot/p.tag 'x'; g add -A; g commit -qm "MNT-210 tag change"; g switch -q migration
g log --format='    %h %s' migration..main -- 'hybris/bin/custom/*/web/*' '*.jsp' '*.tag'
echo "  取り込み後の確認: ルート直下に保守の旧パスが無いこと"; g ls-files -- hybris build .gitignore | wc -l | sed 's/^ */    件数: /'
echo "  blame(保守の行が保守のコミットに帰属するか):"; g blame -s core-customize/$F | sed 's/^/    /' | head -4

echo; echo "=== H7. 切替: 最後に取り込んでから、保守 main を migration へ進める"
g reset -q --hard HEAD; g merge --abort 2>/dev/null
g merge --no-edit -X subtree=core-customize main 2>&1 | res
g ls-files -u | cut -f2 | sort -u | while read f; do g rm -q "$f"; done; g commit -q --no-edit 2>/dev/null
g switch -q main; g merge --ff-only migration 2>&1 | grep -E 'Fast-forward|fatal' | sed 's/^/  /'
g ls-tree --name-only HEAD | sed 's/^/  main のルート: /'
