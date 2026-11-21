#!/usr/bin/env python3
"""Render the one-page world-news summary for Friday 20 November 2026.

The picture is painted entirely with Pillow primitives: a dark masthead,
six large feature cards, twenty-nine small entries arranged in three
columns, tiny hand-drawn pictograms, and a footer that names the sources.
Nothing photographic is used anywhere.
"""

from PIL import Image, ImageDraw, ImageFont

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_PNG = os.path.join(BASE_DIR, "entry.png")

IMG_W = 1024
IMG_H = 1024
SIDE = 28
COL_GAP = 16

FONT_FOLDER = "/usr/share/fonts/truetype/dejavu"

NAVY = (15, 36, 64)
GOLD = (201, 162, 39)
RED = (210, 59, 44)
CREAM = (246, 240, 225)
WHITE = (255, 255, 255)
INK = (22, 30, 40)
GRAY = (96, 102, 110)
EDGE = (226, 220, 205)
HOT = (230, 126, 34)  # flame orange accent

REGIONS = {
    "EUROPE": {"code": "EU", "color": (192, 57, 43)},
    "N. AMERICA": {"code": "NA", "color": (31, 58, 100)},
    "LATIN AMERICA": {"code": "LA", "color": (30, 138, 110)},
    "ASIA": {"code": "AS", "color": (125, 60, 152)},
    "MIDDLE EAST": {"code": "ME", "color": (140, 108, 58)},
    "AFRICA": {"code": "AF", "color": (214, 137, 16)},
    "GLOBAL": {"code": "GL", "color": (52, 73, 94)},
}
REGION_ORDER = ["EUROPE", "N. AMERICA", "LATIN AMERICA", "ASIA",
                "MIDDLE EAST", "AFRICA", "GLOBAL"]

# pictogram kind -> (ink color, disc tint)
STYLE = {
    "missile": ((192, 57, 43), (250, 229, 224)),
    "chart": ((31, 58, 100), (230, 237, 244)),
    "bitcoin": ((224, 122, 26), (252, 236, 205)),
    "probe": ((93, 109, 126), (236, 236, 240)),
    "seismo": ((30, 138, 110), (222, 241, 235)),
    "document": ((36, 113, 163), (226, 237, 248)),
    "shield": ((36, 113, 163), (226, 237, 248)),
    "flag": ((192, 57, 43), (250, 229, 224)),
    "leaf": ((34, 153, 84), (222, 241, 230)),
    "chip": ((31, 58, 100), (230, 237, 244)),
    "mic": ((44, 62, 80), (236, 236, 240)),
    "ballot": ((34, 153, 84), (222, 241, 230)),
    "flame": ((230, 126, 34), (252, 232, 205)),
    "pill": ((192, 57, 43), (250, 230, 236)),
    "scales": ((44, 62, 80), (236, 236, 240)),
    "rocket": ((192, 57, 43), (250, 229, 224)),
    "basketball": ((230, 126, 34), (252, 232, 205)),
    "building": ((52, 73, 94), (230, 237, 244)),
    "plane": ((36, 113, 163), (226, 237, 248)),
    "bottle": ((30, 138, 110), (222, 241, 235)),
    "gamepad": ((44, 62, 80), (236, 236, 240)),
    "gem": ((176, 132, 16), (252, 240, 205)),
    "coin": ((176, 132, 16), (252, 236, 205)),
}


def load_font(name, size):
    return ImageFont.truetype(os.path.join(FONT_FOLDER, name), size)


F_TITLE = load_font("DejaVuSans-Bold.ttf", 62)
F_KICK = load_font("DejaVuSans-Bold.ttf", 20)
F_PILL = load_font("DejaVuSans-Bold.ttf", 20)
F_STATS = load_font("DejaVuSans-Bold.ttf", 20)
F_REGION = load_font("DejaVuSans-Bold.ttf", 13)
F_HERO_HEAD = load_font("DejaVuSans-Bold.ttf", 20)
F_HERO_DET = load_font("DejaVuSans.ttf", 13)
F_SECTION = load_font("DejaVuSans-Bold.ttf", 20)
F_LEGEND = load_font("DejaVuSans-Bold.ttf", 9)
F_CHIP = load_font("DejaVuSans-Bold.ttf", 11)
F_ITEM_HEAD = load_font("DejaVuSans-Bold.ttf", 15)
F_ITEM_DET = load_font("DejaVuSans.ttf", 12)
F_FOOT = load_font("DejaVuSans.ttf", 13)

