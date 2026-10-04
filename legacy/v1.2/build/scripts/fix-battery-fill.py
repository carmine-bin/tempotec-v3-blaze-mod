#!/usr/bin/env python3
# Arregla el relleno del ícono de batería del topbar / pull-down.
#
# CÓMO DIBUJA EL MOTOR (deducido de dos pruebas en device, 2026-08-07): del PNG de `img_focus_path` toma
# las PRIMERAS filas (`h*pct`) y las dibuja pegadas ABAJO del elemento (en `y + h - h*pct`). O sea: el
# borde inferior del relleno siempre queda en `y+h`, y lo que sube/baja es el borde superior.
#   - Con el asset del V3A (canvas 14x20 con el verde metido adentro, filas 6..14) el verde se va CORRIENDO
#     hacia abajo y saliéndose del marco a medida que baja el %, y abajo de ~30% el recorte ya no alcanza
#     el verde => ícono vacío. (Eso es lo que se veía.)
#   - Con el verde macizo centrado tampoco: el motor NO centra, dibuja pegado al origen del elemento.
#
# ARREGLO: que el elemento que el binario maneja sea EXACTAMENTE el hueco del marco. Entonces el recorte
# por porcentaje mapea lineal (11 filas ~ 9% cada una) y nunca se sale:
#   - `topbar_iv_battery` / `pull_down_menu_iv_battery` se mueven a la posición del hueco, con fondo
#     transparente (battery_empty.png) y relleno verde macizo del tamaño del hueco (battery_fill.png).
#   - el marco pasa a un imageview estático aparte (`*_iv_battery_frame`, nombre que el binario no conoce).
#
# COSTO: el marco queda siempre el normal; se pierde el marco ROJO de batería baja (img_path_2), porque
# ese cambio de estado lo hacía el elemento que ahora es el hueco. El % en número sigue al lado.
# Idempotente; si cambia la geometría de battery_bg.png se recalcula solo.
import json, os, re
from PIL import Image

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LG = os.path.join(WS, "theme/theme_port/litegui/theme1")
LY = os.path.join(WS, "theme/theme_port/layout/theme1")
VERDE = (1, 219, 17, 255)

def hueco_de(rel):
    """Geometría del hueco interior de un marco de batería -> (x0, y0, w, h, W, H)."""
    bg = Image.open(os.path.join(LG, rel)).convert("RGBA")
    W, H = bg.size
    px = bg.load()
    filas = [y for y in range(H) if px[0, y][3] > 60 and any(px[x, y][3] <= 60 for x in range(1, W - 1))]
    cols = [x for x in range(W) if all(px[x, y][3] <= 60 for y in filas)]
    assert filas and cols, f"no se detectó el hueco de {rel}"
    return min(cols), min(filas), len(cols), len(filas), W, H


# --- 1. geometría del hueco del marco
hx0, hy0, hw, hh, W, H = hueco_de("topbar/battery_bg.png")

Image.new("RGBA", (hw, hh), VERDE).save(os.path.join(LG, "topbar/battery_fill.png"))
Image.new("RGBA", (hw, hh), (0, 0, 0, 0)).save(os.path.join(LG, "topbar/battery_empty.png"))
print(f"marco {W}x{H}, hueco +{hx0},+{hy0} de {hw}x{hh} -> battery_fill.png / battery_empty.png")

# --- 2. layout: partir el elemento en marco estático + hueco manejado por el binario
objetivos = [("topbar/topbar.view", "topbar_iv_battery"),
             ("hiby_pull_down_menu.view", "pull_down_menu_iv_battery")]
