# ============================================================
#  Pictorial wiring diagrams: every component drawn as it looks,
#  wires routed on a grid - straight runs, square corners, a bridge
#  where two wires cross, a dot where wires join.
#  Writes images/wiring.svg (everything) and wiring_1_power.svg ...
#  wiring_4_display.svg (one step each, the other wires faded), plus
#  PNGs if Chrome or Edge is installed.
#      python tools/make_wiring_diagrams.py
# ============================================================
import heapq, os, shutil, subprocess, tempfile
from xml.sax.saxutils import escape as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images")
G = 23                                      # routing grid pitch (px) = half the Pico pin pitch
COLS, ROWS = 104, 75
W, TOP = 2400, 190                          # TOP: room for the title and the step text
H = TOP + ROWS * G + 90
PANEL = 760                                 # connection chart on the right
WT = W + PANEL

C = dict(red="#d62828", blk="#222222", org="#f08c00", blu="#1c64d6", grn="#1f9d55", olv="#7a8b1e",
         pur="#8e44ad", brn="#9c5a1c", yel="#e9c400", usb="#7d7d85")

def px(i):
    return i * G

# ---------------- component drawings ----------------
pins = {}                                   # name -> (col, row, dcol, drow)
boxes = []                                  # obstacles in px (x0, y0, x1, y1)
DIRS = {"L": (-1, 0), "R": (1, 0), "U": (0, -1), "D": (0, 1)}

def pin(name, c, r, d):
    pins[name] = (c, r) + DIRS[d]

def box(x0, y0, x1, y1):
    boxes.append((x0, y0, x1, y1))

def rect(o, x, y, w, h, fill, stroke="#333", rx=8, sw=2):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def t(o, x, y, s, size=16, col="#222", anchor="middle", bold=False, mono=False):
    fam = "Consolas,monospace" if mono else "Segoe UI,Arial,sans-serif"
    o.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{col}" text-anchor="{anchor}"'
             f'{" font-weight=\"bold\"" if bold else ""}>{E(s)}</text>')

def gold(o, x, y, s=14, on=True):
    o.append(f'<rect x="{x - s / 2}" y="{y - s / 2}" width="{s}" height="{s}" fill="{"#c9a227" if on else "#ccc"}" stroke="#7a6212" stroke-width="1"/>')

PICO_L = {1: "GP0", 2: "GP1", 3: "GND", 4: "GP2", 5: "GP3", 6: "GP4", 7: "GP5", 8: "GND", 9: "GP6", 10: "GP7",
          11: "GP8", 12: "GP9", 13: "GND", 14: "GP10", 15: "GP11", 16: "GP12", 17: "GP13", 18: "GND", 19: "GP14", 20: "GP15"}
PICO_R = {21: "GP16", 22: "GP17", 23: "GND", 24: "GP18", 25: "GP19", 26: "GP20", 27: "GP21", 28: "GND", 29: "GP22", 30: "RUN",
          31: "GP26", 32: "GP27", 33: "AGND", 34: "GP28", 35: "VREF", 36: "3V3", 37: "3V3_EN", 38: "GND", 39: "VSYS", 40: "VBUS"}
USED = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 23, 28, 29, 31, 33, 36, 38, 39, 40}
PL, PR = 44, 60                             # pad columns

def pico(o):
    x0, x1, y0, y1 = px(PL) - 16, px(PR) + 16, px(14) - 30, px(52) + 30
    rect(o, x0, y0, x1 - x0, y1 - y0, "#1f7a3a", "#0f4f24", 14, 3); box(x0, y0, x1, y1)
    cx = (x0 + x1) / 2
    rect(o, cx - 30, y0 - 38, 60, 40, "#b8b8bd", "#666", 4); box(cx - 30, y0 - 38, cx + 30, y0)
    pin("pico.usb", 52, 11, "U")
    t(o, cx, px(29), "Raspberry Pi", 22, "#e8f5e9", bold=True)
    t(o, cx, px(30) + 8, "Pico 2 W", 30, "#ffffff", bold=True)
    for k, s in enumerate(["labels as printed on the", "pin side (mounted pins up)", "pin numbers in grey"]):
        t(o, cx, px(32) + k * 18, s, 13, "#cfe8d4")
    rect(o, cx - 35, px(38), 70, 70, "#2b2b2b", "#111", 4)
    t(o, cx, px(38) + 40, "RP2350", 13, "#bbb", bold=True)
    for n in range(1, 41):
        left = n <= 20
        r = 14 + 2 * (n - 1) if left else 14 + 2 * (40 - n)
        c = PL if left else PR
        x, y, used = px(c), px(r), n in USED
        o.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{"#e0b43a" if used else "#ddd"}" stroke="#555" stroke-width="1.5"/>')
        lab = PICO_L[n] if left else PICO_R[n]
        t(o, x + (16 if left else -16), y + 5, lab, 15, "#fff" if used else "#8fb59a", "start" if left else "end", True, True)
        t(o, x + (98 if left else -98), y + 5, str(n), 13, "#cfe8d4" if used else "#6f9d7c", "start" if left else "end", False, True)
        pin(f"pico.{n}", c, r, "L" if left else "R")

