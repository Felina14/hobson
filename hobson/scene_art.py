"""A drawing for any scene, in the same hand as the seven that were drawn by hand.

Nova invents the place, so the place cannot be known in advance; the seven banners in
static/scenes only ever fitted seven nouns, and Bedrock has had no Amazon image model since
Nova Canvas ended on 30 September 2026. So the drawing is composed here, in line art: a motif
chosen from the scene's own words, a horizon, one warm light, and weather. Deterministic from
the scene text, so the same place is always the same picture. No model, no network, no cost.
"""
from __future__ import annotations

import hashlib
import math
import re

W, H = 1600, 480
BG = "#0e0f12"
INK = "#d8d6cf"
LIGHT = "#f0b35e"


def _rng(seed: int):
    x = (seed or 1) & 0x7FFFFFFF
    def nxt(a: float = 0.0, b: float = 1.0):
        nonlocal x
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        return a + (b - a) * (x / 0x7FFFFFFF)
    return nxt


def ln(x1, y1, x2, y2, w=1.6, op=0.85, col=INK):
    return f'<path d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" stroke="{col}" stroke-width="{w}" opacity="{op}" fill="none"/>'


def pth(d, w=1.6, op=0.85, col=INK, fill="none"):
    return f'<path d="{d}" stroke="{col}" stroke-width="{w}" opacity="{op}" fill="{fill}"/>'


def rect(x, y, w_, h_, w=1.6, op=0.85, col=INK, fill="none"):
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w_:.0f}" height="{h_:.0f}" rx="2" '
            f'stroke="{col}" stroke-width="{w}" opacity="{op}" fill="{fill}"/>')


def circ(cx, cy, r, w=1.6, op=0.85, col=INK, fill="none"):
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" stroke="{col}" stroke-width="{w}" '
            f'opacity="{op}" fill="{fill}"/>')


def glow(cx, cy, r):
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="url(#gl)"/>'
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r/9:.0f}" fill="{LIGHT}" opacity="0.9"/>')


# --------------------------------------------------------------------- motifs
GROUND = 400


def m_tower(r):
    """A lighthouse or any tall tower, with its beam."""
    x = W * 0.72
    top, base = 60, GROUND
    s = pth(f"M{x-26} {base} L{x-13} {top+52} L{x+13} {top+52} L{x+26} {base} Z")
    for i in range(1, 6):
        y = top + 52 + (base - top - 52) * i / 6
        s += ln(x - 13 - 13 * i / 6, y, x + 13 + 13 * i / 6, y, 1.1, 0.5)
    s += rect(x - 30, top + 30, 60, 22)
    s += rect(x - 17, top - 2, 34, 32)
    s += rect(x - 9, top + 6, 18, 18, 1.2, 0.9, LIGHT, LIGHT)
    s += pth(f"M{x-21} {top-2} L{x} {top-24} L{x+21} {top-2}")
    s += pth(f"M{x-12} {top+14} L{x-560} {top-26} L{x-560} {top+92} Z", 0, 0.17, LIGHT, LIGHT)
    s += glow(x, top + 14, 150)
    return s


def m_sea(r):
    s = ""
    for row in range(5):
        y = GROUND + 14 + row * 17
        d, x = f"M0 {y}", 0
        while x < W:
            d += f" q 18 -7 36 0 q 18 7 36 0"
            x += 72
        s += pth(d, 1.2, 0.35 - row * 0.04)
    return s


