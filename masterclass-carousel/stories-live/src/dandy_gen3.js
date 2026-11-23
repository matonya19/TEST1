const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-500','cyrillic-700','cyrillic-800','latin-500','latin-700','latin-800'].map(s=>`@import url("${F}${s}.css");`).join('');
const html=`<!doctype html><meta charset=utf-8><style>${css}*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;font-family:Manrope,'Noto Color Emoji';position:relative;overflow:hidden;background:#2a4fb0 url(bg_art.jpg) 0 0/1080px 1920px;color:#fff}
.logo{position:absolute;top:96px;left:0;right:0;text-align:center}.logo img{height:86px}
.pill{position:absolute;top:226px;left:50%;transform:translateX(-50%);background:#e5322d;border-radius:60px;padding:14px 40px;font:800 33px Manrope;letter-spacing:2px;white-space:nowrap;box-shadow:0 10px 26px rgba(0,0,0,.28)}
.pill i{display:inline-block;width:16px;height:16px;border-radius:50%;background:#fff;margin-right:14px}
h1{position:absolute;top:322px;left:0;right:0;text-align:center;font:800 116px/1.04 Manrope;letter-spacing:-2.5px;text-shadow:0 4px 30px rgba(10,20,80,.45)}
h1 span{color:#ffd23c;display:block}
.card{position:absolute;left:56px;right:56px;top:1236px;background:rgba(255,255,255,.94);backdrop-filter:blur(20px);border-radius:44px;padding:36px 44px 40px;color:#0d1b3d;box-shadow:0 24px 60px rgba(8,20,60,.4)}
.card p{font:500 34px/1.36 Manrope}.card p b{font-weight:800}
.chips{margin-top:22px;display:flex;flex-direction:column;gap:12px}
.chip{align-self:flex-start;background:#eaf1ff;color:#142348;font:700 28px Manrope,'Noto Color Emoji';padding:12px 26px;border-radius:40px}
</style>
<div class=logo><img src="logo_teal.png"></div>
<div class=pill><i></i>СЕГОДНЯ · «Я УЧИТЕЛЬ»</div>
<h1>Dandy’s World<span>с Василисой!</span></h1>
<div class=card><p><b>Василиса Лукащук</b>, ученица 4 класса SHKOLA, расскажет о персонажах и правилах игры в Roblox. А потом пройдём первые этажи вместе!</p>
<div class=chips><span class=chip>👥 Для ребят 8–12 лет с опытом игры в Roblox</span><span class=chip>📱 Телефон, планшет или компьютер с Roblox</span></div></div>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
const p=process.cwd()+'/story3.html';fs.writeFileSync(p,html);await pg.goto('file://'+p);await pg.waitForTimeout(900);await pg.screenshot({path:'story_dandy3.png'});await b.close();})();
