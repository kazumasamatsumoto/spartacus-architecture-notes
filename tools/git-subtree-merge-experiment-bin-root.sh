#!/bin/bash
# 26 章 26.4 の実験 I: 保守はリポジトリ直下に bin/・config/(= hybris ディレクトリそのもの)、移行は core-customize/hybris/ 配下。接頭辞 2 階層の -X subtree で取り込めるか
# 使い方: bash tools/git-subtree-merge-experiment-bin-root.sh [作業ディレクトリ]  (省略時は mktemp -d。macOS の sed -i '' を使う)
set -u
W=${1:-$(mktemp -d)}/work; rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_AUTHOR_NAME=dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=dev GIT_COMMITTER_EMAIL=dev@example.com
g(){ git -c init.defaultBranch=main -c core.pager=cat -c advice.mergeConflict=false "$@"; }
mk(){ mkdir -p "$(dirname "$1")"; printf '%s\n' "${@:2}" > "$1"; }
res(){ grep -E 'CONFLICT|Merge made|Already|fatal|Fast-forward' | sed 's/^/  /'; }
P=core-customize/hybris
F=bin/custom/xfacades/src/PriceFacade.java
g init -q r; cd r
# 保守側: リポジトリ直下 = hybris ディレクトリ(bin/custom, config)
mk $F 'class PriceFacade {' '  int price(int base) {' '    return base;' '  }' '  int tax(int b) {' '    return b / 10;' '  }' '}'
mk bin/custom/xstorefront/web/webroot/WEB-INF/tags/price.tag '<span>${price}</span>'
mk bin/custom/xold/src/Old.java 'class Old {}'
mk config/localextensions.xml '<extensions>' "  <extension name='xfacades'/>" '</extensions>'
mk config/local.properties 'a=1'
mk .gitignore 'bin/platform/' '*.class'
mk README.md 'maintenance repo'
g add -A; g commit -qm "maint: initial (bin/ and config/ at root)"

echo "### 移行側: 直下を全部 $P/ へ(git mv だけ)"
g switch -qc migration
mkdir -p $P; g mv $(g ls-tree --name-only HEAD) $P/; g commit -qm "MIG-0 move everything into $P/"
g ls-tree -r --name-only HEAD | sed 's/^/  /'
mk core-customize/manifest.json '{"useConfig":{"extensions":{"location":"hybris/config/localextensions.xml"}}}'
mk core-customize/hybris/config/environments/common.properties 'x=1'
mk js-storefront/x 'x'; g add -A; g commit -qm "MIG-1 manifest, environments, js-storefront"
sed -i '' 's#return b / 10;#return b * 10 / 100;#' $P/$F; g commit -qam "MIG-2 facade tax"
g tag MIG

echo; echo "### 保守側の変更"
g switch -q main
sed -i '' 's/return base;/return Math.max(base, 0);/' $F; g commit -qam "MNT-301 modify facade"
mk bin/custom/xnew/src/New.java 'class New {}'; g add -A; g commit -qm "MNT-302 add extension"
g tag MNT-ONLY-ADD; g rm -qr bin/custom/xold; g commit -qm "MNT-303 delete extension"
sed -i '' 's#<span>#<span class="p">#' bin/custom/xstorefront/web/webroot/WEB-INF/tags/price.tag; g commit -qam "MNT-304 tag change"
sed -i '' "s#</extensions>#  <extension name='xnew'/>\n</extensions>#" config/localextensions.xml; sed -i '' 's/a=1/a=2/' config/local.properties; g commit -qam "MNT-305 config"
mk scripts/deploy.sh 'echo'; sed -i '' 's/maintenance repo/maintenance repo v2/' README.md; g add -A; g commit -qm "MNT-306 new top-level dir and README"; g tag MNT

echo; echo "=== I1. 台帳(保守の旧パス)"
g switch -q migration
g log --format='  %h %s' migration..main -- 'bin/custom/*/web/*' '*.jsp' '*.tag' 'config/*.properties' 'config/localextensions.xml'
echo; echo "=== I2. git merge -X subtree=$P"
g merge --no-edit --no-ff -X subtree=$P main 2>&1 | res
echo "  直下:"; g ls-tree --name-only HEAD | sed 's/^/    /'
echo "  全ファイル:"; g ls-files | sed 's/^/    /'
echo "  Facade:"; grep -E 'Math.max|100' $P/$F | sed 's/^/    /'
echo "  localextensions:"; grep xnew $P/config/localextensions.xml | sed 's/^/    /'
echo; echo "=== I3. 接頭辞を core-customize(1 階層)と間違えた場合"
g reset -q --hard MIG; g merge --no-edit --no-ff -X subtree=core-customize main 2>&1 | res; g ls-tree --name-only HEAD | sed 's/^/    直下: /'; g ls-files core-customize | grep -v '^core-customize/hybris/\|manifest.json' | sed 's/^/    core-customize 直下にずれたもの: /'; g merge --abort 2>/dev/null; g reset -q --hard MIG
echo; echo "=== I4. オプションを付け忘れた場合"
g merge --no-edit --no-ff main 2>&1 | res; g ls-files bin scripts README.md | sed 's/^/    直下に出たもの: /'; g merge --abort 2>/dev/null; g reset -q --hard MIG
echo "  (削除を含まない取り込みだと、衝突なしで成功してしまう)"
g merge --no-edit --no-ff MNT-ONLY-ADD 2>&1 | res; g ls-files bin scripts | sed 's/^/    直下に出たもの: /'; g reset -q --hard MIG
echo; echo "=== I5. 切替"
g merge -q --no-edit --no-ff -X subtree=$P main; g switch -q main; g merge --ff-only migration 2>&1 | res; g ls-tree --name-only HEAD | sed 's/^/    main 直下: /'
