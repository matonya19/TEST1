const {chromium}=require('playwright');const fs=require('fs');
const B='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/';
const css=['manrope/cyrillic-500','manrope/cyrillic-700','manrope/cyrillic-800','manrope/latin-500','manrope/latin-700','manrope/latin-800','caveat/cyrillic-600','caveat/latin-600'].map(s=>`@import url("${B}${s}.css");`).join('');
const base=`${css}*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;font-family:Manrope,'Noto Color Emoji';position:relative;overflow:hidden;color:#0d1b3d}
.blue{background:linear-gradient(165deg,#3d7cf0,#2457c4);color:#fff}
.logo{position:absolute;top:96px;left:0;right:0;text-align:center}.logo img{height:52px}
.card{position:absolute;left:70px;right:70px;background:rgba(255,255,255,.96);border-radius:40px;padding:44px 50px;box-shadow:0 22px 60px rgba(8,20,50,.28);color:#0d1b3d}
.big{font:800 70px/1.14 Manrope,'Noto Color Emoji';letter-spacing:-1px}
.hl{background:#ffd24a;color:#0d1b3d;padding:0 14px;border-radius:14px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.row{position:absolute;display:flex;gap:18px;align-items:flex-end}
.av{flex:none;width:72px;height:72px;border-radius:50%;background:#2f6bd8;color:#fff;font:800 34px/72px Manrope;text-align:center;box-shadow:0 0 0 5px #fff}
.bub{background:#fff;border-radius:40px 40px 40px 10px;padding:34px 44px;font:700 56px/1.2 Manrope;box-shadow:0 16px 44px rgba(8,20,50,.28);color:#0d1b3d}`;
const S={
1:`<body class=blue><div class=logo><img src="logo_w.png"></div>
<div class=row style="top:300px;left:70px;right:120px"><div class=av style="background:#fff;font-size:42px">🧒</div><div class=bub>«Мам, помоги с&nbsp;одной задачкой»</div></div>
<div style="position:absolute;left:80px;right:80px;top:640px;color:#fff" class=big>Через десять минут <span class=hl>ручка уже у&nbsp;вас в&nbsp;руке.</span><br><span style="font-weight:700">Знакомо? 😅</span></div>`,
2:`<body style="background:#fbf7ea"><style>
.paper{position:absolute;inset:0;background-image:linear-gradient(#bcd3f0 2px,transparent 2px),linear-gradient(90deg,#bcd3f0 2px,transparent 2px);background-size:54px 54px;background-position:30px 20px}
.mg{position:absolute;left:100px;top:0;bottom:0;width:4px;background:#f08b8b}
.dv{position:absolute;left:150px;top:1110px;font:600 112px/1 Caveat;color:#4a5568;transform:rotate(-2deg)}
.dv i{display:block}.hand{font-family:Caveat;font-weight:600}
</style><div class=paper></div><div class=mg></div>
<div class=dv><span style="border-bottom:5px solid #4a5568;padding-right:50px">1 8 2 4</span> <span style="border-left:5px solid #4a5568;border-bottom:5px solid #4a5568;padding:0 30px">4</span><br><span style="color:#8a94a6;font-size:80px">— 1 6 &nbsp;&nbsp; 4 5 6</span></div>
<div class=card style="top:290px"><div class=big style="font-size:58px;font-weight:700">Вы только вспомнили, как делить в&nbsp;столбик, начали объяснять…</div></div>
<div class=row style="top:760px;left:70px;right:100px"><div class=av style="background:#fff;font-size:42px">🧒</div><div class=bub style="font-size:62px">«Нам вообще-то <span class=hl>не&nbsp;так</span> показывали»</div></div>`,
3:`<body style="background:linear-gradient(165deg,#eaf3fd,#d4e5fb)"><div class=logo><img src="logo.png"></div>
<div style="position:absolute;left:80px;right:80px;top:270px" class=big>Собрали рилсы про родителей за&nbsp;домашкой.<div style="font-size:52px;font-weight:700;margin-top:26px">Смешно, пока не&nbsp;<span class=hl>узнаешь себя</span> 😂</div></div>
<div style="position:absolute;left:0;right:0;top:1440px;text-align:center"><div style="display:inline-block;background:#0d1b3d;color:#fff;font:700 46px Manrope,'Noto Color Emoji';padding:24px 48px;border-radius:60px">🔊 Включайте со звуком 👇</div></div>`,
4:`<body class=blue><div class=logo><img src="logo_w.png"></div>
<div class=card style="top:290px;padding-top:50px"><div class=big style="font-size:56px;font-weight:800">В <span class=hl>SHKOLA</span> дети решают задачи прямо на&nbsp;уроке.</div>
<div style="font:500 42px/1.38 Manrope;margin-top:30px;color:#33425f">Если ребёнок где-то запутался, учитель помогает разобраться. Поэтому домашки почти нет 💛</div></div>
<div class=row style="top:880px;left:70px;right:120px"><div class=av>S</div><div class=bub style="font-size:46px;font-weight:600">Посмотрите, как проходят уроки, — приходите на&nbsp;3&nbsp;бесплатных дня.</div></div>`};
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
for(const k in S){const p=process.cwd()+`/s${k}.html`;fs.writeFileSync(p,`<!doctype html><meta charset=utf-8><style>${base}</style>${S[k]}`);await pg.goto('file://'+p);await pg.waitForTimeout(900);await pg.screenshot({path:`story${k}.png`});}
await b.close();})();
