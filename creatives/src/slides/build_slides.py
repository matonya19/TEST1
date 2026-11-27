"""Шаблоны слайдов для сообществ (16:9, 1920x1080) в стиле афиш: тёмный фон, фиолетовый акцент,
огромные буквы, Onest, рамки со скруглением. Плейсхолдеры в [квадратных скобках] — как в исходных шаблонах."""
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE / "html"; OUT.mkdir(exist_ok=True)
LOGO = (HERE.parent / "co-logo-white.svg").read_text().replace('width="77"', 'width="96"').replace('height="38"', 'height="47"')
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(../../poster/fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F,U+2190-21FF'), ('cyrillic', 'U+0400-04FF')))
P, INK, BG = "#A874FF", "#120A22", "#0B0812"

CSS = FF + f"""*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden}}
body{{font-family:'Onest',sans-serif;background:{BG};color:#fff;position:relative}}
.a{{position:absolute}}
.glow{{position:absolute;border-radius:50%;filter:blur(110px);background:rgba(168,116,255,.25)}}
.giant{{position:absolute;font-weight:900;color:{P};line-height:.78;letter-spacing:-.05em;opacity:.95}}
.brand{{position:absolute;left:80px;top:64px;display:flex;align-items:center;gap:14px;font-size:34px;font-weight:500;z-index:5}}
.frame{{position:absolute;border-radius:48px;overflow:hidden;background:#1C1530;border:2px dashed rgba(168,116,255,.5);
 display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.45);font-size:28px;font-weight:600;z-index:3}}
.frame.photo{{border:none;background-size:cover;background-position:center}}
.kick{{font-size:22px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{P}}}
.h{{font-weight:900;letter-spacing:-.04em;line-height:.92;text-transform:uppercase}}
.lbl{{font-size:26px;font-weight:800;color:{P};margin-bottom:10px}}
.txt{{font-size:28px;line-height:1.35;color:rgba(255,255,255,.82)}}
.ph{{color:rgba(255,255,255,.45)}}
.card{{position:absolute;background:#17121F;border:1.5px solid rgba(168,116,255,.3);border-radius:40px;padding:44px 48px;z-index:4}}
.pill{{display:inline-block;border-radius:60px;padding:14px 30px;font-size:26px;font-weight:700;margin:0 12px 14px 0}}
.pill.f{{background:{P};color:{INK}}}
.pill.o{{border:2px solid rgba(168,116,255,.6);background:rgba(168,116,255,.12)}}
.qr{{position:absolute;background:#fff;border-radius:32px;display:flex;align-items:center;justify-content:center;color:{INK};font-size:24px;font-weight:700;z-index:4;overflow:hidden}}
.row{{display:flex;gap:24px;font-size:28px;line-height:1.6}}
.row b{{width:170px;color:{P};font-weight:700}}
"""


def page(body):
    glow = ('<div class="glow" style="left:1250px;top:-200px;width:900px;height:700px"></div>'
            '<div class="glow" style="left:-300px;top:600px;width:900px;height:700px;opacity:.6"></div>')
    brand = f'<div class="brand">{LOGO}<span>Tbilisi</span></div>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{glow}{brand}{body}</body></html>'


def founder():
    return page(f"""
<div class="giant" style="left:-60px;top:170px;font-size:900px">C</div>
<div class="frame" style="left:150px;top:200px;width:680px;height:780px">[Портрет основателя]</div>
<div class="a" style="left:900px;top:190px;z-index:5"><div class="kick">Основатель сообщества</div>
<div class="h" style="font-size:132px;margin-top:26px">[Имя]<br><span style="color:{P}">[Фамилия]</span></div>
<div style="margin-top:34px"><span class="pill f">[Название сообщества]</span></div></div>
<div class="card" style="left:900px;top:640px;width:900px">
<div class="lbl">Кто вы</div><div class="txt ph">[Чем вы занимаетесь?]</div>
<div class="lbl" style="margin-top:28px">Зачем вы собрали сообщество</div><div class="txt ph">[Что подтолкнуло вас объединить людей?]</div></div>""")


def about():
    return page(f"""
<div class="giant" style="right:-80px;top:120px;font-size:900px">O</div>
<div class="frame" style="left:80px;top:170px;width:960px;height:620px">[Фото встречи или участников]</div>
<div class="a" style="left:80px;top:830px;z-index:5"><div class="kick">О сообществе</div>
<div class="h" style="font-size:96px;margin-top:18px">[Название сообщества]</div></div>
<div class="card" style="left:1120px;top:170px;width:720px">
<div class="lbl">Наша миссия</div><div class="txt ph">[Какое изменение вы хотите создать?]</div>
<div class="lbl" style="margin-top:34px">Что делаем вместе</div><div class="txt ph">[Укажите 1–2 формата: встречи, события или совместные проекты.]</div>
<div class="lbl" style="margin-top:34px">Для кого мы</div><div class="txt ph">[Кому будет интересно стать частью сообщества?]</div></div>""")


def join():
    return page(f"""
<div class="giant" style="left:-40px;bottom:-230px;font-size:620px;opacity:.28">JOIN</div>
<div class="a" style="left:80px;top:180px;z-index:5"><div class="kick">[Название сообщества]</div>
<div class="h" style="font-size:118px;margin-top:22px">Как<br><span style="color:{P}">присоединиться</span></div></div>
<div class="card" style="left:80px;top:560px;width:1040px">
<div class="lbl">Первый шаг</div><div class="txt ph">[Напишите в чат, заполните анкету или запишитесь на встречу.]</div>
<div class="lbl" style="margin-top:30px">Где нас найти</div>
<div class="row"><b>Telegram</b><span class="ph">[@имя или короткая ссылка]</span></div>
<div class="row"><b>Instagram</b><span class="ph">[@имя]</span></div>
<div class="row"><b>Встречи</b><span class="ph">[город и место или онлайн]</span></div></div>
<div class="qr" style="left:1300px;top:340px;width:520px;height:520px">[Вставьте QR-код]</div>
<div class="a kick" style="left:1300px;top:890px;width:520px;text-align:center;color:rgba(255,255,255,.6)">Наведи камеру — и ты с нами</div>""")


def single(name, tags, mission, about_t, join_t, photo=None, qr=None, ph=True):
    cls = "ph" if ph else ""
    fr = (f'<div class="frame photo" style="left:80px;top:170px;width:820px;height:640px;background-image:url(../{photo})"></div>' if photo
          else '<div class="frame" style="left:80px;top:170px;width:820px;height:640px">[Фото сообщества]</div>')
    q = (f'<div class="qr" style="left:1490px;top:700px;width:330px;height:330px;padding:18px"><img src="../{qr}" style="width:100%;height:100%;object-fit:contain"></div>' if qr
         else '<div class="qr" style="left:1490px;top:700px;width:330px;height:330px">[QR-код]</div>')
    fs = 72 if len(name) < 22 else 56
    pills = "".join(f'<span class="pill {"f" if i == 0 else "o"}" style="font-size:22px;padding:12px 24px;margin-right:10px">{t}</span>' for i, t in enumerate(tags))
    return page(f"""
<div class="giant" style="right:-60px;top:60px;font-size:760px;opacity:.9">C</div>
{fr}
<div class="a" style="left:80px;top:840px;width:900px;z-index:5"><div class="h" style="font-size:{fs}px">{name}</div>
<div style="margin-top:20px;white-space:nowrap">{pills}</div></div>
<div class="card" style="left:980px;top:170px;width:860px">
<div class="lbl">Наша миссия</div><div class="txt {cls}">{mission}</div>
<div class="lbl" style="margin-top:30px">О чём сообщество</div><div class="txt {cls}">{about_t}</div></div>
<div class="a" style="left:980px;top:720px;width:470px;z-index:5"><span class="pill f" style="background:#fff">Как вступить</span>
<div class="txt {cls}" style="margin-top:10px">{join_t}</div></div>
{q}""")


SLIDES = {
    "talk-1-founder": founder(),
    "talk-2-about": about(),
    "talk-3-join": join(),
    "nospk-1-template": single("[Название сообщества]", ["[Ключевое слово]", "[Ключевое слово]", "[Ключевое слово]"],
                               "[Ради чего мы создали сообщество?]", "[Кого мы объединяем и что делаем вместе?]",
                               "[Укажите первый шаг и короткую ссылку или @имя]"),
    "nospk-2-example": single("Tbilisi Coffee Club", ["Coffee", "Networking", "Community"],
                              "Помогать людям находить свой круг общения, друзей и единомышленников в Тбилиси.",
                              "Объединяем любителей кофе и живого общения. Знакомимся за чашкой кофе, каждую неделю встречаемся в разных кофейнях Тбилиси, открываем новые места и проводим время вместе.",
                              "t.me/TbilisiCoffeeClub", photo="coffee.png", qr="qr_coffee.png", ph=False),
}
for k, v in SLIDES.items():
    (OUT / f"{k}.html").write_text(v)
print("ok")
