const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-500','cyrillic-700','cyrillic-800','latin-500','latin-700','latin-800'].map(s=>`@import url("${F}${s}.css");`).join('');
const html=`<!doctype html><meta charset=utf-8><style>${css}*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;font-family:Manrope,'Noto Color Emoji';position:relative;overflow:hidden;background:linear-gradient(165deg,#4aa0f5 0%,#2a73e0 38%,#2748b8 100%);color:#fff}
.logo{position:absolute;top:120px;left:0;right:0;text-align:center}.logo img{height:92px}
.pill{position:absolute;top:262px;left:50%;transform:translateX(-50%);background:#e5322d;border-radius:60px;padding:16px 44px;font:800 36px Manrope;letter-spacing:2px;white-space:nowrap;box-shadow:0 10px 26px rgba(0,0,0,.25)}
.pill i{display:inline-block;width:18px;height:18px;border-radius:50%;background:#fff;margin-right:16px}
h1{position:absolute;top:372px;left:0;right:0;text-align:center;font:800 128px/1.04 Manrope;letter-spacing:-3px}
h1 span{color:#ffd23c;display:block}
.card{position:absolute;left:300px;top:690px;width:480px;height:480px;border-radius:56px;border:12px solid #fff;overflow:hidden;transform:rotate(-3deg);box-shadow:0 26px 60px rgba(0,0,0,.3)}
.card img{width:100%;height:100%;object-fit:cover}
.tx{position:absolute;left:80px;right:80px;top:1240px;text-align:center;font:500 38px/1.35 Manrope;color:#eaf2ff}
.tx b{font-weight:800;color:#fff}
.row{position:absolute;left:0;right:0;text-align:center}
.chip{display:inline-block;background:#fff;color:#142348;font:700 31px Manrope,'Noto Color Emoji';padding:16px 34px;border-radius:50px;box-shadow:0 10px 26px rgba(0,0,0,.22)}
</style>
<div class=logo><img src="logo_teal.png"></div>
<div class=pill><i></i>СЕГОДНЯ · «Я УЧИТЕЛЬ»</div>
<h1>Dandy’s World<span>с Василисой!</span></h1>
<div class=card><img src="img.png"></div>
<div class=tx><b>Василиса Лукащук</b>, ученица 4 класса SHKOLA, расскажет о персонажах и правилах игры в Roblox. А потом пройдём первые этажи вместе!</div>
<div class=row style="top:1440px"><span class=chip>👥 Для ребят 8–12 лет с опытом игры в Roblox</span></div>
<div class=row style="top:1530px"><span class=chip style="background:rgba(255,255,255,.18);color:#fff;box-shadow:none">📱 Нужен телефон, планшет или компьютер с Roblox</span></div>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
const p=process.cwd()+'/story.html';fs.writeFileSync(p,html);await pg.goto('file://'+p);await pg.waitForTimeout(900);await pg.screenshot({path:'story_dandy.png'});await b.close();})();
