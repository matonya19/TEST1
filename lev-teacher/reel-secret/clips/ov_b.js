const {chromium}=require('playwright');const fs=require('fs');
const B='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/montserrat/';
const css=['cyrillic-800','cyrillic-900','latin-800','latin-900'].map(s=>`@import url("${B}${s}.css");`).join('');
const html=`<style>${css}*{margin:0}body{width:1080px;height:1920px;background:transparent;font-family:Montserrat;position:relative;overflow:hidden}
@keyframes in{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}@keyframes out{to{opacity:0}}
.t{position:absolute;right:50px;text-align:right;animation:in .6s cubic-bezier(.2,.8,.2,1) both,out .4s ease 4.7s both}
.y{color:#1f5fd6;font:900 52px/1.05 Montserrat;-webkit-text-stroke:0;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 12px rgba(255,255,255,.9),0 0 22px rgba(255,255,255,.7)}
.w{color:#fff;font:800 38px/1.15 Montserrat;text-shadow:0 0 6px rgba(0,20,80,.7),0 3px 20px rgba(0,20,80,.7)}
.big{color:#1f5fd6;font:900 108px/.98 Montserrat;letter-spacing:-3px;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 14px rgba(255,255,255,.9),0 0 28px rgba(255,255,255,.7)}
</style>
<div class=t style="top:300px;animation-delay:.3s,4.7s"><div class=y>Секретное<br>упражнение</div></div>
<div class=t style="top:470px;animation-delay:.7s,4.7s"><div class=w>Которое подготовит<br>вас к общению</div></div>
<div class=t style="top:1280px;left:50px;text-align:left;animation-delay:1.1s,4.7s"><div class=big>С любым<br>ребёнком</div></div>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
fs.writeFileSync('ov.html',`<!doctype html><meta charset=utf-8>${html}`);await pg.goto('file://'+process.cwd()+'/ov.html');await pg.waitForTimeout(900);
fs.mkdirSync('ovg',{recursive:true});await pg.evaluate(()=>document.getAnimations().forEach(a=>a.pause()));
for(let f=0;f<160;f++){await pg.evaluate(t=>document.getAnimations().forEach(a=>{a.currentTime=t}),f/30*1000);await pg.screenshot({path:`ovg/o${String(f).padStart(4,'0')}.png`,omitBackground:true});}
await b.close();})();
