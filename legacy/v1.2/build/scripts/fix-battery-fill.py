#!/usr/bin/env python3
# Fixes the fill of the battery icon in the topbar / pull-down.
#
# HOW THE ENGINE DRAWS IT (deduced from two on-device tests, 2026-08-07): from the `img_focus_path` PNG it
# takes the FIRST rows (`h*pct`) and draws them anchored to the BOTTOM of the element (at `y + h - h*pct`).
# So the bottom edge of the fill always sits at `y+h`, and it is the top edge that moves up and down.
#   - With the V3A asset (14x20 canvas with the green inset, rows 6..14) the green SLIDES downwards and
#     out of the frame as the % drops, and below ~30% the crop no longer reaches the green => empty
#     icon. (That is what was showing.)
#   - A solid, centred green does not work either: the engine does NOT centre, it draws from the element origin.
#
# FIX: make the element the binary drives EXACTLY the hole of the frame. The percentage crop then maps
# linearly (11 rows, ~9% each) and never overflows:
#   - `topbar_iv_battery` / `pull_down_menu_iv_battery` move to the position of the hole, with a
#     transparent background (battery_empty.png) and a solid green fill the size of the hole (battery_fill.png).
#   - the frame becomes a separate static imageview (`*_iv_battery_frame`, a name the binary does not know).
#
# COST: the frame is always the normal one; the RED low-battery frame (img_path_2) is lost, because that
# state change was done by the element that is now the hole. The numeric % stays alongside.
# Idempotent; if the geometry of battery_bg.png changes it is recomputed automatically.
import json, os, re
from PIL import Image

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LG = os.path.join(WS, "theme/theme_port/litegui/theme1")
LY = os.path.join(WS, "theme/theme_port/layout/theme1")
GREEN = (1, 219, 17, 255)

def hole_of(rel):
    """Geometry of the inner hole of a battery frame -> (x0, y0, w, h, W, H)."""
    bg = Image.open(os.path.join(LG, rel)).convert("RGBA")
    W, H = bg.size
    px = bg.load()
    rows = [y for y in range(H) if px[0, y][3] > 60 and any(px[x, y][3] <= 60 for x in range(1, W - 1))]
    cols = [x for x in range(W) if all(px[x, y][3] <= 60 for y in rows)]
    assert rows and cols, f"could not detect the hole of {rel}"
    return min(cols), min(rows), len(cols), len(rows), W, H


# --- 1. geometry of the frame's hole
hx0, hy0, hw, hh, W, H = hole_of("topbar/battery_bg.png")

Image.new("RGBA", (hw, hh), GREEN).save(os.path.join(LG, "topbar/battery_fill.png"))
Image.new("RGBA", (hw, hh), (0, 0, 0, 0)).save(os.path.join(LG, "topbar/battery_empty.png"))
print(f"frame {W}x{H}, hole +{hx0},+{hy0} of {hw}x{hh} -> battery_fill.png / battery_empty.png")

# --- 2. layout: split the element into a static frame + a hole driven by the binary
targets = [("topbar/topbar.view", "topbar_iv_battery"),
           ("hiby_pull_down_menu.view", "pull_down_menu_iv_battery")]
for rel, name in targets:
    f = os.path.join(LY, rel)
    t = open(f, newline="").read()
    eol = "\r\n" if "\r\n" in t else "\n"
    i = t.index(f'"name":"{name}"')
    start = t.rindex("\n", 0, t.rindex('"imageview"', 0, i)) + 1
    end = t.index("\n", t.index("},", i)) + 1
    block = t[start:end]
    if "battery_fill.png" in block:
        print(f"{rel}: already split")
        continue
    x = int(block.split('"x":')[1].split(",")[0])
    y = int(block.split('"y":')[1].split(",")[0])
    ind = block[:len(block) - len(block.lstrip("\t"))]      # original indentation of the block
    def line(s): return f"{ind}\t{s}{eol}"
    frame = (f'{ind}"imageview":{{{eol}'
             + line(f'"name":"{name}_frame",')
             + line('"img_path":"topbar\\\\battery_bg.png",')
             + line(f'"x":{x},') + line(f'"y":{y},')
             + line('"imageview":true')
             + f'{ind}}},{eol}')
    hole = (f'{ind}"imageview":{{{eol}'
            + line(f'"name":"{name}",')
            + line('"img_path_0":"topbar\\\\battery_empty.png",')
            + line('"img_path_1":"topbar\\\\battery_empty.png",')
            + line('"img_path_2":"topbar\\\\battery_empty.png",')
            + line('"img_focus_path":"topbar\\\\battery_fill.png",')
            + line(f'"x":{x + hx0},') + line(f'"y":{y + hy0},')
            + line('"imageview":true')
            + f'{ind}}},{eol}')
    t = t[:start] + frame + hole + t[end:]
    open(f, "w", newline="").write(t)
    json.loads(t)      # syntax gate
    print(f"{rel}: {name} -> static frame at ({x},{y}) + hole at ({x + hx0},{y + hy0})")

# --- 3. charging screen with the device OFF (`hiby_charge.view`)
# Same engine, same bug, but here nothing needs splitting: the V3A .view already has the frame and the
# fill as separate elements (`charge_iv_battery_bg` + `charge_iv_battery`). The problem is that
# `charge\battery.png` is the WHOLE battery (outline + cap + fill, 106x159), so when the engine crops
# the first rows it pulls the asset's own cap down to half height => a second battery appears inside
# the frame. Fix: make `battery.png` exactly the hole, and start the element at the hole. The frame
# (`_bg`) is left alone and never moves, so it serves as a stable origin.
cx0, cy0, cw, ch, CW, CH = hole_of("charge/battery_bg.png")
Image.new("RGBA", (cw, ch), GREEN).save(os.path.join(LG, "charge/battery.png"))

f = os.path.join(LY, "hiby_charge.view")
t = open(f, newline="").read()
bx = int(t.split('"name":"charge_iv_battery_bg"')[1].split('"x":')[1].split(",")[0])
by = int(t.split('"name":"charge_iv_battery_bg"')[1].split('"y":')[1].split(",")[0])
i = t.index('"name":"charge_iv_battery"')
end = t.index("},", i)
block = t[i:end]
new = re.sub(r'"x":\d+', f'"x":{bx + cx0}', block, count=1)
new = re.sub(r'"y":\d+', f'"y":{by + cy0}', new, count=1)
t = t[:i] + new + t[end:]
open(f, "w", newline="").write(t)
json.loads(t)      # syntax gate

# At 100% the fill must fit exactly in the hole and not cover the frame.
assert (cw, ch) == Image.open(os.path.join(LG, "charge/battery.png")).size
assert bx + cx0 + cw <= bx + CW and by + cy0 + ch <= by + CH, "the fill overflows the frame"
print(f"hiby_charge.view: frame {CW}x{CH} at ({bx},{by}), "
      f"fill {cw}x{ch} -> ({bx + cx0},{by + cy0})")
