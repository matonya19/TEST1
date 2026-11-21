"""Текстовые карточки для ролика (1080x1920), шрифт Onest, наши цвета."""
import pathlib
HERE = pathlib.Path(__file__).parent
OUT = HERE / "cards"; OUT.mkdir(exist_ok=True)
P = HERE.parent / "poster"
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(../poster/fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (500, 700, 800) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F'), ('cyrillic', 'U+0400-04FF')))
DARK, LILAC = "#0B0812", "#B79BFF"
BASE = FF + "*{margin:0;padding:0}html,body{width:1080px;height:1920px;overflow:hidden;font-family:'Onest',sans-serif}"

def card(name, word, bg, fg, photo=None):
    bgcss = f"background:{bg}"
    if photo:
        bgcss = f"background:linear-gradient(rgba(11,8,18,.35),rgba(11,8,18,.35)),url(../../poster/{photo}) {photo_pos.get(photo,'50% 50%')}/cover"
    html = (f"<!doctype html><html><head><meta charset=utf-8><style>{BASE}body{{{bgcss};display:flex;align-items:center;justify-content:center}}"
            f".w{{color:{fg};font-size:64px;font-weight:700;letter-spacing:.02em;text-transform:uppercase}}</style></head>"
            f"<body><div class=w>{word}</div></body></html>")
    (OUT / f"{name}.html").write_text(html)

photo_pos = {"audience.jpg": "40% 50%"}
words = ["27 ноября", "в Тбилиси", "соберутся", "сообщества", "всего", "города", "приходи"]
for i, w in enumerate(words):
    dark = i % 2 == 0
    card(f"w{i}", w, DARK if dark else LILAC, "#fff" if dark else DARK)
card("w_photo", "приходи", None, "#fff", photo="audience.jpg")

logo = LOGO.replace('width="77"', 'width="200"').replace('height="38"', 'height="99"')
end = (f"<!doctype html><html><head><meta charset=utf-8><style>{BASE}body{{background:{LILAC};color:{DARK};position:relative}}"
       f".l svg path{{fill:{DARK}}}</style></head><body>"
       f"<div class=l style='position:absolute;left:0;right:0;top:330px;text-align:center'>{logo.replace('<svg','<svg style=\"display:inline\"')}</div>"
       f"<div style='position:absolute;left:90px;right:90px;top:640px;text-align:center'>"
       f"<div style='font-size:34px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;opacity:.7'>Сила сообществ</div>"
       f"<div style='font-size:118px;font-weight:800;letter-spacing:-.04em;line-height:.95;margin-top:40px'>Найди<br>своих</div>"
       f"<div style='font-size:52px;font-weight:700;margin-top:80px'>27 ноября · Тбилиси</div>"
       f"<div style='font-size:40px;font-weight:500;margin-top:18px'>Ginger Hotel · сбор 19:00</div>"
       f"<div style='display:inline-block;margin-top:70px;background:{DARK};color:#fff;border-radius:60px;padding:30px 54px;font-size:40px;font-weight:700'>Вход свободный, по регистрации</div>"
       f"<div style='font-size:34px;font-weight:600;margin-top:40px;opacity:.75'>ссылка в профиле @co.tbilisi</div></div></body></html>")
(OUT / "end.html").write_text(end)
print("ok")
