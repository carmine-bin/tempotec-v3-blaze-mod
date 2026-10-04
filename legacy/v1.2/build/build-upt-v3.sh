#!/usr/bin/env bash
# Builds the v3 .upt of the V3A reskin for the TempoTec V3 Blaze (official firmware v1.2 base).
#
# v3 vs v2:
#   - NO /etc/init.d/S91theme hook and NO theme1_stock. The NOTHEME brake was dropped: v2.1 hung the
#     boot right in that hook (it polled the SD mount while sys_server was mounting it), and the real
#     rescue is recovery via the key combo (power + prev) + reinstalling a .upt from the SD, which does
#     not depend on anything baked in. Fewer moving parts = fewer ways to hang the boot.
#     => the only change outside the theme becomes set_functions.json.
#   - Inherited from v2: V3A theme BAKED into the squashfs (litegui/theme1 + layout/theme1) -> a
#     self-contained ROM that does not depend on a tree in /usr/data or on adb.
#   - Inherited from v2: set_functions.json {"about":0} -> {"about":1} => "About" appears in Settings
#     (that is the route to developer mode -> ADB under "USB device mode").
#
# Runs EVERYTHING under fakeroot: a non-root unsquashfs loses the setuid bit of /bin/busybox and the
# http/carmine owners of /var/www and /run/dbus (bug in build v1). With fakeroot the round trip is exact.
#
# Output: out-v3/v3_analog_2025.upt  (that exact name is what the player looks for on the SD)

set -euo pipefail
[ "${BUILD_HISTORICAL_V12:-0}" = 1 ] || { echo "Historical v1.2 builder: use python3 build/build-v1.3.py for current editions." >&2; exit 1; }

# re-exec under fakeroot to preserve squashfs owners/modes
if [ -z "${FAKEROOTKEY:-}" ]; then exec fakeroot "$0" "$@"; fi

HERE=$(cd "$(dirname "$0")" && pwd)          # <repo>/legacy/v1.2/build
ROOT=$(dirname "$HERE")                      # <repo>/legacy/v1.2

# Inputs. The two stock files are NOT versioned (they are TempoTec firmware): they are extracted from
# the official package into <repo>/legacy/v1.2/build/stock/. See docs/releases/v1.0.0-BUILD.md.
# Everything can be overridden from the environment.
STOCK_SQUASHFS="${STOCK_SQUASHFS:-$HERE/stock/rootfs.squashfs}"
STOCK_ROOTFS_MD5=bceb44f6434d17d8e6b634f80737821a
KERNEL="${KERNEL:-$HERE/stock/xImage.stock}"
KERNEL_MD5=97c4b230fb8ef830cfc57c837bf0854a
STAGE="${STAGE:-$ROOT/theme/theme_port}"
MANIFEST="${MANIFEST:-$ROOT/theme/manifest.sha256}"

MTD2_SIZE=47185920      # /dev/mtd2 rootfs (verified V3 Blaze rootfs partition)
MTD1_SIZE=5242880       # /dev/mtd1 kernel

WORK="$HERE/work-v3"
OUT="$HERE/out-v3"
UPT="$OUT/v3_analog_2025.upt"