def usb_port(o):
    x0, y0, x1, y1 = px(46), px(4), px(58), px(8)
    rect(o, x0, y0, x1 - x0, y1 - y0, "#2a2a2e", "#111", 12, 3); box(x0, y0, x1, y1)
    rect(o, (x0 + x1) / 2 - 45, y0 + 18, 90, 34, "#c8c8cc", "#666", 3)
    o.append(f'<rect x="{(x0 + x1) / 2 - 35}" y="{y0 + 26}" width="70" height="10" fill="#222"/>')
    t(o, (x0 + x1) / 2, y0 + 76, "USB-A feedthrough (rear port)", 14, "#ddd", bold=True)
    pin("usb.in", 52, 8, "D")

def trackball(o):
    x0, y0, x1, y1 = px(4), px(15), px(26), px(33) + 12
    rect(o, x0, y0, x1 - x0, y1 - y0, "#2a2a2e", "#111", 20, 3); box(x0, y0, x1, y1)
    cx, cy = x0 + 200, (y0 + y1) / 2 - 20
    o.append(f'<circle cx="{cx}" cy="{cy}" r="150" fill="#151515"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="134" fill="#eceaf2" stroke="#bbb" stroke-width="2"/>')
    o.append(f'<circle cx="{cx - 40}" cy="{cy - 45}" r="34" fill="#ffffff" opacity="0.7"/>')
    t(o, x0 + 190, y1 - 16, '3" trackball (seen from below)', 18, "#ddd", bold=True)
    # ball light lead comes out of the left side
    for lab, r in (("ball light +", 28), ("ball light −", 29)):
        gold(o, x0 + 8, px(r), 12)
        t(o, x0 + 22, px(r) + 5, lab, 13, "#ddd", "start", True)
    pin("tb.RGB+", 4, 28, "L"); pin("tb.RGB-", 4, 29, "L")
    rect(o, px(20), px(17) + 4, px(26) - 8 - px(20), px(32) - px(17), "#1f7a3a", "#0f4f24", 6)
    t(o, px(22) + 18, px(18) + 4, "J1", 18, "#fff", bold=True)
    for i, lab in enumerate(["+5V", "DATA", "CLOCK", "GND", "M", "R", "L"]):
        r = 19 + 2 * i
        used = lab in ("+5V", "DATA", "CLOCK", "GND")
        gold(o, px(26) - 10, px(r), 14, used)
        t(o, px(26) - 24, px(r) + 5, lab, 15, "#fff" if used else "#9bb", "end", True, True)
        pin(f"tb.{lab}", 26, r, "R")

def buttons(o):
    t(o, px(4), px(53) + 6, "3 lit buttons — 3-pin XH plugs, pins 1-2-3 top to bottom", 15, "#444", "start")
    for i, name in enumerate(["LEFT", "RIGHT", "MENU"]):
        r0 = 37 + 6 * i
        cy = px(r0 + 1)
        o.append(f'<circle cx="{px(7)}" cy="{cy}" r="50" fill="#e9e9ee" stroke="#aaa" stroke-width="3"/>')
        o.append(f'<circle cx="{px(7)}" cy="{cy}" r="34" fill="#ffffff" stroke="#ccc" stroke-width="2"/>')
        t(o, px(7), cy + 5, name, 15, "#333", bold=True)
        x0, y0, x1, y1 = px(22), px(r0) - 16, px(26), px(r0 + 2) + 16
        rect(o, x0, y0, x1 - x0, y1 - y0, "#f4f4f4", "#888", 6); box(x0, y0, x1, y1)
        box(px(7) - 52, cy - 52, x0, cy + 52)                                   # button + its lead
        o.append(f'<rect x="{x0 - 8}" y="{y0 + 14}" width="8" height="{y1 - y0 - 28}" fill="#bbb"/>')   # latch
        o.append(f'<path d="M{px(7) + 50} {cy} L {x0 - 8} {cy}" stroke="#555" stroke-width="5" fill="none"/>')
        for k, lab in enumerate(["1 LED−", "2 switch", "3 LED+/com"]):
            r = r0 + k
            gold(o, px(26) - 8, px(r), 12)
            t(o, px(26) - 18, px(r) + 5, lab, 12, "#444", "end")
            pin(f"btn{i}.{k + 1}", 26, r, "R")
        t(o, px(15), cy - 12, f"{name} button lead", 13, "#777")

EP_PINS = ["BUSY", "RST", "DC", "CS", "CLK", "DIN", "GND", "VCC"]   # lead drawn VCC-end down

