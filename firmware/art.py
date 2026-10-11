# ============================================================
#  1-bit pixel art and screen layouts for the e-paper.
#  Sprites are rows of text: '#' = black pixel, anything else = white.
#  All coordinates are landscape (250 x 122).
# ============================================================

BALL = (
    "....####....",
    "..##....##..",
    ".#........#.",
    ".#.#..#...#.",
    "#.......#..#",
    "#..#.#.....#",
    "#.......#..#",
    "#.#..#.....#",
    ".#.....#..#.",
    ".#..#.....#.",
    "..##....##..",
    "....####....",
)

TEE = (
    "##############",
    ".############.",
    "...########...",
    ".....####.....",
    ".....####.....",
    "......##......",
    "......##......",
    "......##......",
    "......##......",
    ".......#......",
)

FLAG_A = (          # cloth only; the pin is drawn as a bar
    "##..............",
    "######..........",
    "##########......",
    "##############..",
    "##########......",
    "######..........",
    "##..............",
)

FLAG_B = (          # waving
    "##...........##.",
    "######....######",
    "###############.",
    "#############...",
    "##########......",
    "######..........",
    "##..............",
)

BT = (
    ".....#.....",
    ".....##....",
    ".....#.#...",
    ".....#..#..",
    "#....#...#.",
    ".#...#..#..",
    "..#..#.#...",
    "...#.##....",
    "....##.....",
    "...#.##....",
    "..#..#.#...",
    ".#...#..#..",
    "#....#...#.",
    ".....#..#..",
    ".....#.#...",
    ".....##....",
    ".....#.....",
)

WAVES = (
    "#......",
    ".#...#.",
    "..#...#",
    "..#...#",
    "..#...#",
    "..#...#",
    "..#...#",
    ".#...#.",
    "#......",
)

MOON = (
    "......####......",
    "....#####.......",
    "...####.........",
    "..####..........",
    ".####...........",
    ".####...........",
    "####............",
    "####............",
    "####............",
    "####............",
    ".####...........",
    ".####...........",
    "..####..........",
    "...####.........",
    "....#####.......",
    "......####......",
)

STAR = (
    "..#..",
    "..#..",
    "#####",
    "..#..",
    "..#..",
)


def sprite(epd, rows, x, y, s=1):
    for j, row in enumerate(rows):
        i = row.find("#")
        n = len(row)
        while i >= 0:
            k = i
            while k < n and row[k] == "#":
                k += 1
            epd.fill_rect(x + i * s, y + j * s, (k - i) * s, s, 0)
            i = row.find("#", k)


def battery(epd, x, y, pct, charging=False):
    """22 x 11 battery outline + nub, filled to pct; bolt when charging."""
    epd.rect(x, y, 22, 11)
    epd.fill_rect(x + 22, y + 3, 2, 5)
    w = max(0, min(18, pct * 18 // 100))
    epd.fill_rect(x + 2, y + 2, w, 7)
    if charging:                            # white bolt over the fill
        for dx, dy, h in ((8, 1, 4), (9, 3, 3), (10, 5, 3), (11, 6, 4)):
            epd.fill_rect(x + dx, y + dy, 2, h, 1)


def conn_icon(epd, x, y, conn, wave=False):
    """Right-aligned-ish status icon: BT rune (+ waves) or a USB tag."""
    if conn == "usb":
        epd.rect(x - 6, y + 3, 28, 12)
        epd.text("USB", x - 3, y + 5)
    else:
        sprite(epd, BT, x + 4, y)
        if wave:
            sprite(epd, WAVES, x + 13, y + 4)


def green(epd, x0, x1, ground, flag_frame=0, ball=True):
    """Flag + ball on a tee, standing on a ground line."""
    epd.hline(x0, ground, x1 - x0)
    px = x1 - 36
    epd.fill_rect(px, ground - 58, 3, 58)            # pin
    sprite(epd, FLAG_B if flag_frame else FLAG_A, px, ground - 58, 2)
    epd.fill_rect(px - 6, ground, 15, 3)            # cup
    if ball:
        tx = x0 + 4
        sprite(epd, TEE, tx, ground - 20, 2)
        sprite(epd, BALL, tx + 2, ground - 44, 2)


STATE_TEXT = {
    "booting": "starting",
    "pairing": "pairing...",
    "connected": "BT connected",
    "usb": "USB wired",
}


def main_screen(epd, d, flag_frame=0, wave=False):
    """d: Display model (name, state, conn, batt, charging, last, best, note)."""
    epd.clear()
    epd.border()
    # top bar
    epd.text(d.name[:20], 6, 8)
    battery(epd, 220, 6, d.batt, d.charging)
    conn_icon(epd, 196, 2, "usb" if d.state == "usb" else "bt",
              wave or d.state == "connected")
    epd.hline(0, 22, 250)
    # swing meter
    epd.text("LAST SWING", 6, 28)
    val = "--" if d.last is None else str(min(d.last, 999))
    epd.text(val, 6, 42, 6)                          # 48 px digits
    epd.text(d.note or STATE_TEXT.get(d.state, d.state), 6, 106)
    # right column: the green + best
    epd.vline(158, 22, 98)
    green(epd, 160, 248, 86, flag_frame)
    epd.text("BEST", 166, 92)
    epd.text("--" if not d.best else str(min(d.best, 999)), 166, 102, 2)


def boot_frame(epd, step):
    """Ball drops onto the tee (steps 0..3), title appears on the last."""
    epd.clear()
    epd.border()
    ground = 70
    epd.hline(60, ground, 130)
    sprite(epd, TEE, 111, ground - 20, 2)
    ys = (4, 18, 32, ground - 20 - 24)
    sprite(epd, BALL, 113, ys[min(step, 3)], 2)
    if step >= 3:
        epd.text("GT TRACKBALL", 29, 84, 2)


def sleep_screen(epd, batt, name):
    epd.clear()
    epd.border()
    sprite(epd, MOON, 16, 14, 3)
    for sx, sy in ((80, 12), (130, 30), (62, 58)):
        sprite(epd, STAR, sx, sy)
    epd.text("z", 92, 50)
    epd.text("z", 102, 38, 2)
    epd.text("Z", 120, 18, 3)
    green(epd, 160, 248, 86)
    epd.text("sleeping", 16, 76, 2)
    epd.text("press a button", 16, 100)
    battery(epd, 166, 98, batt)
    epd.text("{}%".format(batt), 196, 100)
