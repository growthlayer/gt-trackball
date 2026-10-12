# ============================================================
#  Bluetooth / USB Arcade Trackball - main firmware (Pico 2 W)
#
#  Modes (chosen at boot, re-evaluated on cable plug/unplug -> restart):
#    USB cable present  -> wired USB HID mouse, radio off
#    no cable           -> Bluetooth LE HID mouse
#  There is no power switch: in Bluetooth mode, after IDLE_SLEEP_S the
#  trackball is powered down and the Pico lightsleeps, waking on a
#  button press. A hardware watchdog (Bluetooth mode only) reboots the
#  firmware if it ever hangs.
#  Restarts (restart() below): plugging the cable in uses a SOFT
#  restart -- on battery the Pico stays powered, and a hard
#  machine.reset() with the cable attached left USB dead (the host saw no
#  device). Waking from sleep and pulling the cable use a HARD reset:
#  there is no cable then, and a soft restart leaves the Wi-Fi/Bluetooth
#  chip running, after which Windows could never re-encrypt the link
#  (connected, no cursor, until re-paired).
#
#  Maintenance: the USB cable also carries the MicroPython REPL, so
#  config.py can be changed in the finished case with mpremote. Hold
#  LEFT + RIGHT while plugging in to skip the firmware entirely
#  (safe mode: REPL only, nothing running).
#
#  Deps:  mpremote mip install aioble usb-device-hid
# ============================================================

import os
import time
import asyncio
import machine
from machine import Pin
import config
import battery
from ps2 import PS2Mouse

btn_l = Pin(config.PIN_BTN_LEFT, Pin.IN, Pin.PULL_UP)
btn_r = Pin(config.PIN_BTN_RIGHT, Pin.IN, Pin.PULL_UP)
btn_m = Pin(config.PIN_BTN_MIDDLE, Pin.IN, Pin.PULL_UP)
# switch common + LED+ of all three buttons (see config.py)
btn_com = Pin(config.PIN_BTN_COMMON, Pin.OUT, value=1 if config.BUTTON_LEDS else 0)


def buttons():
    # pull the common low briefly: a pressed switch pulls its pin low.
    # HID bits: 0=left 1=right 2=middle
    lit = btn_com.value()
    btn_com.value(0)
    time.sleep_us(config.BTN_STROBE_US)
    b = ((0 if btn_l.value() else 1)
         | (0 if btn_r.value() else 2)
         | (0 if btn_m.value() else 4))
    btn_com.value(lit)
    return b


def button_leds(on):
    btn_com.value(1 if on and config.BUTTON_LEDS else 0)


time.sleep_ms(50)
# The watchdog keeps running across a soft restart; restart() leaves this
# flag so the next boot keeps feeding it (a starved watchdog would do the
# hard reset that breaks USB).
_WDT_FLAG = "wdt_on"
try:
    os.remove(_WDT_FLAG)
    WDT_RUNNING = True
except OSError:
    WDT_RUNNING = False

# exactly LEFT + RIGHT held at power-up (not on a wake-up press)
SAFE_MODE = buttons() == 3 and not WDT_RUNNING
                                             # (all three = lying face-down, not safe mode)

from display import Display
from swing import SwingMeter

tb_en = Pin(config.PIN_TRACKBALL_EN, Pin.OUT, value=1)
ball = PS2Mouse(config.PIN_PS2_DATA, config.PIN_PS2_CLOCK)

try:
    _vbus = Pin("WL_GPIO2", Pin.IN)          # VBUS sense on Pico (2) W
    def usb_present(): return bool(_vbus.value())
except Exception:
    def usb_present(): return False

USB_MODE = config.USB_MODE_ENABLED and usb_present()
# No watchdog in USB mode: it's mains-powered (a hang can't drain the
# battery) and a running watchdog would reset the board while mpremote
# is copying files. Exception: one already running from Bluetooth mode
# can't be stopped, so it has to be fed.
wdt = (machine.WDT(timeout=config.WDT_TIMEOUT_MS)
       if WDT_RUNNING or not (USB_MODE or SAFE_MODE) else None)


def feed():
    if wdt:
        wdt.feed()


def restart(hard=False):
    """Re-run the firmware from the top. hard=True (no cable attached):
    full reset, which also power-cycles the radio chip. Otherwise soft:
    see the header."""
    if hard:
        machine.reset()
    if wdt:
        try:
            open(_WDT_FLAG, "w").close()
        except OSError:
            pass
    machine.soft_reset()


disp = Display(wdt)
if not SAFE_MODE:
    feed()
    if not ball.init(config.PS2_SAMPLE_RATE, config.PS2_RESOLUTION):
        print("trackball: no PS/2 response (check J1 wiring / 5 V)")
meter = SwingMeter()
_last_input = time.ticks_ms()
disp.idle_ms = lambda: time.ticks_diff(time.ticks_ms(), _last_input)


