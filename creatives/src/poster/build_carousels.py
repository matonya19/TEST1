"""Две карусели для @co.tbilisi (1080x1350, 7 слайдов): A — для тех, кто ищет своих; B — для лидеров сообществ.
Тексты — по утверждённым постам А и Б из пакета. Шрифт Onest, фиолетово-тёмная гамма."""
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE / "carousel"
OUT.mkdir(exist_ok=True)
LOGO = (HERE.parent / "co-logo-white.svg").read_text().replace('width="77"', 'width="84"').replace('height="38"', 'height="41"')
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(../fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F,U+20BE'), ('cyrillic', 'U+0400-04FF')))
P = "#A874FF"

CSS = FF + """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:'Onest',sans-serif;background:#0B0812;color:#fff;position:relative}
.abs{position:absolute}
.top{position:absolute;left:72px;right:72px;top:64px;display:flex;justify-content:space-between;align-items:center}
.num{font-size:22px;font-weight:600;color:rgba(255,255,255,.5);letter-spacing:.08em}
.swipe{position:absolute;right:72px;bottom:64px;font-size:22px;font-weight:600;color:rgba(255,255,255,.55);letter-spacing:.06em}
.foot{position:absolute;left:72px;bottom:64px;font-size:22px;font-weight:600;color:rgba(255,255,255,.55);letter-spacing:.06em}
.ph{position:absolute;inset:0;background:url(../audience.jpg) 50% 60%/cover;filter:grayscale(1) brightness(.62);opacity:.72}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,8,18,.55),rgba(11,8,18,.25) 40%,rgba(11,8,18,.92) 75%)}
.giant{position:absolute;font-weight:900;color:#A874FF;letter-spacing:-.05em;line-height:.8}
h1{font-weight:900;letter-spacing:-.045em;line-height:.95}
h2{font-weight:800;letter-spacing:-.035em;line-height:1}
.p{color:#A874FF}
.lead{font-size:34px;line-height:1.3;font-weight:500;color:rgba(255,255,255,.88)}
.muted{color:rgba(255,255,255,.6)}
.chip{display:inline-flex;align-items:center;gap:12px;border:2px solid rgba(168,116,255,.6);background:rgba(168,116,255,.12);border-radius:60px;padding:16px 28px;font-size:36px;font-weight:700;margin:0 14px 18px 0}
.chip i{width:18px;height:18px;border-radius:50%;background:#A874FF;display:block}
.step{display:flex;gap:28px;align-items:flex-start;margin-bottom:34px}
.step b{flex:none;width:72px;height:72px;border-radius:50%;background:#A874FF;color:#0B0812;font-size:36px;font-weight:900;display:flex;align-items:center;justify-content:center}
.step div{font-size:36px;line-height:1.25;font-weight:600;padding-top:12px}
.chat{background:#17121F;border:1.5px solid rgba(255,255,255,.08);border-radius:36px;padding:34px}
.msg{max-width:78%;border-radius:26px;padding:20px 26px;font-size:28px;line-height:1.3;margin-bottom:16px}
.me{margin-left:auto;background:#A874FF;color:#0B0812;font-weight:600;border-bottom-right-radius:8px}
.bot{background:#262033;border-bottom-left-radius:8px}
.btn{display:inline-block;border:2px solid #A874FF;color:#C9A8FF;border-radius:16px;padding:12px 20px;font-size:24px;font-weight:700;margin:6px 8px 0 0}
.card{background:#17121F;border:1.5px solid rgba(168,116,255,.35);border-radius:32px;padding:40px}
.pill{display:inline-block;background:#A874FF;color:#0B0812;font-weight:800;border-radius:50px;padding:16px 30px;font-size:28px}
.person{position:absolute}
.person img{height:100%;display:block}

/* ---- карусель лидеров: тот же фон/шрифт/цвета, другая графика ---- */
.eyebrow{position:absolute;left:72px;top:170px;display:flex;align-items:center;gap:14px;font-size:22px;font-weight:700;letter-spacing:.14em;color:rgba(255,255,255,.7)}
.eyebrow i{width:14px;height:14px;border-radius:50%;background:#A874FF;display:block}
.bar{position:absolute;left:72px;width:6px;background:#A874FF;border-radius:3px}
.outline{position:absolute;font-weight:900;letter-spacing:-.05em;line-height:.8;color:transparent;-webkit-text-stroke:3px #A874FF}
.frame{position:absolute;border-radius:36px;overflow:hidden;border:1.5px solid rgba(168,116,255,.35)}
.frame div{position:absolute;inset:0;background-size:cover;filter:grayscale(1) brightness(.75) contrast(1.05)}
.frame::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 50%,rgba(11,8,18,.7));}
.row{display:flex;align-items:center;gap:30px;border:1.5px solid rgba(168,116,255,.35);border-radius:28px;padding:28px 34px;margin-bottom:22px;background:#140F1E}
.row b{font-size:64px;font-weight:900;color:transparent;-webkit-text-stroke:2px #A874FF;line-height:1;width:60px}
.row div{font-size:32px;line-height:1.25;font-weight:600}
.search{background:#17121F;border:1.5px solid rgba(255,255,255,.1);border-radius:28px;padding:30px 34px}
.q{display:flex;align-items:center;gap:18px;font-size:32px;font-weight:600;padding-bottom:24px;border-bottom:1.5px solid rgba(255,255,255,.08)}
.res{font-size:28px;color:rgba(255,255,255,.45);padding-top:24px;line-height:1.5}

/* ---- инверсия (не используется) ---- */
body.inv{background:#9466FF;color:#120A22}
.inv .p{color:#fff}
.inv .giant{color:#120A22}
.inv .lead{color:rgba(18,10,34,.86)}
.inv .muted,.inv .num,.inv .swipe,.inv .foot{color:rgba(18,10,34,.62)}
.inv .top svg path{fill:#120A22}
.inv .ph{filter:grayscale(1) contrast(1.15) brightness(.9);mix-blend-mode:multiply;opacity:.75}
.inv .shade{background:linear-gradient(180deg,rgba(148,102,255,.45),rgba(148,102,255,.2) 18%,rgba(148,102,255,.97) 40%)}
.inv .step b{background:#120A22;color:#fff}
.inv .step div{color:#120A22}
.inv .chat{background:#120A22;border-color:#120A22;color:#fff}
.inv .me{background:#9466FF;color:#120A22}
.inv .pill{background:#120A22;color:#fff}
"""


def page(body, n, total=7, swipe=True, foot="", inv=False):
    sw = '<div class="swipe">листай →</div>' if swipe else ""
    ft = f'<div class="foot">{foot}</div>' if foot else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body{" class=inv" if inv else ""}>{body}'
            f'<div class="top"><div>{LOGO}</div><div class="num">{n:02d} / {total:02d}</div></div>{sw}{ft}</body></html>')


