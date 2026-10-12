# ============================================================
#  Product renders for the README / MakerWorld (Blender 4.2+ / 5.x),
#  using the dimension-accurate component models in components.py.
#
#  Inputs (from the repo root):
#    openscad -o renders/build/shell.stl -D 'part="shell"'  trackball_bt_case.scad
#    openscad -o renders/build/plate.stl -D 'part="bottom"' trackball_bt_case.scad
#    renders/build/screen.png   e-paper screen image (250 x 122 aspect)
#  Render:
#    blender -b -P renders/render.py -- <repo root> <samples> <shots>
#  shots: comma list of hero,top,rear,exploded,cutaway,layout,thumbs (default all)
#  Writes images/*.png; exploded also writes renders/build/callouts.json
#  (pixel positions of each numbered part, for annotate.py).
# ============================================================
import bpy, math, os, sys, json
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = argv[0] if argv else os.getcwd()
SAMPLES = int(argv[1]) if len(argv) > 1 else 192
SHOTS = (argv[2] if len(argv) > 2 else "hero,top,rear,exploded,cutaway,layout,thumbs").split(",")
sys.path.insert(0, os.path.join(ROOT, "renders"))
import components as C

BUILD = os.path.join(ROOT, "renders", "build")
OUT = os.path.join(ROOT, "images")
MM = C.MM

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render settings ----------
scene.render.engine = "CYCLES"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
vt = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
scene.view_settings.view_transform = "AgX" if "AgX" in vt else "Filmic"
for attr in dir(scene.render):                 # no date / path stamps in the PNGs
    if attr.startswith("use_stamp"):
        try:
            setattr(scene.render, attr, False)
        except Exception:
            pass
try:
    cp = bpy.context.preferences.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            cp.compute_device_type = t; cp.get_devices()
            if any(d.type == t for d in cp.devices):
                break
        except Exception:
            pass
    for d in cp.devices:
        d.use = True
    scene.cycles.device = "GPU"
except Exception as e:
    print("GPU setup failed, using CPU:", e)

# ---------- scene ----------
groups, mt = C.build_all(os.path.join(BUILD, "shell.stl"), os.path.join(BUILD, "plate.stl"),
                         os.path.join(BUILD, "screen.png"))

floor_m = C.mat("Floor", (0.78, 0.78, 0.8), 0.45)
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -3.5 * MM))
floor = bpy.context.object; floor.data.materials.append(floor_m)
floor.is_shadow_catcher = True                  # transparent film + shadows only:
scene.render.film_transparent = True            # composited onto the page colour later

def area(name, loc, rot, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    l = bpy.context.object; l.name = name
    l.data.size = size; l.data.energy = energy; l.data.color = color
    return l

lights = [area("key", (-0.55, -0.55, 0.75), (math.radians(45), 0, math.radians(-40)), 0.9, 45),
          area("fill", (0.7, -0.35, 0.35), (math.radians(65), 0, math.radians(60)), 1.2, 14, (0.92, 0.95, 1.0)),
          area("rim", (0.15, 0.75, 0.55), (math.radians(-55), 0, math.radians(170)), 0.6, 35)]
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.82, 0.83, 0.86, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12

target = bpy.data.objects.new("target", None); scene.collection.objects.link(target)

def descendants(ob):
    out = []
    for c in ob.children:
        out.append(c); out += descendants(c)
    return out

def show(keys):
    for k, g in groups.items():
        for c in descendants(g):
            c.hide_render = k not in keys

def reset_layout():
    for g in groups.values():
        g.location = (0, 0, 0)
    shell = bpy.data.objects["Top shell"]
    for m in list(shell.modifiers):
        shell.modifiers.remove(m)

def camera(name, loc, tgt, lens=55, res=(1920, 1280)):
    target.location = tgt
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_start = 0.001
    cam = bpy.data.objects.new(name, cd); scene.collection.objects.link(cam)
    cam.location = loc
    tc = cam.constraints.new("TRACK_TO"); tc.target = target
    tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = res
    return cam

def render(name):
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("wrote", scene.render.filepath)

ALL = set(groups) - {"wires"}

# ---------- assembled shots ----------
if "hero" in SHOTS:
    reset_layout(); show(ALL); floor.location.z = -3.5 * MM
    camera("hero", (0.27, -0.37, 0.40), (0.0, 0.035, 0.04), lens=46); render("hero")
if "top" in SHOTS:
    reset_layout(); show(ALL)
    camera("top", (0.0, 0.03, 0.62), (0.0, 0.03, 0.0), lens=60, res=(1600, 1600)); render("render_top")
if "rear" in SHOTS:
    reset_layout(); show(ALL)
    camera("rear", (-0.36, 0.52, 0.26), (0.0, 0.04, 0.03)); render("render_rear")

# ---------- cutaway: right half of the shell removed ----------
if "cutaway" in SHOTS:
    reset_layout(); show(ALL | {"wires"})
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.07, 0.035, 0.06))
    cutter = bpy.context.object; cutter.scale = (0.136, 0.30, 0.12); cutter.hide_render = True
    cutter.display_type = "WIRE"
    shell = bpy.data.objects["Top shell"]
    bm = shell.modifiers.new("cutaway", "BOOLEAN"); bm.object = cutter; bm.operation = "DIFFERENCE"
    camera("cutaway", (0.48, 0.02, 0.36), (0.0, 0.06, 0.035), lens=42); render("cutaway")
    shell.modifiers.remove(bm)

