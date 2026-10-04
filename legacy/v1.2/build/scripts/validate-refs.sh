#!/bin/bash
# Scans image refs "subfolder\name.png" across ALL of layout/theme1 (subdirectories included) that do NOT
# exist in litegui/theme1.
# NOTE: the Blaze stock ALREADY has ~42 dangling refs and boots anyway -> the player TOLERATES a missing
# PNG (it does not draw it, it does not crash). A missing ref = absent icon (cosmetic), NOT a boot loop.
# The real soft-brick gate is layout syntax (re-parse on the device). That is why this check only fails
# on NEW missing refs relative to the stock baseline (= cosmetic regression to review).
#   --record : saves the dangling set of the stock baseline (called by 00-baseline.sh)
#   (default): compares the current set against the baseline; fails (exit 1) if there are NEW ones.
set -uo pipefail
export LC_ALL=C
WS="$(cd "$(dirname "$0")/../.." && pwd)"        # <repo>/legacy/v1.2
LG="$WS/theme/theme_port/litegui/theme1"
LY="$WS/theme/theme_port/layout/theme1"
BASE="$WS/theme/baseline-missing-refs.txt"
cur="$WS/theme/missing-refs.txt"

# unique refs referenced by the layout that do not exist in litegui
{ while IFS= read -r -d '' f; do
    grep -oE '"[^"]+\.(png|jpg|jpeg|gif)"' "$f" | tr -d '"' | sed 's#\\\\#/#g; s#\\#/#g'
  done < <(find "$LY" -type f -print0); } | sort -u | while read -r ref; do
    [ -z "$ref" ] && continue
    [ -f "$LG/$ref" ] || echo "$ref"
  done | sort -u > "$cur"

if [ "${1:-}" = "--record" ]; then
  cp "$cur" "$BASE"; echo "dangling-ref baseline: $(wc -l < "$BASE") (tolerated by the player)"; exit 0
fi

[ -f "$BASE" ] || { echo "missing baseline-missing-refs.txt (run 00-baseline.sh)"; exit 2; }
new="$WS/theme/new-missing-refs.txt"
comm -23 "$cur" <(sort -u "$BASE") > "$new"
n=$(wc -l < "$new"); tot=$(wc -l < "$cur"); b=$(wc -l < "$BASE")
if [ "$n" -gt 0 ]; then
  echo "FAIL: $n NEW missing refs (cosmetic regression); total dangling=$tot (baseline=$b)"; cat "$new"; exit 1
fi
echo "validate-refs OK: 0 new missing refs (tolerated dangling=$tot, baseline=$b)"
