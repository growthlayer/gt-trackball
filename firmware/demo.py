# ============================================================
#  Bench demo: plays every screen and animation on the e-paper with
#  fake data -- nothing but the display needs to be wired.
#    mpremote cp config.py epd213.py art.py display.py demo.py :
#    mpremote run demo.py
# ============================================================

import asyncio
import time
from display import Display

d = Display()
d.idle_ms = lambda: 60_000          # pretend idle so ghost cleanup can run


async def script():
    d.set(batt=80)
    await asyncio.sleep(9)          # boot: ball drops onto the tee
    print("pairing (Bluetooth icon pulses)")
    d.set(state="pairing")
    await asyncio.sleep(8)
    print("connected (flag waves)")
    d.set(state="connected")
    await asyncio.sleep(6)
    best = 0
    for score in (62, 88, 75, 97):
        new = score > best
        best = max(best, score)
        print("swing", score, "NEW BEST" if new else "")
        d.swing(score, best, new)
        await asyncio.sleep(4)
    print("USB mode (charging)")
    d.set(state="usb", charging=True, note="")
    await asyncio.sleep(5)
    print("sleep screen (stays on with the power off)")
    d.set(charging=False, batt=65)
    d.sleep_screen()


async def main():
    t = time.ticks_ms()
    asyncio.create_task(d.run())
    await script()
    print("demo done in", time.ticks_diff(time.ticks_ms(), t) // 1000, "s")

asyncio.run(main())
