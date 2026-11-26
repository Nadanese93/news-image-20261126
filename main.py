"""The World - 26 November 2026.

Draws a newspaper front page summing up the world news of
Thursday, 26 November 2026, as a 1024x1024 PNG.

Python 3.13 standard library only: no network, no external fonts or
images. The PNG is encoded by hand (zlib), the text is drawn from an
own 5x7 bitmap font, and every pictogram is drawn from flat shapes.
Fully deterministic: two runs write byte-identical files.

Usage:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes out/entry.png. With MAKEFUN_OUTPUT_DIR unset, writes out/.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# Palette: paper white, black ink, one restrained deep-red accent.
PAPER = (253, 251, 245)
INK = (18, 18, 18)
RED = (163, 22, 33)
DARKRED = (120, 12, 22)
GREY = (105, 105, 100)
LIGHT = (240, 237, 228)
MIDGREY = (190, 187, 178)
DARKGREY = (70, 70, 68)
ORANGE = (230, 108, 20)
YELLOW = (244, 188, 38)
BLUE = (28, 78, 148)
SKY = (214, 228, 240)
GREEN = (34, 110, 60)

# ---------------------------------------------------------------- font
# Own 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit value
# with bit 4 the leftmost column. Only the characters the page needs.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ",": (0, 0, 0, 0, 0, 0x0C, 0x08),
    ".": (0, 0, 0, 0, 0, 0, 0x0C),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    ":": (0, 0, 0x0C, 0, 0, 0x0C, 0),
    ";": (0, 0, 0x0C, 0, 0, 0x0C, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
}


def text_width(text, scale):
    """Pixel width of text at the given font scale (1 px tracking)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for word in text.split(" "):
        if not lines:
            lines.append(word)
            continue
        trial = lines[-1] + " " + word
        if text_width(trial, scale) <= max_w:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]
                i += 3

    def hline(self, x0, x1, y, c):
        if x1 < x0:
            x0, x1 = x1, x0
        self.rect(x0, y, x1 - x0 + 1, 1, c)

    def vline(self, x, y0, y1, c):
        if y1 < y0:
            y0, y1 = y1, y0
        self.rect(x, y0, 1, y1 - y0 + 1, c)

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            f = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * (f ** 0.5)) if f > 0 else 0
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def tri(self, ax, ay, bx, by, cx, cy, c):
        """Filled triangle, scanline fill."""
        pts = sorted(((ax, ay), (bx, by), (cx, cy)), key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        if y0 == y2:
            return
        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / float(yb - ya)
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = edge_x(x0, y0, x1, y1, y)
                xb = edge_x(x0, y0, x2, y2, y)
            else:
                xa = edge_x(x1, y1, x2, y2, y)
                xb = edge_x(x0, y0, x2, y2, y)
            self.hline(int(round(min(xa, xb))), int(round(max(xa, xb))), y, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        """Bresenham line, thickened by stamping discs."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        r = max(0, w // 2)
        while True:
            if r:
                self.circle(x, y, r, c)
            else:
                self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def text(self, x, y, s, scale, c):
        """Draw uppercase text from the bitmap font at (x, y)."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centered(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes(cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png

# ---------------------------------------------------------------- scenes
# Each scene draws one flat pictogram inside the box (x, y, w, h).

def scene_fire(cv, x, y, w, h):
    """Lead: a burning fuel tanker on a highway."""
    cv.rect(x, y, w, h, SKY)
    # smoke puffs drifting off the flame
    for cx, cy, r in ((x + 62, y + 34, 15), (x + 92, y + 20, 19),
                      (x + w - 66, y + 40, 13), (x + w - 40, y + 24, 10)):
        cv.circle(cx, cy, r, MIDGREY)
    # flame: layered teardrop above the tank
    fx = x + w // 2 - 10
    fy = y + h - 158
    cv.ellipse(fx, fy, 54, 62, RED)
    cv.tri(fx - 34, fy - 34, fx + 34, fy - 34, fx, fy - 96, RED)
    cv.ellipse(fx, fy + 14, 36, 44, ORANGE)
    cv.tri(fx - 22, fy - 16, fx + 22, fy - 16, fx, fy - 62, ORANGE)
    cv.ellipse(fx, fy + 26, 19, 26, YELLOW)
    # highway
    road = y + h - 46
    cv.rect(x, road, w, 46, DARKGREY)
    for dx in range(0, w, 44):
        cv.rect(x + dx, road + 22, 24, 4, PAPER)
    # tanker: capsule tank, cab, wheels
    cv.rect(x + 34, road - 52, 186, 44, RED)
    cv.circle(x + 34, road - 30, 22, RED)
    cv.circle(x + 220, road - 30, 22, RED)
    cv.rect(x + 34, road - 52, 186, 8, (196, 60, 70))
    cv.rect(x + 228, road - 44, 62, 44, INK)
    cv.rect(x + 262, road - 38, 22, 16, SKY)
    for wx in (x + 66, x + 176, x + 256):
        cv.circle(wx, road + 2, 13, INK)
        cv.circle(wx, road + 2, 5, MIDGREY)


def scene_markets(cv, x, y, w, h):
    """Falling market chart with a red down arrow."""
    cv.rect(x, y, w, h, LIGHT)
    cv.vline(x + 12, y + 12, y + h - 14, INK)
    cv.hline(x + 12, x + w - 10, y + h - 14, INK)
    bars = (44, 36, 26, 16)
    for i, bh in enumerate(bars):
        bx = x + 22 + i * 20
        col = RED if i == 3 else MIDGREY
        cv.rect(bx, y + h - 14 - bh, 13, bh, col)
    cv.line(x + 16, y + 12, x + 40, y + 28, RED, 4)
    cv.line(x + 40, y + 28, x + 58, y + 24, RED, 4)
    cv.line(x + 58, y + 24, x + 86, y + 56, RED, 4)
    cv.tri(x + 86, y + 56, x + 74, y + 48, x + 92, y + 50, RED)


def scene_parade(cv, x, y, w, h):
    """Thanksgiving parade balloon with a basket."""
    cv.rect(x, y, w, h, LIGHT)
    cx, cy, r = x + w // 2, y + 30, 26
    cv.circle(cx, cy, r, RED)
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        if dx >= 3:
            cv.hline(cx - 3, cx + 3, cy + dy, PAPER)
    cv.line(cx - 14, cy + 20, cx - 6, y + 58, INK, 2)
    cv.line(cx + 14, cy + 20, cx + 6, y + 58, INK, 2)
    cv.rect(cx - 8, y + 58, 16, 11, DARKGREY)
    for dx in (-30, -14, 30):
        cv.circle(cx + dx, y + h - 8, 2, INK)


def scene_space(cv, x, y, w, h):
    """Rocket beside the Tiangong station module."""
    cv.rect(x, y, w, h, (24, 28, 44))
    for sx, sy in ((x + 12, y + 10), (x + 92, y + 12), (x + 52, y + 8),
                   (x + 8, y + 62), (x + 96, y + 66)):
        cv.circle(sx, sy, 2, PAPER)
    # rocket, left
    rx = x + 31
    cv.tri(rx - 11, y + 22, rx + 11, y + 22, rx, y + 6, RED)
    cv.rect(rx - 11, y + 22, 22, 30, PAPER)
    cv.frame(rx - 11, y + 22, 22, 30, INK, 1)
    cv.circle(rx, y + 33, 5, INK)
    cv.circle(rx, y + 33, 3, SKY)
    cv.tri(rx - 11, y + 52, rx - 23, y + 66, rx - 11, y + 60, RED)
    cv.tri(rx + 11, y + 52, rx + 23, y + 66, rx + 11, y + 60, RED)
    cv.tri(rx - 5, y + 52, rx + 5, y + 52, rx, y + 72, ORANGE)
    # station module, right
    cv.rect(x + 62, y + 24, 26, 12, MIDGREY)
    cv.frame(x + 62, y + 24, 26, 12, INK, 1)
    cv.rect(x + 50, y + 27, 12, 6, BLUE)
    cv.rect(x + 88, y + 27, 12, 6, BLUE)
    cv.rect(x + 72, y + 18, 2, 6, INK)
    cv.circle(x + 73, y + 17, 2, RED)


def scene_jet(cv, x, y, w, h):
    """Jet over a runway, with a blast at the far end."""
    cv.rect(x, y, w, h, LIGHT)
    # blast starburst
    bx, by = x + 84, y + 20
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, -1), (1, -1), (-1, 1)):
        cv.line(bx, by, bx + dx * 11, by + dy * 11, ORANGE, 3)
    cv.circle(bx, by, 6, YELLOW)
    # jet, side view
    cv.rect(x + 16, y + 36, 62, 10, INK)
    cv.tri(x + 78, y + 34, x + 96, y + 41, x + 78, y + 48, INK)
    cv.tri(x + 16, y + 36, x + 26, y + 20, x + 32, y + 36, INK)
    cv.tri(x + 42, y + 46, x + 56, y + 62, x + 62, y + 46, INK)
    cv.rect(x + 72, y + 38, 8, 5, SKY)
    # runway
    cv.hline(x + 8, x + w - 8, y + h - 14, GREY)
    cv.hline(x + 8, x + w - 8, y + h - 10, GREY)


