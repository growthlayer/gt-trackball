# ============================================================
#  Small persistent log of Bluetooth events (connect, encryption,
#  disconnect, boot). Kept in ble_log.txt on the Pico, last 60 lines,
#  so a problem can be read back afterwards over USB:
#      mpremote cat :ble_log.txt
#  Only called for rare events (never per report), so flash wear is
#  negligible. Never call it from an IRQ handler.
# ============================================================
import time

_PATH = "ble_log.txt"
_MAX = 60


def log(msg):
    line = "%7d %s" % (time.ticks_ms() // 1000, msg)
    print("ble:", msg)
    try:
        try:
            with open(_PATH) as f:
                lines = [l for l in f.read().split("\n") if l]
        except OSError:
            lines = []
        lines = lines[-(_MAX - 1):] + [line]
        with open(_PATH, "w") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass
