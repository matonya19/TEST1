const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1350}});
for(let i=1;i<=6;i++){await pg.goto('file://'+process.cwd()+`/slide${i}.html`);await pg.waitForTimeout(700);await pg.screenshot({path:`slide${i}.png`});}
await b.close();})();
