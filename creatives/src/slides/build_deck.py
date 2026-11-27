"""Презентация вечера «Сила сообществ»: слайды сообществ в новом стиле (1920x1080).
Тёмная основа + у каждого сообщества свой акцентный цвет. Тексты — из исходной презентации, фото/QR — оттуда же."""
import pathlib, json

HERE = pathlib.Path(__file__).parent
OUT = HERE / "deck"; OUT.mkdir(exist_ok=True)
LOGO = (HERE.parent / "co-logo-white.svg").read_text().replace('width="77"', 'width="96"').replace('height="38"', 'height="47"')
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(../../poster/fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F,U+2190-21FF'), ('cyrillic', 'U+0400-04FF')))
INK, BG = "#120A22", "#0B0812"


def css(A):
    return FF + f"""*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden}}
body{{font-family:'Onest',sans-serif;background:{BG};color:#fff;position:relative}}
.a{{position:absolute}}
.glow{{position:absolute;border-radius:50%;filter:blur(140px);background:{A};opacity:.20}}
/* фоновый мотив — контурные буквы бренда, а не заливка: читаются как буквы, не спорят с фото */
.giant{{position:absolute;font-weight:900;line-height:.8;letter-spacing:-.05em;color:transparent;-webkit-text-stroke:2px {A}66;white-space:nowrap;z-index:1}}
.top{{position:absolute;left:96px;right:96px;top:64px;display:flex;justify-content:space-between;align-items:center;z-index:9}}
.top .brand{{display:flex;align-items:center;gap:14px;font-size:32px;font-weight:500}}
.meta{{font-size:18px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.45)}}
.foot{{position:absolute;left:96px;right:96px;bottom:48px;display:flex;justify-content:space-between;z-index:9}}
.ph{{position:absolute;border-radius:40px;overflow:hidden;z-index:3;background:#1C1530}}
.ph img{{width:100%;height:100%;object-fit:cover;display:block}}
.kick{{font-size:20px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:{A}}}
.h{{font-weight:900;letter-spacing:-.035em;line-height:.92;text-transform:uppercase}}
.col{{position:absolute;z-index:5;display:flex;flex-direction:column}}
.lbl{{font-size:.62em;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{A};margin-bottom:.55em}}
.txt{{font-size:1em;line-height:1.4;color:rgba(255,255,255,.88);font-weight:400}}
.sec{{padding:1em 0;border-top:1.5px solid rgba(255,255,255,.10)}}
.sec:first-child{{border-top:none;padding-top:0}}
.card{{background:#17121F;border:1.5px solid {A}40;border-radius:32px;padding:40px 44px}}
.pill{{display:inline-block;border-radius:60px;padding:12px 26px;font-size:24px;font-weight:700;margin:0 10px 12px 0}}
.pill.f{{background:{A};color:{INK}}}
.pill.o{{border:2px solid {A}88;background:{A}18}}
.qr{{background:#fff;border-radius:28px;overflow:hidden;padding:22px}}
.qr img{{width:100%;height:100%;object-fit:contain;display:block}}
.row{{display:flex;gap:24px;line-height:1.55}}
.row b{{flex:none;width:6.4em;color:{A};font-weight:700}}
"""


FIT = """<script>document.fonts.ready.then(()=>{document.querySelectorAll('[data-fit]').forEach(e=>{
let s=parseFloat(e.dataset.fit);e.style.fontSize=s+'px';const max=parseFloat(e.dataset.max);
while(e.scrollHeight>max&&s>24){s-=1;e.style.fontSize=s+'px'}})});</script>"""


def page(A, body, motif="Co.", footleft="Найди своих", brand=True):
    glow = ('<div class="glow" style="left:1200px;top:-300px;width:1000px;height:760px"></div>'
            '<div class="glow" style="left:-360px;top:700px;width:900px;height:700px;opacity:.12"></div>')
    top = (f'<div class="top"><div class="brand">{LOGO if brand else ""}<span>{"Tbilisi" if brand else ""}</span></div>'
           f'<div class="meta">Сила сообществ · 27.11</div></div>')
    foot = f'<div class="foot"><div class="meta">{footleft}</div><div class="meta">cospace.world</div></div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css(A)}</style></head><body>{glow}'
            f'{motif}{top}{body}{foot}{FIT}</body></html>')


def secs(items):
    out = []
    for lbl, t in items:
        l = f'<div class="lbl">{lbl}</div>' if lbl else ""
        out.append(f'<div class="sec">{l}<div class="txt">{t}</div></div>')
    return "".join(out)


CO = '<div class="giant" style="right:-40px;bottom:-60px;font-size:720px">Co.</div>'


# сетка: поля 96, контент 96..1824, верх контента 176, низ 976
def founder(A, first, last, community, items, photo, letter, pos="50% 25%", kick="Основатель сообщества"):
    nm = max(len(first), len(last))
    fs = 124 if nm <= 10 else (104 if nm <= 14 else 84)
    return page(A, f"""
<div class="ph" style="left:96px;top:176px;width:760px;height:800px"><img src="../img/{photo}" style="object-position:{pos}"></div>
<div class="col" style="left:920px;right:96px;top:176px;height:800px;justify-content:space-between">
<div><div class="kick">{kick}</div>
<div class="h" style="font-size:{fs}px;margin-top:22px">{first}<br><span style="color:{A}">{last}</span></div>
<div style="margin-top:28px"><span class="pill f" style="font-size:26px;padding:14px 30px">{community}</span></div></div>
<div class="card" data-fit="32" data-max="420">{secs(items)}</div></div>""", CO)


