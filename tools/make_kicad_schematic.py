# ============================================================
#  Generate the KiCad schematic  kicad/gt-trackball.kicad_sch
#  from KiCad's own symbol libraries + a few module symbols, then
#  let kicad-cli run ERC and export PDF/SVG.
#      python tools/make_kicad_schematic.py [path\to\KiCad\10.0]
# ============================================================
import math, os, re, subprocess, sys, uuid, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KI = sys.argv[1] if len(sys.argv) > 1 else os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0")
LIBDIR = os.path.join(KI, "share", "kicad", "symbols")
CLI = os.path.join(KI, "bin", "kicad-cli.exe")
OUTDIR = os.path.join(ROOT, "kicad")
PROJECT = "gt-trackball"

# ---------------- s-expressions ----------------
class Q(str):
    """quoted string"""

def parse(text):
    tok = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+', text)
    stack = [[]]
    for t in tok:
        if t == "(":
            stack.append([])
        elif t == ")":
            n = stack.pop(); stack[-1].append(n)
        elif t.startswith('"'):
            stack[-1].append(Q(t[1:-1].replace('\\"', '"')))
        else:
            stack[-1].append(t)
    return stack[0][0]

def dump(n, ind=0):
    if isinstance(n, Q):
        return '"' + n.replace('"', '\\"') + '"'
    if not isinstance(n, list):
        return str(n)
    if all(not isinstance(c, list) for c in n):
        return "(" + " ".join(dump(c) for c in n) + ")"
    pad = "\t" * (ind + 1)
    head = [dump(c) for c in n[:1]]
    rest = []
    for c in n[1:]:
        rest.append("\n" + pad + dump(c, ind + 1) if isinstance(c, list) else " " + dump(c))
    return "(" + head[0] + "".join(rest) + "\n" + "\t" * ind + ")"

def U():
    return Q(str(uuid.uuid4()))

_libs = {}
def lib_symbol(lib, name):
    if lib not in _libs:
        _libs[lib] = parse(open(os.path.join(LIBDIR, lib + ".kicad_sym"), encoding="utf-8").read())
    for n in _libs[lib]:
        if isinstance(n, list) and n[:1] == ["symbol"] and n[1] == name:
            return n
    raise KeyError(lib + ":" + name)

def find_all(n, head):
    out = []
    if isinstance(n, list):
        if n[:1] == [head]:
            out.append(n)
        for c in n:
            out += find_all(c, head)
    return out

def child(n, head):
    for c in n:
        if isinstance(c, list) and c[:1] == [head]:
            return c

def pins_of(sym):
    res = []
    for p in find_all(sym, "pin"):
        at = child(p, "at"); nm = child(p, "name"); no = child(p, "number")
        if at and nm and no:
            res.append(dict(x=float(at[1]), y=float(at[2]), a=float(at[3]), name=str(nm[1]), num=str(no[1]),
                            type=p[1]))
    return res

