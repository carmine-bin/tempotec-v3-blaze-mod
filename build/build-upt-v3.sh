#!/usr/bin/env bash
# Construye el .upt v3 del reskin V3A para el TempoTec V3 Blaze.
#
# v3 vs v2:
#   - SIN hook /etc/init.d/S91theme y SIN theme1_stock. El freno NOTHEME se abandono: la v2.1 colgo el
#     boot justo en ese hook (sondeaba el montaje de la SD mientras sys_server la montaba) y el rescate
#     real es recovery por combo de teclas (power + prev) + reinstalar un .upt desde la SD, que no depende
#     de nada horneado. Menos partes moviles = menos formas de colgar el boot.
#     => el unico cambio fuera del tema pasa a ser set_functions.json.
#   - Heredado de v2: tema V3A HORNEADO en el squashfs (litegui/theme1 + layout/theme1) -> ROM
#     autosuficiente, no depende de un arbol en /usr/data ni de adb.
#   - Heredado de v2: set_functions.json {"about":0} -> {"about":1} => aparece "Acerca de" en Ajustes
#     (de ahi sale el modo desarrollador -> ADB en "Modo de dispositivo USB").
#
# Corre TODO bajo fakeroot: unsquashfs no-root pierde el setuid de /bin/busybox y los owners
# http/carmine de /var/www y /run/dbus (bug del build v1). Con fakeroot el round-trip es exacto.
#
# Salida: out-v3/v3_analog_2025.upt  (ese nombre exacto es el que busca el player en la SD)

set -euo pipefail
[ "${BUILD_HISTORICAL_V12:-0}" = 1 ] || { echo "Historical v1.2 builder: use python3 build/build-v1.3.py for current editions." >&2; exit 1; }

# re-exec bajo fakeroot para preservar owners/modos del squashfs
if [ -z "${FAKEROOTKEY:-}" ]; then exec fakeroot "$0" "$@"; fi

HERE=$(cd "$(dirname "$0")" && pwd)          # <repo>/build
ROOT=$(dirname "$HERE")                      # <repo>

# Entradas. Los dos archivos stock NO se versionan (son firmware de TempoTec): se extraen del
# paquete oficial a <repo>/build/stock/. Ver docs/BUILD.md. Todo overrideable por entorno.
STOCK_SQUASHFS="${STOCK_SQUASHFS:-$HERE/stock/rootfs.squashfs}"
STOCK_ROOTFS_MD5=bceb44f6434d17d8e6b634f80737821a
KERNEL="${KERNEL:-$HERE/stock/xImage.stock}"
KERNEL_MD5=97c4b230fb8ef830cfc57c837bf0854a
STAGE="${STAGE:-$ROOT/theme/theme_port}"
MANIFEST="${MANIFEST:-$ROOT/theme/manifest.sha256}"

MTD2_SIZE=47185920      # /dev/mtd2 rootfs (partición rootfs del V3 Blaze verificada)
MTD1_SIZE=5242880       # /dev/mtd1 kernel

WORK="$HERE/work-v3"
OUT="$HERE/out-v3"
UPT="$OUT/v3_analog_2025.upt"

