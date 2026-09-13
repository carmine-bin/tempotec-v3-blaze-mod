#!/bin/bash
# Escanea refs de imagen "subcarpeta\nombre.png" en TODO layout/theme1 (subdirs incluidos) que NO existan
# en litegui/theme1.
# NOTA: el stock del Blaze YA tiene ~42 refs colgantes y bootea igual -> el player TOLERA un PNG faltante
# (no lo dibuja, no crashea). Una ref faltante = ícono ausente (cosmético), NO boot-loop. El gate real de
# soft-brick es la sintaxis del layout (re-parse en device). Por eso este check falla solo ante refs
# faltantes NUEVAS respecto al baseline stock (= regresión cosmética a revisar).
#   --record : guarda el set colgante del baseline stock (lo llama 00-baseline.sh)
#   (default): compara el set actual contra el baseline; falla (exit 1) si hay NUEVAS.
set -uo pipefail
export LC_ALL=C
WS="$(cd "$(dirname "$0")/../.." && pwd)"        # <repo>
LG="$WS/theme/theme_port/litegui/theme1"
LY="$WS/theme/theme_port/layout/theme1"
BASE="$WS/theme/baseline-missing-refs.txt"
cur="$WS/theme/missing-refs.txt"

# refs únicas referenciadas por layout que no existen en litegui
{ while IFS= read -r -d '' f; do
    grep -oE '"[^"]+\.(png|jpg|jpeg|gif)"' "$f" | tr -d '"' | sed 's#\\\\#/#g; s#\\#/#g'
  done < <(find "$LY" -type f -print0); } | sort -u | while read -r ref; do
    [ -z "$ref" ] && continue
    [ -f "$LG/$ref" ] || echo "$ref"
  done | sort -u > "$cur"

if [ "${1:-}" = "--record" ]; then
  cp "$cur" "$BASE"; echo "baseline de refs colgantes: $(wc -l < "$BASE") (toleradas por el player)"; exit 0
fi

[ -f "$BASE" ] || { echo "falta baseline-missing-refs.txt (correr 00-baseline.sh)"; exit 2; }
new="$WS/theme/new-missing-refs.txt"
comm -23 "$cur" <(sort -u "$BASE") > "$new"
n=$(wc -l < "$new"); tot=$(wc -l < "$cur"); b=$(wc -l < "$BASE")
if [ "$n" -gt 0 ]; then
  echo "FALLA: $n refs faltantes NUEVAS (regresión cosmética); total colgantes=$tot (baseline=$b)"; cat "$new"; exit 1
fi
echo "validate-refs OK: 0 refs nuevas faltantes (colgantes toleradas=$tot, baseline=$b)"
