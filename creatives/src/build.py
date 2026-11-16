"""Генератор рекламных креативов Co.Space.

python3 build.py  -> пишет HTML в ./html, затем render.js делает PNG.
Каждый креатив — в двух размерах: 4:5 (1080x1350) и 9:16 (1080x1920).
"""
import math
import pathlib
import random

HERE = pathlib.Path(__file__).parent
OUT = HERE / "html"
OUT.mkdir(exist_ok=True)
LOGO = (HERE / "co-logo-white.svg").read_text()

DARK = "#1A1A2E"
BLUE = "#4A6CF7"
LILAC = "#A5B4FC"
ORANGE = "#F59E0B"
PINK = "#EC4899"
GREEN = "#10B981"
WHITE = "#FFFFFF"

TBS = dict(city="Тбилиси", date="27 ноября · 19:00", place="Ginger Hotel")
BUS = dict(city="Батуми", date="30 ноября · 19:00", place="Ресторан в центре Батуми")


# ---------- визуалы (SVG, рисуются в квадрате 600x600) ----------

def node(x, y, r, c, halo=True):
    h = f'<circle cx="{x}" cy="{y}" r="{r*1.6:.1f}" fill="{c}" opacity=".18"/>' if halo else ""
    return h + f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>'


def line(a, b, op=.35, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
            f'stroke="#C7CEFF" stroke-width="2" opacity="{op}"{d}/>')


def vis_hub():
    """Лидер в центре, вокруг — его люди."""
    cx, cy = 300, 300
    cols = [BLUE, LILAC, PINK, GREEN, WHITE, BLUE, ORANGE, LILAC, GREEN, PINK]
    pts = []
    for i, c in enumerate(cols):
        a = i / len(cols) * 2 * math.pi - math.pi / 2
        rad = 210 if i % 2 == 0 else 165
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a), 16 + (i * 7) % 18, c))
    s = '<circle cx="300" cy="300" r="250" fill="none" stroke="#C7CEFF" stroke-width="2" opacity=".12"/>'
    s += '<circle cx="300" cy="300" r="140" fill="none" stroke="#C7CEFF" stroke-width="2" opacity=".18" stroke-dasharray="4 10"/>'
    for x, y, r, c in pts:
        s += line((cx, cy), (x, y), .3)
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        s += line(a[:2], b[:2], .15)
    for x, y, r, c in pts:
        s += node(round(x), round(y), r, c)
    s += node(cx, cy, 62, ORANGE)
    s += f'<circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="{ORANGE}" stroke-width="3" opacity=".35"/>'
    return s


def vis_lonely():
    """Одна точка отдельно — и тёплый круг связанных точек."""
    s = node(80, 470, 18, "#6B7090", halo=False)
    s += '<circle cx="80" cy="470" r="44" fill="none" stroke="#6B7090" stroke-width="2" stroke-dasharray="3 9" opacity=".7"/>'
    s += line((120, 450), (250, 380), .35, "2 10")
    pts = [(330, 170, 34, ORANGE), (470, 120, 22, WHITE), (520, 260, 40, BLUE), (400, 320, 28, PINK),
           (280, 330, 20, GREEN), (450, 440, 24, LILAC), (560, 410, 16, WHITE), (340, 460, 14, ORANGE)]
    edges = [(0, 1), (1, 2), (0, 3), (2, 3), (3, 4), (0, 4), (3, 5), (2, 6), (5, 6), (4, 7), (5, 7)]
    for i, j in edges:
        s += line(pts[i][:2], pts[j][:2], .4)
    for x, y, r, c in pts:
        s += node(x, y, r, c)
    return s


def vis_ai():
    """Холодная сетка пикселей распадается в тёплые живые точки."""
    s = ""
    rnd = random.Random(7)
    for gx in range(7):
        for gy in range(9):
            x, y = 30 + gx * 34, 60 + gy * 56
            op = max(0.08, 0.55 - gx * 0.07)
            s += f'<rect x="{x}" y="{y}" width="20" height="20" rx="3" fill="#8890B8" opacity="{op:.2f}"/>'
    pts = []
    cols = [BLUE, ORANGE, PINK, GREEN, LILAC, WHITE, BLUE, ORANGE]
    for i, c in enumerate(cols):
        pts.append((330 + rnd.randint(0, 230), 70 + i * 62 + rnd.randint(-15, 15), rnd.randint(14, 34), c))
    for i in range(len(pts) - 1):
        s += line(pts[i][:2], pts[i + 1][:2], .35)
    s += line(pts[0][:2], pts[3][:2], .2) + line(pts[2][:2], pts[6][:2], .2) + line(pts[4][:2], pts[7][:2], .2)
    for x, y, r, c in pts:
        s += node(x, y, r, c)
    return s


def svg(inner, w):
    return f'<svg class="vis" width="{w}" height="{w}" viewBox="0 0 600 600">{inner}</svg>'


def chips(items):
    cols = [ORANGE, BLUE, PINK, GREEN, LILAC, WHITE]
    out = []
    for i, t in enumerate(items):
        rot = [-4, 3, -2, 5, -3, 2][i % 6]
        out.append(f'<span class="chip" style="transform:rotate({rot}deg)"><i style="background:{cols[i % 6]}"></i>{t}</span>')
    return '<div class="chips">' + "".join(out) + "</div>"


# ---------- шаблон ----------

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;color:#fff;background:%(dark)s;position:relative;
 background:
  radial-gradient(900px 700px at 95%% 5%%, rgba(74,108,247,.55), transparent 60%%),
  radial-gradient(700px 600px at -10%% 100%%, rgba(74,108,247,.30), transparent 60%%),
  %(dark)s;}
