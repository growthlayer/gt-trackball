# ============================================================
#  BLE HID mouse (HID-over-GATT / HOGP) for Pico 2 W.
#  Requires aioble:   mpremote mip install aioble
#
#  Presents a standard 3-button relative mouse. Windows/macOS/
#  Linux pair it like any Bluetooth mouse; TeknoParrot sees it
#  through "Windows Mouse Cursor" with no reconfiguration.
#
#  HID hosts insist on a bonded, encrypted link. The stock
#  MicroPython build for the Pico 2 W has pairing compiled out
#  (macOS's bluetoothd crashed on it); this needs the firmware built
#  with MICROPY_PY_BLUETOOTH_ENABLE_PAIRING_BONDING -- see
#  firmware/README.md. Pairing is "Just Works" legacy pairing
#  (no passkey); BTstack re-derives the key from its identity keys,
#  so the bond survives the Pico's reboots.
# ============================================================

import struct
import asyncio
import bluetooth
import aioble
import aioble.security
from micropython import const
import blelog

_APPEARANCE_MOUSE = const(0x03C2)
_IO_NO_INPUT_OUTPUT = const(3)
_FLAG_READ_ENCRYPTED = const(0x0200)
_FLAG_WRITE_ENCRYPTED = const(0x1000)

_EVENTS = {1: "connect", 2: "disconnect", 3: "gatt write", 4: "gatt read",
           21: "mtu", 27: "conn params", 28: "encryption", 29: "get secret",
           30: "set secret", 31: "passkey action"}


def _log_irq(event, data):
    name = _EVENTS.get(event)
    if name:
        try:
            print("ble:", name, tuple(data) if event != 30 else "(key)")
        except Exception:
            print("ble:", name)
    # returns None so aioble's own handlers still run

_SVC_HID  = bluetooth.UUID(0x1812)
_SVC_DIS  = bluetooth.UUID(0x180A)
_SVC_BATT = bluetooth.UUID(0x180F)

_CHR_HID_INFO      = bluetooth.UUID(0x2A4A)
_CHR_REPORT_MAP    = bluetooth.UUID(0x2A4B)
_CHR_HID_CONTROL   = bluetooth.UUID(0x2A4C)
_CHR_REPORT        = bluetooth.UUID(0x2A4D)
_CHR_PROTOCOL_MODE = bluetooth.UUID(0x2A4E)
_CHR_PNP_ID        = bluetooth.UUID(0x2A50)
_CHR_MANUFACTURER  = bluetooth.UUID(0x2A29)
_CHR_MODEL_NUMBER  = bluetooth.UUID(0x2A24)
_CHR_FIRMWARE_REV  = bluetooth.UUID(0x2A26)
_CHR_BATT_LEVEL    = bluetooth.UUID(0x2A19)
_DSC_REPORT_REF    = bluetooth.UUID(0x2908)

# 3 buttons, X/Y rel 8-bit, wheel - report id 1
_REPORT_MAP = bytes((
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x02,        # Usage (Mouse)
    0xA1, 0x01,        # Collection (Application)
    0x85, 0x01,        #   Report ID (1)
    0x09, 0x01,        #   Usage (Pointer)
    0xA1, 0x00,        #   Collection (Physical)
    0x05, 0x09,        #     Usage Page (Buttons)
    0x19, 0x01, 0x29, 0x03,    # Usage Min 1 / Max 3
    0x15, 0x00, 0x25, 0x01,    # Logical 0..1
    0x95, 0x03, 0x75, 0x01,    # 3 bits
    0x81, 0x02,        #     Input (Data,Var,Abs)
    0x95, 0x01, 0x75, 0x05,    # 5 bit padding
    0x81, 0x03,        #     Input (Const)
    0x05, 0x01,        #     Usage Page (Generic Desktop)
    0x09, 0x30, 0x09, 0x31, 0x09, 0x38,   # X, Y, Wheel
    0x15, 0x81, 0x25, 0x7F,    # Logical -127..127
    0x75, 0x08, 0x95, 0x03,    # 3 x 8 bits
    0x81, 0x06,        #     Input (Data,Var,Rel)
    0xC0,              #   End Collection
    0xC0,              # End Collection
))


