# ============================================================
#  Product renders for the README / MakerWorld (Blender 4.2+ / 5.x).
#
#  Prepare the inputs (from the repo root):
#    openscad -o renders/build/shell.stl -D 'part="shell"'  trackball_bt_case.scad
#    openscad -o renders/build/plate.stl -D 'part="bottom"' trackball_bt_case.scad
#    renders/build/screen.png  = an e-paper screen image, 250x122 aspect
#  Render:
#    blender -b -P renders/render.py -- <repo root> [samples]
#  Writes images/hero.png, images/render_rear.png, images/render_top.png
# ============================================================
import bpy, math, os, sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = argv[0] if argv else os.getcwd()
SAMPLES = int(argv[1]) if len(argv) > 1 else 192
BUILD = os.path.join(ROOT, "renders", "build")
OUT = os.path.join(ROOT, "images")
MM = 0.001

# key case dimensions (trackball_bt_case.scad)
H, TOP_T = 72.1, 4.5
CEIL_Z = H - TOP_T
BUTTONS = [(-53.4, 90.5), (0, 90.5), (53.4, 90.5)]
EPD = (0.0, 123.25)
USB = (26.7, 146.5, 36.0)          # x, rear wall outer face y, z

scene = bpy.context.scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render settings ----------
scene.render.engine = "CYCLES"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
scene.view_settings.look = "None"
for attr in dir(scene.render):              # no date / path stamps in the PNGs
    if attr.startswith("use_stamp"):
        try:
            setattr(scene.render, attr, False)
        except Exception:
            pass
try:
    cp = bpy.context.preferences.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            cp.compute_device_type = t
            cp.get_devices()
            if any(d.type == t for d in cp.devices):
                break
        except Exception:
            pass
    for d in cp.devices:
        d.use = True
    scene.cycles.device = "GPU"
    print("render device:", cp.compute_device_type)
except Exception as e:
    print("GPU setup failed, using CPU:", e)

# ---------- materials ----------
def principled(name, **inputs):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    for k, v in inputs.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    return m, b

def textured(m, b, scale=900.0, strength=0.12):
    """fine matte print texture via a bump map"""
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = strength
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])

shell_m, sb = principled("Printed PLA", **{"Base Color": (0.008, 0.008, 0.009, 1), "Roughness": 0.72, "Specular IOR Level": 0.25})
textured(shell_m, sb)
ring_m, _ = principled("Black ring", **{"Base Color": (0.01, 0.01, 0.01, 1), "Roughness": 0.35})
ball_m, _ = principled("Trackball", **{"Base Color": (0.92, 0.92, 0.95, 1), "Roughness": 0.12,
    "Subsurface Weight": 0.35, "Subsurface Radius": (0.02, 0.02, 0.03), "Coat Weight": 0.6,
    "Emission Color": (0.55, 0.22, 1.0, 1), "Emission Strength": 0.8})
bezel_m, _ = principled("Button bezel", **{"Base Color": (0.95, 0.95, 0.97, 1), "Roughness": 0.05,
    "Transmission Weight": 0.95, "IOR": 1.49})
cap_m, _ = principled("Button cap", **{"Base Color": (0.95, 0.95, 0.95, 1), "Roughness": 0.25,
    "Emission Color": (1, 1, 1, 1), "Emission Strength": 0.25})
metal_m, _ = principled("USB metal", **{"Base Color": (0.75, 0.75, 0.78, 1), "Metallic": 1.0, "Roughness": 0.25})
slot_m, _ = principled("USB slot", **{"Base Color": (0.03, 0.03, 0.04, 1), "Roughness": 0.5})
floor_m, _ = principled("Floor", **{"Base Color": (0.78, 0.78, 0.8, 1), "Roughness": 0.45})

screen_m = bpy.data.materials.new("E-paper")
screen_m.use_nodes = True
nt = screen_m.node_tree
sbsdf = nt.nodes["Principled BSDF"]
sbsdf.inputs["Roughness"].default_value = 0.55
img = nt.nodes.new("ShaderNodeTexImage")
img.image = bpy.data.images.load(os.path.join(BUILD, "screen.png"))
img.interpolation = "Closest"
nt.links.new(img.outputs["Color"], sbsdf.inputs["Base Color"])

