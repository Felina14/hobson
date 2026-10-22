"""Six line-art scene banners for Hobson, drawn as SVG and rasterised to PNG (1600x480).
Style: ink lines on the page's dark background, one warm accent for light sources."""
import cairosvg, os
OUT = "/mnt/user-data/outputs/hobson_visuals/static/scenes"
W, H = 1600, 480
INK, DIM, WARM, MOON = "#cfd0c8", "#6d6f6a", "#ecab46", "#e8e4d2"
HEAD = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">' \
       f'<defs><radialGradient id="glow" r="0.5"><stop offset="0" stop-color="{WARM}" stop-opacity="0.35"/><stop offset="1" stop-color="{WARM}" stop-opacity="0"/></radialGradient>' \
       f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c0d10"/><stop offset="1" stop-color="#15171c"/></linearGradient></defs>' \
       f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
TAIL = '</svg>'
S = f'fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
SD = f'fill="none" stroke="{DIM}" stroke-width="1.6" stroke-linecap="round"'

def ground(y=400):
    return f'<path d="M0 {y} H{W}" {SD}/>' + ''.join(f'<path d="M{x} {y+8+(i%3)*6} h{18+(i%4)*10}" {SD}/>' for i, x in enumerate(range(40, W, 97)))

def stars(seed=3, n=40):
    import random; r = random.Random(seed)
    return ''.join(f'<circle cx="{r.randint(0,W)}" cy="{r.randint(10,200)}" r="{r.choice([0.8,1,1.4])}" fill="{MOON}" opacity="{r.choice([0.4,0.6,0.9])}"/>' for _ in range(n))

def moon(cx=1380, cy=90, r=38):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MOON}" stroke-width="1.8"/><circle cx="{cx+14}" cy="{cy-8}" r="{r}" fill="#0f1013"/>'

def lamp(x, y, s=1.0):
    return (f'<circle cx="{x}" cy="{y}" r="{90*s}" fill="url(#glow)"/>'
            f'<path d="M{x-7*s} {y-12*s} h{14*s} l{3*s} {20*s} h{-20*s} z" fill="{WARM}" opacity="0.9"/>')

def person(x, y, h=90, seated=False):
    # simple figure: head, body, legs (seated: bent)
    hd = h*0.14
    body = f'<circle cx="{x}" cy="{y-h}" r="{hd}" {S}/><path d="M{x} {y-h+hd} V{y-h*0.42}" {S}/>'
    arms = f'<path d="M{x-h*0.22} {y-h*0.62} L{x} {y-h*0.72} L{x+h*0.22} {y-h*0.6}" {S}/>'
    legs = (f'<path d="M{x} {y-h*0.42} L{x+h*0.3} {y-h*0.42} V{y}" {S}/><path d="M{x} {y-h*0.42} L{x-h*0.05} {y-h*0.42} V{y}" {S}/>' if seated
            else f'<path d="M{x} {y-h*0.42} L{x-h*0.16} {y}" {S}/><path d="M{x} {y-h*0.42} L{x+h*0.16} {y}" {S}/>')
    return body + arms + legs

def gate():
    g = HEAD + stars(1) + moon()
    g += f'<rect x="300" y="60" width="90" height="340" {S}/><rect x="1210" y="60" width="90" height="340" {S}/>'  # towers
    for x in (300, 1210):
        g += ''.join(f'<path d="M{x+i*22} 60 v-18 h12 v18" {S}/>' for i in range(4))
        g += f'<rect x="{x+32}" y="150" width="26" height="40" rx="13" fill="#0c0d10" stroke="{INK}" stroke-width="2"/>'
    g += f'<path d="M390 110 Q800 20 1210 110" {S}/>'  # arch
    # two leaning timber doors
    g += f'<path d="M420 400 L430 130 L790 150 L790 400 Z" {S}/><path d="M1180 400 L1170 130 L810 150 L810 400 Z" {S}/>'
    g += ''.join(f'<path d="M{440+i*58} 150 V400" {SD}/>' for i in range(6)) + ''.join(f'<path d="M{1160-i*58} 150 V400" {SD}/>' for i in range(6))
    g += f'<path d="M430 240 H790 M810 240 H1170 M430 330 H790 M810 330 H1170" {SD}/>'
    g += lamp(205, 300) + f'<path d="M180 400 V318 M230 400 V318 M170 318 H240 M195 318 L185 290 h40 l-10 28" {S}/>'  # brazier
    # guard on stool, spear
    g += f'<rect x="1360" y="356" width="46" height="8" {S}/><path d="M1366 364 V400 M1400 364 V400" {S}/>' + person(1383, 356, 96, seated=True)
    g += f'<path d="M1420 400 L1440 230 l-8 -26 l12 10 l8 -14 l2 24" {S}/>'
    g += ground() + TAIL
    return g

def market():
    g = HEAD + stars(2, 30)
    for i, x in enumerate((120, 520, 920, 1300)):
        y = 400
        g += f'<path d="M{x} {y} V{y-170} M{x+260} {y} V{y-170}" {S}/>'
        g += f'<path d="M{x-20} {y-170} L{x+130} {y-230} L{x+280} {y-170} Z" {S}/>'
        g += ''.join(f'<path d="M{x-20+j*50} {y-170} L{x+5+j*50} {y-230}" {SD}/>' for j in range(6))
        g += f'<rect x="{x+20}" y="{y-90}" width="220" height="90" {S}/>'
        g += ''.join(f'<circle cx="{x+50+k*30}" cy="{y-105}" r="12" {SD}/>' for k in range(6))
        g += lamp(x+130, y-150, 0.8)
    g += person(420, 400, 100) + person(860, 400, 92) + person(1240, 400, 104)
    g += ground() + TAIL
    return g

