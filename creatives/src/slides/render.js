const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{const b=await chromium.launch(); const d=path.join(__dirname,'html');
for (const f of fs.readdirSync(d).filter(f=>f.endsWith('.html')).sort()){const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.join(d,f));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
await p.screenshot({path:path.join(__dirname,'..','..','png','slides',f.replace('.html','.png'))});await p.close();}
await b.close();})();
