const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 4320, height: 1350 } });
  await p.goto('file://' + __dirname + '/panorama.html');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  await p.screenshot({ path: __dirname + '/../build/overlay.png', omitBackground: true });
  await b.close();
})();