def about(A, name, tagline, items, photo, letter, pos="50% 50%", photo2=None, kick="О сообществе", qr=None):
    if photo2:
        ph = (f'<div class="ph" style="left:96px;top:176px;width:600px;height:560px"><img src="../img/{photo}" style="object-position:{pos}"></div>'
              f'<div class="ph" style="left:720px;top:176px;width:336px;height:560px"><img src="../img/{photo2}"></div>')
    elif photo:
        ph = f'<div class="ph" style="left:96px;top:176px;width:960px;height:560px"><img src="../img/{photo}" style="object-position:{pos}"></div>'
    else:
        ph = (f'<div class="ph" style="left:96px;top:176px;width:960px;height:560px;background:#1C1530;border:1.5px solid {A}40;display:flex;align-items:center;justify-content:center">'
              f'<div style="font-weight:900;font-size:260px;letter-spacing:-.05em;color:{A};line-height:.8">{name.split()[-1].upper()}</div></div>')
    tg = f'<div class="txt" style="font-size:28px;margin-top:14px;color:rgba(255,255,255,.65)">{tagline}</div>' if tagline else ""
    nfs = 84 if len(name) <= 18 else 64
    return page(A, f"""
{ph}
<div class="col" style="left:96px;width:960px;top:776px"><div class="kick">{kick}</div>
<div class="h" style="font-size:{nfs}px;margin-top:14px">{name}</div>{tg}</div>
<div class="col" data-fit="32" data-max="{200 if qr else 800}" style="left:1120px;right:96px;top:176px">{secs(items)}</div>{qr_badge(qr[0], qr[1], 1120, 400, 440) if qr else ""}""", CO)


def join(A, name, first, rows, qr, caption="Страница на Co.Space"):
    r = "".join(f'<div class="row"><b>{k}</b><span>{v}</span></div>' for k, v in rows)
    cap = f'<div class="kick" style="margin-top:22px;text-align:center;color:rgba(255,255,255,.6)">{caption}</div>' if caption else ""
    motif = '<div class="giant" style="right:96px;bottom:92px;font-size:150px">НАЙДИ СВОИХ</div>'
    return page(A, f"""
<div class="col" style="left:96px;width:1060px;top:176px"><div class="kick">{name}</div>
<div class="h" style="font-size:100px;margin-top:20px">Как<br><span style="color:{A}">присоединиться</span></div>
<div data-fit="32" data-max="470" style="margin-top:40px">
<div class="sec"><div class="lbl">Первый шаг</div><div class="txt">{first}</div></div>
<div class="sec"><div class="lbl">Где нас найти</div><div class="txt">{r}</div></div></div></div>
<div class="col" style="left:1264px;width:560px;top:200px"><div class="qr" style="width:560px;height:560px"><img src="../img/{qr}"></div>{cap}</div>""", motif, "Наведи камеру на QR")


def single(A, name, tags, items, join_t, photo, qr, letter, pos="50% 50%", fit=False):
    pills = "".join(f'<span class="pill {"f" if i == 0 else "o"}">{t}</span>' for i, t in enumerate(tags))
    bg = 'background:#fff;padding:36px;' if fit else ''
    return page(A, f"""
<div class="ph" style="left:96px;top:176px;width:840px;height:560px;{bg}"><img src="../img/{photo}" style="object-position:{pos};{'object-fit:contain' if fit else ''}"></div>
<div class="col" style="left:96px;width:840px;top:776px"><div class="h" style="font-size:76px">{name}</div>
<div style="margin-top:22px">{pills}</div></div>
<div class="col" data-fit="32" data-max="500" style="left:1000px;right:96px;top:176px">{secs(items)}</div>
<div class="col" style="left:1000px;right:96px;top:716px;height:260px;flex-direction:row;gap:40px;align-items:flex-end">
<div class="qr" style="width:260px;height:260px;padding:14px;flex:none"><img src="../img/{qr}"></div>
<div style="padding-bottom:6px"><div class="kick">Как вступить</div><div class="txt" style="margin-top:12px;font-size:28px;word-break:break-word">{join_t}</div></div></div>""", CO)



def cover(A):
    motif = '<div class="giant" style="right:-30px;bottom:-70px;font-size:430px">Co.</div>'
    logo = LOGO.replace('width="96"', 'width="150"').replace('height="47"', 'height="74"')
    return page(A, f"""
<div class="a" style="left:1000px;top:0;right:0;bottom:0;background:url(../../poster/audience.jpg) 40% 50%/cover;filter:grayscale(.3) brightness(.55);
 -webkit-mask-image:linear-gradient(90deg,transparent,#000 45%);z-index:0"></div>
<div class="col" style="left:96px;top:210px;width:1100px">
<div style="display:flex;align-items:center;gap:36px">{logo}</div>
<div class="kick" style="margin-top:70px">Вечер сообществ Тбилиси</div>
<div class="h" style="font-size:190px;margin-top:22px;line-height:.86">Сила<br><span style="color:{A}">сообществ</span></div>
<div style="margin-top:54px;display:flex;gap:16px;flex-wrap:wrap">
<span class="pill f" style="font-size:30px;padding:16px 34px">27 ноября</span>
<span class="pill o" style="font-size:30px;padding:16px 34px">Ginger Hotel, Тбилиси</span></div></div>""", "", brand=False)


