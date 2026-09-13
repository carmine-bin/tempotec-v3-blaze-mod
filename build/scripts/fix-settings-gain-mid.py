#!/usr/bin/env python3
# Genera settings/gain_mid.png en estilo V3A. Los iconos de ganancia del V3A son un SWITCH: pastilla + perilla
# blanca con la letra dentro (gain_low = pastilla gris, perilla a la IZQUIERDA con "L"; gain_high = pastilla
# azul, perilla a la DERECHA con "H"). El estado medio del Blaze no existe en el V3A -> se arma clonando
# gain_high: pastilla azul limpia (mitad izquierda espejada, la pastilla es simetrica) + la misma perilla
# CENTRADA + una "M" azul dentro.
# El V3A trae ganancia de 2 estados y el Blaze de 3; el listview la indexa por img_path_N, asi que sin este
# archivo el estado medio queda sin icono en Ajustes -> Musica. Idempotente (siempre parte de gain_high).
import os
from PIL import Image, ImageDraw, ImageFont

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LG = os.path.join(WS, "theme/theme_port/litegui/theme1/settings")
src = Image.open(os.path.join(LG, "gain_high.png")).convert("RGBA")
W, H = src.size
BLUE = (0, 159, 246, 255)
FONT = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"

# --- 1. perilla: caja de la circunferencia blanca en gain_high (derecha), limpiada de la "H"
KX0, KY0, KS = 11, 1, 14                      # x, y, lado de la caja de la perilla
CX, CY, RIN = (KS - 1) / 2, (KS - 1) / 2, 5.6  # centro y radio "interior" (dentro del trazo del circulo)
knob = src.crop((KX0, KY0, KX0 + KS, KY0 + KS)).copy()
kp = knob.load()
for x in range(KS):
    for y in range(KS):
        if (x - CX) ** 2 + (y - CY) ** 2 <= RIN ** 2:
            kp[x, y] = (255, 255, 255, 255)     # borra la letra -> perilla blanca llena

# --- 2. pastilla azul limpia: mitad izquierda (sin perilla) espejada a la derecha
pill = src.copy()
pp = pill.load()
sp = src.load()
for x in range(W // 2, W):
    for y in range(H):
        pp[x, y] = sp[W - 1 - x, y]

# --- 3. perilla centrada + "M" azul dentro
kx = (W - KS) // 2
pill.alpha_composite(knob, (kx, KY0))
# Caja 8x8 dentro de la perilla de 14 (la "H" original es 6x8, pero la M necesita ancho para leerse),
# centrada con enteros: con medidas pares contra caja par no queda el medio pixel que la corria.
GW, GH = 8, 8
tmp = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
ImageDraw.Draw(tmp).text((40, 40), "M", font=ImageFont.truetype(FONT, 40), fill=BLUE, anchor="mm")
m = tmp.crop(tmp.getbbox()).resize((GW, GH), Image.LANCZOS)
pill.alpha_composite(m, (kx + (KS - GW) // 2, KY0 + (KS - GH) // 2))

pill.save(os.path.join(LG, "gain_mid.png"))
print(f"settings/gain_mid.png: pastilla azul + perilla centrada (x{kx}) + M {GW}x{GH}")

# --- 4. el layout: el V3A dejo listview_class_iv_switch sin img_path_6 (indice del estado medio)
LV = os.path.join(WS, "theme/theme_port/layout/theme1/listview/vg_listview_class.listview")
t = open(LV, newline="").read()          # newline="" -> preserva los CRLF del archivo
KEY = '"img_path_6":"settings\\\\gain_mid.png",'
if KEY in t:
    print("listview: img_path_6 ya estaba")
else:
    anchor = '"img_path_5":"settings\\\\lo.png",'
    assert t.count(anchor) == 1, "ancla img_path_5 no unica"
    i = t.index(anchor)
    indent = t[t.rindex("\n", 0, i) + 1:i]          # misma indentacion (tabs) que la linea ancla
    eol = "\r\n" if t[i + len(anchor):i + len(anchor) + 2] == "\r\n" else "\n"
    t = t.replace(anchor, anchor + eol + indent + KEY, 1)
    open(LV, "w", newline="").write(t)
    print("listview: + img_path_6 -> settings\\gain_mid.png")
import json
json.loads(open(LV, encoding="utf-8", errors="replace").read())   # gate de sintaxis
