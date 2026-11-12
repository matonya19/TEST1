const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('stories.html')); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(500);
  for (let i = 1; i <= 6; i++) await (await pg.$('#s' + i)).screenshot({ path: `story_${i}.png` });
  await b.close(); })();
