#!/usr/bin/env python3
# Cambia el color de acento del tema V3A. El V3A usa UN solo acento, #009FF6, horneado en los PNG
# (barras de progreso, toggles encendidos, pastillas de ganancia, teclado, botón de play, etc.) y en
# 12 colores de texto del layout.
#
#   recolor-accent.py                      -> al morado del selector de fábrica (#6B31A5, color_4.png)
#   recolor-accent.py --to=RRGGBB          -> a otro color
#   recolor-accent.py --from=RRGGBB --to=…  -> si ya lo recoloreaste antes, hay que decirle de dónde sale
#
# No es un reemplazo plano de color: convierte a HSV y aplica el MISMO delta de tono y la misma escala de
# saturación/brillo a todos los píxeles del rango del acento, así que sombras, degradés y antialias
# mantienen su relación (si fuera reemplazo plano, los bordes suavizados quedarían con halo azul).
import colorsys, os, sys
from PIL import Image

# OJO, el ida y vuelta NO es simétrico con el umbral por defecto: al recolorear se multiplica la saturación
# por KS, así que un píxel apenas por encima del piso (p. ej. #cfedfd, s=0.18) cruza al otro lado con s=0.127
# y en el viaje de vuelta queda POR DEBAJO del piso -> no se revierte y queda del color viejo desaturado
# (se vio: 22 px por archivo en 80 archivos, en los brillos de los íconos `_s`). Para revertir un recoloreo
# hay que bajar el piso: --smin=0.08
ORIGEN, DESTINO, SMIN = "009FF6", "6B31A5", 0.15
for a in sys.argv[1:]:
    if a.startswith("--from="): ORIGEN = a.split("=", 1)[1].lstrip("#")
    if a.startswith("--to="):   DESTINO = a.split("=", 1)[1].lstrip("#")
    if a.startswith("--smin="): SMIN = float(a.split("=", 1)[1])

def hsv(hexs):
    r, g, b = (int(hexs[i:i+2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)

h0, s0, v0 = hsv(ORIGEN)
h1, s1, v1 = hsv(DESTINO)
DH, KS, KV = h1 - h0, s1 / s0, v1 / v0
VENTANA = 0.04          # ± en tono: agarra el acento y sus variantes, no toca el resto de la paleta

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LG = os.path.join(WS, "staging/theme_port/litegui/theme1")
LY = os.path.join(WS, "staging/theme_port/layout/theme1")

def mueve(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if abs((h - h0 + 0.5) % 1.0 - 0.5) > VENTANA or s < SMIN or v < 0.12:
        return None
    r2, g2, b2 = colorsys.hsv_to_rgb((h + DH) % 1.0, min(1.0, s * KS), min(1.0, v * KV))
    return round(r2 * 255), round(g2 * 255), round(b2 * 255)

cache = {}
nf = npx = 0
for root, _, fs in os.walk(LG):
    for fn in sorted(fs):
        if not fn.endswith(".png"):
            continue
        p = os.path.join(root, fn)
        try: im = Image.open(p).convert("RGBA")
        except Exception: continue
        px = im.load()
        W, H = im.size
        tocados = 0
        for y in range(H):
            for x in range(W):
                r, g, b, a = px[x, y]
                if a < 12:
                    continue
                k = (r, g, b)
                if k not in cache:
                    cache[k] = mueve(r, g, b)
                nuevo = cache[k]
                if nuevo:
                    px[x, y] = (*nuevo, a)
                    tocados += 1
        if tocados:
            im.save(p)
            nf += 1; npx += tocados
print(f"PNG: {nf} archivos recoloreados, {npx} px  ({ORIGEN} -> {DESTINO})")

# colores de texto del layout (mismo acento en hex)
nl = 0
for root, _, fs in os.walk(LY):
    for fn in sorted(fs):
        p = os.path.join(root, fn)
        t = open(p, newline="", encoding="utf-8", errors="surrogateescape").read()
        n = t.lower().count("0x" + ORIGEN.lower())
        if not n:
            continue
        for viejo in ("0x" + ORIGEN.lower(), "0x" + ORIGEN.upper()):
            t = t.replace(viejo, "0x" + DESTINO.lower())
        open(p, "w", newline="", encoding="utf-8", errors="surrogateescape").write(t)
        nl += n
print(f"layout: {nl} colores de texto cambiados")
