#!/usr/bin/env python3
"""Draw entry.png for make.fun news-image-20261120 (v2 re-push).

One image summing up the world news of Friday 20 November 2026:
35 verified stories across 7 regions, drawn entirely in code with PIL.
No photos, no copied artwork.

Layout (1024x1024):
  - navy header: date + "35 STORIES · 7 REGIONS"
  - 6 hero cards (3x2) with drawn pictograms
  - 29 compact items in 3 columns, each with a drawn mini-icon,
    a colour-coded region tag, a headline and one factual detail line

Every story was verified against at least two independent sources
(full source list in README.md). Events that happened on 19 Nov were
excluded even when reported on 20 Nov.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------------------------------------------------------------- fonts
def find_font(names):
    for p in names:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("none of %r found" % (names,))


ANTON = find_font([
    "/home/hatch/.fonts/Anton-Regular.ttf",
    "/usr/share/fonts/truetype/anton/Anton-Regular.ttf",
])
NOTO_BOLD = find_font([
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])
NOTO = find_font([
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
])


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- palette
PAPER = (245, 241, 232)
INK = (26, 32, 44)
SUB = (68, 64, 58)
NAVY = (16, 35, 63)
GOLD = (212, 172, 13)
CARD = (255, 255, 255)
CARD_EDGE = (217, 210, 194)

# region -> (label, colour, tint)
REGIONS = {
    "EU":    ("EUROPE",        (176, 58, 46),  (253, 237, 236)),
    "NA":    ("N. AMERICA",    (26, 82, 118),  (235, 245, 251)),
    "LATAM": ("LATIN AMERICA", (17, 120, 100), (234, 250, 241)),
    "ASIA":  ("ASIA",          (108, 52, 131), (244, 236, 247)),
    "ME":    ("MIDDLE EAST",   (147, 81, 22),  (253, 242, 233)),
    "AFR":   ("AFRICA",        (185, 119, 14), (254, 245, 231)),
    "GLOB":  ("GLOBAL",        (44, 62, 80),   (234, 236, 239)),
}

HEROES = [
    dict(region="EU", headline="MISSILES LAND IN POLAND",
         sub="Russian missiles fell in Poland. NATO calls it a grave violation.",
         icon="missile"),
    dict(region="GLOB", headline="STOCKS PLUNGE WORLDWIDE",
         sub="S&P 500 fell 3.7% into correction. Nikkei -5.1% as AI shares sold off.",
         icon="chart"),
    dict(region="GLOB", headline="BITCOIN BELOW $60,000",
         sub="First time since July. BTC closed at $58,952 after touching $57,778.",
         icon="bitcoin"),
    dict(region="GLOB", headline="BEPICOLOMBO REACHES MERCURY",
         sub="After 8 years and 6bn miles, the probe arrives at Mercury.",
         icon="mercury"),
    dict(region="LATAM", headline="6.7 QUAKE SHAKES PERU",
         sub="M6.7 in the central Andes at 7:09 p.m., felt in Lima. No casualties.",
         icon="quake"),
    dict(region="EU", headline="UK AND EU SEAL NEW DEALS",
         sub="Food trade, carbon, youth mobility - the biggest Brexit reset yet.",
         icon="deal"),
]

# dense items: (region, icon, headline, one-line detail)
DENSE = [
    ("EU", "missile", "KYIV BRIDGES HIT",
     "Strikes hit 3 Dnipro bridges; 3 killed, ~15 hurt"),
    ("EU", "flag", "BEAR TRAP: 14 VILLAGES RETAKEN",
     "Ukraine says ~200 km\u00b2 freed in Kharkiv"),
    ("EU", "shield", "DENMARK EXPELS RUSSIAN ATTACH\u00c9",
     "Over alleged plot to kill rapper Kyivstoner"),
    ("EU", "deal", "HUNGARY DROPS UKRAINE VETO",
     "EU clears Kyiv's last two accession clusters"),
    ("EU", "coin", "EU SENDS \u20ac8.9BN TO KYIV",
     "\u20ac7.9bn aid plus \u20ac1bn for weapons, approved Fri"),
    ("EU", "shield", "ESTONIA SHUTS RUSSIA BORDER",
     "All road crossings closed from 1 Dec, 6 months"),
    ("EU", "leaf", "COP31: NO FOSSIL-FUEL DEAL",
     "Draft drops fossil-fuel language; talks overtime"),
    ("NA", "chip", "NVIDIA PLUNGES 14%",
     "SEC probes accounting; ~$500bn wiped in a day"),
    ("NA", "chart", "ANTHROPIC SLIDES AFTER $81BN DEBUT",
     "Shares fall the day after its record IPO"),
    ("NA", "mic", "TRUMP CALLS PUTIN A \u201cFRIEND\u201d",
     "Defends the word at White House presser"),
    ("NA", "shield", "ICE & CBP: $41.7BN IN CONTRACTS",
     "CNN: deportation spending surged in FY2026"),
    ("NA", "ballot", "JUDGE WON'T BAN TRUMP ADS",
     "Declines long-term ban on $20m DHS spots"),
    ("NA", "flame", "PALISADES FIRE: GUILTY",
     "Jury convicts man who started the 2025 blaze"),
    ("NA", "pill", "MEASLES HITS 5,838 CASES",
     "Worst US outbreak in decades, CDC says"),
    ("NA", "scale", "BAYER'S $7.25BN ROUNDUP DEAL",
     "Missouri judge approves the settlement"),
    ("NA", "rocket", "SPACEX LAUNCHES USSF-317",
     "Classified Space Force payload; booster lands"),
    ("NA", "ball", "HARDEN PASSES KOBE",
     "51 points; 3rd-most 50-point games in NBA"),
    ("NA", "ballot", "BC'S FIRST CONSERVATIVE GOVT",
     "Doerkson sworn in as premier after ~100 years"),
    ("NA", "building", "NYC TO CLOSE RIKERS BY 2032",
     "Mayor Mamdani releases first shutdown plan"),
    ("LATAM", "plane", "US BACKS COLOMBIA COCA SPRAYING",
     "State Dept backs return of aerial eradication"),
    ("ASIA", "pill", "S. KOREA'S FIRST CHOLERA IN 10 YEARS",
     "Case confirmed after a decade without one"),
    ("ASIA", "chip", "TSMC HALTS CHINA CHIP ORDERS",
     "New US rules force licence checks on 16nm"),
    ("ASIA", "bottle", "TOXIC LIQUOR KILLS 11 IN MANIPUR",
     "180+ hospitalised; CM confirms toll Friday"),
    ("ME", "flame", "BLAST ON IRAN'S QESHM ISLAND",
     "Reports flip from missile strike to munitions"),
    ("ME", "plane", "SAUDI STRIKES HIT YEMEN PORT",
     "Hodeidah hit; Houthis warn airlines off Saudi"),
    ("AFR", "coin", "ANGOLA BUYS 10% OF DE BEERS",
     "$180m stake in the diamond giant"),
    ("AFR", "flag", "S. AFRICA MOURNS MLAMBO-NGCUKA",
     "First woman deputy president dies at 71"),
    ("GLOB", "gamepad", "GTA VI: $3.79BN IN ONE DAY",
     "Biggest entertainment launch ever, say analysts"),
    ("GLOB", "bitcoin", "BINANCE HACKERS MOVE $346M MORE",
     "$594m in ETH shifted in two days via THORChain"),
]

# column assignment for the dense area (balanced counts 10/10/9)
DENSE_COLS = [
    DENSE[0:7] + DENSE[19:20] + DENSE[25:27],    # EU 7 + LATAM 1 + AFRICA 2 = 10
    DENSE[7:17],                                  # NA 10
    DENSE[17:19] + DENSE[20:25] + DENSE[27:29],   # NA 2 + ASIA 3 + ME 2 + GLOB 2 = 9
]

# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------- icons
# Each draws a pictogram into a 96x96 layer (same coordinate space).

def icon_missile(d):
    d.polygon([(43, 72), (53, 72), (48, 90)], fill=(230, 126, 34))
    d.polygon([(45, 72), (51, 72), (48, 82)], fill=(241, 196, 15))
    d.polygon([(40, 56), (27, 74), (40, 70)], fill=(44, 62, 80))
    d.polygon([(56, 56), (69, 74), (56, 70)], fill=(44, 62, 80))
    d.rounded_rectangle([40, 16, 56, 72], radius=6, fill=(93, 109, 126))
    d.polygon([(40, 18), (56, 18), (48, 4)], fill=(176, 58, 46))
    d.ellipse([43, 30, 53, 40], fill=(174, 214, 241), outline=(44, 62, 80), width=2)


def icon_chart(d):
    d.line([(14, 84), (14, 14)], fill=(44, 62, 80), width=4)
    d.line([(14, 84), (86, 84)], fill=(44, 62, 80), width=4)
    pts = [(20, 28), (33, 40), (45, 36), (58, 54), (70, 50), (82, 70)]
    d.line(pts, fill=(176, 58, 46), width=5, joint="curve")
    d.polygon([(82, 70), (70, 66), (78, 80)], fill=(176, 58, 46))


def icon_bitcoin(d):
    d.ellipse([8, 8, 88, 88], fill=(247, 147, 26), outline=(185, 106, 0), width=3)
    f = font(NOTO_BOLD, 56)
    d.text((48, 48), "B", font=f, fill=(255, 255, 255), anchor="mm")
    d.rectangle([37, 20, 41, 76], fill=(255, 255, 255))
    d.rectangle([53, 20, 57, 76], fill=(255, 255, 255))


def icon_mercury(d):
    d.ellipse([10, 34, 66, 90], fill=(176, 169, 159), outline=(138, 131, 120), width=3)
    for (x, y, r) in [(26, 50, 6), (44, 66, 8), (30, 74, 4), (50, 46, 4)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(138, 131, 120))
    d.rectangle([56, 14, 62, 28], fill=(36, 113, 163))
    d.rectangle([80, 14, 86, 28], fill=(36, 113, 163))
    d.rectangle([62, 10, 80, 32], fill=(234, 242, 248), outline=(44, 62, 80), width=2)
    d.line([(71, 32), (60, 46)], fill=(44, 62, 80), width=2)


def icon_quake(d):
    pts = [(8, 62), (20, 62), (26, 34), (34, 62), (42, 62), (48, 24),
           (56, 62), (64, 62), (70, 46), (78, 62), (88, 62)]
    d.line(pts, fill=(146, 43, 33), width=4, joint="curve")
    d.line([(8, 78), (88, 78)], fill=(44, 62, 80), width=3)


def icon_deal(d):
    d.rounded_rectangle([20, 12, 68, 84], radius=4, fill=(255, 255, 255),
                        outline=(44, 62, 80), width=3)
    d.polygon([(56, 12), (68, 24), (56, 24)], fill=(213, 216, 220))
    for y in (36, 46, 56):
        d.line([(28, y), (52, y)], fill=(93, 109, 126), width=4)
    d.ellipse([56, 60, 82, 86], fill=(176, 58, 46), outline=(146, 43, 33), width=2)
    d.polygon(star_points(69, 73, 7, 3), fill=(241, 196, 15))


def icon_flag(d):
    d.line([(22, 12), (22, 86)], fill=(44, 62, 80), width=5)
    d.polygon([(26, 14), (78, 26), (26, 44)], fill=(176, 58, 46))
    d.polygon(star_points(42, 28, 7, 3), fill=(255, 255, 255))


def icon_shield(d):
    d.polygon([(48, 8), (82, 20), (82, 50), (48, 88), (14, 50), (14, 20)],
              fill=(36, 113, 163), outline=(26, 82, 118), width=3)
    d.line([(32, 48), (44, 60), (66, 34)], fill=(255, 255, 255), width=6,
           joint="curve")


def icon_coin(d):
    d.ellipse([12, 12, 84, 84], fill=(241, 196, 15), outline=(185, 119, 14), width=3)
    d.polygon([(48, 26), (66, 48), (48, 70), (30, 48)], fill=(255, 255, 255))
    d.polygon([(48, 34), (58, 48), (48, 62), (38, 48)], fill=(241, 196, 15))


def icon_leaf(d):
    d.polygon([(48, 10), (82, 34), (76, 76), (40, 88), (16, 52)],
              fill=(39, 174, 96), outline=(17, 120, 100), width=3)
    d.line([(48, 14), (48, 84)], fill=(17, 120, 100), width=3)
    d.line([(48, 40), (66, 30)], fill=(17, 120, 100), width=2)
    d.line([(48, 58), (30, 48)], fill=(17, 120, 100), width=2)


def icon_chip(d):
    d.rounded_rectangle([26, 26, 70, 70], radius=6, fill=(44, 62, 80))
    d.rounded_rectangle([38, 38, 58, 58], radius=3, fill=(174, 214, 241))
    for x in (34, 48, 62):
        d.line([(x, 14), (x, 26)], fill=(44, 62, 80), width=4)
        d.line([(x, 70), (x, 82)], fill=(44, 62, 80), width=4)
    for y in (34, 48, 62):
        d.line([(14, y), (26, y)], fill=(44, 62, 80), width=4)
        d.line([(70, y), (82, y)], fill=(44, 62, 80), width=4)


def icon_mic(d):
    d.rounded_rectangle([36, 10, 60, 52], radius=14, fill=(44, 62, 80))
    d.line([(48, 14), (48, 44)], fill=(174, 214, 241), width=3)
    d.arc([28, 40, 68, 76], 0, 180, fill=(44, 62, 80), width=5)
    d.line([(48, 76), (48, 88)], fill=(44, 62, 80), width=5)
    d.line([(36, 88), (60, 88)], fill=(44, 62, 80), width=5)


def icon_ballot(d):
    d.rounded_rectangle([16, 16, 80, 84], radius=6, fill=(255, 255, 255),
                        outline=(44, 62, 80), width=3)
    d.line([(28, 52), (40, 64), (62, 34)], fill=(39, 174, 96), width=7,
           joint="curve")
    d.line([(28, 28), (52, 28)], fill=(93, 109, 126), width=4)


def icon_flame(d):
    d.polygon([(48, 8), (66, 36), (78, 52), (72, 76), (48, 90), (24, 76),
               (18, 52), (32, 34)], fill=(230, 126, 34))
    d.polygon([(48, 40), (60, 56), (56, 74), (48, 82), (40, 74), (36, 56)],
              fill=(241, 196, 15))


def icon_pill(d):
    d.rounded_rectangle([18, 34, 78, 62], radius=14, fill=(255, 255, 255),
                        outline=(176, 58, 46), width=3)
    d.rounded_rectangle([18, 34, 48, 62], radius=14, fill=(176, 58, 46))
    d.rectangle([44, 34, 48, 62], fill=(176, 58, 46))
    d.ellipse([60, 70, 72, 82], fill=(36, 113, 163))
    d.ellipse([70, 76, 78, 84], fill=(36, 113, 163))


def icon_scale(d):
    d.line([(48, 12), (48, 80)], fill=(44, 62, 80), width=5)
    d.line([(20, 22), (76, 22)], fill=(44, 62, 80), width=5)
    d.line([(20, 22), (12, 52)], fill=(44, 62, 80), width=3)
    d.line([(20, 22), (28, 52)], fill=(44, 62, 80), width=3)
    d.line([(76, 22), (68, 52)], fill=(44, 62, 80), width=3)
    d.line([(76, 22), (84, 52)], fill=(44, 62, 80), width=3)
    d.polygon([(8, 52), (32, 52), (20, 64)], fill=(212, 172, 13))
    d.polygon([(64, 52), (88, 52), (76, 64)], fill=(212, 172, 13))
    d.line([(32, 80), (64, 80)], fill=(44, 62, 80), width=5)


def icon_rocket(d):
    d.polygon([(43, 74), (53, 74), (48, 92)], fill=(230, 126, 34))
    d.polygon([(45, 74), (51, 74), (48, 84)], fill=(241, 196, 15))
    d.polygon([(38, 58), (26, 76), (38, 72)], fill=(176, 58, 46))
    d.polygon([(58, 58), (70, 76), (58, 72)], fill=(176, 58, 46))
    d.rounded_rectangle([38, 14, 58, 74], radius=8, fill=(234, 242, 248),
                        outline=(44, 62, 80), width=2)
    d.polygon([(38, 16), (58, 16), (48, 4)], fill=(176, 58, 46))
    d.ellipse([42, 28, 54, 40], fill=(174, 214, 241), outline=(44, 62, 80), width=2)


def icon_ball(d):
    d.ellipse([10, 10, 86, 86], fill=(230, 126, 34), outline=(146, 43, 33), width=3)
    d.line([(10, 48), (86, 48)], fill=(146, 43, 33), width=3)
    d.line([(48, 10), (48, 86)], fill=(146, 43, 33), width=3)
    d.arc([10, 10, 70, 70], 270, 90, fill=(146, 43, 33), width=3)
    d.arc([26, 26, 86, 86], 90, 270, fill=(146, 43, 33), width=3)


def icon_building(d):
    d.rectangle([22, 26, 74, 86], fill=(93, 109, 126), outline=(44, 62, 80), width=3)
    d.rectangle([40, 66, 56, 86], fill=(44, 62, 80))
    for (x, y) in [(30, 34), (46, 34), (62, 34), (30, 50), (46, 50), (62, 50)]:
        d.rectangle([x, y, x + 8, y + 8], fill=(241, 196, 15))
    d.polygon([(18, 26), (78, 26), (48, 10)], fill=(176, 58, 46))


def icon_plane(d):
    d.polygon([(48, 12), (58, 34), (54, 50), (48, 50), (42, 50), (38, 34)],
              fill=(44, 62, 80))
    d.polygon([(40, 40), (12, 62), (40, 56)], fill=(93, 109, 126))
    d.polygon([(56, 40), (84, 62), (56, 56)], fill=(93, 109, 126))
    d.polygon([(44, 50), (52, 50), (56, 70), (48, 78), (40, 70)],
              fill=(44, 62, 80))
    d.ellipse([44, 22, 52, 30], fill=(174, 214, 241))


def icon_bottle(d):
    d.rectangle([42, 10, 54, 26], fill=(36, 113, 163))
    d.polygon([(42, 26), (54, 26), (62, 40), (34, 40)], fill=(36, 113, 163))
    d.rounded_rectangle([30, 40, 66, 86], radius=8, fill=(174, 214, 241),
                        outline=(26, 82, 118), width=3)
    d.rectangle([38, 52, 58, 72], fill=(255, 255, 255))


def icon_gamepad(d):
    d.rounded_rectangle([12, 30, 84, 68], radius=12, fill=(44, 62, 80))
    d.polygon([(24, 40), (28, 40), (28, 36), (32, 36), (32, 40), (36, 40),
               (36, 44), (32, 44), (32, 48), (28, 48), (28, 44), (24, 44)],
              fill=(255, 255, 255))
    d.ellipse([60, 40, 68, 48], fill=(241, 196, 15))
    d.ellipse([68, 48, 76, 56], fill=(176, 58, 46))


ICONS = {
    "missile": icon_missile, "chart": icon_chart, "bitcoin": icon_bitcoin,
    "mercury": icon_mercury, "quake": icon_quake, "deal": icon_deal,
    "flag": icon_flag, "shield": icon_shield, "coin": icon_coin,
    "leaf": icon_leaf, "chip": icon_chip, "mic": icon_mic,
    "ballot": icon_ballot, "flame": icon_flame, "pill": icon_pill,
    "scale": icon_scale, "rocket": icon_rocket, "ball": icon_ball,
    "building": icon_building, "plane": icon_plane, "bottle": icon_bottle,
    "gamepad": icon_gamepad,
}


def draw_icon(base, cx, cy, name, tint, size=96):
    layer = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([2, 2, 94, 94], fill=tint + (255,))
    ICONS[name](d)
    if size != 96:
        layer = layer.resize((size, size), Image.LANCZOS)
    base.alpha_composite(layer, (cx - size // 2, cy - size // 2))


def wrap_first(draw, text, fnt, w_first, w_rest):
    """Wrap with a narrower first line (room for a tag chip), then full width."""
    words = text.split()
    lines, cur, w = [], "", w_first
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=fnt) <= w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
            w = w_rest
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- build
def main():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- header band
    d.rectangle([0, 0, W, 112], fill=NAVY)
    d.rectangle([0, 112, W, 116], fill=GOLD)
    f_kick = font(NOTO_BOLD, 18)
    d.text((24, 12), "THE WORLD IN ONE DAY", font=f_kick, fill=(232, 184, 75))
    f_date = font(ANTON, 50)
    d.text((24, 34), "20 NOVEMBER 2026", font=f_date, fill=(255, 255, 255))
    tag = "FRIDAY"
    f_tag = font(NOTO_BOLD, 22)
    tw = d.textlength(tag, font=f_tag)
    d.rounded_rectangle([W - 24 - tw - 32, 20, W - 24, 20 + 44], radius=9,
                        fill=(192, 57, 43))
    d.text((W - 24 - tw - 16, 42), tag, font=f_tag, fill=(255, 255, 255),
           anchor="lm")
    f_count = font(NOTO_BOLD, 18)
    d.text((W - 24, 88), "35 STORIES  ·  7 REGIONS", font=f_count,
           fill=(232, 184, 75), anchor="ra")

    # ---- hero cards (6, 3x2)
    margin, gutter = 24, 14
    col_w = (W - 2 * margin - 2 * gutter) // 3
    hero_top, hero_h, hero_gap = 128, 136, 10
    f_hkick = font(NOTO_BOLD, 12)
    f_hhead = font(ANTON, 20)
    f_hsub = font(NOTO, 12)

    for i, s in enumerate(HEROES):
        col, row = i % 3, i // 3
        x0 = margin + col * (col_w + gutter)
        y0 = hero_top + row * (hero_h + hero_gap)
        x1, y1 = x0 + col_w, y0 + hero_h
        label, color, tint = REGIONS[s["region"]]

        d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=CARD,
                            outline=CARD_EDGE, width=2)
        d.rounded_rectangle([x0, y0, x1, y0 + 6], radius=3, fill=color)
        d.rectangle([x0, y0 + 3, x1, y0 + 6], fill=color)

        draw_icon(img, x0 + 42, y0 + 68, s["icon"], tint, size=66)

        tx = x0 + 84
        tw_text = x1 - 12 - tx
        d.text((tx, y0 + 12), label, font=f_hkick, fill=color)
        head_lines = wrap(d, s["headline"], f_hhead, tw_text)[:2]
        hy = y0 + 30
        for ln in head_lines:
            d.text((tx, hy), ln, font=f_hhead, fill=INK)
            hy += 23
        sub_lines = wrap(d, s["sub"], f_hsub, tw_text)[:2]
        sy = hy + 5
        for ln in sub_lines:
            d.text((tx, sy), ln, font=f_hsub, fill=SUB)
            sy += 15

    # ---- dense section strip
    strip_y = 420
    f_strip = font(NOTO_BOLD, 16)
    d.text((24, strip_y), "THE REST OF THE DAY \u2014 29 MORE STORIES",
           font=f_strip, fill=INK)
    # region legend, right aligned
    f_leg = font(NOTO_BOLD, 10)
    lx = W - 24
    for key in reversed(list(REGIONS)):
        label, color, _t = REGIONS[key]
        wlab = d.textlength(label, font=f_leg)
        lx -= wlab
        d.text((lx, strip_y + 3), label, font=f_leg, fill=color)
        lx -= 14
        d.ellipse([lx, strip_y + 5, lx + 9, strip_y + 14], fill=color)
        lx -= 12
    d.line([(24, strip_y + 26), (W - 24, strip_y + 26)], fill=CARD_EDGE, width=2)

    # ---- dense columns
    dense_top, dense_bottom = 456, 978
    f_tag = font(NOTO_BOLD, 9)
    f_head = font(NOTO_BOLD, 13)
    f_det = font(NOTO, 11)
    item_gap = 14
    col_x = [margin + c * (col_w + gutter) for c in range(3)]

    # 2-letter region codes for the inline tag chips (full names in legend)
    CODE = {"EU": "EU", "NA": "NA", "LATAM": "LA", "ASIA": "AS",
            "ME": "ME", "AFR": "AF", "GLOB": "GL"}

    for c, items in enumerate(DENSE_COLS):
        x0 = col_x[c]
        y = dense_top
        for (region, icon, headline, detail) in items:
            label, color, tint = REGIONS[region]
            draw_icon(img, x0 + 19, y + 19, icon, tint, size=38)
            tx = x0 + 44
            tw_text = x0 + col_w - 4 - tx
            # region tag chip (2-letter code) + headline, wrapped so the
            # first line leaves room for the chip
            code = CODE[region]
            chip_w = d.textlength(code, font=f_tag) + 10
            head_lines = wrap_first(d, headline, f_head,
                                    tw_text - chip_w - 6, tw_text)[:2]
            d.rounded_rectangle([tx, y + 1, tx + chip_w, y + 15], radius=4,
                                fill=color)
            d.text((tx + 5, y + 8), code, font=f_tag, fill=(255, 255, 255),
                   anchor="lm")
            hy = y
            d.text((tx + chip_w + 6, hy), head_lines[0], font=f_head, fill=INK)
            hy += 16
            for ln in head_lines[1:]:
                d.text((tx, hy), ln, font=f_head, fill=INK)
                hy += 16
            # detail line
            det = detail
            while d.textlength(det + "\u2026", font=f_det) > tw_text and len(det) > 10:
                det = det[:-1]
            if det != detail:
                det += "\u2026"
            d.text((tx, hy), det, font=f_det, fill=SUB)
            y = hy + 13 + item_gap
        print("column", c, "ends at y =", y)
        assert y <= dense_bottom, "dense column %d overflows: %d" % (c, y)

    # ---- footer
    f_foot = font(NOTO, 12)
    d.text((W // 2, 992),
           "All 35 events happened or were first reported on Friday, 20 November 2026.",
           font=f_foot, fill=SUB, anchor="mm")
    f_foot2 = font(NOTO, 11)
    d.text((W // 2, 1010),
           "Sources: AP \u00b7 Reuters \u00b7 BBC \u00b7 The Guardian \u00b7 CNN \u00b7 USGS \u00b7 CDC \u00b7 nyc.gov \u00b7 Euronews \u2014 full list in README. Drawn in code; no photographs.",
           font=f_foot2, fill=SUB, anchor="mm")

    img.convert("RGB").save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