class BleMouse:
    def __init__(self, name, debug=False):
        self._name = name
        self._conn = None
        self._debug = debug
        self._sent = 0
        if debug:
            aioble.core.register_irq_handler(_log_irq, None)
        aioble.config(gap_name=name)          # GAP name = advertised name
        try:
            aioble.config(bond=True, le_secure=False, mitm=False,
                          io=_IO_NO_INPUT_OUTPUT)
            self._pairing = True
        except Exception as e:                # stock firmware: no pairing
            print("ble: pairing unsupported by this firmware:", e)
            self._pairing = False

        hid = aioble.Service(_SVC_HID)
        info = aioble.Characteristic(hid, _CHR_HID_INFO, read=True,
                                     initial=struct.pack("<HBB", 0x0111, 0x00, 0x02))
        rmap = aioble.Characteristic(hid, _CHR_REPORT_MAP, read=True,
                                     initial=_REPORT_MAP)
        ctrl = aioble.Characteristic(hid, _CHR_HID_CONTROL, write_no_response=True)
        mode = aioble.Characteristic(hid, _CHR_PROTOCOL_MODE, read=True,
                                     write_no_response=True, initial=b"\x01")
        self._report = aioble.Characteristic(hid, _CHR_REPORT,
                                             read=True, notify=True,
                                             initial=bytes(4))
        if self._pairing:
            # HID data needs an encrypted link: a host that hasn't paired
            # gets "insufficient encryption" and pairs -- that's what makes
            # macOS start pairing (it ignores a peripheral's pair request).
            for ch in (info, rmap, mode, self._report):
                ch.flags |= _FLAG_READ_ENCRYPTED
            for ch in (ctrl, mode):
                ch.flags |= _FLAG_WRITE_ENCRYPTED
        aioble.Descriptor(self._report, _DSC_REPORT_REF, read=True,
                          initial=struct.pack("<BB", 1, 1))  # id 1, input

        dis = aioble.Service(_SVC_DIS)
        # macOS reads these text fields after pairing (it crashed its
        # bluetoothd with only the PnP ID present) -- real mice have them.
        aioble.Characteristic(dis, _CHR_MANUFACTURER, read=True, initial=b"DIY")
        aioble.Characteristic(dis, _CHR_MODEL_NUMBER, read=True, initial=name.encode())
        aioble.Characteristic(dis, _CHR_FIRMWARE_REV, read=True, initial=b"1.0")
        # PnP ID: source=USB-IF, VID 0x2E8A (Raspberry Pi), PID 0x0001
        aioble.Characteristic(dis, _CHR_PNP_ID, read=True,
                              initial=struct.pack("<BHHH", 0x02, 0x2E8A,
                                                  0x0001, 0x0100))

        batt = aioble.Service(_SVC_BATT)
        self._batt = aioble.Characteristic(batt, _CHR_BATT_LEVEL,
                                           read=True, notify=True,
                                           initial=b"\x64")

        aioble.register_services(hid, dis, batt)

    @property
    def connected(self):
        # "connected" means a host can actually use the reports: with
        # pairing available that needs an encrypted link (Windows ignores
        # HID reports on an unencrypted one, while still showing a link).
        c = self._conn
        return c is not None and c.is_connected() and (c.encrypted or not self._pairing)

    async def advertise_and_serve(self):
        """One advertise/connect cycle; returns when disconnected."""
        async with await aioble.advertise(
                250_000,
                name=self._name,
                appearance=_APPEARANCE_MOUSE,
                services=[_SVC_HID]) as conn:
            self._conn = conn
            try:
                who = conn.device.addr_hex()
            except Exception:
                who = "?"
            blelog.log("connect " + who)
            if self._pairing:
                asyncio.create_task(self._secure(conn))
            await conn.disconnected(timeout_ms=None)
            self._conn = None
            blelog.log("disconnect")

    async def _secure(self, conn):
        """Ask the host to pair/encrypt (a bonded host re-encrypts with
        its stored key; a new one pairs "Just Works")."""
        await asyncio.sleep_ms(300)
        if not conn.is_connected():
            return
        if not conn.encrypted:
            try:
                await aioble.security.pair(conn, bond=True, le_secure=False,
                                           mitm=False, io=_IO_NO_INPUT_OUTPUT,
                                           timeout_ms=15000)
            except Exception as e:
                blelog.log("pair error " + repr(e))
        # a bonded host may also re-encrypt on its own: give it 5 s more
        for _ in range(50):
            if not conn.is_connected() or conn.encrypted:
                break
            await asyncio.sleep_ms(100)
        if not conn.is_connected():
            return
        blelog.log("link encrypted=%s bonded=%s" % (conn.encrypted, conn.bonded))
        if not conn.encrypted:
            # an unencrypted link looks connected but the host drops every
            # report. Hang up so the host reconnects and tries again; if its
            # stored key no longer matches, the screen stays on "pairing"
            # (fix: remove + re-add the device on the computer).
            blelog.log("not encrypted -> disconnecting so the host retries")
            try:
                await conn.disconnect()
            except Exception as e:
                blelog.log("disconnect error " + repr(e))

    def send(self, buttons, dx, dy, wheel=0):
        if not self.connected:
            return
        clamp = lambda v: -127 if v < -127 else (127 if v > 127 else v)
        payload = struct.pack("<Bbbb", buttons & 0x07,
                              clamp(dx), clamp(dy), clamp(wheel))
        # notify() sends to the connected host directly. write(send_update=True)
        # only reaches hosts whose notification subscription (CCCD) the stack
        # remembers -- and that is lost whenever the Pico reboots (every
        # sleep/wake). macOS re-subscribes on each reconnect, but Windows
        # assumes a bonded device remembered it, so it got nothing.
        try:
            self._report.write(payload)
            self._report.notify(self._conn, payload)
            if self._debug:
                self._sent += 1
                if self._sent in (1, 10, 100, 1000):
                    print("ble: report", self._sent, "sent, encrypted=%s" % self._conn.encrypted)
        except Exception as e:
            if self._debug:
                print("ble: report send failed:", repr(e))
            # otherwise: disconnect race - next loop notices

    def set_battery(self, percent):
        v = bytes((max(0, min(100, percent)),))
        try:
            self._batt.write(v)
            if self.connected:
                self._batt.notify(self._conn, v)
        except Exception:
            pass
