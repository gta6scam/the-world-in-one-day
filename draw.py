#!/usr/bin/env python3
"""ATLAS COMPLETE - a one-page newspaper summing up Friday 20 November 2026.

Draws entry.png (1024x1024) next to this file using only Pillow primitives:
flat vector-style shapes, no external images. Deterministic: no randomness,
no clocks, no network.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
MX = 18                      # page margin
CW = W - 2 * MX              # content width = 988

PAPER = (246, 240, 226)
CARD_BG = (253, 250, 242)
INK = (20, 33, 61)
RED = (179, 32, 44)
BLACK = (26, 26, 26)
GREY = (84, 80, 72)
FAINT = (196, 186, 158)

SANS = "DejaVuSans.ttf"
SANSB = "DejaVuSans-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SERIFB = "DejaVuSerif-Bold.ttf"

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

_cache = {}


def F(name, size):
    key = (name, int(size))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), int(size))
    return _cache[key]


def tw(s, font):
    return d.textlength(s, font=font)


def wrap(text, font, max_w):
    """Greedy word wrap; returns list of lines that each fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if tw(trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(x, y, text, fname, size0, size_min, max_w, max_h, fill,
              leading=1.18, align="left"):
    """Draw wrapped text, shrinking the font until it fits max_h. Returns height used."""
    size = size0
    while size > size_min:
        f = F(fname, size)
        lines = wrap(text, f, max_w)
        if len(lines) * size * leading <= max_h:
            break
        size -= 1
    f = F(fname, size)
    lines = wrap(text, f, max_w)
    lh = size * leading
    for i, ln in enumerate(lines):
        lx = x if align == "left" else x + (max_w - tw(ln, f)) / 2
        d.text((lx, y + i * lh), ln, font=f, fill=fill)
    return len(lines) * lh


def fit_font(text, fname, size0, size_min, max_w):
    size = size0
    while size > size_min and tw(text, F(fname, size)) > max_w:
        size -= 1
    return F(fname, size)


def italic_text(x, y, text, font, fill):
    """Fake italic: render upright, then shear the layer (top leans right)."""
    w = int(tw(text, font)) + 4
    h = font.size + 10
    layer = Image.new("RGBA", (w + h // 2, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((h // 4, 3), text, font=font, fill=fill + (255,))
    s = 0.26
    sheared = layer.transform(layer.size, Image.AFFINE,
                              (1, s, -s * h, 0, 1, 0), resample=Image.BILINEAR)
    img.paste(sheared, (int(x), int(y)), sheared)


# --------------------------------------------------------------------------
# Card illustrations: each draws inside (x, y, w, h). Flat shapes only.
# --------------------------------------------------------------------------

def ill_cyclone(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 204, 228))
    d.rectangle([x, y + h * 0.58, x + w, y + h], fill=(64, 116, 168))
    d.polygon([(x + w * 0.52, y + h), (x + w, y + h * 0.5), (x + w, y + h)],
              fill=(224, 198, 142))
    cx, cy = x + w * 0.36, y + h * 0.4
    for i, r in enumerate((5, 9, 13, 17)):
        d.arc([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72],
              start=i * 45, end=i * 45 + 235, fill=(255, 255, 255), width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))


def ill_kyiv(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(17, 23, 46))
    for bx, bw, bh in ((0.04, 0.2, 0.42), (0.28, 0.16, 0.58), (0.48, 0.2, 0.36),
                       (0.7, 0.14, 0.5), (0.86, 0.13, 0.4)):
        d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + bw), y + h],
                    fill=(5, 7, 14))
    for wx, wy in ((0.1, 0.68), (0.16, 0.78), (0.34, 0.55), (0.55, 0.72),
                   (0.75, 0.62), (0.9, 0.7)):
        d.rectangle([x + w * wx, y + h * wy, x + w * wx + 2, y + h * wy + 3],
                    fill=(250, 205, 90))
    d.arc([x - w * 0.15, y + h * 0.02, x + w * 0.75, y + h * 1.05],
          start=15, end=78, fill=(255, 138, 42), width=2)
    d.arc([x + w * 0.3, y - h * 0.1, x + w * 1.1, y + h * 0.95],
          start=25, end=85, fill=(255, 170, 60), width=2)
    for bx, by in ((0.62, 0.6), (0.85, 0.52)):
        cx, cy = x + w * bx, y + h * by
        for dx, dy in ((5, 0), (-5, 0), (0, 5), (0, -5)):
            d.line([cx, cy, cx + dx, cy + dy], fill=(255, 214, 120), width=1)


