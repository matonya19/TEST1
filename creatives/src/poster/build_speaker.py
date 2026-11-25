"""Афиши спикера (EN): Lasha Chkhenkeli, TBC Bank — «Banking opportunities for expats».
A — редакционный тёмный стиль с огромными синими буквами; B — «стикер» с белой обводкой на синем фоне."""
import pathlib
from build_blue import bg as blue_bg

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F'), ('cyrillic', 'U+0400-04FF')))
BLUE, DARK = "#4F75FF", "#0B0812"
CUT = dict(img="lasha_cut.png", fw=305, cx=436, cy=235, w=950)       # лицо в вырезке
STK = dict(img="lasha_sticker.png", fw=305, cx=476, cy=275, w=1030)   # то же + 40px поля обводки

BASE = FF + """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Onest',sans-serif;color:#fff;position:relative;background:%(bgc)s}
.abs{position:absolute}
.kick{font-size:%(k)dpx;font-weight:700;letter-spacing:.16em;text-transform:uppercase}
"""


def place(p, F, fx, fy, extra=""):
    s = F / p["fw"]
    return (f'<img src="{p["img"]}" style="position:absolute;left:{fx - p["cx"] * s:.0f}px;top:{fy - p["cy"] * s:.0f}px;'
            f'width:{p["w"] * s:.0f}px;{extra}">')


def info_block(story, color="#fff", accent=BLUE):
    fs = 34 if story else 30
    return (f'<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:30px">'
            f'<div><div style="font-size:{fs + 22}px;font-weight:800;line-height:1;letter-spacing:-.01em">FRI, 27 NOV</div>'
            f'<div style="font-size:{fs + 22}px;font-weight:500;line-height:1.05;opacity:.75">7:00 PM</div></div>'
            f'<div style="text-align:right;font-size:{fs}px;font-weight:700;line-height:1.2">GINGER HOTEL<br>TBILISI<br>'
            f'<div style="display:inline-block;margin-top:14px;background:{accent};color:{"#fff" if accent == BLUE else DARK};border-radius:40px;'
            f'padding:12px 24px;font-size:{fs - 6}px;font-weight:800">FREE ENTRY · REGISTRATION</div></div></div>')


def poster_a(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    o = 270 if story else 0        # верхняя безопасная зона сторис
    F, fy = (190, 560) if story else (168, 360)
    css = BASE % dict(H=H, bgc=DARK, k=24 if story else 22) + f"""
.L{{position:absolute;font-weight:900;color:{BLUE};line-height:.8;letter-spacing:-.05em}}
.t{{position:absolute;left:60px;right:60px;font-weight:900;color:{BLUE};text-transform:uppercase;letter-spacing:-.04em;line-height:.88}}
"""
    letters = (f'<div class="L" style="left:-60px;top:{o + (40 if story else 100)}px;font-size:{620 if story else 520}px">B</div>'
               f'<div class="L" style="right:-90px;top:{o + (420 if story else 330)}px;font-size:{620 if story else 520}px">$</div>')
    fade = fy + (600 if story else 560)
    body = f"""{letters}
{place(CUT, F, 540, fy)}
<div class="abs" style="left:0;right:0;top:{fade - 420}px;bottom:0;background:linear-gradient(180deg,rgba(11,8,18,0),rgba(11,8,18,.85) 300px,{DARK} 420px)"></div>
<div class="abs" style="left:0;right:0;top:{o + (40 if not story else -170)}px;text-align:center">{LOGO.replace('width="77"', 'width="110"').replace('height="38"', 'height="54"')}
<div class="kick" style="margin-top:14px;opacity:.75">The Power of Communities · Tbilisi</div></div>
<div class="abs" style="left:60px;top:{fy + (300 if story else 250)}px"><div style="background:#fff;color:{DARK};padding:16px 24px 14px;border-radius:18px;box-shadow:0 20px 40px rgba(0,0,0,.4)">
<div style="font-size:{40 if story else 34}px;font-weight:800;line-height:1.05">Lasha Chkhenkeli</div>
<div style="font-size:{26 if story else 23}px;font-weight:600;opacity:.7;margin-top:4px">TBC Bank</div></div>
<div style="display:inline-block;margin:-10px 0 0 18px;background:{BLUE};padding:8px 18px;border-radius:10px;font-size:{22 if story else 20}px;font-weight:800;letter-spacing:.08em;position:relative">SPEAKER</div></div>
<div class="t" style="top:{fade - (40 if story else 30)}px;font-size:{112 if story else 98}px">Banking<br>opportunities<br><span style="color:#fff">for expats</span></div>
<div class="abs" style="left:60px;right:60px;bottom:{(270 if story else 60)}px">{info_block(story)}</div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


def poster_b(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    o = 270 if story else 0
    F, fy = (165, 760) if story else (140, 520)
    css = BASE % dict(H=H, bgc="#0B1F63", k=24 if story else 22)
    body = f"""{blue_bg(1080, H)}
<div class="abs" style="left:0;right:0;top:{o + (-180 if story else 50)}px;text-align:center;z-index:5">{LOGO.replace('width="77"', 'width="110"').replace('height="38"', 'height="54"')}
<div class="kick" style="margin-top:14px">The Power of Communities · Tbilisi</div></div>
<div class="abs" style="left:50px;right:50px;top:{o + (-30 if story else 170)}px;text-align:center;z-index:5;font-weight:900;text-transform:uppercase;letter-spacing:-.035em;line-height:.9;font-size:{96 if story else 82}px;text-shadow:0 6px 30px rgba(0,15,60,.4)">Banking opportunities<br><span style="color:#9CCBFF">for expats</span></div>
<div style="position:absolute;inset:0;z-index:3;-webkit-mask-image:linear-gradient(180deg,#000 {66 if story else 82}%,transparent {75 if story else 93}%)">{place(STK, F, 540, fy, "filter:drop-shadow(0 30px 50px rgba(0,10,40,.5))")}</div>
<div class="abs" style="left:0;right:0;top:{fy + (330 if story else 280)}px;text-align:center;z-index:6">
<div style="display:inline-block;position:relative;background:#fff;color:{DARK};padding:22px 44px 26px;border-radius:22px;box-shadow:0 20px 50px rgba(0,10,40,.45)">
<div style="font-size:{62 if story else 54}px;font-weight:900;letter-spacing:-.02em;line-height:1">Lasha Chkhenkeli</div>
<div style="font-size:{44 if story else 38}px;font-weight:800;line-height:1.1;margin-top:6px">TBC Bank</div>
<div style="position:absolute;right:-22px;bottom:-26px;background:{BLUE};color:#fff;padding:8px 18px;border-radius:10px;font-size:{26 if story else 22}px;font-weight:800;transform:rotate(-4deg)">Speaker</div></div></div>
<div class="abs" style="left:56px;right:56px;bottom:{(270 if story else 56)}px;z-index:6">{info_block(story, accent="#9CCBFF")}</div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"spkA-{fmt}.html").write_text(poster_a(fmt))
    (HERE / f"spkB-{fmt}.html").write_text(poster_b(fmt))
print("ok")