def founder_stats(A, first, last, community, desc, stats, photo, pos="50% 20%", kick="Ведёт вечер", qr=None):
    st = "".join(f'<div style="flex:1"><div style="font-size:84px;font-weight:900;letter-spacing:-.03em;color:{A};line-height:1">{n}</div>'
                 f'<div style="font-size:24px;line-height:1.3;color:rgba(255,255,255,.7);margin-top:10px">{t}</div></div>' for n, t in stats)
    return page(A, f"""
<div class="ph" style="left:96px;top:176px;width:760px;height:800px"><img src="../img/{photo}" style="object-position:{pos}"></div>
<div class="col" style="left:920px;right:96px;top:176px;height:800px;justify-content:space-between">
<div><div class="kick">{kick}</div>
<div class="h" style="font-size:124px;margin-top:22px">{first}<br><span style="color:{A}">{last}</span></div>
<div style="margin-top:28px"><span class="pill f" style="font-size:26px;padding:14px 30px">{community}</span></div>
<div class="txt" style="font-size:30px;margin-top:30px">{desc}</div></div>
<div style="display:flex;gap:40px;border-top:1.5px solid rgba(255,255,255,.12);padding-top:34px">{st}</div></div>{qr_badge(qr[0], qr[1], 600, 640, 230) if qr else ""}""", CO)



def max_who(A):
    bl = "".join(f'<div style="display:flex;gap:22px;padding:14px 0;border-top:1.5px solid rgba(255,255,255,.10)"><span style="color:{A};font-weight:800">—</span><span>{t}</span></div>'
                 for t in ["Предприниматель, основатель Co.", "Создавал коливинги и сообщества в Турции.",
                           "Развивает глобальную экосистему community hubs.", "Строит Y Mirissa — жилой комплекс с community hub на Шри-Ланке."])
    return page(A, f"""
<div class="ph" style="left:96px;top:176px;width:760px;height:800px"><img src="../img/max_portrait2.jpg" style="object-position:50% 25%"></div>
<div class="col" style="left:920px;right:96px;top:176px;height:800px;justify-content:space-between">
<div><div class="kick">Основатель Co.</div>
<div class="h" style="font-size:124px;margin-top:22px">Макс<br><span style="color:{A}">Заикин</span></div>
<div class="txt" style="font-size:36px;margin-top:26px;color:#fff;font-weight:500">Создаёт инфраструктуру нового образа жизни</div></div>
<div class="txt" style="font-size:28px">{bl}</div>
<div style="display:flex;gap:14px;flex-wrap:wrap"><span class="pill f">Недвижимость</span><span class="pill o">×</span><span class="pill f">Сообщества</span><span class="pill o">×</span><span class="pill f">Технологии</span></div></div>{qr_badge("qr_max_ig.png", "Instagram", 600, 640, 230)}""", CO)


def what_co(A):
    cards = [("Сообщества", "Люди по интересам и ценностям"), ("Города", "Локальная инфраструктура жизни"),
             ("Хабы", "Пространства для жизни и работы"), ("События", "Знакомства и новый опыт")]
    c = "".join(f'<div class="card" style="flex:1;padding:36px 36px 40px"><div style="font-size:64px;font-weight:900;color:{A};line-height:1;letter-spacing:-.04em">0{i + 1}</div>'
                f'<div style="font-size:40px;font-weight:800;margin-top:26px;letter-spacing:-.02em">{t}</div>'
                f'<div class="txt" style="font-size:26px;margin-top:12px;color:rgba(255,255,255,.7)">{d}</div></div>' for i, (t, d) in enumerate(cards))
    return page(A, f"""
<div class="col" style="left:96px;right:96px;top:176px"><div class="kick">Что такое Co.</div>
<div class="h" style="font-size:132px;margin-top:22px">Найди своих.<br><span style="color:{A}">Найдёшь своё.</span></div>
<div class="txt" style="font-size:36px;margin-top:30px;color:#fff">Глобальная экосистема людей, сообществ и пространств.</div></div>
<div class="a" style="left:96px;right:96px;top:690px;display:flex;gap:28px;z-index:5">{c}</div>""", CO)


def power(A):
    items = ["Сообщества и их лидеры", "Хабы и пространства", "Люди, идеи и возможности"]
    it = "".join(f'<div style="display:flex;align-items:center;gap:28px;padding:26px 0;border-top:1.5px solid rgba(255,255,255,.12)">'
                 f'<span style="width:22px;height:22px;border-radius:50%;background:{A};flex:none"></span><span style="font-size:40px;font-weight:700">{t}</span></div>' for t in items)
    motif = '<div class="giant" style="right:-30px;bottom:-70px;font-size:430px">Co.</div>'
    return page(A, f"""
<div class="col" style="left:96px;width:900px;top:176px"><div class="kick">Сила сообществ</div>
<div class="h" style="font-size:124px;margin-top:22px;line-height:.86">Сила<br><span style="color:{A}">сообществ</span></div>
<div class="txt" style="font-size:36px;margin-top:34px;color:#fff">Объединяем тех, кто создаёт среду города.</div></div>
<div class="col" style="left:1120px;right:96px;top:250px">{it}<div style="border-top:1.5px solid rgba(255,255,255,.12)"></div></div>
<div class="a" style="left:96px;top:800px;z-index:5"><span class="pill f" style="font-size:40px;padding:22px 44px">Не конкурировать. Объединяться.</span></div>""", motif)



