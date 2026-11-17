"""«Сообщество сильнее одиночества»: сверху наше общее фото, снизу цвет, одна девушка вышла из толпы, провод тянется к ней."""
import pathlib
HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
RED, BLUE, INK = "#E8323C", "#2F5BFF", "#2A0608"

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:%(red)s}
.abs{position:absolute}
.photo{position:absolute;left:0;top:0;width:1080px;height:%(ph)dpx;background:url(group_left.jpg) 0 %(py)dpx/1080px auto no-repeat;filter:saturate(.55) contrast(1.05)}
.lone{position:absolute;filter:drop-shadow(18px 22px 14px rgba(60,0,0,.45))}
.lone img{height:100%%;display:block;-webkit-mask-image:linear-gradient(180deg,#000 90%%,transparent 100%%)}
h1{position:absolute;left:90px;font-weight:500;color:#fff;letter-spacing:-.045em;line-height:.9}
.body{position:absolute;left:92px;width:%(bw)dpx;color:%(ink)s;font-size:21px;line-height:1.3;font-weight:500}
.body b{font-weight:800}
.tag{position:absolute;color:#fff;font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:22px;text-shadow:0 2px 12px rgba(0,0,0,.5)}
"""


def build(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    ph = 860 if story else 600
    py = -300 if story else -260
    lh = 500 if story else 400
    lx, ly = (620, ph + 50) if story else (660, ph + 25)
    hy = (1330 if story else 925)
    hs = 112 if story else 100
    by = hy + hs * 3 * .9 + 26
    top = 270 if story else 56
    # провод: от фото (коннектор у края) вниз, петлёй мимо девушки, вправо за край
    sx, sy = 880, ph - 10
    cable1 = (f'M{sx},{sy} C{sx + 60},{sy + 260} {1040},{ly + lh - 40} {960},{ly + lh + 120} '
              f'S{760},{H - 120} {1120},{H - 60}')
    # второй провод: слева, к руке девушки — почти дотягивается
    hx, hy2 = lx + 40, ly + lh * .55
    cable2 = f'M-40,{hy2 + 160} C{140},{hy2 + 200} {260},{hy2 - 40} {hx - 110},{hy2 + 20}'
    sq = lambda x, y, r: f'<rect x="{x - 15}" y="{y - 15}" width="30" height="30" rx="4" fill="{BLUE}" transform="rotate({r} {x} {y})"/>'
    svg = (f'<svg class="abs" style="left:0;top:0" width="1080" height="{H}">'
           f'<path d="{cable1}" stroke="{BLUE}" stroke-width="6" fill="none" stroke-linecap="round"/>'
           f'<path d="{cable2}" stroke="{BLUE}" stroke-width="6" fill="none" stroke-linecap="round"/>'
           f'{sq(sx, sy, 20)}{sq(hx - 110, hy2 + 20, -25)}</svg>')
    logo = LOGO.replace('width="77"', 'width="104"').replace('height="38"', 'height="51"')
    body = f"""<div class="photo"></div>
<div class="abs" style="left:92px;top:{ph + 60}px">{logo}</div>
<div class="tag" style="left:92px;top:{ph + 140}px;text-shadow:none;font-size:24px">Тбилиси<br>27 ноября</div>
<div class="lone" style="left:{lx}px;top:{ly}px;height:{lh}px"><img src="lone_a.png"></div>
{svg}
<h1 style="top:{hy}px;font-size:{hs}px">сообщество<br>сильнее<br>одиночества</h1>
<div class="body" style="top:{by:.0f}px"><b>Сила сообществ</b> — вечер, где сообщества Тбилиси знакомятся вживую.
<b>27 ноября</b>, сбор 19:00, начало 19:30. <b>Ginger Hotel.</b> Вход свободный, нужна регистрация.</div>"""
    css = CSS % dict(H=H, red=RED, ph=ph, py=py, ink=INK, bw=600 if story else 780)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"lonely-{fmt}.html").write_text(build(fmt))
print("ok")