def transform(dx, dy):
    if config.SWAP_XY:
        dx, dy = dy, dx
    if config.INVERT_X: dx = -dx
    if config.INVERT_Y: dy = -dy
    return dx * config.SCALE_NUM // config.SCALE_DEN, dy * config.SCALE_NUM // config.SCALE_DEN


def battery_state():
    pct, _ = battery.percent()
    return 5 * round(pct / 5)                 # 5 % steps: fewer redraws


# ---------- sleep ----------
def go_to_sleep(stop_radio):
    stop_radio()
    ball.release_lines()                      # don't feed the unpowered chip
    tb_en.value(0)
    button_leds(False)
    disp.set(batt=battery_state())
    disp.sleep_screen()                       # stays visible at 0 W
    while True:
        feed()
        machine.lightsleep(config.SLEEP_CHUNK_MS)
        feed()
        if buttons() or (config.USB_MODE_ENABLED and usb_present()):
            break
    restart(hard=True)                        # wake: fresh radio, no cable attached


# ---------- shared tasks ----------
def _clamp127(v):
    return -127 if v < -127 else (127 if v > 127 else v)


async def input_task(send):
    global _last_input
    prev = 0
    rx = ry = 0                                # motion not yet reported
    t_retry = time.ticks_ms()
    while True:
        feed()
        # the trackball can miss its start-up init (e.g. still in its own
        # power-up self-test): keep retrying instead of leaving it dead
        if not ball.ok and time.ticks_diff(time.ticks_ms(), t_retry) > 3000:
            if ball.init(config.PS2_SAMPLE_RATE, config.PS2_RESOLUTION, attempts=1):
                print("trackball: connected")
            t_retry = time.ticks_ms()
            feed()
        dx, dy = ball.read_delta()
        dy = -dy                               # PS/2: ball away = +y; HID: up = -y
        b = buttons()
        tdx, tdy = transform(dx, dy)
        # a report carries at most +-127 per axis: keep the rest for the
        # next tick instead of clipping it off (fast spins)
        rx += tdx; ry += tdy
        sx, sy = _clamp127(rx), _clamp127(ry)
        rx -= sx; ry -= sy
        if dx or dy or b != prev:
            _last_input = time.ticks_ms()
        if sx or sy or b != prev:
            if send(b, sx, sy) is False:       # host busy: keep it for next tick
                rx += sx; ry += sy
            else:
                prev = b
        meter.update(tdy)
        r = meter.take()
        if r:
            disp.swing(r[0], meter.best, r[1])
        await asyncio.sleep_ms(config.REPORT_MS)


# ---------- USB mode ----------
def run_usb():
    from usb_mouse import UsbMouse
    mouse = UsbMouse()
    disp.set(state="usb", charging=True, batt=battery_state())

    async def housekeeping():
        while True:
            await asyncio.sleep(5)
            if not usb_present():
                restart(hard=True)            # cable pulled -> Bluetooth, fresh radio
            b = battery_state()
            if abs(b - disp.batt) >= 10:      # charging reading wobbles: no redraw spam
                disp.set(batt=b)

    async def main():
        await asyncio.gather(input_task(mouse.send), disp.run(), housekeeping())
    asyncio.run(main())


# ---------- Bluetooth mode ----------
def run_ble():
    import aioble
    from hid_mouse import BleMouse
    try:
        import aioble.security
        aioble.security.load_secrets()       # bonding persists across reboots
    except Exception as e:
        print("bond store:", e)
    import blelog
    blelog.log("boot (reset cause %d)" % machine.reset_cause())
    mouse = BleMouse(config.DEVICE_NAME, getattr(config, "BLE_DEBUG", False))
    disp.set(state="pairing", charging=False, batt=battery_state())

    def stop_radio():
        try:
            aioble.stop()
        except Exception:
            pass

    async def ble_task():
        while True:
            try:
                await mouse.advertise_and_serve()    # returns on disconnect
            except Exception as e:
                print("ble:", e)
                await asyncio.sleep_ms(1000)

    async def housekeeping():
        t_batt = 0
        while True:
            await asyncio.sleep(1)
            if config.USB_MODE_ENABLED and usb_present():
                restart()                     # cable plugged -> USB mode
            if disp.idle_ms() >= config.IDLE_SLEEP_S * 1000:
                go_to_sleep(stop_radio)       # never returns
            disp.set(state="connected" if mouse.connected else "pairing")
            t_batt += 1
            if t_batt >= 60:
                t_batt = 0
                pct = battery_state()
                if abs(pct - disp.batt) >= 10:
                    disp.set(batt=pct)
                if mouse.connected:
                    mouse.set_battery(pct)

    async def main():
        await asyncio.gather(input_task(mouse.send), ble_task(), disp.run(), housekeeping())
    asyncio.run(main())


# ---------- boot ----------
if SAFE_MODE:
    ball.release_lines()
    tb_en.value(0)
    print("safe mode: LEFT+RIGHT held at boot -- firmware not started")
elif USB_MODE:
    run_usb()
else:
    run_ble()