for rel, nombre in objetivos:
    f = os.path.join(LY, rel)
    t = open(f, newline="").read()
    eol = "\r\n" if "\r\n" in t else "\n"
    i = t.index(f'"name":"{nombre}"')
    ini = t.rindex("\n", 0, t.rindex('"imageview"', 0, i)) + 1
    fin = t.index("\n", t.index("},", i)) + 1
    bloque = t[ini:fin]
    if "battery_fill.png" in bloque:
        print(f"{rel}: ya partido")
        continue
    x = int(bloque.split('"x":')[1].split(",")[0])
    y = int(bloque.split('"y":')[1].split(",")[0])
    ind = bloque[:len(bloque) - len(bloque.lstrip("\t"))]      # indentación original del bloque
    def linea(s): return f"{ind}\t{s}{eol}"
    marco = (f'{ind}"imageview":{{{eol}'
             + linea(f'"name":"{nombre}_frame",')
             + linea('"img_path":"topbar\\\\battery_bg.png",')
             + linea(f'"x":{x},') + linea(f'"y":{y},')
             + linea('"imageview":true')
             + f'{ind}}},{eol}')
    hueco = (f'{ind}"imageview":{{{eol}'
             + linea(f'"name":"{nombre}",')
             + linea('"img_path_0":"topbar\\\\battery_empty.png",')
             + linea('"img_path_1":"topbar\\\\battery_empty.png",')
             + linea('"img_path_2":"topbar\\\\battery_empty.png",')
             + linea('"img_focus_path":"topbar\\\\battery_fill.png",')
             + linea(f'"x":{x + hx0},') + linea(f'"y":{y + hy0},')
             + linea('"imageview":true')
             + f'{ind}}},{eol}')
    t = t[:ini] + marco + hueco + t[fin:]
    open(f, "w", newline="").write(t)
    json.loads(t)      # gate de sintaxis
    print(f"{rel}: {nombre} -> marco estático en ({x},{y}) + hueco en ({x + hx0},{y + hy0})")

# --- 3. pantalla de carga con el equipo APAGADO (`hiby_charge.view`)
# Mismo motor, mismo bug, pero acá NO hay que partir nada: el .view del V3A ya trae el marco y el
# relleno como elementos separados (`charge_iv_battery_bg` + `charge_iv_battery`). El problema es que
# `charge\battery.png` es la batería ENTERA (contorno + tapa + relleno, 106x159), así que al recortar
# las primeras filas el motor baja la tapa del propio asset hasta media altura => se ve una segunda
# batería dentro del marco. Arreglo: que `battery.png` sea exactamente el hueco, y que el elemento
# arranque en el hueco. El marco (`_bg`) no se toca y nunca se mueve, así que sirve de origen estable.
cx0, cy0, cw, ch, CW, CH = hueco_de("charge/battery_bg.png")
Image.new("RGBA", (cw, ch), VERDE).save(os.path.join(LG, "charge/battery.png"))

f = os.path.join(LY, "hiby_charge.view")
t = open(f, newline="").read()
bx = int(t.split('"name":"charge_iv_battery_bg"')[1].split('"x":')[1].split(",")[0])
by = int(t.split('"name":"charge_iv_battery_bg"')[1].split('"y":')[1].split(",")[0])
i = t.index('"name":"charge_iv_battery"')
fin = t.index("},", i)
bloque = t[i:fin]
nuevo = re.sub(r'"x":\d+', f'"x":{bx + cx0}', bloque, count=1)
nuevo = re.sub(r'"y":\d+', f'"y":{by + cy0}', nuevo, count=1)
t = t[:i] + nuevo + t[fin:]
open(f, "w", newline="").write(t)
json.loads(t)      # gate de sintaxis

# El relleno al 100% tiene que caber justo en el hueco y no pisar el marco.
assert (cw, ch) == Image.open(os.path.join(LG, "charge/battery.png")).size
assert bx + cx0 + cw <= bx + CW and by + cy0 + ch <= by + CH, "el relleno se sale del marco"
print(f"hiby_charge.view: marco {CW}x{CH} en ({bx},{by}), "
      f"relleno {cw}x{ch} -> ({bx + cx0},{by + cy0})")