def ill_cop(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(243, 234, 208))
    cx = x + w * 0.5
    top, bot = y + 4, y + h - 12
    d.rounded_rectangle([cx - 5, top, cx + 5, bot], radius=5,
                        fill=(255, 255, 255), outline=INK, width=1)
    d.rectangle([cx - 3, y + h * 0.46, cx + 3, bot], fill=RED)
    d.ellipse([cx - 8, y + h - 15, cx + 8, y + h + 1], fill=RED, outline=INK)
    for i in range(3):
        ty = top + 6 + i * 8
        d.line([cx + 8, ty, cx + 13, ty], fill=INK, width=1)
    d.polygon([(x + w * 0.12, y + h * 0.2), (x + w * 0.2, y + h * 0.36),
               (x + w * 0.12, y + h * 0.52)], fill=(240, 178, 60))


def ill_markets(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 245, 238))
    for i in range(3):
        gy = y + h * (0.28 + 0.24 * i)
        d.line([x + 3, gy, x + w - 3, gy], fill=(214, 205, 190), width=1)
    pts = [(x + w * 0.05, y + h * 0.22), (x + w * 0.3, y + h * 0.38),
           (x + w * 0.45, y + h * 0.3), (x + w * 0.64, y + h * 0.6),
           (x + w * 0.79, y + h * 0.54), (x + w * 0.95, y + h * 0.84)]
    d.line(pts, fill=RED, width=3)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 8, ey - 3), (ex - 2, ey - 9)], fill=RED)


def ill_mercury(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(11, 13, 29))
    for sx, sy in ((0.08, 0.15), (0.2, 0.6), (0.3, 0.25), (0.45, 0.1),
                   (0.55, 0.7), (0.66, 0.2), (0.78, 0.55), (0.9, 0.15),
                   (0.94, 0.75), (0.12, 0.85), (0.4, 0.88), (0.85, 0.9)):
        d.point((x + w * sx, y + h * sy), fill=(230, 232, 240))
    cx, cy, r = x + w * 0.7, y + h * 0.52, w * 0.24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(158, 158, 164))
    for gx, gy, gr in ((-0.3, -0.2, 0.28), (0.25, 0.3, 0.2), (0.05, -0.45, 0.16)):
        d.ellipse([cx + r * gx - r * gr, cy + r * gy - r * gr,
                   cx + r * gx + r * gr, cy + r * gy + r * gr], fill=(128, 128, 136))
    px, py = x + w * 0.26, y + h * 0.42
    d.rectangle([px - 9, py - 3, px - 3, py + 3], fill=(70, 110, 190))
    d.rectangle([px + 3, py - 3, px + 9, py + 3], fill=(70, 110, 190))
    d.rectangle([px - 3, py - 4, px + 3, py + 4], fill=(238, 238, 238), outline=INK)
    d.arc([px - 2, py - 12, px + 8, py - 2], start=270, end=360,
          fill=(238, 238, 238), width=1)


def ill_hormuz(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 150, 184))
    d.polygon([(x, y), (x + w * 0.42, y), (x, y + h * 0.34)], fill=(226, 204, 148))
    d.polygon([(x + w, y), (x + w * 0.6, y), (x + w, y + h * 0.3)],
              fill=(226, 204, 148))
    hy = y + h * 0.6
    d.polygon([(x + w * 0.14, hy), (x + w * 0.86, hy), (x + w * 0.78, y + h * 0.82),
               (x + w * 0.22, y + h * 0.82)], fill=(38, 42, 52))
    d.rectangle([x + w * 0.14, y + h * 0.78, x + w * 0.86, y + h * 0.82], fill=RED)
    for i, c in enumerate(((179, 32, 44), (232, 164, 62), (74, 132, 94))):
        d.rectangle([x + w * (0.24 + 0.13 * i), hy - 8, x + w * (0.35 + 0.13 * i), hy],
                    fill=c)
    d.rectangle([x + w * 0.68, hy - 13, x + w * 0.76, hy], fill=(238, 238, 238),
                outline=INK)


def ill_cpi(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(246, 243, 236))
    base = y + h * 0.88
    d.line([x + 4, base, x + w - 4, base], fill=INK, width=1)
    for i, (bh, c) in enumerate(((0.34, INK), (0.5, INK), (0.68, RED))):
        bx = x + w * (0.14 + 0.26 * i)
        d.rectangle([bx, base - h * bh, bx + w * 0.17, base], fill=c)
    d.line([x + w * 0.2, y + h * 0.42, x + w * 0.82, y + h * 0.12], fill=RED, width=2)
    d.polygon([(x + w * 0.82, y + h * 0.12), (x + w * 0.7, y + h * 0.13),
               (x + w * 0.8, y + h * 0.24)], fill=RED)


