"""Бесшовная карусель для гостей («Переехал в Тбилиси?») — та же система, что у лидеров, но своя история:
линия начинается с одинокой серой точки и по ходу ленты обрастает связями."""
import pathlib

HERE = pathlib.Path(__file__).parent
_src = (HERE / "build_wide.py").read_text()
exec(_src[:_src.index("LINE = (")])

CSS2 = CSS + f"""
.chip{{position:absolute;display:inline-flex;align-items:center;gap:14px;border-radius:60px;padding:18px 30px;font-size:34px;font-weight:600;
 background:#17121F;border:1.5px solid rgba(168,116,255,.35);white-space:nowrap;z-index:5}}
.chip i{{width:16px;height:16px;border-radius:50%;background:{P};display:block}}
.chip.on{{background:{P};color:{INK};border-color:{P}}}
.chip.on i{{background:{INK}}}
.step{{position:absolute;z-index:5;display:flex;gap:30px;align-items:flex-start}}
.step .c{{flex:none;width:96px;height:96px;border-radius:50%;background:{P};color:{INK};font-size:46px;font-weight:800;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 14px rgba(168,116,255,.15)}}
.step .t{{font-size:34px;line-height:1.25;font-weight:600;padding-top:8px}}
.step .t span{{display:block;font-size:26px;font-weight:400;color:rgba(255,255,255,.62);margin-top:8px}}
"""
CSS = CSS2

LINE = ("M1300,980 C1500,980 1560,1240 1900,1240 C2120,1240 2090,650 2400,645 L2700,640 C2950,640 3000,610 3240,610 "
        "L4300,610 C4380,610 4420,590 4420,520 L4420,1000 "
        "C4420,1200 4900,1260 5300,1220 C5700,1180 5850,700 6000,640 C6400,480 6700,130 7020,112")
NODES = [(1900, 1240), (2700, 640), (3240, 610), (4420, 520), (4420, 760), (4420, 1000), (6000, 640), (7020, 112)]

els = []
for gx, gy, gr in [(700, 1000, 800), (2700, 300, 700), (4300, 900, 800), (6800, 400, 800)]:
    els.append(f'<div class="glow" style="left:{gx - gr // 2}px;top:{gy - gr // 2}px;width:{gr}px;height:{gr}px"></div>')

n = "".join(f'<circle cx="{x}" cy="{y}" r="26" fill="{P}" opacity=".18"/><circle cx="{x}" cy="{y}" r="10" fill="{P}"/>' for x, y in NODES)
els.append(f'<svg class="a" style="left:0;top:0;z-index:3" width="{W}" height="{H}">'
           f'<path d="{LINE}" stroke="{P}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
           # одинокая серая точка — начало истории
           f'<circle cx="1300" cy="980" r="70" fill="none" stroke="#6B647A" stroke-width="2" stroke-dasharray="4 12"/>'
           f'<circle cx="1300" cy="980" r="20" fill="#8A8398"/>{n}</svg>')

# ---------- 1. Обложка: зал внутри фигуры-«ступеньки» ----------
rects = [(72, 650, 650, 330), (330, 830, 678, 400)]
mask_r = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="64" fill="white"/>' for x, y, w, h in rects)
els.append(f'''<svg class="a" style="left:0;top:0;z-index:2" width="{W}" height="{H}"><defs>{GOO}
<mask id="m1"><g filter="url(#goo)">{mask_r}</g></mask></defs>
<image href="../conf.jpg" x="-250" y="300" width="1560" height="1040" preserveAspectRatio="xMidYMid slice" mask="url(#m1)"/></svg>''')
els.append(f'''<div class="a" style="left:72px;top:200px;z-index:5"><div class="kick">Для тех, кто ищет своих</div>
<div class="h" style="font-size:86px;margin-top:24px">Недавно в Тбилиси,<br>а своих людей<br><em>пока нет?</em></div></div>''')
els.append(f'<div class="a" style="left:110px;top:1120px;z-index:6"><span class="pillw" style="font-size:24px;padding:14px 24px"><i></i>Знакомо. Расскажем, где их искать</span></div>')

# ---------- 2. Одиночество ----------
x = S
els.append(f'''<div class="a" style="left:{x + 72}px;top:210px;z-index:5"><div class="kick">Знакомо?</div>
<div class="h" style="font-size:76px;margin-top:24px">Квартира есть,<br>любимая кофейня тоже.<br><em>А поговорить не с кем.</em></div></div>''')
els.append(f'''<div class="a body" style="left:{x + 72}px;top:620px;width:860px;z-index:5">Это нормально. В новом городе люди есть везде — просто непонятно, где <b>твои</b>.</div>''')
els.append(f'<div class="a cnt" style="left:{x + 160}px;top:1080px;font-size:22px;letter-spacing:.12em;z-index:5">ЭТО ТЫ. ПОКА.</div>')