.logo{position:absolute;left:72px;top:%(top)dpx;width:112px}
.logo svg{width:112px;height:auto;display:block}
.pill{position:absolute;right:72px;top:%(pilltop)dpx;border:2px solid rgba(255,255,255,.55);border-radius:40px;
 padding:12px 26px;font-size:30px;font-weight:500}
.vis{position:absolute}
.text{position:absolute;left:72px;right:72px;bottom:%(bottom)dpx}
.eyebrow{font-size:31px;font-weight:500;color:%(lilac)s;margin-bottom:22px}
h1{font-size:%(h1)dpx;line-height:1.02;font-weight:700;letter-spacing:-2px}
h1 em{font-style:normal;color:%(lilac)s}
.sub{font-size:34px;line-height:1.3;color:rgba(255,255,255,.82);margin-top:24px;font-weight:500}
.date{font-size:56px;font-weight:600;color:%(lilac)s;margin-top:36px;letter-spacing:-1px}
.place{font-size:38px;color:rgba(255,255,255,.75);margin-top:10px;font-weight:500}
.cta{display:inline-block;background:%(blue)s;border-radius:44px;padding:22px 36px;font-size:36px;font-weight:600;margin-top:40px}
.chips{display:flex;flex-wrap:wrap;gap:28px 22px;position:absolute;left:72px;right:72px}
.chip{display:inline-flex;align-items:center;gap:14px;background:rgba(255,255,255,.08);border:2px solid rgba(255,255,255,.18);
 border-radius:50px;padding:22px 38px;font-size:52px;font-weight:600}
.chip i{width:24px;height:24px;border-radius:50%%;display:block}
"""


def page(c, fmt):
    W, H = 1080, (1350 if fmt == "4x5" else 1920)
    story = fmt == "9x16"
    # в 9:16 верх (~250px) и низ (~340px) закрывают имя страницы и кнопка
    top = 270 if story else 60
    bottom = 380 if story else 76
    css = CSS % dict(W=W, H=H, dark=DARK, top=top, pilltop=top + 4, bottom=bottom,
                     lilac=LILAC, blue=BLUE, h1=c.get("h1", 112))
    ev = c["event"]
    vis_y = c.get("vis_y_story" if story else "vis_y", 120)
    vis_w = c.get("vis_w", 560)
    vis_x = c.get("vis_x", W - vis_w - 40)
    body = f'<div class="logo">{LOGO}</div><div class="pill">{ev["city"]}</div>'
    if c.get("vis"):
        body += svg(c["vis"], vis_w).replace('class="vis"', f'class="vis" style="left:{vis_x}px;top:{vis_y}px"')
    if c.get("chips"):
        cy = c.get("chips_y_story" if story else "chips_y", 220)
        body += chips(c["chips"]).replace('class="chips"', f'class="chips" style="top:{cy}px"')
    sub = f'<div class="sub">{c["sub"]}</div>' if c.get("sub") else ""
    date = c.get("date", ev["date"])
    place = c.get("place", ev["place"])
    body += f'''<div class="text">
      <div class="eyebrow">{c["eyebrow"]}</div>
      <h1>{c["h1_text"]}</h1>{sub}
      <div class="date">{date}</div>
      <div class="place">{place}</div>
      <div class="cta">{c.get("cta", "Вход свободный")}</div>
    </div>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>', W, H


CREATIVES = [
    dict(id="tbs-ru-c-leaders", event=TBS, vis=vis_hub(), vis_y=70, vis_y_story=330, vis_w=470,
         eyebrow="Сила сообществ · для лидеров",
         h1_text="Ведёшь сообщество? Расскажи о нём <em>27&nbsp;ноября</em>", h1=96,
         date="Сбор 19:00 · начало 19:30"),
    dict(id="tbs-ru-d-loneliness", event=TBS, vis=vis_lonely(), vis_y=80, vis_y_story=330, vis_w=560,
         eyebrow="Сила сообществ · вечер комьюнити",
         h1_text="Сообщество сильнее одиночества", h1=104),
    dict(id="tbs-ru-e-hobbies", event=TBS, chips=["Бег", "Книги", "IT", "Шахматы", "Кино"],
         chips_y=190, chips_y_story=430,
         eyebrow="Сила сообществ · вечер комьюнити",
         h1_text="Найди своих — <em>найдёшь своё</em>", h1=108,
         sub="Сообщества Тбилиси — в одном зале. Знакомства за столами."),
    dict(id="tbs-ru-f-ai", event=TBS, vis=vis_ai(), vis_y=70, vis_y_story=320, vis_w=540,
         eyebrow="Сила сообществ · вживую",
         h1_text="ИИ ускоряет всё.<br>А найти своих —<br><em>всё сложнее</em>", h1=92),
    dict(id="bus-ru-d-loneliness", event=BUS, vis=vis_lonely(), vis_y=80, vis_y_story=330, vis_w=560,
         eyebrow="Сила сообществ · Батуми",
         h1_text="Сообщество сильнее одиночества", h1=104,
         place="Ресторан в центре · адрес — после записи"),
    dict(id="bus-ru-e-hobbies", event=BUS, chips=["Бег", "Книги", "IT", "Шахматы", "Кино"],
         chips_y=190, chips_y_story=430,
         eyebrow="Сила сообществ · Батуми",
         h1_text="Найди своих <em>в&nbsp;Батуми</em>", h1=112,
         sub="Сообщества города и знакомства за столами.",
         place="Ресторан в центре · адрес — после записи"),
]

if __name__ == "__main__":
    for c in CREATIVES:
        for fmt in ("4x5", "9x16"):
            html, W, H = page(c, fmt)
            (OUT / f'{c["id"]}-{fmt}.html').write_text(html)
    print("ok", len(CREATIVES) * 2)
