"""Редакционный стиль по референсам: A — огромные обрезанные буквы, B — синяя плашка с овалом."""
import pathlib

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
PCUT = (933, 1146, .403, .170, .1955)  # w, h, центр лица x/y в долях, ширина лица / высота
MCUT = (902, 1059, .395, .229, .326)

BASE = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:#141633}
.abs{position:absolute}
.person{position:absolute}
.person img{height:100%%;display:block}
"""


def place(cut, F, fx, fy, img, fade=None):
    h = F / cut[4]
    w = h * cut[0] / cut[1]
    left, top = fx - cut[2] * w, fy - cut[3] * h
    m = ""
    if fade:
        a = (fy + fade[0] - top) / h * 100
        b = (fy + fade[1] - top) / h * 100
        m = f"-webkit-mask-image:linear-gradient(180deg,#000 {a:.1f}%,transparent {b:.1f}%);"
    return f'<div class="person" style="left:{left:.0f}px;top:{top:.0f}px;height:{h:.0f}px;{m}"><img src="{img}"></div>'


# ---------------- A: огромные буквы ----------------
A_CSS = """
body{background:#0D0D10}
.bg{position:absolute;inset:0;background:url(group.src.jpg) center/cover;filter:grayscale(1) brightness(.55) contrast(1.05);opacity:.5}
.sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,13,16,.75),rgba(13,13,16,.2) 35%,rgba(13,13,16,.45) 60%,rgba(13,13,16,.92))}
.L{position:absolute;font-weight:900;color:#FF6A1A;line-height:.8;letter-spacing:-.04em}
.t{color:rgba(255,255,255,.72);font-weight:600;line-height:1.05;letter-spacing:-.01em;text-shadow:0 2px 14px rgba(0,0,0,.8)}
.tb{color:#fff;font-weight:800;line-height:.95;letter-spacing:-.02em;text-shadow:0 2px 14px rgba(0,0,0,.8)}
.title{position:absolute;left:0;right:0;text-align:center;font-weight:900;color:#FF6A1A;letter-spacing:-.05em;line-height:.8}
.logo svg{display:block}
.logo svg path{fill:#fff}
"""


def poster_a(fmt):
    # тёмная версия: оранжевые буквы, ч/б фон
    story = fmt == "9x16"
    H = 1920 if story else 1350
    F = 178 if story else 165
    fy = 700 if story else 430
    s = []
    s.append('<div class="bg"></div><div class="sh"></div>')
    # задние буквы
    if story:
        s.append('<div class="L" style="left:-110px;top:-60px;font-size:760px">С</div>')
        s.append('<div class="L" style="right:-170px;top:330px;font-size:760px">Х</div>')
    else:
        s.append('<div class="L" style="left:-90px;top:-70px;font-size:560px">С</div>')
        s.append('<div class="L" style="right:-140px;top:150px;font-size:560px">Х</div>')
    fade = (330, 520) if story else (300, 470)
    s.append(place(MCUT, F, 255, fy, "max_cut.png", fade))
    s.append(place(PCUT, F, 785, fy, "polina_cut.png", fade))
    # передние нижние буквы
    if story:
        s.append('<div class="L" style="left:-40px;top:1640px;font-size:760px">ВО</div>')
    else:
        s.append('<div class="L" style="left:-30px;top:1200px;font-size:560px">ВО</div>')
    # центр
    ty = 1020 if story else 690
    ts = 300 if story else 250
    s.append(f'<div class="title" style="top:{ty}px;font-size:{ts}px">СВОИХ</div>')
    s.append(f'<div class="abs t" style="left:28px;top:{ty - 34}px;font-size:22px">27.11</div>')
    s.append(f'<div class="abs t" style="right:28px;top:{ty - 34}px;font-size:22px">Тбилиси</div>')
    tl = (270 + 95) if story else 150
    s.append(f'<div class="abs t" style="left:0;right:0;top:{tl}px;text-align:center;font-size:{32 if story else 28}px">ИИ ускоряет всё.<br>А найти своих — всё сложнее</div>')
    by = ty + ts * .8 + 26
    s.append(f'<div class="abs tb" style="left:72px;top:{by:.0f}px;font-size:24px">СИЛА СООБЩЕСТВ &nbsp;·&nbsp; ПОЛИНА · TEXTURA &nbsp;·&nbsp; МАКСИМ · CO.SPACE</div>')
    ds = 64 if story else 54
    s.append(f'<div class="abs" style="left:72px;top:{by + 50:.0f}px"><div class="tb" style="font-size:{ds}px">27 НОЯБРЯ<br>ПЯТНИЦА</div><div class="t" style="font-size:{ds}px">19:00</div></div>')
    s.append(f'<div class="abs tb" style="left:640px;top:{by + 56:.0f}px;font-size:{36 if story else 32}px">GINGER HOTEL<br>ВХОД<br>СВОБОДНЫЙ</div>')
    ly = 270 if story else 60
    s.append(f'<div class="abs logo" style="left:50%;transform:translateX(-50%);top:{ly}px">{LOGO.replace("width=\"77\"", "width=\"120\"").replace("height=\"38\"", "height=\"59\"")}</div>')
    css = BASE % dict(H=H) + A_CSS
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(s)}</body></html>'


# ---------------- B: синяя плашка с овалом ----------------
B_CSS = """
.bg{position:absolute;inset:0;background:url(group.src.jpg) center/cover;filter:saturate(.7) brightness(.95)}
.cream{color:#F1ECE2}
.caps{font-weight:800;text-transform:uppercase;line-height:.92;letter-spacing:-.02em}
.sp{font-weight:600;text-transform:uppercase;letter-spacing:.32em}
.big{font-weight:600;letter-spacing:-.04em;line-height:.88}
.oval{position:absolute;overflow:hidden}
.oval .ph{position:absolute;background:url(group.src.jpg) center/cover;filter:saturate(.7) brightness(.8)}
"""


def poster_b(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    # плашка
    px, py, pw, ph = (90, 230, 900, 1430) if story else (90, 70, 900, 1210)
    cx, cy, rx, ry = (px + 470, py + 520, 360, 400) if story else (px + 470, py + 420, 350, 330)
    blue = "#3B4BD0"
    s = ['<div class="bg"></div>']
    hole = f'M{px},{py} h{pw} v{ph} h-{pw} Z M{cx - rx},{cy} a{rx},{ry} 0 1,0 {2 * rx},0 a{rx},{ry} 0 1,0 -{2 * rx},0 Z'
    # овал: внутри — то же фото чуть темнее + Полина и Максим
    F = 120 if story else 112
    fy = cy - 30
    inner = (f'<div class="ph" style="left:{-cx + rx}px;top:{-cy + ry}px;width:1080px;height:{H}px"></div>')
    people = (place(MCUT, F, cx - 140, fy, "max_cut.png", (150, 260)) + place(PCUT, F, cx + 150, fy, "polina_cut.png", (150, 260)))
    # сдвиг координат внутрь овала
    people = people.replace('class="person" style="left:', 'class="person" data-x style="left:')
    s.append(f'<div class="oval" style="left:{cx - rx}px;top:{cy - ry}px;width:{2 * rx}px;height:{2 * ry}px;border-radius:50%">'
             f'{inner}<div style="position:absolute;left:{-(cx - rx)}px;top:{-(cy - ry)}px;width:1080px;height:{H}px">{people}</div></div>')
    s.append(f'<svg class="abs" style="left:0;top:0" width="1080" height="{H}"><path d="{hole}" fill="{blue}" fill-rule="evenodd"/></svg>')
    # тексты
    s.append(f'<div class="abs cream caps" style="left:{px + 46}px;top:{py + 50}px;font-size:40px">ПТ 27 НОЯБРЯ<br>19:00<br>GINGER HOTEL</div>')
    s.append(f'<div class="abs cream" style="right:{1080 - px - pw + 46}px;top:{py + 50}px;font-size:24px;font-weight:600;text-align:right;line-height:1.2">Тбилиси<br>вход свободный</div>')
    by = cy + ry + (40 if story else 30)
    s.append(f'<div class="abs cream caps" style="left:{px + 46}px;top:{by}px;font-size:34px">ИИ УСКОРЯЕТ ВСЁ.<br>А НАЙТИ СВОИХ —<br>ВСЁ СЛОЖНЕЕ.<br>ПРИХОДИ НА:</div>')
    s.append(f'<div class="abs cream big" style="right:{1080 - px - pw + 46}px;top:{by - 6}px;font-size:92px;text-align:right">сила<br>сообществ</div>')
    sy = py + ph - (200 if story else 170)
    s.append(f'<div class="abs cream" style="left:{px}px;width:{pw}px;top:{sy}px;text-align:center;font-size:20px" >'
             f'<div class="sp">вечер ведут</div><div class="sp" style="font-size:24px;letter-spacing:.2em;margin-top:8px">Полина · TEXTURA &nbsp;/&nbsp; Максим · Co.Space</div></div>')
    s.append(f'<div class="abs" style="left:{px + pw // 2 - 50}px;top:{py + ph - 80}px">{LOGO.replace("width=\"77\"", "width=\"100\"").replace("height=\"38\"", "height=\"49\"").replace("fill=\"white\"", "fill=\"#F1ECE2\"")}</div>')
    css = BASE % dict(H=H) + B_CSS
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(s)}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"edA-{fmt}.html").write_text(poster_a(fmt))
    (HERE / f"edB-{fmt}.html").write_text(poster_b(fmt))
print("ok")
