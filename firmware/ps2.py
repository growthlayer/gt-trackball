# ============================================================
#  PS/2 mouse host for the trackball's own USB/PS2 board.
#
#  The trackball's X-sensor board (J1: +5V DATA CLOCK GND M R L)
#  decodes both optical encoders itself and speaks PS/2 on
#  DATA/CLOCK, so the Pico needs 2 signal wires, not 4 encoder
#  phases. The lines are open-collector: the Pico only ever pulls
#  them LOW or releases them (input + pull-up) -- never drives high.
#
#  Receive: a PIO state machine clocks in 11-bit frames and raises
#  an IRQ; the handler moves the bytes into a buffer, so frames keep
#  arriving while Python is busy (e.g. drawing the e-paper). A full
#  FIFO drops a frame instead of stalling, so the framing never
#  slips.
#  Send: host-to-device frames are clocked out by a viper loop on the
#  SIO registers (no Python IRQs in between). The receiver is paused
#  during a send -- idle bus, so it sits at the start of a frame -- and
#  the viper loop re-enables it via the PIO CTRL register the moment
#  the device finishes its ACK, well before the reply's first bit.
#
#  Verified on hardware: reset -> FA AA 00, enable -> FA, standard
#  3-byte packets (ID 00). Ball RIGHT = +X, ball AWAY = +Y.
# ============================================================

import time
import rp2
import micropython
from machine import Pin

_ACK = 0xFA


@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_RIGHT, fifo_join=rp2.PIO.JOIN_RX)
def _ps2rx():
    wrap_target()
    set(x, 10)               # 11 bits: start, 8 data, parity, stop
    label("bit")
    wait(1, pin, 1)          # count a falling edge only after CLOCK was
    wait(0, pin, 1)          # seen high (not our own inhibit), then sample
    in_(pins, 1)             # DATA
    jmp(x_dec, "bit")
    push(noblock)            # FIFO full -> drop this frame, never stall
    irq(rel(0))
    wrap()


# RP2350 SIO registers, as ptr32 word indexes from 0xD0000000
_GPIO_IN = const(1)       # 0x004
_OUT_CLR = const(8)       # 0x020
_OE_SET = const(14)       # 0x038
_OE_CLR = const(16)       # 0x040
_TIMEOUT = const(3000000) # polling loops (~170 ns each: ~0.5 s)
_PIO0_CTRL_SET = const(0x50202000)   # PIO0 CTRL, atomic-set alias


@micropython.viper
def _tx_bits(bits: int, dm: int, cm: int, sm_en: int) -> int:
    """Clock out the start bit, 8 data bits, parity and stop (bits 0..9,
    LSB first) as the device clocks them in, then wait out its ACK.
    The device samples the START bit on its first clock, so DATA stays
    low through that whole cycle; bit 0 goes out on the second clock
    (measured: releasing DATA on the first clock makes it abort). Open-collector:
    drive LOW or release, never high. Returns 1 on success, 0 on a
    timeout. Runs without yielding, so Python IRQs can't stall it.
    On success it re-enables the receiver SM (sm_en = CTRL enable bit)."""
    sio = ptr32(uint(0xD0000000))
    sio[_OE_CLR] = cm                 # release CLOCK: device starts clocking
    n = 0
    while sio[_GPIO_IN] & cm:         # first clock: start bit (DATA low)
        n += 1
        if n > _TIMEOUT:
            return 0
    n = 0
    while not (sio[_GPIO_IN] & cm):
        n += 1
        if n > _TIMEOUT:
            return 0
    i = 0
    while i < 10:
        n = 0
        while sio[_GPIO_IN] & cm:     # device pulls CLOCK low: set next bit
            n += 1
            if n > _TIMEOUT:
                return 0
        if (bits >> i) & 1:
            sio[_OE_CLR] = dm
        else:
            sio[_OUT_CLR] = dm
            sio[_OE_SET] = dm
        n = 0
        while not (sio[_GPIO_IN] & cm):   # device samples on the rising edge
            n += 1
            if n > _TIMEOUT:
                return 0
        i += 1
    sio[_OE_CLR] = dm
    n = 0
    while sio[_GPIO_IN] & dm:         # ACK: device pulls DATA low...
        n += 1
        if n > _TIMEOUT:
            return 0
    both = dm | cm
    n = 0
    while (sio[_GPIO_IN] & both) != both:   # ...clocks once, releases both
        n += 1
        if n > _TIMEOUT:
            return 0
    ptr32(uint(_PIO0_CTRL_SET))[0] = sm_en  # receiver back on for the reply
    return 1


def _odd_parity_ok(byte, parity):
    return (bin(byte).count("1") + parity) & 1 == 1


