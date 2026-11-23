const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-500','cyrillic-700','cyrillic-800','latin-500','latin-700','latin-800'].map(s=>`@import url("${F}${s}.css");`).join('');
const html=`<!doctype html><meta charset=utf-8><style>${css}*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Manrope;color:#fff;background:linear-gradient(180deg,#1f5fd6 0%,#123a9a 22%,#0d2268 42%,#0d2268 100%)}
.logo{position:absolute;top:96px;left:0;right:0;text-align:center}.logo img{height:80px}
.pill{position:absolute;top:262px;left:0;right:0;text-align:center}
.pill span{display:inline-block;background:#ffd23c;color:#0d1b3d;font:800 36px Manrope;padding:14px 38px;border-radius:60px;letter-spacing:1px;box-shadow:0 10px 28px rgba(0,0,20,.35)}
h1{position:absolute;top:372px;left:0;right:0;text-align:center;font:800 128px/1.04 Manrope;letter-spacing:-3px;text-shadow:0 6px 34px rgba(0,10,60,.45)}
h1 span{color:#ffd23c}
.sub{position:absolute;top:680px;left:0;right:0;text-align:center;font:600 40px Manrope;opacity:.92}
.band{position:absolute;left:0;top:790px;width:1080px;height:auto;-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 120px,#000 calc(100% - 150px),transparent 100%);mask-image:linear-gradient(to bottom,transparent 0,#000 120px,#000 calc(100% - 150px),transparent 100%)}
</style>
<div class=logo><img src="logo_teal.png"></div>
<div class=pill><span>ЛЕНЬ ИЛИ ТРЕВОЖНЫЙ СИГНАЛ?</span></div>
<h1>«Не хочу<br><span>в школу»</span></h1>
<div class=sub>Разбираемся с экспертами</div>
<img class=band src="band2.jpg">`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
const p=process.cwd()+'/cover.html';fs.writeFileSync(p,html);await pg.goto('file://'+p);await pg.waitForTimeout(900);await pg.screenshot({path:'cover.png'});await b.close();})();
