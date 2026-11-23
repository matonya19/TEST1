const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-500','cyrillic-700','cyrillic-800','latin-500','latin-700','latin-800'].map(s=>`@import url("${F}${s}.css");`).join('');
const html=`<!doctype html><meta charset=utf-8><style>${css}*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Manrope;color:#0d1b3d;background:#fff}
.logo,.pill,h1,.sub{z-index:2}.logo{position:absolute;top:96px;left:0;right:0;text-align:center}.logo img{height:80px}
.pill{position:absolute;top:262px;left:0;right:0;text-align:center}
.pill span{display:inline-block;background:#1f5fd6;color:#fff;font:800 36px Manrope;padding:14px 38px;border-radius:60px;letter-spacing:1px;box-shadow:none}
h1{position:absolute;top:350px;left:0;right:0;text-align:center;font:800 128px/1.04 Manrope;letter-spacing:-3px}
h1 span{color:#1f5fd6}
.sub{position:absolute;top:690px;left:0;right:0;text-align:center;font:700 46px Manrope;color:#0d1b3d}
.band{z-index:0;position:absolute;left:0;bottom:-70px;width:1080px;-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 300px);mask-image:linear-gradient(to bottom,transparent 0,#000 300px)}
</style>
<div class=logo><img src="logo.png"></div>
<div class=pill><span>ЛЕНЬ ИЛИ ТРЕВОЖНЫЙ СИГНАЛ?</span></div>
<h1>«Не хочу<br><span>в школу»</span></h1>
<div class=sub>с экспертами</div>
<img class=band src="people2.jpg">`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
const p=process.cwd()+'/cover_w2.html';fs.writeFileSync(p,html);await pg.goto('file://'+p);await pg.waitForTimeout(900);await pg.screenshot({path:'cover_w2.png'});await b.close();})();