def epaper(o):
    x0, y0, x1, y1 = px(4), px(55), px(26), px(68)
    rect(o, x0, y0, x1 - x0, y1 - y0, "#151515", "#000", 10, 3); box(x0, y0, x1, y1)
    rect(o, x0 + 24, y0 + 30, 330, 200, "#d8d6cf", "#999", 4)
    t(o, x0 + 189, y0 + 120, "GT Trackball", 22, "#222", bold=True, mono=True)
    t(o, x0 + 189, y0 + 160, "2.13\" e-Paper HAT V4", 16, "#555")
    t(o, x0 + 200, y1 - 16, "Waveshare 2.13\" e-Paper HAT V4 — 8-pin lead", 15, "#ccc")
    rect(o, px(26) - 72, px(57) - 18, 64, 7 * G + 36, "#f2f2f2", "#999", 4)
    for i, lab in enumerate(EP_PINS):
        r = 57 + i
        gold(o, px(26) - 8, px(r), 12)
        t(o, px(26) - 20, px(r) + 5, lab, 13, "#333", "end", True, True)
        pin(f"ep.{lab}", 26, r, "R")

def battery(o):
    x0, y0, x1, y1 = px(76), px(1) - 6, px(91), px(5)
    rect(o, x0, y0, x1 - x0, y1 - y0, "#c9ccd1", "#888", 14, 3); box(x0, y0, x1, y1)
    rect(o, x0, y1 - 22, x1 - x0, 22, "#e8a020", "#a86a00", 6)
    t(o, (x0 + x1) / 2, y0 + 36, "LiPo 3.7 V   52 × 35 × 10 mm", 20, "#333", bold=True)
    t(o, px(80) + 12, y1 - 6, "black −", 13, "#222", "start"); t(o, px(86) + 12, y1 - 6, "red +", 13, "#a00", "start")
    pin("bat.-", 80, 5, "D"); pin("bat.+", 86, 5, "D")

def pigtail_charger(o):
    x0, y0, x1, y1 = px(76), px(9), px(91), px(22)
    rect(o, x0, y0, x1 - x0, y1 - y0, "#1b1b1d", "#000", 10, 3); box(x0, y0, x1, y1)
    t(o, x0 + 200, y0 + 128, "Charger + 5 V boost", 20, "#fff", bold=True)
    rect(o, x0 + 120, y0 + 150, 80, 80, "#333", "#555", 10); t(o, x0 + 160, y0 + 197, "100", 20, "#999", bold=True)
    o.append(f'<rect x="{x0 + 230}" y="{y0 + 160}" width="40" height="40" fill="#2a63c8"/>')
    t(o, x0 + 250, y0 + 220, "trimpot", 12, "#9ab", bold=True)
    t(o, x0 + 200, y0 + 270, "set VO+ to 5.00 V first", 15, "#ff8a80", bold=True)
    for lab, c in (("B−", 80), ("B+", 86)):
        gold(o, px(c), y0 + 10, 16)
        t(o, px(c), y0 + 40, lab, 16, "#fff", bold=True, mono=True)
        pin("chg." + lab, c, 9, "U")
    # USB-C jack with the pigtail plugged in
    rect(o, x0 - 14, px(12) - 8, 30, px(14) - px(12) + 16, "#c8c8cc", "#666", 4)
    rect(o, px(71), px(12) - 12, x0 - 14 - px(71), px(14) - px(12) + 24, "#3a3a3a", "#111", 8)
    box(px(71), px(12) - 12, x0, px(14) + 12)
    t(o, px(73) + 12, px(12) - 20, "USB-C pigtail", 13, "#555", bold=True)
    for r in (13, 14):
        gold(o, px(71) + 8, px(r), 10)
    pin("pig.blk", 71, 13, "L"); pin("pig.red", 71, 14, "L")
    for lab, r in (("VO+", 16), ("VO−", 18)):
        gold(o, x0 + 10, px(r), 16)
        t(o, x0 + 26, px(r) + 6, lab, 16, "#fff", "start", True, True)
        pin("chg." + lab, 76, r, "L")

def lever(o):
    x0, y0, x1, y1 = px(70) - 4, px(16) - 13, px(73) + 4, px(16) + 13
    rect(o, x0, y0, x1 - x0, y1 - y0, "#f3f3f3", "#888", 5); box(x0, y0, x1, y1)
    for k in range(3):
        o.append(f'<rect x="{x0 + 6 + k * 22}" y="{y0 + 5}" width="14" height="16" rx="3" fill="#f08c00"/>')
    t(o, x0 - 6, y0 - 8, "lever connector", 12, "#555", "end", bold=True)
    pin("lev.OUT1", 70, 16, "L"); pin("lev.IN", 73, 16, "R"); pin("lev.OUT2", 72, 16, "D")

