#!/usr/bin/env python3
# Final state of the pull-down. Usage:
#
#   restore-pulldown-controls.py --slider=vol         (default) a single slider: VOLUME
#   restore-pulldown-controls.py --slider=brightness            a single slider: BRIGHTNESS (experiment)
#
# Why ONE slider: the binary lays out the pull-down icons in its own grid (it ignores the .view y) and
# with the toggles visible the second row lands at ~y150-210. Tested on the device 2026-08-07: a second
# slider there ends up OVERLAPPING the icons. The card has room for one slider, the bottom one (y=225).
#
# BRIGHTNESS: WORKS (device 2026-08-07) with `--slider=brightness`. The key was the element's NAME, not
# its position or assets (see the block of names further down).
#
# Volume slider icon: menu\speaker.png is the STOCK asset (20x20, crude next to the V3A ones and it looks
# pixelated) -> touch_set\vol.png (V3A, 24x24, same size as the V3A brightness icon).
#
# Idempotent. Run AFTER importing the donor layout + convert-brightness-to-volume + fix-pulldown-gain.
import json, os, sys

MODE = "vol"
for a in sys.argv[1:]:
    if a.startswith("--slider="):
        MODE = a.split("=", 1)[1]
assert MODE in ("vol", "brightness"), "use --slider=vol | --slider=brightness"

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f, newline="").read()
eol = "\r\n" if "\r\n" in t else "\n"

def block(first_name, text):
    """return (start, end) of the element whose "name" is first_name, including the trailing comma"""
    i = text.index(f'"name":"{first_name}"')
    start = text.rindex('"', 0, text.rindex(":{", 0, i))
    start = text.rindex("\n", 0, start) + 1
    end = text.index("},", i) + 2
    end = text.index("\n", end) + 1
    return start, end

def remove(name):
    global t
    if f'"name":"{name}"' not in t:
        return False
    start, end = block(name, t)
    t = t[:start] + t[end:]
    return True

# --- 1. a single slider, in the bottom position (y=222/225), with the matching icon+bar pair
# CAREFUL with the names (tested on the device 2026-08-07, each one cost a reboot+apply cycle):
#  - the brightness bar ONLY works as "pull_down_menu_pb". With "pull_down_menu_bklight_pb" the
#    element is drawn and can be dragged, but the binary never installs its callback (sysfs stays at 0).
#    Both names end up in the same handler, so whatever cuts it off happens earlier, inside the binary.
#  - the icon must NOT be called "pull_down_menu_iv_bklight": that name is in the icon table the
#    binary drives (.data 0x92e880) and, without its active function, it does not draw it. With the V3A
#    name ("..._bklight_icon"), which the binary does not know, it stays a static image and is visible.
ICON = {"vol": ("pull_down_menu_iv_vol", "touch_set\\\\vol.png"),
        "brightness": ("pull_down_menu_iv_bklight_icon", "menu\\\\blk.png")}[MODE]
BAR = {"vol": "pull_down_menu_vol_pb", "brightness": "pull_down_menu_pb"}[MODE]
SPARE_ICON = {"vol": "pull_down_menu_iv_bklight_icon", "brightness": "pull_down_menu_iv_vol"}[MODE]
SPARE_BAR = {"vol": "pull_down_menu_pb", "brightness": "pull_down_menu_vol_pb"}[MODE]

new = (
    '\t\t"imageview":{\n'
    f'\t\t\t"name":"{ICON[0]}",\n'
    f'\t\t\t"img_path":"{ICON[1]}",\n'
    '\t\t\t"x":24,\n'
    '\t\t\t"y":223,\n'
    '\t\t\t"color_mode":"color_565",\n'
    '\t\t\t"imageview":true\n'
    '\t\t},\n'
    '\t\t"progress_bar":{\n'
    f'\t\t\t"name":"{BAR}",\n'
    '\t\t\t"img_path_0":"menu\\\\vol_bg.png",\n'
    '\t\t\t"img_path_1":"menu\\\\cursor.png",\n'
    '\t\t\t"img_focus_path_0":"menu\\\\vol_progress.png",\n'
    '\t\t\t"style":"horizon",\n'
    '\t\t\t"x":56,\n'
    '\t\t\t"y":225,\n'
    '\t\t\t"w":239,\n'
    '\t\t\t"h":20,\n'
    '\t\t\t"touch_x":30,\n'
    '\t\t\t"touch_y":210,\n'
    '\t\t\t"touch_w":290,\n'
    '\t\t\t"touch_h":50,\n'
    '\t\t\t"color_mode":"color_565",\n'
    '\t\t\t"progress_bar":true\n'
    '\t\t},\n'
).replace("\n", eol)

# remove ALL the names this script handles (including the ones that did not work), so that re-running
# it or switching mode does not leave orphaned elements stacked in the same position
for nm in ("pull_down_menu_iv_vol", "pull_down_menu_vol_pb", "pull_down_menu_iv_bklight_icon",
           "pull_down_menu_iv_bklight", "pull_down_menu_pb", "pull_down_menu_bklight_pb"):
    remove(nm)
i = t.index('\t\t"imageview":{')          # before the first imageview
t = t[:i] + new + t[i:]
print(f"single slider: {MODE} ({ICON[0]} + {BAR}) at y=220/225")
