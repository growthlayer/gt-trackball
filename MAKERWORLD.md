# MakerWorld listing — copy/paste kit

Everything needed to publish this on MakerWorld. Files to upload are
listed at the bottom.

---

## Title

GT Trackball — Wireless 3" Arcade Trackball for Golden Tee (Bluetooth + USB, e-paper swing meter)

## Category / tags

Category: **Gadgets → Computers & Accessories** (or Toys & Games → Game accessories)

Tags: `trackball`, `arcade`, `golden tee`, `bluetooth`, `raspberry pi pico`,
`pico 2 w`, `e-paper`, `e-ink`, `mouse`, `controller`, `teknoparrot`,
`retrobat`, `mame`, `golf`, `remix`

## License

**CC BY-SA 4.0** (Attribution-ShareAlike) — required: this is a remix of a
CC BY-SA design.

## Remix source

Remix of **3-Inch Arcade Trackball Case** by **vkschannel** —
https://www.thingiverse.com/thing:7334881 (itself a remix of
https://www.thingiverse.com/thing:5914322). Add it in MakerWorld's
"Remixed from" field as an external link.

---

## Description (paste into the description box)

**A wireless arcade trackball you can actually golf with.**

GT Trackball turns a standard 3" illuminated arcade trackball into a
**Bluetooth and USB mouse** with a **battery**, **three lit arcade
buttons** and a **2.13" e-paper screen** that shows the connection, battery
and a **swing meter** — your last swing and best swing after every shot.
It was built for **Golden Tee Live** (TeknoParrot / RetroBat), but it's a
normal mouse, so it works with any game, emulator or computer.

**Features**
- Bluetooth LE on battery, wired USB + charging through one USB-A port
- No power switch — sleeps after 5 minutes, wakes on a button press
- E-paper status screen with pixel-art animations; stays on at zero power
- Same proven trackball mount as the original case (locating pins, clamp)
- Prints **without supports** on any 256 mm bed — two plates, ≈ 8.5 h,
  ≈ 450 g PLA

**Print settings** (already in the 3MF): 0.20 mm layers, 4 walls, 15 %
gyroid, 5 top / 4 bottom layers, 5 mm brim, seam at the rear, elephant-foot
compensation 0.15 mm, no supports. Plate 1: top shell + display clips.
Plate 2: bottom plate.

**You'll also need** a 3" USB/PS2 arcade trackball, a Raspberry Pi Pico 2 W,
a Waveshare 2.13" e-Paper HAT V4, a small charger + boost board, a
52 × 35 × 10 mm LiPo, a MOSFET module, a voltage sensor module, three 30 mm
lit buttons, a USB-A panel feedthrough, 4 M3 heat-set inserts and a few
screws. **Full parts list, wiring diagrams, firmware and step-by-step build
guide:**

👉 **https://github.com/growthlayer/gt-trackball**

**Assembly in short**
1. Print both plates; melt 4 M3 inserts into the top shell.
2. Flash the Pico with the included MicroPython build and copy the firmware.
3. Wire it up (diagram in the repo) and bench-test.
4. Fit buttons, USB port, e-paper and electronics; drop the trackball onto
   its pins; close with 4 screws.
5. Pair "GT Trackball" over Bluetooth, or plug it in.

Credit and thanks to **vkschannel** for the original case.

---

## Images to upload (in this order)

1. `images/hero.png` — cover
2. real photo of your finished controller (front, screen visible)
3. real photo showing it in use / on screen in Golden Tee
4. `images/render_top.png`
5. `images/render_rear.png` — USB port
6. `images/exploded.png` — exploded view with part numbers
7. `images/overview.png` — how it connects
8. `images/wiring.png` — full wiring
9. `images/layout_top.png` — where everything sits

## Files to upload

- **Model files:** `print/stl/top.stl`, `print/stl/bottom.stl`, `print/stl/clips.stl`
- **Print profiles** — MakerWorld takes one Bambu Studio project per
  profile; upload each as its own profile so people get the right printer:
  - `print/bambu-x1c/gt-trackball-all.3mf` — "X1 Carbon · all parts, 2 plates"
  - `print/bambu-p1s/gt-trackball-all.3mf` — "P1S · all parts, 2 plates"
  - `print/bambu-a1/gt-trackball-all.3mf` — "A1 · all parts, 2 plates"
  - optionally the per-part projects (`top.3mf`, `bottom.3mf`, `clips.3mf`)
    as extra profiles for people who print one part at a time
- Optional "other files": `trackball_bt_case.scad` (editable source)

Firmware stays on GitHub (MakerWorld only hosts print files); the
description links to it.
