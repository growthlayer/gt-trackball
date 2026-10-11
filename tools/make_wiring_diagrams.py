# ============================================================
#  Pictorial wiring diagrams: every component drawn as it looks, wires
#  routed pin to pin. Writes images/wiring.svg (everything) and
#  images/wiring_1_power.svg ... wiring_4_display.svg (one step each,
#  the other wires faded).      python tools/make_wiring_diagrams.py
# ============================================================
import os
from xml.sax.saxutils import escape as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images")
W, H = 2400, 1860
TOP = 190                                   # room for the title and steps

C = dict(red="#d62828", blk="#222222", org="#f08c00", blu="#1c64d6", grn="#1f9d55", olv="#7a8b1e",
         pur="#8e44ad", brn="#9c5a1c", yel="#e9c400", usb="#7d7d85")

# ---------------- component drawings ----------------
pins = {}                                   # "comp.pin" -> (x, y, dx, dy)

def pin(name, x, y, d):
    pins[name] = (x, y) + {"L": (-1, 0), "R": (1, 0), "U": (0, -1), "D": (0, 1)}[d]

def rect(o, x, y, w, h, fill, stroke="#333", rx=8, sw=2):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def t(o, x, y, s, size=16, col="#222", anchor="middle", bold=False, mono=False):
    fam = "Consolas,monospace" if mono else "Segoe UI,Arial,sans-serif"
    o.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{col}" text-anchor="{anchor}"'
             f'{" font-weight=\"bold\"" if bold else ""}>{E(s)}</text>')

def pad(o, x, y, label, side, used=True, col="#c9a227"):
    o.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{col if used else "#ddd"}" stroke="#555" stroke-width="1.5"/>')
    if label:
        dx = -14 if side == "R" else 14
        t(o, x + dx, y + 5, label, 15, "#fff" if used else "#aaa", "end" if side == "R" else "start", True, True)

PICO_L = {1: "GP0", 2: "GP1", 3: "GND", 4: "GP2", 5: "GP3", 6: "GP4", 7: "GP5", 8: "GND", 9: "GP6", 10: "GP7",
          11: "GP8", 12: "GP9", 13: "GND", 14: "GP10", 15: "GP11", 16: "GP12", 17: "GP13", 18: "GND", 19: "GP14", 20: "GP15"}
PICO_R = {21: "GP16", 22: "GP17", 23: "GND", 24: "GP18", 25: "GP19", 26: "GP20", 27: "GP21", 28: "GND", 29: "GP22", 30: "RUN",
          31: "GP26", 32: "GP27", 33: "AGND", 34: "GP28", 35: "VREF", 36: "3V3", 37: "3V3_EN", 38: "GND", 39: "VSYS", 40: "VBUS"}
USED = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 23, 28, 29, 31, 33, 36, 38, 39, 40}

def pico(o):
    x0, x1, y0, pitch = 1000, 1340, 290, 46
    rect(o, x0, y0 - 20, x1 - x0, 20 * pitch + 30, "#1f7a3a", "#0f4f24", 14, 3)
    rect(o, 1140, y0 - 44, 60, 34, "#b8b8bd", "#666", 4)                           # micro-USB jack
    pin("pico.usb", 1170, y0 - 44, "U")
    t(o, 1170, y0 + 330, "Raspberry Pi", 22, "#e8f5e9", bold=True)
    t(o, 1170, y0 + 358, "Pico 2 W", 30, "#ffffff", bold=True)
    t(o, 1170, y0 + 392, "labels as printed", 13, "#cfe8d4")
    t(o, 1170, y0 + 409, "on the pin side", 13, "#cfe8d4")
    t(o, 1170, y0 + 426, "(mounted pins up)", 13, "#cfe8d4")
    rect(o, 1135, y0 + 470, 70, 70, "#2b2b2b", "#111", 4)
    t(o, 1170, y0 + 510, "RP2350", 13, "#bbb", bold=True)
    for n in range(1, 41):
        if n <= 20:
            y = y0 + 20 + (n - 1) * pitch; x = x0 + 14; side = "L"; lab = PICO_L[n]
        else:
            y = y0 + 20 + (40 - n) * pitch; x = x1 - 14; side = "R"; lab = PICO_R[n]
        used = n in USED
        pad(o, x, y, lab, "L" if side == "L" else "R", used, "#e0b43a")
        t(o, x - 26 if side == "L" else x + 26, y + 5, str(n), 14, "#555" if used else "#bbb",
          "end" if side == "L" else "start", False, True)
        pin(f"pico.{n}", x - 8 if side == "L" else x + 8, y, side)

