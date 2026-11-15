const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 3400 } });
  await pg.goto('file://' + path.resolve('afisha.html')); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(600);
  console.log('overflow', await pg.evaluate(() => [...document.querySelectorAll('.p')].map(p => p.scrollHeight - p.clientHeight))); await (await pg.$('#a')).screenshot({ path: 'afisha_1080x1350.png' }); await (await pg.$('#b')).screenshot({ path: 'afisha_1080x1920.png' });
  await b.close(); })();
