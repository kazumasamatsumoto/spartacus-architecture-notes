#!/usr/bin/env bash
# Experiment J: maintenance repo is never changed (bin/ and config/ at its root).
# Migration lives in a separate repo with core-customize/hybris + js-storefront,
# created by `git subtree add`, synced by `git subtree pull`, and sends backend
# changes back with `git subtree split`.
set -euo pipefail
W=${1:-$(mktemp -d)}; rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
g(){ git -c init.defaultBranch=main "$@"; }
P=core-customize/hybris
hr(){ echo; echo "=== $* ==="; }

# --- maintenance repo (layout never changes) ---
g init -q maint; cd maint
mkdir -p bin/custom/shop/src bin/custom/shop/web/webroot bin/custom/old config
printf 'class Facade {\n  a();\n  b();\n  c();\n}\n' > bin/custom/shop/src/Facade.java
echo '<p>cart</p>' > bin/custom/shop/web/webroot/cart.jsp
echo 'old' > bin/custom/old/a.txt
echo 'x=1' > config/local.properties
echo '<ext name="shop"/>' > config/localextensions.xml
echo readme > README.md
git add -A; git commit -qm "M0 initial"; git tag M0
cd ..

hr "J1 migration repo: git subtree add (maintenance repo untouched)"
g init -q mig; cd mig
git commit -q --allow-empty -m "MIG-root"
git remote add maint ../maint; git fetch -q maint
git subtree add -q --prefix=$P maint main
mkdir -p js-storefront; echo '{}' > js-storefront/manifest.json
echo '{"extensions":["migocc"]}' > core-customize/manifest.json
mkdir -p $P/bin/custom/migocc; echo occ > $P/bin/custom/migocc/Occ.java
git add -A; git commit -qm "MIG-1 storefront + manifest + migration-only extension"
# migration also edits a maintenance-owned file (line a)
sed -i '' 's/  a();/  a(); \/\/ +occ/' $P/bin/custom/shop/src/Facade.java
git commit -qam "MIG-2 Facade change needed by OCC"
git ls-tree --name-only HEAD; git ls-tree --name-only HEAD core-customize/
echo "maint repo files:"; git -C ../maint ls-tree -r --name-only main
cd ..

hr "J2 maintenance keeps working in its own layout"
cd maint
sed -i '' 's/  c();/  c(); \/\/ fix/' bin/custom/shop/src/Facade.java
echo '<p>cart v2</p>' > bin/custom/shop/web/webroot/cart.jsp
mkdir -p bin/custom/newext; echo n > bin/custom/newext/N.java
git rm -q -r bin/custom/old
echo 'x=2' > config/local.properties
mkdir scripts; echo s > scripts/deploy.sh
git add -A; git commit -qm "M1 maintenance release"; git tag M1
cd ..

hr "J3 migration: git subtree pull"
cd mig; git fetch -q maint
echo "ledger (maintenance paths):"
git --no-pager log --no-merges --format='%h %s' main..maint/main -- 'bin/custom/*/web/*' 'config/*'
git subtree pull -q --prefix=$P maint main -m "sync M1"
git --no-pager diff --stat HEAD~1 HEAD
echo "root:"; git ls-tree --name-only HEAD
echo "Facade:"; cat $P/bin/custom/shop/src/Facade.java
test ! -e $P/bin/custom/old && echo "old removed: yes"
cd ..

hr "J4 upstream: migration-side backend change goes back to maintenance layout"
cd mig
git subtree split -q --prefix=$P -b upstream
git --no-pager log --format='%h %s' -3 upstream
echo "paths in upstream tip:"; git ls-tree -r --name-only upstream | head -20
cd ../maint
git fetch -q ../mig upstream:from-mig
git switch -q -c feature/occ main
git merge -q --no-edit from-mig
echo "maintenance root after merging from-mig:"; git ls-tree --name-only HEAD
git --no-pager diff --stat main HEAD
cd ..

hr "J5 upstream only the chosen commit: format-patch --relative + am"
cd mig
C=$(git log --format=%H --grep='^MIG-2' -1)
git format-patch -q -1 "$C" --relative=$P --stdout > ../mig2.patch
grep '^diff --git' ../mig2.patch
cd ../maint
git switch -q main
git am -q -3 ../mig2.patch
git --no-pager log --format='%h %s' -1; git --no-pager diff --stat HEAD~1 HEAD
cd ..

hr "J6 next subtree pull after maintenance released the upstreamed change"
cd maint; echo '<p>cart v3</p>' > bin/custom/shop/web/webroot/cart.jsp; git commit -qam "M3 release"; cd ..
cd mig; git fetch -q maint
git subtree pull -q --prefix=$P maint main -m "sync M3" >/dev/null 2>&1 && echo "pull: clean" || { echo "pull: conflict"; git diff --name-only --diff-filter=U; }
cat $P/bin/custom/shop/src/Facade.java
cd ..

hr "J7 same-line conflict (both sides edit line b)"
cd mig; sed -i '' 's/  b();/  b(); \/\/ mig/' $P/bin/custom/shop/src/Facade.java; git commit -qam "MIG-3 line b"; cd ..
cd maint; sed -i '' 's/  b();/  b(); \/\/ maint/' bin/custom/shop/src/Facade.java; git commit -qam "M4 line b"; cd ..
cd mig; git fetch -q maint
git subtree pull -q --prefix=$P maint main -m "sync M4" 2>&1 | grep CONFLICT || true
git diff --name-only --diff-filter=U
git checkout -q --theirs $P/bin/custom/shop/src/Facade.java; git commit -qam "sync M4 (resolved)"
cd ..

hr "J8 history visible on migration side"
cd mig
git --no-pager log --format='%h %s' -- $P/bin/custom/shop/web/webroot/cart.jsp bin/custom/shop/web/webroot/cart.jsp
echo "blame:"; git --no-pager blame -s $P/bin/custom/shop/web/webroot/cart.jsp