def trackball(o):
    x, y = 90, 330
    rect(o, x, y, 520, 400, "#2a2a2e", "#111", 20, 3)
    o.append(f'<circle cx="{x + 230}" cy="{y + 200}" r="135" fill="#151515"/>')
    o.append(f'<circle cx="{x + 230}" cy="{y + 200}" r="120" fill="#eceaf2" stroke="#bbb" stroke-width="2"/>')
    o.append(f'<circle cx="{x + 195}" cy="{y + 160}" r="30" fill="#ffffff" opacity="0.7"/>')
    t(o, x + 230, y + 375, '3" trackball (seen from below)', 18, "#ddd", bold=True)
    # J1 on its own PS/2 board
    rect(o, x + 400, y + 20, 110, 330, "#1f7a3a", "#0f4f24", 6)
    t(o, x + 455, y + 45, "J1", 18, "#fff", bold=True)
    rect(o, x + 470, y + 60, 34, 7 * 38 + 6, "#f2f2f2", "#999", 4)
    for i, lab in enumerate(["+5V", "DATA", "CLOCK", "GND", "M", "R", "L"]):
        py = y + 80 + i * 38
        used = lab in ("+5V", "DATA", "CLOCK", "GND")
        o.append(f'<rect x="{x + 480}" y="{py - 7}" width="14" height="14" fill="{"#c9a227" if used else "#ccc"}"/>')
        t(o, x + 462, py + 5, lab, 15, "#fff" if used else "#9bb", "end", True, True)
        pin(f"tb.{lab}", x + 504, py, "R")
    # ball light lead
    rect(o, x + 60, y + 410, 120, 36, "#f2f2f2", "#999", 4)
    t(o, x + 120, y + 434, "ball light", 14, "#333", bold=True)
    pin("tb.RGB+", x + 180, y + 420, "R"); pin("tb.RGB-", x + 180, y + 438, "R")
    t(o, x + 190, y + 418, "yellow +", 12, "#666", "start"); t(o, x + 190, y + 446, "black −", 12, "#666", "start")

def buttons(o):
    x0, y0 = 90, 820
    t(o, x0, y0 - 20, "3 lit buttons — 3-pin XH plug: latch toward you, wires down, pins 1-2-3 left to right",
      15, "#444", "start")
    for i, name in enumerate(["LEFT", "RIGHT", "MENU"]):
        y = y0 + i * 118
        o.append(f'<circle cx="{x0 + 55}" cy="{y + 45}" r="44" fill="#e9e9ee" stroke="#aaa" stroke-width="3"/>')
        o.append(f'<circle cx="{x0 + 55}" cy="{y + 45}" r="30" fill="#ffffff" stroke="#ccc" stroke-width="2"/>')
        t(o, x0 + 55, y + 51, name, 15, "#333", bold=True)
        rect(o, x0 + 330, y + 10, 70, 74, "#f4f4f4", "#888", 6)
        o.append(f'<rect x="{x0 + 345}" y="{y + 4}" width="40" height="8" fill="#bbb"/>')   # latch
        for k, lab in enumerate(["1 LED−", "2 switch", "3 LED+/com"]):
            py = y + 24 + k * 22
            o.append(f'<rect x="{x0 + 392}" y="{py - 6}" width="12" height="12" fill="#c9a227"/>')
            t(o, x0 + 322, py + 5, lab, 13, "#444", "end")
            pin(f"btn{i}.{k + 1}", x0 + 404, py, "R")
        o.append(f'<path d="M{x0 + 99} {y + 45} C {x0 + 200} {y + 125}, {x0 + 365} {y + 125}, {x0 + 365} {y + 84}" '
                 f'stroke="#555" stroke-width="5" fill="none"/>')