def scene_flag(cv, x, y, w, h):
    """Flag on a pole beside a standing missile."""
    cv.rect(x, y, w, h, LIGHT)
    cv.vline(x + 20, y + 10, y + h - 12, INK)
    cv.vline(x + 21, y + 10, y + h - 12, INK)
    cv.rect(x + 23, y + 12, 52, 26, RED)
    cv.rect(x + 23, y + 12, 52, 5, BLUE)
    cv.rect(x + 23, y + 33, 52, 5, BLUE)
    cv.circle(x + 49, y + 25, 8, PAPER)
    cv.circle(x + 49, y + 25, 4, RED)
    # missile
    mx = x + 86
    cv.tri(mx - 5, y + 30, mx + 5, y + 30, mx, y + 16, RED)
    cv.rect(mx - 5, y + 30, 10, 30, GREY)
    cv.frame(mx - 5, y + 30, 10, 30, INK, 1)
    cv.tri(mx - 5, y + 60, mx - 11, y + 68, mx - 5, y + 64, INK)
    cv.tri(mx + 5, y + 60, mx + 11, y + 68, mx + 5, y + 64, INK)
    cv.tri(mx - 3, y + 60, mx + 3, y + 60, mx, y + 74, ORANGE)


# ---------------------------------------------------------------- stories
LEAD = {
    "kicker": "LEAD - CAIRO, EGYPT",
    "headline": ["TANKER FIRE", "KILLS 31"],
    "deck": ("A FUEL TANKER CRASHED AND IGNITED A MASSIVE FIRE "
             "ON A CAIRO HIGHWAY. AT LEAST 31 PEOPLE WERE KILLED."),
    "source": "SOURCE: BBC, 26 NOVEMBER 2026",
    "scene": scene_fire,
}

