# GT Trackball — build assistant notes for Claude Code

You are helping someone build (or modify) the GT Trackball: a wireless 3"
arcade trackball for Golden Tee, with a Raspberry Pi Pico 2 W, an e-paper
screen and a 3D-printed case. The builder may not be an electronics person.
Work step by step with them, confirm what they see before moving on, and
ask for a photo whenever the hardware state is unclear.

## Where things are

| Path | What |
|---|---|
| `README.md` | the build guide: parts, Steps 1–6, troubleshooting. Follow its order. |
| `images/wiring_*.png` | per-step wiring pictures with a pin-to-pin chart on the right |
| `harness/gt-trackball.yml` | every wire as data (WireViz) — the source of truth for pin-to-pin questions |
| `firmware/` | MicroPython firmware; `config.py` holds every pin and tunable |
| `firmware/micropython/` | the patched MicroPython `.uf2` (the stock build will NOT work) |
| `print/` | ready-to-print Bambu Studio 3MFs per printer + STLs |
| `trackball_bt_case.scad` | the parametric case (OpenSCAD) |
| `pc/` | Windows / TeknoParrot / RetroBat setup and the AutoHotkey script |
| `tools/` | generators for the print files, wiring pictures and schematic |

## Things you can do for the builder

- **Flash the Pico** (README Step 4 / `firmware/README.md`): copy the patched
  `.uf2` to the RP2350 drive (BOOTSEL held while plugging in), then
  `mpremote mip install aioble`, `mpremote mip install usb-device-hid`, and
  `mpremote cp <firmware files> :`. Check with `mpremote ls`.
- **Bench test**: `mpremote repl` shows the logs; `firmware/demo.py` exercises
  the screen with nothing else wired.
- **Change settings** (speed, axis direction, sleep time, swing meter): edit
  `firmware/config.py`, then `mpremote cp firmware/config.py :`.
- **Print files for another printer**: `python tools/make_print_files.py`
  (needs Bambu Studio); for other slicers use the STLs in `print/stl/` with
  the settings in `print/README.md`.
- **Case changes**: edit `trackball_bt_case.scad`, export STLs with OpenSCAD
  (`openscad -o print/stl/top.stl -D 'part="shell"' trackball_bt_case.scad`),
  then rebuild the print files.
- **Wiring questions**: answer from `harness/gt-trackball.yml` and the README
  table; regenerate the pictures with `python tools/make_wiring_diagrams.py`
  if wiring changes.
- **PC setup**: walk through `pc/README.md` (pairing, TeknoParrot bindings,
  the RetroBat script).

## Rules

- After **any** `mpremote` command, run `mpremote reset` — mpremote leaves the
  firmware stopped, and the trackball looks dead until it is reset.
- Before power is first applied: the charger's output must be set to
  **5.00 V** with nothing connected, measured with a multimeter. Ask for the
  reading; do not skip this.
- The e-paper is **3.3 V only** (Pico pin 36). Never let anything wire it to 5 V.
- The voltage sensor's GND screw stays **empty** (it would bypass the battery
  protection).
- LiPo safety: never clamp, puncture or short the pouch; if it is swollen or
  hot, stop and tell the builder to disconnect it.
- Pin numbers are the Pico's **physical** pins; the Pico is mounted pins-up,
  so the builder reads the labels printed on the pin side.
- If a measurement or photo contradicts the docs, trust the hardware, say
  so, and stop to work out why before continuing.
- Don't run commands that change the builder's computer settings (registry,
  drivers, system mouse settings) yourself — give them the command and let
  them run it.