def inn():
    g = HEAD + stars(4) + moon(220, 80, 30)
    g += f'<path d="M400 400 V170 L800 60 L1200 170 V400" {S}/><path d="M360 180 L800 40 L1240 180" {S}/>'
    g += f'<path d="M800 60 V400" {SD}/>'
    for x, y in ((470, 220), (620, 220), (980, 220), (1130, 220), (470, 320), (1130, 320)):
        g += f'<rect x="{x-32}" y="{y-28}" width="64" height="56" fill="{WARM}" fill-opacity="0.75" stroke="{INK}" stroke-width="2"/><path d="M{x} {y-28} V{y+28} M{x-32} {y} H{x+32}" stroke="#0c0d10" stroke-width="2"/>'
        g += f'<circle cx="{x}" cy="{y}" r="70" fill="url(#glow)"/>'
    g += f'<path d="M740 400 V300 a60 40 0 0 1 120 0 V400" {S}/>'
    g += f'<path d="M1260 400 V200 M1260 200 H1400 L1370 260 H1260" {S}/><text x="1280" y="240" font-family="Georgia, serif" font-size="26" fill="{INK}">INN</text>'
    g += f'<path d="M560 60 V120 M560 60 h40 v30 h-40" {S}/>'  # chimney smoke
    g += f'<path d="M585 50 q20 -25 0 -50 q-20 -25 0 -50" {SD}/>'
    g += ground() + TAIL
    return g

def jail():
    g = HEAD
    g += f'<path d="M0 0 H{W} V{H} H0 Z" fill="#0a0b0d"/>'
    # stone wall blocks
    for r in range(9):
        y = r * 54
        off = 60 if r % 2 else 0
        g += ''.join(f'<rect x="{x+off}" y="{y}" width="118" height="52" {SD}/>' for x in range(-120, W, 120))
    # barred window with moonlight
    g += f'<rect x="640" y="60" width="320" height="220" fill="#15171c" stroke="{INK}" stroke-width="2.4"/>'
    g += ''.join(f'<path d="M{690+i*55} 60 V280" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>' for i in range(5))
    g += f'<path d="M640 170 H960" stroke="{INK}" stroke-width="5"/>'
    g += f'<path d="M660 280 L560 440 H1040 L940 280 Z" fill="{MOON}" fill-opacity="0.08"/>'
    # jailer outside: keys and dice
    g += person(1320, 400, 100, seated=True) + f'<rect x="1298" y="356" width="46" height="8" {S}/>'
    g += f'<circle cx="1395" cy="330" r="14" {S}/><path d="M1395 344 V380 l10 0 M1395 366 l8 0" {S}/>'
    g += f'<rect x="1230" y="376" width="20" height="20" {S}/><circle cx="1240" cy="386" r="2" fill="{INK}"/><rect x="1258" y="380" width="18" height="18" {S}/><circle cx="1263" cy="385" r="2" fill="{INK}"/><circle cx="1271" cy="393" r="2" fill="{INK}"/>'
    g += lamp(1180, 150, 0.7) + f'<path d="M1180 170 V260" {SD}/>'
    g += ground() + TAIL
    return g

def temple():
    g = HEAD + stars(5) + moon(260, 90, 34)
    g += f'<path d="M300 400 H1300 M330 370 H1270 M360 340 H1240" {S}/>'  # steps
    g += f'<path d="M380 340 V120 H1220 V340" {S}/><path d="M360 120 L800 30 L1240 120 Z" {S}/>'
    for i in range(7):
        x = 420 + i * 127
        g += f'<path d="M{x-16} 340 V140 M{x+16} 340 V140 M{x-22} 140 H{x+22} M{x-22} 340 H{x+22}" {S}/>'
        g += ''.join(f'<path d="M{x-8+k*8} 150 V330" {SD}/>' for k in range(3))
    g += lamp(800, 250, 1.1) + f'<path d="M770 340 V290 H830 V340" {S}/>'
    g += person(560, 400, 96)
    g += ground() + TAIL
    return g

def road():
    g = HEAD + stars(6, 60) + moon(1300, 100, 42)
    g += f'<path d="M0 400 L760 160 L840 160 L{W} 400" {S}/>'
    g += ''.join(f'<path d="M{800-6*i} {170+i*30} V{185+i*30}" {SD}/>' for i in range(8))
    for x, s in ((140, 1.0), (330, 0.7), (1380, 0.9), (1200, 0.6)):
        y = 400 - (1 - s) * 120
        g += f'<path d="M{x} {y} V{y-120*s}" {S}/><path d="M{x} {y-120*s} l{-40*s} {-40*s} M{x} {y-120*s} l{40*s} {-50*s} M{x} {y-90*s} l{-30*s} {-30*s} M{x} {y-100*s} l{30*s} {-20*s}" {S}/>'
    g += f'<path d="M700 300 h120 M680 300 v-70 l70 -30 l50 30 v70" {SD}/>'  # distant milestone/shrine
    g += person(900, 400, 110)
    g += f'<path d="M1000 300 H1140 M1000 290 V220 M1000 220 H1060" {S}/>'  # signpost
    g += ground() + TAIL
    return g

os.makedirs(OUT, exist_ok=True)
for name, fn in {"gate": gate, "market": market, "inn": inn, "jail": jail, "temple": temple, "road": road}.items():
    svg = fn()
    open(f"{OUT}/{name}.svg", "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{OUT}/{name}.png", output_width=W, output_height=H)
    print(name, os.path.getsize(f"{OUT}/{name}.png") // 1024, "KB")