# ---------- 3. 68 сообществ (фото через границу 3|4) ----------
x = 2 * S
els.append(f'<div class="ph" style="left:{x + 470}px;top:180px;width:538px;height:400px;background-image:url(../studio_duo.jpg);background-position:50% 50%;z-index:1"></div>')
els.append(f'''<div class="a" style="left:{x + 60}px;top:200px;z-index:5"><div class="h" style="font-size:300px;color:{P};letter-spacing:-.06em;line-height:.85">70</div></div>''')
els.append(f'''<div class="a" style="left:{x + 72}px;top:720px;z-index:5"><div class="kick">Что мы сделали</div>
<div class="h" style="font-size:66px;margin-top:22px">сообществ Тбилиси —<br><em>в одном месте</em></div></div>''')
els.append(f'''<div class="a body" style="left:{x + 72}px;top:1000px;width:820px;z-index:5"><b>Co.Space</b> — каталог сообществ и афиша их встреч. Чтобы не искать по сотне чатов, а сразу видеть, кто чем живёт.</div>''')

# ---------- 4. Свои для всех: чипсы — узлы сети ----------
x = 3 * S
els.append(f'''<div class="a" style="left:{x + 72}px;top:200px;z-index:5"><div class="kick">Выбирай по душе</div>
<div class="h" style="font-size:80px;margin-top:22px">Тут есть<br><em>свои для всех</em></div></div>''')
chips = [('Походы', 72, 470, True), ('Настолки и квизы', 310, 470, True), ('Бег и спорт', 150, 600, False), ('IT', 483, 600, False), ('Мамы с детьми', 645, 600, False), ('Творчество и импров', 72, 730, True), ('Волонтёрство', 557, 730, False), ('Языковые клубы', 150, 860, False), ('Книжные клубы', 540, 860, False), ('Кино и шахматы', 72, 990, False), ('Предприниматели', 462, 990, False)]
for t, cx, cy, on in chips:
    els.append(f'<div class="chip{" on" if on else ""}" style="left:{x + cx}px;top:{cy}px"><i></i>{t}</div>')

# ---------- 5. Как это работает: шаги на линии ----------
x = 4 * S
els.append(f'''<div class="a" style="left:{x + 72}px;top:200px;z-index:5"><div class="kick">Как это работает</div>
<div class="h" style="font-size:72px;margin-top:22px">Пара минут —<br><em>и ты среди своих</em></div></div>''')
steps = [("Выбираешь сообщество", "на сайте Co.Space"), ("Жмёшь «Вступить»", "бот даст ссылку на чат или поможет подать заявку"),
         ("Записываешься на встречу", "бот напомнит за сутки и за 3 часа")]
for k, (t, sub) in enumerate(steps):
    els.append(f'<div class="step" style="left:{x + 52}px;top:{472 + k * 240}px;width:920px"><div class="c">{k + 1}</div><div class="t">{t}<span>{sub}</span></div></div>')

# ---------- 6. Афиша: карточка встречи ----------
x = 5 * S
els.append(f'''<div class="a" style="left:{x + 72}px;top:200px;z-index:5"><div class="kick">Афиша недели</div>
<div class="h" style="font-size:72px;margin-top:22px">Встречи сообществ —<br><em>в одной афише</em></div></div>''')
els.append(f'''<div class="a glass" style="left:{x + 120}px;top:500px;width:840px;z-index:5;overflow:hidden;transform:rotate(-3deg);box-shadow:0 40px 90px rgba(0,0,0,.55)">
<div style="height:300px;background:url(../outdoor.jpg) -616px -246px/1760px auto"></div>
<div style="padding:34px 40px 40px"><div class="kick" style="color:rgba(255,255,255,.55)">Пт · 27 ноября · 19:00</div>
<div style="font-size:54px;font-weight:700;letter-spacing:-.03em;margin:14px 0 8px">Сила сообществ</div>
<div style="font-size:26px;color:rgba(255,255,255,.6);margin-bottom:28px">Ginger Hotel · вход свободный, по регистрации</div>
<span class="pillw" style="background:{P};font-size:26px;padding:16px 30px">Регистрация</span></div></div>''')
els.append(f'<div class="a body" style="left:{x + 72}px;top:1180px;width:900px;font-size:26px;z-index:5">Заглядывай в начале недели — и сразу видно, куда сходить.</div>')

# ---------- 7. Финал ----------
x = 6 * S
els.append(blob([(x + 40, 150, S - 80, H - 190), (x + 440, 40, 200, 200)], z=4))
els.append(f'''<div class="a" style="left:{x + 110}px;top:310px;z-index:6;color:{INK}">
<div class="kick" style="color:{INK};opacity:.65">Co.Space · Тбилиси</div>
<div class="h" style="font-size:118px;margin-top:28px;font-weight:800">Найди своих —<br>найдёшь<br>своё</div>
<div style="margin-top:56px"><span class="pillw" style="background:{INK};color:#fff;font-size:32px;padding:24px 38px"><i></i>Сообщества Тбилиси — ссылка в профиле</span></div>
<div style="font-size:28px;margin-top:28px;font-weight:500">Сохрани, чтобы не потерять.<br>И отправь тому, кто тоже недавно в Тбилиси.</div></div>''')
els.append(f'<div class="a" style="left:{x + 110}px;top:1140px;z-index:6">{logo(110, INK)}</div>')
els.append(f'<div class="a" style="left:{x + 760}px;top:1170px;z-index:6;color:{INK};font-size:24px;font-weight:700">@co.tbilisi</div>')

for i in range(7):
    els.append(chrome(i, swipe=i < 6))

(OUT / "guests.html").write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(els)}</body></html>')
print("ok")