_glyph_fonts = {}


def glyph_font(size):
    if size not in _glyph_fonts:
        _glyph_fonts[size] = load_font("DejaVuSans-Bold.ttf", size)
    return _glyph_fonts[size]


def wrap_lines(text, fnt, width, limit):
    """Greedy word wrap to at most `limit` lines of `width` pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if fnt.getlength(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            if len(lines) >= limit:
                return lines
            current = word
    if current and len(lines) < limit:
        lines.append(current)
    return lines


def wrap_first(text, fnt, first_width, rest_width, limit=2):
    """Wrap where the first line is narrower (a region chip sits on it)."""
    words = text.split()
    lines = []
    current = ""
    width = first_width
    for word in words:
        trial = f"{current} {word}".strip()
        if fnt.getlength(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            if len(lines) >= limit:
                return lines
            current = word
            width = rest_width
    if current and len(lines) < limit:
        lines.append(current)
    return lines


def squeeze(text, fnt, width):
    """Shorten one line with an ellipsis until it fits `width` pixels."""
    if fnt.getlength(text) <= width:
        return text
    cut = text
    while cut and fnt.getlength(cut + "…") > width:
        cut = cut[:-1]
    return cut + "…"


def paint_glyph(d, kind, cx, cy, r, ink):
    """Draw one small pictogram centred on (cx, cy) inside radius r."""
    w = max(2, int(r / 7))
    thin = max(1, w - 1)
    if kind == "missile":
        d.polygon([(cx, cy - r), (cx - 0.32 * r, cy - 0.30 * r),
                   (cx + 0.32 * r, cy - 0.30 * r)], fill=ink)
        d.rectangle([cx - 0.32 * r, cy - 0.30 * r, cx + 0.32 * r, cy + 0.45 * r], fill=ink)
        d.polygon([(cx - 0.32 * r, cy + 0.45 * r), (cx - 0.65 * r, cy + 0.78 * r),
                   (cx - 0.32 * r, cy + 0.60 * r)], fill=ink)
        d.polygon([(cx + 0.32 * r, cy + 0.45 * r), (cx + 0.65 * r, cy + 0.78 * r),
                   (cx + 0.32 * r, cy + 0.60 * r)], fill=ink)
        d.polygon([(cx - 0.18 * r, cy + 0.45 * r), (cx + 0.18 * r, cy + 0.45 * r),
                   (cx, cy + 0.95 * r)], fill=HOT)
    elif kind == "chart":
        d.line([(cx - 0.70 * r, cy + 0.60 * r), (cx - 0.70 * r, cy - 0.60 * r)], fill=ink, width=w)
        d.line([(cx - 0.70 * r, cy + 0.60 * r), (cx + 0.75 * r, cy + 0.60 * r)], fill=ink, width=w)
        pts = [(cx - 0.58 * r, cy - 0.28 * r), (cx - 0.20 * r, cy + 0.12 * r),
               (cx + 0.15 * r, cy - 0.12 * r), (cx + 0.60 * r, cy + 0.42 * r)]
        d.line(pts, fill=ink, width=w, joint="curve")
        d.polygon([(cx + 0.60 * r, cy + 0.42 * r), (cx + 0.32 * r, cy + 0.34 * r),
                   (cx + 0.44 * r, cy + 0.62 * r)], fill=ink)
    elif kind == "bitcoin":
        d.ellipse([cx - 0.62 * r, cy - 0.62 * r, cx + 0.62 * r, cy + 0.62 * r],
                  outline=ink, width=w)
        d.text((cx, cy), "B", font=glyph_font(int(r * 1.05)), fill=ink, anchor="mm")
    elif kind == "coin":
        d.ellipse([cx - 0.62 * r, cy - 0.62 * r, cx + 0.62 * r, cy + 0.62 * r],
                  outline=ink, width=w)
        d.text((cx, cy), "€", font=glyph_font(int(r * 1.0)), fill=ink, anchor="mm")
    elif kind == "probe":
        d.ellipse([cx - 0.85 * r, cy - 0.32 * r, cx + 0.85 * r, cy + 0.32 * r],
                  outline=ink, width=w)
        d.ellipse([cx - 0.34 * r, cy - 0.34 * r, cx + 0.34 * r, cy + 0.34 * r], fill=ink)
    elif kind == "seismo":
        pts = [(cx - 0.80 * r, cy), (cx - 0.52 * r, cy), (cx - 0.36 * r, cy - 0.55 * r),
               (cx - 0.16 * r, cy + 0.55 * r), (cx + 0.04 * r, cy - 0.40 * r),
               (cx + 0.24 * r, cy + 0.28 * r), (cx + 0.40 * r, cy), (cx + 0.80 * r, cy)]
        d.line(pts, fill=ink, width=w, joint="curve")
    elif kind == "document":
        d.rounded_rectangle([cx - 0.45 * r, cy - 0.60 * r, cx + 0.45 * r, cy + 0.60 * r],
                            radius=int(r * 0.12), outline=ink, width=w)
        for dy in (-0.28, 0.0, 0.28):
            d.line([(cx - 0.28 * r, cy + dy * r), (cx + 0.28 * r, cy + dy * r)],
                   fill=ink, width=thin)
        d.ellipse([cx + 0.18 * r, cy + 0.22 * r, cx + 0.46 * r, cy + 0.50 * r], fill=HOT)
    elif kind == "shield":
        d.polygon([(cx, cy - 0.65 * r), (cx + 0.55 * r, cy - 0.40 * r),
                   (cx + 0.55 * r, cy + 0.10 * r), (cx, cy + 0.70 * r),
                   (cx - 0.55 * r, cy + 0.10 * r), (cx - 0.55 * r, cy - 0.40 * r)], fill=ink)
        d.line([(cx - 0.28 * r, cy + 0.02 * r), (cx - 0.08 * r, cy + 0.24 * r),
                (cx + 0.30 * r, cy - 0.24 * r)], fill=WHITE, width=w)
    elif kind == "flag":
        d.line([(cx - 0.30 * r, cy - 0.65 * r), (cx - 0.30 * r, cy + 0.70 * r)],
               fill=ink, width=w)
        d.polygon([(cx - 0.30 * r, cy - 0.65 * r), (cx + 0.68 * r, cy - 0.42 * r),
                   (cx - 0.30 * r, cy - 0.15 * r)], fill=ink)
    elif kind == "leaf":
        d.polygon([(cx, cy - 0.65 * r), (cx + 0.50 * r, cy - 0.08 * r),
                   (cx, cy + 0.65 * r), (cx - 0.50 * r, cy - 0.08 * r)], fill=ink)
        d.line([(cx, cy - 0.48 * r), (cx, cy + 0.55 * r)], fill=CREAM, width=thin)
    elif kind == "chip":
        d.rectangle([cx - 0.45 * r, cy - 0.45 * r, cx + 0.45 * r, cy + 0.45 * r],
                    outline=ink, width=w)
        d.rectangle([cx - 0.20 * r, cy - 0.20 * r, cx + 0.20 * r, cy + 0.20 * r], fill=ink)
        for s in (-0.22, 0.0, 0.22):
            d.line([(cx + s * r, cy - 0.45 * r), (cx + s * r, cy - 0.65 * r)],
                   fill=ink, width=thin)
            d.line([(cx + s * r, cy + 0.45 * r), (cx + s * r, cy + 0.65 * r)],
                   fill=ink, width=thin)
            d.line([(cx - 0.45 * r, cy + s * r), (cx - 0.65 * r, cy + s * r)],
                   fill=ink, width=thin)
            d.line([(cx + 0.45 * r, cy + s * r), (cx + 0.65 * r, cy + s * r)],
                   fill=ink, width=thin)
    elif kind == "mic":
        d.rounded_rectangle([cx - 0.26 * r, cy - 0.62 * r, cx + 0.26 * r, cy + 0.08 * r],
                            radius=int(r * 0.26), fill=ink)
        d.line([(cx - 0.26 * r, cy - 0.18 * r), (cx + 0.26 * r, cy - 0.18 * r)],
               fill=CREAM, width=thin)
        d.line([(cx - 0.26 * r, cy + 0.02 * r), (cx + 0.26 * r, cy + 0.02 * r)],
               fill=CREAM, width=thin)
        d.arc([cx - 0.46 * r, cy - 0.30 * r, cx + 0.46 * r, cy + 0.62 * r],
              0, 180, fill=ink, width=w)
        d.line([(cx, cy + 0.62 * r), (cx, cy + 0.82 * r)], fill=ink, width=w)
    elif kind == "ballot":
        d.rectangle([cx - 0.50 * r, cy - 0.50 * r, cx + 0.50 * r, cy + 0.50 * r],
                    outline=ink, width=w)
        d.line([(cx - 0.30 * r, cy + 0.04 * r), (cx - 0.08 * r, cy + 0.28 * r),
                (cx + 0.34 * r, cy - 0.28 * r)], fill=ink, width=w)
    elif kind == "flame":
        d.polygon([(cx, cy - 0.70 * r), (cx + 0.34 * r, cy - 0.12 * r),
                   (cx + 0.46 * r, cy + 0.22 * r), (cx + 0.20 * r, cy + 0.66 * r),
                   (cx - 0.20 * r, cy + 0.66 * r), (cx - 0.46 * r, cy + 0.22 * r),
                   (cx - 0.34 * r, cy - 0.12 * r)], fill=ink)
        d.polygon([(cx, cy + 0.05 * r), (cx + 0.20 * r, cy + 0.30 * r),
                   (cx, cy + 0.55 * r), (cx - 0.20 * r, cy + 0.30 * r)], fill=HOT)
    elif kind == "pill":
        d.rounded_rectangle([cx - 0.60 * r, cy - 0.28 * r, cx + 0.60 * r, cy + 0.28 * r],
                            radius=int(r * 0.28), outline=ink, width=w)
        d.line([(cx, cy - 0.28 * r), (cx, cy + 0.28 * r)], fill=ink, width=thin)
        d.ellipse([cx - 0.52 * r, cy - 0.20 * r, cx - 0.08 * r, cy + 0.20 * r], fill=ink)
    elif kind == "scales":
        d.line([(cx, cy - 0.60 * r), (cx, cy + 0.62 * r)], fill=ink, width=w)
        d.line([(cx - 0.62 * r, cy - 0.44 * r), (cx + 0.62 * r, cy - 0.44 * r)],
               fill=ink, width=w)
        for s in (-1, 1):
            px = cx + s * 0.62 * r
            d.line([(px, cy - 0.44 * r), (px - 0.16 * r, cy + 0.12 * r)],
                   fill=ink, width=thin)
            d.line([(px, cy - 0.44 * r), (px + 0.16 * r, cy + 0.12 * r)],
                   fill=ink, width=thin)
            d.arc([px - 0.24 * r, cy - 0.02 * r, px + 0.24 * r, cy + 0.34 * r],
                  0, 180, fill=ink, width=thin)
        d.line([(cx - 0.20 * r, cy + 0.62 * r), (cx + 0.20 * r, cy + 0.62 * r)],
               fill=ink, width=w)
    elif kind == "rocket":
        d.polygon([(cx, cy - 0.68 * r), (cx - 0.30 * r, cy - 0.20 * r),
                   (cx + 0.30 * r, cy - 0.20 * r)], fill=ink)
        d.rectangle([cx - 0.30 * r, cy - 0.20 * r, cx + 0.30 * r, cy + 0.42 * r], fill=ink)
        d.ellipse([cx - 0.13 * r, cy - 0.08 * r, cx + 0.13 * r, cy + 0.18 * r], fill=CREAM)
        d.polygon([(cx - 0.30 * r, cy + 0.42 * r), (cx - 0.58 * r, cy + 0.68 * r),
                   (cx - 0.30 * r, cy + 0.58 * r)], fill=ink)
        d.polygon([(cx + 0.30 * r, cy + 0.42 * r), (cx + 0.58 * r, cy + 0.68 * r),
                   (cx + 0.30 * r, cy + 0.58 * r)], fill=ink)
        d.polygon([(cx - 0.16 * r, cy + 0.42 * r), (cx + 0.16 * r, cy + 0.42 * r),
                   (cx, cy + 0.92 * r)], fill=HOT)
    elif kind == "basketball":
        d.ellipse([cx - 0.62 * r, cy - 0.62 * r, cx + 0.62 * r, cy + 0.62 * r],
                  outline=ink, width=w)
        d.line([(cx, cy - 0.62 * r), (cx, cy + 0.62 * r)], fill=ink, width=thin)
        d.line([(cx - 0.62 * r, cy), (cx + 0.62 * r, cy)], fill=ink, width=thin)
        d.arc([cx - 0.95 * r, cy - 0.45 * r, cx + 0.05 * r, cy + 0.45 * r],
              300, 60, fill=ink, width=thin)
        d.arc([cx - 0.05 * r, cy - 0.45 * r, cx + 0.95 * r, cy + 0.45 * r],
              120, 240, fill=ink, width=thin)
    elif kind == "building":
        d.rectangle([cx - 0.40 * r, cy - 0.55 * r, cx + 0.40 * r, cy + 0.65 * r],
                    outline=ink, width=w)
        for row in range(4):
            for col in range(3):
                if row == 3 and col == 1:
                    continue  # the door lives here
                wx = cx - 0.28 * r + col * 0.28 * r
                wy = cy - 0.42 * r + row * 0.26 * r
                d.rectangle([wx, wy, wx + 0.12 * r, wy + 0.12 * r], fill=ink)
        d.rectangle([cx - 0.10 * r, cy + 0.38 * r, cx + 0.10 * r, cy + 0.65 * r], fill=ink)
    elif kind == "plane":
        d.polygon([(cx - 0.75 * r, cy + 0.18 * r), (cx + 0.75 * r, cy - 0.38 * r),
                   (cx + 0.12 * r, cy + 0.34 * r), (cx - 0.08 * r, cy + 0.04 * r)], fill=ink)
        d.polygon([(cx - 0.10 * r, cy + 0.10 * r), (cx + 0.30 * r, cy + 0.62 * r),
                   (cx + 0.02 * r, cy + 0.42 * r)], fill=ink)
    elif kind == "bottle":
        d.rectangle([cx - 0.16 * r, cy - 0.66 * r, cx + 0.16 * r, cy - 0.46 * r], fill=ink)
        d.rectangle([cx - 0.18 * r, cy - 0.46 * r, cx + 0.18 * r, cy - 0.20 * r],
                    outline=ink, width=thin)
        d.rounded_rectangle([cx - 0.40 * r, cy - 0.20 * r, cx + 0.40 * r, cy + 0.66 * r],
                            radius=int(r * 0.14), outline=ink, width=w)
        d.line([(cx - 0.40 * r, cy + 0.28 * r), (cx + 0.40 * r, cy + 0.28 * r)],
               fill=ink, width=thin)
    elif kind == "gamepad":
        d.rounded_rectangle([cx - 0.66 * r, cy - 0.36 * r, cx + 0.66 * r, cy + 0.36 * r],
                            radius=int(r * 0.30), fill=ink)
        d.rectangle([cx - 0.44 * r, cy - 0.05 * r, cx - 0.24 * r, cy + 0.05 * r], fill=CREAM)
        d.rectangle([cx - 0.39 * r, cy - 0.10 * r, cx - 0.29 * r, cy + 0.10 * r], fill=CREAM)
        d.ellipse([cx + 0.22 * r, cy - 0.16 * r, cx + 0.34 * r, cy - 0.04 * r], fill=CREAM)
        d.ellipse([cx + 0.40 * r, cy + 0.02 * r, cx + 0.52 * r, cy + 0.14 * r], fill=CREAM)
    elif kind == "gem":
        d.polygon([(cx, cy - 0.60 * r), (cx + 0.55 * r, cy - 0.08 * r),
                   (cx, cy + 0.66 * r), (cx - 0.55 * r, cy - 0.08 * r)], fill=ink)
        d.line([(cx - 0.55 * r, cy - 0.08 * r), (cx + 0.55 * r, cy - 0.08 * r)],
               fill=CREAM, width=thin)
        d.line([(cx, cy - 0.60 * r), (cx, cy + 0.66 * r)], fill=CREAM, width=thin)
    else:
        d.ellipse([cx - 0.30 * r, cy - 0.30 * r, cx + 0.30 * r, cy + 0.30 * r], fill=ink)


HEROES = [
    {"region": "EUROPE", "icon": "missile", "head": "MISSILES LAND IN POLAND",
     "det": "Two missiles and a drone fell in Poland; NATO: grave violation."},
    {"region": "GLOBAL", "icon": "chart", "head": "STOCKS PLUNGE WORLDWIDE",
     "det": "S&P 500 -3.7% into correction; Nikkei -5.1% on AI sell-off."},
    {"region": "GLOBAL", "icon": "bitcoin", "head": "BITCOIN BELOW $60,000",
     "det": "First since July: BTC closed $58,952 after touching $57,778."},
    {"region": "GLOBAL", "icon": "probe", "head": "BEPICOLOMBO REACHES MERCURY",
     "det": "After 8 years and 6bn miles, the probe arrives at Mercury."},
    {"region": "LATIN AMERICA", "icon": "seismo", "head": "6.7 QUAKE SHAKES PERU",
     "det": "M6.7 in the Andes at 7:09 p.m.; felt in Lima, no deaths."},
    {"region": "EUROPE", "icon": "document", "head": "UK AND EU SEAL NEW DEALS",
     "det": "Food, carbon, youth mobility — biggest Brexit reset yet."},
]

COLUMNS = [
    [
        {"region": "EUROPE", "icon": "missile", "head": "KYIV BRIDGES HIT",
         "det": "3 Dnipro bridges hit; 3 killed, ~15 hurt"},
        {"region": "EUROPE", "icon": "flag", "head": "BEAR TRAP: 14 VILLAGES RETAKEN",
         "det": "Ukraine says ~200 km² freed in Kharkiv"},
        {"region": "EUROPE", "icon": "shield", "head": "DENMARK EXPELS RUSSIAN ATTACHÉ",
         "det": "Over alleged plot to kill rapper Kyivstoner"},
        {"region": "EUROPE", "icon": "document", "head": "HUNGARY DROPS UKRAINE VETO",
         "det": "EU clears Kyiv's last two accession clusters"},
        {"region": "EUROPE", "icon": "coin", "head": "EU SENDS €8.9BN TO KYIV",
         "det": "€7.9bn aid + €1bn weapons, approved Fri"},
        {"region": "EUROPE", "icon": "shield", "head": "ESTONIA SHUTS RUSSIA BORDER",
         "det": "All crossings closed from 1 Dec, 6 months"},
        {"region": "EUROPE", "icon": "leaf", "head": "COP31: NO FOSSIL-FUEL DEAL",
         "det": "Draft drops fossil-fuel text; talks overtime"},
        {"region": "LATIN AMERICA", "icon": "plane", "head": "US BACKS COLOMBIA COCA SPRAYING",
         "det": "State Dept backs return of aerial eradication"},
        {"region": "AFRICA", "icon": "gem", "head": "ANGOLA BUYS 10% OF DE BEERS",
         "det": "$180m stake in the diamond giant"},
        {"region": "AFRICA", "icon": "flag", "head": "S. AFRICA MOURNS MLAMBO-NGCUKA",
         "det": "First woman deputy president dies at 71"},
    ],
    [
        {"region": "N. AMERICA", "icon": "chip", "head": "NVIDIA PLUNGES 14%",
         "det": "SEC probes accounting; ~$500bn wiped"},
        {"region": "N. AMERICA", "icon": "chart", "head": "ANTHROPIC SLIDES AFTER $81BN DEBUT",
         "det": "Shares fall the day after its record IPO"},
        {"region": "N. AMERICA", "icon": "mic", "head": "TRUMP CALLS PUTIN A “FRIEND”",
         "det": "Defends the word at White House presser"},
        {"region": "N. AMERICA", "icon": "shield", "head": "ICE & CBP: $41.7BN IN CONTRACTS",
         "det": "CNN: deportation spending surged in FY2026"},
        {"region": "N. AMERICA", "icon": "ballot", "head": "JUDGE WON'T BAN TRUMP ADS",
         "det": "Declines long-term ban on $20m DHS spots"},
        {"region": "N. AMERICA", "icon": "flame", "head": "PALISADES FIRE: GUILTY",
         "det": "Jury convicts man who started the 2025 blaze"},
        {"region": "N. AMERICA", "icon": "pill", "head": "MEASLES HITS 5,838 CASES",
         "det": "Worst US outbreak in decades, CDC says"},
        {"region": "N. AMERICA", "icon": "scales", "head": "BAYER'S $7.25BN ROUNDUP DEAL",
         "det": "Missouri judge approves the settlement"},
        {"region": "N. AMERICA", "icon": "rocket", "head": "SPACEX LAUNCHES USSF-317",
         "det": "Classified Space Force payload; booster lands"},
        {"region": "N. AMERICA", "icon": "basketball", "head": "HARDEN PASSES KOBE",
         "det": "51 points; 3rd-most 50-point games in NBA"},
    ],
    [
        {"region": "N. AMERICA", "icon": "ballot", "head": "BC'S FIRST CONSERVATIVE GOVT",
         "det": "Doerkson sworn in as premier after ~100 years"},
        {"region": "N. AMERICA", "icon": "building", "head": "NYC TO CLOSE RIKERS BY 2032",
         "det": "Mayor Mamdani releases first shutdown plan"},
        {"region": "ASIA", "icon": "pill", "head": "S. KOREA'S FIRST CHOLERA IN 10 YEARS",
         "det": "Case confirmed after a decade without one"},
        {"region": "ASIA", "icon": "chip", "head": "TSMC HALTS CHINA CHIP ORDERS",
         "det": "New US rules force licence checks on 16nm"},
        {"region": "ASIA", "icon": "bottle", "head": "TOXIC LIQUOR KILLS 11 IN MANIPUR",
         "det": "180+ hospitalised; CM confirms toll Friday"},
        {"region": "MIDDLE EAST", "icon": "flame", "head": "BLAST ON IRAN'S QESHM ISLAND",
         "det": "Reports flip from missile strike to munitions"},
        {"region": "MIDDLE EAST", "icon": "plane", "head": "SAUDI STRIKES HIT YEMEN PORT",
         "det": "Hodeidah hit; Houthis warn airlines off Saudi"},
        {"region": "GLOBAL", "icon": "gamepad", "head": "GTA VI: $3.79BN IN ONE DAY",
         "det": "Biggest entertainment launch ever"},
        {"region": "GLOBAL", "icon": "bitcoin", "head": "BINANCE HACKERS MOVE $346M MORE",
         "det": "$594m in ETH shifted in two days"},
    ],
]


def paint_header(d):
    d.rectangle([0, 0, IMG_W, 112], fill=NAVY)
    d.text((SIDE, 14), "THE WORLD IN ONE DAY", font=F_KICK, fill=GOLD)
    d.text((SIDE, 38), "20 NOVEMBER 2026", font=F_TITLE, fill=WHITE)
    pill = "FRIDAY"
    pw = F_PILL.getlength(pill)
    x0 = IMG_W - SIDE - pw - 36
    d.rounded_rectangle([x0, 18, IMG_W - SIDE, 58], radius=20, fill=RED)
    d.text((x0 + 18, 27), pill, font=F_PILL, fill=WHITE)
    stats = "35 STORIES · 7 REGIONS"
    sw = F_STATS.getlength(stats)
    d.text((IMG_W - SIDE - sw, 78), stats, font=F_STATS, fill=GOLD)
    d.rectangle([0, 112, IMG_W, 116], fill=GOLD)


def paint_hero(d, story, x, y, w, h):
    col = REGIONS[story["region"]]["color"]
    ink, tint = STYLE[story["icon"]]
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=WHITE)
    d.rounded_rectangle([x, y, x + w, y + 8], radius=10, fill=col)
    d.rectangle([x, y + 4, x + w, y + 8], fill=col)
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, outline=EDGE, width=1)
    cx, cy = x + 40, y + 70
    d.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], fill=tint)
    paint_glyph(d, story["icon"], cx, cy, 19, ink)
    tx = x + 80
    tw = w - 80 - 12
    d.text((tx, y + 16), story["region"], font=F_REGION, fill=col)
    hy = y + 38
    for line in wrap_lines(story["head"], F_HERO_HEAD, tw, 2):
        d.text((tx, hy), line, font=F_HERO_HEAD, fill=INK)
        hy += 24
    dy = y + 90
    for line in wrap_lines(story["det"], F_HERO_DET, tw, 2):
        d.text((tx, dy), line, font=F_HERO_DET, fill=GRAY)
        dy += 17


def paint_divider(d, y):
    title = "THE REST OF THE DAY — 29 MORE STORIES"
    d.text((SIDE, y), title, font=F_SECTION, fill=INK)
    spans = []
    total = 0
    for name in REGION_ORDER:
        w = F_LEGEND.getlength(name)
        spans.append((name, w))
        total += 8 + 3 + w + 6
    total -= 6
    title_end = SIDE + F_SECTION.getlength(title)
    x = max(IMG_W - SIDE - total, title_end + 12)
    for name, w in spans:
        col = REGIONS[name]["color"]
        d.ellipse([x, y + 3, x + 8, y + 11], fill=col)
        d.text((x + 11, y + 2), name, font=F_LEGEND, fill=INK)
        x += 11 + w + 6


def paint_item(d, story, x, y, w):
    col = REGIONS[story["region"]]["color"]
    ink, tint = STYLE[story["icon"]]
    d.ellipse([x, y + 4, x + 36, y + 40], fill=tint)
    paint_glyph(d, story["icon"], x + 18, y + 22, 12, ink)
    tx = x + 46
    tw = w - 46
    code = REGIONS[story["region"]]["code"]
    cw = F_CHIP.getlength(code)
    d.text((tx, y + 3), code, font=F_CHIP, fill=col)
    lines = wrap_first(story["head"], F_ITEM_HEAD, tw - cw - 8, tw, 2)
    d.text((tx + cw + 8, y + 1), lines[0], font=F_ITEM_HEAD, fill=INK)
    if len(lines) > 1:
        d.text((tx, y + 18), lines[1], font=F_ITEM_HEAD, fill=INK)
    d.text((tx, y + 35), squeeze(story["det"], F_ITEM_DET, tw),
           font=F_ITEM_DET, fill=GRAY)


def paint_footer(d):
    line1 = "All 35 events happened or were first reported on Friday, 20 November 2026."
    line2 = ("Sources: AP · Reuters · BBC · The Guardian · CNN · USGS · CDC · nyc.gov · "
             "Euronews — full list in README. Drawn in code; no photographs.")
    for i, line in enumerate((line1, line2)):
        w = F_FOOT.getlength(line)
        d.text(((IMG_W - w) / 2, 968 + i * 22), line, font=F_FOOT, fill=GRAY)


def build():
    img = Image.new("RGB", (IMG_W, IMG_H), CREAM)
    d = ImageDraw.Draw(img)
    paint_header(d)
    cell_w = (IMG_W - 2 * SIDE - 2 * COL_GAP) // 3
    cell_h = 140
    for i, story in enumerate(HEROES):
        row, col_i = divmod(i, 3)
        x = SIDE + col_i * (cell_w + COL_GAP)
        y = 132 + row * (cell_h + COL_GAP)
        paint_hero(d, story, x, y, cell_w, cell_h)
    paint_divider(d, 442)
    for c, column in enumerate(COLUMNS):
        x = SIDE + c * (cell_w + COL_GAP)
        for r, story in enumerate(column):
            paint_item(d, story, x, 478 + r * 48, cell_w)
    paint_footer(d)
    img.save(TARGET_PNG, "PNG")
    print(f"wrote {TARGET_PNG}")


if __name__ == "__main__":
    build()
