"""Афиша лидера сообщества: Константин Кочура, Tbilisi Running Club — вечер «Сила сообществ» 27.11 (RU).
Стиль — как у афиши спикера TBC (тёмный фон, огромные синие буквы)."""
import pathlib

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()
FF = ''.join(f"@font-face{{font-family:'Onest';src:url(fonts/onest-{sub}-{w}-normal.woff2) format('woff2');font-weight:{w};unicode-range:{rng}}}"
             for w in (400, 500, 600, 700, 800, 900) for sub, rng in (('latin', 'U+0000-00FF,U+2000-206F'), ('cyrillic', 'U+0400-04FF')))
BLUE, DARK = "#4F75FF", "#0B0812"
CUT_W, CUT_H, FACE_CX, FACE_CY, FACE_W = 1180, 2326, 527, 843, 962


def build(fmt):
    story = fmt == "9x16"
    H = 1920 if story else 1350
    o = 270 if story else 0
    F = 520 if story else 480                      # ширина лица на афише
    s = F / FACE_W
    w, h = CUT_W * s, CUT_H * s
    fx, fy = (760, 720) if story else (760, 470)  # центр лица
    left, top = fx - FACE_CX * s, fy - FACE_CY * s
    cut_bottom = fy + (460 if story else 390)
    mask_a = (cut_bottom - 220 - top) / h * 100
    mask_b = (cut_bottom - top) / h * 100
    hs = 104 if story else 92
    css = FF + f"""*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:{H}px;overflow:hidden}}
body{{font-family:'Onest',sans-serif;color:#fff;position:relative;background:{DARK}}}
.abs{{position:absolute}}
.L{{position:absolute;font-weight:900;color:{BLUE};line-height:.8;letter-spacing:-.05em}}
.kick{{font-size:{24 if story else 22}px;font-weight:700;letter-spacing:.16em;text-transform:uppercase}}
"""
    body = f"""
<div class="L" style="left:-70px;top:{o + (20 if story else 90)}px;font-size:{640 if story else 540}px">R</div>
<div class="L" style="right:-60px;top:{o + (560 if story else 470)}px;font-size:{640 if story else 540}px;opacity:.9">C</div>
<img src="kostya_cut.png" style="position:absolute;left:{left:.0f}px;top:{top:.0f}px;width:{w:.0f}px;
 -webkit-mask-image:linear-gradient(180deg,#000 {mask_a:.1f}%,transparent {mask_b:.1f}%)">
<div class="abs" style="left:0;right:0;top:{o + (-170 if story else 40)}px;text-align:center">{LOGO.replace('width="77"', 'width="110"').replace('height="38"', 'height="54"')}
<div class="kick" style="margin-top:14px;opacity:.75">Сила сообществ · Тбилиси</div></div>
<div class="abs" style="left:60px;top:{fy - (250 if story else 200)}px;width:{230 if story else 200}px;height:{230 if story else 200}px;border-radius:50%;background:#fff;padding:8px;box-shadow:0 20px 40px rgba(0,0,0,.45)">
<img src="trc_logo.png" style="width:100%;height:100%;display:block"></div>
<div class="abs" style="left:60px;top:{fy + (40 if story else 40)}px">
<div style="background:#fff;color:{DARK};padding:16px 24px 14px;border-radius:18px;box-shadow:0 20px 40px rgba(0,0,0,.4)">
<div style="font-size:{40 if story else 34}px;font-weight:800;line-height:1.05">Константин Кочура</div>
<div style="font-size:{25 if story else 22}px;font-weight:600;opacity:.7;margin-top:4px">капитан Tbilisi Running Club</div></div>
<div style="display:inline-block;margin:-10px 0 0 18px;background:{BLUE};padding:8px 18px;border-radius:10px;font-size:{21 if story else 19}px;font-weight:800;letter-spacing:.08em;position:relative">ЛИДЕР СООБЩЕСТВА</div></div>
<div class="abs" style="left:60px;right:60px;top:{cut_bottom - (40 if story else 50)}px;font-weight:900;text-transform:uppercase;letter-spacing:-.04em;line-height:.9;font-size:{hs}px">
<span style="color:{BLUE}">Как убежать</span><br>от одиночества</div>
<div class="abs" style="left:60px;right:60px;top:{cut_bottom - (40 if story else 50) + hs * 1.8 + 24:.0f}px;font-size:{29 if story else 24}px;line-height:1.35;color:rgba(255,255,255,.8)">
Начал бегать, чтобы убежать от экспатской депрессии. Бегать одному надоело — так появился клуб.</div>
<div class="abs" style="left:60px;right:60px;bottom:{270 if story else 56}px;display:flex;justify-content:space-between;align-items:flex-end">
<div><div style="font-size:{54 if story else 48}px;font-weight:800;line-height:1">ПТ, 27 НОЯБРЯ</div>
<div style="font-size:{54 if story else 48}px;font-weight:500;line-height:1.05;opacity:.75">19:00</div></div>
<div style="text-align:right;font-size:{32 if story else 28}px;font-weight:700;line-height:1.2">GINGER HOTEL<br>ТБИЛИСИ<br>
<div style="display:inline-block;margin-top:14px;background:{BLUE};border-radius:40px;padding:12px 24px;font-size:{26 if story else 22}px;font-weight:800">ВХОД СВОБОДНЫЙ</div></div></div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


for fmt in ("4x5", "9x16"):
    (HERE / f"trc-{fmt}.html").write_text(build(fmt))
print("ok")
