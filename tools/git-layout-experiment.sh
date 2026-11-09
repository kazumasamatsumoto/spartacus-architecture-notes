#!/bin/bash
# 26 章 26.3 の実験 G: 移行側でフォルダ構成を変えた(オンプレ構成 hybris/ → CCv2 構成 core-customize/hybris/)とき、保守の変更を取り込めるか
# 使い方: bash tools/git-layout-experiment.sh [作業ディレクトリ]  (省略時は mktemp -d。macOS の sed -i '' を使う)
set -u
W=${1:-$(mktemp -d)}/work; rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_AUTHOR_NAME=dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=dev GIT_COMMITTER_EMAIL=dev@example.com
g(){ git -c init.defaultBranch=main -c core.pager=cat "$@"; }
mk(){ mkdir -p "$(dirname "$1")"; printf '%s\n' "${@:2}" > "$1"; }
F=hybris/bin/custom/xfacades/src/PriceFacade.java
g init -q r; cd r
# 保守側はオンプレ構成(リポジトリ直下に hybris/)
mk $F 'class PriceFacade {' '  int price(int base) {' '    return base;' '  }' '  int tax(int b) {' '    return b / 10;' '  }' '}'
mk hybris/bin/custom/xstorefront/web/src/C.java 'class C {' '  boolean ok(int q){ return q <= 99; }' '}'
mk hybris/config/localextensions.xml '<extensions>' "  <extension name='xfacades'/>" '</extensions>'
g add -A; g commit -qm init; g tag T0
g switch -qc main-work
sed -i '' 's/return base;/return Math.max(base, 0);/' $F; g commit -qam "MNT-101 facade fix"
mk hybris/bin/custom/xfacades/src/NewUtil.java 'class NewUtil {}'; g add -A; g commit -qm "MNT-105 add new file"
echo "=== G1. 移行側で hybris/ → core-customize/hybris/ に移動だけ。保守は旧パスのまま"
g switch -qc mig1 T0; mkdir core-customize; g mv hybris core-customize/; g commit -qm "move to CCv2 layout"; g tag M1
echo "--- G1a 保守が既存ファイルを修正しただけ"
g merge --no-edit main-work~1 2>&1 | grep -E "CONFLICT|Merge made|Already"; g reset -q --hard M1
echo "--- G1b 保守が新しいファイルを追加した"
g merge --no-edit main-work 2>&1 | grep -E "CONFLICT|Merge made|Already"; g merge --abort
echo "=== G2. 移動 + 移行側で Facade の別の行を書き換え"
sed -i '' 's#return b / 10;#return b * 10 / 100;#' core-customize/$F; g commit -qam "MIG edit tax"
g merge --no-edit main-work~1 2>&1 | grep -E "CONFLICT|Merge made|Already"; g show HEAD:core-customize/$F | grep -E 'Math.max|100'
g reset -q --hard M1
echo "=== G3. 移動 + Facade を大きく書き換え"
printf 'class PriceFacade {\n  long price(long b, Ctx c){ return c.round(b); }\n  long tax(long b){ return b*10/100; }\n  long ship(){ return 500; }\n}\n' > core-customize/$F; g commit -qam "MIG rewrite"
g merge --no-edit main-work~1 2>&1 | grep -E "CONFLICT|Merge made|Already"; g merge --abort
echo "--- 同じ状況で -X subtree=core-customize を付けると"
g merge --no-edit -X subtree=core-customize main-work~1 2>&1 | grep -E "CONFLICT|Merge made|Already"; g merge --abort 2>/dev/null
g reset -q --hard M1
echo "=== G4. 移動は保守 main 側で先にやる(upstream first)。移行側はそこからブランチ"
g switch -qc main-moved main-work~2; mkdir core-customize; g mv hybris core-customize/; g commit -qm "MNT-100 move to CCv2 layout (maintenance too)"
g switch -qc mig4
printf 'class PriceFacade {\n  long price(long b, Ctx c){ return c.round(b); }\n}\n' > /dev/null
mk js-storefront/x '1'; g add -A; g commit -qm MIG
g switch -q main-moved; sed -i '' 's/return base;/return Math.max(base, 0);/' core-customize/$F; g commit -qam "MNT-101 facade fix (new path)"
g switch -q mig4; g merge --no-edit main-moved 2>&1 | grep -E 'CONFLICT|Merge made'
