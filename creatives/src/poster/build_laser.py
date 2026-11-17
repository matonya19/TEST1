"""Для лидеров в стиле «лазерной сети»: красное свечение, лучи между людьми, минимум текста."""
import pathlib, random

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
FACES = [(171, 630), (192, 528), (369, 522), (447, 446), (521, 648), (636, 516), (650, 786), (692, 418), (793, 560),
         (812, 816), (903, 469), (984, 468), (1009, 596), (1133, 538), (1182, 392), (1258, 557), (1396, 506),
         (1463, 492), (1558, 569), (1740, 490), (1917, 494)]
PCUT = (933, 1146, .403, .170, .1955)
MCUT = (902, 1059, .395, .229, .326)
DEPTH = (1 - .229) / .326

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:#140000;color:#fff}
.abs{position:absolute}
.bg{position:absolute;left:%(bx)dpx;top:%(by)dpx;width:%(bw)dpx;filter:brightness(.85) contrast(1.15)}
.fog{position:absolute;inset:0;background:
 radial-gradient(45%% 30%% at 12%% 8%%,rgba(20,0,0,.75),transparent 80%%),
 radial-gradient(55%% 35%% at 65%% 15%%,rgba(255,120,60,.35),transparent 70%%),
 radial-gradient(120%% 80%% at 50%% 40%%,transparent 35%%,rgba(25,0,0,.9) 100%%)}
.person{position:absolute;overflow:hidden;filter:drop-shadow(0 0 40px rgba(255,80,20,.35))}
.person img{position:absolute;left:0;top:0;display:block}
.txt{font-weight:500;letter-spacing:-.02em;line-height:1.02;text-shadow:0 2px 20px rgba(80,0,0,.6)}
.small{font-size:22px;font-weight:500;letter-spacing:.02em;color:rgba(255,255,255,.85)}
"""


def person_bottom(cut, F, fx, H, img):
    h = F / cut[4]
    w = h * cut[0] / cut[1]
    vis = cut[3] * h + DEPTH * F
    return (f'<div class="person" style="left:{fx - cut[2] * w:.0f}px;top:{H - vis:.0f}px;width:{w:.0f}px;height:{vis:.0f}px">'
            f'<img src="{img}" style="height:{h:.0f}px"></div>'), (fx, H - DEPTH * F)


def lasers(pts, W, H, seed):
    rnd = random.Random(seed)
    out = []
    pairs = set()
    n = len(pts) - 2
    for _ in range(7):
        i, j = rnd.sample(range(n), 2)
        pairs.add(tuple(sorted((i, j))))
    for hero in (n, n + 1):
        for j in rnd.sample(range(n), 3):
            pairs.add((j, hero))
    for i, j in pairs:
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2 - x1, y2 - y1
        n = (dx * dx + dy * dy) ** .5 or 1
        k = 2500 / n
        a = (x1 - dx * k, y1 - dy * k); b = (x2 + dx * k, y2 + dy * k)
        d = f'M{a[0]:.0f},{a[1]:.0f} L{b[0]:.0f},{b[1]:.0f}'
        out.append(f'<path d="{d}" stroke="#FF3A0A" stroke-width="7" opacity=".45" filter="url(#b8)"/>')
        out.append(f'<path d="{d}" stroke="#FFB070" stroke-width="1.6" opacity=".9"/>')
    for x, y in pts:
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="16" fill="#FF6A1A" opacity=".7" filter="url(#b8)"/>')
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="#FFE3B0"/>')
    defs = '<defs><filter id="b8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter></defs>'
    return f'<svg class="abs" style="left:0;top:0;mix-blend-mode:screen" width="{W}" height="{H}">{defs}{"".join(out)}</svg>'


def build(fmt):
    story = fmt == "9x16"
    W, H = 1080, (1920 if story else 1350)
    s_ = 1.3 if story else .93
    bw = 2016 * s_
    ox, oy = (bw - W) / 2 + (60 if story else 0), 0
    faces = [(x * s_ - ox, y * s_ - oy) for x, y in FACES]
    faces = [(x, y) for x, y in faces if 20 < x < W - 20]
    F = 160 if story else 135
    pm, hm = person_bottom(MCUT, F, 300, H, "max_red.png")
    pp, hp = person_bottom(PCUT, F, 790, H, "polina_red.png")
    pts = faces + [hm, hp]
    ty = 640 if story else 520
    body = f"""<img class="bg" src="group_red.jpg"><div class="fog"></div>
{lasers(pts, W, H, 7)}
{pm}{pp}
<div class="abs" style="left:50%;transform:translateX(-50%);top:{270 if story else 60}px">{LOGO}</div>
<div class="abs txt" style="left:90px;top:{ty}px;font-size:{64 if story else 58}px">Ведёшь сообщество?<br>Расскажи о нём<br>27 ноября в Тбилиси.</div>
<div class="abs small" style="left:90px;top:{ty + (64 if story else 58) * 3.1 + 18:.0f}px">Сила сообществ · Ginger Hotel · сбор 19:00 · вход свободный</div>
<div class="abs small" style="right:40px;bottom:{(H - hp[1]) + 40 if False else 0}px;display:none"></div>"""
    css = CSS % dict(H=H, bx=-ox, by=-oy, bw=bw)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"laser-{fmt}.html").write_text(build(fmt))
print("ok")