# ---------------- module symbols (box + named pins) ----------------
def box_symbol(name, left, right, ref="U", w=20.32, top_title=""):
    """left/right: list of (number, name). Pins 2.54 apart, length 2.54."""
    n = max(len(left), len(right))
    h = (n + 1) * 5.08
    y0 = h / 2
    pins = []
    for i, (num, nm) in enumerate(left):
        y = y0 - 5.08 * (i + 1)
        pins.append(["pin", "passive", "line", ["at", f"{-w / 2 - 2.54:.2f}", f"{y:.2f}", "0"], ["length", "2.54"],
                     ["name", Q(nm), ["effects", ["font", ["size", "1.27", "1.27"]]]],
                     ["number", Q(str(num)), ["effects", ["font", ["size", "1.27", "1.27"]]]]])
    for i, (num, nm) in enumerate(right):
        y = y0 - 5.08 * (i + 1)
        pins.append(["pin", "passive", "line", ["at", f"{w / 2 + 2.54:.2f}", f"{y:.2f}", "180"], ["length", "2.54"],
                     ["name", Q(nm), ["effects", ["font", ["size", "1.27", "1.27"]]]],
                     ["number", Q(str(num)), ["effects", ["font", ["size", "1.27", "1.27"]]]]])
    return ["symbol", Q(name), ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
            ["property", Q("Reference"), Q(ref), ["at", "0", f"{y0 + 1.27:.2f}", "0"], ["effects", ["font", ["size", "1.27", "1.27"]]]],
            ["property", Q("Value"), Q(name), ["at", "0", f"{-y0 - 1.27:.2f}", "0"], ["effects", ["font", ["size", "1.27", "1.27"]]]],
            ["property", Q("Footprint"), Q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]],
            ["property", Q("Datasheet"), Q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]],
            ["symbol", Q(name + "_0_1"),
             ["rectangle", ["start", f"{-w / 2:.2f}", f"{y0:.2f}"], ["end", f"{w / 2:.2f}", f"{-y0:.2f}"],
              ["stroke", ["width", "0.254"], ["type", "default"]], ["fill", ["type", "background"]]]],
            ["symbol", Q(name + "_1_1")] + pins]

CUSTOM = {
    "PS1_ChargerBoost": box_symbol("PS1_ChargerBoost", [(1, "IN+ (USB-C)"), (2, "IN- (USB-C)")],
                                   [(3, "VO+"), (4, "VO-"), (5, "B+"), (6, "B-")], "PS", 25.4),
    "Q1_MOSFET_Module": box_symbol("Q1_MOSFET_Module", [(1, "VIN+"), (2, "VIN-"), (5, "TRIG"), (6, "GND")],
                                   [(3, "OUT+"), (4, "OUT-")], "Q", 22.86),
    "U2_VoltageSensor": box_symbol("U2_VoltageSensor", [(1, "VCC"), (2, "GND")], [(3, "S"), (4, "+"), (5, "-")], "U", 20.32),
    "J1_Trackball_PS2": box_symbol("J1_Trackball_PS2", [], [(1, "+5V"), (2, "DATA"), (3, "CLOCK"), (4, "GND"),
                                                           (5, "M"), (6, "R"), (7, "L")], "J", 22.86),
    "DS1_EPaper_HAT": box_symbol("DS1_EPaper_HAT", [(1, "VCC"), (2, "GND"), (3, "DIN"), (4, "CLK"), (5, "CS"),
                                                    (6, "DC"), (7, "RST"), (8, "BUSY")], [], "DS", 22.86),
}

# ---------------- schematic builder ----------------
ROOT_UUID = U()
items, lib_used, counters = [], {}, {}

def libid_symbol(libid):
    lib, name = libid.split(":")
    if lib == "gt":
        s = [*CUSTOM[name]]
    else:
        s = lib_symbol(lib, name)
        s = parse(dump(s))                       # deep copy
    s[1] = Q(libid)
    return s

