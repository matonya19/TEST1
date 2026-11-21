const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(__dirname,'cards','w_over.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:path.join(__dirname,'cards','w_over.png'),omitBackground:true});await b.close();})();
