// Renders each slide of carousel.html to a 1080x1440 PNG.
// Usage: node render.js [scale]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const scale = Number(process.argv[2] || 1);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1440 }, deviceScaleFactor: scale });
  await page.goto('file://' + path.join(__dirname, 'carousel.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForLoadState('networkidle');
  const slides = await page.$$('section.slide');
  for (let i = 0; i < slides.length; i++) {
    const out = path.join(__dirname, 'out', `slide-${String(i + 1).padStart(2, '0')}.png`);
    await slides[i].screenshot({ path: out });
    console.log(out);
  }
  await browser.close();
})();
