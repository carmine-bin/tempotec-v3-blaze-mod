#!/usr/bin/env python3
# Genera menu/gain_m.png en estilo V3A (badge azul #009FF6 + parlante + letra blanca) clonando gain_h:
# borra SOLO la letra (preserva el badge redondo) y compone una "M" ANGOSTA/ALARGADA (comprimida en ancho) del
# tamaño de la H, centrada en la misma caja que L/H -> alineada, con margen al parlante y al borde del badge.
import os
from PIL import Image, ImageDraw, ImageFont
WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LG = os.path.join(WS, "staging/theme_port/litegui/theme1/menu")
im = Image.open(os.path.join(LG, "gain_h.png")).convert("RGBA")
W, H = im.size
px = im.load()
BLUE = (0, 159, 246, 255)
for x in range(29, W):           # borrar solo la letra (R>80), preservar badge
    for y in range(H):
        if px[x, y][0] > 80:
            px[x, y] = BLUE

FONT = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
TARGET_W, TARGET_H = 16, 22       # angosta (16) y un toque alta (22) = alargada; alineada con la H (16x21)
CX, CY = 37, 27                   # centro de la H original (x30..45, y17..37)

tmp = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
ImageDraw.Draw(tmp).text((40, 40), "M", font=ImageFont.truetype(FONT, 40), fill=(255, 255, 255, 255), anchor="mm")
m = tmp.crop(tmp.getbbox()).resize((TARGET_W, TARGET_H), Image.LANCZOS)   # comprimir ancho -> alargada
im.alpha_composite(m, (round(CX - TARGET_W / 2), round(CY - TARGET_H / 2)))
im.save(os.path.join(LG, "gain_m.png"))
print(f"gain_m: M alargada {TARGET_W}x{TARGET_H} en x[{round(CX-TARGET_W/2)}..{round(CX+TARGET_W/2)}] y[{round(CY-TARGET_H/2)}..{round(CY+TARGET_H/2)}]")
