# PC setup — Golden Tee Live (TeknoParrot) and RetroBat

Optional. The controller is a standard mouse, so it works in any game
without this. These steps are what made **Golden Tee Live 2018 / 2019
under TeknoParrot, launched from RetroBat** play properly. Tested on
Windows 11 with a 4K 120 Hz TV and a soundbar — tune the numbers to taste.

`<RetroBat>` below means your RetroBat folder (e.g. `C:\RetroBat`).

## 1. Windows: turn off mouse acceleration

Settings → Bluetooth & devices → Mouse → **Additional mouse settings** →
**Pointer Options** → untick **Enhance pointer precision** → OK.

TeknoParrot reads the trackball through the Windows cursor; with
acceleration on, a slow backswing gets shrunk and feels choppy. Pointer
speed can stay wherever you like it — step 2 sets the in-game speed.

## 2. TeknoParrot: Golden Tee settings

Open TeknoParrot → Golden Tee Live 2019 (and 2018) → **Game settings**:

| Setting | Value | Why |
|---|---|---|
| Input API | MergedInput | |
| Trackball Sensitivity X (left/right, aiming) | **15** | aiming wants to be slower than the swing |
| Trackball Sensitivity Y (forward/back, swing) | **28** | |
| Custom Resolution | **on**, set to your desktop resolution (e.g. 3840 × 2160) | otherwise the game switches the display mode on launch; on HDMI TVs with a soundbar that can drop the audio or make it cut in and out |

Then **Controller setup** (RawInput section):

| Golden Tee input | Bind to |
|---|---|
| TrackBall | Windows Mouse Cursor |
| Start | trackball **middle** button (MENU) |
| Left, Switch Club Left | trackball **left** button |
| Right, Switch Club Right | trackball **right** button |

Bind the buttons by clicking each field and pressing the controller's
button. Lower sensitivity = slower; change one axis at a time, then quit
and relaunch the game (TeknoParrot reads settings at launch).

### Why the buttons need step 3

TeknoParrot binds mouse **buttons** to one specific device and won't
accept "any mouse" for them, and the controller is a different device
over USB than over Bluetooth. So bindings made over Bluetooth do nothing
when it's plugged in, and vice versa. The script in step 3 fixes that
automatically.

## 3. retrobat-trackball.ahk (AutoHotkey v2)

1. Install [AutoHotkey v2](https://www.autohotkey.com/).
2. Put this folder somewhere permanent and run `retrobat-trackball.ahk`.
3. Start it with Windows: Win+R → `shell:startup` → add a shortcut to it.

What it does — only while RetroBat's menu is the active window:

- **Menu navigation:** roll = arrow keys, LEFT = select / launch,
  RIGHT = back, MENU = main menu. (RetroBat's menus don't take mouse
  input; these are RetroBat's default keyboard keys X / Z / Enter.)
- **Button bindings follow the connection:** every 2 s it checks whether
  the controller is on USB or Bluetooth and points the Golden Tee button
  bindings at it. Switch between USB and Bluetooth **in the menu**, not
  mid-game.
- **Launch splash:** brings Golden Tee in front of RetroBat's "launching"
  screen, which otherwise stays on top of the game.

While a game is running it does nothing. RetroBat is found in
`C:\`, `D:\`, `E:\`, `R:\` or Documents; edit `RETROBAT` at the top of the
script if yours is elsewhere. Golden Tee 2018/2019 profiles are the only
ones it touches (`TP_PROFILES`).

## Tried and rejected

- Doubling the trackball's resolution (PS/2 8 counts/mm): the in-game
  swing got worse. The controller uses the trackball's default.
- Binding the buttons to "Windows Mouse Cursor": TeknoParrot ignores it
  for buttons (works for the trackball axis only).
