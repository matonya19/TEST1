const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch(); const name=process.argv[2]||'leaders';
const p=await b.newPage({viewport:{width:7560,height:1350}});
await p.goto('file://'+path.join(__dirname,'wide',name+'.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
await p.screenshot({path:path.join(__dirname,'wide',name+'.png')});await b.close();})();