def ill_rates(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(246, 243, 236))
    cx, cy, r = x + w * 0.5, y + h * 0.86, w * 0.36
    d.arc([cx - r, cy - r, cx + r, cy + r], start=180, end=360, fill=INK, width=3)
    for ang in (180, 225, 270, 315, 360):
        a = math.radians(ang)
        d.line([cx + (r - 5) * math.cos(a), cy + (r - 5) * math.sin(a),
                cx + r * math.cos(a), cy + r * math.sin(a)], fill=INK, width=1)
    a = math.radians(308)
    d.line([cx, cy, cx + (r - 7) * math.cos(a), cy + (r - 7) * math.sin(a)],
           fill=RED, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=INK)


def ill_cricket(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 216, 160))
    d.rectangle([x + w * 0.42, y + h * 0.2, x + w * 0.58, y + h], fill=(226, 204, 148))
    d.polygon([(x + w * 0.3, y + h * 0.1), (x + w * 0.4, y + h * 0.06),
               (x + w * 0.56, y + h * 0.68), (x + w * 0.44, y + h * 0.74)],
              fill=(216, 178, 110), outline=INK)
    bx, by = x + w * 0.72, y + h * 0.34
    d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=RED)
    d.arc([bx - 4, by - 5, bx + 4, by + 5], start=300, end=60,
          fill=(255, 255, 255), width=1)


def ill_ballot(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 230, 242))
    d.rectangle([x + w * 0.36, y + 2, x + w * 0.64, y + h * 0.46],
                fill=(255, 255, 255), outline=INK)
    d.line([x + w * 0.42, y + h * 0.16, x + w * 0.58, y + h * 0.16], fill=GREY)
    d.line([x + w * 0.42, y + h * 0.26, x + w * 0.58, y + h * 0.26], fill=GREY)
    d.line([x + w * 0.44, y + h * 0.34, x + w * 0.49, y + h * 0.4], fill=RED, width=2)
    d.line([x + w * 0.49, y + h * 0.4, x + w * 0.58, y + h * 0.3], fill=RED, width=2)
    d.rectangle([x + w * 0.18, y + h * 0.4, x + w * 0.82, y + h * 0.92],
                fill=(120, 132, 160), outline=INK)
    d.rectangle([x + w * 0.34, y + h * 0.46, x + w * 0.66, y + h * 0.52],
                fill=(30, 34, 44))


def ill_boat(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 203, 226))
    d.polygon([(x + w * 0.52, y + h * 0.1), (x + w * 0.52, y + h * 0.5),
               (x + w * 0.72, y + h * 0.5)], fill=(255, 255, 255), outline=INK)
    d.line([x + w * 0.52, y + h * 0.08, x + w * 0.52, y + h * 0.56], fill=INK, width=2)
    d.polygon([(x + w * 0.2, y + h * 0.52), (x + w * 0.78, y + h * 0.46),
               (x + w * 0.7, y + h * 0.66), (x + w * 0.28, y + h * 0.68)],
              fill=(146, 94, 52), outline=INK)
    for r in range(3):
        wy = y + h * (0.76 + 0.09 * r)
        for i in range(4):
            d.arc([x + 4 + i * (w - 8) / 4 + (r % 2) * 5, wy - 3,
                   x + 4 + (i + 1) * (w - 8) / 4 + (r % 2) * 5, wy + 4],
                  start=180, end=360, fill=(52, 102, 160), width=2)


