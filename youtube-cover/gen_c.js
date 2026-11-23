const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/';
const css=['montserrat/cyrillic-800','montserrat/cyrillic-900','montserrat/latin-800','montserrat/latin-900'].map(x=>`@import url("${F}${x}.css");`).join('');
const base=`${css}*{margin:0;box-sizing:border-box}body{width:1280px;height:720px;position:relative;overflow:hidden;font-family:Montserrat;color:#0d1b3d}
.bg{position:absolute;inset:0;width:1280px;height:720px}
.logo{position:absolute;left:56px;top:40px}.logo img{height:58px}
.tag{position:absolute;left:56px;top:128px;background:#1f5fd6;color:#fff;font:800 28px Montserrat;padding:10px 26px;border-radius:30px}
h1{position:absolute;left:56px;font:900 80px/1.04 Montserrat;letter-spacing:-2px}
h1 em{font-style:normal;display:inline-block;background:#1f5fd6;color:#fff;padding:2px 22px 8px;border-radius:18px;margin-top:6px}
.st{position:absolute;font:900 34px Montserrat;padding:14px 28px;border-radius:30px;box-shadow:0 14px 32px rgba(10,30,90,.3)}
.y{background:#ffd23c;color:#0d1b3d}.w{background:#fff;color:#1f5fd6}
.ck{position:absolute;width:92px;height:92px;border-radius:50%;background:#2fbf71;color:#fff;font:900 56px/92px Montserrat;text-align:center;box-shadow:0 14px 30px rgba(10,30,90,.3)}`;
const c1=`<img class=bg src="c1_bg.jpg"><div class=logo><img src="logo.png"></div>
<h1 style="top:190px;width:640px;font-size:76px">Как понять, что дочка <em>успевает?</em></h1>
<div class="st y" style="left:60px;top:560px;transform:rotate(-4deg)">Онлайн-школа без оценок</div>
<div class="ck" style="left:540px;top:440px;transform:rotate(8deg)">✓</div>`;
const c2=`<img class=bg src="c2_bg.jpg"><div class=logo><img src="logo.png"></div>
<h1 style="top:170px;width:590px;font-size:70px">Кто объяснит, если ребёнок <em>не понял?</em></h1>
<div class="st y" style="left:60px;top:560px;transform:rotate(-4deg)">Онлайн-школа</div>
<div class="st w" style="left:60px;top:630px;transform:rotate(3deg);font-size:30px">Учитель объяснит ещё раз</div>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1280,height:720}});
for(const [n,h] of [['c1',c1],['c2',c2]]){const p=process.cwd()+`/${n}.html`;fs.writeFileSync(p,`<!doctype html><meta charset=utf-8><style>${base}</style>${h}`);await pg.goto('file://'+p);await pg.waitForTimeout(800);await pg.screenshot({path:`thumb_${n}.png`});}
await b.close();})();
