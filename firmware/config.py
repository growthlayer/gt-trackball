# ============================================================
#  Bluetooth Arcade Trackball - configuration
#  All pin assignments match ../wiring.svg
# ============================================================

# --- trackball: PS/2 from its own USB/PS2 board (connector J1:
#     +5V DATA CLOCK GND M R L). The board decodes both encoders; the
#     Pico is the PS/2 host. Open-collector lines, internal pull-ups. ---
PIN_PS2_DATA  = 2     # J1 DATA
PIN_PS2_CLOCK = 3     # J1 CLOCK
PS2_SAMPLE_RATE = 200 # reports/s (10..200); smaller per-report deltas
PS2_RESOLUTION  = None  # None = trackball default; 0..3 = 1/2/4/8 counts/mm

# --- buttons: lit 3-wire harnesses, identified by plug position
#     (latch toward you, wires down, 1-2-3 left to right):
#       pin 2 = switch -> its own GPIO (pull-up)
#       pin 3 = LED+ and switch common -> PIN_BTN_COMMON (all three)
#       pin 1 = LED-   -> GND (all three)
#     The common is held HIGH to light the LEDs (dim at 3.3 V) and
#     pulled LOW for BTN_STROBE_US to read the buttons: a pressed
#     switch then pulls its GPIO low. Nothing on the buttons sees 5 V. ---
PIN_BTN_LEFT   = 4
PIN_BTN_RIGHT  = 5
PIN_BTN_MIDDLE = 6   # "menu" button -> HID middle click
PIN_BTN_COMMON = 7
BTN_STROBE_US  = 20
BUTTON_LEDS    = True  # False = button LEDs stay off

# --- trackball power MOSFET (high = trackball on). Gates the WHOLE
#     trackball 5 V feed: its USB/PS2 board, encoder IR LEDs and the
#     RGB string. This is what makes sleep possible. ---
PIN_TRACKBALL_EN = 22

# --- e-ink display (Raspberry Pi form-factor 2.13inch e-Paper HAT,
#     wired via its 8-pin JST connector -- see README.md) ---
EPD_SCK  = 10
EPD_MOSI = 11
EPD_CS   = 9
EPD_DC   = 8
EPD_RST  = 12
EPD_BUSY = 13
EPD_FLIP = True     # True turns the picture 180 degrees (mounting)

# --- behaviour ---
DEVICE_NAME     = "GT Trackball"
REPORT_MS       = 10        # HID report interval when active (100 Hz)
INVERT_X        = False     # flip if cursor moves the wrong way
INVERT_Y        = False
SWAP_XY         = False     # if axes are crossed
SCALE_NUM       = 1         # movement scaling: delta * NUM // DEN
SCALE_DEN       = 1

# USB: when a cable is plugged in (VBUS present) the controller boots
# as a USB HID mouse instead of Bluetooth. Plug/unplug -> reboot.
USB_MODE_ENABLED = True
BLE_DEBUG        = False    # print Bluetooth events (connect, pairing...) on the USB REPL

# --- sleep (there is no power switch; this is the "off") ---
IDLE_SLEEP_S     = 300      # sleep after 5 min without input
                            # wake = any button (the trackball is unpowered
                            # in sleep; a PS/2 restart takes ~0.4 s, too
                            # costly to poll for ball movement)
SLEEP_CHUNK_MS   = 900      # lightsleep slice (must stay < WDT timeout)
WDT_TIMEOUT_MS   = 8000     # watchdog: a hung firmware reboots instead
                            # of draining the battery

# --- e-paper animation / refresh ---
DRAW_IDLE_MS    = 300       # screen only redraws once the ball has been still this long
PAIR_ANIM_S     = 20        # pulse the Bluetooth icon this long, then hold
GHOST_PARTIALS  = 30        # partial refreshes before a cleaning full one...
GHOST_IDLE_S    = 20        # ...done once the controller is idle this long

# --- swing meter (see swing.py) ---
SWING_FORWARD   = -1        # sign of Y for a forward swing (cursor up = -1)
SWING_START_CPS = 1500      # forward speed that counts as a swing, counts/s
SWING_END_MS    = 150       # swing ends after this long below that speed
SWING_SCALE_NUM = 1         # score = peak counts/s * NUM // DEN;
SWING_SCALE_DEN = 100       #   calibrate so a hard drive reads ~100
# --- battery sense: 0-25 V sensor module (30k / 7.5k, divides by 5) ---
# B+ -> sensor VCC, sensor S -> GP26, sensor - -> GND
PIN_BATT_ADC    = 26
BATT_DIVIDER    = 4.95      # nominal 5.0; 4.95 matched a meter (3.95 V)
BATTERY_FULL_V  = 4.10
BATTERY_EMPTY_V = 3.30
