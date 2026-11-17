"""Для лидеров: фиолетово-чёрная лазерная сцена (фото-референс перекрашено), Полина и Максим внизу."""
import pathlib
HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
PCUT = (933, 1146, .403, .170, .1955)
MCUT = (902, 1059, .395, .229, .326)
DEPTH = (1 - .229) / .326

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:#06020C;color:#fff}
.abs{position:absolute}
.bg{position:absolute;left:%(bx)dpx;top:0;height:%(H)dpx}
.vig{position:absolute;inset:0;background:radial-gradient(75%% 60%% at 50%% 42%%,transparent 35%%,rgba(6,2,12,.92) 100%%),
 linear-gradient(180deg,rgba(6,2,12,.35),transparent 25%%,transparent 65%%,rgba(6,2,12,.9))}
.person{position:absolute;overflow:hidden;filter:drop-shadow(0 0 40px rgba(140,90,255,.35))}
.person img{position:absolute;left:0;top:0;display:block}
.main{font-weight:500;letter-spacing:-.025em;line-height:1.02}
.small{font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.8);line-height:1.6}
"""


def person_bottom(cut, F, fx, H, img):
    h = F / cut[4]; w = h * cut[0] / cut[1]; vis = cut[3] * h + DEPTH * F
    return (f'<div class="person" style="left:{fx - cut[2] * w:.0f}px;top:{H - vis:.0f}px;width:{w:.0f}px;height:{vis:.0f}px">'
            f'<img src="{img}" style="height:{h:.0f}px"></div>')


def build(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    bh = H; bw = 1200 * H / 1500; bx = -(bw - 1080) / 2
    F = 140 if story else 120
    top = 270 if story else 70
    mainy = 720 if story else 520
    ms = 70 if story else 60
    datey = 1080 if story else 800
    body = f"""<img class="bg" src="crowd_purple.jpg"><div class="vig"></div>
{person_bottom(MCUT, F, 210, H, 'max_purple.png')}{person_bottom(PCUT, F, 875, H, 'polina_purple.png')}
<div class="abs small" style="left:90px;top:{top}px;font-size:20px">Сила сообществ<br>Ginger Hotel · сбор 19:00<br>вход свободный</div>
<div class="abs main" style="left:90px;top:{mainy}px;font-size:{ms}px">Ведёшь сообщество?<br>Расскажи о нём.</div>
<div class="abs main" style="right:90px;top:{datey}px;font-size:{40 if story else 36}px;text-align:right;color:#E3D4FF">27 ноября<br>в Тбилиси</div>
<div class="abs" style="left:50%;transform:translateX(-50%);bottom:{(320 if story else 70)}px">{LOGO.replace('width="77"','width="110"').replace('height="38"','height="54"')}</div>"""
    css = CSS % dict(H=H, bx=bx)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"purple-{fmt}.html").write_text(build(fmt))
print("ok")
