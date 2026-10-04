#!/usr/bin/env python3
# Restores the Blaze stock assets that carry the device's IDENTITY. The reskin overwrote them with the
# V3 Analog ones, which in turn carried HiBy branding:
#   - the V3A `certificate/certificate.png` says "Model: HiBy R3II" (in dark ink, unreadable on the
#     theme's black background). The stock one says "TempoTec V3" and is already white.
#   - the V3A `about_dev/logo.png` is the HiBy logo; the stock one is TempoTec's.
#   - the `*_qrcode.png` files are the brand's official accounts.
# Rule: the look is ported, the identity is NOT.
#
# The platform icons (facebook/wechat/weibo) are NOT identity: the V3A ones stay because the V3A layout
# places them at their size (54x54); the stock ones are 63x63 and end up crooked/cramped against the edge.
#
# Also recentres `about_dev_iv_icon`: the stock logo is 44x37 and the V3A one 96x26, so the V3A layout's
# x (112) left it shifted to the left.
# Idempotent.
import json, os, shutil, filecmp

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STOCK_ROOTFS = os.environ.get("BLAZE_STOCK_ROOTFS")
DONOR_ROOTFS = os.environ.get("V3_ANALOG_ROOTFS")
if not STOCK_ROOTFS or not DONOR_ROOTFS:
    raise SystemExit("Set BLAZE_STOCK_ROOTFS and V3_ANALOG_ROOTFS to extracted firmware rootfs trees")
STOCK = os.path.join(STOCK_ROOTFS, "usr/resource/litegui/theme1")
V3A = os.path.join(DONOR_ROOTFS, "usr/resource/litegui/theme1")
STAGE = os.path.join(WS, "theme/theme_port/litegui/theme1")

IDENTITY = ["certificate/certificate.png", "about_dev/logo.png",
            "about_dev/facebook_qrcode.png", "about_dev/wechat_qrcode.png", "about_dev/weibo_qrcode.png"]
LOOK = ["about_dev/facebook.png", "about_dev/wechat.png", "about_dev/weibo.png",
        "about_dev/microblog.png", "about_dev/microblog_s.png",
        "about_dev/post_bar.png", "about_dev/post_bar_s.png"]

n = 0
for source, files, label in ((STOCK, IDENTITY, "stock"), (V3A, LOOK, "V3A")):
    for rel in files:
        src, dst = os.path.join(source, rel), os.path.join(STAGE, rel)
        if not os.path.isfile(src):
            continue
        if os.path.isfile(dst) and filecmp.cmp(src, dst, shallow=False):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  {rel} <- {label}")
        n += 1
print(f"identity/look: {n} files adjusted")

# --- recentre the About logo (stock 44x37 on a 320-pixel screen)
f = os.path.join(WS, "theme/theme_port/layout/theme1/hiby_about_dev.view")
t = open(f, newline="").read()
i = t.index('"name":"about_dev_iv_icon"')
end = t.index("},", i)
block = t[i:end]
x, y = 138, 67          # (320-44)/2 ; same visual height as the V3A logo (72 + (26-37)/2)
new = block
for k, v in (("x", x), ("y", y)):
    old = f'"{k}":' + block.split(f'"{k}":')[1].split(",")[0]
    new = new.replace(old, f'"{k}":{v}')
if new != block:
    t = t[:i] + new + t[end:]
    open(f, "w", newline="").write(t)
    json.loads(t)
    print(f"about_dev_iv_icon recentred at ({x},{y})")
else:
    print("about_dev_iv_icon: already centred")
