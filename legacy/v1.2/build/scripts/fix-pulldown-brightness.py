#!/usr/bin/env python3
# Hace funcional el slider de brillo del pull-down del V3A en el binario del Blaze:
#  1) agrega "move_cb":1 al progress_bar (sin esto el arrastre no dispara el handler backlight_set).
#  2) renombra el icono pull_down_menu_iv_bklight_icon -> pull_down_menu_iv_bklight (nombre que el binario busca).
# Debe correrse DESPUÉS de importar el layout donante (que sobrescribe el layout con V3A crudo). Idempotente.
import json, sys, os
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f).read()

# 2) rename icono (idempotente: solo si aún está el nombre viejo)
if "pull_down_menu_iv_bklight_icon" in t:
    assert t.count("pull_down_menu_iv_bklight_icon") == 1
    t = t.replace("pull_down_menu_iv_bklight_icon", "pull_down_menu_iv_bklight")

# 1) agregar move_cb al pb (idempotente: solo si no está ya)
anchor = '"name":"pull_down_menu_bklight_pb",'
assert t.count(anchor) == 1, "ancla del pb no única"
if '"move_cb"' not in t[t.find(anchor):t.find("progress_bar", t.find(anchor))]:
    t = t.replace(anchor, anchor + '\n\t\t\t"move_cb":1,')

open(f, "w").write(t)
json.load(open(f))  # valida sintaxis
print("brillo parcheado (move_cb + rename icono); JSON válido")
