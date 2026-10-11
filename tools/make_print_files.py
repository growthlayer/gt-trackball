# ============================================================
#  Build the ready-to-print Bambu Studio projects from the STLs.
#
#    python tools/make_print_files.py [path\to\bambu-studio.exe]
#
#  For each printer it writes print/bambu-<printer>/:
#    gt-trackball-all.3mf   every part, arranged on 2 plates
#    top.3mf / bottom.3mf / clips.3mf   one part each
#  all with the case's print settings applied on top of Bambu's
#  "0.20mm Standard" process and "Bambu PLA Basic" filament.
# ============================================================
import glob, json, os, shutil, subprocess, sys, tempfile, time, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = sys.argv[1] if len(sys.argv) > 1 else r"C:\Program Files\Bambu Studio\bambu-studio.exe"
BBL = os.path.join(os.path.dirname(EXE), "resources", "profiles", "BBL")
STL = os.path.join(ROOT, "print", "stl")

PRINTERS = {          # folder: (machine, process, filament)
    "x1c": ("Bambu Lab X1 Carbon 0.4 nozzle", "0.20mm Standard @BBL X1C", "Bambu PLA Basic @BBL X1C"),
    "p1s": ("Bambu Lab P1S 0.4 nozzle", "0.20mm Standard @BBL X1C", "Bambu PLA Basic @BBL X1C"),
    "a1":  ("Bambu Lab A1 0.4 nozzle", "0.20mm Standard @BBL A1", "Bambu PLA Basic @BBL A1"),
}
CASE_SETTINGS = {
    "wall_loops": "4",
    "top_shell_layers": "5",
    "bottom_shell_layers": "4",
    "sparse_infill_density": "15%",
    "sparse_infill_pattern": "gyroid",
    "enable_support": "0",
    "seam_position": "back",
    "elefant_foot_compensation": "0.15",
    "brim_type": "outer_only",
    "brim_width": "5",
}
SETS = {"gt-trackball-all": ["top", "bottom", "clips"], "top": ["top"], "bottom": ["bottom"], "clips": ["clips"]}
META = {"Title": "GT Trackball - wireless 3in arcade trackball case",
        "License": "CC BY-SA 4.0",
        "Description": "Remix of 3-Inch Arcade Trackball Case by vkschannel (thing:7334881). "
                       "Build guide: github.com/growthlayer/gt-trackball",
        "ProfileTitle": "0.20mm PLA, 4 walls, gyroid 15%, no supports"}

index = {}
for kind in ("machine", "process", "filament"):
    for p in glob.glob(os.path.join(BBL, kind, "**", "*.json"), recursive=True):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if "name" in d:
            index[(kind, d["name"])] = d

def flat(kind, name):
    d = dict(index[(kind, name)])
    parent = d.pop("inherits", None)
    if parent:
        base = flat(kind, parent); base.update(d); d = base
    return d

def write(kind, name, extra, path, printer):
    d = flat(kind, name); d.update(extra)
    d.pop("inherits", None); d.pop("instantiation", None)
    d["from"] = "User" if extra else "system"
    if kind != "machine" and "compatible_printers" in d and printer not in d["compatible_printers"]:
        d["compatible_printers"] = list(d["compatible_printers"]) + [printer]
    json.dump(d, open(path, "w", encoding="utf-8"), indent=1)

def set_meta(path):
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                t = data.decode("utf-8")
                for k, v in META.items():
                    t = t.replace(f'<metadata name="{k}"></metadata>', f'<metadata name="{k}">{v}</metadata>')
                data = t.encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, path)

work = tempfile.mkdtemp(prefix="gt3mf_")
for key, (machine, process, filament) in PRINTERS.items():
    prof = os.path.join(work, key); os.makedirs(prof, exist_ok=True)
    write("machine", machine, {}, os.path.join(prof, "machine.json"), machine)
    write("process", process, dict(CASE_SETTINGS, name="GT Trackball case 0.20mm (4 walls, gyroid 15%)"),
          os.path.join(prof, "process.json"), machine)
    write("filament", filament, {}, os.path.join(prof, "filament.json"), machine)
    out_dir = os.path.join(ROOT, "print", "bambu-" + key); os.makedirs(out_dir, exist_ok=True)
    for name, parts in SETS.items():
        out = os.path.join(out_dir, name + ".3mf")
        if os.path.exists(out):
            os.remove(out)
        cmd = [EXE, "--orient", "0", "--arrange", "1",
               "--load-settings", os.path.join(prof, "machine.json") + ";" + os.path.join(prof, "process.json"),
               "--load-filaments", os.path.join(prof, "filament.json"),
               "--export-3mf", out] + [os.path.join(STL, p + ".stl") for p in parts]
        subprocess.run(cmd, cwd=work)
        for _ in range(120):                    # the GUI build returns before it finishes
            if os.path.exists(out):
                break
            time.sleep(0.5)
        time.sleep(1)
        set_meta(out)
        print("wrote", os.path.relpath(out, ROOT))
shutil.rmtree(work, ignore_errors=True)
