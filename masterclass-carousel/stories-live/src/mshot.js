const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('m.html')); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(600);
  await (await pg.$('#s')).screenshot({ path: 'live_maria_book.png' }); await b.close(); })();
