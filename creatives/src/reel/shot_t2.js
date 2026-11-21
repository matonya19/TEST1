const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();
for (const k of ['t1','t2','t3','t4','t5','t6','t7']){const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(__dirname,'cards',k+'.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(200);
await p.screenshot({path:path.join(__dirname,'cards',k+'.png'),omitBackground:true});await p.close();}
await b.close();})();
