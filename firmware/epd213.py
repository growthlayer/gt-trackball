# ============================================================
#  Driver for the Waveshare 2.13inch e-Paper HAT V4 (SSD1680,
#  250 x 122 black/white). Verified on hardware 2026-09-24.
#
#  Drawing is LANDSCAPE (250 wide x 122 tall). The panel's RAM is
#  portrait, so show() rotates the landscape buffer into it; config
#  EPD_FLIP turns the picture 180 degrees to suit how it's mounted.
#
#  Two refresh kinds (sequences from Waveshare's epd2in13_V4 demo):
#    full     ~3 s, flashes black/white, clears ghosting
#    partial  ~0.6 s (measured), no flash -- used for animation frames and the
#             swing meter; do a full one every so often
#  show() blocks; show_async() lets other asyncio tasks (mouse input)
#  keep running while the panel is busy.
# ============================================================

import time
import framebuf
import micropython
from machine import Pin, SPI
import config

_W = 122          # panel width  (portrait native)
_H = 250          # panel height
_BPR = (_W + 7) // 8   # bytes per row (16: 128 px, the last 6 unused)
LW, LH = _H, _W        # landscape drawing size: 250 x 122

# bit-reverse lookup (landscape VLSB byte -> portrait HLSB byte)
_REV = bytearray(sum(((i >> k) & 1) << (7 - k) for k in range(8)) for i in range(256))


# portrait pixel (nx, ny) <- landscape pixel:
#   normal:  (249-ny, nx)            -> byte-reversed copy
#   flipped: (ny, 127-nx) (y0 = 6)   -> straight copy
@micropython.viper
def _rot_normal(src: ptr8, dst: ptr8, rev: ptr8):
    ny = 0
    while ny < 250:
        row = ny * 16
        x = 249 - ny
        b = 0
        while b < 16:
            dst[row + b] = rev[src[b * 250 + x]]
            b += 1
        ny += 1


@micropython.viper
def _rot_flip(src: ptr8, dst: ptr8):
    ny = 0
    while ny < 250:
        row = ny * 16
        b = 0
        while b < 16:
            dst[row + b] = src[(15 - b) * 250 + ny]
            b += 1
        ny += 1


