const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{const b=await chromium.launch(); const d=path.join(__dirname,'deck');
const order=JSON.parse(fs.readFileSync(path.join(d,'order.json')));
for (const f of order){const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.join(d,f));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
await p.screenshot({path:path.join(__dirname,'..','..','png','deck',f.replace('.html','.png'))});await p.close();}
await b.close();})();