def sensor(o):
    x0, y0, x1, y1 = px(76), px(25), px(91), px(33)
    rect(o, x0, y0, x1 - x0, y1 - y0, "#b3261e", "#6d120c", 10, 3); box(x0, y0, x1, y1)
    t(o, x0 + 175, y0 + 80, "Voltage sensor ÷5", 20, "#fff", bold=True)
    t(o, x0 + 175, y0 + 106, "0-25 V module", 14, "#ffd6d3")
    t(o, x0 + 175, y0 + 130, "GND screw stays empty", 13, "#ffd6d3")
    for lab, r, used in (("−", 28, True), ("+", 30, False), ("S", 32, True)):
        gold(o, x0 + 8, px(r), 14, used)
        t(o, x0 + 24, px(r) + 6, lab, 16, "#fff" if used else "#f4c7c3", "start", True, True)
        pin("sen." + lab, 76, r, "L")
    for lab, r, used in (("VCC", 27, True), ("GND", 30, False)):
        rect(o, x1 - 30, px(r) - 18, 26, 36, "#1f9d55" if used else "#7cbf98", "#0c5a2e", 5)
        t(o, x1 - 38, px(r) + 5, lab, 13, "#fff" if used else "#f4c7c3", "end", True, True)
        pin("sen." + lab, 91, r, "R")

def mosfet(o):
    x0, y0, x1, y1 = px(72), px(35), px(91), px(45)
    rect(o, x0, y0, x1 - x0, y1 - y0, "#1d4fa8", "#0c2f6f", 10, 3); box(x0, y0, x1, y1)
    t(o, x0 + 250, y0 + 70, "MOSFET module (XY-MOS)", 20, "#fff", bold=True)
    t(o, x0 + 250, y0 + 96, "switches the trackball off in sleep", 14, "#cdd9f5")
    for lab, r in (("TRIG", 36), ("GND", 38)):
        gold(o, x0 + 8, px(r), 12)
        t(o, x0 + 22, px(r) + 5, lab, 14, "#fff", "start", True, True)
        pin("fet." + lab, 72, r, "L")
    rect(o, x0 + 4, px(41) - 16, 30, 32, "#2a63c8", "#0c2f6f", 5)
    t(o, x0 + 42, px(41) + 6, "VIN−", 15, "#fff", "start", True, True); pin("fet.VIN−", 72, 41, "L")
    rect(o, px(77) - 16, y0 + 4, 32, 30, "#2a63c8", "#0c2f6f", 5)
    t(o, px(77) + 22, y0 + 26, "VIN+", 15, "#fff", "start", True, True); pin("fet.VIN+", 77, 35, "U")
    for lab, cols in (("OUT−", (79, 80)), ("OUT+", (85, 84))):
        lo, hi = min(cols), max(cols)
        rect(o, px(lo) - 16, y1 - 34, px(hi) - px(lo) + 32, 30, "#2a63c8", "#0c2f6f", 5)
        t(o, (px(lo) + px(hi)) / 2, y1 - 44, lab, 15, "#fff", "middle", True, True)
        for k, c in enumerate(cols):
            pin("fet." + lab + "ab"[k], c, 45, "D")

COMPONENTS = [pico, usb_port, trackball, buttons, epaper, battery, pigtail_charger, lever, sensor, mosfet]

# ---------------- wires: (from, to, colour, step, net) ----------------
WIRES = [
    ("usb.in", "pico.usb", "usb", "power", "USB"),
    ("pig.red", "pico.40", "red", "power", "VBUS"),
    ("pig.blk", "pico.3", "blk", "power", "GND3"),
    ("bat.+", "chg.B+", "red", "power", "B+"),
    ("bat.-", "chg.B−", "blk", "power", "B-"),
    ("chg.VO+", "lev.IN", "red", "power", "5V"),
    ("lev.OUT1", "pico.39", "red", "power", "5V"),
    ("lev.OUT2", "fet.VIN+", "red", "power", "5V"),
    ("chg.VO−", "pico.38", "blk", "power", "GND38"),
    ("fet.VIN−", "pico.23", "blk", "power", "GND23"),
    ("sen.VCC", "chg.B+", "red", "power", "B+"),
    ("sen.S", "pico.31", "brn", "power", "SENSE"),
    ("sen.−", "pico.33", "blk", "power", "AGND"),
    ("fet.TRIG", "pico.29", "brn", "trackball", "TRIG"),
    ("fet.GND", "pico.28", "blk", "trackball", "GND28"),
    ("tb.DATA", "pico.4", "blu", "trackball", "DATA"),
    ("tb.CLOCK", "pico.5", "blu", "trackball", "CLK"),
    ("fet.OUT+a", "tb.+5V", "red", "trackball", "TB+"),
    ("fet.OUT−a", "tb.GND", "blk", "trackball", "TB-"),
    ("fet.OUT+b", "tb.RGB+", "yel", "trackball", "RGB+"),
    ("fet.OUT−b", "tb.RGB-", "blk", "trackball", "RGB-"),
    ("btn0.2", "pico.6", "grn", "buttons", "SW_L"),
    ("btn1.2", "pico.7", "grn", "buttons", "SW_R"),
    ("btn2.2", "pico.9", "grn", "buttons", "SW_M"),
    ("btn0.3", "pico.10", "olv", "buttons", "COM"),
    ("btn1.3", "pico.10", "olv", "buttons", "COM"),
    ("btn2.3", "pico.10", "olv", "buttons", "COM"),
    ("btn0.1", "pico.8", "blk", "buttons", "BGND"),
    ("btn1.1", "pico.8", "blk", "buttons", "BGND"),
    ("btn2.1", "pico.8", "blk", "buttons", "BGND"),
    ("ep.VCC", "pico.36", "org", "display", "3V3"),
    ("ep.GND", "pico.18", "blk", "display", "EGND"),
    ("ep.DIN", "pico.15", "pur", "display", "DIN"),
    ("ep.CLK", "pico.14", "pur", "display", "SCK"),
    ("ep.CS", "pico.12", "pur", "display", "CS"),
    ("ep.DC", "pico.11", "pur", "display", "DC"),
    ("ep.RST", "pico.16", "pur", "display", "RST"),
    ("ep.BUSY", "pico.17", "pur", "display", "BUSY"),
]

