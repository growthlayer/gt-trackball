# Printing the case

Three parts — **top shell**, **bottom plate**, **2 display clips** — in
PLA, no supports. Every file below comes with the print settings built in.

## Ready-to-print Bambu Studio projects

Pick the folder for your printer, open a file, press **Slice all**, print.

| Folder | Printer |
|---|---|
| [`bambu-x1c/`](bambu-x1c/) | X1 Carbon / X1 / X1E |
| [`bambu-p1s/`](bambu-p1s/) | P1S / P1P |
| [`bambu-a1/`](bambu-a1/) | A1 (not the A1 mini — the top shell needs a 256 mm bed) |

Each folder has:

| File | Contents | X1C / P1S | A1 |
|---|---|---|---|
| **`gt-trackball-all.3mf`** | everything, 2 plates: top shell + clips, then the bottom plate | 8 h 26 min, 446 g | 8 h 49 min, 446 g |
| `top.3mf` | top shell only | 5 h 46 min, 322 g | 6 h 00 min, 322 g |
| `bottom.3mf` | bottom plate only | 2 h 37 min, 123 g | 2 h 46 min, 123 g |
| `clips.3mf` | the 2 display clips | 3 min | 3 min |

All twelve slice with no warnings (0.4 mm nozzle, Bambu PLA Basic,
0.20 mm layers + the settings below). Another Bambu printer with a 256 mm
bed: open any of them and switch the printer at the top-left of Bambu
Studio — the process settings carry over.

## Other slicers (Prusa, Orca, Cura, ...)

The plain models are in [`stl/`](stl/) — `top.stl`, `bottom.stl`,
`clips.stl`, already in print orientation. An STL can't carry settings, so
use the table below. Bed needed: about 256 × 256 mm (top shell is
201 × 225 mm, plus a 5 mm brim).

To rebuild the projects after changing the design:
`python tools/make_print_files.py` (needs Bambu Studio installed).

## Common (all parts)

| Setting | Value | Why |
|---|---|---|
| Material | PLA, or PETG if the room gets hot (the deck takes palm pressure) | |
| Nozzle | 0.4 mm | |
| Layer height | 0.20 mm | 0.16 on the top if you want a smoother deck |
| Walls | **4** (1.6 mm) | pins, pillars and the feedthrough ring are wall-only features |
| Top / bottom layers | 5 / 4 | the 4.5 mm deck is mostly solid anyway |
| Infill | 15 % gyroid | |
| Supports | **none** | every part is designed support-free |
| Brim | 5 mm outer | the top shell's big flat footprint lifts at the corners; harmless on the other parts |
| Seam | rear | keeps the seam off the palm bevel |
| Elephant-foot compensation | 0.15 mm | keeps the ball bore and button holes on size |

## Per part

| Part | Orientation | Notes |
|---|---|---|
| `top.stl` | **as exported** — deck face down on the bed | The Ø76.1 ball bore, the four Ø5.1 locating pins and the corner pillars all point up. The 45° palm bevel is self-supporting. The e-ink window is a through-cut, nothing to bridge. |
| `bottom.stl` | as exported, flat side down | Battery tray walls, Pico standoffs and board posts point up. The Ø13 × 1.2 feet recesses are on the bed side and print as-is. |
| `clips.stl` | as exported | Two small bars; print together. |

## After printing

- **Pin fit**: the four locating pins are Ø5.1 to match the original. If
  the trackball is tight on them, ease the *trackball* holes with a 5 mm
  drill — do not thin the pins.
- **Inserts**: M3 × L4 × D5 heat-set into the Ø4.2 pillar pockets at
  ~230 °C (PLA) / ~250 °C (PETG). Keep the iron square.
- **Feedthrough**: the Ø24.4 rear-wall hole and the two Ø2.6 pilots suit
  the D-type's M3 self-tappers. Test-fit before wiring.
- **Button holes**: Ø29.3, same as the original — a 1-1/8" arcade button
  pushes in without filing.