def statement(A, l1, l2, kick=""):
    motif = '<div class="giant" style="right:-30px;bottom:-70px;font-size:430px">Co.</div>'
    k = f'<div class="kick">{kick}</div>' if kick else ""
    return page(A, f"""
<div class="col" style="left:96px;right:96px;top:0;bottom:0;justify-content:center">{k}
<div class="h" style="font-size:150px;margin-top:26px;line-height:.9">{l1}</div>
<div class="h" style="font-size:150px;line-height:.9;color:{A}">{l2}</div></div>""", motif)


def speaker(A, first, last, org, topic, photo, pos="50% 20%"):
    return page(A, f"""
<div class="ph" style="left:96px;top:176px;width:760px;height:800px"><img src="../img/{photo}" style="object-position:{pos}"></div>
<div class="col" style="left:920px;right:96px;top:176px;height:800px;justify-content:space-between">
<div><div class="kick">Спикер</div>
<div class="h" style="font-size:124px;margin-top:22px">{first}<br><span style="color:{A}">{last}</span></div>
<div style="margin-top:28px"><span class="pill f" style="font-size:28px;padding:14px 30px">{org}</span></div></div>
<div><div class="lbl" style="font-size:20px">Тема выступления</div>
<div class="h" style="font-size:64px;line-height:1">{topic}</div></div></div>""", CO)


def em_founder(A):
    return page(A, f"""
<div class="ph" style="left:96px;top:176px;width:760px;height:800px;background:{A};display:flex;align-items:center;justify-content:center">
<div style="font-weight:900;font-size:120px;letter-spacing:-.04em;color:{INK};line-height:.9;text-align:center">Event<br>Mates</div></div>
<div class="col" style="left:920px;right:96px;top:176px;height:800px;justify-content:space-between">
<div><div class="kick">Основатель EventMates</div>
<div class="h" style="font-size:124px;margin-top:22px">Максим<br><span style="color:{A}">Муратов</span></div>
<div style="margin-top:28px"><span class="pill f" style="font-size:28px;padding:14px 30px">EventMates</span></div></div>
<div class="card" data-fit="30" data-max="440">{secs([("Кто я", "Основатель EventMates, IT-архитектор и разработчик."),
 ("Зачем я создал проект", "Чтобы участники находили единомышленников, партнёров и новые возможности для сотрудничества.")])}</div></div>""", CO)


def em_product(A):
    cards = [("AI-нетворкинг", "Поиск людей с учётом интересов и целей участников."),
             ("Регистрация и бейджи", "Печать именных бейджей прямо на входе."),
             ("Программа и активности", "Расписание, рассадка, опросы и обратная связь.")]
    c = "".join(f'<div class="card" style="flex:1;padding:32px 34px"><div style="font-size:56px;font-weight:900;color:{A};line-height:1">0{i+1}</div>'
                f'<div style="font-size:34px;font-weight:800;margin-top:20px">{t}</div><div class="txt" style="font-size:24px;margin-top:10px;color:rgba(255,255,255,.72)">{d}</div></div>'
                for i, (t, d) in enumerate(cards))
    return page(A, f"""
<div class="col" style="left:96px;width:1060px;top:176px"><div class="kick">EventMates</div>
<div class="h" style="font-size:72px;margin-top:20px">Больше полезных знакомств.<br><span style="color:{A}">Меньше рутины для организатора.</span></div></div>
<div class="a" style="left:96px;width:1060px;top:520px;display:flex;gap:24px;z-index:5">{c}</div>
<div class="a txt" style="left:96px;width:1060px;top:880px;font-size:24px;color:rgba(255,255,255,.6);z-index:5">Скоро: привлечение новых участников — персональные рекомендации ваших событий по интересам.</div>
<div class="card" style="position:absolute;left:1230px;right:96px;top:176px;height:800px;z-index:5;display:flex;flex-direction:column;justify-content:space-between">
<div><div class="lbl" style="font-size:20px">Организаторам сообществ и событий</div>
<div style="font-size:40px;font-weight:800;line-height:1.1">Попробуйте EventMates на вашем следующем мероприятии.</div>
<div class="txt" style="font-size:24px;margin-top:20px">Для мероприятий со свободным входом до 100 участников — <b style="color:{A}">0 ₾</b></div></div>
<div class="txt" style="font-size:28px;line-height:1.7"><div><span style="color:{A};font-weight:700">Telegram</span>&nbsp; @muratov_m_a</div>
<div><span style="color:{A};font-weight:700">Телефон</span>&nbsp; +995 551 126 537</div><div><span style="color:{A};font-weight:700">Сайт</span>&nbsp; eventmates.io</div></div></div>""", CO)



def gallery(A, name, imgs):
    # 7 фото мозаикой: сетка 4 колонки x 2 ряда, первое фото — 2x2
    pos = [(0, 0, 2, 2), (2, 0, 1, 1), (3, 0, 1, 1), (2, 1, 1, 1), (3, 1, 1, 1)]
    cw, ch, g, x0, y0 = 438, 300, 16, 96, 176
    t = ""
    for (c, r, w, h), im in zip(pos, imgs):
        t += (f'<div class="ph" style="left:{x0 + c * (cw + g)}px;top:{y0 + r * (ch + g)}px;width:{w * cw + (w - 1) * g}px;'
              f'height:{h * ch + (h - 1) * g}px;border-radius:28px"><img src="../img/{im}"></div>')
    return page(A, f"""{t}
<div class="col" style="left:96px;width:1400px;top:820px"><div class="kick">Как это выглядит</div>
<div class="h" style="font-size:84px;margin-top:14px">{name}</div></div>""", CO)