class EPD213:
    def __init__(self, wdt=None):
        self._wdt = wdt
        self._spi = SPI(1, baudrate=4_000_000, sck=Pin(config.EPD_SCK),
                        mosi=Pin(config.EPD_MOSI))
        self._cs = Pin(config.EPD_CS, Pin.OUT, value=1)
        self._dc = Pin(config.EPD_DC, Pin.OUT, value=0)
        self._rst = Pin(config.EPD_RST, Pin.OUT, value=1)
        self._busy = Pin(config.EPD_BUSY, Pin.IN)
        self.buf = bytearray(_BPR * _H)          # portrait, sent to the panel
        # landscape canvas, 250 x 128 VLSB (16 pages); 6 rows are padding
        self._lbuf = bytearray(LW * _BPR)
        self.fb = framebuf.FrameBuffer(self._lbuf, LW, _BPR * 8, framebuf.MONO_VLSB)
        self._flip = getattr(config, "EPD_FLIP", False)
        # in the flipped mapping canvas rows 0..5 fall off the panel
        self.y0 = 6 if self._flip else 0
        self._asleep = True                      # forces a full refresh first

    # ---- low level ----
    def _cmd(self, c, data=None):
        self._dc(0); self._cs(0)
        self._spi.write(bytes((c,)))
        self._cs(1)
        if data:
            self._data(data)

    def _data(self, d):
        self._dc(1); self._cs(0)
        self._spi.write(d if isinstance(d, (bytes, bytearray)) else bytes(d))
        self._cs(1)

    def busy(self):
        return self._busy.value() == 1

    def _wait(self):
        t0 = time.ticks_ms()
        while self.busy():
            if self._wdt: self._wdt.feed()
            if time.ticks_diff(time.ticks_ms(), t0) > 10_000:
                break
            time.sleep_ms(10)

    def _init_panel(self):
        self._rst(0); time.sleep_ms(20)
        self._rst(1); time.sleep_ms(20)
        self._cmd(0x12)                     # SWRESET
        self._wait()
        self._config()
        self._wait()

    async def _init_panel_async(self):
        import asyncio
        self._rst(0); await asyncio.sleep_ms(20)
        self._rst(1); await asyncio.sleep_ms(20)
        self._cmd(0x12)
        await self._wait_async()
        self._config()
        await self._wait_async()

    async def _wait_async(self):
        import asyncio
        t0 = time.ticks_ms()
        while self.busy() and time.ticks_diff(time.ticks_ms(), t0) < 10_000:
            await asyncio.sleep_ms(10)

    def _config(self):
        self._cmd(0x01, (0xF9, 0x00, 0x00)) # driver output: 249 gates
        self._cmd(0x11, (0x03,))            # data entry: x+ y+
        self._cmd(0x44, (0x00, _BPR - 1))   # RAM x window
        self._cmd(0x45, (0x00, 0x00, 0xF9, 0x00))  # RAM y window
        self._cmd(0x3C, (0x05,))            # border waveform
        self._cmd(0x21, (0x00, 0x80))       # display update control
        self._cmd(0x18, (0x80,))            # internal temp sensor

    def _ram(self, reg):
        self._cmd(0x4E, (0x00,))
        self._cmd(0x4F, (0x00, 0x00))
        self._cmd(reg)
        self._data(self.buf)

    def _start(self, full, inited=False):
        """Send the frame and trigger the update; does not wait. A full
        refresh needs the panel re-initialised first (inited=True when
        the caller already did it)."""
        if self._flip:
            _rot_flip(self._lbuf, self.buf)
        else:
            _rot_normal(self._lbuf, self.buf, _REV)
        if full or self._asleep:
            if not inited:
                self._init_panel()
            self._ram(0x24)
            self._ram(0x26)                 # base image for later partials
            self._cmd(0x22, (0xF7,))
        else:
            self._rst(0); time.sleep_ms(1); self._rst(1)
            self._cmd(0x3C, (0x80,))
            self._cmd(0x01, (0xF9, 0x00, 0x00))
            self._cmd(0x11, (0x03,))
            self._cmd(0x44, (0x00, _BPR - 1))
            self._cmd(0x45, (0x00, 0x00, 0xF9, 0x00))
            self._ram(0x24)
            self._cmd(0x22, (0xFF,))        # partial update
        self._cmd(0x20)
        self._asleep = False

    # ---- public ----
    def show(self, full=True):
        if not self._asleep:                # BUSY stays high in deep sleep
            self._wait()                    # finish any update in flight
        self._start(full)
        self._wait()

    async def show_async(self, full=False):
        """Like show(), but every wait yields to other asyncio tasks."""
        if not self._asleep:                # BUSY stays high in deep sleep
            await self._wait_async()        # previous update still running?
        inited = False
        if full or self._asleep:
            await self._init_panel_async()
            inited = True
        self._start(full, inited)
        await self._wait_async()

    def sleep(self):
        """Deep sleep: the picture stays on screen at zero power."""
        self._cmd(0x10, (0x01,))
        self._asleep = True

    # ---- drawing helpers (landscape coords, 250 x 122; black = 0) ----
    def clear(self):
        self.fb.fill(1)                     # 1 = white

    def fill_rect(self, x, y, w, h, c=0):
        self.fb.fill_rect(x, y + self.y0, w, h, c)

    def rect(self, x, y, w, h, c=0):
        self.fb.rect(x, y + self.y0, w, h, c)

    def hline(self, x, y, w, c=0):
        self.fb.hline(x, y + self.y0, w, c)

    def vline(self, x, y, h, c=0):
        self.fb.vline(x, y + self.y0, h, c)

    def text(self, txt, x, y, scale=1, c=0):
        """8 px font, optionally scaled up (2 = 16 px, 6 = 48 px)."""
        y += self.y0
        if scale == 1:
            self.fb.text(txt, x, y, c)
            return
        w = len(txt) * 8
        tmp = bytearray(w)                  # one 8-px-tall VLSB row
        t = framebuf.FrameBuffer(tmp, w, 8, framebuf.MONO_VLSB)
        t.text(txt, 0, 0, 1)
        for cx in range(w):
            col = tmp[cx]
            if col:
                for cy in range(8):
                    if col >> cy & 1:
                        self.fb.fill_rect(x + cx * scale, y + cy * scale, scale, scale, c)

    def border(self, t=2):
        """Outline the whole visible area -- makes centering the panel in
        the deck window easy."""
        for i in range(t):
            self.fb.rect(i, self.y0 + i, LW - 2 * i, LH - 2 * i, 0)


def status_screen(epd, state, batt_pct, name):
    """Plain text screen (bring-up test)."""
    epd.clear()
    epd.border()
    epd.text(name[:29], 6, 6)
    epd.hline(0, 18, LW)
    epd.text(state[:10], 6, 32, 3)          # 24 px, up to 10 chars
    epd.text("batt {:3d}%".format(batt_pct), 6, 84, 2)
    epd.show()