# ---------------- grid router ----------------
BEND, CROSS, NEAR_BOX, SHARE, CLASH = 4.0, 30.0, 1.5, 0.15, 2000.0

def route_all():
    blocked = set()
    near = set()
    for (x0, y0, x1, y1) in boxes:
        for c in range(COLS):
            for r in range(ROWS):
                x, y = px(c), px(r)
                if x0 - 6 <= x <= x1 + 6 and y0 - 6 <= y <= y1 + 6:
                    blocked.add((c, r))
                elif x0 - G - 6 <= x <= x1 + G + 6 and y0 - G - 6 <= y <= y1 + G + 6:
                    near.add((c, r))
    # keep wires from running along the Pico's pin rows
    for r in range(12, 55):
        for c in (PL - 1, PR + 1):
            blocked.add((c, r))
    stub = {}                                   # stub cell -> net
    for a, b, col, grp, net in WIRES:
        for p in (a, b):
            c, r, dc, dr = pins[p]
            stub[(c + dc, r + dr)] = net
            blocked.discard((c + dc, r + dr))
    occ = {}                                    # cell -> {net: set("h"/"v"/"x" for bend/end)}

    def add(path, net, on=True):
        for k, cell in enumerate(path):
            marks = set()
            if k > 0:
                marks.add("h" if path[k - 1][1] == cell[1] else "v")
            if k + 1 < len(path):
                marks.add("h" if path[k + 1][1] == cell[1] else "v")
            if len(marks) > 1 or k in (0, len(path) - 1):
                marks.add("x")
            d = occ.setdefault(cell, {})
            if on:
                d.setdefault(net, [set(), 0])
                d[net][0] |= marks; d[net][1] += 1
            else:
                d[net][1] -= 1
                if d[net][1] == 0:
                    del d[net]

    def astar(a, b, net):
        ca, ra, dca, dra = pins[a]
        cb, rb, dcb, drb = pins[b]
        s, g = (ca + dca, ra + dra), (cb + dcb, rb + drb)
        start_dir = (dca, dra)
        end_dir = (-dcb, -drb)                  # direction of travel into pin b
        h = lambda cell: abs(cell[0] - g[0]) + abs(cell[1] - g[1])
        best = {(s, start_dir): 0.0}
        prev = {}
        pq = [(h(s), 0.0, s, start_dir)]
        while pq:
            f, cost, cell, d = heapq.heappop(pq)
            if cost > best.get((cell, d), 1e18):
                continue
            if cell == g:
                tot = cost + (BEND if d != end_dir else 0)
                final = (cell, d)
                # accept the first goal pop (bend into the pin is small vs. alternatives)
                path = [cell]
                st = final
                while st in prev:
                    st = prev[st]; path.append(st[0])
                return path[::-1], tot
            others = {n: v for n, v in occ.get(cell, {}).items() if n != net}
            for nd in DIRS.values():
                if nd == (-d[0], -d[1]):
                    continue
                nc = (cell[0] + nd[0], cell[1] + nd[1])
                if not (0 <= nc[0] < COLS and 0 <= nc[1] < ROWS) or nc in blocked:
                    continue
                if nc in stub and stub[nc] != net:
                    continue
                o2 = {n: v for n, v in occ.get(nc, {}).items() if n != net}
                orient = "h" if nd[1] == 0 else "v"
                step = 1.0
                if nd != d and others:          # bending on a cell another wire uses
                    step += CLASH
                if o2:
                    if any(orient in v[0] or "x" in v[0] for v in o2.values()):
                        step += CLASH           # would run along / touch another wire
                    else:
                        step += CROSS
                if net in occ.get(nc, {}):
                    step = min(step, SHARE + (CROSS if o2 else 0))
                if nc in near:
                    step += NEAR_BOX
                if nd != d:
                    step += BEND
                nc_cost = cost + step
                if nc_cost < best.get((nc, nd), 1e18):
                    best[(nc, nd)] = nc_cost
                    prev[(nc, nd)] = (cell, d)
                    heapq.heappush(pq, (nc_cost + h(nc), nc_cost, nc, nd))
        raise RuntimeError(f"no route {a} -> {b}")

    def manhattan(w):
        a, b = pins[w[0]], pins[w[1]]
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    order = sorted(range(len(WIRES)), key=lambda i: manhattan(WIRES[i]))
    paths = {}
    for i in order:
        a, b, col, grp, net = WIRES[i]
        paths[i], _ = astar(a, b, net)
        add(paths[i], net)
    for _ in range(4):                          # rip up and reroute
        for i in order:
            a, b, col, grp, net = WIRES[i]
            add(paths[i], net, False)
            paths[i], _ = astar(a, b, net)
            add(paths[i], net)
    clashes = 0
    for cell, d in occ.items():
        if len(d) > 1:
            marks = [v[0] for v in d.values()]
            if any("x" in m for m in marks) or sum("h" in m for m in marks) > 1 or sum("v" in m for m in marks) > 1:
                clashes += 1; print("clash at", cell, list(d))
    print("clashes:", clashes)
    return paths, occ

