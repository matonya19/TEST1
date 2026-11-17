"""Афиша v2: общее фото на весь фон, Полина и Максим вырезаны по бокам, нейросвязи между людьми."""
import pathlib, random

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
K = 1.0  # центры лиц из детектора OpenCV (оригинал 2016x1512)
FACES = [(171, 630), (192, 528), (369, 522), (447, 446), (521, 648), (636, 516), (650, 786), (692, 418), (793, 560), (812, 816), (903, 469), (984, 468), (1009, 596), (1133, 538), (1182, 392), (1258, 557), (1396, 506), (1463, 492), (1558, 569), (1740, 490), (1917, 494)]
EDGES_EXTRA = 4
FWID = [110, 104, 107, 92, 93, 88, 105, 88, 98, 112, 92, 89, 90, 87, 92, 92, 91, 73, 91, 87, 86]
COLORS = ["#4A6CF7", "#F59E0B", "#EC4899", "#10B981", "#A5B4FC", "#FFFFFF"]

FMT = {
    "4x5": dict(W=1080, H=1350, s=0.95, ox=430, oy=-80, top=60, mono=170, h1=228, h1s=94,
                pol=dict(left=-170, bottom=280, h=560), mx=dict(right=-140, bottom=280, h=600), info=1085),
    "9x16": dict(W=1080, H=1920, s=1.0, ox=470, oy=-300, top=270, mono=390, h1=455, h1s=96,
                 pol=dict(left=-180, bottom=500, h=640), mx=dict(right=-150, bottom=500, h=680), info=1450),
}

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#1A1A2E}
body{font-family:'Inter Display','Inter',sans-serif;color:#fff;position:relative}
.bg{position:absolute;left:%(bx)dpx;top:%(by)dpx;width:%(bw)dpx;filter:saturate(.85) brightness(.62) contrast(1.05);-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 18%%,#000 100%%)}
.shade{position:absolute;inset:0;background:
 linear-gradient(180deg,rgba(26,26,46,.96) 0%%,rgba(26,26,46,.72) %(g1)d%%,rgba(26,26,46,.25) %(g2)d%%,rgba(26,26,46,.35) %(g3)d%%,rgba(26,26,46,.97) %(g4)d%%),
 radial-gradient(700px 500px at 100%% 0%%,rgba(74,108,247,.45),transparent 70%%)}
svg.net{position:absolute;left:0;top:0}
.person{position:absolute;-webkit-mask-image:linear-gradient(180deg,#000 72%%,transparent 100%%)}
.person img{height:100%%;display:block;filter:drop-shadow(0 0 30px rgba(74,108,247,.35))}
.logo{position:absolute;left:72px;top:%(top)dpx}.logo svg{width:112px;height:auto;display:block}
.pill{position:absolute;right:72px;top:%(pt)dpx;border:2px solid rgba(255,255,255,.55);border-radius:40px;padding:12px 26px;font-size:30px;font-weight:500;background:rgba(26,26,46,.4)}
.mono{position:absolute;left:72px;top:%(mono)dpx;font-family:'JetBrains Mono',monospace;font-size:40px;color:#A5B4FC}
.mono s{text-decoration:none;color:#6B75B8}
.mono b{display:inline-block;width:22px;height:44px;background:#A5B4FC;vertical-align:-8px;margin-left:6px}
h1{position:absolute;left:72px;right:60px;top:%(h1)dpx;font-size:%(h1s)dpx;line-height:1;font-weight:800;letter-spacing:-3px;text-shadow:0 4px 30px rgba(0,0,0,.5)}
h1 em{font-style:normal;background:linear-gradient(90deg,#F59E0B,#EC4899);-webkit-background-clip:text;color:transparent}
.name{position:absolute;display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.95);color:#1A1A2E;border-radius:40px;
 padding:10px 22px 10px 12px;font-size:28px;font-weight:800;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.name i{width:22px;height:22px;border-radius:50%%;display:block}
.name small{font-size:20px;font-weight:600;color:#4A4E6E}
.info{position:absolute;left:0;right:0;top:%(info)dpx;text-align:center}
.lead{font-size:30px;color:rgba(255,255,255,.85);font-weight:500;margin-bottom:14px}
.date{font-size:64px;font-weight:800;letter-spacing:-2px}
.date span{color:#A5B4FC}
.row{display:flex;justify-content:center;align-items:center;gap:26px;margin-top:22px}
.place{font-size:34px;color:rgba(255,255,255,.8);font-weight:600}
.cta{background:#4A6CF7;border-radius:44px;padding:18px 32px;font-size:32px;font-weight:700}
"""


def heads(L):
    W, H = L["W"], L["H"]
    p, m = L["pol"], L["mx"]
    pw = p["h"] * 933 / 1146; mw = m["h"] * 934 / 1400
    ph = (p["left"] + .43 * pw, H - p["bottom"] - p["h"] + .13 * p["h"])
    mh = (W - m["right"] - mw + .42 * mw, H - m["bottom"] - m["h"] + .39 * m["h"])
    return ph, mh


def net_svg(L):
    rnd = random.Random(3)
    s, ox, oy = L["s"], L["ox"], L["oy"]
    pts = [(x * K * s - ox, y * K * s - oy) for x, y in FACES]
    keep = [i for i, (x, y) in enumerate(pts) if 30 < x < L['W'] - 30 and 0 < y < L['H']]
    FW = [FWID[i] for i in keep]
    pts = [pts[i] for i in keep]
    out = []
    # ближайшие соседи
    edges = set()
    for i, a in enumerate(pts):
        d = sorted(range(len(pts)), key=lambda j: (pts[j][0] - a[0]) ** 2 + (pts[j][1] - a[1]) ** 2)
        for j in d[1:3]:
            edges.add(tuple(sorted((i, j))))
    for _ in range(EDGES_EXTRA):
        i, j = rnd.sample(range(len(pts)), 2)
        edges.add(tuple(sorted((i, j))))
    for i, j in edges:
        (x1, y1), (x2, y2) = pts[i], pts[j]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 30
        out.append(f'<path d="M{x1:.0f},{y1:.0f} Q{mx:.0f},{my:.0f} {x2:.0f},{y2:.0f}" stroke="#C7CEFF" stroke-width="2" fill="none" opacity=".55"/>')
    # к Полине и Максу — толстые светящиеся линии
    for hx, hy in heads(L):
        hx, hy = round(hx), round(hy)
        near = sorted(pts, key=lambda p: (p[0] - hx) ** 2 + (p[1] - hy) ** 2)[1:4]
        for x, y in near:
            out.append(f'<path d="M{hx},{hy} Q{(hx+x)/2:.0f},{min(hy,y)-60:.0f} {x:.0f},{y:.0f}" stroke="url(#gl)" stroke-width="4" fill="none" opacity=".9"/>')
    for k, (x, y) in enumerate(pts):
        c = COLORS[k % len(COLORS)]
        r = round(FW[k] * L['s'] * .62) if k < len(FW) else 40
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="none" stroke="{c}" stroke-width="3" opacity=".85"/>')
        out.append(f'<circle cx="{x + r * .7:.0f}" cy="{y - r * .7:.0f}" r="8" fill="{c}"/>')
    W, H = L["W"], L["H"]
    defs = '<defs><linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="#F59E0B"/><stop offset="1" stop-color="#EC4899"/></linearGradient></defs>'
    return f'<svg class="net" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs}{"".join(out)}</svg>'


def person(img, pos):
    side = "left" if "left" in pos else "right"
    return (f'<div class="person" style="{side}:{pos[side]}px;bottom:{pos["bottom"]}px;height:{pos["h"]}px">'
            f'<img src="{img}"></div>')


for fmt, L in FMT.items():
    W, H = L["W"], L["H"]
    bw = int(2016 * L["s"])
    g = (14, 30, 62, 84) if fmt == "4x5" else (20, 30, 58, 78)
    css = CSS % dict(W=W, H=H, bx=-L["ox"], by=-L["oy"], bw=bw, top=L["top"], pt=L["top"] + 4,
                     mono=L["mono"], h1=L["h1"], h1s=L["h1s"], info=L["info"], g1=g[0], g2=g[1], g3=g[2], g4=g[3])
    ph, mh = heads(L)
    body = f"""<img class="bg" src="group.src.jpg"><div class="shade"></div>
{net_svg(L)}
{person('polina_cut.png', L['pol'])}{person('max_cut.png', L['mx'])}
<div class="name" style="left:40px;top:{ph[1] + 300:.0f}px"><i style="background:#EC4899"></i>Полина <small>TEXTURA</small></div>
<div class="name" style="right:40px;top:{mh[1] + 200:.0f}px"><i style="background:#4A6CF7"></i>Максим <small>Co.Space</small></div>
<div class="logo">{LOGO}</div><div class="pill">Тбилиси</div>
<div class="mono"><s>&gt;</s> ИИ ускоряет всё<b></b></div>
<h1>А найти своих —<br><em>всё сложнее</em></h1>
<div class="info"><div class="lead">Сила сообществ · вечер, где знакомятся вживую</div>
<div class="date">27 ноября <span>· 19:00</span></div>
<div class="row"><span class="place">Ginger Hotel</span><span class="cta">Вход свободный</span></div></div>"""
    (HERE / f"poster2-{fmt}.html").write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>')
print("ok")
