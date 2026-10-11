# Firmware — Bluetooth / USB Arcade Trackball

MicroPython for the Pico 2 W. One firmware, two modes:

| Cable in the rear USB-A port? | Mode |
|---|---|
| no | **Bluetooth LE HID mouse** (advertises as *GT Trackball*) |
| yes | **USB HID mouse** on the same cable; the battery charges at the same time |

Plugging or unplugging the cable reboots the Pico into the other mode
(~2 s). There is no power switch: after `IDLE_SLEEP_S` (5 min) the
trackball is powered down and the Pico sleeps; a button press wakes it.
A hardware watchdog reboots the firmware if it ever hangs.

## Files

| File | Purpose |
|---|---|
| `config.py` | pins and all tunables |
| `main.py` | mode select, input loop, sleep/wake, watchdog |
| `ps2.py` | PS/2 host for the trackball's own USB/PS2 board (PIO receiver, IRQ-buffered) |
| `hid_mouse.py` | BLE HOGP mouse (aioble) |
| `usb_mouse.py` | USB HID mouse (`usb-device-hid`) |
| `epd213.py` | e-ink driver: landscape drawing, full + partial refresh, async |
| `art.py` | pixel art and screen layouts |
| `display.py` | screen manager: boot / pairing / connected animations, swing updates, ghost cleanup, sleep screen |
| `swing.py` | swing meter (peak forward ball speed -> score) |
| `demo.py` | bench demo of every screen, needs only the display wired |
| `battery.py` | battery voltage via the GP26 divider |
| `micropython/` | the patched MicroPython `.uf2`, its patch and build script |

## Flashing

1. Install the **patched MicroPython** from [`micropython/`](micropython/)
   (`gt-trackball-micropython-v1.29.0-RPI_PICO2_W.uf2`) — hold BOOTSEL,
   plug in, copy the `.uf2`. The stock micropython.org build won't do:
   with it the trackball comes up in USB mode after a cold start, and
   Bluetooth can't pair. See [`micropython/README.md`](micropython/README.md).
2. Install the two libraries:
   ```
   mpremote mip install aioble
   mpremote mip install usb-device-hid
   ```
3. Copy the firmware:
   ```
   mpremote cp config.py ps2.py hid_mouse.py usb_mouse.py epd213.py art.py display.py swing.py battery.py main.py :
   ```
4. Unplug USB and power from the battery: the e-ink shows `pairing...`; add
   **GT Trackball** in Windows Bluetooth settings like any mouse. Bonding is
   saved, so it reconnects by itself afterwards.

## Changing settings once it's in the case

No need to open it. The rear USB port is the Pico's own USB, and in USB
mode it is a mouse **and** a serial REPL at the same time
(`builtin_driver=True`), so from any computer with the A-to-A cable:

```
mpremote cp config.py :     # after editing config.py
mpremote reset
```

The watchdog only runs in Bluetooth mode, so it can't reset the board
mid-copy. If a bad edit ever stops it booting cleanly, **hold LEFT +
RIGHT (not MENU) while plugging the cable in**: safe mode starts nothing, leaving
just the REPL for mpremote. Last resort: BOOTSEL needs the case open.
(There's no SSH -- the Pico isn't a Linux computer; USB is the way in.)

## Wiring recap (see ../images/wiring.svg)

| Pico pin | Function |
|---|---|
| GP2 (pin 4) | trackball J1 **DATA** (PS/2) |
| GP3 (pin 5) | trackball J1 **CLOCK** (PS/2) |
| GP4 / GP5 / GP6 (pins 6, 7, 9) | LEFT / RIGHT / MENU switch, harness pin 2 (MENU = middle click) |
| GP7 (pin 10) | button common: harness pin 3 of all three buttons |
| GND (pin 8) | harness pin 1 of all three buttons |
| GP22 | MOSFET module TRIG/PWM (whole trackball 5 V: its board + RGB) |
| GP8–GP13 | e-ink display (see below) |
| GP26 | battery sense: 0–25 V sensor module S (B+ ÷ 5) |
| VSYS | +5 V from the charger/boost board OUT+ |
| VBUS | → USB-C male pigtail into the charger/boost board (charges from the USB cable) |

### Trackball