# ---------------- drawing ----------------
def polyline(i, path):
    a, b = WIRES[i][0], WIRES[i][1]
    ca, ra, _, _ = pins[a]; cb, rb, _, _ = pins[b]
    pts = [(ca, ra)] + list(path) + [(cb, rb)]
    out = [pts[0]]
    for k in range(1, len(pts) - 1):
        p0, p1, p2 = out[-1], pts[k], pts[k + 1]
        if (p0[0] == p1[0] == p2[0]) or (p0[1] == p1[1] == p2[1]):
            continue
        out.append(p1)
    out.append(pts[-1])
    return [(px(c), px(r)) for c, r in out]

def path_d(pts, hops, R=10, HR=9):
    """Square route with rounded corners; hops = list of (x, y) where this wire bridges another."""
    d = f"M{pts[0][0]} {pts[0][1]}"
    n = len(pts)
    for k in range(1, n):
        (x0, y0), (x1, y1) = pts[k - 1], pts[k]
        horiz = y0 == y1
        sgn = 1 if (x1 > x0 if horiz else y1 > y0) else -1
        # segment start/end trimmed for the corners
        s0 = (x0, y0) if k == 1 else ((x0 + sgn * R, y0) if horiz else (x0, y0 + sgn * R))
        e1 = (x1, y1) if k == n - 1 else ((x1 - sgn * R, y1) if horiz else (x1, y1 - sgn * R))
        hs = [(hx, hy) for hx, hy in hops if (hy == y0 and min(x0, x1) + R + HR < hx < max(x0, x1) - R - HR) if horiz]
        hs += [(hx, hy) for hx, hy in hops if (not horiz and hx == x0 and min(y0, y1) + R + HR < hy < max(y0, y1) - R - HR)]
        hs.sort(key=lambda p: sgn * (p[0] if horiz else p[1]))
        for hx, hy in hs:
            if horiz:
                d += f" L {hx - sgn * HR} {hy} A {HR} {HR} 0 0 {1 if sgn > 0 else 0} {hx + sgn * HR} {hy}"
            else:
                d += f" L {hx} {hy - sgn * HR} A {HR} {HR} 0 0 {1 if sgn > 0 else 0} {hx} {hy + sgn * HR}"
        d += f" L {e1[0]} {e1[1]}"
        if k < n - 1:
            x2, y2 = pts[k + 1]
            nx = (x1 + (R if x2 > x1 else -R), y1) if y1 == y2 else (x1, y1 + (R if y2 > y1 else -R))
            d += f" Q {x1} {y1} {nx[0]} {nx[1]}"
    return d

def segments(pts):
    return [(pts[k - 1], pts[k]) for k in range(1, len(pts))]

def crossings(pa, pb):
    """Points where a segment of pa crosses a segment of pb at right angles (interiors only)."""
    out = []
    for (a0, a1) in segments(pa):
        for (b0, b1) in segments(pb):
            ha, hb = a0[1] == a1[1], b0[1] == b1[1]
            if ha == hb:
                continue
            h0, h1, v0, v1 = (a0, a1, b0, b1) if ha else (b0, b1, a0, a1)
            x, y = v0[0], h0[1]
            if min(h0[0], h1[0]) < x < max(h0[0], h1[0]) and min(v0[1], v1[1]) < y < max(v0[1], v1[1]):
                out.append((x, y))
    return out

def junctions(paths):
    dots = []
    bynet = {}
    for i, p in paths.items():
        bynet.setdefault(WIRES[i][4], []).append(i)
    for net, idx in bynet.items():
        if len(idx) < 2:
            continue
        dirs = {}
        for i in idx:
            cells = [pins[WIRES[i][0]][:2]] + paths[i] + [pins[WIRES[i][1]][:2]]
            for k, cell in enumerate(cells):
                for j in (k - 1, k + 1):
                    if 0 <= j < len(cells):
                        dirs.setdefault(cell, set()).add((cells[j][0] - cell[0], cells[j][1] - cell[1]))
        for cell, ds in dirs.items():
            if len(ds) >= 3:
                dots.append((px(cell[0]), px(cell[1]), WIRES[idx[0]][2]))
    return dots