def dots(c="#A874FF", line="#C9A8FF", lone="#5B556B"):
    """Одна точка в стороне и связанная группа — образ «один / вместе»."""
    pts = [(700, 240, 34), (840, 170, 22), (900, 320, 40), (770, 390, 28), (640, 360, 20), (860, 470, 24), (960, 450, 16), (720, 500, 14)]
    edges = [(0, 1), (1, 2), (0, 3), (2, 3), (3, 4), (0, 4), (3, 5), (2, 6), (5, 6), (4, 7), (5, 7)]
    s = '<svg class="abs" style="left:0;top:180px" width="1080" height="620">'
    s += f'<circle cx="220" cy="430" r="20" fill="{lone}"/><circle cx="220" cy="430" r="52" fill="none" stroke="{lone}" stroke-width="2" stroke-dasharray="3 10"/>'
    for i, j in edges:
        s += f'<line x1="{pts[i][0]}" y1="{pts[i][1]}" x2="{pts[j][0]}" y2="{pts[j][1]}" stroke="{line}" stroke-width="2" opacity=".45"/>'
    for x, y, r in pts:
        s += f'<circle cx="{x}" cy="{y}" r="{r * 1.7:.0f}" fill="{c}" opacity=".15"/><circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>'
    return s + '</svg>'