def ill_italy(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
    d.line([x + w * 0.16, y + 3, x + w * 0.16, y + h - 3], fill=INK, width=2)
    fx, fy, fw, fh = x + w * 0.16, y + h * 0.1, w * 0.24, h * 0.52
    for i, c in enumerate(((0, 146, 70), (255, 255, 255), (206, 43, 55))):
        d.rectangle([fx + i * fw, fy, fx + (i + 1) * fw, fy + fh], fill=c, outline=INK)
    d.rectangle([x + w * 0.1, y + h * 0.74, x + w * 0.9, y + h * 0.92], fill=RED)


def ill_pill(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(224, 238, 232))
    layer = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx, cy = w / 2, h / 2
    ld.rounded_rectangle([cx - 24, cy - 10, cx + 24, cy + 10], radius=10,
                         fill=(255, 255, 255), outline=INK + (255,), width=2)
    ld.rectangle([cx - 24, cy - 10, cx, cy + 10], fill=RED + (255,))
    ld.rounded_rectangle([cx - 24, cy - 10, cx + 24, cy + 10], radius=10,
                         outline=INK + (255,), width=2)
    layer = layer.rotate(-28, resample=Image.BILINEAR, center=(cx, cy))
    img.paste(layer, (int(x), int(y)), layer)
    d.ellipse([x + w * 0.14, y + h * 0.68, x + w * 0.14 + 7, y + h * 0.68 + 7],
              fill=(120, 170, 150))
    d.ellipse([x + w * 0.8, y + h * 0.14, x + w * 0.8 + 6, y + h * 0.14 + 6],
              fill=(120, 170, 150))


# --------------------------------------------------------------------------
# World map: simplified continent blobs in (lon, lat), equirectangular.
# --------------------------------------------------------------------------

NAM = [(-165, 68), (-150, 70), (-135, 69), (-125, 71), (-112, 68), (-100, 69),
       (-92, 66), (-88, 62), (-84, 58), (-80, 58), (-78, 54), (-76, 50),
       (-70, 48), (-66, 45), (-70, 43), (-73, 40), (-74, 36), (-76, 32),
       (-79, 28), (-81, 26), (-82, 28), (-85, 29), (-89, 29), (-93, 29),
       (-97, 26), (-97, 23), (-95, 19), (-92, 15), (-88, 14), (-85, 12),
       (-83, 9), (-79, 9), (-82, 8), (-87, 13), (-92, 15), (-97, 17),
       (-102, 19), (-106, 23), (-110, 24), (-113, 28), (-118, 33), (-122, 37),
       (-124, 42), (-124, 47), (-129, 52), (-138, 58), (-150, 59), (-160, 58)]
GRL = [(-46, 60), (-38, 62), (-30, 65), (-22, 68), (-19, 70), (-22, 74),
       (-28, 78), (-40, 79), (-52, 77), (-58, 73), (-56, 68), (-53, 63)]
SAM = [(-79, 9), (-75, 10), (-70, 12), (-64, 10), (-59, 8), (-53, 5),
       (-50, 1), (-44, -3), (-37, -6), (-35, -9), (-38, -14), (-39, -18),
       (-41, -23), (-47, -25), (-52, -30), (-56, -35), (-58, -39), (-62, -41),
       (-65, -45), (-67, -49), (-68, -53), (-70, -54), (-72, -51), (-73, -46),
       (-73, -40), (-72, -33), (-70, -27), (-70, -21), (-73, -17), (-76, -14),
       (-79, -9), (-81, -5), (-81, -1), (-79, 2), (-77, 5), (-79, 8)]
EUR = [(-9, 37), (-9, 44), (-2, 47), (-4, 48), (-1, 50), (2, 51), (5, 53),
       (8, 55), (9, 57), (13, 58), (18, 59), (19, 61), (21, 64), (24, 68),
       (30, 70), (40, 68), (48, 66), (56, 64), (62, 61), (66, 57), (63, 52),
       (56, 50), (50, 49), (44, 48), (39, 46), (33, 45), (29, 44), (29, 42),
       (26, 40), (23, 39), (22, 41), (24, 43), (22, 45), (19, 44), (16, 43),
       (14, 42), (12, 44), (9, 44), (6, 43), (3, 42), (1, 40), (-1, 38),
       (-4, 36), (-7, 36)]
ITALY = [(7, 44), (11, 44), (13, 42), (15, 40), (18, 39), (19, 41), (17, 42),
         (15, 42), (13, 43), (11, 45), (8, 45)]
AFR = [(-6, 35), (0, 36), (9, 37), (11, 34), (19, 32), (27, 31), (32, 31),
       (34, 27), (36, 24), (38, 21), (40, 18), (43, 12), (46, 11), (51, 12),
       (50, 8), (46, 4), (42, -2), (40, -7), (39, -13), (37, -19), (35, -24),
       (32, -28), (27, -33), (20, -35), (18, -33), (16, -29), (14, -23),
       (13, -18), (12, -13), (12, -8), (10, -3), (9, 1), (6, 4), (0, 5),
       (-5, 5), (-10, 6), (-14, 8), (-17, 11), (-17, 15), (-16, 19),
       (-16, 23), (-15, 27), (-13, 29), (-10, 31), (-8, 33)]
ARABIA = [(34, 28), (36, 32), (39, 32), (42, 30), (47, 29), (50, 26), (53, 25),
          (56, 24), (59, 22), (58, 20), (55, 17), (52, 15), (48, 14),
          (44, 12), (42, 15), (40, 20), (38, 24), (36, 28)]
ASIA = [(30, 45), (38, 47), (47, 50), (56, 53), (66, 57), (78, 61), (90, 64),
        (103, 66), (117, 68), (132, 70), (147, 71), (160, 70), (172, 68),
        (179, 65), (178, 61), (169, 59), (160, 57), (154, 53), (149, 49),
        (144, 45), (141, 41), (138, 37), (134, 34), (130, 32), (126, 29),
        (122, 27), (119, 24), (114, 22), (109, 19), (106, 13), (104, 8),
        (101, 7), (99, 11), (96, 15), (93, 18), (91, 22), (88, 22), (86, 20),
        (88, 24), (91, 28), (90, 32), (94, 36), (98, 37), (102, 34),
        (107, 31), (113, 30), (120, 30), (126, 32), (129, 35), (128, 38),
        (125, 40), (119, 40), (115, 41), (113, 43), (117, 46), (122, 48),
        (128, 49), (133, 47), (138, 45), (141, 48), (139, 51), (133, 49),
        (127, 47), (121, 46), (114, 45), (107, 43), (100, 42), (93, 42),
        (86, 43), (79, 44), (72, 45), (65, 46), (58, 46), (51, 45), (44, 45),
        (37, 45)]
INDIA = [(72, 21), (75, 15), (77, 9), (79, 8), (81, 12), (84, 17), (87, 20),
         (90, 22), (92, 21), (90, 19), (86, 18), (82, 19), (78, 20), (74, 22)]
AUS = [(113, -22), (112, -26), (114, -31), (115, -34), (118, -35), (123, -33),
       (128, -32), (131, -32), (134, -33), (136, -35), (138, -36), (140, -38),
       (144, -38), (147, -38), (150, -37), (152, -33), (153, -28), (153, -24),
       (151, -21), (148, -19), (145, -16), (143, -13), (142, -11), (141, -14),
       (140, -18), (139, -19), (137, -16), (136, -13), (135, -12), (132, -11),
       (130, -13), (127, -14), (124, -16), (121, -18), (118, -20)]
BLOBS = [  # (lon, lat, width_deg, height_deg): UK, Japan, Indonesia, NZ, Madagascar
    (-3, 54, 7, 5), (130, 31, 3, 2), (133, 34, 3, 2), (137, 35, 3, 2),
    (139, 37, 3, 3), (141, 40, 3, 3), (142, 43, 4, 3),
    (102, -1, 10, 3), (112, -2, 9, 3), (119, -2, 8, 3), (128, -3, 9, 3),
    (138, -4, 10, 4), (167, -45, 4, 3), (172, -41, 4, 3), (175, -38, 3, 2),
    (47, -19, 4, 8),
]
PINS = {  # card number: (lon, lat, dx, dy nudge in px)
    1: (86, 20, 0, 0), 2: (30.5, 50.4, 0, 0), 3: (30.7, 36.9, 0, 0),
    4: (127, 37.5, 3, 2), 6: (56.3, 26.5, 0, 0), 7: (139.7, 35.7, 0, 0),
    8: (116.4, 39.9, -3, -3), 9: (174.8, -41.3, -4, 0), 10: (-89.2, 13.7, 0, 0),
    11: (-17.4, 14.7, 0, 0), 12: (12.5, 41.9, 2, -2), 13: (2.2, 41.4, -3, 2),
}
LAND = (31, 52, 89)


def draw_map(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(203, 214, 220), outline=INK, width=1)

    def px(lon):
        return x + (lon + 180) / 360 * w

    def py(lat):
        return y + (85 - lat) / 150 * h

    for glon in range(-150, 180, 30):
        d.line([px(glon), y + 1, px(glon), y + h - 1], fill=(182, 196, 205), width=1)
    for glat in (-30, 0, 30, 60):
        d.line([x + 1, py(glat), x + w - 1, py(glat)], fill=(182, 196, 205), width=1)
    for poly in (NAM, GRL, SAM, EUR, ITALY, AFR, ARABIA, ASIA, INDIA, AUS):
        d.polygon([(px(lon), py(lat)) for lon, lat in poly], fill=LAND)
    for lon, lat, wd, ht in BLOBS:
        d.ellipse([px(lon - wd / 2), py(lat + ht / 2), px(lon + wd / 2),
                   py(lat - ht / 2)], fill=LAND)
    pf = F(SANSB, 8)
    for num, (lon, lat, dx, dy) in PINS.items():
        cx, cy = px(lon) + dx, py(lat) + dy
        d.ellipse([cx - 6.5, cy - 6.5, cx + 6.5, cy + 6.5], fill=RED,
                  outline=(255, 255, 255), width=1)
        s = str(num)
        d.text((cx - tw(s, pf) / 2, cy - 4.5), s, font=pf, fill=(255, 255, 255))
    # Pin 5 is in space: a Mercury callout box in the map's top-right corner.
    bx, by, bw, bh = x + w - 122, y + 4, 118, 36
    d.rectangle([bx, by, bx + bw, by + bh], fill=(203, 214, 220), outline=INK,
                width=1)
    cx, cy = bx + 16, by + 13
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(158, 158, 164), outline=INK)
    d.ellipse([cx + 8, cy - 6.5, cx + 21, cy + 6.5], fill=RED,
              outline=(255, 255, 255), width=1)
    d.text((cx + 11.5, cy - 4.5), "5", font=pf, fill=(255, 255, 255))
    sf = F(SANS, 9)
    d.text((bx + 6, cy + 9), "SPACE: MERCURY", font=sf, fill=INK)


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

