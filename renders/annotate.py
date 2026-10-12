# Put the transparent Blender renders on the page colour; number the
# exploded view. Run after render.py:  python renders/annotate.py <repo root>
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
IMG = os.path.join(ROOT, "images"); BUILD = os.path.join(ROOT, "renders", "build")
BG = (245, 245, 247)

def flatten(src, dst):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, BG + (255,))
    Image.alpha_composite(bg, im).convert("RGB").save(dst, optimize=True)

for f in ["hero", "render_top", "render_rear", "cutaway"] + [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(IMG, "part_*.png"))]:
    p = os.path.join(IMG, f + ".png")
    if os.path.exists(p) and Image.open(p).mode == "RGBA":
        flatten(p, p)

raw = os.path.join(IMG, "exploded_raw.png")
if os.path.exists(raw):
    pts = {int(k): v for k, v in json.load(open(os.path.join(BUILD, "callouts.json"))).items()}
    flatten(raw, raw)
    base = Image.open(raw); TOP = 330
    im = Image.new("RGB", (base.width, base.height + TOP), BG); im.paste(base, (0, TOP))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("segoeui.ttf", 27); fn = ImageFont.truetype("segoeuib.ttf", 24)
    fs = ImageFont.truetype("segoeuib.ttf", 18); ft = ImageFont.truetype("segoeuib.ttf", 40)
    names = {1: "3 lit arcade buttons", 2: "Top shell (plate 1)", 3: "USB-A feedthrough (rear port)",
             4: "2.13\" e-paper + 2 clips (plate 1)", 5: "3\" trackball, turned 45°", 6: "Bottom plate (plate 2)",
             7: "LiPo 52x35x10 in its tray", 8: "Pico 2 W (upside down, pins up)", 9: "Charger + 5 V boost board",
             10: "Battery voltage sensor", 11: "MOSFET switch module", 12: "4 rubber feet + M3 screws"}
    for n, (x, y) in pts.items():
        y += TOP; r = 21
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 60, 40), outline="white", width=3)
        d.text((x, y), str(n), font=fn, fill="white", anchor="mm")
    d.text((60, 40), "GT Trackball - exploded view", font=ft, fill=(30, 30, 30))
    for i, n in enumerate(sorted(names)):
        cx, cy = (60, 110) if i < 6 else (720, 110); cy += (i % 6) * 36
        d.ellipse([cx, cy + 4, cx + 30, cy + 34], fill=(220, 60, 40))
        d.text((cx + 15, cy + 19), str(n), font=fs, fill="white", anchor="mm")
        d.text((cx + 42, cy + 2), names[n], font=f, fill=(40, 40, 40))
    im.save(os.path.join(IMG, "exploded.png"), optimize=True)
    os.remove(raw)
raw = os.path.join(IMG, "layout_raw.png")
if os.path.exists(raw):
    pts = {int(k): v for k, v in json.load(open(os.path.join(BUILD, "layout_callouts.json"))).items()}
    src = Image.open(raw).convert("RGBA")
    l, t, r, b = src.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()
    m = 60; l, t, r, b = max(l - m, 0), max(t - m, 0), min(r + m, src.width), min(b + m, src.height)
    bg = Image.new("RGBA", src.size, BG + (255,))
    base = Image.alpha_composite(bg, src).convert("RGB").crop((l, t, r, b))
    TOP, KEY = 110, 230
    im = Image.new("RGB", (base.width, base.height + TOP + KEY), BG); im.paste(base, (0, TOP))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("segoeui.ttf", 25); fn = ImageFont.truetype("segoeuib.ttf", 24)
    fs = ImageFont.truetype("segoeuib.ttf", 18); ft = ImageFont.truetype("segoeuib.ttf", 36)
    names = {3: "USB-A feedthrough (rear wall)", 5: "Trackball (hangs from the top deck)", 6: "Bottom plate",
             7: "LiPo in its tray", 8: "Pico 2 W, pins up", 9: "Charger + 5 V boost",
             10: "Voltage sensor", 11: "MOSFET module", 12: "M3 screw pillars (4)"}
    for n, (x, y) in pts.items():
        x -= l; y += TOP - t; rr = 21
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(220, 60, 40), outline="white", width=3)
        d.text((x, y), str(n), font=fn, fill="white", anchor="mm")
    d.text((40, 30), "Component layout - bottom half, top shell lifted off", font=ft, fill=(30, 30, 30))
    y0 = TOP + base.height + 20
    for i, n in enumerate(sorted(names)):
        cx, cy = 40 + (i // 5) * (im.width // 2), y0 + (i % 5) * 40
        d.ellipse([cx, cy + 4, cx + 30, cy + 34], fill=(220, 60, 40))
        d.text((cx + 15, cy + 19), str(n), font=fs, fill="white", anchor="mm")
        d.text((cx + 42, cy + 2), names[n], font=f, fill=(40, 40, 40))
    d.text((im.width - 40, y0 + 4 * 40 + 2), "numbers match the exploded view", font=f, fill=(120, 120, 120), anchor="ra")
    im.save(os.path.join(IMG, "layout_top.png"), optimize=True)
    os.remove(raw)
print("annotated")
