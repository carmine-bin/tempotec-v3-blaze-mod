#!/usr/bin/env python3
# Generates settings/gain_mid.png in V3A style. The V3A gain icons are a SWITCH: a pill + a white knob
# with the letter inside (gain_low = grey pill, knob on the LEFT with "L"; gain_high = blue pill, knob
# on the RIGHT with "H"). The Blaze middle state does not exist in the V3A, so it is built by cloning
# gain_high: a clean blue pill (left half mirrored; the pill is symmetric) + the same knob CENTRED + a
# blue "M" inside.
# The V3A has 2 gain states and the Blaze has 3; the listview indexes it by img_path_N, so without this
# file the middle state has no icon in Settings -> Music. Idempotent (always starts from gain_high).
import os
from PIL import Image, ImageDraw, ImageFont

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LG = os.path.join(WS, "theme/theme_port/litegui/theme1/settings")
src = Image.open(os.path.join(LG, "gain_high.png")).convert("RGBA")
W, H = src.size
BLUE = (0, 159, 246, 255)
FONT = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"

# --- 1. knob: box of the white circle in gain_high (right side), cleared of the "H"
KX0, KY0, KS = 11, 1, 14                      # x, y, side of the knob box
CX, CY, RIN = (KS - 1) / 2, (KS - 1) / 2, 5.6  # centre and "inner" radius (inside the circle's stroke)
knob = src.crop((KX0, KY0, KX0 + KS, KY0 + KS)).copy()
kp = knob.load()
for x in range(KS):
    for y in range(KS):
        if (x - CX) ** 2 + (y - CY) ** 2 <= RIN ** 2:
            kp[x, y] = (255, 255, 255, 255)     # erase the letter -> solid white knob

# --- 2. clean blue pill: left half (no knob) mirrored to the right
pill = src.copy()
pp = pill.load()
sp = src.load()
for x in range(W // 2, W):
    for y in range(H):
        pp[x, y] = sp[W - 1 - x, y]

# --- 3. centred knob + blue "M" inside
kx = (W - KS) // 2
pill.alpha_composite(knob, (kx, KY0))
# 8x8 box inside the 14-pixel knob (the original "H" is 6x8, but the M needs width to be legible),
# centred with integers: even sizes in an even box avoid the half pixel that shifted it.
GW, GH = 8, 8
tmp = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
ImageDraw.Draw(tmp).text((40, 40), "M", font=ImageFont.truetype(FONT, 40), fill=BLUE, anchor="mm")
m = tmp.crop(tmp.getbbox()).resize((GW, GH), Image.LANCZOS)
pill.alpha_composite(m, (kx + (KS - GW) // 2, KY0 + (KS - GH) // 2))

pill.save(os.path.join(LG, "gain_mid.png"))
print(f"settings/gain_mid.png: blue pill + centred knob (x{kx}) + M {GW}x{GH}")

# --- 4. the layout: the V3A left listview_class_iv_switch without img_path_6 (index of the middle state)
LV = os.path.join(WS, "theme/theme_port/layout/theme1/listview/vg_listview_class.listview")
t = open(LV, newline="").read()          # newline="" -> keep the file's CRLF line endings
KEY = '"img_path_6":"settings\\\\gain_mid.png",'
if KEY in t:
    print("listview: img_path_6 already present")
else:
    anchor = '"img_path_5":"settings\\\\lo.png",'
    assert t.count(anchor) == 1, "img_path_5 anchor not unique"
    i = t.index(anchor)
    indent = t[t.rindex("\n", 0, i) + 1:i]          # same indentation (tabs) as the anchor line
    eol = "\r\n" if t[i + len(anchor):i + len(anchor) + 2] == "\r\n" else "\n"
    t = t.replace(anchor, anchor + eol + indent + KEY, 1)
    open(LV, "w", newline="").write(t)
    print("listview: + img_path_6 -> settings\\gain_mid.png")
import json
json.loads(open(LV, encoding="utf-8", errors="replace").read())   # syntax gate