CARDS = [
    # (place, topic, headline, body, chip lines, illustration)
    ("ODISHA, INDIA", "CYCLONE", "Cyclone Akvan makes landfall in eastern India",
     "Crosses near Gopalpur: 300,000+ evacuated, winds 90-100 gusting 110 km/h, "
     "423 rescue teams, schools shut. (IMD, The Hindu)",
     ["LANDFALL", "GUSTS 110 KM/H"], ill_cyclone),
    ("KYIV, UKRAINE", "WAR", "Russia fires wave of ~30 ballistic missiles at Kyiv",
     "Seven overnight waves hit energy and transport sites; three water workers "
     "killed; two embassies damaged. (Kyiv Post, Reuters)",
     ["01:25 LOCAL", "7 WAVES"], ill_kyiv),
    ("ANTALYA, TÜRKIYE", "CLIMATE", "COP31 reaches its final day deadlocked",
     "Closing draft omits fossil-fuel phase-out; $120bn adaptation finance "
     "unresolved; '35 by 35' clean-power push. (UN News, Reuters)",
     ["COP31", "FINAL DAY", "DEADLOCK"], ill_cop),
    ("SEOUL/TOKYO", "MARKETS", "AI sell-off sinks Asia to worst week since 2020",
     "Nikkei -4.5%, KOSPI -4.7%, SoftBank -16% as MSCI Asia-Pacific falls 7% - "
     "worst week since 2020. (Reuters)",
     ["NIKKEI -4.5%", "KOSPI -4.7%"], ill_markets),
    ("MERCURY", "SPACE", "BepiColombo reaches Mercury after 8 years",
     "ESA/JAXA probe ends its 6bn-mile, 8-year cruise; orbit insertion around "
     "Mercury set for Saturday. (ESA, BBC)",
     ["8 YEARS", "6BN MILES"], ill_mercury),
    ("HORMUZ", "ENERGY", "Strait of Hormuz stays shut; Brent crude near $92.50",
     "46 ships waiting at 02:30 UTC; four attacks on vessels in 96 hours, "
     "maritime centre says. (UKMTO, Reuters)",
     ["46 SHIPS", "WAITING"], ill_hormuz),
    ("TOKYO", "ECONOMY", "Japan inflation hits 2.3%; BoJ hike eyed",
     "Oct headline CPI rises 2.1% to 2.3%; core stays above 2% a second month, "
     "fuelling hike bets. (Reuters)",
     ["CPI 2.3%", "OCTOBER"], ill_cpi),
    ("BEIJING", "RATES", "China holds lending rates for 18th month",
     "1-year LPR held at 3.0% and 5-year at 3.5%, as expected - an 18th "
     "straight month on hold. (PBOC, Reuters)",
     ["LPR HELD", "18TH MONTH"], ill_rates),
    ("WELLINGTON", "CRICKET", "Phillips makes history with 118 vs India",
     "First NZ batter with centuries in all 3 formats vs India in a year; "
     "NZ post 368. (ICC, AP)",
     ["118", "RECORD"], ill_cricket),
    ("SAN SALVADOR", "POLITICS", "Bukele registers for third-term run",
     "Files with electoral tribunal for Feb 2027 vote; rights groups "
     "object. (AP)",
     ["2027", "THIRD TERM"], ill_ballot),
    ("SENEGAL", "MIGRATION", "Migrant boat capsizes off Yenne; 4 dead",
     "Dozens missing from ~50-100 aboard as Canary Islands arrivals "
     "surge. (Al Jazeera)",
     ["~50-100", "ABOARD"], ill_boat),
    ("ROME", "LABOUR", "Italy's CGIL holds 24-hr general strike",
     "Unions rally in ~100 squares against 2027 budget; transit "
     "disrupted. (CGIL, AFP)",
     ["SCIOPERO", "24-HOUR"], ill_italy),
    ("BARCELONA", "HEALTH", "Pancreatic cancer pill shrinks tumours 60.7%",
     "Daraxonrasib + chemo shrinks tumours 60.7% vs 23-42% for chemo alone, "
     "early trial finds. (Reuters)",
     ["60.7%", "RESPONSE"], ill_pill),
]