def place(libid, ref, value, x, y, rot=0, hide_ref=False):
    x, y = round(x / 1.27) * 1.27, round(y / 1.27) * 1.27
    if libid not in lib_used:
        lib_used[libid] = libid_symbol(libid)
    sym = lib_used[libid]
    pins = pins_of(sym)
    def prop_at(name, default):
        for pr in sym:
            if isinstance(pr, list) and pr[:2] == ["property", name]:
                at = child(pr, "at")
                px, py = float(at[1]), float(at[2])
                rr = math.radians(rot)
                ang = int(float(at[3]) if len(at) > 3 else 0)    # KiCad turns fields with the symbol
                eff = child(pr, "effects")
                just = [e for e in (eff or [])[1:] if isinstance(e, list) and e[0] == "justify"]
                return (x + px * math.cos(rr) - py * math.sin(rr), y - (px * math.sin(rr) + py * math.cos(rr)),
                        ang, just)
        return default + (0, [])
    rx, ry, rang, rjust = prop_at("Reference", (x, y - 2))
    vx, vy, vang, vjust = prop_at("Value", (x, y + 2))
    inst = ["symbol", ["lib_id", Q(libid)], ["at", f"{x:.2f}", f"{y:.2f}", str(rot)], ["unit", "1"],
            ["exclude_from_sim", "no"], ["in_bom", "no" if ref.startswith("#") else "yes"], ["on_board", "yes"],
            ["dnp", "no"], ["uuid", U()],
            ["property", Q("Reference"), Q(ref), ["at", f"{rx:.2f}", f"{ry:.2f}", str(rang)],
             ["effects", ["font", ["size", "1.27", "1.27"]]] + rjust + ([["hide", "yes"]] if hide_ref else [])],
            ["property", Q("Value"), Q(value), ["at", f"{vx:.2f}", f"{vy:.2f}", str(vang)],
             ["effects", ["font", ["size", "1.27", "1.27"]]] + vjust],
            ["property", Q("Footprint"), Q(""), ["at", f"{x:.2f}", f"{y:.2f}", "0"],
             ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]],
            ["property", Q("Datasheet"), Q(""), ["at", f"{x:.2f}", f"{y:.2f}", "0"],
             ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]]]
    for p in pins:
        inst.append(["pin", Q(p["num"]), ["uuid", U()]])
    inst.append(["instances", ["project", Q(PROJECT), ["path", Q("/" + ROOT_UUID), ["reference", Q(ref)], ["unit", "1"]]]])
    items.append(inst)
    r = math.radians(rot)
    out = {}
    for p in pins:
        lx = p["x"] * math.cos(r) - p["y"] * math.sin(r)
        ly = p["x"] * math.sin(r) + p["y"] * math.cos(r)
        a = math.radians(p["a"] + rot + 180)                # outward from the body
        dx, dy = round(math.cos(a)), round(math.sin(a))
        pt = dict(x=round(x + lx, 2), y=round(y - ly, 2), dx=dx, dy=-dy, name=p["name"], type=p["type"])
        out[p["num"]] = pt
        out.setdefault("name:" + p["name"], pt)
    return out

def wire(x1, y1, x2, y2):
    items.append(["wire", ["pts", ["xy", f"{x1:.2f}", f"{y1:.2f}"], ["xy", f"{x2:.2f}", f"{y2:.2f}"]],
                  ["stroke", ["width", "0"], ["type", "default"]], ["uuid", U()]])

POWER = {"GND": "power:GND", "+5V": "power:+5V", "+3V3": "power:+3V3", "VBUS": "power:VBUS"}

def pwr_ref():
    counters["pwr"] = counters.get("pwr", 0) + 1
    return f"#PWR{counters['pwr']:02d}"

