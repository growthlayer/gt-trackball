# ============================================================
#  Display manager: owns the e-paper, runs as an asyncio task so the
#  mouse keeps working while the panel refreshes.
#
#  Other code only sets fields (set(), swing()); run() decides what
#  to redraw:
#    boot       ball drops onto the tee (1 full + 3 partial frames)
#    pairing    Bluetooth icon pulses for PAIR_ANIM_S, then holds still
#    connected  flag waves a few frames, then holds still
#    swing      LAST SWING / BEST update (one partial refresh)
#    ghosting   after GHOST_PARTIALS partial refreshes, one full refresh
#               as soon as the controller has been idle for GHOST_IDLE_S
#    sleep      sleep_screen(): full refresh, then panel deep sleep
#               (the picture stays on at zero power)
#  With no panel (init failed) every call is a harmless no-op.
# ============================================================

import time
import asyncio
import config
import art

try:
    from epd213 import EPD213
except Exception as e:
    print("e-ink driver unavailable:", e)
    EPD213 = None


class Display:
    def __init__(self, wdt=None):
        self.epd = None
        if EPD213:
            try:
                self.epd = EPD213(wdt=wdt)
            except Exception as e:
                print("e-ink init failed (continuing headless):", e)
        self.name = config.DEVICE_NAME
        self.state = "booting"
        self.batt = 0
        self.charging = False
        self.last = None
        self.best = 0
        self.note = ""
        self.idle_ms = lambda: 0          # main.py replaces this
        self._dirty = True
        self._partials = 0
        self._flag = 0
        self._wave = False

    # ---- called by the rest of the firmware ----
    def set(self, **kw):
        for k, v in kw.items():
            if getattr(self, k) != v:
                setattr(self, k, v)
                self._dirty = True

    def swing(self, score, best, new_best):
        self.last, self.best = score, best
        self.note = "NEW BEST!" if new_best else ""
        self._dirty = True

    def sleep_screen(self):
        """Blocking: draw the sleep scene, then put the panel to sleep."""
        if not self.epd:
            return
        try:
            art.sleep_screen(self.epd, self.batt, self.name)
            self.epd.show(full=True)
            self.epd.sleep()
        except Exception as e:
            print("display:", e)

    # ---- internals ----
    def _draw(self):
        art.main_screen(self.epd, self, self._flag, self._wave)

    async def _push(self, full=False):
        self._partials = 0 if full else self._partials + 1
        await self.epd.show_async(full)

    async def _boot(self):
        for step in range(4):
            art.boot_frame(self.epd, step)
            await self._push(full=(step == 0))
            await asyncio.sleep_ms(250)
        await asyncio.sleep_ms(1200)

    async def run(self):
        if not self.epd:
            return
        try:
            await self._boot()
            prev = None
            pair_t0 = t_anim = time.ticks_ms()
            while True:
                # never redraw while the ball is rolling: drawing + rotation
                # stall the input loop for tens of ms (a choppy backswing)
                if self.idle_ms() < config.DRAW_IDLE_MS:
                    await asyncio.sleep_ms(50)
                    continue
                now = time.ticks_ms()
                if self.state != prev:
                    prev = self.state
                    if self.state == "pairing":
                        pair_t0 = now
                    if self.state == "connected":        # flag waves
                        self._wave = False
                        for f in (1, 0, 1, 0):
                            self._flag = f
                            self._draw()
                            await self._push()
                            await asyncio.sleep_ms(300)
                        self._dirty = False
                if (self.state == "pairing"
                        and time.ticks_diff(now, pair_t0) < config.PAIR_ANIM_S * 1000
                        and time.ticks_diff(now, t_anim) > 1500):
                    self._wave = not self._wave
                    self._dirty = True
                    t_anim = now
                if self._dirty:
                    self._dirty = False
                    if self.state == "pairing" and time.ticks_diff(now, pair_t0) >= config.PAIR_ANIM_S * 1000:
                        self._wave = True               # hold the "searching" icon
                    self._draw()
                    await self._push()
                elif (self._partials >= config.GHOST_PARTIALS
                        and self.idle_ms() > config.GHOST_IDLE_S * 1000):
                    self._draw()
                    await self._push(full=True)
                await asyncio.sleep_ms(150)
        except Exception as e:                          # never take input down
            print("display task stopped:", e)
