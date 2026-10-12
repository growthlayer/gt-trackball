# ============================================================
#  Blender models of every GT Trackball component, to real dimensions,
#  placed where trackball_bt_case.scad puts them (case frame, mm:
#  x = right, y = toward the rear, z = up, bottom plate at z = 0).
#
#  Each part is a group (an Empty with children) so it can be moved for
#  the exploded view or rendered on its own. Used by renders/render.py.
# ============================================================
import bpy, math, os
from mathutils import Vector

MM = 0.001

# ---- case geometry (trackball_bt_case.scad) ----
PLATE_T = 3.7
H, TOP_T = 72.1, 4.5
CEIL = H - TOP_T                       # deck underside, 67.6
INNER_RY = 143.5
WALL = 3.0
BUTTONS = [(-53.4, 90.5), (0.0, 90.5), (53.4, 90.5)]
EPD = (0.0, 123.25)
PICO = (0.0, 130.0)
PICO_Z = PLATE_T + 8.0                  # PCB rests on 8 mm standoffs
CHG = (-79.5, 107.0)
FET = (80.5, 107.0)
SENSOR = (-84.0, 75.0)
BAT = (0.0, 95.0)
CRADLE = 2.5                            # boards snap into cradles this far above the plate
USB = (26.7, 36.0)                      # x, z on the rear wall
PILLARS = [(-92.5, -70.5), (92.5, -70.5), (-92.5, 138.5), (92.5, 138.5)]
FEET = [(-77.5, -55.5), (77.5, -55.5), (-77.5, 123.5), (77.5, 123.5)]
BALL_Z = CEIL - 10.0                    # ball centre; top 23.6 mm above the deck

# ---------- materials ----------
_mats = {}
def mat(name, color, rough=0.5, metal=0.0, **kw):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in kw.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    _mats[name] = m
    return m

def M():
    return dict(
        pla=mat("Printed PLA", (0.008, 0.008, 0.009), 0.72, **{"Specular IOR Level": 0.25}),
        pcb_g=mat("PCB green", (0.02, 0.22, 0.07), 0.35),
        pcb_k=mat("PCB black", (0.012, 0.012, 0.014), 0.35),
        pcb_b=mat("PCB blue", (0.02, 0.09, 0.35), 0.35),
        pcb_r=mat("PCB red", (0.45, 0.02, 0.02), 0.35),
        chip=mat("IC black", (0.015, 0.015, 0.016), 0.45),
        silver=mat("Tin", (0.80, 0.80, 0.82), 0.25, 1.0),
        gold=mat("Gold", (0.95, 0.70, 0.30), 0.25, 1.0),
        brass=mat("Brass", (0.85, 0.62, 0.28), 0.3, 1.0),
        steel=mat("Steel", (0.55, 0.56, 0.58), 0.35, 1.0),
        plastic_k=mat("Plastic black", (0.02, 0.02, 0.022), 0.45),
        plastic_w=mat("Plastic white", (0.85, 0.85, 0.82), 0.4),
        term_b=mat("Terminal blue", (0.05, 0.25, 0.75), 0.4),
        term_g=mat("Terminal green", (0.05, 0.45, 0.12), 0.4),
        trim=mat("Trimpot blue", (0.05, 0.25, 0.85), 0.3),
        foil=mat("LiPo foil", (0.78, 0.79, 0.80), 0.18, 0.9),
        kapton=mat("Kapton", (0.90, 0.55, 0.05), 0.3, 0.0, **{"Transmission Weight": 0.3}),
        wire_r=mat("Wire red", (0.70, 0.03, 0.03), 0.5),
        wire_k=mat("Wire black", (0.02, 0.02, 0.02), 0.5),
        wire_y=mat("Wire yellow", (0.85, 0.65, 0.02), 0.5),
        wire_bl=mat("Wire blue", (0.03, 0.18, 0.75), 0.5),
        wire_gr=mat("Wire green", (0.03, 0.5, 0.15), 0.5),
        wire_pu=mat("Wire purple", (0.4, 0.08, 0.6), 0.5),
        wire_br=mat("Wire brown", (0.35, 0.18, 0.06), 0.5),
        wire_w=mat("Wire white", (0.85, 0.85, 0.85), 0.5),
        housing=mat("Trackball housing", (0.014, 0.014, 0.016), 0.55),
        rubber=mat("Rubber", (0.03, 0.03, 0.03), 0.85),
        ring=mat("Black ring", (0.01, 0.01, 0.01), 0.35),
        ball=mat("Trackball", (0.92, 0.92, 0.95), 0.12, 0.0, **{"Subsurface Weight": 0.35,
                 "Subsurface Radius": (0.02, 0.02, 0.03), "Coat Weight": 0.6,
                 "Emission Color": (0.55, 0.22, 1.0, 1), "Emission Strength": 0.8}),
        clear=mat("Clear acrylic", (0.95, 0.95, 0.97), 0.05, 0.0, **{"Transmission Weight": 0.95, "IOR": 1.49}),
        cap=mat("Button cap", (0.95, 0.95, 0.95), 0.25, 0.0, **{"Emission Color": (1, 1, 1, 1), "Emission Strength": 0.25}),
        glass=mat("E-paper glass", (0.82, 0.82, 0.78), 0.55),
        silk=mat("Silkscreen", (0.95, 0.95, 0.95), 0.5),
        led=mat("LED", (0.9, 0.1, 0.1), 0.2, 0.0, **{"Emission Color": (1, 0.1, 0.1, 1), "Emission Strength": 2.0}),
        slot=mat("USB slot", (0.03, 0.03, 0.04), 0.5),
        fpc=mat("FPC", (0.85, 0.55, 0.12), 0.35),
    )

