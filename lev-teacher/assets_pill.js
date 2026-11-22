const {chromium}=require('playwright');const fs=require('fs');
const F='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-500','cyrillic-700','cyrillic-800','latin-500','latin-700','latin-800'].map(s=>`@import url("${F}${s}.css");`).join('');
const hl=(t,w)=>w?t.replace(w,`<span class=hl>${w}</span>`):t;
const caps=[
['c1','Ты новенький? Пока учителя нет, покажу одну штуку',''],
['c2','Давай',''],
['c3','Если тебя спросят, а ты не знаешь как — <b class=hl>просто замри.</b> Типа интернет завис',''],
['c4','Саш, ты показываешь или правда завис?',''],
['c5','Вот видишь, работает',''],
['c6','Так, ребят, всем привет.',''],
['c7','Я Лев, ваш новый <b class=hl>учитель</b> математики',''],
['c8','А контрольные у вас будут?',''],
['c9','Лев, <b class=hl>мышку</b> тоже не двигайте',''],
];
const base=`${css}*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;background:transparent;font-family:Manrope;position:relative}
.c{position:absolute;left:70px;right:70px;bottom:940px;text-align:center;font:800 56px/1.2 Manrope;letter-spacing:-.5px;color:#fff;text-shadow:0 0 10px rgba(0,0,0,.6),0 3px 28px rgba(0,0,0,.85)}
.hl{background:#ffd24a;color:#0d1b3d;text-shadow:none;padding:0 12px;border-radius:12px;font-weight:800;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.pill{position:absolute;left:44px;top:275px;background:#fff;color:#0d1b3d;font:700 28px Manrope;padding:11px 24px;border-radius:40px;box-shadow:0 8px 24px rgba(0,0,0,.3)}
.lab{position:absolute;color:#fff;font:700 32px Manrope;text-shadow:0 2px 10px rgba(0,0,0,.7)}.lab small{display:block;font:500 22px Manrope;opacity:.85}
.sh{position:absolute;background:linear-gradient(transparent,rgba(0,0,0,.55));border-radius:0 0 30px 30px}
.tile{position:absolute;border-radius:30px;overflow:hidden}`;
const bigLabel=(name)=>`<div class=sh style="left:24px;top:1560px;width:1032px;height:336px"></div><div class=lab style="left:56px;top:1814px">${name}<small>в сети</small></div>`;
const gridLabels=[['Саша',24,1046],['Аня',546,1046],['Тимур',24,1478],['Вика',546,1478]].map(([n,x,y])=>`<div class=sh style="left:${x}px;top:${y+260}px;width:510px;height:158px"></div><div class=lab style="left:${x+24}px;top:${y+340}px;font-size:28px">${n}<small style="font-size:20px">в сети</small></div>`).join('');
const others={pill:`<div class=pill>Лев, учитель математики</div>`,big_sasha:bigLabel('Саша'),big_girl:bigLabel('Аня'),grid:gridLabels};
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});let N=0;
async function shot(html,out){const p=process.cwd()+`/b/_h${N++}.html`;fs.writeFileSync(p,`<!doctype html><meta charset=utf-8><style>${base}</style>${html}`);await pg.goto('file://'+p);await pg.waitForTimeout(600);await pg.screenshot({path:out,omitBackground:true});}
for(const k of ['pill']) await shot(others[k],`b/${k}.png`);
await b.close();})();