ALSO = [
    (14, "BRAZIL", "Lula meets Chief Raoni as Indigenous land is recognised", "Al Jazeera"),
    (15, "SEOUL", "Ruling party moves to impeach Chief Justice Cho Hee-dae", "SBS"),
    (16, "BOUGAINVILLE", "Rio Tinto pledges $370m for Panguna mine fleet", "Reuters"),
    (17, "CANBERRA", "CBO warns AUKUS sub sales could shrink US fleet", "Reuters"),
    (18, "FLORIDA", "St. Johns River hits record 18.3 ft; four counties shut schools", "AP"),
    (19, "IOWA", "US Army sets noon detonation of 68 unstable explosive barrels", "AP"),
    (20, "TONGA", "Pacific kingdom declares emergency as El Niño drought bites", "RNZ"),
    (21, "WASHINGTON", "Pentagon puts US war cost against Iran at $48.3bn", "Reuters"),
    (22, "LONDON", "UK & Norway fund £100m+ for two Ukrainian naval vessels", "BBC"),
    (23, "COPENHAGEN", "Denmark's parliament approves Greenland defence bill", "AFP"),
    (24, "JAKARTA", "Indonesia's parliament passes asset-forfeiture bill", "Reuters"),
    (25, "GLOBAL", "UN marks World Children's Day across member states", "UN News"),
    (26, "CINCINNATI", "Zoo's famed hippo Fiona dies after swallowing hat", "AP"),
    (27, "SENEGAL", "President Faye enacts supplementary budget by decree", "AFP"),
    (28, "BRUSSELS", "Burnham holds first EU-UK reset summit", "EU Council"),
    (29, "NEW DELHI", "Pakistan minister to lead delegation to SCO meeting", "The Hindu"),
    (30, "QATAR", "U17 World Cup: Australia stun Argentina 2-0", "FIFA"),
    (31, "SOUTH AFRICA", "Harmer spins Proteas to Test win; Bavuma sets record", "ICC"),
    (32, "HONG KONG", "Badminton Open reaches semifinals after upset", "BWF"),
    (33, "TAIWAN", "Short-sell curbs take effect; two Russian bombers tracked", "Reuters"),
    (34, "TURIN", "Alcaraz-Cobolli & Medvedev-Tiafoe close ATP Finals groups", "ATP"),
    (35, "LOS ANGELES", "Thomas Markle ruled fit to stand trial", "BBC"),
    (36, "WELLINGTON", "Henry Nicholls scores 175* in 216-run stand with Phillips", "ICC"),
]