# ---------- primitives (sizes and positions in mm) ----------
def _finish(ob, m, parent, name, bevel):
    if name:
        ob.name = name
    if m:
        ob.data.materials.append(m)
    if bevel:
        bv = ob.modifiers.new("bevel", "BEVEL")
        bv.width = bevel * MM; bv.segments = 2; bv.limit_method = "ANGLE"
    if parent:
        ob.parent = parent
    return ob

def box(size, loc, m, bevel=0.0, rot=(0, 0, 0), parent=None, name=""):
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(v * MM for v in loc),
                                    rotation=tuple(math.radians(r) for r in rot))
    ob = bpy.context.object
    ob.scale = tuple(v * MM for v in size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(ob, m, parent, name, bevel)

def cyl(d, h, loc, m, rot=(0, 0, 0), verts=48, parent=None, name="", bevel=0.0, d2=None):
    if d2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=d / 2 * MM, depth=h * MM,
                                            location=tuple(v * MM for v in loc),
                                            rotation=tuple(math.radians(r) for r in rot))
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=d / 2 * MM, radius2=d2 / 2 * MM,
                                        depth=h * MM, location=tuple(v * MM for v in loc),
                                        rotation=tuple(math.radians(r) for r in rot))
    ob = bpy.context.object
    bpy.ops.object.shade_smooth()
    return _finish(ob, m, parent, name, bevel)

def text(s, size, loc, m, rot=(0, 0, 0), parent=None, align="CENTER"):
    bpy.ops.object.text_add(location=tuple(v * MM for v in loc),
                            rotation=tuple(math.radians(r) for r in rot))
    ob = bpy.context.object
    ob.data.body = s; ob.data.size = size * MM; ob.data.align_x = align; ob.data.align_y = "CENTER"
    ob.data.extrude = 0.02 * MM
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob

