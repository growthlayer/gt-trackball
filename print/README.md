# Printing the case

## The easy way: `gt-trackball-case.3mf`

One Bambu Studio project with every part placed and every setting below
already applied (X1 Carbon, 0.4 nozzle, Bambu PLA Basic, 0.20 mm). Open
it, press **Slice all**, send each plate.

| Plate | Parts | Time | PLA |
|---|---|---|---|
| 1 | top shell (deck down) + 2 display clips | ≈ 5 h 50 min | ≈ 323 g |
| 2 | bottom plate | ≈ 2 h 40 min | ≈ 123 g |

Printing on the **A1** instead: switch the printer at the top-left of
Bambu Studio; it keeps the process settings. The project slices with no
warnings and both plates fit the 256 mm bed with the brim.

The individual `top.stl`, `bottom.stl` and `clips.stl` are here too for
other slicers — use the settings below.

Tested target: Bambu Lab X1C / A1 (256 mm bed). The top shell is
201 × 225 mm, so it needs the full bed.

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
| Brim | 5 mm outer (the top shell's big flat footprint lifts at the corners) | the 3MF applies it to every part; harmless on the others |
| Seam | rear | keeps the seam off the palm bevel |
| Elephant-foot compensation | 0.15 mm | keeps the ball bore and button holes on size |

## Per part

| File | Orientation | Notes |
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
