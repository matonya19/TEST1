"""Бесшовная карусель для лидеров: один холст 7×1080 = 7560×1350, режется на 7 слайдов.
Линия-«связь» проходит через все слайды, фото переходят через границы, люди вырезаны и выходят из плашек."""
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE / "wide"
OUT.mkdir(exist_ok=True)
LOGO_W = (HERE.parent / "co-logo-white.svg").read_text()
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(../fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F,U+2190-21FF'), ('cyrillic', 'U+0400-04FF')))
W, H, S = 7560, 1350, 1080
P, INK, BG = "#A874FF", "#120A22", "#0B0812"


def logo(w=96, color="white"):
    h = round(w * 38 / 77)
    return LOGO_W.replace('width="77"', f'width="{w}"').replace('height="38"', f'height="{h}"').replace('fill="white"', f'fill="{color}"')


CSS = FF + f"""*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{font-family:'Onest',sans-serif;background:{BG};color:#fff;position:relative}}
.a{{position:absolute}}
.glow{{position:absolute;border-radius:50%;filter:blur(90px);background:rgba(168,116,255,.22)}}
.kick{{font-size:22px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:{P}}}
.h{{font-weight:700;letter-spacing:-.04em;line-height:.98}}
.h em{{font-style:normal;color:{P}}}
.body{{font-size:30px;line-height:1.38;color:rgba(255,255,255,.72);font-weight:400}}
.body b{{color:#fff;font-weight:600}}
.cnt{{font-size:22px;font-weight:600;letter-spacing:.08em;color:rgba(255,255,255,.45)}}
.ph{{position:absolute;overflow:hidden;border-radius:48px;background-size:cover}}
.cut{{position:absolute}}
.cut img{{height:100%;display:block}}
.pillw{{display:inline-flex;align-items:center;gap:14px;background:#fff;color:{INK};border-radius:60px;padding:20px 32px;font-size:28px;font-weight:700}}
.pillw i{{width:14px;height:14px;border-radius:50%;background:{P};display:block}}
.glass{{background:rgba(23,18,31,.82);border:1.5px solid rgba(255,255,255,.1);border-radius:36px;-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px)}}
.card{{position:absolute;border-radius:40px;display:flex;align-items:center;gap:34px;padding:0 48px 0 44px}}
.card .dot{{width:28px;height:28px;border-radius:50%;flex:none}}
.card .t{{font-size:34px;font-weight:600;line-height:1.22;flex:1}}
.card .n{{font-size:110px;font-weight:900;line-height:1;color:transparent;-webkit-text-stroke:2px rgba(168,116,255,.7)}}
.msg{{border-radius:26px;padding:18px 24px;font-size:24px;line-height:1.3;margin-bottom:14px;max-width:86%}}
.me{{margin-left:auto;background:{P};color:{INK};font-weight:600;border-bottom-right-radius:8px}}
.bot{{background:#262033;border-bottom-left-radius:8px}}
.btn{{display:block;text-align:center;border:1.5px solid {P};color:#D7C2FF;border-radius:14px;padding:12px;font-size:22px;font-weight:700;margin-top:10px}}
.ava{{width:84px;height:84px;border-radius:50%;border:3px solid {P};background-size:cover;background-color:#2a2238}}
"""


def chrome(i, swipe=True):
    x = i * S
    sw = f'<div class="a cnt" style="left:{x + 860}px;top:1250px">листай →</div>' if swipe else ""
    return (f'<div class="a" style="left:{x + 72}px;top:70px;z-index:9">{logo()}</div>'
            f'<div class="a cnt" style="left:{x + 860}px;top:84px;z-index:9">{i + 1:02d} / 07</div>{sw}')


GOO = ('<filter id="goo"><feGaussianBlur in="SourceGraphic" stdDeviation="22"/>'
       '<feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 36 -16"/></filter>')


def blob(rects, color=P, z=2):
    """Сливает прямоугольники в одну плавную фигуру (как плашки на референсах)."""
    r = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="64" fill="{color}"/>' for x, y, w, h in rects)
    return f'<svg class="a" style="left:0;top:0;z-index:{z}" width="{W}" height="{H}"><defs>{GOO}</defs><g filter="url(#goo)">{r}</g></svg>'


LINE = ("M1010,900 C1060,1200 1150,1270 1400,1270 L1780,1260 C2100,1260 2300,1190 2700,1190 C3100,1190 3300,1290 3780,1290 "
        "C4250,1290 4500,1180 4800,1180 C5200,1180 5350,300 5700,250 C6100,200 6500,120 7020,112")
NODES = [(1010, 900), (1780, 1260), (2700, 1190), (3780, 1290), (4800, 1180), (7020, 112)]


def line():
    n = "".join(f'<circle cx="{x}" cy="{y}" r="26" fill="{P}" opacity=".18"/><circle cx="{x}" cy="{y}" r="10" fill="{P}"/>' for x, y in NODES)
    return (f'<svg class="a" style="left:0;top:0;z-index:3" width="{W}" height="{H}">'
            f'<path d="{LINE}" stroke="{P}" stroke-width="3" fill="none" stroke-linecap="round"/>{n}</svg>')


def cut(img, left, top, h, fade=None, z=4):
    m = f"-webkit-mask-image:linear-gradient(180deg,#000 {fade[0]}%,transparent {fade[1]}%);" if fade else ""
    return f'<div class="cut" style="left:{left}px;top:{top}px;height:{h}px;z-index:{z};{m}"><img src="../{img}"></div>'


els = []
# фоновое свечение по всей ленте
for gx, gy, gr in [(800, 200, 700), (2600, 1100, 800), (4700, 300, 700), (6900, 900, 800)]:
    els.append(f'<div class="glow" style="left:{gx - gr // 2}px;top:{gy - gr // 2}px;width:{gr}px;height:{gr}px"></div>')
els.append(line())

# ---------- 1. Обложка: Полина ----------
els.append(blob([(72, 210, 600, 560), (560, 560, 400, 620)]))
els.append(f'''<div class="a" style="left:120px;top:262px;width:500px;z-index:5;color:{INK}">
<div class="kick" style="color:{INK};opacity:.7">Для лидеров сообществ</div>
<div class="h" style="font-size:70px;margin-top:22px">Ведёшь<br>сообщество<br>в Тбилиси?</div>
<div style="font-size:28px;line-height:1.35;margin-top:26px;font-weight:500">Тебя уже ищут. Покажем,<br>как сделать, чтобы нашли.</div></div>''')
els.append('<div class="cut" style="left:545px;top:430px;width:535px;height:750px;overflow:hidden;z-index:4;'
           'clip-path:path(\'M80,0 H535 V686 A64,64 0 0 1 471,750 H80 Z\')"><img src="../polina_cut.png" style="height:1176px;margin-left:-110px;margin-top:-70px"></div>')
els.append(f'<div class="a" style="left:110px;top:1080px;z-index:6"><span class="pillw" style="font-size:22px;padding:12px 22px"><i></i>Полина · TEXTURA</span></div>')

# ---------- 2. Проблема: общий чат ----------
x = S
els.append(f'''<div class="a" style="left:{x + 72}px;top:210px;z-index:5"><div class="kick">Что происходит</div>
<div class="h" style="font-size:80px;margin-top:22px">Люди переезжают<br>и ищут <em>своих</em></div></div>''')
els.append(f'''<div class="a glass" style="left:{x + 72}px;top:520px;width:{S - 144}px;padding:30px 34px 22px;z-index:5">
<div style="display:flex;align-items:center;gap:16px;padding-bottom:22px;margin-bottom:24px;border-bottom:1.5px solid rgba(255,255,255,.08)">
<div style="width:56px;height:56px;border-radius:50%;background:#2E2640;display:flex;align-items:center;justify-content:center;font-size:26px">👥</div>
<div><div style="font-size:26px;font-weight:700">Общий чат «Тбилиси»</div><div style="font-size:18px;color:rgba(255,255,255,.45)">чат переезжающих</div></div></div>
<div class="msg bot" style="max-width:92%;font-size:26px">Месяц в Тбилиси, никого не знаю 🙈 Где тут бегают по утрам, ходят в походы, играют в настолки?</div>
<div class="msg bot" style="max-width:70%;font-size:24px;color:rgba(255,255,255,.75)">Был какой-то чат, не помню название</div>
<div class="msg bot" style="max-width:50%;font-size:24px;color:rgba(255,255,255,.75)">Поищи в инсте</div></div>''')
els.append(f'''<div class="a body" style="left:{x + 72}px;top:1010px;width:880px;z-index:5">Твой чат закрытый — снаружи его не видно. Люди, которым нужны <b>именно вы</b>, проходят мимо.</div>''')

# ---------- 3. Проверь себя: 70 сообществ ----------
x = 2 * S
els.append(f'<div class="ph" style="left:{x + 72}px;top:150px;width:{S - 144}px;height:460px;background-image:url(../audience.jpg);background-position:50% 55%;z-index:1"></div>')
els.append(f'<div class="a" style="left:{x + 110}px;top:578px;z-index:7"><span class="pillw" style="font-size:30px"><i></i>70 сообществ Тбилиси уже в каталоге</span></div>')
tags = ["бег", "походы", "настолки", "квизы", "IT", "импров", "мамы с детьми"]
els.append(f'<div class="a" style="left:{x + 72}px;top:710px;width:{S - 144}px;z-index:6;display:flex;flex-wrap:wrap;gap:12px">' +
           "".join(f'<span style="border:1.5px solid rgba(168,116,255,.5);border-radius:40px;padding:10px 22px;font-size:26px;font-weight:600">{t}</span>' for t in tags) + '</div>')
els.append(f'''<div class="a" style="left:{x + 72}px;top:870px;z-index:6"><div class="kick">Проверь себя</div>
<div class="h" style="font-size:64px;margin-top:18px">Возможно, и ваше<br><em>уже у нас.</em></div></div>''')
els.append(f'<div class="a body" style="left:{x + 72}px;top:1070px;width:820px;font-size:28px;z-index:6">Проверим за минуту — на следующих слайдах.</div>')

# ---------- 4. Что даём ----------
x = 3 * S
els.append(f'''<div class="a" style="left:{x + 72}px;top:200px;z-index:5"><div class="kick">Что даём — бесплатно</div>
<div class="h" style="font-size:70px;margin-top:22px">Своя страница и встречи<br><em>в афише города</em></div></div>''')
steps = ["Страница сообщества — по ней вас находят новенькие", "Встречи в афише Тбилиси — добавляешь сам", "Запись через Telegram, бот сам напоминает гостям"]
for k, t in enumerate(steps):
    y = 500 + k * 200
    filled = k == 0
    bg = f"background:{P};color:{INK}" if filled else "background:#17121F;border:1.5px solid rgba(168,116,255,.3)"
    dot = INK if filled else P
    num = f'<div class="n" style="-webkit-text-stroke:2px rgba(18,10,34,.5)">{k + 1}</div>' if filled else f'<div class="n">{k + 1}</div>'
    els.append(f'<div class="card" style="left:{x + 34}px;top:{y}px;width:{S - 106}px;height:170px;z-index:4;{bg}">'
               f'<div class="dot" style="background:{dot};margin-left:6px"></div><div class="t">{t}</div>{num}</div>')
els.append(f'<div class="a cnt" style="left:{x + 72}px;top:1140px;letter-spacing:.02em;font-size:26px;color:rgba(255,255,255,.6);z-index:5">Меньше рутины — больше времени на своих</div>')

# ---------- 5. Как это сделать: бот ----------
x = 4 * S
els.append(f'''<div class="a" style="left:{x + 72}px;top:210px;width:470px;z-index:5"><div class="kick">Как это сделать</div>
<div class="h" style="font-size:68px;margin-top:22px">Пришли боту<br>ссылку на<br><em>свой чат</em></div>
<div class="body" style="margin-top:34px;font-size:27px">Есть страница — бот предложит сделать её вашей. Нет — поможет завести <b>за 3 минуты</b>.</div>
<div style="margin-top:22px;font-size:22px;line-height:1.35;color:rgba(255,255,255,.5)">Заявку на готовую страницу команда проверяет — обычно в течение дня.</div></div>''')
els.append(f'''<div class="a" style="left:{x + 545}px;top:230px;width:430px;height:820px;border-radius:64px;background:#17121F;border:10px solid #2A2238;
transform:rotate(5deg);box-shadow:0 40px 90px rgba(0,0,0,.6),0 0 120px rgba(168,116,255,.25);padding:70px 26px 30px;z-index:5">
<div style="display:flex;align-items:center;gap:14px;margin-bottom:34px"><div style="width:58px;height:58px;border-radius:50%;background:{P};display:flex;align-items:center;justify-content:center">{logo(34, INK)}</div>
<div><div style="font-size:24px;font-weight:700">Co.Space бот</div><div style="font-size:18px;color:rgba(255,255,255,.45)">онлайн</div></div></div>
<div class="msg me">t.me/твой_чат</div>
<div class="msg bot">Это сообщество уже есть в каталоге Co.Space. Сделать страницу вашей?<span class="btn" style="font-size:20px">✅ Да, это моё — отправить заявку</span></div></div>''')

# ---------- 6. Вечер ----------
x = 5 * S
els.append(f'<div class="ph" style="left:{x}px;top:0;width:{S}px;height:{H}px;border-radius:0;background-image:url(../audience.jpg);background-position:45% 50%;filter:brightness(.7) saturate(.85);z-index:1"></div>')
els.append(f'<div class="a" style="left:{x}px;top:0;width:{S}px;height:{H}px;background:linear-gradient(180deg,rgba(11,8,18,.65),rgba(11,8,18,.1) 30%,rgba(11,8,18,.2) 60%,rgba(11,8,18,.85));z-index:2"></div>')
els.append(f'<div class="a" style="left:{x + 40}px;top:40px;width:{S - 80}px;height:{H - 80}px;border:2px solid rgba(255,255,255,.7);border-radius:60px;z-index:4"></div>')
els.append(blob([(x + 380, 500, 610, 300), (x + 90, 760, 820, 380)], z=5))
els.append(f'''<div class="a" style="left:{x + 425}px;top:540px;z-index:6;color:{INK};font-size:26px;line-height:1.5;font-weight:600">
<div>› 27 ноября, пятница</div><div>› Ginger Hotel, 49 Kakabadze St</div><div>› сбор 19:00 · начало 19:30</div><div>› вход свободный, нужна регистрация</div></div>''')
els.append(f'''<div class="a" style="left:{x + 140}px;top:840px;width:720px;z-index:6;color:{INK}"><div class="kick" style="color:{INK};opacity:.65">Сила сообществ · 27 ноября</div>
<div class="h" style="font-size:56px;margin-top:16px">Покажем твоё сообщество<br><em style="color:#fff">на вечере</em></div>
<div style="font-size:24px;line-height:1.35;margin-top:16px;font-weight:500">Со сцены или на слайде с QR — так, чтобы зал узнал, как к вам попасть.</div></div>''')
els.append(f'''<div class="a" style="left:{x + 96}px;top:1175px;z-index:6;display:flex;align-items:center;gap:16px">
<div class="ava" style="background-image:url(../polina_cut.png);background-size:330%;background-position:40% 8%"></div>
<div style="font-size:24px;line-height:1.25"><b>Ведёт Полина Язвенко</b><br><span style="color:rgba(255,255,255,.75)">лидер сообщества TEXTURA</span></div></div>''')

# ---------- 7. Финал ----------
x = 6 * S
els.append(blob([(x + 40, 150, S - 80, H - 190), (x + 440, 40, 200, 200)], z=4))
els.append(f'''<div class="a" style="left:{x + 110}px;top:290px;z-index:6;color:{INK}">
<div class="kick" style="color:{INK};opacity:.65">Сила сообществ · 27 ноября</div>
<div class="h" style="font-size:120px;margin-top:28px;font-weight:800">Сообщество<br>сильнее<br>одиночества</div>
<div style="margin-top:50px"><span class="pillw" style="background:{INK};color:#fff;font-size:32px;padding:24px 38px"><i></i>Добавить сообщество — ссылка в профиле</span></div>
<div style="font-size:27px;margin-top:26px;font-weight:500;line-height:1.4">Бесплатно · около 3 минут в Telegram.<br><b>Добавленные сообщества покажем на вечере 27.11.</b><br>Знаешь лидера сообщества? Перешли ему.</div></div>''')
els.append(f'<div class="a" style="left:{x + 110}px;top:1170px;z-index:6">{logo(110, INK)}</div>')
els.append(f'<div class="a" style="left:{x + 760}px;top:1195px;z-index:6;color:{INK};font-size:24px;font-weight:700">@co.tbilisi</div>')

for i in range(7):
    els.append(chrome(i, swipe=i < 6))

html = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(els)}</body></html>'
(OUT / "leaders.html").write_text(html)
print("ok")