def wire(points, m, d=1.6, parent=None):
    cu = bpy.data.curves.new("wire", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = d / 2 * MM; cu.bevel_resolution = 3
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = Vector(p) * MM
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new("wire", cu); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob

def group(name):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    return e

# ---------- components ----------
def raspberry_pico(mt, g):
    """Pico 2 W, mounted UPSIDE DOWN: components face the plate, headers up."""
    x0, y0 = PICO; z = PICO_Z           # PCB underside (now the component side) rests here
    t = 1.0
    pcb = box((51, 21, t), (x0, y0, z + t / 2), mt["pcb_g"], 0.3, parent=g, name="Pico PCB")
    # castellated pads + headers: 20 per side, 2.54 pitch, rows 17.78 apart
    for side in (-1, 1):
        yr = y0 + side * 8.89
        box((50.8, 2.5, 2.5), (x0, yr, z + t + 1.25), mt["plastic_k"], 0.2, parent=g)     # header plastic (top)
        for i in range(20):
            xp = x0 - 24.13 + i * 2.54
            box((0.64, 0.64, 6.0), (xp, yr, z + t + 2.5 + 3.0), mt["gold"], parent=g)        # long pins, up
            box((0.64, 0.64, 2.0), (xp, yr, z - 1.0), mt["gold"], parent=g)                  # short tails, down
            cyl(1.6, 0.05, (xp, yr, z + t + 0.03), mt["gold"], parent=g)
    # components hang below the PCB
    box((7.0, 7.0, 0.9), (x0 + 2.0, y0, z - 0.45), mt["chip"], 0.1, parent=g, name="RP2350")
    box((11.0, 11.0, 1.4), (x0 - 12.0, y0, z - 0.7), mt["silver"], 0.2, parent=g, name="CYW43439 shield")
    box((7.5, 5.6, 2.6), (x0 + 24.3, y0, z - 1.3), mt["silver"], 0.2, parent=g, name="micro-USB")
    box((3.5, 4.5, 1.6), (x0 + 15.5, y0 - 4.0, z - 0.8), mt["plastic_w"], 0.2, parent=g, name="BOOTSEL")
    box((5.0, 6.0, 1.0), (x0 + 9.0, y0 + 3.5, z - 0.5), mt["chip"], 0.1, parent=g, name="flash")
    box((2.0, 1.2, 0.6), (x0 + 19.0, y0 + 5.5, z - 0.3), mt["led"], parent=g)
    text("Pico 2 W", 2.4, (x0 - 4, y0 + 4.0, z + t + 0.01), mt["silk"], parent=g)
    return g

def epaper(mt, g, clips=True):
    """Waveshare 2.13" e-Paper HAT V4, face up against the deck underside."""
    x0, y0 = EPD
    ztop = CEIL
    box((59.2, 29.2, 1.1), (x0 - 1.5, y0, ztop - 0.55), mt["glass"], 0.2, parent=g, name="E-paper panel")
    # active area texture is applied by render.py (object "E-paper screen")
    box((65.0, 30.5, 1.6), (x0, y0, ztop - 1.1 - 0.8), mt["pcb_k"], 0.3, parent=g, name="HAT PCB")
    box((12.0, 18.0, 0.15), (x0 + 27.0, y0, ztop - 1.0), mt["fpc"], parent=g, name="FPC")
    # 8-pin JST PH on the rear (harness) edge, under the PCB
    box((18.0, 4.5, 5.5), (x0 - 10.0, y0 + 12.5, ztop - 2.7 - 2.75), mt["plastic_w"], 0.2, parent=g, name="JST")
    box((2.0, 2.0, 1.5), (x0 + 20.0, y0 - 10.0, ztop - 3.4), mt["chip"], parent=g)
    for sx in (-1, 1):                                   # mounting holes
        cyl(3.0, 0.1, (x0 + sx * 29.5, y0 - 12.0, ztop - 2.66), mt["gold"], parent=g)
    if clips:
        for sx in (-1, 1):
            cx = x0 + sx * (65.0 / 2 + 4)
            c = box((24.0, 8.5, 2.5), (cx - sx * 6, y0, ztop - 2.7 - 1.25), mt["pla"], 1.2, parent=g, name="Clip")
            cyl(5.0, 1.6, (cx + sx * 3, y0, ztop - 2.7 - 2.5 - 0.8), mt["steel"], parent=g)
    return g

def charger(mt, g):
    """TP4056-type charger + adjustable boost, 24 x 19, USB-C toward the battery (+x)."""
    x0, y0 = CHG; z = PLATE_T + CRADLE
    box((24, 19, 1.2), (x0, y0, z + 0.6), mt["pcb_k"], 0.2, parent=g, name="Charger PCB")
    box((7.3, 8.9, 3.2), (x0 + 9.5, y0 + 3.0, z + 1.2 + 1.6), mt["silver"], 0.4, parent=g, name="USB-C")
    box((6.0, 6.0, 4.5), (x0 - 6.0, y0 + 3.0, z + 1.2 + 2.25), mt["chip"], 0.8, parent=g, name="Inductor")
    text("100", 2.2, (x0 - 6.0, y0 + 3.0, z + 1.2 + 4.51), mt["silk"], rot=(0, 0, 90), parent=g)
    box((5.0, 4.0, 1.5), (x0 + 1.5, y0 - 4.0, z + 1.2 + 0.75), mt["chip"], 0.1, parent=g, name="TP4056")
    box((3.4, 3.4, 2.0), (x0 + 1.0, y0 + 3.5, z + 1.2 + 1.0), mt["trim"], 0.2, parent=g, name="Trimpot")
    cyl(1.6, 0.4, (x0 + 1.0, y0 + 3.5, z + 1.2 + 2.2), mt["plastic_w"], parent=g)
    for i, (px, py, lab) in enumerate([(-9, -7, "B-"), (-4, -7, "B+"), (5, -7, "-"), (9.5, -7, "+")]):
        box((2.8, 2.8, 0.06), (x0 + px, y0 + py, z + 1.23), mt["gold"], parent=g)
    box((1.6, 0.8, 0.5), (x0 + 4.0, y0 + 7.5, z + 1.45), mt["led"], parent=g)
    return g

def mosfet(mt, g):
    """XY-MOS dual D4184 trigger module (34 x 17) in its right-rear cradle."""
    x0, y0 = FET; z = PLATE_T + CRADLE
    box((17, 34, 1.6), (x0, y0, z + 0.8), mt["pcb_b"], 0.2, parent=g, name="MOSFET PCB")
    for dy in (-3.5, 3.5):
        box((6.6, 6.1, 2.3), (x0 + 2.5, y0 + dy, z + 1.6 + 1.15), mt["chip"], 0.2, parent=g, name="D4184")
        box((5.2, 1.2, 0.3), (x0 - 1.6, y0 + dy, z + 1.75), mt["silver"], parent=g)
    for sy in (-1, 1):
        box((10.0, 7.5, 9.0), (x0, y0 + sy * 13.25, z + 1.6 + 4.5), mt["term_b"], 0.4, parent=g, name="Terminal")
        for dx in (-2.5, 2.5):
            cyl(3.0, 0.6, (x0 + dx, y0 + sy * 13.25, z + 1.6 + 9.3), mt["steel"], parent=g)
    return g

def sensor(mt, g):
    """0-25 V voltage sensor (30 k / 7.5 k divider)."""
    x0, y0 = SENSOR; z = PLATE_T + CRADLE
    box((13.5, 27, 1.6), (x0, y0, z + 0.8), mt["pcb_r"], 0.2, parent=g, name="Sensor PCB")
    box((10.0, 7.5, 9.0), (x0, y0 + 8.5, z + 1.6 + 4.5), mt["term_g"], 0.4, parent=g, name="Terminal")
    for dx in (-2.5, 2.5):
        cyl(3.0, 0.6, (x0 + dx, y0 + 8.5, z + 1.6 + 9.3), mt["steel"], parent=g)
    box((7.6, 2.5, 2.5), (x0, y0 - 10.5, z + 1.6 + 1.25), mt["plastic_k"], 0.2, parent=g)
    for dx in (-2.54, 0, 2.54):
        box((0.64, 0.64, 8.0), (x0 + dx, y0 - 10.5, z + 1.6 + 4.0), mt["gold"], parent=g)
    for dy in (-3, 1):
        box((3.2, 1.6, 0.6), (x0, y0 + dy, z + 1.9), mt["chip"], parent=g)
    return g

def battery(mt, g):
    x0, y0 = BAT; z = PLATE_T
    box((52, 35, 10), (x0, y0, z + 5.0), mt["foil"], 2.0, parent=g, name="LiPo")
    box((6, 33, 10.4), (x0 - 23.5, y0, z + 5.0), mt["kapton"], 1.0, parent=g)
    wire([(x0 - 26, y0 + 4, z + 6), (x0 - 40, y0 + 5, z + 6), (CHG[0] + 3, CHG[1] - 7, z + 3)], mt["wire_r"], 1.4, g)
    wire([(x0 - 26, y0 - 2, z + 6), (x0 - 42, y0 - 1, z + 6), (CHG[0] - 1, CHG[1] - 7, z + 3)], mt["wire_k"], 1.4, g)
    return g

def prism(points, z0, z1, m, parent=None, name="", rot_z=0.0, bevel=0.0):
    """Extrude a 2-D outline (mm, counter-clockwise) from z0 to z1, rotated rot_z deg."""
    c, sn = math.cos(math.radians(rot_z)), math.sin(math.radians(rot_z))
    pts = [((x * c - y * sn) * MM, (x * sn + y * c) * MM) for x, y in points]
    n = len(pts)
    verts = [(x, y, z0 * MM) for x, y in pts] + [(x, y, z1 * MM) for x, y in pts]
    faces = [list(range(n))[::-1], list(range(n, 2 * n))]
    faces += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    me = bpy.data.meshes.new(name or "prism"); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name or "prism", me); bpy.context.scene.collection.objects.link(ob)
    return _finish(ob, m, parent, None, bevel)

