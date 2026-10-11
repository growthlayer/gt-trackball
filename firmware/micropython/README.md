# Patched MicroPython for the GT Trackball

The firmware needs **this MicroPython build**, not the stock
`RPI_PICO2_W` download: MicroPython v1.29.0 plus
`gt-trackball-micropython-v1.29.0.patch`.

| File | What it is |
|---|---|
| `gt-trackball-micropython-v1.29.0-RPI_PICO2_W.uf2` | ready to flash (hold BOOTSEL, plug in, copy it to the `RP2350` drive; or `machine.bootloader()` from the REPL) |
| `gt-trackball-micropython-v1.29.0.patch` | the changes, against the `v1.29.0` tag |
| `build.sh` | rebuilds the `.uf2` from the tag + patch |

Flashing firmware doesn't touch the filesystem: `main.py`, `config.py`
and `lib/` survive.

## What the patch changes, and why

**1. Trackball comes up in PS/2 mode** (`ports/rp2/boards/RPI_PICO2_W/mpconfigboard.h`)

The trackball's own USB/PS2 chip picks USB or PS/2 once, at power-up,
from the level of DATA/CLOCK: pulled down means USB, pulled up means
PS/2. Its 5 V comes up with the Pico's, and RP2350 pads default to
pull-down, so with stock firmware a cold start put it in USB mode (it
then ignores PS/2; DATA sits high on the chip's own 1.5 kΩ USB pull-up).
`MICROPY_BOARD_STARTUP()` now pulls GP2/GP3 up within milliseconds of
reset. (The trackball MOSFET, GP22, makes this deterministic too: the
firmware can power the trackball only after the pull-ups are on.)

**2. Bluetooth pairing and bonding** (`MICROPY_PY_BLUETOOTH_ENABLE_PAIRING_BONDING`)

HID-over-GATT hosts require a bonded, encrypted link. The stock build
compiles pairing out (`ble.config(bond=...)` is "unknown config param").

**3. Just Works pairing is confirmed** (`extmod/btstack/modbluetooth_btstack.c`)

BTstack waits for the application to confirm Just Works pairing
(`SM_EVENT_JUST_WORKS_REQUEST`), but MicroPython never registered for
Security Manager events, so pairing stalled until the host's 30 s SMP
timeout. The binding now registers with `sm_add_event_handler` and
confirms (no UI on this device to ask).

**4. Service Changed is INDICATE**

MicroPython declared the GATT Service Changed characteristic (0x2A05)
read-only. The spec requires INDICATE; macOS enables its indications
right after pairing, and the failure crashed macOS 26's `bluetoothd`.

**5. GATT reads return the value** (inverted check)

`att_read_callback` treated `mp_bluetooth_gatts_on_read_request() == 0`
as "denied" -- but 0 means allowed (the NimBLE binding uses it that
way). On ports with sync BLE events (rp2) every read of a
characteristic therefore returned zero bytes: macOS read an empty
Device Information PnP ID and crashed `bluetoothd`.

Fixes 3-5 are MicroPython bugs worth reporting upstream.

## Status

Verified on the bench, 2026-09-25:

- USB HID mouse, PS/2 trackball, buttons, e-paper.
- Trackball in PS/2 mode after a cold power-up (fix 1).
- **Bluetooth mouse on macOS 26**: pairs ("Just Works", no PIN), bonds,
  cursor and all three buttons work, no `bluetoothd` crashes. After a
  full power cycle it reconnects with the stored bond, no re-pairing.
