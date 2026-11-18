"""Стиль по референсу: цветное фото на весь кадр, тонкая рамка, фигурная плашка, нижняя строка с аватаром и кнопкой.
Наши цвета (тёмный + фиолетовый), шрифт Onest."""
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE / "blob"
OUT.mkdir(exist_ok=True)
LOGO = (HERE.parent / "co-logo-white.svg").read_text().replace('width="77"', 'width="96"').replace('height="38"', 'height="47"')
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(../fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F'), ('cyrillic', 'U+0400-04FF')))
PURPLE, INK = "#A874FF", "#120A22"

CSS = FF + """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:'Onest',sans-serif;background:#0B0812;color:#fff;position:relative}
.abs{position:absolute}
.photo{position:absolute;inset:0;background-size:cover;filter:saturate(.9) contrast(1.03)}
.vig{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,8,18,.35),transparent 22%,transparent 60%,rgba(11,8,18,.55) 100%)}
.frame{position:absolute;left:40px;right:40px;top:40px;bottom:40px;border:2px solid rgba(255,255,255,.75);border-radius:64px}
.tag{position:absolute;left:96px;top:96px;font-size:30px;font-weight:500;letter-spacing:-.01em}
.logo{position:absolute;right:96px;top:90px}
.head{position:absolute;color:#120A22;font-weight:500;letter-spacing:-.035em;line-height:1.02}
.head b{font-weight:800}
.list{position:absolute;color:#120A22;font-size:31px;line-height:1.45;font-weight:500}
.bar{position:absolute;left:96px;right:96px;bottom:84px;display:flex;align-items:center;justify-content:space-between}
.who{display:flex;align-items:center;gap:18px}
.ava{width:92px;height:92px;border-radius:50%;border:4px solid #A874FF;background-size:cover}
.who .sep{width:2px;height:56px;background:rgba(255,255,255,.7)}
.who b{display:block;font-size:30px;font-weight:700}
.who span{font-size:22px;color:rgba(255,255,255,.85)}
.cta{display:flex;align-items:center;gap:14px;background:#120A22;border:2px solid #A874FF;border-radius:50px;padding:18px 32px;font-size:26px;font-weight:600}
.cta i{width:16px;height:16px;border-radius:50%;background:#A874FF;display:block}
"""

R = 60
# Плашка-«ступенька»: верхний блок справа + широкий нижний блок
SHAPE_L = (f"M{110 + R},900 H500 A{R},{R} 0 0 0 560,840 V{680 + R} A{R},{R} 0 0 1 {560 + R},680 H{990 - R} "
           f"A{R},{R} 0 0 1 990,{680 + R} V{1000 - R} A{R},{R} 0 0 1 {990 - R},1000 H820 A{R},{R} 0 0 0 760,1060 "
           f"V{1190} A{R},{R} 0 0 1 700,1250 H{110 + R} A{R},{R} 0 0 1 110,1190 V{900 + R} A{R},{R} 0 0 1 {110 + R},900 Z")


def blob(mirror=False, color=PURPLE):
    t = ' transform="translate(1080,-140) scale(-1,1)"' if mirror else ' transform="translate(0,-140)"'
    return f'<svg class="abs" style="left:0;top:0" width="1080" height="1350"><path d="{SHAPE_L}" fill="{color}"{t}/></svg>'


def slide(photo, pos, tag, head, bullets, mirror=False, cta="Ссылка в профиле"):
    if mirror:   # нижний блок справа, верхний слева
        hx, lx = "right:150px;left:auto;text-align:right", "left:150px"
    else:
        hx, lx = "left:150px", "right:120px;text-align:left;left:600px"
    lis = "".join(f"<div>› {b}</div>" for b in bullets)
    body = f"""<div class="photo" style="background-image:url(../{photo});background-position:{pos}"></div><div class="vig"></div>
<div class="frame"></div>
<div class="tag">{tag}</div><div class="logo">{LOGO}</div>
{blob(mirror)}
<div class="list" style="{lx};top:580px;width:{390 if not mirror else 400}px">{lis}</div>
<div class="head" style="{hx};top:890px;font-size:58px;width:600px">{head}</div>
<div class="bar"><div class="who"><div class="ava" style="background:#120A22;display:flex;align-items:center;justify-content:center">{LOGO.replace('width="96"','width="54"').replace('height="47"','height="27"')}</div><div class="sep"></div>
<div><b>Co.Space</b><span>сообщества и встречи Тбилиси</span></div></div>
<div class="cta"><i></i>{cta}</div></div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'


SLIDES = {
    "leaders-cover": slide("stage.jpg", "50% 30%", "#силасообществ",
                           "Ведёшь сообщество?<br><b>Тебя уже ищут.</b>",
                           ["Страница — бесплатно", "Встречи — в афише", "Запись — в Telegram"],
                           cta="Добавить сообщество"),
    "guests-cover": slide("audience.jpg", "40% 50%", "#найдисвоих",
                          "Переехал в Тбилиси?<br><b>Найди своих.</b>",
                          ["Предприниматели и IT", "Женские сообщества", "Спорт, книги, кино"],
                          mirror=True, cta="Сообщества Тбилиси"),
    "event": slide("audience.jpg", "75% 45%", "#27ноября",
                   "Расскажи о своих<br><b>со сцены</b>",
                   ["27 ноября · пятница", "Ginger Hotel, сбор 19:00", "Вход свободный"],
                   cta="Регистрация"),
}

for name, html in SLIDES.items():
    (OUT / f"{name}.html").write_text(html)
print("ok")