def trackball(mt, g):
    """3" illuminated trackball, modelled from the seller's photos.
    In its own frame: square top plate (corners clipped) with a mounting
    boss at each corner of the 80.5 mm square; a boxy body below it; two
    short encoder housings on adjacent sides (+x and -y), each with its
    sensor board on the outer face (J1 on the +x one); copper LED-power
    tabs on the -x side; black ring and frosted lit ball. It sits turned
    45 deg in the case, so the mounting holes are on the case axes."""
    R = 45.0                                            # rotation into the case frame
    c, sn = math.cos(math.radians(R)), math.sin(math.radians(R))
    rot = lambda x, y: (x * c - y * sn, x * sn + y * c)
    top = CEIL                                          # hole surface = deck underside
    # square top plate, corners clipped, 100 x 100 x 4
    s, k = 50.0, 9.0
    plate = [(-s + k, -s), (s - k, -s), (s, -s + k), (s, s - k), (s - k, s), (-s + k, s), (-s, s - k), (-s, -s + k)]
    prism(plate, top - 4.0, top, mt["housing"], g, "Top plate", R, 0.6)
    for hx, hy in ((40.25, 40.25), (-40.25, 40.25), (40.25, -40.25), (-40.25, -40.25)):
        x, y = rot(hx, hy)
        cyl(11.0, 6.0, (x, y, top - 3.0), mt["housing"], parent=g)
        cyl(5.6, 6.2, (x, y, top - 3.0), mt["chip"], parent=g)
    # boxy body under the plate
    zb = PLATE_T + 2.0
    bw = 42.0
    prism([(-bw, -bw), (bw, -bw), (bw, bw), (-bw, bw)], zb, top - 4.0, mt["housing"], g, "Body", R, 1.5)
    # two encoder housings on adjacent sides, sensor boards on their outer faces
    z0, z1 = top - 48.0, top - 6.0
    for side, j1 in (("+x", True), ("-y", False)):
        if side == "+x":
            outline = [(bw - 1, -24), (bw + 13, -24), (bw + 13, 24), (bw - 1, 24)]
            px, py, nx, ny = bw + 14, 0.0, 1.0, 0.0
        else:
            outline = [(-24, -bw - 13), (24, -bw - 13), (24, -bw + 1), (-24, -bw + 1)]
            px, py, nx, ny = 0.0, -bw - 14, 0.0, -1.0
        prism(outline, z0, z1, mt["housing"], g, "Encoder housing", R, 1.0)
        x, y = rot(px, py)
        size = (1.6, 40.0, 30.0) if side == "+x" else (40.0, 1.6, 30.0)
        box(size, (x, y, (z0 + z1) / 2), mt["pcb_g"], 0.2, rot=(0, 0, R), parent=g,
            name="J1 board" if j1 else "Sensor board")
        if j1:
            jx, jy = rot(px + nx * 3.5, py + ny * 3.5)
            box((5.5, 17.5, 6.0), (jx, jy, (z0 + z1) / 2 + 4), mt["plastic_w"], 0.3,
                rot=(0, 0, R), parent=g, name="J1")
    # ring + lip, frosted ball
    cyl(75.5, 4.5, (0, 0, CEIL + 2.25), mt["ring"], parent=g, name="Ring", bevel=0.6)
    cyl(80.0, 1.0, (0, 0, CEIL + 0.5), mt["ring"], parent=g)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=76.2 / 2 * MM,
                                         location=(0, 0, BALL_Z * MM))
    ball = bpy.context.object; ball.name = "Ball"; ball.data.materials.append(mt["ball"])
    bpy.ops.object.shade_smooth(); ball.parent = g
    # copper LED-power tabs with screws on the -x face of the body
    for dy in (-12, 12):
        x, y = rot(-bw - 1.0, dy)
        box((2.0, 10, 8), (x, y, top - 14.0), mt["gold"], 0.2, rot=(0, 0, R), parent=g)
        sx, sy = rot(-bw - 2.2, dy)
        cyl(4.0, 1.0, (sx, sy, top - 14.0), mt["steel"], rot=(0, 90, R), parent=g)
    return g

