const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/';
const css=['montserrat/cyrillic-800','montserrat/cyrillic-900','montserrat/latin-800','montserrat/latin-900'].map(x=>`@import url("${F}${x}.css");`).join('');
const html=`<!doctype html><meta charset=utf-8><style>${css}*{margin:0;box-sizing:border-box}
body{width:1280px;height:720px;position:relative;overflow:hidden;font-family:Montserrat;color:#fff;background:#445}
.bg{position:absolute;left:0;top:0;width:1280px}
.sh{position:absolute;left:0;top:0;bottom:0;width:640px;background:linear-gradient(90deg,rgba(10,30,100,.82) 0%,rgba(10,30,100,.55) 55%,rgba(10,30,100,0) 100%)}
.logo{position:absolute;left:56px;top:40px}.logo img{height:62px}
h1{position:absolute;left:56px;top:150px;font:900 84px/1.04 Montserrat;letter-spacing:-1.5px;text-shadow:0 4px 26px rgba(0,10,60,.5)}
h2{position:absolute;left:56px;top:428px;font:900 100px/1 Montserrat;letter-spacing:-2px;color:#ffd23c;text-shadow:0 4px 26px rgba(0,10,60,.5)}
.b{position:absolute;background:#fff;color:#123a9a;font:900 40px Montserrat;padding:16px 30px;border-radius:30px;box-shadow:0 14px 34px rgba(0,10,60,.4)}
.b:after{content:'';position:absolute;bottom:-16px;left:40px;border:14px solid transparent;border-top:18px solid #fff;border-bottom:0}
.b.y{background:#ffd23c;color:#0d1b3d}.b.y:after{border-top-color:#ffd23c}
.b.r:after{left:auto;right:40px}
.abc{position:absolute;width:86px;height:86px;border-radius:20px;font:900 52px/86px Montserrat;text-align:center;box-shadow:0 14px 30px rgba(0,10,60,.4)}
</style>
<img class=bg src="bg_full.jpg"><div class=sh></div>
<div class=logo><img src="logo_teal.png"></div>
<h1>Английский<br>до школы.</h1><h2>Уже пора?</h2>
<div class="b" style="left:860px;top:150px;transform:rotate(-6deg)">Hello!</div>
<div class="b y r" style="left:1040px;top:210px;transform:rotate(5deg)">ABC</div>
<div class="b r" style="left:960px;top:440px;transform:rotate(-4deg);font-size:34px;white-space:nowrap">My name is…</div>
<div class=abc style="left:640px;top:590px;background:#2f6bd8;color:#fff;transform:rotate(-12deg)">A</div>
<div class=abc style="left:735px;top:620px;background:#ff7a59;color:#fff;transform:rotate(8deg)">B</div>
<div class=abc style="left:828px;top:592px;background:#ffd23c;color:#0d1b3d;transform:rotate(-6deg)">C</div>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1280,height:720}});
const p=process.cwd()+'/rich.html';fs.writeFileSync(p,html);await pg.goto('file://'+p);await pg.waitForTimeout(900);await pg.screenshot({path:'thumb_rich.png'});await b.close();})();
