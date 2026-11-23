const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-700','cyrillic-800','latin-700','latin-800'].map(s=>`@import url("${F}${s}.css");`).join('');
const html=`<!doctype html><meta charset=utf-8><style>${css}*{margin:0;box-sizing:border-box}
body{width:1280px;height:720px;position:relative;overflow:hidden;font-family:Manrope;color:#fff;background:linear-gradient(120deg,#1f5fd6 0%,#123a9a 60%,#0d2a78 100%)}
.ph{position:absolute;right:0;top:0;width:560px;height:720px;overflow:hidden}
.ph img{width:100%;height:100%;object-fit:cover;object-position:50% 0%}
.ph:after{content:'';position:absolute;left:0;top:0;bottom:0;width:140px;background:linear-gradient(90deg,#123a9a,rgba(18,58,154,0))}
.logo{position:absolute;left:64px;top:46px}.logo img{height:64px}
h1{position:absolute;left:64px;top:176px;width:760px;font:800 100px/1.02 Manrope;letter-spacing:-2.5px;text-shadow:0 4px 24px rgba(0,10,60,.35)}
h2{position:absolute;left:64px;top:430px;font:800 112px/1 Manrope;letter-spacing:-2.5px;color:#ffd23c}
</style>
<div class=ph><img src="woman.jpg"></div>
<div class=logo><img src="logo_teal.png"></div>
<h1>Английский<br>до школы.</h1><h2>Уже пора?</h2>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1280,height:720}});
const p=process.cwd()+'/t.html';fs.writeFileSync(p,html);await pg.goto('file://'+p);await pg.waitForTimeout(800);await pg.screenshot({path:'thumb.png'});await b.close();})();