def button(mt, g, x, y):
    """30 mm lit arcade button: bezel + cap above the deck, nut, body,
    switch/LED board and 3-pin XH harness below."""
    box_z = H
    cyl(33.0, 2.8, (x, y, box_z + 1.4), mt["clear"], parent=g, bevel=0.6)
    cyl(27.5, 3.2, (x, y, box_z + 2.8), mt["clear"], parent=g)
    cyl(23.5, 5.0, (x, y, box_z + 4.8), mt["cap"], parent=g, bevel=1.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=17.0 * MM, depth=5 * MM,
                                        location=(x * MM, y * MM, (CEIL - 2.5) * MM))
    nut = bpy.context.object; nut.data.materials.append(mt["clear"]); nut.parent = g
    cyl(28.0, 22.0, (x, y, CEIL - 11.0), mt["clear"], parent=g)
    box((21, 21, 16), (x, y, CEIL - 22.0 - 8.0), mt["plastic_w"], 0.6, parent=g)      # switch / LED holder
    box((16, 14, 1.2), (x, y, CEIL - 38.6), mt["pcb_g"], 0.2, parent=g)               # JZT-08 board
    box((8, 4.5, 6.0), (x, y - 3, CEIL - 42.2), mt["plastic_w"], 0.3, parent=g)       # XH plug
    return g

