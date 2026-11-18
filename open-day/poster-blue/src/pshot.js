const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await pg.goto('file://' + path.resolve('poster.html')); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(800);
  await (await pg.$('#p')).screenshot({ path: 'poster_1080x1350.png' }); await b.close(); })();
