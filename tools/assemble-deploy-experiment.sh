#!/usr/bin/env bash
# Experiment K: no merge at all. Maintenance repo and migration repo stay independent;
# tools/assemble-deploy.sh builds the CCv2 tree and a deploy repo records each build.
set -euo pipefail
T=$(cd "$(dirname "$0")" && pwd)
W=${1:-$(mktemp -d)}; rm -rf "$W"; mkdir -p "$W"; cd "$W"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
g(){ git -c init.defaultBranch=main "$@"; }
hr(){ echo; echo "=== $* ==="; }
deploy(){ "$T/assemble-deploy.sh" "$W/maint" main "$W/mig" "$W/out" || return 1
  rsync -a --delete --exclude .git "$W/out/" "$W/deploy/"
  git -C "$W/deploy" add -A; git -C "$W/deploy" commit -qm "deploy $1"; echo "deploy commit: $(git -C "$W/deploy" log -1 --format='%h %s')"; }

g init -q maint; cd maint
mkdir -p bin/custom/shop/src bin/custom/shop/web/webroot config
printf 'class Facade {\n  a();\n  b();\n  c();\n}\n' > bin/custom/shop/src/Facade.java
echo '<p>cart</p>' > bin/custom/shop/web/webroot/cart.jsp
echo '<ext name="shop"/>' > config/localextensions.xml
git add -A; git commit -qm "M0"; cd ..

g init -q mig; cd mig
mkdir -p js-storefront core-customize/overlay/bin/custom/migocc core-customize/overlay/bin/custom/shop/src
echo '{}' > js-storefront/manifest.json
echo '{"extensions":["migocc"],"useConfig":{"extensions":{"location":"hybris/config/localextensions.xml"}}}' > core-customize/manifest.json
echo occ > core-customize/overlay/bin/custom/migocc/Occ.java
printf 'class Facade {\n  a(); // +occ\n  b();\n  c();\n}\n' > core-customize/overlay/bin/custom/shop/src/Facade.java
echo "bin/custom/shop/src/Facade.java $(git -C ../maint rev-parse main:bin/custom/shop/src/Facade.java)" > core-customize/overlay.lock
git add -A; git commit -qm "MIG-1"; cd ..
g init -q deploy

hr "K1 first assembly"
deploy K1
(cd deploy && find . -path ./.git -prune -o -type f -print | sort); cat deploy/DEPLOYED_FROM

hr "K2 maintenance changes files the migration does not replace"
cd maint; echo '<p>cart v2</p>' > bin/custom/shop/web/webroot/cart.jsp
mkdir -p bin/custom/newext; echo n > bin/custom/newext/N.java
echo '<ext name="shop"/><ext name="newext"/>' > config/localextensions.xml
git add -A; git commit -qm "M1"; cd ..
deploy K2; git -C deploy --no-pager diff --stat HEAD~1 HEAD

hr "K3 maintenance changes a file the migration replaces"
cd maint; sed -i '' 's/  c();/  c(); \/\/ fix/' bin/custom/shop/src/Facade.java; git commit -qam "M2 fix in Facade"; cd ..
deploy K3 || echo "(deploy stopped, nothing committed: $(git -C deploy log -1 --format=%s))"

hr "K4 migration reviews: takes the maintenance fix into the overlay and updates the lock"
cd mig
git -C ../maint --no-pager diff HEAD~1 HEAD -- bin/custom/shop/src/Facade.java | sed -n '/^@@/,$p'
sed -i '' 's/  c();/  c(); \/\/ fix/' core-customize/overlay/bin/custom/shop/src/Facade.java
echo "bin/custom/shop/src/Facade.java $(git -C ../maint rev-parse main:bin/custom/shop/src/Facade.java)" > core-customize/overlay.lock
git commit -qam "MIG-2 take M2 into Facade overlay"; cd ..
deploy K4; cat deploy/core-customize/hybris/bin/custom/shop/src/Facade.java

hr "K5 deploy history: which maintenance commit is in each deploy"
git -C deploy --no-pager log --format='%h %s'
git -C deploy --no-pager log --format='%h' -1 | xargs -I{} git -C deploy show {}:DEPLOYED_FROM
