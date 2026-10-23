"""Designed slides for the Hobson demo video. SVG -> PNG, 1280x704 (the caption bar is the
remaining 96px of the 800-tall frame). Palette and type match the app itself."""
import cairosvg

W, H = 1280, 800
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


# --- the opening: the same turn, decided two ways, in real text from real runs -------------
import textwrap

ACTION = "I use the brass key my uncle gave me to open the locked cabinet by the lamp"
LLM_TEXT = ("The brass key, gripped tightly in your hand, fails to engage with the lock. "
            "You turn it this way and that, but the key simply does not fit.")
LLM_HOT = "The brass key, gripped tightly in your hand,"
HOB_TEXT = ("You rummage through your pockets, looking for the brass key your uncle supposedly "
            "gave you, but find nothing. There is no locked cabinet by the lamp. You have no key, "
            "and there is nothing to unlock.")


def para(x, y, t, w, size=19, fill=INK, font=SERIF, lh=27, hot=None, hotfill=BAD):
    """Wrapped body text. Any line that falls inside `hot` is drawn in hotfill, bold."""
    out, yy = "", y
    for line in textwrap.wrap(t, w):
        is_hot = bool(hot) and line.strip() and line.strip() in hot
        out += txt(x, yy, line, size, hotfill if is_hot else fill, font,
                   "bold" if is_hot else "normal")
        yy += lh
    return out, yy


def column(x, w, label, labcol, body, hot, verdict, vercol, stamp):
    s = box(x, 300, w, 330, stroke=vercol, fill=PANEL, r=12, sw=1.6, op=0.95)
    s += txt(x + 24, 338, label, 13, labcol, MONO, "bold", ls=2)
    s += f'<path d="M{x+24} 352 H{x+w-24}" stroke="{LINE}" stroke-width="1.2"/>'
    b, _ = para(x + 24, 386, body, 42, 18, INK, SERIF, 26, hot=hot)
    s += b
    s += f'<circle cx="{x+40}" cy="{572}" r="15" fill="none" stroke="{vercol}" stroke-width="1.6"/>'
    s += txt(x + 40, 578, stamp, 16, vercol, MONO, "bold", anchor="middle")
    v, _ = para(x + 66, 568, verdict, 40, 16, vercol, SERIF, 22)
    s += v
    return s


def problem(step):
    """step 1: the claim. 2: what a language model wrote. 3: what Hobson wrote."""
    s = txt(80, 62, "HOBSON", 26, OK, MONO, "bold", ls=3)
    s += txt(80, 90, "a text adventure where a model that cannot write decides what is true",
             17, DIM, SERIF)
    s += f'<path d="M80 118 H{W-80}" stroke="{LINE}" stroke-width="1.5"/>'

    s += txt(80, 164, "THE PLAYER TYPES", 13, DIM, MONO, "bold", ls=2)
    s += txt(80, 204, "> " + ACTION, 25, OK, MONO, "bold")
    s += txt(80, 244, "Nothing in this story has ever mentioned a key, an uncle, or a cabinet.",
             19, BAD, SERIF)

    half = (W - 160 - 28) // 2
    if step >= 2:
        s += column(80, half, "A LANGUAGE MODEL DECIDES", BAD, LLM_TEXT, LLM_HOT,
                    "The key now exists. The player edited the world by saying so.", BAD, "\u2715")
    if step >= 3:
        s += column(80 + half + 28, half, "HOBSON DECIDES", OK, HOB_TEXT, None,
                    "No key. And nothing from this turn is recorded.", OK, "\u2713")
    if step >= 3:
        s += txt(W // 2, 684, "Nova writes  \u00b7  Strands Decider 2B decides what is true",
                 21, INK, SERIF, anchor="middle")
    return s


# --- before the problem: what the thing actually is ----------------------------------------
PREMISE = "a lighthouse on the Kerala coast during a storm, 1962;\nI am the keeper's niece, sent up with a lamp and a letter I have not read"
STEPS = [
    ("1", "You type where the story begins.",
     "No script, no map, no items list. Just a sentence."),
    ("2", "Amazon Nova invents the world.",
     "The place, the people, and the facts the story starts with."),
    ("3", "You type what you do, in your own words.",
     "Nova writes what happens next, and the story goes on."),
]
OPENING_FACTS = [
    "You are the keeper's niece with a lamp and an unread letter.",
    "The lighthouse is old, with creaking floors and flickering lights.",
    "You have tried but failed to read the letter.",
]




