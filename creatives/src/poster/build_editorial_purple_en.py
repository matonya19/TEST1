"""Редакционный стиль по референсам: A — огромные обрезанные буквы, B — синяя плашка с овалом."""
import pathlib

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
PCUT = (933, 1146, .403, .170, .1955)  # w, h, центр лица x/y в долях, ширина лица / высота
MCUT = (902, 1059, .395, .229, .326)

BASE = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:#141633}
.abs{position:absolute}
.person{position:absolute}
.person img{height:100%%;display:block}
"""


def place(cut, F, fx, fy, img, fade=None):
    h = F / cut[4]
    w = h * cut[0] / cut[1]
    left, top = fx - cut[2] * w, fy - cut[3] * h
    m = ""
    if fade:
        a = (fy + fade[0] - top) / h * 100
        b = (fy + fade[1] - top) / h * 100
        m = f"-webkit-mask-image:linear-gradient(180deg,#000 {a:.1f}%,transparent {b:.1f}%);"
    return f'<div class="person" style="left:{left:.0f}px;top:{top:.0f}px;height:{h:.0f}px;{m}"><img src="{img}"></div>'


A_CSS = """
body{background:#0B0812}
.bg{position:absolute;inset:0;background:url(group.src.jpg) center/cover;filter:grayscale(1) brightness(.55) contrast(1.05);opacity:.5}
.sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,8,18,.75),rgba(11,8,18,.2) 35%,rgba(11,8,18,.45) 60%,rgba(11,8,18,.92))}
.L{position:absolute;font-weight:900;color:#9B5CFF;line-height:.8;letter-spacing:-.04em}
.t{color:rgba(255,255,255,.72);font-weight:600;line-height:1.05;letter-spacing:-.01em;text-shadow:0 2px 14px rgba(0,0,0,.8)}
.tb{color:#fff;font-weight:800;line-height:.95;letter-spacing:-.02em;text-shadow:0 2px 14px rgba(0,0,0,.8)}
.title{position:absolute;left:0;right:0;text-align:center;font-weight:900;color:#9B5CFF;letter-spacing:-.05em;line-height:.8}
.logo svg{display:block}
.flow{position:absolute;left:72px;right:72px}
.fit{display:block;white-space:nowrap;font-weight:900;color:#A874FF;letter-spacing:-.05em;line-height:.86;text-align:center}
.dark{position:absolute;left:0;right:0;bottom:0;z-index:1}
.flow{z-index:3}
.logo svg path{fill:#fff}
"""


def poster_purple(fmt):
    # тёмная версия: оранжевые буквы, ч/б фон
    story = fmt == "9x16"
    H = 1920 if story else 1350
    F = 178 if story else 165
    fy = 600 if story else 370
    s = []
    s.append('<div class="bg"></div><div class="sh"></div>')
    # задние буквы
    if story:
        s.append('<div class="L" style="left:-110px;top:-60px;font-size:760px">F</div>')
        s.append('<div class="L" style="right:-170px;top:330px;font-size:760px">Y</div>')
    else:
        s.append('<div class="L" style="left:-90px;top:-70px;font-size:560px">F</div>')
        s.append('<div class="L" style="right:-140px;top:150px;font-size:560px">Y</div>')
    fade = (330, 520) if story else (300, 470)
    F = int(F * .88)
    s.append(place(MCUT, F, 190, fy, "max_cut.png", fade))
    s.append(place(PCUT, F, 890, fy, "polina_cut.png", fade))
    s.append(place((950, 1789, 0.4589, 0.1314, 0.1705), F, 540, fy + 20, "lasha_cut.png", fade).replace('class="person"', 'class="person" style="z-index:1"', 1) if False else place((950, 1789, 0.4589, 0.1314, 0.1705), F, 540, fy + 20, "lasha_cut.png", fade))
    # передние нижние буквы
    if story:
        s.append('<div class="L" style="z-index:2;left:-40px;top:1760px;font-size:760px">PE</div>')
    else:
        s.append('<div class="L" style="z-index:2;left:-30px;top:1290px;font-size:560px">PE</div>')
    # центр — один поток: заголовок (каждая строка во всю ширину), город, инфо
    ty = 900 if story else 600
    tl = (270 + 95) if story else 150
    s.append(f'<div class="abs t" style="left:0;right:0;top:{tl}px;text-align:center;font-size:{32 if story else 28}px">The Power of Communities — an evening<br>where Tbilisi communities meet in person</div>')
    s.append(f'<div class="abs t" style="left:28px;top:{ty - 34}px;font-size:22px">27.11</div>')
    cs = 88 if story else 72
    ds = 60 if story else 48
    s.append(f'<div class="dark" style="top:{ty - 320}px;background:linear-gradient(180deg,rgba(11,8,18,0),rgba(11,8,18,.35) 160px,rgba(11,8,18,.62) 320px,rgba(11,8,18,.72) 70%,rgba(11,8,18,.85))"></div>')
    s.append(f'''<div class="flow" style="top:{ty}px">
<span class="fit">FIND YOUR</span><span class="fit">PEOPLE</span>
<div style="text-align:center;font-weight:900;font-size:{cs}px;letter-spacing:-.04em;line-height:1;color:#fff;margin-top:14px">IN TBILISI</div>
<div class="tb" style="font-weight:500;letter-spacing:.02em;text-align:center;font-size:{22 if story else 20}px;margin-top:18px">SPEAKER: LASHA CHKHENKELI · TBC BANK — BANKING FOR EXPATS<br>HOSTS: POLINA · TEXTURA &nbsp;·&nbsp; MAXIM · CO.SPACE</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:26px"><div><div class="tb" style="font-size:{ds}px">27 NOVEMBER<br>FRIDAY</div><div class="t" style="font-size:{ds}px">7:00 PM</div></div>
<div style="text-align:right"><div class="tb" style="font-weight:500;line-height:1.1;font-size:{38 if story else 32}px">GINGER HOTEL<br>TBILISI</div><div style="display:inline-block;margin-top:{18 if story else 14}px;background:#A874FF;color:#0B0812;font-weight:800;border-radius:40px;padding:{16 if story else 12}px {30 if story else 24}px;font-size:{30 if story else 24}px">FREE ENTRY</div></div></div></div>
<script>document.fonts.ready.then(()=>{{const W=document.querySelector('.flow').clientWidth;document.querySelectorAll('.fit').forEach(e=>{{e.style.fontSize='100px';e.style.display='inline-block';const w=e.getBoundingClientRect().width;e.style.fontSize=(100*W*.8/w)+'px';e.style.display='block'}})}})</script>''')
    ly = 270 if story else 60
    s.append(f'<div class="abs logo" style="left:50%;transform:translateX(-50%);top:{ly}px">{LOGO.replace("width=\"77\"", "width=\"120\"").replace("height=\"38\"", "height=\"59\"")}</div>')
    css = BASE % dict(H=H) + A_CSS
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(s)}</body></html>'



for fmt in ("4x5", "9x16"):
    (HERE / f"edP-en-{fmt}.html").write_text(poster_purple(fmt))
print("ok")
