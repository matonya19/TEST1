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
    body = f"""<div class="abs" style="inset:0;background:url(conf.jpg) 50% 40%/auto {H}px;filter:grayscale(1) brightness(.55);opacity:.55"></div>
<div class="abs" style="inset:0;background:linear-gradient(180deg,rgba(11,8,18,.75),rgba(11,8,18,.25) 30%,rgba(11,8,18,.35) 55%,rgba(11,8,18,.9) 75%)"></div>
{letters}
{place(CUT, F, 540, fy)}
<div class="abs" style="left:0;right:0;top:{fade - 420}px;bottom:0;background:linear-gradient(180deg,rgba(11,8,18,0),rgba(11,8,18,.85) 300px,{DARK} 420px)"></div>
<div class="abs" style="left:0;right:0;top:{o + (40 if not story else -170)}px;text-align:center">{LOGO.replace('width="77"', 'width="110"').replace('height="38"', 'height="54"')}
<div class="kick" style="margin-top:14px;opacity:.75">The Power of Communities · Tbilisi</div></div>
<div class="abs" style="left:60px;top:{fy + (230 if story else 250)}px"><div style="background:#fff;color:{DARK};padding:16px 24px 14px;border-radius:18px;box-shadow:0 20px 40px rgba(0,0,0,.4)">
<div style="font-size:{40 if story else 34}px;font-weight:800;line-height:1.05">Lasha Chkhenkeli</div>
<div style="font-size:{26 if story else 23}px;font-weight:600;opacity:.7;margin-top:4px">TBC Bank</div></div>
<div style="display:inline-block;margin:-10px 0 0 18px;background:{BLUE};padding:8px 18px;border-radius:10px;font-size:{22 if story else 20}px;font-weight:800;letter-spacing:.08em;position:relative">SPEAKER</div></div>
<div class="t" style="top:{fade - (120 if story else 110)}px;font-size:{108 if story else 86}px">Banking<br>opportunities<br><span style="color:#fff">for expats</span><br><span style="color:#fff;font-size:.85em;letter-spacing:-.03em">in Tbilisi</span></div>
<div class="abs" style="left:60px;right:60px;bottom:{(270 if story else 60)}px">{info_block(story)}</div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


def poster_b(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    o = 270 if story else 0
    F, fy = (175, 640) if story else (150, 420)
    css = BASE % dict(H=H, bgc="#0B1F63", k=24 if story else 22) + """
.ghost{position:absolute;left:-30px;right:-30px;text-align:center;font-weight:900;letter-spacing:-.045em;line-height:.8;color:rgba(130,195,255,.28);text-transform:uppercase}
"""
    gs = 250 if story else 215
    body = f"""{blue_bg(1080, H)}
<div class="ghost" style="top:{o + (40 if story else 175)}px;font-size:{gs}px">Expats<br>Banking</div>
<div class="abs" style="left:0;right:0;top:{o + (-180 if story else 50)}px;text-align:center;z-index:5">{LOGO.replace('width="77"', 'width="110"').replace('height="38"', 'height="54"')}
<div class="kick" style="margin-top:14px">The Power of Communities · Tbilisi</div></div>
<div style="position:absolute;inset:0;z-index:3;-webkit-mask-image:linear-gradient(180deg,#000 {58 if story else 60}%,transparent {72 if story else 76}%)">{place(CUT, F, 540, fy, "filter:drop-shadow(0 30px 50px rgba(0,10,40,.5))")}</div>
<div class="abs" style="left:40px;right:40px;top:{fy + (360 if story else 290)}px;text-align:center;z-index:6;font-weight:900;text-transform:uppercase;letter-spacing:-.035em;line-height:.9;font-size:{104 if story else 90}px;text-shadow:0 6px 30px rgba(0,15,60,.45)">Banking<br>opportunities<br><span style="color:#9CCBFF">for expats</span><br><span style="font-size:.85em;letter-spacing:-.03em">in Tbilisi</span></div>
<div class="abs" style="left:0;right:0;top:{fy + (800 if story else 690)}px;text-align:center;z-index:6;font-size:{28 if story else 24}px;font-weight:700;letter-spacing:.06em;text-transform:uppercase">Speaker: Lasha Chkhenkeli · TBC Bank</div>
<div class="abs" style="left:56px;right:56px;bottom:{(270 if story else 56)}px;z-index:6">{info_block(story, accent="#9CCBFF")}</div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"spkA-{fmt}.html").write_text(poster_a(fmt))
    (HERE / f"spkB-{fmt}.html").write_text(poster_b(fmt))
print("ok")