say(){ printf '\n=== %s ===\n' "$*"; }
die(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- 0. precondiciones
say "0. precondiciones"
[ -f "$STOCK_SQUASHFS" ] || die "falta el squashfs stock: $STOCK_SQUASHFS"
[ -f "$KERNEL" ]         || die "falta el kernel: $KERNEL"
[ -d "$STAGE" ]          || die "falta el staging del tema: $STAGE"

got=$(md5sum "$STOCK_SQUASHFS" | cut -d' ' -f1)
[ "$got" = "$STOCK_ROOTFS_MD5" ] || die "rootfs stock md5 $got != $STOCK_ROOTFS_MD5"
got=$(md5sum "$KERNEL" | cut -d' ' -f1)
[ "$got" = "$KERNEL_MD5" ] || die "kernel md5 $got != $KERNEL_MD5 (debe quedar INTACTO)"
echo "rootfs stock y kernel: md5 ok"

# integridad del staging del tema (el manifest se genera tras cada regen de assets)
( cd "$(dirname "$MANIFEST")" && sha256sum -c --quiet "$MANIFEST" ) || die "staging del tema corrupto vs manifest"
echo "staging del tema: $(wc -l < "$MANIFEST") archivos verificados vs manifest"

# ---------------------------------------------------------------- 1. desempacar stock
say "1. desempacar rootfs stock"
rm -rf "$WORK"; mkdir -p "$WORK"
unsquashfs -q -d "$WORK/rootfs" "$STOCK_SQUASHFS" >/dev/null
R="$WORK/rootfs"
[ -x "$R/usr/bin/hiby_player" ] || die "el arbol desempacado no tiene pinta de rootfs"
[ -u "$R/bin/busybox" ] || die "se perdio el setuid de busybox (fakeroot no esta actuando)"
echo "rootfs desempacado: $(find "$R" | wc -l) entradas, setuid de busybox preservado"

# ---------------------------------------------------------------- 2. Acerca de / ADB
say "2. habilitar entradas de Ajustes escondidas por flag (set_functions.json)"
SF="$R/usr/resource/set_functions.json"
# about  -> "Acerca de" (de ahi sale el modo desarrollador -> ADB)
# color  -> "Tema de color": el firmware ya trae dialog/settings_color.dlg con 5 muestras
#           (settings/color_0..4.png), el slider y los textos traducidos; solo estaba apagado.
for flag in about color; do
    grep -q "{\"$flag\":0}" "$SF" || die "no encuentro {\"$flag\":0} en set_functions.json"
    sed -i "s/{\"$flag\":0}/{\"$flag\":1}/" "$SF"
    grep -q "{\"$flag\":1}" "$SF" || die "el patch de $flag no aplico"
    echo "set_functions.json: $flag 0 -> 1"
done

# ---------------------------------------------------------------- 2b/2c. ajustes FUERA del tema
# Tres palancas de velocidad, independientes (cada una se puede apagar sola para bisecar):
#   TF_IMG=1  cache de portadas en la TF   (lo que hace rapido el cambio de caratula)
#   TF_DB=1   base de musica en la TF + dac_to_store
#   IO_TUNE=1 ubifs noatime + read_ahead_kb/vfs_cache_pressure
# Las tres estuvieron en 0 un tiempo porque apagandolas desaparecia el bug de "la calidad del now playing
# es la de la cancion siguiente". Esa bisección acusaba al grupo: el culpable era SOLO TF_IMG, y no por
# cachear nada sino por el efecto colateral de la API 0x1f (ver 2d). Con el NOP de 2d el bug ya no existe
# => las tres vuelven a 1 (2026-08-12, fix de la calidad confirmado en device por el usuario).
# TF_DB e IO_TUNE nunca tuvieron nada que ver con ese bug.
TF_IMG=${TF_IMG:-1}
TF_DB=${TF_DB:-1}
IO_TUNE=${IO_TUNE:-1}
CFG="$R/usr/resource/config_2025.json"   # el player abre z:\config_2025.json (verificado en .rodata)
if [ "$TF_IMG" = 1 ]; then

# ---------------------------------------------------------------- 2b. cache de portadas en la TF
# tf_image_cache_enable: unica palanca contra el "flash negro" de la portada al cambiar de cancion
# (el binario recarga y recomputa el blur de forma asincrona). Se lee SOLO en el arranque => no se puede
# probar por bind volatil, tiene que ir horneada. OJO: quedaba diferida por sospecha de empeorar el bug de
# memoria pre-existente; si aparecen mas cuelgues/reinicios, ESTE es el primer flag a volver a 0.
grep -q '{"tf_image_cache_enable":0}' "$CFG" || die "no encuentro tf_image_cache_enable:0 en config_2025.json"
sed -i 's/{"tf_image_cache_enable":0}/{"tf_image_cache_enable":1}/' "$CFG"
grep -q '{"tf_image_cache_enable":1}' "$CFG" || die "el patch de tf_image_cache_enable no aplico"
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$CFG" || die "config_2025.json quedo con JSON invalido"
echo "config_2025.json: tf_image_cache_enable 0 -> 1"
else
echo "TF_IMG=0: sin cache de portadas (config_2025.json como el stock en ese flag)"
fi

# ---------------------------------------------------------------- 2d. fix binario del "quality" del now playing
# Bug: con tf_image_cache_enable=1 el texto de calidad del now playing muestra el de la cancion SIGUIENTE.
#
# Cadena completa (Ghidra sobre usr/bin/hiby_player del squashfs stock, MIPS32 LE, base 0x400000):
#   1. La vista del now playing (0x50e020 y 0x5105e0) hace, SOLO si el flag esta encendido:
#          if (get_flag(7) == 1) { player_api(0x1f, buf); precargar_portada(buf+4); }
#      get_flag == FUN_0042f560, que devuelve el bit N de 0x964878; el indice 7 es
#      tf_image_cache_enable (orden de la tabla del parser de config en FUN_0042d8a0).
#   2. player_api(0x1f) = "dame la cancion siguiente" (FUN_00436920 case 0x1f). Devuelve bien su
#      struct de 0xa88, pero ADEMAS, de yapa, hace:
#          FUN_00435060(siguiente->path, &0x964a50, ...)   <- 0x00436a00
#      o sea parsea los metadatos de la SIGUIENTE cancion encima del UNICO buffer global de info de
#      la cancion ACTUAL (0x964a50, 128 B: samplerate, bits, codec, bitrate...).
#   3. El hilo de render del now playing (FUN_00510ec8) refresca leyendo player_api(4), que es
#      memcpy desde ese mismo 0x964a50, y se lo pasa al formateador "%d-bit %d.%dkHz %s"
#      (FUN_0050c880) => en el refresh siguiente se ve la calidad de la otra cancion.
#
# Fix: NOP al `jal FUN_00435060` de 0x00436a00 (offset 0x36a00). Los DOS unicos llamadores de la API
# 0x1f solo usan el path del struct devuelto para precargar la portada; ninguno lee el global despues,
# asi que ese parseo no le sirve a nadie. De regalo se van un open+parse completo del archivo siguiente
# en cada cambio de cancion y una fuga: FUN_00435060 arranca con memset(struct,0,0x80) SIN liberar los
# punteros a titulo/artista/album que ya vivian ahi (+0x30..+0x78).
# El delay slot (addiu a0,a0,4) se deja: a0 queda muerto igual, en el stock tambien llega basura al
# unlock de 0x436a08. Se parchea siempre, con TF_IMG=0 la ruta ni se ejecuta.
BINFIX=${BINFIX:-1}          # BINFIX=0 => binario stock, para volver al comportamiento viejo sin editar esto
if [ "$BINFIX" = 1 ]; then
say "2d. NOP del parseo que pisa la info de la cancion actual (hiby_player 0x436a00)"
python3 - "$R/usr/bin/hiby_player" <<'PY' || die "el parche binario de 0x436a00 no aplico"
import sys
OFF  = 0x36a00                      # vaddr 0x00436a00 - 0x400000 (.text: 0x420940 @ 0x20940)
JAL  = bytes.fromhex("18d4100c")    # jal 0x00435060
SLOT = bytes.fromhex("04008424")    # addiu a0,a0,4  (delay slot, ancla de que estamos en el sitio)
NOP  = bytes(4)
with open(sys.argv[1], "r+b") as f:
    f.seek(OFF); got = f.read(8)
    if got != JAL + SLOT:
        sys.exit(f"esperaba {(JAL+SLOT).hex()} en 0x{OFF:x}, hay {got.hex()} (binario distinto al stock)")
    f.seek(OFF); f.write(NOP)
    f.seek(OFF); assert f.read(8) == NOP + SLOT
print(f"hiby_player: 0x{OFF:x} jal FUN_00435060 -> nop")
PY
else
echo "BINFIX=0: hiby_player stock (con TF_IMG=1 vuelve el bug de la calidad de la cancion siguiente)"
fi

if [ "$TF_DB" = 1 ]; then
# dac_to_store    -> persiste el ajuste de DAC entre reinicios
# tf_music_db_enable -> la base de datos de musica vive en la TF en vez de la NAND interna
for flag in dac_to_store tf_music_db_enable; do
    grep -q "{\"$flag\":0}" "$CFG" || die "no encuentro {\"$flag\":0} en config_2025.json"
    sed -i "s/{\"$flag\":0}/{\"$flag\":1}/" "$CFG"
    grep -q "{\"$flag\":1}" "$CFG" || die "el patch de $flag no aplico"
    echo "config_2025.json: $flag 0 -> 1"
done
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$CFG" || die "config_2025.json quedo con JSON invalido"
else
echo "TF_DB=0: base de musica en la NAND interna, dac_to_store como el stock"
fi

if [ "$IO_TUNE" = 1 ]; then
# ---------------------------------------------------------------- 2c. tuning de I/O (mod de bidhata, R1)
# Solo se porta lo que APLICA al Blaze (verificado en device 2026-08-10):
#   - fstab noatime al root ext2  -> NO: nuestro root es squashfs ro, esa linea es vestigial.
#   - quitar batd de hiby_player.sh -> NO: /usr/bin/batd no existe, el bloque ya esta guardado por un if.
#   - ot_devices.json (tablas de ganancia) -> NO: son del hardware del R1, otro DAC. No se copian.
MU="$R/usr/bin/mount_ubifs.sh"
grep -q 'mount -o sync -t ubifs' "$MU" || die "no encuentro el mount -o sync en mount_ubifs.sh"
sed -i 's/mount -o sync -t ubifs/mount -o noatime -t ubifs/' "$MU"
grep -q 'mount -o noatime -t ubifs' "$MU" || die "el patch de mount_ubifs.sh no aplico"
sh -n "$MU" || die "mount_ubifs.sh quedo con sintaxis invalida"
echo "mount_ubifs.sh: /usr/data ubifs  sync -> noatime"

# read_ahead 2048, igual que el mod: el R1 declara 64 MB (las especificaciones del HiBy R1) y el Blaze
# reporta 56936 kB de MemTotal = los mismos 64 MB menos framebuffer y kernel. Mismo equipo en la practica.
# vfs_cache_pressure por /proc porque en este firmware NO existe el binario sysctl.
HP="$R/usr/bin/hiby_player.sh"
grep -q 'read_ahead_kb' "$HP" && die "hiby_player.sh ya tiene el tuning (build no idempotente)"
python3 - "$HP" <<'PY' || die "no pude insertar el tuning en hiby_player.sh"
import sys
p = sys.argv[1]
t = open(p).read()
ancla = "#/usr/bin/hiby_player &>/dev/null"
if ancla not in t:
    sys.exit(1)
tuning = """# tuning de I/O (ver rom-build/build-upt-v3.sh, paso 2c)
[ -w /sys/block/mmcblk0/queue/read_ahead_kb ] && echo 2048 > /sys/block/mmcblk0/queue/read_ahead_kb
[ -w /proc/sys/vm/vfs_cache_pressure ] && echo 50 > /proc/sys/vm/vfs_cache_pressure

"""
open(p, "w").write(t.replace(ancla, tuning + ancla, 1))
PY
sh -n "$HP" || die "hiby_player.sh quedo con sintaxis invalida (COLGARIA EL BOOT)"
grep -q 'reboot' "$HP" || die "se perdio el reboot final de hiby_player.sh"
echo "hiby_player.sh: read_ahead_kb 128 -> 2048, vfs_cache_pressure 100 -> 50"
else
echo "IO_TUNE=0: mount_ubifs.sh y hiby_player.sh como el stock"
fi

# ---------------------------------------------------------------- 3. hornear el tema
# v3: sin theme1_stock. Sin hook que lo bindee es peso muerto (2.9 MB); volver a stock = reinstalar
# un .upt desde la SD (recovery por combo de teclas).
say "3. hornear el tema V3A"
for pair in "litegui" "layout"; do
    dst="$R/usr/resource/$pair/theme1"
    [ -d "$dst" ] || die "falta $dst en el rootfs stock"
    rm -rf "$dst"
    cp -a "$STAGE/$pair/theme1" "$dst"
    echo "$pair/theme1: $(find "$dst" -type f | wc -l) archivos V3A"
done
! [ -e "$R/etc/init.d/S91theme" ] || die "quedo un S91theme en el rootfs (v3 no lleva hook)"

# gates del tema: (1) sintaxis de layout -> lo unico que puede colgar el boot; (2) refs de PNG faltantes
# NUEVAS respecto al stock -> regresion cosmetica (el player tolera un PNG ausente, no crashea).
say "3b. gates del tema"
python3 - "$R/usr/resource/layout/theme1" <<'PY' || die "layout con sintaxis invalida (riesgo de boot-loop)"
import json, sys, pathlib
bad = 0
for f in sorted(pathlib.Path(sys.argv[1]).rglob("*")):
    if f.is_file() and f.suffix in (".view", ".dlg", ".listview", ".json"):
        try: json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception as e: print("SINTAXIS", f.name, e); bad += 1
print(f"layout: {bad} archivos con sintaxis invalida")
sys.exit(1 if bad else 0)
PY
bash "$HERE/scripts/validate-refs.sh" || die "refs de PNG faltantes NUEVAS vs stock"

# ---------------------------------------------------------------- 5. squashfs
say "5. mksquashfs"
mksquashfs "$R" "$WORK/rootfs.squashfs" -comp lzo -b 131072 -noappend -no-progress >/dev/null
ROOTFS_SIZE=$(stat -c%s "$WORK/rootfs.squashfs")
ROOTFS_MD5=$(md5sum "$WORK/rootfs.squashfs" | cut -d' ' -f1)
echo "rootfs.squashfs: $ROOTFS_SIZE B  md5 $ROOTFS_MD5"
[ "$ROOTFS_SIZE" -le "$MTD2_SIZE" ] || die "no entra en mtd2 ($ROOTFS_SIZE > $MTD2_SIZE)"
echo "cabe en mtd2 ($MTD2_SIZE B), margen $(( (MTD2_SIZE - ROOTFS_SIZE) / 1024 )) KiB"

KERNEL_SIZE=$(stat -c%s "$KERNEL")
[ "$KERNEL_SIZE" -le "$MTD1_SIZE" ] || die "el kernel no entra en mtd1"

# ---------------------------------------------------------------- 6. .upt
# Estructura del OTA oficial: ISO9660 (Joliet+RockRidge) con ota_config.in + ota_v0/,
# cada img partida en chunks de 512K y cada chunk renombrado con el md5 del ANTERIOR
# (el del primero es el md5 de la img completa). Ver etc/ota_bin/local_ota_update.sh.
say "6. armar el .upt"
ISO="$WORK/iso"; rm -rf "$ISO"; mkdir -p "$ISO/ota_v0"

chunk(){  # chunk <archivo> <prefijo> -> deja los chunks renombrados + ota_md5_<prefijo>.<md5>
    local src=$1 name=$2 full_md5 md5 md5next part
    full_md5=$(md5sum "$src" | cut -d' ' -f1)
    split "$src" -d -a 4 -b 512k "$name."
    : > "ota_md5_$name.$full_md5"
    md5=$full_md5
    for part in $(ls "$name".[0-9]* | sort); do
        md5next=$(md5sum "$part" | cut -d' ' -f1)
        echo "$md5next" >> "ota_md5_$name.$full_md5"
        mv "$part" "$part.$md5"
        md5=$md5next
    done
}

pushd "$ISO/ota_v0" >/dev/null
chunk "$KERNEL" xImage
chunk "$WORK/rootfs.squashfs" rootfs.squashfs
cat > ota_update.in <<EOM
ota_version=0

img_type=kernel
img_name=xImage
img_size=${KERNEL_SIZE}
img_md5=${KERNEL_MD5}

img_type=rootfs
img_name=rootfs.squashfs
img_size=${ROOTFS_SIZE}
img_md5=${ROOTFS_MD5}
EOM
echo > ota_v0.ok
popd >/dev/null
echo "current_version=0" > "$ISO/ota_config.in"

rm -rf "$OUT"; mkdir -p "$OUT"
xorrisofs -quiet -J -r -o "$UPT" "$ISO"
echo "$UPT  $(stat -c%s "$UPT") B"

# ---------------------------------------------------------------- 7. validacion
say "7. validacion del .upt"
VER="$WORK/verify"; rm -rf "$VER"; mkdir -p "$VER"
xorriso -osirrox on -indev "$UPT" -extract / "$VER" >/dev/null 2>&1
cat "$VER/ota_config.in"
cat "$VER/ota_v0/ota_update.in"

# reensamblar las imgs desde los chunks del .upt y comparar md5 contra el manifiesto
cat $(ls "$VER"/ota_v0/xImage.[0-9]*.* | sort) > "$VER/xImage.re"
cat $(ls "$VER"/ota_v0/rootfs.squashfs.[0-9]*.* | sort) > "$VER/rootfs.re"
k=$(md5sum "$VER/xImage.re" | cut -d' ' -f1); r=$(md5sum "$VER/rootfs.re" | cut -d' ' -f1)
[ "$k" = "$KERNEL_MD5" ] || die "kernel reensamblado != stock ($k)"
[ "$r" = "$ROOTFS_MD5" ] || die "rootfs reensamblado != el construido ($r)"
echo "kernel reensamblado md5 $k == stock (INTACTO)"
echo "rootfs reensamblado md5 $r == manifiesto"

# diff real contra el stock: modos, owners, tamanos y rutas.
# Se normaliza: fuera fecha/hora (no es propiedad de seguridad) y fuera el tamano de los DIRECTORIOS
# (squashfs lo recalcula segun el contenido, asi que cambia por el tema y es ruido).
say "8. diff vs rootfs stock (modos/owners/tamanos)"
norm(){ grep -E '^[-dlbcps]' | sed 's/  */ /g' \
        | awk '{ if (substr($1,1,1)=="d") print $1,$2,$6; else print $1,$2,$3,$6 }' | sort; }
unsquashfs -lls "$STOCK_SQUASHFS"  2>/dev/null | norm > "$WORK/stock.list"
unsquashfs -lls "$VER/rootfs.re"   2>/dev/null | norm > "$WORK/new.list"
diff "$WORK/stock.list" "$WORK/new.list" > "$WORK/diff.txt" || true
{
  echo "solo en stock : $(grep -c '^<' "$WORK/diff.txt" || true)"
  echo "solo en nuevo : $(grep -c '^>' "$WORK/diff.txt" || true)"
  echo
  echo "-- cambios FUERA de litegui/theme1*, layout/theme1* --"
  grep -E '^[<>]' "$WORK/diff.txt" | grep -vE 'resource/(litegui|layout)/theme1' || echo "(ninguno)"
} | tee "$WORK/diff-summary.txt"

# gate duro por METADATOS: fuera del tema no puede aparecer/desaparecer/cambiar de modo nada mas que
# set_functions.json (que ademas conserva el tamano, 0 -> 1).
otras=$(awk '/^[<>]/ && !/resource\/(litegui|layout)\/theme1/ && !/set_functions\.json/ && !/config_2025\.json/ && !/mount_ubifs\.sh/ && !/hiby_player\.sh/' "$WORK/diff.txt" | wc -l)
[ "$otras" -eq 0 ] || die "hay $otras cambios de metadatos fuera del tema (ver $WORK/diff-summary.txt)"
echo "gate metadatos: fuera del tema, sin cambios"

# gate duro por CONTENIDO: sha256 archivo por archivo (el de metadatos no ve un cambio del mismo tamano).
say "9. gate de contenido (sha256 por archivo) vs rootfs stock"
rm -rf "$WORK/stockfs"; unsquashfs -q -d "$WORK/stockfs" "$STOCK_SQUASHFS" >/dev/null
hashes(){ ( cd "$1" && find . -type f \
              -not -path './usr/resource/litegui/theme1/*' \
              -not -path './usr/resource/layout/theme1/*' \
              -print0 | xargs -0 sha256sum | sort -k2 ); }
hashes "$WORK/stockfs" > "$WORK/stock.sha"
hashes "$R"            > "$WORK/new.sha"
# (diff sale 1 cuando hay diferencias -> || true, si no pipefail+set -e cortan el script)
diff "$WORK/stock.sha" "$WORK/new.sha" > "$WORK/content-diff.txt" || true
esperados='/set_functions\.json|config_2025\.json|mount_ubifs\.sh|hiby_player\.sh|bin\/hiby_player$/'
difs=$(awk "/^[<>]/ && \$0 !~ $esperados" "$WORK/content-diff.txt" | wc -l)
if [ "$difs" -ne 0 ]; then
    awk "/^[<>]/ && \$0 !~ $esperados" "$WORK/content-diff.txt"
    die "hay $difs archivos con contenido distinto fuera del tema"
fi

# el binario es lo unico horneado a mano: que la diferencia sea EXACTAMENTE el NOP del paso 2d
# (cmp -l cuenta bytes desde 1 => los 4 del NOP en 0x36a00 son 223745..223748)
cmp -l "$WORK/stockfs/usr/bin/hiby_player" "$R/usr/bin/hiby_player" > "$WORK/bin-diff.txt" || true
bindifs=$(wc -l < "$WORK/bin-diff.txt")
if [ "$BINFIX" = 1 ]; then
    [ "$(awk '$1>=223745 && $1<=223748 && $3=="0"' "$WORK/bin-diff.txt" | wc -l)" = 4 ] \
        || die "hiby_player: el NOP de 0x36a00 no esta en el binario horneado"
    [ "$bindifs" = 4 ] || die "hiby_player difiere del stock en $bindifs bytes, esperaba solo los 4 del NOP"
else
    [ "$bindifs" = 0 ] || die "BINFIX=0 pero hiby_player difiere del stock en $bindifs bytes"
fi
echo "gate contenido: $(wc -l < "$WORK/new.sha") archivos fuera del tema, todos identicos al stock"
echo "                (cambios: set_functions.json, config_2025.json, mount_ubifs.sh, hiby_player.sh,"
echo "                 hiby_player = 4 bytes, el NOP de 0x36a00)"

say "LISTO"
echo "artefacto: $UPT"
echo "copiarlo TAL CUAL (nombre incluido) a la raiz de la microSD."