def epaper(o):
    x, y = 90, 1260
    rect(o, x, y, 520, 290, "#151515", "#000", 10, 3)
    rect(o, x + 30, y + 30, 380, 200, "#d8d6cf", "#999", 4)
    t(o, x + 220, y + 120, "GT Trackball", 22, "#222", bold=True, mono=True)
    t(o, x + 220, y + 160, "2.13\" e-Paper HAT V4", 16, "#555")
    t(o, x + 220, y + 270, "Waveshare 2.13\" e-Paper HAT V4 — 8-pin JST lead", 15, "#ccc")
    rect(o, x + 440, y + 20, 64, 8 * 30 + 12, "#f2f2f2", "#999", 4)
    for i, lab in enumerate(["VCC", "GND", "DIN", "CLK", "CS", "DC", "RST", "BUSY"]):
        py = y + 40 + i * 30
        o.append(f'<rect x="{x + 490}" y="{py - 6}" width="12" height="12" fill="#c9a227"/>')
        t(o, x + 482, py + 5, lab, 14, "#333", "end", True, True)
        pin(f"ep.{lab}", x + 504, py, "R")

def usb_port(o):
    x, y = 300, 70
    rect(o, x, y, 230, 150, "#2a2a2e", "#111", 12, 3)
    rect(o, x + 70, y + 50, 90, 40, "#c8c8cc", "#666", 3)
    o.append(f'<rect x="{x + 80}" y="{y + 60}" width="70" height="12" fill="#222"/>')
    t(o, x + 115, y + 125, "USB-A feedthrough (rear port)", 15, "#ddd", bold=True)
    t(o, x + 115, y - 12, "to the PC: USB-A to USB-A cable", 14, "#666")
    pin("usb.in", x + 230, y + 70, "R")

def charger(o):
    x, y = 1640, 340
    rect(o, x, y, 400, 300, "#1b1b1d", "#000", 10, 3)
    rect(o, x - 20, y + 110, 70, 80, "#c8c8cc", "#666", 6)
    t(o, x + 15, y + 210, "USB-C", 13, "#ccc", bold=True)
    pin("chg.usbc", x - 20, y + 150, "L")
    rect(o, x + 150, y + 70, 90, 90, "#333", "#555", 10); t(o, x + 195, y + 122, "100", 20, "#999", bold=True)
    o.append(f'<rect x="{x + 270}" y="{y + 80}" width="40" height="40" fill="#2a63c8"/>')
    t(o, x + 290, y + 140, "trimpot", 12, "#9ab", bold=True)
    t(o, x + 200, y + 40, "Charger + 5 V boost", 20, "#fff", bold=True)
    t(o, x + 200, y + 200, "set OUT to 5.00 V first", 15, "#ff8a80", bold=True)
    for lab, px in (("B−", 90), ("B+", 170)):
        o.append(f'<rect x="{x + px - 16}" y="{y + 262}" width="32" height="32" fill="#c9a227"/>')
        t(o, x + px, y + 252, lab, 16, "#fff", bold=True, mono=True)
        pin("chg." + lab, x + px, y + 300, "D")
    for lab, py in (("VO+", 120), ("VO−", 200)):
        o.append(f'<rect x="{x + 372}" y="{py + y - 16}" width="28" height="32" fill="#c9a227"/>')
        t(o, x + 362, y + py + 6, lab, 16, "#fff", "end", True, True)
        pin("chg." + lab, x + 400, y + py, "R")

def lever(o):
    x, y = 2160, 250
    rect(o, x, y, 120, 150, "#f3f3f3", "#888", 8)
    for k in range(3):
        o.append(f'<rect x="{x + 6}" y="{y + 18 + k * 44}" width="40" height="26" rx="4" fill="#f08c00"/>')
        pin(f"lev.{k}", x, y + 31 + k * 44, "L")
    t(o, x + 85, y + 80, "lever", 14, "#555", bold=True); t(o, x + 85, y + 98, "connector", 14, "#555", bold=True)
    t(o, x + 60, y + 175, "+5 V split", 14, "#d62828", bold=True)

def mosfet(o):
    x, y = 1500, 40
    rect(o, x, y, 420, 230, "#1d4fa8", "#0c2f6f", 10, 3)
    t(o, x + 210, y + 40, "MOSFET module (XY-MOS)", 20, "#fff", bold=True)
    t(o, x + 210, y + 66, "switches the trackball off in sleep", 14, "#cdd9f5")
    for lab, py in (("OUT+", 120), ("OUT−", 180)):
        rect(o, x - 6, y + py - 24, 70, 48, "#2a63c8", "#0c2f6f", 6)
        t(o, x + 80, y + py + 6, lab, 16, "#fff", "start", True, True)
        pin("fet." + lab, x - 6, y + py, "L")
    for lab, px in (("VIN+", 300), ("VIN−", 370)):
        rect(o, x + px - 28, y + 170, 56, 66, "#2a63c8", "#0c2f6f", 6)
        t(o, x + px, y + 160, lab, 15, "#fff", bold=True, mono=True)
        pin("fet." + lab, x + px, y + 236, "D")
    for lab, px in (("TRIG", 140), ("GND", 200)):
        o.append(f'<rect x="{x + px - 7}" y="{y + 216}" width="14" height="14" fill="#c9a227"/>')
        t(o, x + px, y + 206, lab, 14, "#fff", "middle", True, True)
        pin("fet." + lab, x + px, y + 230, "D")

