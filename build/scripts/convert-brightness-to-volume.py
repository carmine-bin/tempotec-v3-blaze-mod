#!/usr/bin/env python3
# El pull-down del V3A reemplazó el slider de VOLUMEN del stock por uno de BRILLO, que el binario del Blaze
# no cablea (dead). Este script convierte ese slider de brillo en el slider de VOLUMEN funcional del stock:
#   - pull_down_menu_bklight_pb        -> pull_down_menu_vol_pb   (el binario SÍ lo cablea a volumen)
#   - pull_down_menu_iv_bklight_icon   -> pull_down_menu_iv_vol   (ícono que el binario actualiza)
#   - ícono: menu\blk.png (brillo)     -> menu\speaker.png        (speaker)
# Los assets del slider ya eran estilo-volumen (menu\vol_bg/cursor/vol_progress). Corre DESPUÉS de importar el layout donante.
import json, os
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f).read()
assert t.count('"pull_down_menu_bklight_pb"') == 1, "pb no único"
assert t.count('"pull_down_menu_iv_bklight_icon"') == 1, "icono no único"
assert t.count('blk.png') == 1, "blk.png no único"
t = t.replace('"pull_down_menu_bklight_pb"', '"pull_down_menu_vol_pb"')
t = t.replace('"pull_down_menu_iv_bklight_icon"', '"pull_down_menu_iv_vol"')
t = t.replace('blk.png', 'speaker.png')
open(f, "w").write(t)
json.load(open(f))
print("brillo -> volumen (slider + icono + asset); JSON válido")
