#!/usr/bin/env python3
# Devuelve los estados CARGANDO y BATERÍA BAJA al ícono de batería, sin romper el relleno alineado.
#
# POR QUÉ NO SE PUEDE VOLVER AL ELEMENTO ÚNICO (demostrado, no supuesto): el motor dibuja el relleno
# tomando las PRIMERAS `H*pct` filas de `img_focus_path` y pegándolas en `y + H - H*pct` (ver
# fix-battery-fill.py). Con el marco entero como elemento, el verde queda dentro del hueco SOLO al 100%
# y se va corriendo hacia abajo al bajar el %. La única solución con relleno correcto es que el elemento
# que maneja el binario SEA el hueco (eso ya lo hizo fix-battery-fill.py) — pero entonces el marco es un
# imageview estático y `img_path_1/2` (carga/baja) dejaron de verse.
#
# ARREGLO: los estados se mueven ADENTRO del hueco, que es el elemento que el binario sí maneja.
#   img_path_0 = hueco transparente        (normal)
#   img_path_1 = rayo de carga             (recortado del battery_charge_bg.png del V3A)
#   img_path_2 = hueco rojo macizo         (batería baja)
# El marco sigue siendo blanco siempre; la señal de carga/baja va en el interior del ícono.
# Funciona con cualquier z-order entre img_path_N y img_focus_path: si el relleno va encima, con batería
# baja el verde es mínimo y el rojo se ve igual; si va debajo, el rojo tapa el verde.
#
# Idempotente. La geometría del hueco se redetecta del marco, igual que en fix-battery-fill.py.
import json, os
from PIL import Image

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LG = os.path.join(WS, "staging/theme_port/litegui/theme1")
LY = os.path.join(WS, "staging/theme_port/layout/theme1")
ROJO = (255, 0, 0, 255)          # el mismo rojo del battery_low_bg.png del V3A

# --- 1. geometría del hueco (idéntica a fix-battery-fill.py)
bg = Image.open(os.path.join(LG, "topbar/battery_bg.png")).convert("RGBA")
W, H = bg.size
px = bg.load()
filas = [y for y in range(H) if px[0, y][3] > 60 and any(px[x, y][3] <= 60 for x in range(1, W - 1))]
cols = [x for x in range(W) if all(px[x, y][3] <= 60 for y in filas)]
hx0, hy0, hw, hh = min(cols), min(filas), len(cols), len(filas)
caja = (hx0, hy0, hx0 + hw, hy0 + hh)

Image.new("RGBA", (hw, hh), ROJO).save(os.path.join(LG, "topbar/battery_low.png"))
rayo = Image.open(os.path.join(LG, "topbar/battery_charge_bg.png")).convert("RGBA").crop(caja)
assert rayo.getbbox(), "el recorte del rayo salió vacío: revisá battery_charge_bg.png"
rayo.save(os.path.join(LG, "topbar/battery_charge.png"))
print(f"hueco +{hx0},+{hy0} de {hw}x{hh} -> battery_low.png (rojo) / battery_charge.png (rayo)")

# --- 2. layout: apuntar img_path_1 / img_path_2 del hueco a los nuevos estados
for rel, nombre in [("topbar/topbar.view", "topbar_iv_battery"),
                    ("hiby_pull_down_menu.view", "pull_down_menu_iv_battery")]:
    f = os.path.join(LY, rel)
    t = open(f, newline="").read()
    i = t.index(f'"name":"{nombre}"')
    fin = t.index("\n", t.index("},", i)) + 1
    bloque = t[i:fin]
    assert "battery_empty.png" in bloque, f"{rel}: {nombre} no está partido; corré antes fix-battery-fill.py"
    nuevo = (bloque.replace('"img_path_1":"topbar\\\\battery_empty.png"',
                            '"img_path_1":"topbar\\\\battery_charge.png"')
                   .replace('"img_path_2":"topbar\\\\battery_empty.png"',
                            '"img_path_2":"topbar\\\\battery_low.png"'))
    t = t[:i] + nuevo + t[fin:]
    open(f, "w", newline="").write(t)
    json.loads(t)      # gate de sintaxis
    print(f"{rel}: {nombre} -> carga=battery_charge.png, baja=battery_low.png")

# --- 3. los dos estados NO se tiñen (si el rojo se vuelve azul no señala nada)
nsl = os.path.join(LG, "no_skin_list.txt")
d = open(nsl, "rb").read()
for e in (b"topbar\\battery_low.png", b"topbar\\battery_charge.png"):
    if e not in d:
        d += e + b"\r\n"
        print(f"no_skin_list += {e.decode()}")
open(nsl, "wb").write(d)
