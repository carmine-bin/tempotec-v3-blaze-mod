#!/usr/bin/env python3
# Makes the V3A pull-down brightness slider work with the Blaze binary:
#  1) adds "move_cb":1 to the progress_bar (without it, dragging never fires the backlight_set handler).
#  2) renames the icon pull_down_menu_iv_bklight_icon -> pull_down_menu_iv_bklight (the name the binary looks up).
# Must run AFTER importing the donor layout (which overwrites the layout with raw V3A). Idempotent.
import json, sys, os
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f).read()

# 2) rename the icon (idempotent: only if the old name is still there)
if "pull_down_menu_iv_bklight_icon" in t:
    assert t.count("pull_down_menu_iv_bklight_icon") == 1
    t = t.replace("pull_down_menu_iv_bklight_icon", "pull_down_menu_iv_bklight")

# 1) add move_cb to the pb (idempotent: only if not already present)
anchor = '"name":"pull_down_menu_bklight_pb",'
assert t.count(anchor) == 1, "pb anchor not unique"
if '"move_cb"' not in t[t.find(anchor):t.find("progress_bar", t.find(anchor))]:
    t = t.replace(anchor, anchor + '\n\t\t\t"move_cb":1,')

open(f, "w").write(t)
json.load(open(f))  # validate syntax
print("brightness patched (move_cb + icon rename); valid JSON")
