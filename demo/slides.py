"""Designed slides for the Hobson demo video. SVG -> PNG, 1280x704 (the caption bar is the
remaining 96px of the 800-tall frame). Palette and type match the app itself."""
import cairosvg

W, H = 1280, 704
BG, PANEL, INK, DIM, LINE = "#101114", "#171a20", "#e8e6df", "#8a8c88", "#262a33"
OK, WARN, BAD, BLUE = "#68c478", "#ecab46", "#ec6e6e", "#6eaaf0"
MONO, SERIF = "DejaVu Sans Mono", "DejaVu Serif"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(body, bg=BG):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>')


def txt(x, y, t, size=22, fill=INK, font=SERIF, weight="normal", anchor="start", ls=0, op=1):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op}">{esc(t)}</text>')


def box(x, y, w, h, stroke=LINE, fill="none", r=10, sw=1.6, op=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>')


def heading(t, sub=None):
    s = txt(80, 96, t, 40, OK, MONO, "bold", ls=1)
    s += f'<path d="M80 118 H{W-80}" stroke="{LINE}" stroke-width="1.5"/>'
    if sub:
        s += txt(80, 150, sub, 22, DIM, SERIF)
    return s


def render(name, body, out):
    cairosvg.svg2png(bytestring=svg(body).encode(), write_to=out, output_width=W, output_height=H)
    return out


# ---------------------------------------------------------------- 1. title
def title():
    b = txt(80, 230, "HOBSON", 92, OK, MONO, "bold", ls=8)
    b += f'<path d="M80 262 H540" stroke="{OK}" stroke-width="2.5"/>'
    b += txt(80, 322, "A text adventure with two brains.", 32, INK, SERIF)
    b += txt(80, 374, "Amazon Nova writes the story.", 25, DIM, SERIF)
    b += txt(80, 410, "Strands Decider 2B decides what is true in it.", 25, DIM, SERIF)
    # the pair, as chips
    b += box(80, 452, 250, 64, OK, "#131a15", 8)
    b += txt(100, 480, "Nova Lite / Pro", 20, OK, MONO, "bold")
    b += txt(100, 502, "writes · on Bedrock", 15, DIM, MONO)
    b += box(350, 452, 250, 64, BLUE, "#121722", 8)
    b += txt(370, 480, "Decider 2B", 20, BLUE, MONO, "bold")
    b += txt(370, 502, "rules · on this Mac", 15, DIM, MONO)
    b += txt(80, 586, "Nothing about the story is written in advance.", 24, WARN, SERIF)
    b += txt(80, 622, "You type where it begins, and what you do.", 24, WARN, SERIF)
    return b


# ---------------------------------------------------------------- 2. agenda
def agenda(items):
    b = heading("WHAT THIS SHOWS")
    y = 212
    for i, (t, d) in enumerate(items, 1):
        b += f'<circle cx="104" cy="{y-8}" r="20" fill="none" stroke="{OK}" stroke-width="1.8"/>'
        b += txt(104, y, str(i), 22, OK, MONO, "bold", anchor="middle")
        b += txt(148, y - 4, t, 27, INK, SERIF)
        b += txt(148, y + 26, d, 19, DIM, SERIF)
        y += 86
    return b


# ---------------------------------------------------------------- 3. the questions
def questions(rows):
    b = heading("EVERY TURN, DECIDER ANSWERS", "the ledger is the story's only memory")
    y = 196
    for q, a, kind in rows:
        col = {"yesno": OK, "pick": BLUE, "guard": WARN}[kind]
        b += box(80, y, W - 160, 62, LINE, PANEL, 8)
        b += f'<path d="M80 {y} v62" stroke="{col}" stroke-width="4"/>'
        b += txt(106, y + 38, q, 23, INK, MONO)
        b += txt(W - 106, y + 38, a, 20, col, SERIF, anchor="end")
        y += 74
    b += txt(80, y + 36, "Every answer carries a confidence.", 23, INK, SERIF)
    b += txt(80, y + 70, "Under 60%, Decider says “not sure” and hands that one call to Nova.", 23, WARN, SERIF)
    return b


# ---------------------------------------------------------------- 4. results
def results(cols, rows, foot):
    b = heading("THE SAME SCRIPT, TWO REFEREES, THREE RUNS EACH")
    x0, x1, x2 = 80, 640, 990
    b += txt(x1, 196, cols[0], 20, BLUE, MONO, "bold")
    b += txt(x2, 196, cols[1], 20, DIM, MONO, "bold")
    b += f'<path d="M80 212 H{W-80}" stroke="{LINE}" stroke-width="1.2"/>'
    y = 254
    for label, a, bb, hi in rows:
        b += txt(x0, y, label, 22, DIM, SERIF)
        b += txt(x1, y, a, 21, OK if hi else INK, MONO, "bold" if hi else "normal")
        b += txt(x2, y, bb, 21, BAD if hi else INK, MONO)
        y += 58
    b += f'<path d="M80 {y-24} H{W-80}" stroke="{LINE}" stroke-width="1.2"/>'
    for i, line in enumerate(foot):
        b += txt(80, y + 24 + i * 34, line, 21, INK if i == 0 else DIM, SERIF)
    return b


# ---------------------------------------------------------------- 5. end
def end(url, tags, lines):
    b = txt(80, 200, "HOBSON", 56, OK, MONO, "bold", ls=6)
    b += f'<path d="M80 226 H420" stroke="{OK}" stroke-width="2"/>'
    b += txt(80, 300, url, 32, BLUE, MONO)
    x = 80
    for t in tags:
        w = 20 + len(t) * 14
        b += box(x, 340, w, 44, WARN, "#1a1710", 22)
        b += txt(x + w / 2, 369, t, 20, WARN, MONO, anchor="middle")
        x += w + 16
    y = 448
    for line in lines:
        b += txt(80, y, line, 23, DIM, SERIF); y += 38
    return b