def sensor(o):
    x, y = 1640, 1250
    rect(o, x, y, 330, 230, "#b3261e", "#6d120c", 10, 3)
    t(o, x + 120, y + 150, "Voltage", 20, "#fff", bold=True); t(o, x + 120, y + 176, "sensor ÷5", 20, "#fff", bold=True)
    for lab, px, used in (("VCC", 210, True), ("GND", 280, False)):
        rect(o, x + px - 28, y - 10, 56, 60, "#1f9d55" if used else "#7cbf98", "#0c5a2e", 6)
        t(o, x + px, y + 76, lab, 15, "#fff" if used else "#f4c7c3", bold=True, mono=True)
        pin("sen." + lab, x + px, y - 10, "U")
    t(o, x + 280, y + 96, "leave empty", 13, "#ffd6d3")
    for lab, py, used in (("S", 130, True), ("+", 165, False), ("−", 200, True)):
        o.append(f'<rect x="{x - 2}" y="{y + py - 7}" width="14" height="14" fill="{"#c9a227" if used else "#ccc"}"/>')
        t(o, x + 22, y + py + 5, lab, 16, "#fff" if used else "#f4c7c3", "start", True, True)
        pin("sen." + lab, x - 2, y + py, "L")

def battery(o):
    x, y = 1930, 860
    rect(o, x, y, 400, 260, "#c9ccd1", "#888", 18, 3)
    rect(o, x, y, 50, 260, "#e8a020", "#a86a00", 10)
    t(o, x + 235, y + 120, "LiPo 3.7 V", 26, "#333", bold=True)
    t(o, x + 235, y + 152, "52 × 35 × 10 mm", 16, "#555")
    pin("bat.+", x + 15, y + 80, "L"); pin("bat.-", x + 15, y + 150, "L")
    t(o, x + 60, y + 86, "red +", 13, "#a00", "start"); t(o, x + 60, y + 156, "black −", 13, "#333", "start")

def pigtail(o):
    x, y = 1490, 490
    rect(o, x, y - 22, 80, 44, "#3a3a3a", "#111", 8)
    t(o, x + 40, y - 32, "USB-C pigtail", 13, "#555", bold=True)
    pin("pig.in", x, y, "L"); pin("pig.out", x + 80, y, "R")