def networking_qr(A):
    motif = '<div class="giant" style="left:80px;bottom:96px;font-size:150px">НАЙДИ СВОИХ</div>'
    steps = ["Наведи камеру на QR", "Зарегистрируйся в EventMates", "Заполни интересы — приложение подскажет, с кем познакомиться"]
    st = "".join(f'<div style="display:flex;gap:26px;align-items:flex-start;padding:22px 0;border-top:1.5px solid rgba(255,255,255,.10)">'
                 f'<span style="font-size:44px;font-weight:900;color:{A};line-height:1;width:50px">{i+1}</span><span style="font-size:34px;font-weight:600;line-height:1.25">{t}</span></div>'
                 for i, t in enumerate(steps))
    return page(A, f"""
<div class="col" style="left:96px;width:1060px;top:176px"><div class="kick">Нетворкинг · EventMates</div>
<div class="h" style="font-size:96px;margin-top:22px">Ты уже<br><span style="color:{A}">зарегистрирован?</span></div>
<div style="margin-top:44px">{st}</div></div>
<div class="col" style="left:1264px;width:560px;top:200px"><div class="qr" style="width:560px;height:560px"><img src="../img/qr_eventmates.png"></div>
<div class="kick" style="margin-top:22px;text-align:center;color:rgba(255,255,255,.6)">Регистрация на нетворкинг</div></div>""", motif, "Наведи камеру на QR")



def qr_badge(img, label, left, top, size=230):
    return (f'<div class="a" style="left:{left}px;top:{top}px;width:{size}px;z-index:6;text-align:center">'
            f'<div style="background:#fff;border-radius:24px;padding:12px;box-shadow:0 20px 40px rgba(0,0,0,.45)">'
            f'<img src="../img/{img}" style="width:100%;display:block;border-radius:12px"></div>'
            f'<div class="meta" style="margin-top:12px;color:rgba(255,255,255,.75)">{label}</div></div>')


# ---------------- контент (из презентации «Диана») ----------------
S = []
A = "#A874FF"
S += [("00-cover", cover(A)),
      ("00b-net", networking_qr(A)),
      ("pol-1", founder_stats(A, "Полина", "Язвенко", "TEXTURA",
        "Предприниматель, тренер по публичным выступлениям, эксперт по публичности и медийности. Основатель онлайн-школы TEXTURA с образовательной лицензией.",
        [("500+", "спикеров обучено за 5 лет"), ("30+", "тренингов и программ"), ("3 года", "в прямом эфире на ТВ")],
        "polina_portrait.jpg", "50% 18%", qr=("qr_polina_ig.png", "Instagram"))),
      ("pol-2", about(A, "JB Glamping", "Глэмпинг в Грузии",
        [("Кто", "Полина Язвенко — сооснователь JB Glamping вместе с мужем"),
         ("Что это", "Глэмпинг в Грузии: купола посреди зелёных полей с видом на горы")],
        "glamping.jpg", "G", "50% 45%", kick="Сооснователь")),
      ("tex-1", about(A, '<img src="../img/textura_white.png" style="height:64px;display:block;margin:6px 0 4px">', "",
        [("О сообществе", "Сообщество людей, которые создают компании, запускают проекты, инвестируют, строят личные бренды и влияют на рынок.")],
        "textura_stage.jpg", "T", "50% 50%", qr=("qr_textura_big.png", "TEXTURA"))),
      ("max-1", max_who(A)),
      ("max-2", what_co(A)),
      ("max-3", power(A)),
      ("st-1", statement(A, "Люди для людей.", "Для всего остального есть технологии.")),
      ("st-2", statement(A, "Люди. Идеи.", "Возможности.")),
      ("lasha", speaker(A, "Лаша", "Чхенкели", "TBC Bank", "Банковские возможности для экспатов", "lasha.jpg", "50% 15%"))]
# 0. По душам — Анастасия Кулькова
A = "#A874FF"
S += [("kul-1", founder(A, "Анастасия", "Кулькова", "Женское сообщество «По душам»",
        [("Кто вы", "Предприниматель в сфере инвестиционной недвижимости и организатор женских международных бизнес-акселераторов Openmind"),
         ("Зачем вы собрали сообщество", "Личный запрос на качественное женское окружение, яркий новый опыт и отдых")],
        "kul_portrait.jpg", "П", "50% 25%")),
      ("kul-2", about(A, "По душам", "Женское сообщество Тбилиси",
        [("Наша миссия", "Мы помогаем женщинам в Тбилиси найти своё окружение: людей, с которыми хочется расти, отдыхать и делиться жизнью. «По душам» — это третье пространство, не работа и не семья, а место для себя."),
         ("Что делаем вместе", "Каждый месяц собираемся на установочную встречу: ставим цели и находим бадди-пару. Читаем вместе книги, занимаемся спортом, каждый месяц отдыхаем по-новому."),
         ("Для кого мы", "Для активных женщин от 25 до 70 лет, экспатов и местных, которым интересны саморазвитие, предпринимательство, культура и путешествия.")],
        "kul_group.jpg", "П", "50% 50%")),
      ("kul-3", gallery(A, "По душам", ["kul_g4.jpg", "kul_g1.jpg", "kul_g2.jpg", "kul_g7.jpg", "kul_g5.jpg"])),
      ("kul-4", join(A, "Женское сообщество «По душам»", "Напиши в директ и запишись на первую бесплатную встречу в формате нетворкинг-завтрака",
        [("Telegram", "t.me/+xSXb7MfEeTA2M2Iy"), ("Instagram", "@tbilisi_events"), ("Встречи", "в Тбилиси")], "cs_kul.png"))]
