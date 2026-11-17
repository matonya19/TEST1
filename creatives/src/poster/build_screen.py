"""Для лидеров: сцена с оранжевым экраном (фото-референс, очищено), наш текст на экране и на стене. Шрифт Onest."""
import pathlib
HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F'), ('cyrillic', 'U+0400-04FF')))
PX0, PX1, PY0, PY1 = 338, 742, 155, 790   # экран (видимая часть над головами)

CSS = FF + """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Onest',sans-serif;position:relative;background:%(bgc)s;color:#fff}
.abs{position:absolute}
.scene{position:absolute;left:0;top:%(oy)dpx;width:1080px;height:1350px;background:url(panel_clean.jpg) 0 0/1080px 1350px;
 -webkit-mask-image:linear-gradient(180deg,%(mtop)s,#000 6%%,#000 94%%,%(mbot)s)}
.ghost{position:absolute;left:-30px;right:-30px;font-weight:500;letter-spacing:-.05em;line-height:.86;color:rgba(255,235,220,.10);white-space:nowrap}
.screen{position:absolute;left:%(sx)dpx;top:%(sy)dpx;width:%(sw)dpx;height:%(sh)dpx;background:url(panel_clean.jpg) -%(sx)dpx -%(py0)dpx/1080px 1350px}
.head{font-weight:500;font-size:52px;line-height:1.02;letter-spacing:-.03em}
.meta{font-size:20px;font-weight:500;line-height:1.4;color:rgba(255,255,255,.92)}
.meta b{font-weight:800;font-size:26px;display:block;margin-bottom:6px;color:#fff}
"""


def build(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    oy = 285 if story else 0
    bgc = "#0d0604"
    sx, sy, sw, sh = PX0, PY0 + oy, PX1 - PX0, PY1 - PY0
    g = []
    lines = [("ведёшь", -40), ("сообщество?", 250), ("расскажи", 540)]
    if story:
        lines = [("ты", 0), ("ведёшь", 250), ("сообщество?", 530), ("расскажи", 810)]
    for t, y in lines:
        g.append(f'<div class="ghost" style="top:{y + (oy if not story else 0)}px;font-size:{260 if not story else 270}px;text-align:center">{t}</div>')
    logo = LOGO.replace('width="77"', 'width="104"').replace('height="38"', 'height="51"')
    body = f"""<div class="scene"></div>
{''.join(g)}
<div class="screen" style="--x:0"></div>
<div class="abs" style="left:{sx + 40}px;top:{sy + 56}px">{logo}</div>
<div class="abs head" style="left:{sx + 40}px;top:{sy + 300}px">Ведёшь<br>сообщество?<br>Расскажи<br>о нём.</div>
<div class="abs meta" style="left:{sx + 40}px;top:{sy + 545}px"><b>27 ноября · Тбилиси</b>Ginger Hotel · сбор 19:00<br>вход свободный</div>"""
    css = CSS % dict(H=H, bgc=bgc, oy=oy, sx=sx, sy=sy, sw=sw, sh=sh, py0=PY0,
                     mtop="transparent" if story else "#000", mbot="transparent" if story else "#000")
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"screen-{fmt}.html").write_text(build(fmt))
print("ok")