# ---------- geometry ----------
def import_stl(name, mat):
    path = os.path.join(BUILD, name)
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=path)
    else:
        bpy.ops.import_mesh.stl(filepath=path)
    ob = bpy.context.selected_objects[0]
    ob.scale = (MM, MM, MM)
    ob.data.materials.clear(); ob.data.materials.append(mat)
    bpy.ops.object.shade_auto_smooth() if hasattr(bpy.ops.object, "shade_auto_smooth") else None
    return ob

def cyl(d, h, loc, mat, verts=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=d / 2 * MM, depth=h * MM,
                                        location=tuple(v * MM for v in loc))
    ob = bpy.context.object; ob.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return ob

import_stl("shell.stl", shell_m)
import_stl("plate.stl", shell_m)

# trackball: ball + black ring flush with the deck
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=76.2 / 2 * MM,
                                     location=(0, 0, (CEIL_Z - 10) * MM))
ball = bpy.context.object; ball.data.materials.append(ball_m); bpy.ops.object.shade_smooth()
cyl(75.4, 2.0, (0, 0, H - 1.2), ring_m)

# buttons: clear bezel + lit white cap
for x, y in BUTTONS:
    cyl(33, 2.6, (x, y, H + 1.3), bezel_m)
    cyl(27.5, 3.0, (x, y, H + 2.6), bezel_m)
    cyl(23.5, 5.0, (x, y, H + 4.6), cap_m)

# e-paper behind the deck window
bpy.ops.mesh.primitive_plane_add(size=1, location=(EPD[0] * MM, EPD[1] * MM, (CEIL_Z + 0.05) * MM))
scr = bpy.context.object
scr.scale = (48.6 * MM, 23.7 * MM, 1)
scr.data.materials.append(screen_m)

# USB-A feedthrough on the rear wall
ux, uy, uz = USB
body = cyl(23.7, 3.0, (0, 0, 0), metal_m)
body.rotation_euler = (math.radians(90), 0, 0)
body.location = (ux * MM, (uy + 1.5) * MM, uz * MM)
bpy.ops.mesh.primitive_cube_add(size=1, location=(ux * MM, (uy + 3.05) * MM, uz * MM))
slot = bpy.context.object; slot.scale = (12.5 * MM, 0.2 * MM, 5.0 * MM); slot.data.materials.append(slot_m)

# floor
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -3.5 * MM))
bpy.context.object.data.materials.append(floor_m)

# ---------- lights + world ----------
def area(name, loc, rot, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    l = bpy.context.object; l.name = name
    l.data.size = size; l.data.energy = energy; l.data.color = color
    return l

area("key", (-0.55, -0.55, 0.75), (math.radians(45), 0, math.radians(-40)), 0.9, 45)
area("fill", (0.7, -0.35, 0.35), (math.radians(65), 0, math.radians(60)), 1.2, 14, (0.92, 0.95, 1.0))
area("rim", (0.15, 0.75, 0.55), (math.radians(-55), 0, math.radians(170)), 0.6, 35)
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.82, 0.83, 0.86, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12

# ---------- cameras + renders ----------
target_ob = bpy.data.objects.new("target", None); scene.collection.objects.link(target_ob)

def shot(name, cam_loc, target, lens=55, res=(1920, 1280)):
    target_ob.location = target
    cam_data = bpy.data.cameras.new(name); cam_data.lens = lens
    cam = bpy.data.objects.new(name, cam_data); scene.collection.objects.link(cam)
    cam.location = cam_loc
    c = cam.constraints.new("TRACK_TO"); c.target = target_ob
    c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("wrote", scene.render.filepath)

shot("hero", (0.27, -0.37, 0.40), (0.0, 0.035, 0.04), lens=46)
shot("render_rear", (-0.36, 0.52, 0.26), (0.0, 0.04, 0.03))
shot("render_top", (0.0, 0.03, 0.62), (0.0, 0.03, 0.0), lens=60, res=(1600, 1600))
