; ============================================================
;  GT Trackball -> RetroBat menu navigation  (AutoHotkey v2)
;
;  RetroBat's menus (EmulationStation) only take keyboard/gamepad
;  input; the trackball is a mouse. While the RetroBat menu window is
;  in front this script turns it into menu controls:
;
;    roll up/down/left/right  ->  arrow keys
;    LEFT button              ->  X      (RetroBat "A": select / launch)
;    RIGHT button             ->  Z      (RetroBat "B": back)
;    MENU (middle) button     ->  Enter  (RetroBat "Start": main menu)
;
;  Keys come from <RetroBat>\emulationstation\.emulationstation\
;  es_input.cfg (default keyboard: a=x, b=z, start=Enter). As soon as a game
;  is in front (TeknoParrot etc.) the script does nothing, so Golden
;  Tee gets the real mouse and buttons. Any mouse counts while the menu
;  is in front -- clicking isn't used there anyway.
;
;  It also:
;   - brings Golden Tee in front of RetroBat's "launching" splash, and
;   - keeps the Golden Tee button bindings pointed at whichever way the
;     controller is connected (USB or Bluetooth), see SyncBindings().
;
;  Install: AutoHotkey v2, then put a shortcut to this file in the
;  Startup folder (Win+R, shell:startup). RetroBat is found in the usual
;  places (see RETROBAT below); set it yourself if yours lives elsewhere.
; ============================================================
#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent

MENU_EXE  := "ahk_exe emulationstation.exe"
STEP_PX   := 60     ; cursor travel per arrow press (bigger = slower)
MAX_STEPS := 3      ; at most this many presses per axis per tick
TICK_MS   := 15
; Game windows that open BEHIND RetroBat's "launching" splash and leave
; it on screen (Golden Tee under TeknoParrot = BudgieLoader). Each new
; window is brought to the front once; Alt+Tab still works after that.
GAME_EXES := ["BudgieLoader.exe"]
raised := Map()

; TeknoParrot binds buttons to ONE specific device (it won't take "any
; mouse" for buttons), and the controller is a different device over
; USB than over Bluetooth. So while the RetroBat menu is in front, the
; button bindings in these profiles are pointed at whichever connection
; is present right now -- before a game is launched.
RETROBAT := ""                         ; e.g. "D:\Games\RetroBat" -- blank = auto
if RETROBAT = ""
    for dir in ["C:\RetroBat", "D:\RetroBat", "E:\RetroBat", "R:\RetroBat", A_MyDocuments "\RetroBat"]
        if DirExist(dir) {
            RETROBAT := dir
            break
        }
TP_DIR := RETROBAT "\emulators\teknoparrot\UserProfiles\"
TP_PROFILES := [TP_DIR "GoldenTeeLive2018.xml", TP_DIR "GoldenTeeLive2019.xml"]
boundPath := ""

CoordMode "Mouse", "Screen"
accX := 0, accY := 0
SetTimer Poll, TICK_MS
SetTimer SyncBindings, 2000

Poll() {
    global accX, accY
    if WinActive(MENU_EXE) && RaiseGame()
        return
    if !WinActive(MENU_EXE) {
        accX := 0, accY := 0
        return
    }
    ; read how far the cursor moved since last tick, then park it back
    ; in the middle of the screen so it can never stick at an edge
    cx := A_ScreenWidth // 2, cy := A_ScreenHeight // 2
    MouseGetPos &mx, &my
    DllCall("SetCursorPos", "Int", cx, "Int", cy)
    accX += mx - cx, accY += my - cy
    ; one axis at a time: the bigger motion wins, the other is dropped
    if Abs(accX) >= Abs(accY)
        accY := 0, Steps(&accX, "{Right}", "{Left}")
    else
        accX := 0, Steps(&accY, "{Down}", "{Up}")
}

RaiseGame() {
    for exe in GAME_EXES {
        for hwnd in WinGetList("ahk_exe " exe) {
            if raised.Has(hwnd) || !(WinGetStyle(hwnd) & 0x10000000)   ; visible only
                continue
            raised[hwnd] := true
            WinActivate hwnd
            return true
        }
    }
    return false
}

; RawInput path of the trackball as TeknoParrot sees it: USB (VID_2E8A)
; preferred, else Bluetooth (VID&022e8a). "" when neither is connected.
TrackballPath() {
    sz := A_PtrSize * 2
    n := 0
    DllCall("GetRawInputDeviceList", "Ptr", 0, "UInt*", &n, "UInt", sz)
    if !n
        return ""
    list := Buffer(n * sz)
    got := DllCall("GetRawInputDeviceList", "Ptr", list, "UInt*", &n, "UInt", sz)
    usb := "", ble := ""
    loop got {
        off := (A_Index - 1) * sz
        if NumGet(list, off + A_PtrSize, "UInt") != 0        ; mice only
            continue
        h := NumGet(list, off, "Ptr")
        len := 0
        DllCall("GetRawInputDeviceInfoW", "Ptr", h, "UInt", 0x20000007, "Ptr", 0, "UInt*", &len)
        name := Buffer(len * 2 + 2, 0)
        DllCall("GetRawInputDeviceInfoW", "Ptr", h, "UInt", 0x20000007, "Ptr", name, "UInt*", &len)
        path := StrGet(name, "UTF-16")
        if InStr(path, "VID_2E8A")
            usb := path
        else if InStr(path, "VID&022e8a")
            ble := path
    }
    return usb != "" ? usb : ble
}

SyncBindings() {
    global boundPath
    if !WinActive(MENU_EXE)                 ; never while a game is running
        return
    p := TrackballPath()
    if p = "" || p = boundPath
        return
    repl := "${1}" StrReplace(StrReplace(p, "&", "&amp;"), "$", "$$") "${2}"
    pat := "(<DevicePath>)[^<]*(</DevicePath>\s*<DeviceType>Mouse</DeviceType>\s*<MouseButton>(?:Left|Right|Middle)Button</MouseButton>)"
    for f in TP_PROFILES {
        if !FileExist(f)
            continue
        xml := FileRead(f, "UTF-8")
        new := RegExReplace(xml, pat, repl)
        if new != xml {
            fh := FileOpen(f, "w", "UTF-8")
            fh.Write(new)
            fh.Close()
        }
    }
    boundPath := p
}

Steps(&acc, posKey, negKey) {
    n := 0
    while Abs(acc) >= STEP_PX && n < MAX_STEPS {
        Send acc > 0 ? posKey : negKey
        acc += acc > 0 ? -STEP_PX : STEP_PX
        n++
    }
    if n = MAX_STEPS
        acc := 0            ; flick: don't keep scrolling after the ball stops
}

#HotIf WinActive(MENU_EXE)
*LButton::Send "{x down}"
*LButton up::Send "{x up}"
*RButton::Send "{z down}"
*RButton up::Send "{z up}"
*MButton::Send "{Enter down}"
*MButton up::Send "{Enter up}"
#HotIf
