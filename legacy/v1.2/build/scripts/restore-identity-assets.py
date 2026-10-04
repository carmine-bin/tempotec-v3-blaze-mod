#!/usr/bin/env python3
# Devuelve al stock del Blaze los assets que llevan IDENTIDAD del equipo. El reskin los pisó con los del
# V3 Analog, que a su vez venían con la marca de HiBy:
#   - `certificate/certificate.png` del V3A dice "Model: HiBy R3II" (y en tinta oscura, ilegible sobre el
#     fondo negro del tema). El del stock dice "TempoTec V3" y ya viene en blanco.
#   - `about_dev/logo.png` del V3A es el logo de HiBy; el del stock es el de TempoTec.
#   - los `*_qrcode.png` son las cuentas oficiales de la marca.
# Regla: el look se porta, la identidad NO.
#
# Los íconos de plataforma (facebook/wechat/weibo) NO son identidad: se quedan los del V3A porque el layout
# V3A los ubica con sus medidas (54x54); los del stock son 63x63 y quedan chuecos/apretados contra el borde.
#
# Además recentra `about_dev_iv_icon`: el logo del stock es 44x37 y el del V3A 96x26, así que la x del
# layout V3A (112) lo dejaba corrido a la izquierda.
# Idempotente.
import json, os, shutil, filecmp

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STOCK_ROOTFS = os.environ.get("BLAZE_STOCK_ROOTFS")
DONOR_ROOTFS = os.environ.get("V3_ANALOG_ROOTFS")
if not STOCK_ROOTFS or not DONOR_ROOTFS:
    raise SystemExit("Set BLAZE_STOCK_ROOTFS and V3_ANALOG_ROOTFS to extracted firmware rootfs trees")
STOCK = os.path.join(STOCK_ROOTFS, "usr/resource/litegui/theme1")
V3A = os.path.join(DONOR_ROOTFS, "usr/resource/litegui/theme1")
STAGE = os.path.join(WS, "theme/theme_port/litegui/theme1")

IDENTIDAD = ["certificate/certificate.png", "about_dev/logo.png",
             "about_dev/facebook_qrcode.png", "about_dev/wechat_qrcode.png", "about_dev/weibo_qrcode.png"]
LOOK = ["about_dev/facebook.png", "about_dev/wechat.png", "about_dev/weibo.png",
        "about_dev/microblog.png", "about_dev/microblog_s.png",
        "about_dev/post_bar.png", "about_dev/post_bar_s.png"]

n = 0
for origen, lista, que in ((STOCK, IDENTIDAD, "stock"), (V3A, LOOK, "V3A")):
    for rel in lista:
        src, dst = os.path.join(origen, rel), os.path.join(STAGE, rel)
        if not os.path.isfile(src):
            continue
        if os.path.isfile(dst) and filecmp.cmp(src, dst, shallow=False):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  {rel} <- {que}")
        n += 1
print(f"identidad/look: {n} archivos ajustados")

# --- recentrar el logo del About (44x37 del stock en pantalla de 320)
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_about_dev.view")
t = open(f, newline="").read()
i = t.index('"name":"about_dev_iv_icon"')
fin = t.index("},", i)
bloque = t[i:fin]
x, y = 138, 67          # (320-44)/2 ; misma altura visual que el logo V3A (72 + (26-37)/2)
nuevo = bloque
for k, v in (("x", x), ("y", y)):
    viejo = f'"{k}":' + bloque.split(f'"{k}":')[1].split(",")[0]
    nuevo = nuevo.replace(viejo, f'"{k}":{v}')
if nuevo != bloque:
    t = t[:i] + nuevo + t[fin:]
    open(f, "w", newline="").write(t)
    json.loads(t)
    print(f"about_dev_iv_icon recentrado en ({x},{y})")
else:
    print("about_dev_iv_icon: ya estaba centrado")
