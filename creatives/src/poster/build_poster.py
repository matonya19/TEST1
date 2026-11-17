"""Афиша «ИИ ускоряет всё» — Тбилиси, 27.11. python3 build_poster.py && node ../render.js-подобный рендер ниже."""
import pathlib

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent / "co-logo-white.svg").read_text()

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:%(H)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;color:#fff;position:relative;
 background:radial-gradient(800px 600px at 100%% 0%%, rgba(74,108,247,.55), transparent 60%%),
            radial-gradient(700px 700px at 0%% 100%%, rgba(236,72,153,.18), transparent 60%%), #1A1A2E}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(165,180,252,.07) 1px,transparent 1px),
 linear-gradient(90deg,rgba(165,180,252,.07) 1px,transparent 1px);background-size:40px 40px;
 -webkit-mask-image:linear-gradient(180deg,#000 0%%,transparent 55%%)}
.logo{position:absolute;left:72px;top:%(top)dpx}.logo svg{width:112px;height:auto;display:block}
.pill{position:absolute;right:72px;top:%(pt)dpx;border:2px solid rgba(255,255,255,.55);border-radius:40px;padding:12px 26px;font-size:30px;font-weight:500}
.mono{position:absolute;left:72px;top:%(mono)dpx;font-family:'JetBrains Mono',monospace;font-size:40px;color:#A5B4FC;letter-spacing:-.5px}
.mono b{display:inline-block;width:22px;height:44px;background:#A5B4FC;vertical-align:-8px;margin-left:6px}
.mono s{text-decoration:none;color:#6B75B8}
h1{position:absolute;left:72px;right:60px;top:%(h1)dpx;font-size:%(h1s)dpx;line-height:1;font-weight:800;letter-spacing:-3px}
h1 em{font-style:normal;background:linear-gradient(90deg,#F59E0B,#EC4899);-webkit-background-clip:text;color:transparent}
.photo{position:absolute;left:72px;right:72px;top:%(ph)dpx;height:%(phh)dpx;border-radius:28px;overflow:hidden;
 background:url(group.jpg) center/cover;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.tag{position:absolute;font-family:'JetBrains Mono',monospace;font-size:22px;padding:8px 14px;border-radius:8px}
.t1{left:20px;top:20px;background:rgba(26,26,46,.75);color:#A5B4FC;border:1.5px solid rgba(165,180,252,.5)}
.t2{right:20px;top:20px;background:#fff;color:#1A1A2E;font-family:'Inter Display';font-weight:700;font-size:26px}
.who{position:absolute;right:56px;top:%(who)dpx;display:flex;gap:18px}
.p{position:relative;width:%(pw)dpx}
.p .ph{width:%(pw)dpx;height:%(pw)dpx;border-radius:50%%;background-size:cover;background-position:center;border:6px solid #1A1A2E;
 box-shadow:0 0 0 3px #4A6CF7}
.badge{position:relative;margin:-34px auto 0;width:%(bw)dpx;background:#fff;color:#1A1A2E;border-radius:14px;overflow:hidden;
 box-shadow:0 14px 30px rgba(0,0,0,.4);text-align:center}
.badge i{display:block;font-style:normal;background:#4A6CF7;color:#fff;font-size:17px;font-weight:700;letter-spacing:2px;padding:6px 0;text-transform:uppercase}
.badge b{display:block;font-size:34px;font-weight:800;padding:6px 0 0;letter-spacing:-1px}
.badge small{display:block;font-size:18px;font-weight:600;color:#4A4E6E;padding:0 6px 10px}
.r1{transform:rotate(-5deg)}.r2{transform:rotate(4deg)}
.info{position:absolute;left:72px;top:%(info)dpx;width:440px}
.lead{font-size:30px;line-height:1.3;color:rgba(255,255,255,.85);font-weight:500;margin-bottom:26px}
.date{font-size:56px;font-weight:700;letter-spacing:-1.5px;line-height:1.05}
.date span{color:#A5B4FC}
.place{font-size:34px;color:rgba(255,255,255,.75);margin-top:10px;font-weight:500}
.cta{display:inline-block;background:#4A6CF7;border-radius:44px;padding:20px 34px;font-size:34px;font-weight:700;margin-top:30px}
"""

LAYOUT = {
    "4x5": dict(H=1350, top=60, pt=64, mono=170, h1=232, h1s=92, ph=450, phh=420, who=720, pw=210, bw=200, info=900),
    "9x16": dict(H=1920, top=270, pt=274, mono=390, h1=455, h1s=96, ph=690, phh=500, who=1040, pw=220, bw=210, info=1200),
}

BODY = """<div class="grid"></div>
<div class="logo">{logo}</div><div class="pill">Тбилиси</div>
<div class="mono"><s>&gt;</s> ИИ ускоряет всё<b></b></div>
<h1>А найти своих —<br><em>всё сложнее</em></h1>
<div class="photo"><span class="tag t1">human_detected: true</span><span class="tag t2">Сила сообществ</span></div>
<div class="who">
  <div class="p r1"><div class="ph" style="background-image:url(polina.jpg)"></div>
    <div class="badge"><i>Привет, я</i><b>Полина</b><small>TEXTURA</small></div></div>
  <div class="p r2"><div class="ph" style="background-image:url(max.jpg)"></div>
    <div class="badge"><i>Привет, я</i><b>Максим</b><small>Co.Space</small></div></div>
</div>
<div class="info">
  <div class="lead">Вечер, где сообщества Тбилиси знакомятся вживую</div>
  <div class="date">27 ноября<br><span>19:00</span></div>
  <div class="place">Ginger Hotel</div>
  <div class="cta">Вход свободный</div>
</div>"""

for fmt, L in LAYOUT.items():
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS % L}</style></head><body>{BODY.format(logo=LOGO)}</body></html>'
    (HERE / f"poster-ai-{fmt}.html").write_text(html)
print("ok")