# ---------------- A: для тех, кто ищет своих ----------------
A = [
    page('''<div class="ph"></div><div class="shade"></div>
<div class="giant" style="right:-60px;top:120px;font-size:620px;opacity:.9">?</div>
<h1 class="abs" style="left:72px;right:72px;top:640px;font-size:108px">Переехал<br>в Тбилиси,<br>а своих людей<br><span class="p">пока нет?</span></h1>
<div class="abs lead" style="left:72px;top:1150px;font-size:30px">Знакомо. Давай расскажем, где их искать →</div>''', 1),
    page(f'''{dots()}
<h1 class="abs" style="left:72px;right:72px;top:740px;font-size:76px">Квартиру нашёл,<br>кофейню любимую тоже.<br><span class="p">А поговорить не с кем.</span></h1>
<div class="abs lead" style="left:72px;right:120px;top:1060px">Это нормально. В новом городе люди есть везде — просто непонятно, где <i>твои</i>.</div>''', 2),
    page('''<div class="giant" style="left:56px;top:150px;font-size:520px">68</div>
<h2 class="abs" style="left:72px;top:600px;font-size:64px">сообществ Тбилиси<br>собрали в одном месте</h2>
<div class="abs lead" style="left:72px;right:110px;top:860px">Мы сделали <b style="color:#fff">Co.Space</b> — каталог сообществ и афишу их встреч. Чтобы не искать по сотне чатов, а сразу видеть, кто чем живёт.</div>''', 3),
    page('''<h1 class="abs" style="left:72px;top:170px;font-size:88px">Тут есть<br><span class="p">свои для всех</span></h1>
<div class="abs" style="left:72px;right:30px;top:390px">
<span class="chip"><i></i>Предприниматели</span><span class="chip"><i></i>IT</span>
<span class="chip"><i></i>Женские сообщества</span><span class="chip"><i></i>Спорт и бег</span>
<span class="chip"><i></i>Проявленность и личный бренд</span><span class="chip"><i></i>Саморазвитие</span><span class="chip"><i></i>Книжные клубы</span>
<span class="chip"><i></i>Творчество</span><span class="chip"><i></i>Нетворкинг</span>
<span class="chip"><i></i>Кино</span><span class="chip"><i></i>Шахматы</span><span class="chip"><i></i>Языковые клубы</span><span class="chip"><i></i>Родители</span>
<span class="chip" style="border-style:dashed;background:none">и ещё много</span></div>
<div class="abs lead" style="left:72px;right:120px;top:1150px;font-size:30px">Выбирай по душе — от бизнес-клуба до пробежки по выходным.</div>''', 4),
    page('''<h1 class="abs" style="left:72px;top:190px;font-size:88px">Как это<br><span class="p">работает</span></h1>
<div class="abs" style="left:72px;right:72px;top:480px">
<div class="step"><b>1</b><div>Заходишь на Co.Space и выбираешь сообщество</div></div>
<div class="step"><b>2</b><div>Жмёшь «Вступить» — бот в Telegram подскажет, как попасть внутрь</div></div>
<div class="step"><b>3</b><div>Записываешься на встречу в пару нажатий. Бот напомнит, чтобы не забыл</div></div></div>
<div class="abs muted" style="left:72px;top:1130px;font-size:28px;font-weight:600">Пара минут — и ты уже не один</div>''', 5),
    page('''<h1 class="abs" style="left:72px;top:190px;font-size:84px">Все встречи недели —<br><span class="p">в одной афише</span></h1>
<div class="abs card" style="left:72px;right:72px;top:500px">
<div class="muted" style="font-size:24px;font-weight:700;letter-spacing:.1em">ПТ · 27 НОЯБРЯ · 19:00</div>
<div style="font-size:56px;font-weight:800;letter-spacing:-.03em;margin:14px 0 10px">Сила сообществ</div>
<div class="muted" style="font-size:28px;margin-bottom:28px">Ginger Hotel · вход свободный</div>
<span class="pill">Регистрация</span></div>
<div class="abs lead" style="left:72px;right:110px;top:1000px">Заглядывай в начале недели: что интересного, куда сходить. Например, на наш вечер 27 ноября — там будут сообщества со всего города.</div>''', 6),
    page('''<div class="ph"></div><div class="shade"></div>
<h1 class="abs" style="left:72px;right:72px;top:560px;font-size:118px">Найди своих —<br><span class="p">найдёшь своё</span></h1>
<div class="abs" style="left:72px;top:900px"><span class="pill" style="font-size:32px;padding:20px 36px">Сообщества Тбилиси — ссылка в профиле</span></div>
<div class="abs lead" style="left:72px;top:1040px;font-size:30px">Сохрани, чтобы не потерять. И отправь тому, кто тоже недавно переехал</div>''', 7, swipe=False, foot="@co.tbilisi"),
]


# ---------------- B: для лидеров ----------------
def heroes(F=150, fy=520):
    def place(cut, fx, img):
        h = F / cut[4]; w = h * cut[0] / cut[1]
        return (f'<div class="person" style="left:{fx - cut[2] * w:.0f}px;top:{fy - cut[3] * h:.0f}px;height:{h:.0f}px;'
                f'-webkit-mask-image:linear-gradient(180deg,#000 55%,transparent 85%)"><img src="../{img}"></div>')
    return place((902, 1059, .395, .229, .326), 310, "max_cut.png") + place((933, 1146, .403, .170, .1955), 780, "polina_cut.png")


