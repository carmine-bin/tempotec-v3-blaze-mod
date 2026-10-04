#!/usr/bin/env python3
# Estado final del pull-down. Uso:
#
#   restore-pulldown-controls.py --slider=vol      (default) un solo slider: VOLUMEN
#   restore-pulldown-controls.py --slider=brillo             un solo slider: BRILLO (experimento)
#
# Por qué UN solo slider: el binario acomoda los íconos del pull-down en grilla propia (ignora la y del
# .view) y con los toggles visibles la segunda fila cae ~y150-210. Probado en device 2026-08-07: un
# segundo slider ahí queda SOBREPUESTO a los íconos. La tarjeta da para un slider, el de abajo (y=225).
#
# BRILLO: FUNCIONA (device 2026-08-07) con `--slider=brillo`. La clave fue el NOMBRE del elemento, no la
# posición ni los assets (ver el bloque de nombres más abajo y PULLDOWN-BINARIO.md).
#
# Ícono del slider de volumen: menu\speaker.png es el asset del STOCK (20x20, tosco entre los V3A y se ve
# pixelado) -> touch_set\vol.png (V3A, 24x24, mismo tamaño que el ícono de brillo del V3A).
#
# Idempotente. Correr DESPUES de importar el layout donante + convert-brightness-to-volume + fix-pulldown-gain.
import json, os, sys

MODO = "vol"
for a in sys.argv[1:]:
    if a.startswith("--slider="):
        MODO = a.split("=", 1)[1]
assert MODO in ("vol", "brillo"), "usar --slider=vol | --slider=brillo"

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_pull_down_menu.view")
t = open(f, newline="").read()
eol = "\r\n" if "\r\n" in t else "\n"

def bloque(nombre_ini, texto):
    """devuelve (inicio, fin) del elemento cuyo "name" es nombre_ini, incluyendo la coma final"""
    i = texto.index(f'"name":"{nombre_ini}"')
    ini = texto.rindex('"', 0, texto.rindex(":{", 0, i))
    ini = texto.rindex("\n", 0, ini) + 1
    fin = texto.index("},", i) + 2
    fin = texto.index("\n", fin) + 1
    return ini, fin

def quitar(nombre):
    global t
    if f'"name":"{nombre}"' not in t:
        return False
    ini, fin = bloque(nombre, t)
    t = t[:ini] + t[fin:]
    return True

# --- 1. un solo slider, en la posición de abajo (y=222/225), con el par ícono+barra que corresponda
# OJO con los nombres (probado en device 2026-08-07, cada uno costó un ciclo reboot+apply):
#  - la barra de brillo SOLO funciona como "pull_down_menu_pb". Con "pull_down_menu_bklight_pb" el
#    elemento se dibuja y arrastra pero el binario nunca le instala el callback (el sysfs queda en 0).
#    Los dos nombres caen en el mismo handler, así que lo que corta está antes, adentro del binario.
#  - el ícono NO puede llamarse "pull_down_menu_iv_bklight": ese nombre está en la tabla de íconos que
#    maneja el binario (.data 0x92e880) y, sin su función activa, no lo dibuja. Con el nombre del V3A
#    ("..._bklight_icon"), que el binario no conoce, queda como imagen estática y se ve.
ICONO = {"vol": ("pull_down_menu_iv_vol", "touch_set\\\\vol.png"),
         "brillo": ("pull_down_menu_iv_bklight_icon", "menu\\\\blk.png")}[MODO]
BARRA = {"vol": "pull_down_menu_vol_pb", "brillo": "pull_down_menu_pb"}[MODO]
SOBRA_ICONO = {"vol": "pull_down_menu_iv_bklight_icon", "brillo": "pull_down_menu_iv_vol"}[MODO]
SOBRA_BARRA = {"vol": "pull_down_menu_pb", "brillo": "pull_down_menu_vol_pb"}[MODO]

nuevo = (
    '\t\t"imageview":{\n'
    f'\t\t\t"name":"{ICONO[0]}",\n'
    f'\t\t\t"img_path":"{ICONO[1]}",\n'
    '\t\t\t"x":24,\n'
    '\t\t\t"y":223,\n'
    '\t\t\t"color_mode":"color_565",\n'
    '\t\t\t"imageview":true\n'
    '\t\t},\n'
    '\t\t"progress_bar":{\n'
    f'\t\t\t"name":"{BARRA}",\n'
    '\t\t\t"img_path_0":"menu\\\\vol_bg.png",\n'
    '\t\t\t"img_path_1":"menu\\\\cursor.png",\n'
    '\t\t\t"img_focus_path_0":"menu\\\\vol_progress.png",\n'
    '\t\t\t"style":"horizon",\n'
    '\t\t\t"x":56,\n'
    '\t\t\t"y":225,\n'
    '\t\t\t"w":239,\n'
    '\t\t\t"h":20,\n'
    '\t\t\t"touch_x":30,\n'
    '\t\t\t"touch_y":210,\n'
    '\t\t\t"touch_w":290,\n'
    '\t\t\t"touch_h":50,\n'
    '\t\t\t"color_mode":"color_565",\n'
    '\t\t\t"progress_bar":true\n'
    '\t\t},\n'
).replace("\n", eol)

# se limpian TODOS los nombres que este script maneja (incluidos los que no funcionaron), para que
# re-correrlo o cambiar de modo no deje elementos huérfanos apilados en la misma posición
for nm in ("pull_down_menu_iv_vol", "pull_down_menu_vol_pb", "pull_down_menu_iv_bklight_icon",
           "pull_down_menu_iv_bklight", "pull_down_menu_pb", "pull_down_menu_bklight_pb"):
    quitar(nm)
i = t.index('\t\t"imageview":{')          # antes del primer imageview
t = t[:i] + nuevo + t[i:]
print(f"slider unico: {MODO} ({ICONO[0]} + {BARRA}) en y=220/225")
