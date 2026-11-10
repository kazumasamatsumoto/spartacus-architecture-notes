#!/usr/bin/env bash
# Build the CCv2 repository tree from two independent repos, without merging:
#   maintenance repo (bin/ and config/ at its root, never changed)
#   migration repo   (js-storefront/, core-customize/manifest.json,
#                     core-customize/overlay/  files placed on top of core-customize/hybris/,
#                     core-customize/overlay.lock  "<path> <maintenance blob>" for overlay files
#                                                  that replace a maintenance file)
# usage: assemble-deploy.sh <maint-repo> <maint-ref> <mig-repo> <out-dir>
set -euo pipefail
MAINT=$1 REF=$2 MIG=$3 OUT=$4
H=$OUT/core-customize/hybris
LOCK=$MIG/core-customize/overlay.lock
SHA=$(git -C "$MAINT" rev-parse --verify "$REF^{commit}")

rm -rf "$OUT"; mkdir -p "$H"
git -C "$MAINT" archive "$SHA" | tar -x -C "$H"

# an overlay file that replaces a maintenance file must have been reviewed
# against the maintenance blob that is being deployed now
fail=0
while IFS= read -r f; do
  rel=${f#./}
  now=$(git -C "$MAINT" rev-parse -q --verify "$SHA:$rel" || true)
  locked=$(awk -v p="$rel" '$1==p{print $2}' "$LOCK" 2>/dev/null || true)
  if [ -n "$now" ] && [ "$now" != "$locked" ]; then
    echo "REVIEW: $rel changed in maintenance (${locked:-not locked} -> $now)"; fail=1
  elif [ -z "$now" ] && [ -n "$locked" ]; then
    echo "REVIEW: $rel was deleted in maintenance"; fail=1
  fi
done < <(cd "$MIG/core-customize/overlay" && find . -type f | sort)
[ $fail = 0 ] || { echo "assemble stopped: merge the maintenance change into the overlay, then update overlay.lock"; exit 1; }

cp -R "$MIG/core-customize/overlay/." "$H/"
cp "$MIG/core-customize/manifest.json" "$OUT/core-customize/"
cp -R "$MIG/js-storefront" "$OUT/"
printf 'maintenance %s\nmigration %s\n' "$SHA" "$(git -C "$MIG" rev-parse HEAD)" > "$OUT/DEPLOYED_FROM"
echo "assembled: maintenance ${SHA:0:7} + migration $(git -C "$MIG" rev-parse --short HEAD)"
