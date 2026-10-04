#!/usr/bin/env python3
# Generates menu/gain_m.png in V3A style (blue #009FF6 badge + speaker + white letter) by cloning gain_h:
# erases ONLY the letter (keeps the round badge) and composites a NARROW/TALL "M" (compressed in width)
# the size of the H, centred in the same box as L/H -> aligned, with margin to the speaker and the badge edge.
import os
from PIL import Image, ImageDraw, ImageFont
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LG = os.path.join(WS, "theme/theme_port/litegui/theme1/menu")
im = Image.open(os.path.join(LG, "gain_h.png")).convert("RGBA")
W, H = im.size
px = im.load()
BLUE = (0, 159, 246, 255)
for x in range(29, W):           # erase only the letter (R>80), keep the badge
    for y in range(H):
        if px[x, y][0] > 80:
            px[x, y] = BLUE

FONT = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
TARGET_W, TARGET_H = 16, 22       # narrow (16) and slightly tall (22) = elongated; aligned with the H (16x21)
CX, CY = 37, 27                   # centre of the original H (x30..45, y17..37)

tmp = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
ImageDraw.Draw(tmp).text((40, 40), "M", font=ImageFont.truetype(FONT, 40), fill=(255, 255, 255, 255), anchor="mm")
m = tmp.crop(tmp.getbbox()).resize((TARGET_W, TARGET_H), Image.LANCZOS)   # compress width -> elongated
im.alpha_composite(m, (round(CX - TARGET_W / 2), round(CY - TARGET_H / 2)))
im.save(os.path.join(LG, "gain_m.png"))
print(f"gain_m: elongated M {TARGET_W}x{TARGET_H} at x[{round(CX-TARGET_W/2)}..{round(CX+TARGET_W/2)}] y[{round(CY-TARGET_H/2)}..{round(CY+TARGET_H/2)}]")