def usb_port(mt, g, cable=True):
    x, z = USB; yo = INNER_RY + WALL                      # outer face of the rear wall
    box((26.0, 2.5, 31.0), (x, yo + 1.25, z), mt["plastic_k"], 1.5, parent=g, name="USB flange")
    box((14.5, 1.0, 7.0), (x, yo + 2.6, z), mt["silver"], 0.3, parent=g)
    box((12.2, 1.1, 4.6), (x, yo + 2.7, z + 0.6), mt["slot"], parent=g)
    box((10.5, 1.2, 1.6), (x, yo + 2.7, z - 0.8), mt["plastic_w"], parent=g)
    for sx in (-1, 1):
        cyl(5.6, 0.8, (x + sx * 9.5, yo + 2.6, z - sx * 12.0), mt["steel"], rot=(90, 0, 0), parent=g)
    cyl(23.7, 20.0, (x, yo - 3.0 - 10.0, z), mt["plastic_k"], rot=(90, 0, 0), parent=g, name="USB body")
    if cable:
        # inner micro-USB-to-A cable: A plug in the coupler, micro plug in the Pico
        box((16, 30, 8.5), (x, yo - 3 - 20 - 15, z), mt["plastic_k"], 2.0, parent=g)
        wire([(x, yo - 53, z), (x, yo - 70, z - 6), (PICO[0] + 40, PICO[1] + 4, PICO_Z - 2),
              (PICO[0] + 33, PICO[1], PICO_Z - 1.3)], mt["plastic_k"], 3.5, g)
        box((14, 8, 6.5), (PICO[0] + 32.5, PICO[1], PICO_Z - 1.3), mt["plastic_k"], 1.2, parent=g)
    return g

def shell_hardware(mt, g):
    for x, y in PILLARS:                                  # heat-set inserts
        cyl(5.0, 4.0, (x, y, PLATE_T + 2.0 + 0.2), mt["brass"], parent=g)
    return g

def plate_hardware(mt, g):
    for x, y in PILLARS:                                  # M3 countersunk screws
        cyl(6.0, 1.8, (x, y, 0.9), mt["steel"], d2=3.0, parent=g)
        cyl(3.0, 8.0, (x, y, 4.0), mt["steel"], parent=g)
    for x, y in FEET:
        cyl(12.7, 3.5, (x, y, -1.75 + 1.2), mt["rubber"], parent=g, bevel=1.2)
    return g