# 1. Ertad — жёлтый
A = "#A874FF"
S += [("ertad-1", founder(A, "Ирина", "Ластовка", "Бизнес-сообщество Ertad",
        [("Кто вы", "Основатель и идейный вдохновитель"),
         ("Зачем вы собрали сообщество", "Объединить местных и экспатов, чтобы вместе делать крутой бизнес в Грузии")],
        "ertad_founder.jpg", "E", "50% 30%")),
      ("ertad-2", about(A, "Бизнес-сообщество Ertad", "Для тех, кто развивает бизнес в Грузии",
        [("Наша миссия", "Крутые совместные проекты экспатов и грузин."),
         ("Что делаем вместе", "Бизнес-завтраки, круглые столы, встречи, конференции, подкаст"),
         ("Для кого мы", "Все, для кого актуальна тема бизнеса в Грузии.")], None, "E")),
      ("ertad-3", join(A, "Бизнес-сообщество Ertad", "Выбрать интересное для вас мероприятие, заполнить анкету и прийти.",
        [("Telegram", "@ertad_community"), ("Instagram", "@ertad.community"), ("Встречи", "Тбилиси и Батуми")], "cs_ertad.png"))]
# 1b. Телеграм о Грузии — Николай Левшиц
A = "#A874FF"
S += [("lev-1", founder(A, "Николай", "Левшиц", "Телеграм о Грузии",
        [("Кто он", "Основатель и автор телеграм-канала «Телеграм о Грузии»"),
         (None, "Создал многочисленные ресурсы и проекты о Грузии. Блогер, активный участник сообществ по спорту и IT.")],
        "lev_founder.jpg", "T", "40% 30%", kick="Спикер · основатель канала")),
      ("lev-2", about(A, "Телеграм о Грузии", "Самый популярный телеграм-канал о Грузии",
        [("О чём канал", "Николай рассказывает о Грузии: о жизни, новостях и обо всём, что полезно знать, если ты здесь живёшь или собираешься переехать."),
         ("Для кого", "Для тех, кто живёт в Грузии или собирается переехать.")],
        "lev_about.jpg", "T", "50% 40%", kick="О канале")),
      ("lev-3", join(A, "Телеграм о Грузии", "Наведи камеру на QR — откроется страница канала на Co.Space, оттуда можно сразу перейти в канал.",
        [("Co.Space", "cospace.world/ru/communities/pro-georgia-pro-gruziyu")], "cs_lev.png"))]
# 2. ESTATE HUB — синий
A = "#A874FF"
S += [("estate-1", founder(A, "Diana", "Panieva-Kutateladze", "ESTATE HUB",
        [(None, "Real Estate &amp; Investment Advisor | Real Estate Lawyer"),
         (None, "<b style='color:#fff'>Основала ESTATE HUB</b> — сообщество, усиливающее бизнес в сфере недвижимости.")],
        "estate_founder.jpg", "E", "50% 30%")),
      ("estate-2", about(A, "ESTATE HUB", "Объединяем сильных игроков рынка для синергии, роста и совместных сделок.",
        [("Наша миссия", "Объединяем и усиливаем экспертов рынка недвижимости, задавая высокие стандарты профессии и этики партнёрства."),
         ("Что делаем вместе", "Закрытые бизнес-встречи и нетворкинг, практические мастермайнды и совместные брокер-туры с девелоперами в Тбилиси."),
         ("Для кого мы", "Специалистам и компаниям рынка недвижимости Грузии: риэлторам, девелоперам, юристам, инвесторам, а также подрядчикам в сфере ремонта, дизайна, хоумстейджинга и сопровождения сделок.")],
        "estate_about.jpg", "H")),
      ("estate-3", join(A, "ESTATE HUB", "Заполните анкету (ссылка в шапке профиля в Instagram), далее мы с вами свяжемся для проведения краткого интервью",
        [("Telegram", "@RealEstateDi"), ("Instagram", "@estate_hub_1"), ("Встречи", "Тбилиси и онлайн")], "cs_estate.png"))]
# 3. Tbilisi Running Club — розовый
A = "#A874FF"
S += [("trc-1", founder(A, "Konstantin", "Kocura", "Tbilisi Running Club",
        [("Капитан клуба", "Вместе с друзьями основал Tbilisi Running Club — открытое сообщество для тех, кто любит Грузию через бег")],
        "trc_founder.jpg", "R", "50% 35%")),
      ("trc-2", about(A, "Tbilisi Running Club", "Бегаем вместе с 2019 года: по городу, на стадионе, холмам и в горах.",
        [("Наша миссия", "Объединяем любителей бега всех уровней, возрастов и национальностей и делаем бег в Тбилиси доступным для всех."),
         ("Что делаем вместе", "Бесплатные тренировки почти каждый день: город, стадион, трейлы в холмах, пробежки на рассвете и ночью, выезды в горы на выходных"),
         ("Для кого мы", "Всем, кто уже бегает или только хочет начать: от новичков на лёгких 3 км до марафонцев и ультрабегунов. Тбилисцам, экспатам и гостям города.")],
        "trc_about.jpg", "R")),
      ("trc-3", join(A, "Tbilisi Running Club", "Подпишитесь на Telegram: канал или чат (расписание — по понедельникам), выберите тренировку и приходите на старт",
        [("Telegram", "@tbilisirunningclub"), ("Instagram", "@tbilisirunningclub"), ("Strava", "@tbilisirunningclub"), ("Чат", "@tbilisirunningclubtalks")], "cs_trc.png"))]