STATS = [
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("~30", "ballistic missiles fired at Kyiv"),
    ("-7%", "Asia shares' worst week since 2020"),
    ("2.3%", "Japan Oct headline CPI; BoJ eyed"),
    ("118", "Phillips' historic century vs India"),
    ("8 yrs", "BepiColombo reaches Mercury"),
]

CHIPS = ["EUROPE 7", "AMERICAS 8", "ASIA-PACIFIC 10", "MIDEAST 3", "AFRICA 3",
         "OCEANIA 4", "WORLD / SPACE 1"]


def draw_card(x, y, w, h, num, card, panel_w, head0, body0):
    place, topic, headline, body, chips, ill = card
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=INK, width=1)
    chip_h = 30
    ill(x + 1, y + 1, panel_w - 2, h - chip_h - 2)
    d.rectangle([x, y + h - chip_h, x + panel_w, y + h], fill=INK)
    cf = F(SANSB, 8)
    lh = 10
    cy = y + h - chip_h + (chip_h - len(chips) * lh) / 2 + 1
    for ln in chips:
        d.text((x + (panel_w - tw(ln, cf)) / 2, cy), ln, font=cf,
               fill=(255, 255, 255))
        cy += lh
    d.line([x + panel_w, y, x + panel_w, y + h], fill=INK, width=1)
    tx = x + panel_w + 8
    tw_max = x + w - 6 - tx
    kf = F(SANSB, 11 if panel_w > 70 else 10)
    nstr = str(num)
    d.text((tx, y + 5), nstr, font=kf, fill=RED)
    d.text((tx + tw(nstr, kf) + 3, y + 5), "· " + place + " · " + topic,
           font=kf, fill=INK)
    ky = y + 5 + kf.size + 4
    used = fit_block(tx, ky, headline, SANSB, head0, 10, tw_max,
                     y + h - ky - 40, INK, leading=1.14)
    fit_block(tx, ky + used + 2, body, SANS, body0, 8, tw_max,
              y + h - (ky + used + 2) - 4, BLACK, leading=1.16)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

# Top bar
tf = F(SANSB, 19)
d.text((MX, 15), "THE WORLD IN ONE DAY", font=tf, fill=INK)
rt = "FRIDAY'S NEWS · ONE PAGE · 36 STORIES · 6 CONTINENTS"
rf = F(SANSB, 12)
d.text((MX + CW - tw(rt, rf), 20), rt, font=rf, fill=RED)
d.rectangle([MX, 42, MX + CW, 45], fill=INK)
d.line([MX, 49, MX + CW, 49], fill=INK, width=1)

# Headline + strap
hf = fit_font("Friday 20 November 2026", SERIFB, 68, 40, CW)
d.text((MX, 56), "Friday 20 November 2026", font=hf, fill=INK)
strap = ("Cyclone Akvan strikes India • Ballistic missiles hit Kyiv • "
         "COP31 deadlocked on final day • Asian AI sell-off")
sf = fit_font(strap, SERIF, 19, 12, CW)
italic_text(MX, 128, strap, sf, RED)
d.line([MX, 156, MX + CW, 156], fill=INK, width=1)

