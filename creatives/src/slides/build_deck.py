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
.glow{{position:absolute;border-radius:50%;filter:blur(120px);background:{A};opacity:.22}}
.giant{{position:absolute;font-weight:900;color:{A};line-height:.78;letter-spacing:-.05em}}
.brand{{position:absolute;left:80px;top:64px;display:flex;align-items:center;gap:14px;font-size:34px;font-weight:500;z-index:9}}
.ph{{position:absolute;border-radius:44px;overflow:hidden;z-index:3;background:#1C1530}}
.ph img{{width:100%;height:100%;object-fit:cover;display:block}}
.kick{{font-size:22px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{A}}}
.h{{font-weight:900;letter-spacing:-.04em;line-height:.92;text-transform:uppercase}}
.card{{position:absolute;background:#17121F;border:1.5px solid {A}55;border-radius:40px;padding:44px 48px;z-index:4;overflow:hidden}}
.lbl{{font-size:1em;font-weight:800;color:{A};margin-bottom:.35em}}
.txt{{font-size:1em;line-height:1.38;color:rgba(255,255,255,.86);font-weight:400}}
.sec+.sec{{margin-top:1.1em}}
.pill{{display:inline-block;border-radius:60px;padding:12px 26px;font-size:24px;font-weight:700;margin:0 10px 12px 0}}
.pill.f{{background:{A};color:{INK}}}
.pill.o{{border:2px solid {A}99;background:{A}1f}}
.qr{{position:absolute;background:#fff;border-radius:32px;z-index:4;overflow:hidden;padding:22px}}
.qr img{{width:100%;height:100%;object-fit:contain;display:block}}
.row{{display:flex;gap:20px;font-size:1em;line-height:1.55}}
.row b{{flex:none;width:7.2em;color:{A};font-weight:700}}
"""


FIT = """<script>document.fonts.ready.then(()=>{document.querySelectorAll('[data-fit]').forEach(e=>{
let s=parseFloat(e.dataset.fit);e.style.fontSize=s+'px';const max=e.clientHeight;
while(e.scrollHeight>max+1&&s>16){s-=1;e.style.fontSize=s+'px'}})});</script>"""


def page(A, body):
    glow = (f'<div class="glow" style="left:1250px;top:-250px;width:900px;height:700px"></div>'
            f'<div class="glow" style="left:-300px;top:650px;width:900px;height:700px;opacity:.14"></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css(A)}</style></head><body>{glow}'
            f'<div class="brand">{LOGO}<span>Tbilisi</span></div>{body}{FIT}</body></html>')


def secs(items):
    out = []
    for lbl, t in items:
        l = f'<div class="lbl">{lbl}</div>' if lbl else ""
        out.append(f'<div class="sec">{l}<div class="txt">{t}</div></div>')
    return "".join(out)


def founder(A, first, last, community, items, photo, letter, pos="50% 25%"):
    nm = max(len(first), len(last))
    fs = 132 if nm <= 10 else (110 if nm <= 14 else 92)
    return page(A, f"""
<div class="giant" style="left:-70px;top:140px;font-size:920px">C</div>
<div class="ph" style="left:150px;top:190px;width:680px;height:800px"><img src="../img/{photo}" style="object-position:{pos}"></div>
<div class="a" style="left:900px;top:170px;right:80px;z-index:5"><div class="kick">Основатель сообщества</div>
<div class="h" style="font-size:{fs}px;margin-top:24px">{first}<br><span style="color:{A}">{last}</span></div>
<div style="margin-top:30px"><span class="pill f" style="font-size:28px;padding:14px 30px">{community}</span></div></div>
<div class="card" data-fit="30" style="left:900px;top:600px;width:940px;height:400px">{secs(items)}</div>""")


def about(A, name, tagline, items, photo, letter, pos="50% 50%", photo2=None):
    ph = (f'<div class="ph" style="left:80px;top:170px;width:1000px;height:600px"><img src="../img/{photo}" style="object-position:{pos}"></div>' if photo
          else f'<div class="ph" style="left:80px;top:170px;width:1000px;height:600px;background:{A};display:flex;align-items:center;justify-content:center"><div style="font-weight:900;font-size:300px;letter-spacing:-.05em;color:{INK};line-height:.8">{name.split()[-1].upper()}</div></div>')
    if photo2:
        ph = (f'<div class="ph" style="left:80px;top:170px;width:600px;height:600px"><img src="../img/{photo}" style="object-position:{pos}"></div>'
              f'<div class="ph" style="left:700px;top:170px;width:380px;height:600px"><img src="../img/{photo2}"></div>')
    tg = f'<div class="txt" style="font-size:28px;margin-top:16px;max-width:1000px;color:rgba(255,255,255,.7)">{tagline}</div>' if tagline else ""
    nfs = 88 if len(name) <= 18 else 70
    return page(A, f"""
<div class="giant" style="right:-90px;top:110px;font-size:900px;opacity:.9">O</div>
{ph}
<div class="a" style="left:80px;top:810px;width:1000px;z-index:5"><div class="kick">О сообществе</div>
<div class="h" style="font-size:{nfs}px;margin-top:14px">{name}</div>{tg}</div>
<div class="card" data-fit="28" style="left:1140px;top:170px;width:700px;height:840px">{secs(items)}</div>""")


def join(A, name, first, rows, qr, caption=""):
    r = "".join(f'<div class="row"><b>{k}</b><span>{v}</span></div>' for k, v in rows)
    cap = f'<div class="a kick" style="left:1300px;top:825px;width:500px;text-align:center;color:rgba(255,255,255,.6)">{caption}</div>' if caption else ""
    return page(A, f"""
<div class="giant" style="right:40px;bottom:20px;font-size:150px;opacity:.18;white-space:nowrap;line-height:.85">НАЙДИ СВОИХ</div>
<div class="a" style="left:80px;top:170px;z-index:5"><div class="kick">{name}</div>
<div class="h" style="font-size:118px;margin-top:22px">Как<br><span style="color:{A}">присоединиться</span></div></div>
<div class="card" data-fit="28" style="left:80px;top:500px;width:1100px;height:420px">
<div class="sec"><div class="lbl">Первый шаг</div><div class="txt">{first}</div></div>
<div class="sec"><div class="lbl">Где нас найти</div>{r}</div></div>
<div class="qr" style="left:1300px;top:300px;width:500px;height:500px"><img src="../img/{qr}"></div>{cap}""")


def single(A, name, tags, items, join_t, photo, qr, letter, pos="50% 50%", fit=False):
    pills = "".join(f'<span class="pill {"f" if i == 0 else "o"}">{t}</span>' for i, t in enumerate(tags))
    return page(A, f"""
<div class="giant" style="right:-60px;top:60px;font-size:760px;opacity:.9">C</div>
<div class="ph" style="left:80px;top:170px;width:820px;height:600px;{'background:#fff;padding:40px' if fit else ''}"><img src="../img/{photo}" style="object-position:{pos};{'object-fit:contain' if fit else ''}"></div>
<div class="a" style="left:80px;top:805px;width:900px;z-index:5"><div class="h" style="font-size:72px">{name}</div>
<div style="margin-top:20px">{pills}</div></div>
<div class="card" data-fit="28" style="left:980px;top:170px;width:860px;height:480px">{secs(items)}</div>
<div class="a" style="left:980px;top:700px;width:470px;z-index:5"><span class="pill f" style="background:#fff">Как вступить</span>
<div class="txt" style="margin-top:10px;font-size:26px;word-break:break-word">{join_t}</div></div>
<div class="qr" style="left:1500px;top:690px;width:340px;height:340px;padding:16px"><img src="../img/{qr}"></div>""")


# ---------------- контент (из презентации «Диана») ----------------
S = []
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
        [("Telegram", "@ertad_community"), ("Instagram", "@ertad.community"), ("Встречи", "Тбилиси и Батуми")], "ertad_qr.jpg"))]
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
        [("Telegram", "@RealEstateDi"), ("Instagram", "@estate_hub_1"), ("Встречи", "Тбилиси и онлайн")], "estate_qr.jpg"))]
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
        [("Telegram", "@tbilisirunningclub"), ("Instagram", "@tbilisirunningclub"), ("Strava", "@tbilisirunningclub"), ("Чат", "@tbilisirunningclubtalks")], "trc_qr.jpg"))]
# 4. Sami Residence — зелёный (1 слайд)
A = "#A874FF"
S += [("sami", single(A, "Sami Residence", ["Адаптация в Грузии", "Культурное погружение", "Новые друзья"],
        [("Наша миссия", "Помогаем в адаптации в Грузии"),
         ("О чём сообщество", "Мы изучаем грузинский язык, культуру и историю. Объединяем людей через ивенты со смыслом")],
        "instagram.com/sami.residence.tbilisi", "sami_photo.jpg", "sami_qr.jpg", "S", "50% 40%", fit=True))]
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
        "isoul_qr.jpg", "Анкета на вступление"))]
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
        [("Telegram", "@martech_ai"), ("Instagram", "@alex.happy.longevity"), ("Встречи", "Tbilisi, Ibis Tbilisi Stadium")], "mai_qr.jpg"))]
# 7. Tbilisi Coffee Club — оранжевый (1 слайд)
A = "#A874FF"
S += [("coffee", single(A, "Tbilisi Coffee Club", ["Coffee", "Networking", "Community"],
        [("Наша миссия", "Помогать людям находить свой круг общения, друзей и единомышленников в Тбилиси."),
         ("О чём сообщество", "Объединяем любителей кофе и живого общения. Знакомимся за чашкой кофе, каждую неделю встречаемся в разных кофейнях Тбилиси, открываем новые места и проводим время вместе.")],
        "t.me/TbilisiCoffeeClub", "coffee_photo.jpg", "coffee_qr.jpg", "C"))]
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
        [("Telegram", "@mesto_games"), ("Бот", "@mesto123_bot"), ("Instagram", "@mesto.tbilisi"), ("Встречи", "Тбилиси, Вахтанга Бочоришвили 37А")], "mesto_qr.jpg"))]
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
        [("Telegram", "@mari_manjari"), ("Instagram", "@mir_vdvoem"), ("Встречи", "Тбилиси, Батуми и онлайн")], "blog_qr.jpg"))]
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

order = []
for i, (k, h) in enumerate(S, 1):
    fn = f"{i:02d}-{k}.html"; (OUT / fn).write_text(h); order.append(fn)
(OUT / "order.json").write_text(json.dumps(order))
print(len(order))