STORIES = [
    {
        "kicker": "MARKETS - NEW YORK",
        "headline": "MARKETS PLUNGE ON AI FEARS",
        "deck": ("NASDAQ DOWN ALMOST 4%. NEW TARIFFS HIT CHINA "
                 "AT NEARLY 45%."),
        "scene": scene_markets,
    },
    {
        "kicker": "NEW YORK - THANKSGIVING",
        "headline": "MACY'S PARADE POSTPONED",
        "deck": ("THE 100TH THANKSGIVING PARADE MOVES TO SATURDAY "
                 "AS WINDS BEAR DOWN."),
        "scene": scene_parade,
    },
    {
        "kicker": "SPACE - TIANGONG STATION",
        "headline": "PAKISTAN'S FIRST ASTRONAUT REACHES TIANGONG",
        "deck": ("MUHAMMAD ZEESHAN ALI IS THE FIRST FOREIGN ASTRONAUT "
                 "ON TIANGONG."),
        "scene": scene_space,
    },
    {
        "kicker": "WAR IN UKRAINE",
        "headline": "UKRAINE STRIKES RUSSIAN AIR BASE",
        "deck": ("KYIV SAYS FIVE PLANES WERE DAMAGED. RUSSIA HAS LOST "
                 "NEARLY 500,000."),
        "scene": scene_jet,
    },
    {
        "kicker": "KOREAN PENINSULA",
        "headline": "NORTH KOREA EXPELS SWISS DIPLOMAT",
        "deck": ("KIM JONG UN CALLS FOR WIDER DEPLOYMENT OF TACTICAL "
                 "NUCLEAR WEAPONS."),
        "scene": scene_flag,
    },
]

