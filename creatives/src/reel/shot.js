const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{const b=await chromium.launch(); const d=path.join(__dirname,'cards');
for (const f of fs.readdirSync(d).filter(f=>f.endsWith('.html'))){const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(d,f));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:path.join(d,f.replace('.html','.png'))});await p.close();}
await b.close();})();
