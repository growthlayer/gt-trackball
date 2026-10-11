# ============================================================
#  Swing meter: turns trackball motion into a Golden Tee style
#  "swing power" number.
#
#  A swing starts when the ball rolls FORWARD faster than
#  SWING_START_CPS (counts per second) and ends after SWING_END_MS
#  below that speed. Its score is the peak forward speed scaled by
#  SWING_SCALE_NUM / SWING_SCALE_DEN. Every swing prints its raw peak
#  to the REPL so the scale can be calibrated (a hard drive ~ 100).
# ============================================================

import time
import config


class SwingMeter:
    def __init__(self):
        self.best = 0
        self._active = False
        self._peak = 0
        self._t_prev = time.ticks_ms()
        self._t_fast = 0
        self._result = None

    def update(self, dy):
        """Call every input tick with the (transformed) Y delta."""
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._t_prev) or 1
        self._t_prev = now
        v = dy * config.SWING_FORWARD * 1000 // dt      # forward counts/s
        if v >= config.SWING_START_CPS:
            if not self._active:
                self._active = True
                self._peak = 0
            if v > self._peak:
                self._peak = v
            self._t_fast = now
        elif self._active and time.ticks_diff(now, self._t_fast) > config.SWING_END_MS:
            self._active = False
            score = self._peak * config.SWING_SCALE_NUM // config.SWING_SCALE_DEN
            print("swing: peak", self._peak, "counts/s -> score", score)
            if score > 0:
                new_best = score > self.best
                if new_best:
                    self.best = score
                self._result = (score, new_best)

    def take(self):
        """(score, new_best) once per finished swing, else None."""
        r, self._result = self._result, None
        return r