class PS2Mouse:
    def __init__(self, data_pin, clock_pin, sm_id=0):
        assert 0 <= sm_id < 4                     # PIO0 (see _tx_bits)
        self._dm = 1 << data_pin
        self._cm = 1 << clock_pin
        self._d = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        self._c = Pin(clock_pin, Pin.IN, Pin.PULL_UP)
        self._sm_id = sm_id
        self._sm = rp2.StateMachine(sm_id)
        self._rx = []            # received bytes, oldest first
        self._pkt = []           # partial movement packet
        self._bad = False        # a frame failed its checks -> resync
        self._skip = 0           # frames to drop (our own command, echoed)
        self.dropped = 0         # corrupt frames / rejected packets (debug)
        self.ok = False          # True once init() succeeded
        self._rx_start()

    def _rx_start(self):
        """(Re)start the receiver at the top of its program: bit count
        and PC reset, so it is aligned for the next frame."""
        self._sm.active(0)
        self._sm.init(_ps2rx, in_base=self._d)
        self._sm.irq(self._on_irq)
        self._sm.active(1)

    # ---- receive ----
    def _on_irq(self, sm):
        while sm.rx_fifo():
            f = sm.get() >> 21                   # 11-bit frame, bit0 = start
            if self._skip:
                self._skip -= 1                  # our own command's clocks
                continue
            if self._bad:
                continue                         # drop all until resync
            b = (f >> 1) & 0xFF
            if f & 1 or not (f >> 10) & 1 or not _odd_parity_ok(b, (f >> 9) & 1):
                # packet boundaries are lost: anything that follows would be
                # read shifted (a data byte taken as status = a wild jump)
                self._bad = True
                self._rx = []
                self.dropped += 1
                continue
            if len(self._rx) < 256:
                self._rx.append(b)

    def _resync(self):
        """Restart the receiver during an idle gap (CLOCK high >= 200 us)."""
        t0 = time.ticks_us()
        hi = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), t0) < 5000:
            if not self._c.value():
                hi = time.ticks_us()
            elif time.ticks_diff(time.ticks_us(), hi) >= 200:
                break
        self._rx_start()
        self._bad = False
        self._pkt = []

    def _take(self):
        rx, self._rx = self._rx, []
        return rx

    # ---- send ----
    def _low(self, p):
        p.init(Pin.OUT, value=0)

    def _release(self, p):
        p.init(Pin.IN, Pin.PULL_UP)

    def _send(self, byte):
        """One host-to-device frame; True if the device clocked all the bits
        in. Success is confirmed by the caller from the reply (FA)."""
        d, c = self._d, self._c
        parity = 1 ^ (bin(byte).count("1") & 1)
        self._sm.active(0)                        # idle bus: parked at frame start
        self._low(c)                              # inhibit
        time.sleep_us(150)
        self._low(d)                              # request to send
        ok = _tx_bits(byte | parity << 8 | 1 << 9, self._dm, self._cm,
                      1 << self._sm_id)
        self._release(d)
        self._release(c)
        if not ok:                                # clock count unknown: realign
            self._rx_start()
        return bool(ok)

    def _expect(self, seq, timeout_ms):
        """Wait until the received bytes start with seq; True on match."""
        got = []
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            got += self._take()
            if len(got) >= len(seq):
                return got[:len(seq)] == list(seq)
            time.sleep_ms(1)
        return False

    def command(self, *data):
        """Send a command and its arguments; each byte must be ACKed (FA)."""
        for b in data:
            self._take()
            if not (self._send(b) and self._expect((_ACK,), 100)):
                return False
        return True

    # ---- public ----
    def init(self, sample_rate=None, resolution=None, attempts=3):
        """Reset, configure and enable streaming. Blocks up to ~2 s per
        attempt (the reset self-test takes a few hundred ms)."""
        self.ok = False
        for _ in range(attempts):
            self._take()
            if self._send(0xFF) and self._expect((_ACK, 0xAA, 0x00), 2000):
                break
            time.sleep_ms(100)
        else:
            return False
        self.command(0xE6)                           # scaling 1:1 (no accel)
        if sample_rate:
            self.command(0xF3, sample_rate)
        if resolution is not None:
            self.command(0xE8, resolution)
        self.ok = self.command(0xF4)                 # enable data reporting
        self._pkt = []
        self._take()
        return self.ok

    def read_delta(self):
        """Movement since the last call as (dx, dy), PS/2 convention
        (right = +x, ball away = +y). Also re-enables reporting if the
        trackball announces a fresh power-up (AA 00)."""
        if self._bad:
            self._resync()
            self._take()                              # nothing trustworthy
        pkt = self._pkt
        pkt += self._take()
        dx = dy = 0
        while len(pkt) >= 3:
            s = pkt[0]
            if s == 0xAA and pkt[1] == 0x00:          # device rebooted
                del pkt[:2]
                print("trackball: power-up (AA 00) seen, re-enabling reports")
                self.command(0xF4)
                continue
            # status byte: bit 3 always set; the board's own L/M/R inputs
            # (bits 0-2) are unwired, so always clear; overflow (bits 6-7)
            # can't happen at 200 Hz -- seen only when the stream is
            # misaligned. Anything else: slide one byte and try again.
            if s & 0xC7 or not s & 0x08:
                del pkt[0]
                self.dropped += 1
                continue
            x, y = pkt[1], pkt[2]
            del pkt[:3]
            x = x - 256 if s & 0x10 else x
            y = y - 256 if s & 0x20 else y
            dx += x
            dy += y
        self._pkt = pkt
        return dx, dy

    def release_lines(self):
        """Before cutting trackball power: stop receiving and drop the
        pull-ups so the Pico doesn't feed the unpowered chip through its
        DATA/CLOCK pins (measured ~0.9 V on its 5 V rail otherwise)."""
        self._sm.active(0)
        self._d.init(Pin.IN, None)
        self._c.init(Pin.IN, None)
        self.ok = False