# ---------------- wires ----------------
WIRES = [  # (from, to, colour, group, label at the Pico end)
    ("usb.in", "pico.usb", "usb", "power", "micro-USB cable"),
    ("pico.40", "pig.in", "red", "power", "VBUS"),
    ("pig.out", "chg.usbc", "red", "power", ""),
    ("pico.23", "pig.in", "blk", "power", "GND"),
    ("chg.B+", "bat.+", "red", "power", ""),
    ("chg.B−", "bat.-", "blk", "power", ""),
    ("chg.VO+", "lev.0", "red", "power", ""),
    ("lev.1", "pico.39", "red", "power", "VSYS"),
    ("lev.2", "fet.VIN+", "red", "power", ""),
    ("chg.VO−", "pico.38", "blk", "power", "GND"),
    ("fet.VIN−", "pico.3", "blk", "power", "GND"),
    ("chg.B+", "sen.VCC", "red", "power", ""),
    ("sen.S", "pico.31", "brn", "power", "GP26"),
    ("sen.−", "pico.33", "blk", "power", "AGND"),
    ("fet.TRIG", "pico.29", "brn", "trackball", "GP22"),
    ("fet.GND", "pico.28", "blk", "trackball", "GND"),
    ("fet.OUT+", "tb.+5V", "red", "trackball", ""),
    ("fet.OUT−", "tb.GND", "blk", "trackball", ""),
    ("fet.OUT+", "tb.RGB+", "yel", "trackball", ""),
    ("fet.OUT−", "tb.RGB-", "blk", "trackball", ""),
    ("tb.DATA", "pico.4", "blu", "trackball", "GP2"),
    ("tb.CLOCK", "pico.5", "blu", "trackball", "GP3"),
    ("btn0.2", "pico.6", "grn", "buttons", "GP4"),
    ("btn1.2", "pico.7", "grn", "buttons", "GP5"),
    ("btn2.2", "pico.9", "grn", "buttons", "GP6"),
    ("btn0.3", "pico.10", "olv", "buttons", "GP7"),
    ("btn1.3", "pico.10", "olv", "buttons", ""),
    ("btn2.3", "pico.10", "olv", "buttons", ""),
    ("btn0.1", "pico.8", "blk", "buttons", "GND"),
    ("btn1.1", "pico.8", "blk", "buttons", ""),
    ("btn2.1", "pico.8", "blk", "buttons", ""),
    ("ep.VCC", "pico.36", "org", "display", "3V3"),
    ("ep.GND", "pico.18", "blk", "display", "GND"),
    ("ep.DIN", "pico.15", "pur", "display", "GP11"),
    ("ep.CLK", "pico.14", "pur", "display", "GP10"),
    ("ep.CS", "pico.12", "pur", "display", "GP9"),
    ("ep.DC", "pico.11", "pur", "display", "GP8"),
    ("ep.RST", "pico.16", "pur", "display", "GP12"),
    ("ep.BUSY", "pico.17", "pur", "display", "GP13"),
]
ROUTE = {   # waypoints that keep wires off the boards
    ("ep.VCC", "pico.36"): [(650, 1250), (1430, 1250), (1430, 520)],
    ("fet.VIN−", "pico.3"): [(1870, 345), (1430, 345), (1430, 228), (960, 228), (960, 402)],
    ("lev.2", "fet.VIN+"): [(2110, 369), (2110, 318), (1800, 318)],
    ("pico.23", "pig.in"): [(1450, 1112), (1450, 490)],
    ("chg.B+", "sen.VCC"): [(1810, 760), (1850, 1180)],
    ("fet.OUT+", "tb.+5V"): [(760, 160), (680, 410)],
    ("fet.OUT−", "tb.GND"): [(800, 200), (700, 524)],
    ("fet.OUT+", "tb.RGB+"): [(740, 160), (720, 750)],
    ("fet.OUT−", "tb.RGB-"): [(780, 200), (740, 768)],
    ("usb.in", "pico.usb"): [(1170, 145)],
    ("lev.1", "pico.39"): [(2135, 325), (2135, 296), (1600, 296), (1600, 330), (1400, 376)],
    ("chg.VO−", "pico.38"): [(2090, 540), (2090, 680), (1480, 680), (1480, 430), (1380, 422)],
    ("fet.TRIG", "pico.29"): [(1640, 330), (1520, 330), (1520, 836)],
    ("fet.GND", "pico.28"): [(1700, 340), (1540, 340), (1540, 882)],
    ("sen.S", "pico.31"): [(1560, 1380), (1560, 744)],
    ("sen.−", "pico.33"): [(1580, 1450), (1580, 652)],
}

def path_d(a, b, via):
    (x1, y1, dx1, dy1), (x2, y2, dx2, dy2) = pins[a], pins[b]
    pts = [(x1, y1)] + via + [(x2, y2)]
    if not via:
        k = max(60, min(260, (abs(x2 - x1) + abs(y2 - y1)) * 0.35))
        return f"M{x1} {y1} C {x1 + dx1 * k} {y1 + dy1 * k}, {x2 + dx2 * k} {y2 + dy2 * k}, {x2} {y2}"
    # smooth path through waypoints: leave/arrive along the pin direction
    d = f"M{x1} {y1} L {x1 + dx1 * 30} {y1 + dy1 * 30}"
    prev = (x1 + dx1 * 30, y1 + dy1 * 30)
    for p in via:
        d += f" L {p[0]} {p[1]}"
        prev = p
    d += f" L {x2 + dx2 * 30} {y2 + dy2 * 30} L {x2} {y2}"
    return d

