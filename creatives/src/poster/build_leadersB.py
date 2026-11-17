"""Креатив для лидеров в стиле B: синяя плашка с овалом (внутри и снаружи — общее фото),
Полина и Максим крупно по бокам поверх плашки, обрезаны только нижним краем кадра."""
import pathlib

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
PCUT = (933, 1146, .403, .170, .1955)  # w, h, центр лица x/y (доли), ширина лица/высота
MCUT = (902, 1059, .395, .229, .326)
DEPTH = (1 - .229) / .326  # сколько «лиц» от центра лица до низа вырезки Макса (≈2.37)
CREAM = "#F1ECE2"
BLUE = "#3B4BD0"

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:#111}
.abs{position:absolute}
.bg{position:absolute;inset:0;background:url(group.src.jpg) center/cover;filter:saturate(.75) brightness(.9)}
.oval{position:absolute;overflow:hidden;border-radius:50%%}
.oval div{position:absolute;inset:0;background:url(group.src.jpg) %(opos)s/%(osize)s no-repeat;filter:saturate(.8)}
.cream{color:#F1ECE2}
.caps{font-weight:800;text-transform:uppercase;line-height:.95;letter-spacing:-.02em}
.sp{font-weight:600;text-transform:uppercase;letter-spacing:.28em}
.big{font-weight:600;letter-spacing:-.04em;line-height:.95}
.person{position:absolute;overflow:hidden;filter:drop-shadow(0 20px 40px rgba(0,0,0,.45))}
.person img{position:absolute;left:0;top:0;display:block}
"""


def person_bottom(cut, F, fx, H, img):
    """Человек, у которого низ вырезки совпадает с низом кадра; лицо шириной F."""
    h = F / cut[4]
    w = h * cut[0] / cut[1]
    visible = cut[3] * h + DEPTH * F  # от верха до уровня «пояса» Макса
    left = fx - cut[2] * w
    return (f'<div class="person" style="left:{left:.0f}px;top:{H - visible:.0f}px;width:{w:.0f}px;height:{visible:.0f}px">'
            f'<img src="{img}" style="height:{h:.0f}px"></div>')


def build(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    if story:
        px, py, pw, ph = 70, 230, 940, 1560
        cx, cy, rx, ry = 540, 660, 360, 300
        F, mfx, pfx = 175, 180, 905
        hy, hs = 1010, 84
    else:
        px, py, pw, ph = 70, 60, 940, 1230
        cx, cy, rx, ry = 540, 400, 330, 235
        F, mfx, pfx = 150, 160, 915
        hy, hs = 690, 76
    hole = (f'M{px},{py} h{pw} v{ph} h-{pw} Z '
            f'M{cx - rx},{cy} a{rx},{ry} 0 1,0 {2 * rx},0 a{rx},{ry} 0 1,0 -{2 * rx},0 Z')
    s = ['<div class="bg"></div>']
    s.append(f'<div class="oval" style="left:{cx - rx}px;top:{cy - ry}px;width:{2 * rx}px;height:{2 * ry}px"><div></div></div>')
    s.append(f'<svg class="abs" style="left:0;top:0" width="1080" height="{H}"><path d="{hole}" fill="{BLUE}" fill-rule="evenodd"/></svg>')
    # верх
    s.append(f'<div class="abs cream caps" style="left:{px + 44}px;top:{py + 44}px;font-size:36px">ПТ 27 НОЯБРЯ<br>СБОР 19:00 · НАЧАЛО 19:30<br>GINGER HOTEL</div>')
    s.append(f'<div class="abs cream" style="right:{1080 - px - pw + 44}px;top:{py + 40}px;text-align:right">'
             f'<div class="caps" style="font-size:52px">ТБИЛИСИ</div><div style="font-size:24px;font-weight:600;margin-top:8px">вход свободный</div></div>')
    # заголовок
    s.append(f'<div class="abs cream big" style="left:{px + 44}px;right:{1080 - px - pw + 44}px;top:{hy}px;font-size:{hs}px">'
             f'Ведёшь сообщество?<br>Расскажи о нём<br>27&nbsp;ноября</div>')
    s.append(f'<div class="abs cream sp" style="left:{px + 44}px;top:{hy - 38}px;font-size:20px">Сила сообществ · вечер для лидеров</div>')
    # люди по бокам поверх плашки
    s.append(person_bottom(MCUT, F, mfx, H, "max_cut.png"))
    s.append(person_bottom(PCUT, F, pfx, H, "polina_cut.png"))
    # подписи и логотип по центру между ними
    ly = H - (250 if story else 205)
    s.append(f'<div class="abs cream" style="left:0;right:0;top:{ly}px;text-align:center">'
             f'<div class="sp" style="font-size:17px">ведут</div>'
             f'<div class="caps" style="font-size:26px;margin-top:8px;line-height:1.15">Максим<br><span style="font-size:17px;font-weight:600;letter-spacing:.15em">CO.SPACE</span><br>Полина<br><span style="font-size:17px;font-weight:600;letter-spacing:.15em">TEXTURA</span></div></div>')
    logo = LOGO.replace('width="77"', 'width="90"').replace('height="38"', 'height="44"').replace('fill="white"', f'fill="{CREAM}"')
    s.append(f'<div class="abs" style="left:495px;top:{H - (330 if story else 275)}px">{logo}</div>')
    # фото в овале: показываем людей крупнее
    osize = "1500px auto" if not story else "1650px auto"
    opos = "-330px -170px" if not story else "-380px -140px"
    css = CSS % dict(H=H, opos=opos, osize=osize)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(s)}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"leadersB-{fmt}.html").write_text(build(fmt))
print("ok")