say(){ printf '\n=== %s ===\n' "$*"; }
die(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- 0. preconditions
say "0. preconditions"
[ -f "$STOCK_SQUASHFS" ] || die "missing stock squashfs: $STOCK_SQUASHFS"
[ -f "$KERNEL" ]         || die "missing kernel: $KERNEL"
[ -d "$STAGE" ]          || die "missing theme staging: $STAGE"

got=$(md5sum "$STOCK_SQUASHFS" | cut -d' ' -f1)
[ "$got" = "$STOCK_ROOTFS_MD5" ] || die "stock rootfs md5 $got != $STOCK_ROOTFS_MD5"
got=$(md5sum "$KERNEL" | cut -d' ' -f1)
[ "$got" = "$KERNEL_MD5" ] || die "kernel md5 $got != $KERNEL_MD5 (must stay UNTOUCHED)"
echo "stock rootfs and kernel: md5 ok"

# theme staging integrity (the manifest is regenerated after every asset regeneration)
( cd "$(dirname "$MANIFEST")" && sha256sum -c --quiet "$MANIFEST" ) || die "theme staging does not match the manifest"
echo "theme staging: $(wc -l < "$MANIFEST") files verified against the manifest"

# ---------------------------------------------------------------- 1. unpack stock
say "1. unpack stock rootfs"
rm -rf "$WORK"; mkdir -p "$WORK"
unsquashfs -q -d "$WORK/rootfs" "$STOCK_SQUASHFS" >/dev/null
R="$WORK/rootfs"
[ -x "$R/usr/bin/hiby_player" ] || die "the unpacked tree does not look like a rootfs"
[ -u "$R/bin/busybox" ] || die "busybox lost its setuid bit (fakeroot is not active)"
echo "rootfs unpacked: $(find "$R" | wc -l) entries, busybox setuid preserved"

# ---------------------------------------------------------------- 2. About / ADB
say "2. enable Settings entries hidden by flag (set_functions.json)"
SF="$R/usr/resource/set_functions.json"
# about  -> "About" (route to developer mode -> ADB)
# color  -> "Colour theme": the firmware already ships dialog/settings_color.dlg with 5 swatches
#           (settings/color_0..4.png), the slider and the translated strings; it was just switched off.
for flag in about color; do
    grep -q "{\"$flag\":0}" "$SF" || die "cannot find {\"$flag\":0} in set_functions.json"
    sed -i "s/{\"$flag\":0}/{\"$flag\":1}/" "$SF"
    grep -q "{\"$flag\":1}" "$SF" || die "the $flag patch did not apply"
    echo "set_functions.json: $flag 0 -> 1"
done

# ---------------------------------------------------------------- 2b/2c. settings OUTSIDE the theme
# Three independent speed levers (each can be switched off on its own for bisecting):
#   TF_IMG=1  cover cache on the TF card    (what makes artwork changes fast)
#   TF_DB=1   music database on the TF card + dac_to_store
#   IO_TUNE=1 ubifs noatime + read_ahead_kb/vfs_cache_pressure
# All three were at 0 for a while because switching them off made the "Now Playing quality is the next
# track's" bug go away. That bisection blamed the group: the culprit was ONLY TF_IMG, and not because of
# caching anything but because of a side effect of API 0x1f (see 2d). With the 2d NOP the bug is gone
# => all three are back to 1 (2026-08-12, quality fix confirmed on the device by the user).
# TF_DB and IO_TUNE never had anything to do with that bug.
TF_IMG=${TF_IMG:-1}
TF_DB=${TF_DB:-1}
IO_TUNE=${IO_TUNE:-1}
CFG="$R/usr/resource/config_2025.json"   # the player opens z:\config_2025.json (verified in .rodata)
if [ "$TF_IMG" = 1 ]; then

# ---------------------------------------------------------------- 2b. cover cache on the TF card
# tf_image_cache_enable: the only lever against the cover's "black flash" on track change
# (the binary reloads and recomputes the blur asynchronously). Read ONLY at boot => cannot be tested
# with a volatile bind mount, it has to be baked in. CAREFUL: it was deferred on suspicion of worsening
# the pre-existing memory bug; if more hangs/reboots appear, THIS is the first flag to set back to 0.
grep -q '{"tf_image_cache_enable":0}' "$CFG" || die "cannot find tf_image_cache_enable:0 in config_2025.json"
sed -i 's/{"tf_image_cache_enable":0}/{"tf_image_cache_enable":1}/' "$CFG"
grep -q '{"tf_image_cache_enable":1}' "$CFG" || die "the tf_image_cache_enable patch did not apply"
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$CFG" || die "config_2025.json is now invalid JSON"
echo "config_2025.json: tf_image_cache_enable 0 -> 1"
else
echo "TF_IMG=0: no cover cache (config_2025.json as stock for that flag)"
fi

# ---------------------------------------------------------------- 2d. binary fix for the Now Playing "quality"
# Bug: with tf_image_cache_enable=1 the Now Playing quality text shows the NEXT track's.
#
# Full chain (Ghidra on usr/bin/hiby_player from the stock squashfs, MIPS32 LE, base 0x400000):
#   1. The Now Playing view (0x50e020 and 0x5105e0) does, ONLY if the flag is on:
#          if (get_flag(7) == 1) { player_api(0x1f, buf); preload_cover(buf+4); }
#      get_flag == FUN_0042f560, which returns bit N of 0x964878; index 7 is
#      tf_image_cache_enable (order of the config parser table in FUN_0042d8a0).
#   2. player_api(0x1f) = "give me the next track" (FUN_00436920 case 0x1f). It returns its 0xa88
#      struct correctly, but ALSO, as a bonus, does:
#          FUN_00435060(next->path, &0x964a50, ...)   <- 0x00436a00
#      i.e. it parses the NEXT track's metadata over the ONLY global info buffer of the
#      CURRENT track (0x964a50, 128 B: sample rate, bits, codec, bitrate...).
#   3. The Now Playing render thread (FUN_00510ec8) refreshes by reading player_api(4), which is a
#      memcpy from that same 0x964a50, and passes it to the "%d-bit %d.%dkHz %s" formatter
#      (FUN_0050c880) => on the next refresh the other track's quality is shown.
#
# Fix: NOP the `jal FUN_00435060` at 0x00436a00 (offset 0x36a00). The ONLY TWO callers of API 0x1f
# only use the path from the returned struct to preload the cover; neither reads the global afterwards,
# so that parse is useless. As a bonus this removes a full open+parse of the next file on every track
# change, and a leak: FUN_00435060 starts with memset(struct,0,0x80) WITHOUT freeing the
# title/artist/album pointers that already lived there (+0x30..+0x78).
# The delay slot (addiu a0,a0,4) is left: a0 is dead anyway, and in stock garbage also reaches the
# unlock at 0x436a08. Always patched; with TF_IMG=0 the path does not even run.
BINFIX=${BINFIX:-1}          # BINFIX=0 => stock binary, to return to the old behaviour without editing this
if [ "$BINFIX" = 1 ]; then
say "2d. NOP the parse that overwrites the current track's info (hiby_player 0x436a00)"
python3 - "$R/usr/bin/hiby_player" <<'PY' || die "the binary patch at 0x436a00 did not apply"
import sys
OFF  = 0x36a00                      # vaddr 0x00436a00 - 0x400000 (.text: 0x420940 @ 0x20940)
JAL  = bytes.fromhex("18d4100c")    # jal 0x00435060
SLOT = bytes.fromhex("04008424")    # addiu a0,a0,4  (delay slot, anchors that we are at the right place)
NOP  = bytes(4)
with open(sys.argv[1], "r+b") as f:
    f.seek(OFF); got = f.read(8)
    if got != JAL + SLOT:
        sys.exit(f"expected {(JAL+SLOT).hex()} at 0x{OFF:x}, found {got.hex()} (binary differs from stock)")
    f.seek(OFF); f.write(NOP)
    f.seek(OFF); assert f.read(8) == NOP + SLOT
print(f"hiby_player: 0x{OFF:x} jal FUN_00435060 -> nop")
PY
else
echo "BINFIX=0: stock hiby_player (with TF_IMG=1 the next-track quality bug comes back)"
fi

if [ "$TF_DB" = 1 ]; then
# dac_to_store       -> persists the DAC setting across reboots
# tf_music_db_enable -> the music database lives on the TF card instead of internal NAND
for flag in dac_to_store tf_music_db_enable; do
    grep -q "{\"$flag\":0}" "$CFG" || die "cannot find {\"$flag\":0} in config_2025.json"
    sed -i "s/{\"$flag\":0}/{\"$flag\":1}/" "$CFG"
    grep -q "{\"$flag\":1}" "$CFG" || die "the $flag patch did not apply"
    echo "config_2025.json: $flag 0 -> 1"
done
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$CFG" || die "config_2025.json is now invalid JSON"
else
echo "TF_DB=0: music database on internal NAND, dac_to_store as stock"
fi

if [ "$IO_TUNE" = 1 ]; then
# ---------------------------------------------------------------- 2c. I/O tuning (bidhata's R1 mod)
# Only what APPLIES to the Blaze is ported (verified on the device 2026-08-10):
#   - fstab noatime on the ext2 root  -> NO: our root is read-only squashfs, that line is vestigial.
#   - remove batd from hiby_player.sh -> NO: /usr/bin/batd does not exist, the block is already guarded by an if.
#   - ot_devices.json (gain tables)   -> NO: they belong to the R1 hardware, a different DAC. Not copied.
MU="$R/usr/bin/mount_ubifs.sh"
grep -q 'mount -o sync -t ubifs' "$MU" || die "cannot find mount -o sync in mount_ubifs.sh"
sed -i 's/mount -o sync -t ubifs/mount -o noatime -t ubifs/' "$MU"
grep -q 'mount -o noatime -t ubifs' "$MU" || die "the mount_ubifs.sh patch did not apply"
sh -n "$MU" || die "mount_ubifs.sh now has invalid syntax"
echo "mount_ubifs.sh: /usr/data ubifs  sync -> noatime"

# read_ahead 2048, same as the mod: the R1 declares 64 MB (HiBy R1 specifications) and the Blaze
# reports 56936 kB MemTotal = the same 64 MB minus framebuffer and kernel. Effectively the same device.
# vfs_cache_pressure via /proc because this firmware has NO sysctl binary.
HP="$R/usr/bin/hiby_player.sh"
grep -q 'read_ahead_kb' "$HP" && die "hiby_player.sh already has the tuning (build is not idempotent)"
# The inserted comment line below is firmware content and is kept verbatim (in Spanish) so the
# generated hiby_player.sh stays byte-identical to the one shipped in v1.0.0 and carried into v1.3.
python3 - "$HP" <<'PY' || die "could not insert the tuning into hiby_player.sh"
import sys
p = sys.argv[1]
t = open(p).read()
anchor = "#/usr/bin/hiby_player &>/dev/null"
if anchor not in t:
    sys.exit(1)
tuning = """# tuning de I/O (ver rom-build/build-upt-v3.sh, paso 2c)
[ -w /sys/block/mmcblk0/queue/read_ahead_kb ] && echo 2048 > /sys/block/mmcblk0/queue/read_ahead_kb
[ -w /proc/sys/vm/vfs_cache_pressure ] && echo 50 > /proc/sys/vm/vfs_cache_pressure

"""
open(p, "w").write(t.replace(anchor, tuning + anchor, 1))
PY
sh -n "$HP" || die "hiby_player.sh now has invalid syntax (IT WOULD HANG THE BOOT)"
grep -q 'reboot' "$HP" || die "hiby_player.sh lost its final reboot"
echo "hiby_player.sh: read_ahead_kb 128 -> 2048, vfs_cache_pressure 100 -> 50"
else
echo "IO_TUNE=0: mount_ubifs.sh and hiby_player.sh as stock"
fi

# ---------------------------------------------------------------- 3. bake the theme
# v3: no theme1_stock. Without a hook to bind it, it is dead weight (2.9 MB); going back to stock =
# reinstalling a .upt from the SD (recovery via the key combo).
say "3. bake the V3A theme"
for pair in "litegui" "layout"; do
    dst="$R/usr/resource/$pair/theme1"
    [ -d "$dst" ] || die "missing $dst in the stock rootfs"
    rm -rf "$dst"
    cp -a "$STAGE/$pair/theme1" "$dst"
    echo "$pair/theme1: $(find "$dst" -type f | wc -l) V3A files"
done
! [ -e "$R/etc/init.d/S91theme" ] || die "an S91theme was left in the rootfs (v3 has no hook)"

# theme gates: (1) layout syntax -> the only thing that can hang the boot; (2) NEW missing PNG refs
# relative to stock -> cosmetic regression (the player tolerates a missing PNG, it does not crash).
say "3b. theme gates"
python3 - "$R/usr/resource/layout/theme1" <<'PY' || die "layout with invalid syntax (boot-loop risk)"
import json, sys, pathlib
bad = 0
for f in sorted(pathlib.Path(sys.argv[1]).rglob("*")):
    if f.is_file() and f.suffix in (".view", ".dlg", ".listview", ".json"):
        try: json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception as e: print("SYNTAX", f.name, e); bad += 1
print(f"layout: {bad} files with invalid syntax")
sys.exit(1 if bad else 0)
PY
bash "$HERE/scripts/validate-refs.sh" || die "NEW missing PNG refs vs stock"

# ---------------------------------------------------------------- 5. squashfs
say "5. mksquashfs"
mksquashfs "$R" "$WORK/rootfs.squashfs" -comp lzo -b 131072 -noappend -no-progress >/dev/null
ROOTFS_SIZE=$(stat -c%s "$WORK/rootfs.squashfs")
ROOTFS_MD5=$(md5sum "$WORK/rootfs.squashfs" | cut -d' ' -f1)
echo "rootfs.squashfs: $ROOTFS_SIZE B  md5 $ROOTFS_MD5"
[ "$ROOTFS_SIZE" -le "$MTD2_SIZE" ] || die "does not fit in mtd2 ($ROOTFS_SIZE > $MTD2_SIZE)"
echo "fits in mtd2 ($MTD2_SIZE B), margin $(( (MTD2_SIZE - ROOTFS_SIZE) / 1024 )) KiB"

KERNEL_SIZE=$(stat -c%s "$KERNEL")
[ "$KERNEL_SIZE" -le "$MTD1_SIZE" ] || die "the kernel does not fit in mtd1"

# ---------------------------------------------------------------- 6. .upt
# Structure of the official OTA: ISO9660 (Joliet+RockRidge) with ota_config.in + ota_v0/,
# each image split into 512K chunks and each chunk renamed with the md5 of the PREVIOUS one
# (the first one's is the md5 of the whole image). See etc/ota_bin/local_ota_update.sh.
say "6. assemble the .upt"
ISO="$WORK/iso"; rm -rf "$ISO"; mkdir -p "$ISO/ota_v0"

chunk(){  # chunk <file> <prefix> -> leaves the renamed chunks + ota_md5_<prefix>.<md5>
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

# ---------------------------------------------------------------- 7. validation
say "7. validate the .upt"
VER="$WORK/verify"; rm -rf "$VER"; mkdir -p "$VER"
xorriso -osirrox on -indev "$UPT" -extract / "$VER" >/dev/null 2>&1
cat "$VER/ota_config.in"
cat "$VER/ota_v0/ota_update.in"

# reassemble the images from the .upt chunks and compare md5 against the manifest
cat $(ls "$VER"/ota_v0/xImage.[0-9]*.* | sort) > "$VER/xImage.re"
cat $(ls "$VER"/ota_v0/rootfs.squashfs.[0-9]*.* | sort) > "$VER/rootfs.re"
k=$(md5sum "$VER/xImage.re" | cut -d' ' -f1); r=$(md5sum "$VER/rootfs.re" | cut -d' ' -f1)
[ "$k" = "$KERNEL_MD5" ] || die "reassembled kernel != stock ($k)"
[ "$r" = "$ROOTFS_MD5" ] || die "reassembled rootfs != the one built ($r)"
echo "reassembled kernel md5 $k == stock (UNTOUCHED)"
echo "reassembled rootfs md5 $r == manifest"

# real diff against stock: modes, owners, sizes and paths.
# Normalized: date/time removed (not a security property) and DIRECTORY sizes removed
# (squashfs recomputes them from their contents, so they change with the theme and are noise).
say "8. diff vs stock rootfs (modes/owners/sizes)"
norm(){ grep -E '^[-dlbcps]' | sed 's/  */ /g' \
        | awk '{ if (substr($1,1,1)=="d") print $1,$2,$6; else print $1,$2,$3,$6 }' | sort; }
unsquashfs -lls "$STOCK_SQUASHFS"  2>/dev/null | norm > "$WORK/stock.list"
unsquashfs -lls "$VER/rootfs.re"   2>/dev/null | norm > "$WORK/new.list"
diff "$WORK/stock.list" "$WORK/new.list" > "$WORK/diff.txt" || true
{
  echo "only in stock : $(grep -c '^<' "$WORK/diff.txt" || true)"
  echo "only in new   : $(grep -c '^>' "$WORK/diff.txt" || true)"
  echo
  echo "-- changes OUTSIDE litegui/theme1*, layout/theme1* --"
  grep -E '^[<>]' "$WORK/diff.txt" | grep -vE 'resource/(litegui|layout)/theme1' || echo "(none)"
} | tee "$WORK/diff-summary.txt"

# hard METADATA gate: outside the theme nothing may appear/disappear/change mode except
# set_functions.json (which also keeps its size, 0 -> 1).
others=$(awk '/^[<>]/ && !/resource\/(litegui|layout)\/theme1/ && !/set_functions\.json/ && !/config_2025\.json/ && !/mount_ubifs\.sh/ && !/hiby_player\.sh/' "$WORK/diff.txt" | wc -l)
[ "$others" -eq 0 ] || die "$others metadata changes outside the theme (see $WORK/diff-summary.txt)"
echo "metadata gate: no changes outside the theme"

# hard CONTENT gate: sha256 file by file (the metadata gate cannot see a same-size change).
say "9. content gate (per-file sha256) vs stock rootfs"
rm -rf "$WORK/stockfs"; unsquashfs -q -d "$WORK/stockfs" "$STOCK_SQUASHFS" >/dev/null
hashes(){ ( cd "$1" && find . -type f \
              -not -path './usr/resource/litegui/theme1/*' \
              -not -path './usr/resource/layout/theme1/*' \
              -print0 | xargs -0 sha256sum | sort -k2 ); }
hashes "$WORK/stockfs" > "$WORK/stock.sha"
hashes "$R"            > "$WORK/new.sha"
# (diff exits 1 when there are differences -> || true, otherwise pipefail+set -e stop the script)
diff "$WORK/stock.sha" "$WORK/new.sha" > "$WORK/content-diff.txt" || true
expected='/set_functions\.json|config_2025\.json|mount_ubifs\.sh|hiby_player\.sh|bin\/hiby_player$/'
difs=$(awk "/^[<>]/ && \$0 !~ $expected" "$WORK/content-diff.txt" | wc -l)
if [ "$difs" -ne 0 ]; then
    awk "/^[<>]/ && \$0 !~ $expected" "$WORK/content-diff.txt"
    die "$difs files with different content outside the theme"
fi

# the binary is the only thing baked by hand: the difference must be EXACTLY the step 2d NOP
# (cmp -l counts bytes from 1 => the 4 NOP bytes at 0x36a00 are 223745..223748)
cmp -l "$WORK/stockfs/usr/bin/hiby_player" "$R/usr/bin/hiby_player" > "$WORK/bin-diff.txt" || true
bindifs=$(wc -l < "$WORK/bin-diff.txt")
if [ "$BINFIX" = 1 ]; then
    [ "$(awk '$1>=223745 && $1<=223748 && $3=="0"' "$WORK/bin-diff.txt" | wc -l)" = 4 ] \
        || die "hiby_player: the 0x36a00 NOP is not in the baked binary"
    [ "$bindifs" = 4 ] || die "hiby_player differs from stock in $bindifs bytes, expected only the 4 NOP bytes"
else
    [ "$bindifs" = 0 ] || die "BINFIX=0 but hiby_player differs from stock in $bindifs bytes"
fi
echo "content gate: $(wc -l < "$WORK/new.sha") files outside the theme, all identical to stock"
echo "              (changes: set_functions.json, config_2025.json, mount_ubifs.sh, hiby_player.sh,"
echo "               hiby_player = 4 bytes, the 0x36a00 NOP)"

say "DONE"
echo "artifact: $UPT"
echo "copy it AS IS (name included) to the root of the microSD card."