def build(focus=None, title="", subtitle="", steps=None):
    o = []
    comps = [usb_port, pico, trackball, buttons, epaper, charger, lever, mosfet, sensor, battery, pigtail]
    for f in comps:
        f(o)
    involved = set()
    for a, b, col, grp, lab in WIRES:
        on = focus is None or grp == focus
        if on:
            involved.add(a.split(".")[0]); involved.add(b.split(".")[0])
    # wires, dimmed ones first
    order = sorted(WIRES, key=lambda w: focus is not None and w[3] == focus)
    for a, b, col, grp, lab in order:
        on = focus is None or grp == focus
        via = ROUTE.get((a, b), [])
        d = path_d(a, b, via)
        w = 9 if col == "usb" else 6
        op = 1.0 if on else 0.10
        o.append(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="{0.35 * op}" stroke-width="{w + 3}" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<path d="{d}" fill="none" stroke="{C[col]}" stroke-opacity="{op}" stroke-width="{w}" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
        if on:
            for p in (a, b):
                x, y, _, _ = pins[p]
                o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{C[col]}" stroke-width="3"/>')
    # splice dots where several button wires meet one pin
    head = [f'<rect width="{W}" height="{H}" fill="#fbfbfc"/>']
    t(head, 40, 50, title, 34, "#111", "start", True)
    t(head, 40, 84, subtitle, 18, "#555", "start")
    if steps:
        for i, s in enumerate(steps):
            t(head, 40, 118 + i * 24, s, 16, "#333", "start")
    leg = [("red", "+5 V / VBUS / B+"), ("blk", "GND"), ("org", "3.3 V"), ("blu", "PS/2 data"), ("grn", "button switch"),
           ("olv", "button common"), ("pur", "display SPI"), ("brn", "control / sense"), ("yel", "ball light +"),
           ("usb", "USB cable")]
    for i, (c, s) in enumerate(leg):
        x = 40 + (i % 5) * 230; y = H - 60 + (i // 5) * 30
        head.append(f'<line x1="{x}" y1="{y}" x2="{x + 40}" y2="{y}" stroke="{C[c]}" stroke-width="7" stroke-linecap="round"/>')
        t(head, x + 52, y + 6, s, 16, "#333", "start")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           + "".join(head) + f'<g transform="translate(0,{TOP})">' + "".join(o) + "</g></svg>")
    return svg

pages = [
    ("wiring.svg", None, "GT Trackball — complete wiring",
     "Every connection. Colours are a suggestion; what matters is which pin goes where. Pin numbers = Pico physical pins.", None),
    ("wiring_1_power.svg", "power", "Step 3.1 — Power and charging",
     "Battery → charger/boost → 5 V to the Pico and the MOSFET module; USB charges through the pigtail.",
     ["1. Set the charger's output to 5.00 V with nothing connected.",
      "2. Battery red → B+, black → B−.   3. VO+ → lever connector → Pico VSYS and MOSFET VIN+.   4. VO− → Pico GND (38).",
      "5. Pico VBUS (40) / GND (23) → USB-C pigtail → charger USB-C.   6. Sensor VCC screw → B+, S → GP26, − → AGND. Sensor GND screw stays empty."]),
    ("wiring_2_trackball.svg", "trackball", "Step 3.2 — Trackball",
     "The trackball's own board talks PS/2 to the Pico; the MOSFET module switches its power off in sleep.",
     ["1. Unplug the trackball's USB cable from J1.   2. J1 DATA → GP2, CLOCK → GP3.",
      "3. MOSFET OUT+ → J1 +5V and the ball light's yellow wire; OUT− → J1 GND and the black wire.",
      "4. MOSFET TRIG → GP22, its GND → Pico GND (28).   J1 M / R / L stay unconnected."]),
    ("wiring_3_buttons.svg", "buttons", "Step 3.3 — Buttons",
     "Each button's 3-pin plug: pin 1 = LED −, pin 2 = switch, pin 3 = LED + and the switch's other side.",
     ["1. Check each harness first: 5 V on pin 3 and GND on pin 1 lights the button (wire markings vary — go by position).",
      "2. Pin 2: LEFT → GP4, RIGHT → GP5, MENU → GP6.   3. All three pin 3s → GP7.   4. All three pin 1s → GND (8)."]),
    ("wiring_4_display.svg", "display", "Step 3.4 — E-paper display",
     "Waveshare 2.13\" e-Paper HAT V4 on its 8-pin JST lead. 3.3 V only — never 5 V.",
     ["VCC → 3V3 (36), GND → GND (18), DIN → GP11, CLK → GP10, CS → GP9, DC → GP8, RST → GP12, BUSY → GP13."]),
]
for fname, focus, title, sub, steps in pages:
    pins.clear()
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(build(focus, title, sub, steps))
    print("wrote images/" + fname)