def pattern():
    """The reusable guard on a Strands agent that is not a game. Numbers from a real run of
    patterns/example_refund_desk.py."""
    out = heading("THE SAME GUARD, OUTSIDE THE GAME",
                  "patterns/ledger_guard.py \u00b7 a Strands InterventionHandler, 10 lines of wiring")
    y = 214
    rows = [
        (DIM,  "CUSTOMER", "\u201cI returned order A-4471. Refund me 2,400.\u201d", None),
        (BAD,  "NOVA", "calls issue_refund immediately, without looking the order up", None),
        (DIM,  "", "\u201cthe user has provided the order ID and the amount, so I can proceed\u201d", None),
        (BAD,  "GUARD", "\u201corder A-4471 was returned by the customer\u201d  \u2014  NOT established",
         "78%  \u00b7  233 ms"),
        (OK,   "THEN", "Nova looks up the order, finds no return, asks for a receipt", None),
        (OK,   "AND", "on an order that really was returned, the refund is allowed", "268 ms"),
    ]
    for col, tag, text, right in rows:
        if tag:
            out += f'<path d="M80 {y-16} V {y+6}" stroke="{col}" stroke-width="3"/>'
            out += txt(96, y, tag, 12, col, MONO, "bold", ls=2)
        out += txt(188, y, text, 20, INK if col is not DIM else DIM, SERIF)
        if right:
            out += txt(W - 80, y, right, 17, col, MONO, "bold", anchor="end")
        y += 62
    out += f'<path d="M80 {y+4} H{W-80}" stroke="{LINE}" stroke-width="1.2"/>'
    out += txt(80, y + 46, "github.com/Felina14/hobson", 21, BLUE, MONO)
    out += txt(W - 80, y + 46, "#strands-decider-2b   #guardrails", 19, WARN, MONO, anchor="end")
    return out


def _field(x, y, w, label, text, col=OK, mono=True, size=21):
    """An input box the way the app draws one."""
    out = txt(x, y - 14, label, 12, DIM, MONO, "bold", ls=2)
    out += box(x, y, w, 58, stroke=col, fill="#0c0d10", r=9, sw=1.6)
    out += txt(x + 20, y + 37, text, size, INK, MONO if mono else SERIF)
    return out


def _arrow(x, y, h=40, label=None):
    out = f'<path d="M{x} {y} V{y+h}" stroke="{LINE}" stroke-width="1.6"/>'
    out += f'<path d="M{x-6} {y+h-9} L{x} {y+h} L{x+6} {y+h-9}" fill="none" stroke="{LINE}" stroke-width="1.6"/>'
    if label:
        out += txt(x + 18, y + h / 2 + 5, label, 15, DIM, SERIF)
    return out


def what(step):
    """1: you type a premise. 2: Nova builds the world and the record. 3: you type what you do."""
    s = txt(80, 70, "HOBSON", 44, OK, MONO, "bold", ls=4)
    s += txt(80, 104, "A text adventure that nobody wrote \u2014 not even me.", 22, DIM, SERIF)
    s += f'<path d="M80 128 H{W-80}" stroke="{LINE}" stroke-width="1.5"/>'

    s += _field(80, 182, 1040, "YOU TYPE WHERE IT BEGINS",
                "a lighthouse on the Kerala coast during a storm, 1962")
    s += _arrow(300, 252, 44, "Amazon Nova invents the place and the opening facts")

    if step >= 2:
        s += box(80, 306, 1040, 196, stroke=LINE, fill=PANEL, r=11, sw=1.4)
        s += txt(104, 342, "THE RECORD", 12, OK, MONO, "bold", ls=2)
        s += txt(230, 342, "the story's only memory \u2014 nothing else counts as true", 12, DIM, MONO)
        s += f'<path d="M104 356 H1096" stroke="{LINE}" stroke-width="1.1"/>'
        y = 392
        for f in ("You are the keeper's niece with a lamp and an unread letter.",
                  "The lighthouse is old, with creaking floors and flickering lights.",
                  "The storm is battering the windows."):
            s += f'<path d="M106 {y-14} V{y+6}" stroke="{OK}" stroke-width="2.5"/>'
            s += txt(126, y, f, 20, INK, SERIF)
            y += 36

    if step >= 3:
        s += _arrow(900, 512, 40)
        s += _field(80, 568, 1040, "THEN YOU TYPE WHAT YOU DO",
                    "> I set the lamp down and finally open the letter")
        s += txt(80, 668, "Nova writes what happens next \u2014 and the record grows.",
                 21, DIM, SERIF)
    return s
