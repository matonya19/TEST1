const {chromium}=require('playwright');const fs=require('fs');const {base,S}=require('./page.js');
const n=process.argv[2],dur=8,fps=30;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
const p=process.cwd()+`/st${n}.html`;fs.writeFileSync(p,`<!doctype html><meta charset=utf-8><style>${base}</style><body>${S[n]}</body>`);
await pg.goto('file://'+p);await pg.waitForTimeout(900);
fs.mkdirSync(`fr${n}`,{recursive:true});
await pg.evaluate(()=>{document.getAnimations().forEach(a=>a.pause())});
for(let f=0;f<dur*fps;f++){const t=f/fps*1000;
 await pg.evaluate(t=>{document.getAnimations().forEach(a=>{a.currentTime=t})},t);
 await pg.screenshot({path:`fr${n}/f${String(f).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});}
await pg.evaluate(()=>{document.getAnimations().forEach(a=>{a.currentTime=7500})});await pg.screenshot({path:`final${n}.png`});
await b.close();})();