# ---------- exploded view ----------
if "exploded" in SHOTS:
    reset_layout(); show(ALL)
    offs = {"trackball": (0, 0, 100), "epaper": (0, 0, 205), "shell": (0, 0, 290),
            "usb": (0, 45, 290), "buttons": (0, 0, 385)}
    for k, o in offs.items():
        groups[k].location = tuple(v * MM for v in o)
    floor.location.z = -14 * MM
    cam = camera("exploded", (-0.40, 0.60, 0.58), (0.0, 0.045, 0.20), lens=50, res=(1400, 1900))
    anchors = {                                     # part number -> point on it (mm, before offset)
        1: ("buttons", (-53.4, 90.5, 80)), 2: ("shell", (-99, 40, 50)), 3: ("usb", (26.7, 149, 36)),
        4: ("epaper", (0, 123.25, 67)), 5: ("trackball", (60, -40, 40)), 6: ("plate", (-60, -40, 2)),
        7: ("battery", (0, 95, 14)), 8: ("pico", (-10, 130, 21)), 9: ("charger", (-79.5, 107, 8)),
        10: ("sensor", (-84, 75, 6)), 11: ("mosfet", (80.5, 107, 13)), 12: ("plate", (-92.5, 138.5, 0)),
    }
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    W, Hh = scene.render.resolution_x, scene.render.resolution_y
    pts = {}
    for n, (k, p) in anchors.items():
        w = Vector(p) * MM + groups[k].location
        v = world_to_camera_view(scene, cam, w)
        pts[n] = (round(v.x * W), round((1 - v.y) * Hh))
    os.makedirs(BUILD, exist_ok=True)
    json.dump(pts, open(os.path.join(BUILD, "callouts.json"), "w"))
    render("exploded_raw")
    reset_layout(); floor.location.z = -3.5 * MM

# ---------- layout: looking down into the bottom half (shell, buttons and screen lifted off) ----------
if "layout" in SHOTS:
    reset_layout(); show(ALL - {"shell", "buttons", "epaper"})
    floor.location.z = -3.5 * MM
    cam = camera("layout", (0.0, 0.035, 0.66), (0.0, 0.035, 0.0), lens=58, res=(1500, 1700))
    anchors = {3: ("usb", (26.7, 150, 52)), 5: ("trackball", (0, -20, 70)), 6: ("plate", (-62, -45, 4)),
               7: ("battery", (0, 95, 10)), 8: ("pico", (-8, 130, 13)), 9: ("charger", (-79.5, 107, 5)),
               10: ("sensor", (-84, 70, 12)), 11: ("mosfet", (80.5, 107, 12)), 12: ("plate", (-92.5, 138.5, 4))}
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    W, Hh = scene.render.resolution_x, scene.render.resolution_y
    pts = {n: [round(c) for c in (lambda v: (v.x * W, (1 - v.y) * Hh))(
        world_to_camera_view(scene, cam, Vector(p) * MM + groups[k].location))] for n, (k, p) in anchors.items()}
    os.makedirs(BUILD, exist_ok=True)
    json.dump(pts, open(os.path.join(BUILD, "layout_callouts.json"), "w"))
    render("layout_raw")

# ---------- one render per component ----------
if "thumbs" in SHOTS:
    reset_layout()
    items = [("trackball", "part_trackball"), ("pico", "part_pico"), ("epaper", "part_epaper"),
             ("charger", "part_charger"), ("mosfet", "part_mosfet"), ("sensor", "part_sensor"),
             ("battery", "part_battery"), ("buttons", "part_buttons"), ("usb", "part_usb"),
             ("shell", "part_shell"), ("plate", "part_plate")]
    for key, fname in items:
        show({key})
        g = groups[key]
        if key == "pico":                             # show the component side, not the pin side
            g.rotation_euler = (math.radians(180), 0, 0); g.location = (0, 0, 2 * (C.PICO_Z + 0.5) * MM)
        else:
            g.rotation_euler = (0, 0, 0); g.location = (0, 0, 0)
        obs = [o for o in descendants(groups[key]) if o.type in ("MESH", "CURVE", "FONT")]
        bpy.context.view_layer.update()
        corners = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
        lo = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
        hi = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
        ctr = (lo + hi) / 2; rad = (hi - lo).length / 2
        floor.location.z = lo.z - 0.05 * MM
        d = Vector((0.85, -1.1, 0.95)).normalized()
        lens = 70; fov = 2 * math.atan(36 / 2 / lens)
        dist = rad / math.sin(fov / 2) * 1.08
        camera("thumb_" + key, tuple(ctr + d * dist), tuple(ctr), lens=lens, res=(1000, 1000))
        render(fname)
    floor.location.z = -3.5 * MM