def m_machines(r):
    """Server racks, consoles, anything with panels and lights."""
    s = ""
    for i in range(4):
        x = 180 + i * 300 + r(-18, 18)
        h_ = 230 + r(-24, 24)
        s += rect(x, GROUND - h_, 170, h_)
        for k in range(int(h_ // 26)):
            y = GROUND - h_ + 14 + k * 26
            s += ln(x + 12, y, x + 158, y, 1.0, 0.33)
            if r() > 0.62:
                s += circ(x + 150, y, 3, 0, 0.85, LIGHT, LIGHT)
        s += ln(x, GROUND - h_ - 8, x + 170, GROUND - h_ - 8, 1.2, 0.5)
    s += glow(W * 0.5, GROUND - 190, 190)
    return s


def m_interior(r):
    """A room: a window with panes, a table, a lamp on it."""
    wx, wy, ww, wh = 980, 90, 300, 210
    s = rect(wx, wy, ww, wh, 1.8)
    s += ln(wx + ww / 2, wy, wx + ww / 2, wy + wh, 1.2, 0.6)
    s += ln(wx, wy + wh / 2, wx + ww, wy + wh / 2, 1.2, 0.6)
    for i in range(9):      # rain on the glass
        x = wx + r(10, ww - 10)
        y = wy + r(10, wh - 40)
        s += ln(x, y, x - 7, y + 26, 1.0, 0.3)
    s += ln(0, GROUND, W, GROUND, 1.4, 0.55)
    tx = 330
    s += ln(tx - 150, GROUND - 120, tx + 150, GROUND - 120, 1.8)
    s += ln(tx - 130, GROUND - 120, tx - 130, GROUND, 1.4, 0.7)
    s += ln(tx + 130, GROUND - 120, tx + 130, GROUND, 1.4, 0.7)
    s += pth(f"M{tx-28} {GROUND-120} L{tx-18} {GROUND-168} L{tx+18} {GROUND-168} L{tx+28} {GROUND-120} Z")
    s += circ(tx, GROUND - 150, 7, 0, 0.9, LIGHT, LIGHT)
    s += glow(tx, GROUND - 150, 170)
    return s


def m_ship(r):
    """A hull: ribs, a porthole, pipes."""
    s = ""
    for i in range(5):
        x = 150 + i * 310
        s += pth(f"M{x} {GROUND} Q {x+60} 150 {x+150} 96", 1.3, 0.4)
    s += circ(1180, 190, 86, 2.0)
    s += circ(1180, 190, 70, 1.1, 0.45)
    for a in range(8):
        t = a * math.pi / 4
        s += ln(1180 + 70 * math.cos(t), 190 + 70 * math.sin(t),
                1180 + 86 * math.cos(t), 190 + 86 * math.sin(t), 1.1, 0.5)
    s += pth(f"M120 {GROUND-70} H760 q 24 0 24 -24 V 180", 1.6, 0.6)
    s += ln(0, GROUND, W, GROUND, 1.4, 0.55)
    s += glow(1180, 190, 180)
    return s


def m_city(r):
    s = ""
    x = -40
    while x < W:
        w_ = r(90, 190); h_ = r(110, 300)
        s += rect(x, GROUND - h_, w_, h_, 1.4, 0.6)
        for ry in range(int(h_ // 44)):
            for cx in range(int(w_ // 46)):
                if r() > 0.6:
                    s += rect(x + 14 + cx * 46, GROUND - h_ + 18 + ry * 44, 16, 20, 0, 0.5, LIGHT, LIGHT)
        x += w_ + r(16, 42)
    s += ln(0, GROUND, W, GROUND, 1.4, 0.6)
    s += glow(W * 0.3, GROUND - 240, 170)
    return s


def m_forest(r):
    s = ""
    for i in range(11):
        x = 60 + i * 150 + r(-30, 30)
        h_ = r(150, 290)
        s += pth(f"M{x} {GROUND} L{x} {GROUND-h_*0.25}")
        for k in range(3):
            w_ = 62 - k * 16
            y = GROUND - h_ * (0.25 + 0.25 * k)
            s += pth(f"M{x-w_} {y} L{x} {y-62} L{x+w_} {y} Z", 1.3, 0.55)
    s += ln(0, GROUND, W, GROUND, 1.4, 0.55)
    s += glow(W * 0.78, 140, 160)
    return s


def m_ward(r):
    """Beds in a row, a rail, a drip stand."""
    s = ln(0, GROUND, W, GROUND, 1.4, 0.55)
    for i in range(3):
        x = 180 + i * 420
        s += rect(x, GROUND - 92, 250, 56)
        s += rect(x + 250, GROUND - 130, 16, 94)
        s += ln(x, GROUND - 36, x, GROUND, 1.3, 0.7)
        s += ln(x + 250, GROUND - 36, x + 250, GROUND, 1.3, 0.7)
        s += rect(x + 16, GROUND - 108, 62, 20, 1.2, 0.6)
    s += ln(120, 60, W - 120, 60, 1.3, 0.45)
    s += ln(1320, 60, 1320, GROUND - 60, 1.2, 0.5)
    s += circ(1320, GROUND - 120, 10, 0, 0.8, LIGHT, LIGHT)
    s += glow(1320, GROUND - 120, 150)
    return s


def m_desk(r):
    s = ln(0, GROUND, W, GROUND, 1.4, 0.55)
    s += ln(420, GROUND - 130, 1180, GROUND - 130, 1.9)
    s += ln(470, GROUND - 130, 470, GROUND, 1.4, 0.7)
    s += ln(1130, GROUND - 130, 1130, GROUND, 1.4, 0.7)
    s += rect(700, GROUND - 268, 230, 132, 1.7)
    s += ln(815, GROUND - 136, 815, GROUND - 130, 1.4, 0.7)
    for i in range(5):
        s += ln(718, GROUND - 246 + i * 20, 718 + r(60, 196), GROUND - 246 + i * 20, 1.0, 0.4, LIGHT)
    s += rect(980, GROUND - 146, 120, 16, 1.2, 0.6)
    s += glow(815, GROUND - 200, 200)
    return s


def m_ruins(r):
    s = ""
    for i in range(4):
        x = 230 + i * 340
        h_ = r(170, 250)
        s += rect(x, GROUND - h_, 52, h_, 1.5, 0.7)
        s += rect(x - 12, GROUND - h_ - 18, 76, 18, 1.5, 0.7)
        for k in range(int(h_ // 34)):
            s += ln(x, GROUND - h_ + 20 + k * 34, x + 52, GROUND - h_ + 20 + k * 34, 1.0, 0.3)
    d, x = f"M0 {GROUND}", 0
    while x < W:
        d += f" q 110 -38 220 0"
        x += 220
    s += pth(d, 1.4, 0.5)
    s += glow(W * 0.2, 130, 190)
    return s


def m_stairs(r):
    s = ""
    x, y = 420, GROUND
    for i in range(11):
        s += ln(x, y, x + 86, y, 1.5, 0.75)
        s += ln(x + 86, y, x + 86, y - 30, 1.5, 0.6)
        x += 56; y -= 30
    s += ln(400, GROUND, 400, 120, 1.3, 0.45)
    s += ln(0, GROUND, W, GROUND, 1.4, 0.5)
    s += glow(1140, 110, 180)
    return s


def m_cave(r):
    s = pth(f"M240 {GROUND} Q 240 110 800 92 Q 1360 110 1360 {GROUND}", 1.8, 0.8)
    for i in range(9):
        x = 330 + i * 120 + r(-24, 24)
        s += pth(f"M{x} {120 + r(0,36)} l {r(-13,13):.0f} {r(42,92):.0f}", 1.2, 0.45)
    s += ln(0, GROUND, W, GROUND, 1.4, 0.55)
    s += glow(800, 250, 200)
    return s


MOTIFS = [
    (m_tower,    ("lighthouse", "tower", "beacon", "lamp room", "summit", "spire", "minaret",
                  "observatory", "watchtower", "belfry", "mast", "rig", "turret", "campanile")),
    (m_machines, ("server", "rack", "machine", "engine", "console", "terminal", "data", "plant",
                  "reactor", "factory", "recycler", "generator", "lab", "control", "datacentre",
                  "datacenter", "substation", "refinery", "boiler", "turbine", "mill", "workshop",
                  "foundry", "pump", "switchboard", "signal box")),
    (m_ship,     ("ship", "hull", "deck", "airlock", "submarine", "boat", "vessel", "orbit",
                  "station", "shuttle", "ferry", "tanker", "freighter", "capsule", "module",
                  "observation deck", "porthole")),
    (m_ward,     ("ward", "hospital", "clinic", "infirmary", "bed", "surgery", "sickbay",
                  "dispensary", "casualty", "icu", "dormitory", "barracks", "shelter")),
    (m_desk,     ("office", "desk", "study", "newsroom", "bureau", "cabin", "library", "archive",
                  "court", "courtroom", "courthouse", "tribunal", "chancery", "registry",
                  "classroom", "school", "lecture", "boardroom", "cubicle", "records room",
                  "reading room", "surgery office", "station house")),
    (m_forest,   ("forest", "woods", "woodland", "grove", "jungle", "orchard", "garden", "tree", "plantation",
                  "paddy", "field", "farm", "meadow", "thicket")),
    (m_city,     ("street", "city", "market", "town", "square", "alley", "harbour", "harbor",
                  "docks", "quay", "village", "platform", "bazaar", "pier", "wharf", "promenade",
                  "terminal", "airport", "rooftop", "skyline", "junction", "crossing")),
    (m_ruins,    ("ruin", "temple", "desert", "dune", "tomb", "shrine", "monument", "canyon",
                  "fort", "citadel", "colonnade", "amphitheatre", "necropolis", "mesa")),
    (m_stairs,   ("stair", "staircase", "stairwell", "steps", "ladder", "climb", "ascent",
                  "landing", "escalator", "spiral")),
    (m_cave,     ("cave", "tunnel", "cellar", "basement", "mine", "crypt", "vault", "undercroft",
                  "sewer", "catacomb", "bunker", "shaft", "grotto", "burrow")),
    (m_interior, ("room", "chamber", "hall", "kitchen", "parlour", "parlor", "bedroom", "house",
                  "cottage", "interior", "keep", "inn", "tavern", "lounge", "dining", "hallway",
                  "corridor", "attic", "loft", "apartment", "flat", "quarters", "lobby")),
]
SEA_WORDS = ("sea", "coast", "shore", "ocean", "tide", "wave", "harbour", "harbor", "beach", "cliff")
RAIN_WORDS = ("storm", "rain", "monsoon", "downpour", "squall", "thunder", "gale")
STAR_WORDS = ("space", "star", "void", "orbit", "night sky", "cosmos", "galaxy", "interstellar")


def pick(text: str):
    """The scene's name comes first in the text and is the strongest signal, so words found
    there count for more than words anywhere in the description."""
    low = text.lower()
    head = " " + re.sub(r"[-_/]", " ", low.split(" ", 1)[0]) + " "
    t = " " + re.sub(r"[-_/]", " ", low) + " "
    best, score = m_interior, 0
    for fn, words in MOTIFS:
        n = 0
        for w in words:
            if f" {w} " in head: n += 8
            elif f" {w} " in t:  n += 3
            elif w in t:         n += 1
        if n > score:
            best, score = fn, n
    return best


def svg_for(text: str, seed: int | None = None) -> str:
    t = text.lower()
    if seed is None:
        seed = int(hashlib.sha1(text.encode()).hexdigest()[:8], 16)
    r = _rng(seed)
    body = pick(text)(r)
    if any(w in t for w in SEA_WORDS):
        body += m_sea(r)
    extra = ""
    if any(w in t for w in RAIN_WORDS):
        extra = "".join(ln(x := r(-60, W), y := r(0, GROUND), x - 9, y + 34, 1.0, r(0.12, 0.32))
                        for _ in range(130))
    elif any(w in t for w in STAR_WORDS):
        extra = "".join(circ(r(0, W), r(0, GROUND - 40), r(0.6, 1.7), 0, r(0.2, 0.7), INK, INK)
                        for _ in range(150))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs><radialGradient id="gl" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="{LIGHT}" stop-opacity="0.42"/>
  <stop offset="55%" stop-color="{LIGHT}" stop-opacity="0.10"/>
  <stop offset="100%" stop-color="{LIGHT}" stop-opacity="0"/>
</radialGradient></defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{extra}{body}</svg>"""
