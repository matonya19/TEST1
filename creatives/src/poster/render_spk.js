const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();
for (const v of ['A','B']) for (const [f,h] of [['4x5',1350],['9x16',1920]]){const p=await b.newPage({viewport:{width:1080,height:h}});
await p.goto('file://'+path.join(__dirname,`spk${v}-${f}.html`));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
await p.screenshot({path:path.join(__dirname,'..','..','png',`tbs-en-speaker-tbc-${v}-${f}.png`)});await p.close();}
await b.close();})();
