#!/usr/bin/env python3
# Restores the CHARGING and LOW BATTERY states to the battery icon without breaking the aligned fill.
#
# WHY A SINGLE ELEMENT CANNOT COME BACK (demonstrated, not assumed): the engine draws the fill by taking
# the FIRST `H*pct` rows of `img_focus_path` and placing them at `y + H - H*pct` (see
# fix-battery-fill.py). With the whole frame as the element, the green sits inside the hole ONLY at 100%
# and slides downwards as the % drops. The only solution with a correct fill is for the element the
# binary drives to BE the hole (fix-battery-fill.py already did that) — but then the frame is a static
# imageview and `img_path_1/2` (charging/low) are no longer shown.
#
# FIX: the states move INSIDE the hole, which is the element the binary does drive.
#   img_path_0 = transparent hole          (normal)
#   img_path_1 = charging bolt             (cropped from the V3A battery_charge_bg.png)
#   img_path_2 = solid red hole            (low battery)
# The frame stays white at all times; the charging/low signal is shown inside the icon.
# Works with any z-order between img_path_N and img_focus_path: if the fill is on top, at low battery
# the green is minimal and the red still shows; if it is below, the red covers the green.
#
# Idempotent. The hole geometry is re-detected from the frame, as in fix-battery-fill.py.
import json, os
from PIL import Image

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LG = os.path.join(WS, "theme/theme_port/litegui/theme1")
LY = os.path.join(WS, "theme/theme_port/layout/theme1")
RED = (255, 0, 0, 255)          # the same red as the V3A battery_low_bg.png

# --- 1. hole geometry (identical to fix-battery-fill.py)
bg = Image.open(os.path.join(LG, "topbar/battery_bg.png")).convert("RGBA")
W, H = bg.size
px = bg.load()
rows = [y for y in range(H) if px[0, y][3] > 60 and any(px[x, y][3] <= 60 for x in range(1, W - 1))]
cols = [x for x in range(W) if all(px[x, y][3] <= 60 for y in rows)]
hx0, hy0, hw, hh = min(cols), min(rows), len(cols), len(rows)
box = (hx0, hy0, hx0 + hw, hy0 + hh)

Image.new("RGBA", (hw, hh), RED).save(os.path.join(LG, "topbar/battery_low.png"))
bolt = Image.open(os.path.join(LG, "topbar/battery_charge_bg.png")).convert("RGBA").crop(box)
assert bolt.getbbox(), "the bolt crop came out empty: check battery_charge_bg.png"
bolt.save(os.path.join(LG, "topbar/battery_charge.png"))
print(f"hole +{hx0},+{hy0} of {hw}x{hh} -> battery_low.png (red) / battery_charge.png (bolt)")

# --- 2. layout: point the hole's img_path_1 / img_path_2 at the new states
for rel, name in [("topbar/topbar.view", "topbar_iv_battery"),
                  ("hiby_pull_down_menu.view", "pull_down_menu_iv_battery")]:
    f = os.path.join(LY, rel)
    t = open(f, newline="").read()
    i = t.index(f'"name":"{name}"')
    end = t.index("\n", t.index("},", i)) + 1
    block = t[i:end]
    assert "battery_empty.png" in block, f"{rel}: {name} is not split; run fix-battery-fill.py first"
    new = (block.replace('"img_path_1":"topbar\\\\battery_empty.png"',
                         '"img_path_1":"topbar\\\\battery_charge.png"')
                .replace('"img_path_2":"topbar\\\\battery_empty.png"',
                         '"img_path_2":"topbar\\\\battery_low.png"'))
    t = t[:i] + new + t[end:]
    open(f, "w", newline="").write(t)
    json.loads(t)      # syntax gate
    print(f"{rel}: {name} -> charging=battery_charge.png, low=battery_low.png")

# --- 3. the two states are NOT tinted (if the red turns blue it signals nothing)
nsl = os.path.join(LG, "no_skin_list.txt")
d = open(nsl, "rb").read()
for e in (b"topbar\\battery_low.png", b"topbar\\battery_charge.png"):
    if e not in d:
        d += e + b"\r\n"
        print(f"no_skin_list += {e.decode()}")
open(nsl, "wb").write(d)
