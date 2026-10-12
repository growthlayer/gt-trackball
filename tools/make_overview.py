# ============================================================
#  "How it all connects" overview: one card per part (with its
#  Blender thumbnail from images/part_*.png), wires that never cross,
#  labels beside the wires, arrows for power flow.
#      python tools/make_overview.py
#  Writes images/overview.svg and images/overview.png (PNG needs
#  Chrome or Edge).
# ============================================================
import base64, io, os, shutil, subprocess, tempfile
from xml.sax.saxutils import escape as E
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
W, H = 1800, 1180
TOP = 96                                # room for the title

COL = {"power": "#d62828", "data": "#1c64d6", "ctrl": "#b5651d", "usb": "#7b3fbf", "button": "#1f9d55"}

def thumb(name, size=170):
    im = Image.open(os.path.join(IMG, f"part_{name}.png")).convert("RGB")
    # trim the page-coloured margin, then fit into a square
    bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
    from PIL import ImageChops
    bbox = ImageChops.difference(im, bg).point(lambda v: 255 if v > 12 else 0).getbbox() or (0, 0) + im.size
    im = im.crop(bbox)
    im.thumbnail((size * 2, size * 2))
    sq = Image.new("RGB", (max(im.size),) * 2, im.getpixel((1, 1)))
    sq.paste(im, ((sq.width - im.width) // 2, (sq.height - im.height) // 2))
    buf = io.BytesIO(); sq.resize((size * 2, size * 2)).save(buf, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

o = []
def t(x, y, s, size=18, col="#222", anchor="start", bold=False, mono=False):
    fam = "Consolas,monospace" if mono else "Segoe UI,Arial,sans-serif"
    o.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{col}" text-anchor="{anchor}"'
             f'{" font-weight=\"bold\"" if bold else ""}>{E(s)}</text>')

def card(x0, y0, x1, y1, title, sub, img=None, tint="#ffffff"):
    o.append(f'<rect x="{x0 + 4}" y="{y0 + 6}" width="{x1 - x0}" height="{y1 - y0}" rx="16" fill="#000" opacity="0.06"/>')
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="16" fill="{tint}" stroke="#c9ccd6" stroke-width="2"/>')
    tx = x0 + 24
    if img:
        s = y1 - y0 - 24
        o.append(f'<clipPath id="c{x0}{y0}"><rect x="{x0 + 12}" y="{y0 + 12}" width="{s}" height="{s}" rx="10"/></clipPath>')
        o.append(f'<image href="{img}" x="{x0 + 12}" y="{y0 + 12}" width="{s}" height="{s}" clip-path="url(#c{x0}{y0})" preserveAspectRatio="xMidYMid slice"/>')
        tx = x0 + 12 + s + 18
    my = (y0 + y1) / 2
    t(tx, my - 4, title, 22, "#111", bold=True)
    for k, line in enumerate(sub.split("\n")):
        t(tx, my + 24 + k * 22, line, 16, "#555")

def wire(pts, kind, dashed=False, arrow=False, w=5):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    extra = ' stroke-dasharray="14 10"' if dashed else ""
    mk = ' marker-end="url(#arr_%s)"' % kind if arrow else ""
    o.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w + 6}" stroke-linejoin="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="{COL[kind]}" stroke-width="{w}" stroke-linejoin="round"{extra}{mk}/>')

def tag(x, y, s, kind, anchor="middle"):
    wpx = len(s) * 8.6 + 18
    x0 = x - wpx / 2 if anchor == "middle" else (x if anchor == "start" else x - wpx)
    o.append(f'<rect x="{x0}" y="{y - 17}" width="{wpx}" height="26" rx="13" fill="#fff" stroke="{COL[kind]}" stroke-width="1.5"/>')
    t(x0 + wpx / 2, y + 2, s, 15, COL[kind], "middle", True)

def port(x, y, s, anchor):
    t(x, y + 5, s, 15, "#1d5e33", anchor, True, True)

# ---------- wires first (cards drawn over their ends) ----------
# PC <-> USB port, USB port -> Pico, PC ... Pico (Bluetooth)
wire([(230, 180), (230, 262)], "usb"); tag(230, 225, "USB-A to USB-A cable", "usb", "start") if False else tag(330, 225, "USB-A to USB-A cable", "usb")
wire([(400, 322), (642, 322)], "usb"); tag(521, 304, "micro-USB cable", "usb")
wire([(400, 112), (870, 112), (870, 262)], "usb", dashed=True); tag(635, 94, "Bluetooth LE (wireless)", "usb")
# power
wire([(642, 420), (330, 420), (330, 466)], "power", arrow=True); tag(500, 402, "USB 5 V → charge input", "power")
wire([(400, 545), (636, 545)], "power", arrow=True); tag(520, 527, "5 V → VSYS", "power")
wire([(330, 612), (330, 756)], "power"); tag(330, 690, "B+ / B−", "power")
wire([(60, 585), (30, 585), (30, 1010), (1270, 1010), (1270, 906)], "power", arrow=True)
tag(650, 1010, "5 V (via the lever connector) → MOSFET in", "power")
wire([(1440, 830), (1545, 830), (1545, 646)], "power", arrow=True); tag(1545, 720, "switched 5 V", "power")
# battery sense + control
wire([(560, 830), (636, 830)], "power", arrow=True)
wire([(810, 756), (810, 646)], "ctrl", arrow=True); tag(810, 700, "battery level", "ctrl")
wire([(1050, 640), (1050, 700), (1200, 700), (1200, 754)], "ctrl", arrow=True); tag(1125, 682, "sleep on / off", "ctrl")
# data
wire([(1100, 300), (1220, 300), (1220, 130), (1336, 130)], "data", arrow=True); tag(1220, 215, "SPI + 3.3 V", "data")
wire([(1100, 340), (1336, 340)], "button"); tag(1218, 322, "switches + LEDs", "button")
wire([(1100, 560), (1336, 560)], "data"); tag(1218, 542, "PS/2 data + clock", "data")

# ---------- cards ----------
pc_icon = ("data:image/svg+xml;base64," + base64.b64encode(
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#eef1fb"/>'
    b'<rect x="14" y="18" width="72" height="48" rx="4" fill="#2b2f3a"/><rect x="19" y="23" width="62" height="38" fill="#7aa0e8"/>'
    b'<rect x="44" y="66" width="12" height="10" fill="#2b2f3a"/><rect x="30" y="76" width="40" height="5" rx="2" fill="#2b2f3a"/></svg>').decode())
card(60, 50, 400, 180, "PC / Mac", "plays the game", pc_icon, "#f4f6fd")
card(60, 262, 400, 382, "USB-A port", "rear wall feedthrough", thumb("usb"))
card(60, 466, 400, 612, "Charger + 5 V boost", "charges the LiPo,\nmakes the 5 V rail", thumb("charger"))
card(220, 756, 560, 906, "LiPo 3.7 V", "103450 pouch cell", thumb("battery"))
card(640, 756, 980, 906, "Voltage sensor", "battery level (÷5)", thumb("sensor"))
card(1100, 756, 1440, 906, "MOSFET module", "cuts trackball power\nin sleep", thumb("mosfet"))
card(1340, 60, 1740, 200, '2.13" e-paper', "status + swing meter", thumb("epaper"))
card(1340, 270, 1740, 410, "3 lit buttons", "LEFT / MENU / RIGHT", thumb("buttons"))
card(1340, 480, 1740, 646, '3" trackball', "its own PS/2 board (J1)\n+ ball light", thumb("trackball"))

# the Pico, larger, with its pin groups on the edges
x0, y0, x1, y1 = 640, 262, 1100, 642
o.append(f'<rect x="{x0 + 4}" y="{y0 + 6}" width="{x1 - x0}" height="{y1 - y0}" rx="18" fill="#000" opacity="0.06"/>')
o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="18" fill="#eef7f0" stroke="#3c8a55" stroke-width="2.5"/>')
o.append(f'<image href="{thumb("pico", 200)}" x="{(x0 + x1) / 2 - 95}" y="{y0 + 70}" width="190" height="190"/>')
t((x0 + x1) / 2, y0 + 296, "Raspberry Pi Pico 2 W", 24, "#111", "middle", True)
t((x0 + x1) / 2, y0 + 322, "runs the firmware", 16, "#555", "middle")
port(x0 + 14, 322, "USB", "start"); port(x0 + 14, 420, "VBUS", "start"); port(x0 + 14, 545, "VSYS", "start")
port(x1 - 14, 300, "GP8–13", "end"); port(x1 - 14, 340, "GP4–7", "end"); port(x1 - 14, 560, "GP2 / GP3", "end")
t(810, y1 - 14, "GP26", 15, "#1d5e33", "middle", True, True); t(1050, y1 - 14, "GP22", 15, "#1d5e33", "middle", True, True)
t(870, y0 + 26, "Bluetooth", 15, "#1d5e33", "middle", True, True)

# ---------- title, legend ----------
head = [f'<rect width="{W}" height="{H}" fill="#fafbfc"/>']
for k, c in COL.items():
    head.append(f'<marker id="arr_{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
                f'<path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>')
o2 = o; o = head
t(40, 48, "GT Trackball — how it all connects", 30, "#111", bold=True)
t(40, 78, "Overview only — exact pins and wire colours are in the Step 3 wiring pictures.", 17, "#666")
leg = [("power", "power (arrow = direction)"), ("data", "data"), ("button", "buttons"), ("ctrl", "control / sensing"), ("usb", "USB / Bluetooth")]
for i, (k, s) in enumerate(leg):
    x = 40 + i * 330; y = H - 32
    o.append(f'<line x1="{x}" y1="{y}" x2="{x + 36}" y2="{y}" stroke="{COL[k]}" stroke-width="6" stroke-linecap="round"/>')
    t(x + 46, y + 6, s, 16, "#333")
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>'
       + "".join(x for x in o if x.startswith("<marker")) + "</defs>"
       + "".join(x for x in o if not x.startswith("<marker"))
       + f'<g transform="translate(0,{TOP})">' + "".join(o2) + "</g></svg>")
out = os.path.join(IMG, "overview.svg")
open(out, "w", encoding="utf-8").write(svg)
print("wrote images/overview.svg")

exe = next((p for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome") if os.path.exists(p)),
           shutil.which("chromium") or shutil.which("google-chrome"))
if exe:
    tmp = tempfile.mkdtemp()
    html = os.path.join(tmp, "o.html")
    open(html, "w", encoding="utf-8").write(
        f'<html><body style="margin:0"><img src="file:///{out.replace(os.sep, "/")}" width="{W}"></body></html>')
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                    f"--screenshot={os.path.join(IMG, 'overview.png')}", "file:///" + html.replace(os.sep, "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote images/overview.png")
