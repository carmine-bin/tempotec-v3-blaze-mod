#!/usr/bin/env python3
# The V3A pull-down replaced the stock VOLUME slider with a BRIGHTNESS one, which the Blaze binary does
# not wire up (dead). This script turns that brightness slider into the stock's working VOLUME slider:
#   - pull_down_menu_bklight_pb        -> pull_down_menu_vol_pb   (the binary DOES wire this to volume)
#   - pull_down_menu_iv_bklight_icon   -> pull_down_menu_iv_vol   (icon the binary updates)
#   - icon: menu\blk.png (brightness)  -> menu\speaker.png        (speaker)
# The slider assets were already volume-style (menu\vol_bg/cursor/vol_progress). Run AFTER importing the donor layout.
import json, os
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f).read()
assert t.count('"pull_down_menu_bklight_pb"') == 1, "pb not unique"
assert t.count('"pull_down_menu_iv_bklight_icon"') == 1, "icon not unique"
assert t.count('blk.png') == 1, "blk.png not unique"
t = t.replace('"pull_down_menu_bklight_pb"', '"pull_down_menu_vol_pb"')
t = t.replace('"pull_down_menu_iv_bklight_icon"', '"pull_down_menu_iv_vol"')
t = t.replace('blk.png', 'speaker.png')
open(f, "w").write(t)
json.load(open(f))
print("brightness -> volume (slider + icon + asset); valid JSON")
