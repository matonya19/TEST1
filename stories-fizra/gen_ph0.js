const {chromium}=require('playwright');const fs=require('fs');
const B='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/';
const css=['manrope/cyrillic-500','manrope/cyrillic-700','manrope/cyrillic-800','manrope/latin-500','manrope/latin-700','manrope/latin-800','caveat/cyrillic-600','caveat/latin-600'].map(s=>`@import url("${B}${s}.css");`).join('');
const base=`${css}*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;font-family:Manrope,'Noto Color Emoji';position:relative;overflow:hidden;color:#0d1b3d}
.blue{background:linear-gradient(165deg,#3d7cf0,#2457c4);color:#fff}.light{background:linear-gradient(165deg,#eaf3fd,#d4e5fb)}
.logo{position:absolute;top:96px;left:0;right:0;text-align:center}.logo img{height:52px}
.big{font:800 70px/1.14 Manrope,'Noto Color Emoji';letter-spacing:-1px}
.hl{background:#ffd24a;color:#0d1b3d;padding:0 14px;border-radius:14px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.row{position:absolute;display:flex;gap:18px;align-items:flex-end}.row.r{flex-direction:row-reverse}
.av{flex:none;width:72px;height:72px;border-radius:50%;background:#fff;font:800 40px/72px Manrope,'Noto Color Emoji';text-align:center;box-shadow:0 0 0 5px rgba(255,255,255,.9)}
.bub{background:#fff;border-radius:40px 40px 40px 10px;padding:30px 42px;font:700 52px/1.22 Manrope;box-shadow:0 16px 44px rgba(8,20,50,.28);color:#0d1b3d}
.row.r .bub{border-radius:40px 40px 10px 40px;background:#ffd24a}
.card{position:absolute;left:70px;right:70px;background:rgba(255,255,255,.96);border-radius:40px;padding:44px 50px;box-shadow:0 22px 60px rgba(8,20,50,.28);color:#0d1b3d}
.btn{display:inline-block;background:#2f6bd8;color:#fff;font:700 34px Manrope,'Noto Color Emoji';padding:22px 44px;border-radius:50px}
.cap{position:absolute;left:80px;right:80px;font:700 40px/1.3 Manrope;opacity:.95}
.sp{position:absolute;left:0;right:0;text-align:center;font:600 34px Manrope;opacity:.75}`;
const PH={0:'ph0.jpg',1:'ph1.jpg',3:'ph3.jpg',5:'ph5.jpg'};
const S={
0:`<body class=blue><div class=logo><img src="logo_w.png"></div>
<div class=card style="top:210px;padding:40px 46px"><div class=big style="font-size:58px;line-height:1.16">Сколько раз вы слышали от&nbsp;ребёнка: <span class=hl>«Можно я сегодня останусь дома?»</span></div></div>`,

1:`<body class=blue><div class=logo><img src="logo_w.png"></div>
<div class=card style="top:210px;padding:30px 44px"><div class=big style="font-size:44px;line-height:1.25">В воскресенье вечером ребёнок заглядывает в&nbsp;расписание</div></div>
<div class=row style="top:440px;left:70px;right:170px"><div class=av>🧒</div><div class=bub>«Мам, завтра <span class=hl>опять физра?</span>»</div></div>
<div class=card style="top:700px;padding:18px 40px;left:340px;right:340px;text-align:center"><div style="font:700 40px Manrope">А утром…</div></div>
<div class=row style="top:810px;left:70px;right:150px"><div class=av>🧒</div><div class=bub>«Можно я сегодня <span class=hl>останусь дома?</span>»</div></div>`,
2:`<body class=light><div class=logo><img src="logo.png"></div>
<style>.grid{position:absolute;left:70px;right:70px;top:330px}.d{display:flex;align-items:center;gap:24px;background:#fff;border-radius:36px;padding:28px 36px;margin-bottom:18px;box-shadow:0 12px 34px rgba(40,80,150,.16);font:700 44px Manrope}.d i{font-style:normal;width:150px;color:#7a8aa5;font-size:34px}.d.f{background:#ffd24a}.d.f b{margin-left:auto;font-size:40px}</style>
<div class=big style="position:absolute;left:80px;right:80px;top:170px;font-size:64px">В четверг всё повторяется</div>
<div class=grid style="top:360px"><div class="d f"><i>Пн</i>Физра 🏃<b>«Останусь дома»</b></div><div class=d><i>Вт</i>Математика · Русский</div><div class=d><i>Ср</i>Литература · Английский</div><div class="d f"><i>Чт</i>Физра 🏃<b>«Останусь дома»</b></div><div class=d><i>Пт</i>История · Музыка</div></div>
<div class=card style="top:1230px;background:#2457c4;color:#fff;font:800 56px/1.2 Manrope"><span class=hl>Именно в дни, когда в расписании физра</span><div style="font:500 38px/1.35 Manrope;margin-top:24px">Вы замечаете, что он просится остаться дома</div></div>`,
3:`<body class=blue><div class=logo><img src="logo_w.png"></div>
<div class=card style="top:210px;padding:30px 44px"><div class=big style="font-size:46px">Попробуйте начать с&nbsp;того, что <span class=hl>заметили</span></div></div>
<div class=row style="top:1010px;left:60px;right:200px"><div class=av style="font-size:36px">👩</div><div class=bub style="font-size:38px">«Слушай, ты чаще просишь остаться дома, когда у&nbsp;тебя физра. Как у&nbsp;тебя там дела?»</div></div>
<div class=row r style="top:1260px;left:160px;right:50px"><div class=av>🧒</div><div class=bub style="font-size:42px">«Сама физра нормальная. Я&nbsp;<span style="background:#fff;padding:0 10px;border-radius:12px">в раздевалку идти не хочу</span>»</div></div>
<div class=card style="top:1560px;padding:22px 40px;text-align:center"><div style="font:800 44px/1.25 Manrope">Теперь есть о&nbsp;чём поговорить конкретнее</div></div>`,
4:`<body class=blue><div class=logo><img src="logo_w.png"></div>
<div class=card style="top:250px;padding:40px 46px"><div class=big style="font-size:52px">Что делать, если <span class=hl>«можно я не пойду?»</span> звучит всё чаще?</div></div>
<div class=cap style="top:1540px;text-align:center;font-size:36px;line-height:1.4">В рилсе разбираем, на что обратить внимание и&nbsp;в какой момент стоит подумать о&nbsp;смене класса или школы</div>
`,
5:`<body class=blue><div class=logo><img src="logo_w.png"></div>
<div class=card style="top:210px;padding:36px 44px"><div class=big style="font-size:48px">Присматриваетесь к&nbsp;онлайн-школе?</div><div style="font:500 36px/1.38 Manrope;margin-top:20px;color:#33425f">Попробуйте <b class=hl style="font-weight:800">3 бесплатных дня</b> в&nbsp;SHKOLA. Ребёнок подключится к&nbsp;урокам по&nbsp;расписанию и&nbsp;познакомится с&nbsp;классом.</div></div>
<div class=row r style="top:1180px;left:60px;right:60px"><div class=av style="font-size:36px">💬</div><div class=bub style="font-size:44px;background:#fff">Напишите <span class=hl>«3 дня»</span> в&nbsp;ответ на&nbsp;сторис 💛</div></div>`};
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
for(const k in S){const p=process.cwd()+`/s${k}.html`;let h=S[k];if(PH[k])h=h.replace(/<body class=blue>/,`<body style="background:#223 url(${PH[k]}) 0 0/1080px 1920px">`);fs.writeFileSync(p,`<!doctype html><meta charset=utf-8><style>${base}</style>${h}`);await pg.goto('file://'+p);await pg.waitForTimeout(800);await pg.screenshot({path:`ps${k}.png`});}
await b.close();})();