# 4. Sami Residence — зелёный (1 слайд)
A = "#A874FF"
S += [("sami", single(A, "Sami Residence", ["Адаптация в Грузии", "Культурное погружение", "Новые друзья"],
        [("Наша миссия", "Помогаем в адаптации в Грузии"),
         ("О чём сообщество", "Мы изучаем грузинский язык, культуру и историю. Объединяем людей через ивенты со смыслом")],
        "Страница на Co.Space: cospace.world/ru/communities/sami-residence", "sami_photo.jpg", "sami_qr2.png", "S", "50% 40%", fit=True))]
# 5. ISOUL — фиолетовый
A = "#A874FF"
S += [("isoul-1", founder(A, "Юлия", "Шенгелия", "ISOUL Грузия",
        [("Кто вы", "Президент ISOUL в Грузии. Психолог, профайлер, стратег личного бренда и лидерского влияния, 14 лет психологической практики."),
         ("Зачем вы собрали сообщество", "Чтобы у женщин в Грузии было сильное окружение и доступ к глобальной экосистеме ISOUL: место, где можно найти поддержку, единомышленниц и расти вместе.")],
        "isoul_founder.jpg", "I", "50% 30%")),
      ("isoul-2", about(A, "ISOUL", "",
        [("Наша миссия", "Создать экосистему поддержки женщин-лидеров по всему миру: соединить технологии и осознанность, помогать масштабировать проекты женщин и выстраивать кросс-культурные связи."),
         ("Что делаем вместе", "Глобальный нетворкинг онлайн и офлайн, бизнес-клуб и премия ISOUL Women Leadership Award. В 2026 году — бизнес-кемп в Тбилиси."),
         ("Для кого мы", "Для женщин-лидеров, предпринимательниц и экспертов, которым важны рост и сильное окружение. За 4 года: 8 000+ участниц, 250+ резиденток, 32 страны.")],
        "isoul_about.jpg", "S")),
      ("isoul-3", join(A, "ISOUL Грузия", "Заполните анкету по QR-коду и пройдите интервью с президентом ISOUL в Грузии Юлией Шенгелия.",
        [("Telegram", "t.me/+N9qDQ3-1Kv0xZmQ6 (чат ISOUL в Грузии)"), ("Instagram", "@isoul.community"), ("Встречи", "Тбилиси, Батуми"), ("Сайт", "isoul.space")],
        "isoul_qr.jpg"))]
# 6. Marketing and AI — бирюзовый
A = "#A874FF"
S += [("mai-1", founder(A, "Alex", "Kochnev", "Marketing and AI",
        [("Кто вы", "Предприниматель, 20+ лет опыта, более 4 лет внедряю AI в проекты. Помогаю с помощью AI увеличивать прибыль."),
         ("Зачем вы собрали сообщество", "Чтобы любой мог увидеть, что AI — это не сложно, но очень-очень полезно)")],
        "mai_founder.jpg", "A", "50% 25%")),
      ("mai-2", about(A, "Marketing and AI", "",
        [("Наша миссия", "Сделать AI в маркетинге доступным для «не технарей», а маркетинг — доступным для «технарей»"),
         ("Что делаем вместе", "Проводим воркшопы, лекции, разборы инструментов"),
         ("Для кого мы", "Для предпринимателей, маркетологов, AI-энтузиастов, специалистов")],
        "mai_about.jpg", "M")),
      ("mai-3", join(A, "Marketing and AI", "Go в наш чат!",
        [("Telegram", "@martech_ai"), ("Instagram", "@alex.happy.longevity"), ("Встречи", "Tbilisi, Ibis Tbilisi Stadium")], "cs_mai.png"))]
# 7. Tbilisi Coffee Club — оранжевый (1 слайд)
A = "#A874FF"
S += [("coffee", single(A, "Tbilisi Coffee Club", ["Coffee", "Networking", "Community"],
        [("Наша миссия", "Помогать людям находить свой круг общения, друзей и единомышленников в Тбилиси."),
         ("О чём сообщество", "Объединяем любителей кофе и живого общения. Знакомимся за чашкой кофе, каждую неделю встречаемся в разных кофейнях Тбилиси, открываем новые места и проводим время вместе.")],
        "t.me/TbilisiCoffeeClub", "coffee_photo.jpg", "cs_coffee.png", "C"))]
# 8. Mesto — коралловый
A = "#A874FF"
S += [("mesto-1", founder(A, "Ирина", "Сивридкина", "Mesto",
        [(None, "<b style='color:#fff'>Mesto</b> — пространство для настольных игр и мероприятий. Совладелец и идейный вдохновитель Mesto."),
         (None, "Мы хотим показать, насколько увлекательным может быть интеллектуальный досуг. Он помогает людям находить общие интересы, знакомиться, создавать настоящие социальные связи и вместе открывать новое.")],
        "mesto_founder.jpg", "M", "50% 40%")),
      ("mesto-2", about(A, "Mesto", "Настольные игры в Тбилиси",
        [("Наша миссия", "Создаём в Тбилиси уютное место, где можно знакомиться, общаться и находить единомышленников за настольными играми и различными эвентами."),
         ("Что делаем вместе", "Проводим встречи и мероприятия с настольными играми, а также создаём пространство для коворкинга и общения."),
         ("Для кого мы", "Для тех, кто любит настольные игры, ищет компанию и новые знакомства.")],
        "mesto_about.jpg", "M")),
      ("mesto-3", join(A, "Mesto настольные игры", "Подпишись на группу в Telegram и бот, выбирай в боте мероприятия и записывайся.",
        [("Telegram", "@mesto_games"), ("Бот", "@mesto123_bot"), ("Instagram", "@mesto.tbilisi"), ("Встречи", "Тбилиси, Вахтанга Бочоришвили 37А")], "cs_mesto.png"))]
