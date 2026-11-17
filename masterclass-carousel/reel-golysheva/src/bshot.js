const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('bg.html')); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(500);
  await (await pg.$('#c')).screenshot({ path: 'bg.png' }); await b.close(); })();