# Stat strip
sy = 162
colw = CW / 6
nf, lf = F(SANSB, 26), F(SANS, 11)
for i, (num, label) in enumerate(STATS):
    cx = MX + i * colw
    if i:
        d.line([cx, sy + 2, cx, sy + 54], fill=FAINT, width=1)
    d.text((cx + 8, sy), num, font=nf, fill=RED)
    fit_block(cx + 8, sy + 33, label, SANS, 11, 8, colw - 14, 26, BLACK,
              leading=1.12)

# Region chips
cy0 = 226
cx = MX
cf2 = F(SANSB, 11)
for chip in CHIPS:
    wch = tw(chip, cf2) + 16
    d.rounded_rectangle([cx, cy0, cx + wch, cy0 + 24], radius=5, fill=INK)
    d.text((cx + 8, cy0 + 6), chip, font=cf2, fill=(255, 255, 255))
    cx += wch + 6
note = "ALL STORIES: FRI 20 NOV 2026, ANY TIME ZONE"
nf2 = fit_font(note, SANSB, 10, 7, MX + CW - cx - 4)
d.text((MX + CW - tw(note, nf2), cy0 + 7), note, font=nf2, fill=GREY)

# Cards: rows of 3, 3, 3, 4
rows = [(258, 96, 3, 84, 15, 11), (360, 96, 3, 84, 15, 11),
        (462, 96, 3, 84, 15, 11), (564, 88, 4, 60, 13, 10)]
idx = 0
for ry, rh, n, panel_w, head0, body0 in rows:
    if n == 3:
        xs = [MX + i * (322 + 11) for i in range(3)]
        ws = [322] * 3
    else:
        xs = [MX + i * (241 + 8) for i in range(4)]
        ws = [241] * 4
    for i in range(n):
        draw_card(xs[i], ry, ws[i], rh, idx + 1, CARDS[idx], panel_w, head0, body0)
        idx += 1

# Bottom left: map + date check
d.text((MX, 660), "WHERE IT HAPPENED", font=F(SANSB, 13), fill=INK)
draw_map(MX, 682, 434, 176)
dy = 866
d.rectangle([MX, dy, MX + 434, 950], outline=RED, width=2)
dc_title = "DATE CHECK — "
dc_rest = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: the "
           "Trump-Xi-Putin Shenzhen summit itself · Anthropic's $83 IPO pricing "
           "& Nasdaq debut · ICJ Myanmar Rohingya genocide verdict · GTA VI "
           "midnight launch · $190.4m Van Gogh sale · Senate 48-51 Iran "
           "war-powers vote.")
df = F(SANS, 10)
lines = wrap(dc_rest, df, 434 - 16 - tw(dc_title, F(SANSB, 10)))
ty = dy + 7
d.text((MX + 8, ty), dc_title, font=F(SANSB, 10), fill=RED)
d.text((MX + 8 + tw(dc_title, F(SANSB, 10)), ty), lines[0], font=df, fill=BLACK)
for ln in lines[1:]:
    ty += 13
    d.text((MX + 8, ty), ln, font=df, fill=BLACK)

# Bottom right: also list
ax = 466
aw = W - MX - ax
d.text((ax, 658), "ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES",
       font=F(SANSB, 14), fill=RED)
ly = 686
lead = (950 - ly) / 23
for num, place, text, src in ALSO:
    size = 11
    while size > 8:
        fn, fb = F(SANS, size), F(SANSB, size)
        total = (tw(str(num) + " ", fb) + tw(place + " ", fb)
                 + tw(text + " (" + src + ")", fn))
        if total <= aw:
            break
        size -= 1
    fn, fb = F(SANS, size), F(SANSB, size)
    xcur = ax
    d.text((xcur, ly), str(num), font=fb, fill=RED)
    xcur += tw(str(num), fb) + 3
    d.text((xcur, ly), place, font=fb, fill=INK)
    xcur += tw(place, fb) + 4
    d.text((xcur, ly), text + " (" + src + ")", font=fn, fill=BLACK)
    ly += lead

# Footer
d.line([MX, 958, MX + CW, 958], fill=INK, width=1)
f1 = ("Every story here happened, or was first reported, on Friday 20 November "
      "2026 in at least one time zone. Claims are attributed, not stated as fact.")
f2 = ("Sources: Reuters, AP, AFP, BBC, IMD, UN News, Al Jazeera, ICC, EU Council, "
      "PBOC, UKMTO. Original vector drawings.")
ff = F(SANS, 10)
d.text(((W - tw(f1, ff)) / 2, 966), f1, font=ff, fill=GREY)
d.text(((W - tw(f2, ff)) / 2, 982), f2, font=ff, fill=GREY)

# Save (quantize only if the flat PNG is unexpectedly large)
img.save(OUT, optimize=True)
if os.path.getsize(OUT) > 300 * 1024:
    img.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(
        OUT, optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