# IN BRIEF strip: three more verified stories from today, each one line
# (headline in red, one short fact clause in ink).
IN_BRIEF = [
    ("TRUMP BIRTHRIGHT ORDER BLOCKED",
     "SECOND JUDGE BLOCKS THE NEW ORDER."),
    ("ANDY TAYLOR DIES AT 65",
     "DURAN DURAN GUITARIST AND SONGWRITER."),
    ("HOUTHIS HIT SAUDI PORTS",
     "TWO PORTS STRUCK AFTER COALITION STRIKES."),
]


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    cv.frame(12, 12, W - 24, H - 24, INK, 3)

    # Masthead and dateline.
    cv.text_centered(W // 2, 34, "THE WORLD", 13, INK)
    cv.text_centered(W // 2, 130, "THURSDAY, 26 NOVEMBER 2026", 3, RED)
    cv.rect(32, 158, 960, 5, INK)
    cv.rect(32, 168, 960, 3, RED)

    # Lead story: text left, pictogram right.
    cv.text(32, 188, LEAD["kicker"], 2, RED)
    hy = 212
    for line in LEAD["headline"]:
        cv.text(32, hy, line, 5, INK)
        hy += 40
    deck_lines = wrap_text(LEAD["deck"], 2, 584)
    dy = 300
    for line in deck_lines:
        cv.text(32, dy, line, 2, INK)
        dy += 18
    cv.text(32, dy + 12, LEAD["source"], 2, GREY)
    cv.frame(648, 184, 344, 258, INK, 2)
    LEAD["scene"](cv, 650, 186, 340, 254)

    # Divider, then five stories in rows.
    cv.rect(32, 454, 960, 3, INK)
    y = 468
    for st in STORIES:
        cv.frame(32, y, 104, 86, INK, 2)
        st["scene"](cv, 34, y + 2, 100, 82)
        cv.text(152, y + 8, st["kicker"], 2, RED)
        head_lines = wrap_text(st["headline"], 3, 840)
        hy = y + 30
        for line in head_lines:
            cv.text(152, hy, line, 3, INK)
            hy += 25
        deck_lines = wrap_text(st["deck"], 2, 840)
        dy = y + 60
        for line in deck_lines:
            cv.text(152, dy, line, 2, INK)
            dy += 18
        y += 88

    # IN BRIEF strip: three more stories from today, one line each.
    # The sources line moves up onto the strip header row to make room.
    cv.rect(32, 918, 960, 3, INK)
    cv.text(32, 928, "IN BRIEF", 2, RED)
    src = "SOURCES: BBC - REUTERS - AP - THURSDAY, 26 NOVEMBER 2026"
    cv.text(992 - text_width(src, 2), 928, src, 2, GREY)
    by = 948
    for head, fact in IN_BRIEF:
        cv.rect(32, by + 4, 6, 6, RED)
        cx = cv.text(48, by, head, 2, RED)
        cv.text(cx, by, " - " + fact, 2, INK)
        by += 16
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
