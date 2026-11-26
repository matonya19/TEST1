const {chromium}=require('playwright');const fs=require('fs');
const B='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-700','cyrillic-800','latin-700','latin-800'].map(s=>`@import url("${B}${s}.css");`).join('');
const subs=[['Лев, можно маме голосовое?',.1,2.6,'y'],['А что ей сказать?',2.65,.9,'w'],['Я сказал, у нас полшколы бесплатно. Она сказала уточнить',3.9,4.3,'y'],['Здравствуйте! У нас в школе Чёрная пятница',10.7,3.2,'w'],['До 27 ноября включительно',14.3,2.2,'w'],['скидка на первый месяц обучения в школе — пятьдесят процентов',16.5,4.7,'w'],['Лев, спасибо, я записала',21.3,2.5,'m']];
const html=`<style>${css}*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;background:transparent;font-family:Manrope;position:relative;overflow:hidden}
@keyframes sub{0%{opacity:0;transform:translateY(24px)}10%{opacity:1;transform:none}90%{opacity:1}100%{opacity:0}}
@keyframes pop{0%{opacity:0;transform:scale(.4) translateY(30px)}70%{opacity:1;transform:scale(1.06)}100%{opacity:1;transform:none}}
@keyframes out{to{opacity:0;transform:translateY(-20px)}}
@keyframes up{from{opacity:0;transform:translateY(160px)}to{opacity:1;transform:none}}
.sub{position:absolute;left:70px;right:70px;top:1240px;text-align:center;font:800 54px/1.22 Manrope;color:#fff;text-shadow:0 0 12px rgba(0,0,0,.65),0 3px 26px rgba(0,0,0,.85);opacity:0;animation:sub var(--d) linear both;animation-delay:var(--s)}
.sub.y{color:#ffd23c}.sub.m{color:#e8f0ff;font-style:italic;font-weight:700}
.chat{position:absolute;left:60px;top:930px;display:flex;align-items:center;gap:16px;opacity:0;animation:pop .5s cubic-bezier(.2,.9,.3,1.2) .35s both,out .4s ease 3.5s both}
.av{width:64px;height:64px;border-radius:50%;background:#ffd23c;color:#0d1b3d;font:800 32px/64px Manrope;text-align:center;box-shadow:0 0 0 4px #fff}
.bub{background:#1f7bff;color:#fff;border-radius:36px 36px 36px 8px;padding:24px 34px;font:700 42px/1.15 Manrope;display:flex;align-items:center;gap:16px;box-shadow:0 14px 36px rgba(0,20,80,.4)}
.ban{position:absolute;left:60px;right:60px;top:1420px;background:#fff;border-radius:44px;padding:34px 44px;box-shadow:0 24px 60px rgba(0,0,0,.35);opacity:0;animation:up .7s cubic-bezier(.2,.8,.2,1) 14.9s both;color:#0d1b3d;display:flex;align-items:center;gap:30px}
.ban b{font:800 120px/1 Manrope;color:#1f5fd6;letter-spacing:-4px;white-space:nowrap}
.ban div{font:700 40px/1.22 Manrope}.ban small{display:block;font:600 30px Manrope;color:#5b6a85;margin-top:8px}
</style>
<div class=chat><div class=av>С</div><div class=bub>Можно маме голосовое?<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><rect x="9" y="3" width="6" height="11" rx="3" fill="#fff"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg></div></div>
${subs.map(([t,s,d,c])=>`<div class="sub ${c}" style="--s:${s}s;--d:${d}s">${t}</div>`).join('')}
<div class=ban><b>−50%</b><div>на первый месяц<br>обучения в SHKOLA<small>до 27 ноября включительно</small></div></div>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
fs.writeFileSync('ov.html',`<!doctype html><meta charset=utf-8>${html}`);await pg.goto('file://'+process.cwd()+'/ov.html');await pg.waitForTimeout(900);
fs.mkdirSync('ovf',{recursive:true});await pg.evaluate(()=>document.getAnimations().forEach(a=>a.pause()));
for(let f=0;f<714;f++){await pg.evaluate(t=>document.getAnimations().forEach(a=>{a.currentTime=t}),f/30*1000);await pg.screenshot({path:`ovf/o${String(f).padStart(4,'0')}.png`,omitBackground:true});}
await b.close();})();
