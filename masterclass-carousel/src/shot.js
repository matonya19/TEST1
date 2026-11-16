const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await pg.goto('file://' + path.resolve('car.html')); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(800);
  console.log('overflow px per slide:', JSON.stringify(await pg.evaluate(() => [...document.querySelectorAll('.content')].map(c => c.scrollHeight - c.clientHeight))));
  for (let i = 1; i <= 12; i++) await (await pg.$('#s' + i)).screenshot({ path: `slide_${String(i).padStart(2, '0')}.png` });
  await b.close(); })();
