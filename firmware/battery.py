# ============================================================
#  Battery voltage.
#
#  The +5 V rail is boosted, so VSYS always reads ~5 V and says
#  nothing about the cell. Instead the cell (B+) feeds a 0-25 V
#  sensor module (30k / 7.5k) into GP26 (ADC0): the pin sees a fifth
#  of the cell voltage (max 0.84 V, safely under 3.3 V). Verify
#  against a multimeter on first bring-up and tweak BATT_DIVIDER.
# ============================================================

from machine import ADC
import config

_adc = ADC(config.PIN_BATT_ADC)


def read_battery():
    # average a few samples; the divider is high-impedance
    total = 0
    for _ in range(8):
        total += _adc.read_u16()
    return total / 8 * 3.3 / 65535 * config.BATT_DIVIDER


read_vsys = read_battery   # old name, kept for REPL habits


def percent():
    v = read_battery()
    lo, hi = config.BATTERY_EMPTY_V, config.BATTERY_FULL_V
    pct = int((v - lo) * 100 / (hi - lo))
    return max(0, min(100, pct)), v
