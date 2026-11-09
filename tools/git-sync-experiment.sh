#!/bin/bash
# 26 章の実験: 保守ブランチ(main)の変更を移行側へ取り込めるかを、小さな hybris 風リポジトリで確かめる
# 使い方: bash tools/git-sync-experiment.sh [作業ディレクトリ]  (省略時は mktemp -d。macOS の sed -i '' を使う)
set -u
W=${1:-$(mktemp -d)}/work; rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_AUTHOR_NAME=dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=dev GIT_COMMITTER_EMAIL=dev@example.com
g(){ git -c init.defaultBranch=main -c core.pager=cat -c advice.mergeConflict=false "$@"; }
C=core-customize/hybris
LX=$C/config/localextensions.xml
FAC=$C/bin/custom/xfacades/src/PriceFacade.java
mk(){ mkdir -p "$(dirname "$1")"; printf '%s\n' "${@:2}" > "$1"; }
addext(){ sed -i '' "s#</extensions>#  <extension name='$1'/>\n</extensions>#" $LX; }
maint(){ # 保守開発の 2 コミット
  sed -i '' 's/return base;/return Math.max(base, 0);/' $FAC
  g commit -qam "MNT-101 fix negative price in PriceFacade"
  sed -i '' 's#<span>${price}</span>#<span class="price">${price} JPY</span>#' $C/bin/custom/xstorefront/web/webroot/WEB-INF/tags/price.tag
  sed -i '' 's/q <= 99/q <= 50/' $C/bin/custom/xstorefront/web/src/CartPageController.java
  g commit -qam "MNT-102 show currency, max qty 50 (storefront only)"
}
g init -q hybris; cd hybris
mk $LX '<extensions>' "  <extension name='xcore'/>" "  <extension name='xfacades'/>" "  <extension name='xstorefront'/>" '</extensions>'
mk $FAC 'class PriceFacade {' '  int price(int base) {' '    return base;' '  }' '}'
mk $C/bin/custom/xstorefront/web/webroot/WEB-INF/tags/price.tag '<%-- price --%>' '<span>${price}</span>'
mk $C/bin/custom/xstorefront/web/src/CartPageController.java 'class CartPageController {' '  boolean ok(int q){ return q <= 99; }' '}'
g add -A; g commit -qm "initial"; g tag T0; cd ..

echo "=== A. 同じリポジトリで migration ブランチを切る"
cd hybris; g switch -qc migration
mk js-storefront/manifest.json '{"applications":[{"name":"xstore","path":"xstore"}]}'
mk js-storefront/xstore/src/app/price.component.ts 'export class PriceComponent {}'
mk $C/bin/custom/xocc/src/PriceController.java 'class PriceController { /* calls PriceFacade */ }'
addext xocc
g add -A; g commit -qm "MIG-1 add js-storefront and xocc"
g switch -q main; maint
echo "--- 保守 main に MNT-103(拡張追加)。移行側も同じ末尾に xocc を足している"
addext xpromo; g commit -qam "MNT-103 add xpromo extension"
g switch -q migration
echo "--- 取り込み前の移植台帳: migration にまだ無い保守コミットのうち web 層を触ったもの"
g log --format='%h %s' migration..main -- "$C/bin/custom/*/web/*" '*.jsp' '*.tag'
echo "--- merge main -> migration"
g merge --no-edit main 2>&1 | grep -E 'CONFLICT|Merge made'; g merge --abort
cd ..

echo; echo "=== A'. 同じ状況で、xocc の追加を先に保守 main へ入れておいた場合(upstream first)"
rm -rf hybris2; g clone -q hybris hybris2; cd hybris2
g switch -qc main2 T0; addext xocc; mk $C/bin/custom/xocc/src/PriceController.java 'class PriceController {}'
g add -A; g commit -qm "MNT-090 add xocc (OCC only, unused by accelerator)"
g switch -qc migration2
mk js-storefront/manifest.json '{"applications":[]}'; g add -A; g commit -qm "MIG-1 add js-storefront"
g switch -q main2; maint; addext xpromo; g commit -qam "MNT-103 add xpromo extension"
g switch -q migration2; g merge --no-edit main2 2>&1 | grep -E 'CONFLICT|Merge made'
echo "--- migration 側から見た Facade の履歴(保守のハッシュのまま)"
g log --format='%h %s' -- $FAC
echo "--- main2 の MNT-101 のハッシュ"; g log -1 --format='%h %s' --grep MNT-101 main2
cd ..

echo; echo "=== B. 履歴なしでコピーした別リポジトリ(T0 時点のスナップショット)"
mkdir copied; (cd hybris && g archive T0) | tar -x -C copied; cd copied; g init -q; g add -A; g commit -qm "snapshot of hybris"
mk js-storefront/manifest.json '{}'; g add -A; g commit -qm "MIG-1"
g remote add upstream ../hybris2; g fetch -q upstream
g merge --no-edit upstream/main2 2>&1 | tail -1
echo "--- --allow-unrelated-histories"
g merge --no-edit --allow-unrelated-histories upstream/main2 2>&1 | grep CONFLICT
g merge --abort; cd ..

echo; echo "=== C. 履歴ごと複製した別リポジトリ(clone / mirror push)"
g clone -q hybris2 forked
(cd hybris2 && g switch -q main2 && sed -i '' 's/q <= 50/q <= 40/' $C/bin/custom/xstorefront/web/src/CartPageController.java && sed -i '' 's/Math.max(base, 0)/Math.max(base, 1)/' $FAC && g commit -qam "MNT-104 min price 1 / max qty 40")
cd forked; g switch -q migration2; g fetch -q origin
g merge --no-edit origin/main2 2>&1 | grep -E 'CONFLICT|Merge made|Already'
echo "--- 取り込んだ MNT-104 のハッシュ(元リポジトリと同じ)"; g log -1 --format='%h %s' --grep MNT-104; (cd ../hybris2 && g log -1 --format='%h %s' main2)
cd ..

echo; echo "=== D. 移行側でディレクトリを移動した場合"
cd hybris2; g switch -qc moved T0
g mv core-customize backend; g commit -qm "move core-customize -> backend"
g switch -qc main3 T0; maint; g switch -q moved
echo "--- 移動だけなら rename 検出で追従"
g merge --no-edit main3 2>&1 | grep -E 'CONFLICT|Merge made'; g reset -q --hard HEAD~1
echo "--- 移動と同時に中身も書き換えると追従できない"
printf 'class PriceFacade {\n  long price(long b, Ctx c){\n    // rewritten for OCC\n    return c.round(b);\n  }\n  long tax(long b){ return b/10; }\n}\n' > backend/hybris/bin/custom/xfacades/src/PriceFacade.java
g commit -qam "rewrite facade"
g merge --no-edit main3 2>&1 | grep -E 'CONFLICT|Merge made'; g merge --abort 2>/dev/null
cd ..

echo; echo "=== E. cherry-pick で拾った後に merge すると"
cd hybris2; g switch -qc pick T0
mk js-storefront/a '1'; g add -A; g commit -qm MIG
g cherry-pick main3~1 >/dev/null 2>&1; g log -1 --format='%h %s'
g merge --no-edit main3 2>&1 | grep -E 'CONFLICT|Merge made'
echo "--- 同じ変更が別ハッシュで 2 つある"; g log --format='%h %s' --grep MNT-101
cd ..
echo; echo "=== F. 移行側で storefront 拡張を先に消した場合"
cd hybris2; g switch -qc deleted T0
g rm -rq $C/bin/custom/xstorefront; g commit -qm "remove xstorefront early"
g merge --no-edit main3 2>&1 | grep -E 'CONFLICT|Merge made'; g merge --abort 2>/dev/null
