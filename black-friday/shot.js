const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => { const [date = '20', out = 'slide.png'] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('slide.html') + '?date=' + date); await pg.evaluate(() => window.ready);
  const d = await pg.evaluate(() => document.getElementById('c').toDataURL('image/png'));
  fs.writeFileSync(out, Buffer.from(d.split(',')[1], 'base64')); await b.close(); })();