def net(pin, name, stub=5.08):
    """Short wire out of the pin, then a net label or power symbol."""
    x2, y2 = pin["x"] + pin["dx"] * stub, pin["y"] + pin["dy"] * stub
    wire(pin["x"], pin["y"], x2, y2)
    if name in POWER:
        rot = {1: 90, -1: 270}.get(pin["dx"], 0) if name == "GND" else 0
        place(POWER[name], pwr_ref(), name, x2, y2, rot, hide_ref=True)
    else:
        ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[(pin["dx"], pin["dy"])]
        just = "left" if ang in (0, 90) else "right"
        items.append(["label", Q(name), ["at", f"{x2:.2f}", f"{y2:.2f}", str(ang)], ["fields_autoplaced", "yes"],
                      ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", just, "bottom"]], ["uuid", U()]])

def nc(pin):
    items.append(["no_connect", ["at", f"{pin['x']:.2f}", f"{pin['y']:.2f}"], ["uuid", U()]])

def text(s, x, y, size=1.8, bold=False):
    eff = ["font", ["size", f"{size}", f"{size}"]] + ([["bold", "yes"]] if bold else [])
    items.append(["text", Q(s), ["exclude_from_sim", "no"], ["at", f"{x:.2f}", f"{y:.2f}", "0"],
                  ["effects", eff, ["justify", "left", "bottom"]], ["uuid", U()]])

def frame(x1, y1, x2, y2, title):
    items.append(["rectangle", ["start", f"{x1:.2f}", f"{y1:.2f}"], ["end", f"{x2:.2f}", f"{y2:.2f}"],
                  ["stroke", ["width", "0.2"], ["type", "dash"]], ["fill", ["type", "none"]], ["uuid", U()]])
    text(title, x1 + 1.5, y1 + 4, 2.0, True)

def flag(netname, x, y):
    p = place("power:PWR_FLAG", pwr_ref(), "PWR_FLAG", x, y, 0, hide_ref=True)
    pt = list(p.values())[0]
    net(dict(pt, dx=1, dy=0), netname, 7.62)

# ======================= the circuit =======================
# U1 Pico 2 W (same pinout as the KiCad Pico symbol)
u1 = place("MCU_Module:RaspberryPi_Pico", "U1", "Raspberry Pi Pico 2 W", 205, 145)
U1NET = {"4": "PS2_DATA", "5": "PS2_CLK", "6": "BTN_LEFT", "7": "BTN_RIGHT", "9": "BTN_MENU", "10": "BTN_COM",
         "11": "EPD_DC", "12": "EPD_CS", "14": "EPD_CLK", "15": "EPD_DIN", "16": "EPD_RST", "17": "EPD_BUSY",
         "29": "TB_EN", "31": "BATT_SENSE", "36": "+3V3", "39": "+5V", "40": "VBUS"}
for num, pt in u1.items():
    if num.startswith("name:"):
        continue
    if num in U1NET:
        net(pt, U1NET[num])
    elif pt["name"] == "AGND":
        net(pt, "AGND")
    elif pt["name"] == "GND":
        net(pt, "GND")
    else:
        nc(pt)
frame(170, 95, 245, 205, "CONTROLLER")
text("U1: Pico 2 W, mounted pins-up.", 172, 200, 1.5)

# ---- power + charging ----
frame(18, 22, 150, 124, "POWER, CHARGING, BATTERY SENSE")
j2 = place("Connector:USB_A", "J2", "USB-A feedthrough", 35, 60)
for k, pt in j2.items():
    if k.startswith("name:"):
        continue
    if pt["name"] in ("VBUS",):
        net(pt, "VBUS", 12.7)
    elif pt["name"] == "GND":
        net(pt, "GND")
    else:
        nc(pt)
text("J2 = the rear USB-A port. D+/D- go to U1's micro-USB jack", 22, 32, 1.5)
text("through a short micro-USB-to-A cable (not drawn).", 22, 35.5, 1.5)
ps1 = place("gt:PS1_ChargerBoost", "PS1", "Charger + 5 V boost (TP4056 type)", 95, 52)
net(ps1["1"], "VBUS"); net(ps1["2"], "GND"); net(ps1["3"], "+5V"); net(ps1["4"], "GND")
net(ps1["5"], "BATT+", 10.16); net(ps1["6"], "GND", 10.16)
text("IN via J3: USB-C male pigtail from U1 VBUS/GND.", 75, 72, 1.5)
text("Set VO+ to 5.00 V before connecting anything.", 75, 75.5, 1.5)
bt1 = place("Device:Battery_Cell", "BT1", "LiPo 3.7 V 52x35x10", 40, 95)
net(bt1["1"], "BATT+"); net(bt1["2"], "GND")
r1 = place("Device:R", "R1", "30k", 95, 92)
r2 = place("Device:R", "R2", "7.5k", 95, 106)
net(r1["1"], "BATT+"); wire(r1["2"]["x"], r1["2"]["y"], r2["1"]["x"], r2["1"]["y"]); net(r2["2"], "AGND")
mid_y = round((r1["2"]["y"] + r2["1"]["y"]) / 2 / 1.27) * 1.27
tx = r1["2"]["x"]
wire(tx, mid_y, tx + 10.16, mid_y)
items.append(["junction", ["at", f"{tx:.2f}", f"{mid_y:.2f}"], ["diameter", "0"], ["color", "0", "0", "0", "0"], ["uuid", U()]])
items.append(["label", Q("BATT_SENSE"), ["at", f"{tx + 10.16:.2f}", f"{mid_y:.2f}", "0"], ["fields_autoplaced", "yes"],
              ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", "left", "bottom"]], ["uuid", U()]])
text("U2 sensor module (R1/R2): BATT+ / 5.", 22, 115, 1.5)
text("GND screw empty; S->GP26, - ->AGND.", 22, 118.5, 1.5)
for nm, x in (("+5V", 130), ("BATT+", 110)):
    flag(nm, x, 112)

# ---- trackball + ball light + sleep switch ----
frame(265, 22, 405, 134, "TRACKBALL + SLEEP SWITCH")
j1 = place("gt:J1_Trackball_PS2", "J1", "Trackball PS/2 board", 300, 60)
net(j1["1"], "+5V"); net(j1["2"], "PS2_DATA"); net(j1["3"], "PS2_CLK"); net(j1["4"], "TB_GND")
for k in ("5", "6", "7"):
    nc(j1[k])
d1 = place("Device:LED", "D1", "Ball light (RGB string)", 360, 45)
net(d1["2"], "+5V"); net(d1["1"], "TB_GND")
q1 = place("Device:Q_NMOS", "Q1", "2x D4184 (XY-MOS module)", 355, 100)
qp = {p["name"]: p for k, p in q1.items() if not k.startswith("name:")}
net(qp["D"], "TB_GND"); net(qp["S"], "GND")
r3 = place("Device:R", "R3", "1k", 330, 100, 90)
near, far = sorted((r3["1"], r3["2"]), key=lambda q: abs(q["x"] - qp["G"]["x"]))
wire(near["x"], near["y"], qp["G"]["x"], qp["G"]["y"])
net(far, "TB_EN")
r4 = place("Device:R", "R4", "100k", 345, 108)
wire(r4["1"]["x"], r4["1"]["y"], r4["1"]["x"], qp["G"]["y"])
items.append(["junction", ["at", f"{r4['1']['x']:.2f}", f"{qp['G']['y']:.2f}"], ["diameter", "0"],
              ["color", "0", "0", "0", "0"], ["uuid", U()]])
net(r4["2"], "GND")
text("Q1 = MOSFET module: OUT- (drain) is the trackball's switched ground TB_GND.", 270, 126, 1.5)
text("TB_EN high = trackball on; low in sleep. R3/R4 are on the module; VIN+/OUT+ just pass +5V.", 270, 129.5, 1.5)

# ---- buttons ----
frame(18, 132, 150, 275, "BUTTONS (JZT-08 LIT BUTTONS, 3-PIN XH)")
for i, (sw, gpnet) in enumerate((("LEFT", "BTN_LEFT"), ("RIGHT", "BTN_RIGHT"), ("MENU", "BTN_MENU"))):
    y = 155 + i * 40
    s = place("Switch:SW_Push", f"SW{i + 1}", f"{sw} switch", 50, y)
    net(s["1"], "BTN_COM"); net(s["2"], gpnet)
    d = place("Device:LED", f"D{i + 2}", f"{sw} LED", 95, y, 180)
    r = place("Device:R", f"R{i + 5}", "330", 120, y, 90)
    net(d["2"], "BTN_COM"); wire(d["1"]["x"], d["1"]["y"], r["1"]["x"], r["1"]["y"]); net(r["2"], "GND")
    text(f"SW{i + 1} plug: pin 1 = LED-,  pin 2 = switch -> {gpnet},  pin 3 = LED+/COM -> BTN_COM", 22, y + 13, 1.4)
text("BTN_COM (GP7) is driven HIGH to light the LEDs and pulsed LOW for 20 us to read", 22, 268, 1.5)
text("the switches on GP4/5/6 (internal pull-ups, active low).", 22, 271.5, 1.5)

# ---- display ----
frame(265, 140, 405, 230, "E-PAPER DISPLAY")
ds1 = place("gt:DS1_EPaper_HAT", "DS1", "Waveshare 2.13in e-Paper HAT V4", 340, 180)
for k, nm in (("1", "+3V3"), ("2", "GND"), ("3", "EPD_DIN"), ("4", "EPD_CLK"), ("5", "EPD_CS"), ("6", "EPD_DC"),
              ("7", "EPD_RST"), ("8", "EPD_BUSY")):
    net(ds1[k], nm)
text("3.3 V only. 8-pin JST lead.", 270, 222, 1.5)

# ---- notes ----
text("GT TRACKBALL - SCHEMATIC.  Net labels with the same name are connected.", 170, 248, 2.0, True)
text("Wiring harness (wire colours, lengths, plugs): harness/gt-trackball.svg", 170, 253, 1.6)

# ======================= write =======================
today = datetime.date.today().isoformat()
sch = ["kicad_sch", ["version", "20250114"], ["generator", Q("eeschema")], ["generator_version", Q("9.0")],
       ["uuid", Q(ROOT_UUID)], ["paper", Q("A3")],
       ["title_block", ["title", Q("GT Trackball")], ["date", Q(today)], ["rev", Q("A")],
        ["company", Q("github.com/growthlayer/gt-trackball")], ["comment", "1", Q("Wireless 3in arcade trackball, Pico 2 W")],
        ["comment", "2", Q("Licence: CC BY-SA 4.0")]],
       ["lib_symbols"] + list(lib_used.values())] + items + [
       ["sheet_instances", ["path", Q("/"), ["page", Q("1")]]]]
os.makedirs(OUTDIR, exist_ok=True)
path = os.path.join(OUTDIR, PROJECT + ".kicad_sch")
open(path, "w", encoding="utf-8", newline="\n").write(dump(sch) + "\n")
pro = os.path.join(OUTDIR, PROJECT + ".kicad_pro")
if not os.path.exists(pro):
    open(pro, "w", encoding="utf-8").write('{"meta": {"filename": "%s.kicad_pro", "version": 1}}\n' % PROJECT)
print("wrote", os.path.relpath(path, ROOT))

# project library with the module symbols + a table that points at it and KiCad's stock libraries
lib = ["kicad_symbol_lib", ["version", "20241209"], ["generator", Q("gt_trackball")], ["generator_version", Q("1.0")]] \
      + [parse(dump(v)) for v in CUSTOM.values()]
open(os.path.join(OUTDIR, "gt.kicad_sym"), "w", encoding="utf-8", newline="\n").write(dump(lib) + "\n")
rows = ['  (lib (name "gt")(type "KiCad")(uri "${KIPRJMOD}/gt.kicad_sym")(options "")(descr "GT Trackball modules"))']
for nm in sorted({k.split(":")[0] for k in lib_used} - {"gt"}):
    rows.append(f'  (lib (name "{nm}")(type "KiCad")(uri "${{KICAD10_SYMBOL_DIR}}/{nm}.kicad_sym")(options "")(descr ""))')
open(os.path.join(OUTDIR, "sym-lib-table"), "w", encoding="utf-8", newline="\n").write(
    "(sym_lib_table\n  (version 7)\n" + "\n".join(rows) + "\n)\n")
print("wrote kicad/gt.kicad_sym, kicad/sym-lib-table")
