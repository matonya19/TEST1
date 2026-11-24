"""Афиша «Сообщество сильнее одиночества» — Батуми, синяя, по референсу (волнистый фон с зерном,
огромный полупрозрачный текст за людьми, герои по центру, крупный заголовок поверх)."""
import pathlib

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F'), ('cyrillic', 'U+0400-04FF')))

# лица: центр (x, y) в пикселях вырезки, ширина лица, размер вырезки
MAX = dict(img="max_portrait_cut.png", w=674, h=1237, cx=343, cy=178, fw=194)
POL = dict(img="polina_cut.png", w=933, h=1146, cx=376, cy=195, fw=224)


def person(p, F, fx, fy, fade_y, H):
    s = F / p["fw"]
    w, h = p["w"] * s, p["h"] * s
    left, top = fx - p["cx"] * s, fy - p["cy"] * s
    a = (fade_y - top) / h * 100
    b = (fade_y + 230 - top) / h * 100
    return (f'<img src="{p["img"]}" style="position:absolute;left:{left:.0f}px;top:{top:.0f}px;width:{w:.0f}px;'
            f'-webkit-mask-image:linear-gradient(180deg,#000 {a:.1f}%,transparent {b:.1f}%);'
            f'filter:drop-shadow(0 30px 60px rgba(0,10,40,.55));z-index:3">')


def bg(W, H):
    return f'''<svg class="abs" style="left:0;top:0;z-index:0" width="{W}" height="{H}">
<defs>
 <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B1F63"/><stop offset=".55" stop-color="#1B4FD1"/><stop offset="1" stop-color="#0A2A8A"/></linearGradient>
 <filter id="wave" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.0016 0.004" numOctaves="2" seed="7"/>
  <feDisplacementMap in="SourceGraphic" scale="420"/><feGaussianBlur stdDeviation="12"/></filter>
 <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#g)"/>
<g filter="url(#wave)" opacity=".9">
 <ellipse cx="{W*.15:.0f}" cy="{H*.18:.0f}" rx="{W*.6:.0f}" ry="{H*.05:.0f}" fill="#58A8FF" transform="rotate(-18 {W*.15:.0f} {H*.18:.0f})"/>
 <ellipse cx="{W*.85:.0f}" cy="{H*.42:.0f}" rx="{W*.55:.0f}" ry="{H*.06:.0f}" fill="#3C8BFF" transform="rotate(22 {W*.85:.0f} {H*.42:.0f})"/>
 <ellipse cx="{W*.25:.0f}" cy="{H*.7:.0f}" rx="{W*.7:.0f}" ry="{H*.05:.0f}" fill="#6CC2FF" transform="rotate(-12 {W*.25:.0f} {H*.7:.0f})"/>
 <ellipse cx="{W*.9:.0f}" cy="{H*.9:.0f}" rx="{W*.5:.0f}" ry="{H*.05:.0f}" fill="#2A6BEA" transform="rotate(15 {W*.9:.0f} {H*.9:.0f})"/>
 <ellipse cx="{W*.5:.0f}" cy="{H*.05:.0f}" rx="{W*.5:.0f}" ry="{H*.04:.0f}" fill="#061547" transform="rotate(8 {W*.5:.0f} {H*.05:.0f})"/>
 <ellipse cx="{W*.55:.0f}" cy="{H*.58:.0f}" rx="{W*.45:.0f}" ry="{H*.035:.0f}" fill="#081A55" transform="rotate(-25 {W*.55:.0f} {H*.58:.0f})"/>
</g>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".16"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</svg>'''


def build(fmt):
    story = fmt == "9x16"
    W, H = 1080, (1920 if story else 1350)
    # вертикальная раскладка
    if story:
        top, ghost_y, gs, fy, F, fade, title_y, foot_y, date_y = 150, 300, 250, 640, 178, 1330, 1235, 1730, 470
    else:
        top, ghost_y, gs, fy, F, fade, title_y, foot_y, date_y = 50, 140, 220, 410, 128, 830, 760, 1225, 260
    logo = LOGO.replace('width="77"', 'width="130"').replace('height="38"', 'height="64"')
    css = FF + f"""*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#0B1F63}}
body{{font-family:'Onest',sans-serif;color:#fff;position:relative}}
.abs{{position:absolute}}
.ghost{{position:absolute;left:-20px;right:-20px;text-align:center;font-weight:900;letter-spacing:-.04em;line-height:.82;color:rgba(120,190,255,.32);z-index:1}}
.title{{position:absolute;left:30px;right:30px;text-align:center;z-index:5;text-shadow:0 6px 30px rgba(0,15,60,.45)}}
.kick{{font-size:{46 if story else 40}px;font-weight:800;letter-spacing:.02em}}
.dash{{width:56px;height:6px;background:#fff;margin:{18 if story else 14}px auto}}
.big{{font-size:{118 if story else 102}px;font-weight:900;letter-spacing:-.03em;line-height:.9;text-transform:uppercase}}
.sub{{font-size:{26 if story else 23}px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;margin-top:{20 if story else 16}px}}
.date{{position:absolute;left:56px;font-size:{108 if story else 92}px;font-weight:800;line-height:.92;letter-spacing:-.02em;z-index:5}}
.pill{{position:absolute;right:56px;background:#5AB2FF;color:#061547;border-radius:60px;padding:16px 30px;font-size:{25 if story else 22}px;font-weight:800;text-align:center;line-height:1.1;text-transform:uppercase;z-index:5}}
.foot{{position:absolute;left:56px;right:56px;display:flex;justify-content:space-between;align-items:center;font-size:{30 if story else 26}px;font-weight:600;line-height:1.15;text-transform:uppercase;z-index:5}}
"""
    body = f"""{bg(W, H)}
<div class="abs" style="left:0;right:0;top:{top}px;text-align:center;z-index:5">{logo}</div>
<div class="ghost" style="top:{ghost_y}px;font-size:{gs}px">СИЛА<br>БАТУМИ</div>
{person(MAX, F, W * .34, fy, fade, H)}{person(POL, F, W * .66, fy, fade, H)}
<div class="abs" style="left:0;right:0;top:{fade - 120}px;height:{H - fade + 120}px;background:linear-gradient(180deg,rgba(11,31,99,0),rgba(11,31,99,.55) 40%,rgba(8,24,80,.85));z-index:4"></div>
<div class="date" style="top:{date_y}px">30.11<br>ПН</div>
<div class="pill" style="top:{date_y + 30}px">вход<br>свободный</div>
<div class="title" style="top:{title_y}px"><div class="kick">СИЛА СООБЩЕСТВ</div><div class="dash"></div>
<div class="big">Сообщество<br>сильнее<br>одиночества</div>
<div class="sub">Полина · TEXTURA &nbsp;/&nbsp; Максим · Co.Space</div></div>
<div class="foot" style="top:{foot_y}px"><div>Вечер<br>в Батуми</div><div style="text-align:center;font-size:.8em">Регистрация —<br>ссылка в профиле</div><div style="text-align:right">@co.batumi</div></div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"blue-{fmt}.html").write_text(build(fmt))
print("ok")
