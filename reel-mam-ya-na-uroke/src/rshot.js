const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('reel.html')); await pg.evaluate(() => window.ready);
  for (const t of process.argv.slice(2).map(Number)) { const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/jpeg', .9); }, t);
    fs.writeFileSync(`t_${t}.jpg`, Buffer.from(d.split(',')[1], 'base64')); }
  await b.close(); })();
