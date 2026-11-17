"""Креатив для лидеров: «Ведёшь сообщество? Расскажи о нём 27 ноября» с Полиной и Максимом."""
import pathlib, random

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
K = 1.0  # центры лиц из детектора OpenCV (оригинал 2016x1512)
FACES = [(171, 630), (192, 528), (369, 522), (447, 446), (521, 648), (636, 516), (650, 786), (692, 418), (793, 560), (812, 816), (903, 469), (984, 468), (1009, 596), (1133, 538), (1182, 392), (1258, 557), (1396, 506), (1463, 492), (1558, 569), (1740, 490), (1917, 494)]
EDGES_EXTRA = 4
FWID = [110, 104, 107, 92, 93, 88, 105, 88, 98, 112, 92, 89, 90, 87, 92, 92, 91, 73, 91, 87, 86]
COLORS = ["#4A6CF7", "#F59E0B", "#EC4899", "#10B981", "#A5B4FC", "#FFFFFF"]

FMT = {
    "4x5": dict(W=1080, H=1350, s=0.95, ox=430, oy=30, top=60, mono=0, h1=915, h1s=92, info=165,
                pol=dict(left=463,top=350,h=880,fy=500), mx=dict(left=22,top=379,h=528,fy=500), polname=(622, 765), maxname=(70, 765), g=(16, 26, 52, 70)),
    "9x16": dict(W=1080, H=1920, s=1.0, ox=470, oy=-150, top=270, mono=0, h1=1250, h1s=100, info=385,
                 pol=dict(left=456,top=635,h=910,fy=790), mx=dict(left=21,top=665,h=546,fy=790), polname=(625, 1055), maxname=(75, 1055), g=(22, 30, 54, 66)),
}
PCUT = (933, 1146, .403, .170)   # w, h, центр головы x/y в долях
MCUT = (902, 1059, .395, .229)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#1A1A2E}
body{font-family:'Inter Display','Inter',sans-serif;color:#fff;position:relative}
.bg{position:absolute;left:%(bx)dpx;top:%(by)dpx;width:%(bw)dpx;filter:saturate(.85) brightness(.5) blur(1.5px) contrast(1.05);-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 18%%,#000 100%%)}
.shade{position:absolute;inset:0;background:
 linear-gradient(180deg,rgba(26,26,46,.96) 0%%,rgba(26,26,46,.72) %(g1)d%%,rgba(26,26,46,.25) %(g2)d%%,rgba(26,26,46,.35) %(g3)d%%,rgba(26,26,46,.97) %(g4)d%%),
 radial-gradient(700px 500px at 100%% 0%%,rgba(74,108,247,.45),transparent 70%%)}
svg.net{position:absolute;left:0;top:0}
.glow{position:absolute;left:-200px;right:-200px;bottom:-300px;height:700px;background:radial-gradient(closest-side,rgba(74,108,247,.35),transparent)}
.person{position:absolute;-webkit-mask-image:linear-gradient(180deg,#000 62%%,transparent 92%%)}
.halo{position:absolute;border-radius:50%%;border:3px solid;box-shadow:0 0 40px currentColor}
.person img{height:100%%;display:block;filter:drop-shadow(0 0 30px rgba(74,108,247,.35))}
.logo{position:absolute;left:72px;top:%(top)dpx}.logo svg{width:112px;height:auto;display:block}
.pill{position:absolute;right:72px;top:%(pt)dpx;border-radius:40px;padding:14px 30px;font-size:30px;font-weight:700;color:#fff;background:linear-gradient(90deg,#FFB800 0%%,#FF5A1F 55%%,#FF2E8A 100%%)}
.mono{position:absolute;left:72px;top:%(mono)dpx;font-family:'JetBrains Mono',monospace;font-size:40px;color:#C3CCFF;text-shadow:0 0 16px rgba(120,140,255,.7)}
.mono s{text-decoration:none;color:#6B75B8}
.mono b{display:inline-block;width:22px;height:44px;background:#A5B4FC;vertical-align:-8px;margin-left:6px}
h1{position:absolute;left:72px;right:40px;top:%(h1)dpx;font-size:%(h1s)dpx;line-height:1.02;font-weight:800;letter-spacing:-3px;color:#fff;text-shadow:0 0 24px rgba(255,255,255,.25),0 4px 30px rgba(0,0,0,.7)}
h1 em{font-style:normal;text-shadow:none;background:linear-gradient(90deg,#FFB800 0%%,#FF5A1F 55%%,#FF2E8A 100%%);-webkit-background-clip:text;color:transparent}
.name{position:absolute;display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.14);border:1.5px solid rgba(255,255,255,.35);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);color:#fff;border-radius:40px;
 padding:10px 22px 10px 12px;font-size:28px;font-weight:800;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.name i{width:22px;height:22px;border-radius:50%%;display:block}
.name small{font-size:20px;font-weight:600;color:rgba(255,255,255,.75)}
.info{position:absolute;left:72px;right:72px;top:%(info)dpx}
.eyebrow{font-size:30px;font-weight:600;color:#C3CCFF;margin-bottom:12px}
.meta{display:flex;align-items:center;gap:20px;flex-wrap:wrap;font-size:34px;font-weight:700}
.meta .dot{color:#6B75B8}
.free{font-size:26px;font-weight:700;padding:10px 20px;border-radius:30px;background:#4A6CF7}
.lead{font-size:30px;color:rgba(255,255,255,.85);font-weight:500;margin-bottom:14px}
.date{font-size:64px;font-weight:800;letter-spacing:-2px}
.date span{color:#A5B4FC}
.row{display:flex;justify-content:center;align-items:center;gap:26px;margin-top:22px}
.place{font-size:34px;color:rgba(255,255,255,.8);font-weight:600}
.cta{background:#4A6CF7;border-radius:44px;padding:18px 32px;font-size:32px;font-weight:700}
"""


def heads(L):
    p, m = L["pol"], L["mx"]
    ph = (p["left"] + PCUT[2] * p["h"] * PCUT[0] / PCUT[1], p["top"] + PCUT[3] * p["h"])
    mh = (m["left"] + MCUT[2] * m["h"] * MCUT[0] / MCUT[1], m["top"] + MCUT[3] * m["h"])
    return ph, mh


def net_svg(L):
    rnd = random.Random(3)
    s, ox, oy = L["s"], L["ox"], L["oy"]
    pts = [(x * K * s - ox, y * K * s - oy) for x, y in FACES]
    keep = [i for i, (x, y) in enumerate(pts) if 30 < x < L['W'] - 30 and 0 < y < L['H']]
    def hidden(x, y):
        for q, c in ((L["pol"], PCUT), (L["mx"], MCUT)):
            w = q["h"] * c[0] / c[1]
            if q["left"] - 40 < x < q["left"] + w + 40 and y > q["top"] + q["h"] * .3:
                return True
        return False
    keep = [i for i in keep if not hidden(*pts[i])]
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
        out.append(f'<path d="M{x1:.0f},{y1:.0f} Q{mx:.0f},{my:.0f} {x2:.0f},{y2:.0f}" stroke="#C7CEFF" stroke-width="1.5" fill="none" opacity=".35"/>')
    # к Полине и Максу — толстые светящиеся линии
    for hx, hy in heads(L):
        hx, hy = round(hx), round(hy)
        near = sorted(pts, key=lambda p: (p[0] - hx) ** 2 + (p[1] - hy) ** 2)[0:6]
        for x, y in near:
            out.append(f'<path d="M{hx},{hy} Q{(hx+x)/2:.0f},{min(hy,y)-60:.0f} {x:.0f},{y:.0f}" stroke="url(#gl)" stroke-width="3" fill="none" opacity=".85"/>')
    for k, (x, y) in enumerate(pts):
        c = COLORS[k % len(COLORS)]
        r = round(FW[k] * L['s'] * .62) if k < len(FW) else 40
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="none" stroke="{c}" stroke-width="2.5" opacity=".6"/>')
        out.append(f'<circle cx="{x + r * .7:.0f}" cy="{y - r * .7:.0f}" r="8" fill="{c}"/>')
    W, H = L["W"], L["H"]
    defs = '<defs><linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="#F59E0B"/><stop offset="1" stop-color="#EC4899"/></linearGradient></defs>'
    return f'<svg class="net" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs}{"".join(out)}</svg>'


def deco_svg(L, zones):
    """Сеть в пустых зонах сторис — в том же стиле, что связи на фото: кольца с точкой и дуги."""
    rnd = random.Random(5)
    W, H = L["W"], L["H"]
    pts = []
    for zi, (y0, y1, n) in enumerate(zones):
        cols = n
        for k in range(n):
            x = int((k + .5) * (W / cols) + rnd.randint(-50, 50))
            pts.append((x, rnd.randint(y0, y1), rnd.randint(26, 46), "#FFFFFF"))
    # точки сети на фото — чтобы дуги уходили к людям
    s_, ox, oy = L["s"], L["ox"], L["oy"]
    faces = [(x * s_ - ox, y * s_ - oy) for x, y in FACES]
    faces = [f for f in faces if 40 < f[0] < W - 40]
    out = []
    def arc(a, b, grad, op, lift=50):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - lift
        st = '#FFFFFF'
        out.append(f'<path d="M{a[0]:.0f},{a[1]:.0f} Q{mx:.0f},{my:.0f} {b[0]:.0f},{b[1]:.0f}" stroke="{st}" stroke-width="{2 if grad else 1.5}" fill="none" opacity="{op}"/>')
    for i, p in enumerate(pts):
        d = sorted(range(len(pts)), key=lambda j: (pts[j][0] - p[0]) ** 2 + (pts[j][1] - p[1]) ** 2)
        for n_, j in enumerate(d[1:3]):
            if i < j:
                arc(p, pts[j], (i + n_) % 3 == 0, .16 if (i + n_) % 3 == 0 else .1, rnd.choice([-40, 40, 60]))
    # длинные дуги от верхней/нижней сети к людям на фото
    for x, y, r, c in pts:
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c}" stroke-width="2" opacity=".14"/>')
        out.append(f'<circle cx="{x + r * .7:.0f}" cy="{y - r * .7:.0f}" r="6" fill="{c}" opacity=".25"/>')
    defs = '<defs><linearGradient id="dg" x1="0" x2="1"><stop offset="0" stop-color="#FFB800"/><stop offset=".55" stop-color="#FF5A1F"/><stop offset="1" stop-color="#FF2E8A"/></linearGradient></defs>'
    return f'<svg class="net" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs}{"".join(out)}</svg>'


def person(img, pos):
    a = (pos["fy"] + 220 - pos["top"]) / pos["h"] * 100
    b = (pos["fy"] + 370 - pos["top"]) / pos["h"] * 100
    m = f"-webkit-mask-image:linear-gradient(180deg,#000 {a:.1f}%,transparent {b:.1f}%)"
    return f'<div class="person" style="left:{pos["left"]}px;top:{pos["top"]}px;height:{pos["h"]}px;{m}"><img src="{img}"></div>'


for fmt, L in FMT.items():
    W, H = L["W"], L["H"]
    bw = int(2016 * L["s"])
    g = L["g"]
    css = CSS % dict(W=W, H=H, bx=-L["ox"], by=-L["oy"], bw=bw, top=L["top"], pt=L["top"] + 4,
                     mono=L["mono"], h1=L["h1"], h1s=L["h1s"], info=L["info"], g1=g[0], g2=g[1], g3=g[2], g4=g[3])
    ph, mh = heads(L)
    body = f"""<img class="bg" src="group.src.jpg"><div class="shade"></div>
<div class="glow"></div>{deco_svg(L, [(50, 230, 6), (1640, 1760, 5), (1790, 1890, 6)]) if fmt == "9x16" else ""}
{net_svg(L)}
{person('max_cut.png', L['mx'])}{person('polina_cut.png', L['pol'])}
<div class="name" style="left:{L['polname'][0]}px;top:{L['polname'][1]}px"><i style="background:#EC4899"></i>Полина <small>TEXTURA</small></div>
<div class="name" style="left:{L['maxname'][0]}px;top:{L['maxname'][1]}px"><i style="background:#4A6CF7"></i>Максим <small>Co.Space</small></div>
<div class="logo">{LOGO}</div><div class="pill">Тбилиси</div>
<div class="info"><div class="eyebrow">Сила сообществ · для лидеров</div>
<div class="meta"><span>Сбор 19:00 · начало 19:30</span><span class="dot">·</span><span>Ginger Hotel</span><span class="free">Вход свободный</span></div></div>
<h1>Ведёшь сообщество?<br>Расскажи о нём<br><em>27&nbsp;ноября</em></h1>"""
    (HERE / f"leaders-{fmt}.html").write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>')
print("ok")
