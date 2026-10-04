#!/usr/bin/env python3
# The V3A pull-down gain icon uses the 2-state model (img_path=gain_l + img_focus_path=gain_h),
# but gain has 3 states (L/M/H) and the Blaze binary drives it by INDEX (img_path_0/1/2).
# Fix: replace with img_path_0/1/2 = gain_l/gain_m/gain_h. Runs AFTER importing the donor layout. Idempotent.
import json, os
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f).read()

# isolate the gain element's block
i = t.find('"pull_down_menu_iv_gain"')
assert i > 0
s = t.rfind('{', 0, i); d = 0; j = s
while j < len(t):
    if t[j] == '{': d += 1
    elif t[j] == '}':
        d -= 1
        if d == 0: break
    j += 1
block = t[s:j+1]

if '"img_path_0"' not in block:  # idempotent
    assert block.count('"img_path":') == 1 and block.count('"img_focus_path":') == 1
    block = block.replace('"img_path":', '"img_path_0":')
    block = block.replace('"img_focus_path":', '"img_path_2":')
    # insert the middle state (gain_m) after gain_l; \\\\ in the source = \\ in the file (JSON)
    block = block.replace('gain_l.png",', 'gain_l.png",\n\t\t\t"img_path_1":"menu\\\\gain_m.png",')
    t = t[:s] + block + t[j+1:]
    open(f, "w").write(t)

json.load(open(f))
print("gain -> img_path_0/1/2 (gain_l/m/h); valid JSON")
