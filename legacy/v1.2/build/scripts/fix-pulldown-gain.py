#!/usr/bin/env python3
# El icono de ganancia del pull-down V3A usa el modelo 2-estados (img_path=gain_l + img_focus_path=gain_h),
# pero la ganancia tiene 3 estados (L/M/H) y el binario del Blaze la maneja por INDICE (img_path_0/1/2).
# Fix: reemplazar por img_path_0/1/2 = gain_l/gain_m/gain_h. Corre DESPUÉS de importar el layout donante. Idempotente.
import json, os
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f).read()

# aislar el bloque del elemento gain
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

if '"img_path_0"' not in block:  # idempotente
    assert block.count('"img_path":') == 1 and block.count('"img_focus_path":') == 1
    block = block.replace('"img_path":', '"img_path_0":')
    block = block.replace('"img_focus_path":', '"img_path_2":')
    # insertar el estado medio (gain_m) tras gain_l; \\\\ en el fuente = \\ en el archivo (JSON)
    block = block.replace('gain_l.png",', 'gain_l.png",\n\t\t\t"img_path_1":"menu\\\\gain_m.png",')
    t = t[:s] + block + t[j+1:]
    open(f, "w").write(t)

json.load(open(f))
print("ganancia -> img_path_0/1/2 (gain_l/m/h); JSON válido")
