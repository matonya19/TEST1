const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-500','cyrillic-700','cyrillic-800','latin-500','latin-700','latin-800'].map(s=>`@import url("${F}${s}.css");`).join('');
const base=`${css}*{margin:0;box-sizing:border-box}
body{font-family:Manrope,'Noto Color Emoji';position:relative;overflow:hidden;background:linear-gradient(165deg,#ff8f86 0%,#e4496f 45%,#9a2d6c 100%);color:#fff}
.card{position:absolute;border-radius:56px;border:12px solid #fff;overflow:hidden;box-shadow:0 26px 60px rgba(60,10,40,.35)}
.card img{width:100%;height:100%;object-fit:cover}
.av{position:absolute;border-radius:50%;border:10px solid #fff;overflow:hidden;box-shadow:0 18px 40px rgba(60,10,40,.4)}
.av img{width:100%;height:100%;object-fit:cover;object-position:55% 35%}
.pillw{display:inline-block;background:#fff;color:#7a1f4f;font:800 33px Manrope;padding:14px 38px;border-radius:60px;box-shadow:0 10px 26px rgba(60,10,40,.28);white-space:nowrap}
.hl{color:#ffd23c}
.chip{display:inline-block;background:rgba(255,255,255,.2);color:#fff;font:700 28px Manrope,'Noto Color Emoji';padding:12px 28px;border-radius:40px}`;
const story=`<!doctype html><meta charset=utf-8><style>${base}body{width:1080px;height:1920px}
.logo{position:absolute;top:96px;left:0;right:0;text-align:center}.logo img{height:86px}
.pillr{position:absolute;top:226px;left:0;right:0;text-align:center}
h1{position:absolute;top:330px;left:0;right:0;text-align:center;font:800 124px/1.03 Manrope;letter-spacing:-3px;text-shadow:0 4px 30px rgba(60,10,40,.3)}
h1 span{display:block;color:#ffd23c}
.sub{position:absolute;left:70px;right:70px;top:1200px;text-align:center;font:800 50px/1.2 Manrope}
.who{position:absolute;left:0;right:0;top:1342px;text-align:center;font:500 36px Manrope;opacity:.95}.who b{font-weight:800}
.row{position:absolute;left:0;right:0;text-align:center}</style>
<div class=logo><img src="logo_teal.png"></div>
<div class=pillr><span class=pillw>● СЕГОДНЯ · «Я УЧИТЕЛЬ»</span></div>
<h1>Театральное<span>искусство!</span></h1>
<div class=card style="left:290px;top:640px;width:500px;height:500px;transform:rotate(-3deg)"><img src="masks.png"></div>
<div class=av style="left:650px;top:930px;width:250px;height:250px"><img src="photo.jpg"></div>
<div class=sub>Развитие речи и постановка мини‑сценок</div>
<div class=who>Ведущая — <b>Эвита Ильина</b>, 7 класс</div>
<div class=row style="top:1430px"><span class=pillw style="background:#fff;color:#7a1f4f">Сегодня · 23 ноября · 16:00 МСК</span></div>
<div class=row style="top:1522px"><span class=chip>🎭 Для 1–11 классов · нужны только настроение и фантазия</span></div>`;
const post=`<!doctype html><meta charset=utf-8><style>${base}body{width:1080px;height:1350px}
.logo{position:absolute;top:50px;left:64px}.logo img{height:64px}
.pr{position:absolute;top:56px;right:64px}.pr .pillw{font-size:26px;padding:12px 28px}
h1{position:absolute;left:64px;right:64px;top:150px;font:800 56px/1.12 Manrope;letter-spacing:-1.2px}
.card{left:48px;top:350px;width:520px;height:640px;transform:rotate(-2deg)}
.card img{object-position:50% 22%}
.sticker{position:absolute;left:400px;top:800px;width:250px;height:250px;border-radius:50%;border:10px solid #fff;overflow:hidden;transform:rotate(6deg);box-shadow:0 20px 44px rgba(60,10,40,.4)}
.sticker img{width:100%;height:100%;object-fit:cover;transform:scale(1.25)}
.name{position:absolute;left:70px;top:945px;background:#fff;color:#7a1f4f;border-radius:44px;padding:14px 32px;font:800 36px Manrope;box-shadow:0 12px 28px rgba(60,10,40,.3);transform:rotate(-2deg)}.name small{font:600 28px Manrope;opacity:.85;margin-left:10px}
ul{position:absolute;left:612px;right:50px;top:360px;list-style:none;font:600 30px/1.25 Manrope}
li{position:relative;padding-left:40px;margin-bottom:16px}li:before{content:'';position:absolute;left:0;top:11px;width:20px;height:20px;border-radius:50%;background:#ffd23c}
.goal{position:absolute;left:672px;right:48px;top:800px;background:#ffd23c;color:#6b1a45;border-radius:32px;padding:24px 28px;font:800 29px/1.25 Manrope;box-shadow:0 16px 36px rgba(60,10,40,.3)}
.goal small{display:block;font:700 22px Manrope;letter-spacing:1px;margin-bottom:8px;opacity:.85}
.bot{position:absolute;left:64px;right:64px;top:1130px}.bot .pillw{font-size:36px}.bot .chip{margin-left:16px;font-size:27px}
.note{position:absolute;left:64px;right:64px;top:1236px;font:500 30px Manrope;opacity:.92}</style>
<div class=logo><img src="logo_teal.png"></div><div class=pr><span class=pillw>МАСТЕР-КЛАСС «Я УЧИТЕЛЬ»</span></div>
<h1>Театральное искусство: <span class=hl>развитие речи</span> и&nbsp;постановка мини‑сценок</h1>
<div class=card><img src="photo_big.jpg"></div><div class=sticker><img src="masks.png"></div>
<div class=name>Эвита Ильина<small>7 класс</small></div>
<ul><li>Работаем над красивой и выразительной речью</li><li>Играем с эмоциями</li><li>Учимся импровизировать</li><li>Разыгрываем мини‑сценки</li></ul>
<div class=goal><small>НА МАСТЕР-КЛАССЕ</small>Научимся ярко выражать эмоции и уверенно говорить</div>
<div class=bot><span class=pillw>Сегодня · 23 ноября · 16:00 МСК</span><span class=chip>Для 1–11 классов</span></div>
<div class=note>Нужны только хорошее настроение и фантазия 💛</div>`;
(async()=>{const b=await chromium.launch();
for(const [n,h,w,hh] of [['post2',post,1080,1350]]){const pg=await b.newPage({viewport:{width:w,height:hh}});const p=process.cwd()+`/${n}.html`;fs.writeFileSync(p,h);await pg.goto('file://'+p);await pg.waitForTimeout(900);await pg.screenshot({path:`evita_${n}.png`});}
await b.close();})();
