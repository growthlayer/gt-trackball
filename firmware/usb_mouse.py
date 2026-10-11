# ============================================================
#  USB HID mouse (wired mode) for the Pico 2 W.
#  Requires:   mpremote mip install usb-device-hid
#  Keeps the REPL/CDC alive (builtin_driver=True) so mpremote still
#  works while the mouse interface is active.
# ============================================================

import struct
import usb.device
from usb.device.hid import HIDInterface

# same 3-button relative mouse as the BLE profile, no report ID
_REPORT_DESC = bytes((
    0x05, 0x01, 0x09, 0x02, 0xA1, 0x01,
    0x09, 0x01, 0xA1, 0x00,
    0x05, 0x09, 0x19, 0x01, 0x29, 0x03,
    0x15, 0x00, 0x25, 0x01, 0x95, 0x03, 0x75, 0x01, 0x81, 0x02,
    0x95, 0x01, 0x75, 0x05, 0x81, 0x03,
    0x05, 0x01, 0x09, 0x30, 0x09, 0x31, 0x09, 0x38,
    0x15, 0x81, 0x25, 0x7F, 0x75, 0x08, 0x95, 0x03, 0x81, 0x06,
    0xC0, 0xC0,
))


class UsbMouse(HIDInterface):
    def __init__(self):
        super().__init__(_REPORT_DESC, interface_str="GT Trackball")
        usb.device.get().init(self, builtin_driver=True)

    @property
    def connected(self):
        return self.is_open()

    def send(self, buttons, dx, dy, wheel=0):
        """False when the report couldn't go out (host hasn't collected the
        previous one yet) -- the caller keeps the motion for the next tick."""
        if not self.is_open():
            return None
        clamp = lambda v: -127 if v < -127 else (127 if v > 127 else v)
        try:
            return bool(self.send_report(struct.pack("<Bbbb", buttons & 0x07,
                                         clamp(dx), clamp(dy), clamp(wheel))))
        except Exception:
            return False