# ---------------- connection chart ----------------
BTN = ["LEFT", "RIGHT", "MENU"]
BTN_PIN = {"1": "pin 1 (LED−)", "2": "pin 2 (switch)", "3": "pin 3 (LED+/com)"}
PART = {"usb": "USB-A feedthrough", "pig": "USB-C pigtail", "bat": "Battery", "chg": "Charger", "lev": "Lever connector",
        "fet": "MOSFET", "sen": "Voltage sensor", "tb": "Trackball J1", "ep": "E-paper"}

def pin_name(p):
    part, name = p.split(".", 1)
    if part == "pico":
        if name == "usb":
            return "micro-USB jack"
        n = int(name)
        return f"{(PICO_L if n <= 20 else PICO_R)[n]}  (pin {n})"
    if part.startswith("btn"):
        return f"{BTN[int(part[3])]} button {BTN_PIN[name]}"
    if part == "pig":
        return "USB-C pigtail " + {"red": "red", "blk": "black"}[name]
    if part == "bat":
        return "Battery " + {"+": "red +", "-": "black −"}[name]
    if part == "lev":
        return "Lever connector"
    if part == "fet":
        name = name.rstrip("ab")
    if part == "tb" and name.startswith("RGB"):
        return "Ball light " + ("yellow +" if name.endswith("+") else "black −")
    if part == "usb":
        return "USB-A feedthrough"
    return f"{PART[part]} {name}"

STEP_TITLES = {"power": "3.1  Power and charging", "trackball": "3.2  Trackball",
               "buttons": "3.3  Buttons", "display": "3.4  E-paper display"}

def chart(focus):
    o = []
    x0 = W + 10
    rect(o, x0, 20, PANEL - 40, H - 130, "#ffffff", "#d6d6dc", 12, 2)
    t(o, x0 + 24, 64, "Connections" + ("" if not focus else " — this step"), 28, "#111", "start", True)
    t(o, x0 + 24, 94, "Pico pin  →  where it goes", 18, "#666", "start")
    y = 118
    groups = [focus] if focus else list(STEP_TITLES)
    RH = 38 if focus else 34
    for g in groups:
        rows = []
        for a, b, col, grp, net in WIRES:
            if grp != g:
                continue
            if a.startswith("pico."):
                a, b = b, a
            if b.startswith("pico.") and b != "pico.usb":
                key = (0, int(b.split(".")[1]))
                left, right = pin_name(b), pin_name(a)
            else:
                key = (1, 0)
                left, right = pin_name(a), pin_name(b)
            rows.append((key, col, left, right))
        rows.sort(key=lambda r: r[0])
        if not focus:
            y += 14
            t(o, x0 + 24, y + 16, STEP_TITLES[g], 21, "#333", "start", True)
            y += 30
        for k, (key, col, left, right) in enumerate(rows):
            if k % 2 == 0:
                o.append(f'<rect x="{x0 + 12}" y="{y}" width="{PANEL - 64}" height="{RH}" fill="#f3f4f7"/>')
            o.append(f'<line x1="{x0 + 24}" y1="{y + RH / 2}" x2="{x0 + 58}" y2="{y + RH / 2}" stroke="{C[col]}" stroke-width="8" stroke-linecap="round"/>')
            t(o, x0 + 72, y + RH / 2 + 7, left, 19, "#111", "start", key[0] == 0, key[0] == 0)
            t(o, x0 + 268, y + RH / 2 + 7, "→", 19, "#888", "middle")
            t(o, x0 + 288, y + RH / 2 + 7, right, 19, "#222", "start")
            y += RH
    return o

def build(paths, focus=None, title="", subtitle="", steps=None):
    o = []
    for f in COMPONENTS:
        f(o)
    polys = {i: polyline(i, p) for i, p in paths.items()}
    on = {i: focus is None or WIRES[i][3] == focus for i in paths}
    order = sorted(paths, key=lambda i: (on[i], WIRES[i][2] == "usb"))
    drawn = []
    for i in order:
        a, b, col, grp, net = WIRES[i]
        hops = []
        for j in drawn:
            if WIRES[j][4] != net:
                hops += crossings(polys[i], polys[j])
        drawn.append(i)
        d = path_d(polys[i], hops)
        w = 10 if col == "usb" else 6
        op = 1.0 if on[i] else 0.13
        o.append(f'<path d="{d}" fill="none" stroke="#fbfbfc" stroke-opacity="{op}" stroke-width="{w + 8}" stroke-linejoin="round"/>')
        o.append(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="{0.45 * op}" stroke-width="{w + 2.5}" stroke-linejoin="round"/>')
        o.append(f'<path d="{d}" fill="none" stroke="{C[col]}" stroke-opacity="{op}" stroke-width="{w}" stroke-linejoin="round"/>')
        if on[i]:
            for p in (polys[i][0], polys[i][-1]):
                o.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="5" fill="#fff" stroke="{C[col]}" stroke-width="3"/>')
    for x, y, col in junctions(paths):
        net_on = any(on[i] for i in paths if WIRES[i][2] == col)
        o.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{C[col]}" stroke="#fff" stroke-width="2" opacity="{1 if net_on else 0.13}"/>')
    head = [f'<rect width="{WT}" height="{H}" fill="#fbfbfc"/>'] + chart(focus)
    t(head, 40, 50, title, 34, "#111", "start", True)
    t(head, 40, 84, subtitle, 18, "#555", "start")
    for k, s in enumerate(steps or []):
        t(head, 40, 118 + k * 24, s, 16, "#333", "start")
    leg = [("red", "+5 V / VBUS / B+"), ("blk", "GND"), ("org", "3.3 V"), ("blu", "PS/2 data"), ("grn", "button switch"),
           ("olv", "button common"), ("pur", "display SPI"), ("brn", "control / sense"), ("yel", "ball light +"),
           ("usb", "USB cable")]
    for k, (c, s) in enumerate(leg):
        x = 40 + (k % 5) * 230; y = H - 62 + (k // 5) * 30
        head.append(f'<line x1="{x}" y1="{y}" x2="{x + 40}" y2="{y}" stroke="{C[c]}" stroke-width="7" stroke-linecap="round"/>')
        t(head, x + 52, y + 6, s, 16, "#333", "start")
    t(head, W - 40, H - 32, "bridge = wires cross, not joined     dot = wires joined", 16, "#555", "end")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WT}" height="{H}" viewBox="0 0 {WT} {H}">'
            + "".join(head) + f'<g transform="translate(0,{TOP})">' + "".join(o) + "</g></svg>")