# 9. Bloggers & UGC Creators — лайм
A = "#A874FF"
S += [("blog-1", founder(A, "Василий и Мария", "Стешенко", "Bloggers &amp; UGC Creators",
        [("Кто вы", "Совладельцы маркетингового агентства по продвижению индустрии Wellness, Health &amp; Beauty, эксперты по AI, блогеры"),
         ("Зачем вы собрали сообщество", "Идея содружества по интересу создания контента и развития бизнесов Грузии")],
        "blog_founder.jpg", "B", "50% 30%")),
      ("blog-2", about(A, "Bloggers &amp; UGC Creators", "",
        [("Наша миссия", "Объединить блогеров и креаторов, улучшить качество взаимодействия с компаниями и брендами"),
         ("Что делаем вместе", "Тематические встречи по блогингу, монтажу и коллаборациям; блогерские туры; обмен опытом"),
         ("Для кого мы", "Для лидеров мнений и креаторов, кто любит делиться впечатлениями о посещении ресторанов, отелей, спа и других бизнесов Грузии.")],
        "blog_about.jpg", "B")),
      ("blog-3", join(A, "Bloggers &amp; UGC Creators", "Напишите в чат, оплатите первый месяц участия — 40 лари",
        [("Telegram", "@mari_manjari"), ("Instagram", "@mir_vdvoem"), ("Встречи", "Тбилиси, Батуми и онлайн")], "cs_blog.png"))]
# Balance Community — Игорь Копыльцов
A = "#A874FF"
S += [("igor-1", founder(A, "Игорь", "Копыльцов", "Balance Community",
        [("Кто вы", "Проводник свободы. Парус, доска, боевые искусства — разные способы почувствовать один принцип: всё есть баланс. В неустойчивом равновесии можно найти опору в себе и выбирать, как действовать."),
         ("Зачем собрали сообщество", "Чтобы передать то, что Игорь сам понял через движение и взаимодействие со стихиями, с людьми, с миром. Этот опыт даёт опору, с которой можно найти свою свободу и идти своим путём.")],
        "igor_founder.jpg", "B", "50% 20%")),
      ("igor-2", about(A, "Balance Community", "Сообщество свободных людей",
        [("Наша миссия", "Свобода движения, свобода выбора, свобода личности. На практике человек обнаруживает, что способен на большее, чем привык думать о себе."),
         ("Что делаем вместе", "Ходим под парусом, встаём на доски, собираем экипажи и едем в кэмпы. В Balance Hub исследуем движение и взаимодействие на тренировках, в импровизации и в разговоре."),
         ("Для кого", "Для тех, кто хочет стать ближе к себе, найти свои смыслы и понять, куда идти дальше. Кого тянет к движению, к живым людям и к энергии на грани выхода из равновесия.")],
        "igor_founder.jpg", "B", "50% 25%")),
      ("igor-3", join(A, "Balance Community", "Вступить в Balance Community. Познакомиться с людьми и выбрать, с чего хочется начать.",
        [("Telegram", "@Balance_Community_Hub")], "cs_igor.png"))]
# 10. Бизнес Круг — маджента
A = "#A874FF"
S += [("krug-1", founder(A, "Елена", "Пулькина", "Сообщество Бизнес Круг",
        [(None, "Сооснователь проекта «Система» (обучение для экспертов и предпринимателей)"),
         (None, "Создаю среду для роста и наполненной жизни для себя и других")],
        "krug_founder.jpg", "K", "50% 25%")),
      ("krug-2", about(A, "Бизнес Круг", "",
        [("Наша миссия", "Создавать среду для роста и жизни: людей, знания, события"),
         ("Наши ценности", "Открытость и доброта, проактивность, честность, быть вкладом в сообщество и друг друга"),
         ("Что делаем вместе", "Падел, хайки, бани, настольные игры, выступления спикеров, мастермайнды, камерные закрытые встречи"),
         ("Для кого мы", "Предприниматели и эксперты, которые живут в Грузии и ведут бизнес здесь или в любой точке мира")],
        "krug_about.jpg", "K", photo2="krug_about2.jpg")),
      ("krug-3", join(A, "Сообщество Бизнес Круг", "Подписывайся на Instagram, пришлю расписание ближайших встреч",
        [("Instagram", "@krug.tbilisi"), ("Встречи", "офлайн, Тбилиси")], "krug_qr.jpg"))]

A = "#A874FF"
S += [("em-1", em_founder(A)), ("em-2", em_product(A))]

order = []
for i, (k, h) in enumerate(S, 1):
    fn = f"{i:02d}-{k}.html"; (OUT / fn).write_text(h); order.append(fn)
(OUT / "order.json").write_text(json.dumps(order))
print(len(order))
