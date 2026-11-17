"""Для лидеров в стиле B: синяя плашка, в овале — общее фото и Полина с Максимом
(крупно, низ уходит за край овала — без растворения)."""
import math
import pathlib

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
PCUT = (933, 1146, .403, .170, .1955)
MCUT = (902, 1059, .395, .229, .326)
DEPTH = (1 - .229) / .326
CREAM = "#F1ECE2"
BLUE = "#3B4BD0"

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:#111}
.abs{position:absolute}
.bg{position:absolute;inset:0;background:url(group.src.jpg) center/cover;filter:saturate(.7) brightness(.95)}
.oval{position:absolute;overflow:hidden;border-radius:50%%}
.oval .ph{position:absolute;background:url(group.src.jpg) center/cover;filter:saturate(.7) brightness(.72)}
.person{position:absolute}
.person img{height:100%%;display:block}
.cream{color:#F1ECE2}
.caps{font-weight:800;text-transform:uppercase;line-height:.92;letter-spacing:-.02em}
.sp{font-weight:600;text-transform:uppercase;letter-spacing:.2em}
.big{font-weight:600;letter-spacing:-.04em;line-height:.88}
"""


def place(cut, F, fx, fy, img):
    h = F / cut[4]
    w = h * cut[0] / cut[1]
    return f'<div class="person" style="left:{fx - cut[2] * w:.0f}px;top:{fy - cut[3] * h:.0f}px;height:{h:.0f}px"><img src="{img}"></div>'


def build(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    px, py, pw, ph = (90, 230, 900, 1430) if story else (90, 70, 900, 1210)
    cx, cy, rx, ry = (px + 450, py + 500, 370, 360) if story else (px + 450, py + 400, 360, 300)
    F = 150 if story else 135
    mfx, pfx = cx - 200, cx + 200
    # лицо ставим так, чтобы низ вырезки Макса ушёл ниже края овала
    fy = cy + ry - DEPTH * F + 6  # низ Макса — ниже самой нижней точки овала
    s = ['<div class="bg"></div>']
    inner = f'<div class="ph" style="left:{-(cx - rx)}px;top:{-(cy - ry)}px;width:1080px;height:{H}px"></div>'
    people = place(MCUT, F, mfx, fy, "max_cut.png") + place(PCUT, F, pfx, fy, "polina_cut.png")
    s.append(f'<div class="oval" style="left:{cx - rx}px;top:{cy - ry}px;width:{2 * rx}px;height:{2 * ry}px">'
             f'{inner}<div style="position:absolute;left:{-(cx - rx)}px;top:{-(cy - ry)}px;width:1080px;height:{H}px">{people}</div></div>')
    hole = f'M{px},{py} h{pw} v{ph} h-{pw} Z M{cx - rx},{cy} a{rx},{ry} 0 1,0 {2 * rx},0 a{rx},{ry} 0 1,0 -{2 * rx},0 Z'
    s.append(f'<svg class="abs" style="left:0;top:0" width="1080" height="{H}"><path d="{hole}" fill="{BLUE}" fill-rule="evenodd"/></svg>')
    # верх
    s.append(f'<div class="abs cream caps" style="left:{px + 46}px;top:{py + 50}px;font-size:38px">ПТ 27 НОЯБРЯ<br>19:00<br>GINGER HOTEL</div>')
    s.append(f'<div class="abs cream" style="right:{1080 - px - pw + 46}px;top:{py + 46}px;text-align:right">'
             f'<div class="caps" style="font-size:50px">ТБИЛИСИ</div><div style="font-size:24px;font-weight:600;margin-top:8px">вход свободный</div></div>')
    # под овалом
    by = cy + ry + (40 if story else 28)
    s.append(f'<div class="abs cream caps" style="left:{px + 46}px;top:{by + 8}px;font-size:32px">СИЛА<br>СООБЩЕСТВ.<br>ВЕЧЕР ДЛЯ<br>ЛИДЕРОВ</div>')
    s.append(f'<div class="abs cream big" style="right:{1080 - px - pw + 46}px;top:{by}px;font-size:{84 if story else 76}px;text-align:right">'
             f'ведёшь<br>сообщество?<br>расскажи о нём<br>27 ноября</div>')
    sy = py + ph - (200 if story else 158)
    s.append(f'<div class="abs cream" style="left:{px}px;width:{pw}px;top:{sy}px;text-align:center;font-size:18px">'
             f'<div class="sp">вечер ведут</div><div class="sp" style="font-size:24px;margin-top:8px">Полина · TEXTURA &nbsp;/&nbsp; Максим · Co.Space</div></div>')
    logo = LOGO.replace('width="77"', 'width="96"').replace('height="38"', 'height="47"').replace('fill="white"', f'fill="{CREAM}"')
    s.append(f'<div class="abs" style="left:{px + pw // 2 - 48}px;top:{py + ph - 80}px">{logo}</div>')
    css = CSS % dict(H=H)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(s)}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"leadersOval-{fmt}.html").write_text(build(fmt))
print("ok")