PAGES = [
    ("wiring", None, "GT Trackball — complete wiring",
     "Every connection. Colours are a suggestion; what matters is which pin goes where. Grey numbers = Pico physical pins.", None),
    ("wiring_1_power", "power", "Step 3.1 — Power and charging",
     "Battery → charger/boost → 5 V to the Pico and the MOSFET module; USB charges through the pigtail.",
     ["1. Set the charger's output to 5.00 V with nothing connected.   2. Battery red → B+, black → B−.",
      "3. VO+ → lever connector → Pico VSYS (39) and MOSFET VIN+.   4. VO− → Pico GND (38).   5. MOSFET VIN− → Pico GND (23).",
      "6. Pico VBUS (40) / GND (3) → USB-C pigtail → charger USB-C.   7. Sensor VCC → B+, S → GP26 (31), − → AGND (33); its GND stays empty."]),
    ("wiring_2_trackball", "trackball", "Step 3.2 — Trackball",
     "The trackball's own board talks PS/2 to the Pico; the MOSFET module switches its power off in sleep.",
     ["1. Unplug the trackball's USB cable from J1.   2. J1 DATA → GP2 (4), CLOCK → GP3 (5).",
      "3. MOSFET OUT+ → J1 +5V and the ball light's yellow wire; OUT− → J1 GND and the ball light's black wire.",
      "4. MOSFET TRIG → GP22 (29), its GND → Pico GND (28).   J1 M / R / L stay unconnected."]),
    ("wiring_3_buttons", "buttons", "Step 3.3 — Buttons",
     "Each button's 3-pin plug: pin 1 = LED −, pin 2 = switch, pin 3 = LED + and the switch's other side.",
     ["1. Check each lead first: 5 V on pin 3 and GND on pin 1 lights the button (wire colours vary — go by position).",
      "2. Pin 2: LEFT → GP4 (6), RIGHT → GP5 (7), MENU → GP6 (9).   3. All three pin 3s → GP7 (10).   4. All three pin 1s → GND (8)."]),
    ("wiring_4_display", "display", "Step 3.4 — E-paper display",
     "Waveshare 2.13\" e-Paper HAT V4 on its 8-pin lead. 3.3 V only — never 5 V.",
     ["VCC → 3V3 (36), GND → GND (18), DIN → GP11 (15), CLK → GP10 (14), CS → GP9 (12), DC → GP8 (11), RST → GP12 (16), BUSY → GP13 (17)."]),
]

def browser():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if os.path.exists(p):
            return p
    return shutil.which("chromium") or shutil.which("google-chrome")

if __name__ == "__main__":
    pins.clear(); boxes.clear()
    for f in COMPONENTS:
        f([])
    paths, _ = route_all()
    exe = browser()
    tmp = tempfile.mkdtemp(prefix="gtwire_")
    for name, focus, title, sub, steps in PAGES:
        svg = os.path.join(OUT, name + ".svg")
        open(svg, "w", encoding="utf-8").write(build(paths, focus, title, sub, steps))
        print("wrote images/" + name + ".svg")
        if exe:
            html = os.path.join(tmp, name + ".html")
            open(html, "w", encoding="utf-8").write(
                f'<html><body style="margin:0"><img src="file:///{svg.replace(os.sep, "/")}" width="{WT}"></body></html>')
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={WT},{H}",
                            f"--screenshot={os.path.join(OUT, name + '.png')}", "file:///" + html.replace(os.sep, "/")],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("wrote images/" + name + ".png")
    shutil.rmtree(tmp, ignore_errors=True)