EB = '<div class="eyebrow"><i></i>ДЛЯ ЛИДЕРОВ СООБЩЕСТВ</div>'
B = [
    page(EB + '''<div class="frame" style="left:72px;right:72px;top:240px;height:520px"><div style="background-image:url(../stage.jpg);background-position:50% 38%"></div></div>
<div class="bar" style="top:830px;height:300px"></div>
<h1 class="abs" style="left:110px;right:60px;top:820px;font-size:96px">Ведёшь<br>сообщество<br>в Тбилиси?</h1>
<h2 class="abs p" style="left:110px;top:1140px;font-size:52px">Тебя уже ищут. Правда</h2>''', 1),
    page(EB + '''<div class="abs search" style="left:72px;right:72px;top:330px">
<div class="q"><span style="color:#A874FF">⌕</span>книжный клуб тбилиси</div>
<div class="res">Ничего не найдено.<br>Чат закрытый — снаружи его не видно.</div></div>
<div class="bar" style="top:680px;height:300px"></div>
<h1 class="abs" style="left:110px;right:72px;top:670px;font-size:70px">В Тбилиси всё время<br>приезжают люди,<br><span class="p">которым нужны<br>именно вы.</span></h1>
<div class="abs lead" style="left:110px;right:90px;top:1050px">Но найти вас пока сложно. Давай это исправим.</div>''', 2),
    page(EB + '''<h2 class="abs muted" style="left:72px;top:300px;font-size:48px">Своя страница<br>в каталоге Тбилиси —</h2>
<div class="outline" style="left:66px;top:520px;font-size:184px">бесплатно</div>
<div class="bar" style="top:860px;height:110px"></div>
<div class="abs lead" style="left:110px;right:110px;top:852px">Рассказываешь, кто вы и чем живёте. А новенькие в городе находят вас сами — по интересам.</div>''', 3),
    page(EB + '''<h1 class="abs" style="left:72px;top:250px;font-size:84px">Твои встречи —<br><span class="p">в афише города</span></h1>
<div class="abs" style="left:72px;right:72px;top:520px">
<div class="row"><b>1</b><div>Сам добавляешь встречу в кабинете сообщества</div></div>
<div class="row"><b>2</b><div>Люди записываются через Telegram — без таблиц и личных сообщений</div></div>
<div class="row"><b>3</b><div>Бот сам напомнит им о встрече. Тебе ничего не нужно делать</div></div></div>
<div class="abs muted" style="left:72px;top:1150px;font-size:28px;font-weight:600">Меньше рутины — больше времени на своих</div>''', 4),
    page(EB + '''<h1 class="abs" style="left:72px;top:250px;font-size:84px">Кстати, вы уже<br><span class="p">можете быть у нас</span></h1>
<div class="abs chat" style="left:72px;right:72px;top:540px">
<div class="msg me">t.me/твой_чат</div>
<div class="msg bot">Это сообщество уже есть в каталоге. Сделать страницу вашей?</div>
<div class="msg bot">Нет страницы? Поможем завести — около 3 минут.</div></div>
<div class="bar" style="top:1060px;height:80px"></div>
<div class="abs lead" style="left:110px;right:110px;top:1052px">Просто пришли боту ссылку на свой чат или канал — он всё подскажет.</div>''', 5),
    page(EB + '''<div class="frame" style="left:72px;right:72px;top:240px;height:560px"><div style="background-image:url(../audience.jpg);background-position:50% 55%"></div></div>
<div class="abs muted" style="left:100px;top:740px;font-size:22px;font-weight:700;letter-spacing:.1em;z-index:2">ВИД СО СЦЕНЫ</div>
<div class="bar" style="top:860px;height:150px"></div>
<h1 class="abs" style="left:110px;right:72px;top:850px;font-size:76px">Расскажи о своих<br><span class="p">со сцены</span></h1>
<div class="abs lead" style="left:72px;right:90px;top:1040px;font-size:28px">На вечере «Сила сообществ» лидеры рассказывают, зачем создали своё сообщество и как в него попасть. На пилоте выступили 12 сообществ и пришли около 50 гостей.</div>
<div class="abs" style="left:72px;top:1200px;font-size:24px;font-weight:700">27 ноября · Ginger Hotel · ведут Полина и Максим</div>''', 6, swipe=False),
    page(EB + '''<div class="frame" style="left:72px;right:72px;top:240px;height:400px"><div style="background-image:url(../stage.jpg);background-size:150%;background-position:40% 42%"></div></div>
<div class="bar" style="top:700px;height:300px"></div>
<h1 class="abs" style="left:110px;right:72px;top:690px;font-size:100px">Сообщество<br>сильнее<br><span class="p">одиночества</span></h1>
<div class="abs" style="left:72px;top:1040px"><span class="pill" style="font-size:30px;padding:20px 34px">Добавить сообщество — ссылка в профиле</span></div>
<div class="abs lead" style="left:72px;right:90px;top:1150px;font-size:28px">Бесплатно, около 3 минут. Знаешь лидера сообщества? Перешли ему</div>''', 7, swipe=False, foot="@co.tbilisi"),
]

for tag, slides in (("A", A), ("B", B)):
    for i, h in enumerate(slides, 1):
        (OUT / f"{tag}-{i}.html").write_text(h)
print("ok")