The trackball's X-sensor board has its own USB/PS2 chip, which decodes
both encoders. Its connector **J1** reads `+5V DATA CLOCK GND M R L`.
The stock cable (red/white/green/black to a USB-A plug) uses the first
four; unplug it and wire J1 instead:

| J1 | To |
|---|---|
| +5V | +5 V rail (VBUS, pin 40, on the bench) |
| DATA | GP2 |
| CLOCK | GP3 |
| GND | the MOSFET's switched ground in the case; any GND on the bench |
| M / R / L | unused (the trackball's own button inputs) |

The Pico is the PS/2 host: it resets the trackball, sets 200 reports/s
and enables streaming at boot (`ps2.py`). DATA/CLOCK are
open-collector and the Pico only ever pulls them low, so nothing drives
5 V into it. Verified on hardware: reset → `FA AA 00`, ball right = +X,
ball away = +Y (the firmware flips Y for HID, so away = cursor up).

### Buttons

The lit buttons have a small board (JZT-08: switch + LED + 330 Ω) and a
3-wire harness with an XH plug at both ends. The wire **markings differ
between harnesses** -- go by plug position, counted with the latch
toward you, wires down, 1-2-3 left to right:

| Harness pin | Inside the button | To |
|---|---|---|
| 1 | LED − | GND (all three) |
| 2 | switch | its own GPIO: GP4 / GP5 / GP6 |
| 3 | LED + **and** the switch's other side | GP7 (all three) |

The switch shares the LED+ wire, so pressing it connects pin 2 to pin 3.
GP7 is held high (the LEDs light, dimly, from 3.3 V) and pulled low for
20 µs about every 10 ms to read the buttons: a pressed switch then
pulls its GPIO low against the internal pull-up. No resistors, and
nothing on the buttons sees 5 V. Check each harness before wiring it: 5 V
on pin 3 and GND on pin 1 should light its LED.

## Display wiring

The **Raspberry Pi** form-factor `2.13inch e-Paper HAT` (65 × 30.5 mm,
250×122, V4/SSD1680) is wired, not plugged on. Use its 8-pin JST lead:

| Display pin | Pico pin | Note |
|---|---|---|
| VCC | 3V3 (pin 36) | 3.3 V only |
| GND | any GND | |
| DIN | GP11 | SPI1 MOSI |
| CLK | GP10 | SPI1 SCK |
| CS  | GP9  | |
| DC  | GP8  | |
| RST | GP12 | |
| BUSY| GP13 | |

No JST lead? The same signals are on the 2×20 socket at the Raspberry Pi
positions — 3V3 pin 1, GND pin 6, DIN 19, CLK 23, CS 24, DC 22, RST 11,
BUSY 18 — reachable with male-to-female jumpers.

## Tuning (`config.py`)

- Cursor direction wrong → `INVERT_X` / `INVERT_Y`; axes crossed → `SWAP_XY`.
- Cursor speed → `SCALE_NUM` / `SCALE_DEN` (e.g. 1/2 = half speed).
- Time before sleep → `IDLE_SLEEP_S`.
- Trackball report rate / resolution → `PS2_SAMPLE_RATE` / `PS2_RESOLUTION`.
- Button LEDs off → `BUTTON_LEDS = False`.
- `USB_MODE_ENABLED = False` forces Bluetooth even with a cable in (the
  cable then only charges).

## Screen

- **Boot**: ball drops onto a tee, then the main screen.
- **Main**: name, Bluetooth / USB icon, battery; big **LAST SWING**
  number; **BEST** under a pixel flag-and-tee scene.
- **Pairing**: the Bluetooth icon pulses for `PAIR_ANIM_S`, then holds.
- **Connected**: the flag waves.
- **Sleep**: moon-and-zzz scene with the battery level; e-ink keeps it on
  screen at zero power.

Updates use partial refreshes (~0.6 s measured, vs ~3.3 s full); after `GHOST_PARTIALS` of them a
full (flashing) refresh cleans up ghosting, but only once the controller
has been idle `GHOST_IDLE_S` — never mid-game. Redraws run as an asyncio
task, so the cursor never stalls.

**Swing meter calibration:** every swing prints
`swing: peak N counts/s -> score S` on the REPL. Hit a few hard drives,
then set `SWING_SCALE_DEN` so they read ~100. If ordinary cursor moves
register as swings, raise `SWING_START_CPS`; if the backswing is scored
instead of the forward swing, flip `SWING_FORWARD`.

## Sleep, in detail

1. `IDLE_SLEEP_S` with no input → screen says `sleeping`, BLE stops,
   the PS/2 pull-ups are dropped (so the Pico doesn't feed the unpowered
   trackball through DATA/CLOCK), GP22 goes low (trackball fully off)
   and GP7 goes low (button LEDs off).
2. Loop: `lightsleep(SLEEP_CHUNK_MS)` → feed the watchdog → button
   pressed? cable plugged?
3. Either → `machine.reset()` — a clean boot is the reliable way back to
   a working radio / USB stack.

Wake is by **button** (within ~1 s; hold it briefly). Spinning the ball
does not wake it: the trackball is unpowered in sleep, and restarting its
PS/2 chip to check for movement takes ~0.4 s at full trackball current.

## First bring-up checklist

1. **Before the battery chain**: power the Pico from USB only. It boots as
   a USB mouse — the cursor should move when you spin the ball
   (`mpremote repl` on the same cable shows the logs).
2. Watch for `e-ink init failed` (panel revision mismatch → compare
   `epd213.py` against Waveshare's demo for the revision on your flex).
3. Unplug USB and power from the charger/boost board's OUT: e-ink says `pairing...`; pair
   and verify cursor motion. Fix direction / speed in `config.py`.
4. Leave it 5 min: screen should say `sleeping`, the ball and button LEDs
   go dark. Press a button: reboots and reconnects.
5. Verify the battery reading against a meter on B+ (`battery.read_battery()`); adjust `BATT_DIVIDER` if it's off.
6. Plug the cable back in while paired: it should drop BLE and re-appear as
   a USB mouse; the charger board's charge LED should come on.
7. TeknoParrot: the trackball needs no change (*Windows Mouse Cursor*). The
   three buttons are now mouse L / R / M — rebind them in the game profile.

## Verified on the bench (2026-09-25)

- USB mode: macOS sees a HID mouse (VID 0x2E8A); ball moves the cursor,
  LEFT / RIGHT / MENU click.
- PS/2: reset, 200 Hz, streaming; all four directions, no drift at rest,
  no dropped frames while the e-paper redraws.
- Buttons: one clean transition per press at 1 ms resolution (no bounce),
  LEFT+RIGHT combo reads correctly.
- Bluetooth mouse on macOS 26: pairs, bonds, cursor + buttons work, and
  it reconnects on its own after a power cycle (needs the patched
  MicroPython, see `micropython/`).
- Swing meter calibrated (2026-10-11, USB on the TeknoParrot PC): normal
  aiming/menu movement triggered nothing at `SWING_START_CPS = 1500`;
  five hard drives peaked 6090-9900 counts/s (scores 60-99 with
  `SWING_SCALE_DEN = 100`); soft putts 1545-2090 (15-20), the softest
  one below the threshold. Defaults kept.

## Verified on battery (2026-10-11)

- MOSFET module: GP22 switches the trackball and ball light off and on;
  the trackball answers PS/2 again after power returns.
- Battery sense: 3.955 V read vs 3.95 V on a meter (`BATT_DIVIDER = 4.95`).
- Charging from the USB cable through the pigtail (charge LED on).
- Unplugging USB restarts into Bluetooth on battery; the Mac reconnects
  with the stored bond and the cursor works.
- Sleep after 5 min without input (Bluetooth drops, trackball and lights
  off); a button press wakes it, it reconnects and the cursor works.

## Verified on Windows 11 (2026-10-11)

- Bluetooth on the TeknoParrot PC (Intel adapter): pairs, connects, and
  shows up as a BLE HID mouse (VID 0x2E8A); cursor and buttons work.
  If pairing ever misbehaves, `BLE_DEBUG = True` prints each Bluetooth
  event on the USB REPL.

## Known unknowns to verify on hardware

- BLE bonding persistence across a full battery drain
- lightsleep current with the MOSFET open — measure it; if the radio is not
  fully off, `aioble.stop()` may need `bluetooth.BLE().active(False)` too