def wiring(mt, g):
    """Representative jumper wiring (not every conductor) for the cutaway."""
    zt = PICO_Z + 1.0 + 2.5 + 6.0                         # header pin tips
    def dup(x, y):                                        # Dupont housing on a pin
        box((2.5, 2.5, 14), (x, y, zt - 2 + 7), mt["plastic_k"], 0.2, parent=g)
        return (x, y, zt - 2 + 14)
    px = lambda i: PICO[0] - 24.13 + i * 2.54
    front, rear = PICO[1] - 8.89, PICO[1] + 8.89
    runs = [
        (dup(px(1), front), (EPD[0] - 14, EPD[1] + 12.5, CEIL - 8), "wire_pu"),
        (dup(px(2), front), (EPD[0] - 12, EPD[1] + 12.5, CEIL - 8), "wire_pu"),
        (dup(px(4), front), (EPD[0] - 8, EPD[1] + 12.5, CEIL - 8), "wire_pu"),
        (dup(px(5), front), (EPD[0] - 6, EPD[1] + 12.5, CEIL - 8), "wire_pu"),
        (dup(px(7), front), (BUTTONS[0][0], BUTTONS[0][1] - 3, CEIL - 45), "wire_gr"),
        (dup(px(8), front), (BUTTONS[1][0], BUTTONS[1][1] - 3, CEIL - 45), "wire_gr"),
        (dup(px(10), front), (BUTTONS[2][0], BUTTONS[2][1] - 3, CEIL - 45), "wire_gr"),
        (dup(px(13), front), (44.8, 43.4, CEIL - 20), "wire_bl"),
        (dup(px(14), front), (43.4, 44.8, CEIL - 20), "wire_bl"),
        (dup(px(3), rear), (FET[0], FET[1] - 11.5, PLATE_T + 12), "wire_br"),
        (dup(px(6), rear), (SENSOR[0], SENSOR[1] - 10.5, PLATE_T + 10), "wire_br"),
        (dup(px(18), rear), (CHG[0] + 9, CHG[1] - 7, PLATE_T + 3), "wire_r"),
    ]
    for (a, b, col) in runs:
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, max(a[2], b[2]) + 12)
        wire([a, mid, b], mt[col], 1.3, g)
    # trackball power from the MOSFET module
    wire([(FET[0] - 3, FET[1] - 11.5, PLATE_T + 11), (60, 80, PLATE_T + 30), (45.5, 42.0, CEIL - 25)], mt["wire_r"], 1.3, g)
    wire([(FET[0] + 3, FET[1] - 11.5, PLATE_T + 11), (62, 82, PLATE_T + 28), (42.0, 45.5, CEIL - 25)], mt["wire_k"], 1.3, g)
    return g

# ---------- build everything ----------
def build_all(shell_stl, plate_stl, screen_png):
    mt = M()
    groups = {}
    def imp(path, name, parent):
        if hasattr(bpy.ops.wm, "stl_import"):
            bpy.ops.wm.stl_import(filepath=path)
        else:
            bpy.ops.import_mesh.stl(filepath=path)
        ob = bpy.context.selected_objects[0]
        ob.name = name; ob.scale = (MM, MM, MM)
        ob.data.materials.append(mt["pla"]); ob.parent = parent
        return ob
    groups["plate"] = g = group("plate");    imp(plate_stl, "Bottom plate", g); plate_hardware(mt, g)
    groups["battery"] = battery(mt, group("battery"))
    groups["pico"] = raspberry_pico(mt, group("pico"))
    groups["charger"] = charger(mt, group("charger"))
    groups["mosfet"] = mosfet(mt, group("mosfet"))
    groups["sensor"] = sensor(mt, group("sensor"))
    groups["trackball"] = trackball(mt, group("trackball"))
    groups["epaper"] = g = epaper(mt, group("epaper"))
    # the screen image on the panel's active area
    sm = bpy.data.materials.new("E-paper screen"); sm.use_nodes = True
    b = sm.node_tree.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.55
    tex = sm.node_tree.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(screen_png)
    tex.interpolation = "Closest"
    sm.node_tree.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(EPD[0] * MM, EPD[1] * MM, (CEIL + 0.03) * MM))
    scr = bpy.context.object; scr.name = "E-paper screen"
    scr.scale = (48.6 * MM, 23.7 * MM, 1); scr.data.materials.append(sm); scr.parent = g
    groups["shell"] = g = group("shell");    imp(shell_stl, "Top shell", g); shell_hardware(mt, g)
    groups["buttons"] = g = group("buttons")
    for x, y in BUTTONS:
        button(mt, g, x, y)
    groups["usb"] = usb_port(mt, group("usb"))
    groups["wires"] = wiring(mt, group("wires"))
    return groups, mt
