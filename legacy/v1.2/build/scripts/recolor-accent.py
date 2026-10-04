#!/usr/bin/env python3
# Changes the accent colour of the V3A theme. The V3A uses ONE accent, #009FF6, baked into the PNGs
# (progress bars, enabled toggles, gain pills, keyboard, play button, etc.) and into
# 12 text colours in the layout.
#
#   recolor-accent.py                      -> to the purple of the factory picker (#6B31A5, color_4.png)
#   recolor-accent.py --to=RRGGBB          -> to another colour
#   recolor-accent.py --from=RRGGBB --to=…  -> if you already recoloured it, say where it starts from
#
# Not a flat colour replacement: it converts to HSV and applies the SAME hue delta and the same
# saturation/value scale to every pixel in the accent range, so shadows, gradients and antialiasing
# keep their relationship (a flat replacement would leave smoothed edges with a blue halo).
import colorsys, os, sys
from PIL import Image

# NOTE: the round trip is NOT symmetric with the default threshold: recolouring multiplies saturation
# by KS, so a pixel just above the floor (e.g. #cfedfd, s=0.18) ends up on the other side with s=0.127
# and on the way back falls BELOW the floor -> it is not reverted and stays the old colour, desaturated
# (observed: 22 px per file in 80 files, in the highlights of the `_s` icons). To revert a recolour,
# lower the floor: --smin=0.08
SOURCE, TARGET, SMIN = "009FF6", "6B31A5", 0.15
for a in sys.argv[1:]:
    if a.startswith("--from="): SOURCE = a.split("=", 1)[1].lstrip("#")
    if a.startswith("--to="):   TARGET = a.split("=", 1)[1].lstrip("#")
    if a.startswith("--smin="): SMIN = float(a.split("=", 1)[1])

def hsv(hexs):
    r, g, b = (int(hexs[i:i+2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)

h0, s0, v0 = hsv(SOURCE)
h1, s1, v1 = hsv(TARGET)
DH, KS, KV = h1 - h0, s1 / s0, v1 / v0
WINDOW = 0.04          # ± in hue: catches the accent and its variants, leaves the rest of the palette alone

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LG = os.path.join(WS, "theme/theme_port/litegui/theme1")
LY = os.path.join(WS, "theme/theme_port/layout/theme1")

def shift(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if abs((h - h0 + 0.5) % 1.0 - 0.5) > WINDOW or s < SMIN or v < 0.12:
        return None
    r2, g2, b2 = colorsys.hsv_to_rgb((h + DH) % 1.0, min(1.0, s * KS), min(1.0, v * KV))
    return round(r2 * 255), round(g2 * 255), round(b2 * 255)

cache = {}
nf = npx = 0
for root, _, fs in os.walk(LG):
    for fn in sorted(fs):
        if not fn.endswith(".png"):
            continue
        p = os.path.join(root, fn)
        try: im = Image.open(p).convert("RGBA")
        except Exception: continue
        px = im.load()
        W, H = im.size
        touched = 0
        for y in range(H):
            for x in range(W):
                r, g, b, a = px[x, y]
                if a < 12:
                    continue
                k = (r, g, b)
                if k not in cache:
                    cache[k] = shift(r, g, b)
                new = cache[k]
                if new:
                    px[x, y] = (*new, a)
                    touched += 1
        if touched:
            im.save(p)
            nf += 1; npx += touched
print(f"PNG: {nf} files recoloured, {npx} px  ({SOURCE} -> {TARGET})")

# layout text colours (same accent in hex)
nl = 0
for root, _, fs in os.walk(LY):
    for fn in sorted(fs):
        p = os.path.join(root, fn)
        t = open(p, newline="", encoding="utf-8", errors="surrogateescape").read()
        n = t.lower().count("0x" + SOURCE.lower())
        if not n:
            continue
        for old in ("0x" + SOURCE.lower(), "0x" + SOURCE.upper()):
            t = t.replace(old, "0x" + TARGET.lower())
        open(p, "w", newline="", encoding="utf-8", errors="surrogateescape").write(t)
        nl += n
print(f"layout: {nl} text colours changed")
