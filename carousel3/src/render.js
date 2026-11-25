// usage: node render.js still <t>   |   node render.js frames <seconds> <fps>
const { chromium } = require('playwright');
const [mode, a1, a2] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 8640, height: 1350 } });
  await p.goto('file://' + __dirname + '/panorama.html');
  await p.waitForFunction(() => window.__ready);
  const out = __dirname + '/../build/';
  if (mode === 'still') {
    await p.evaluate(t => window.setT(t), +a1);
    await p.screenshot({ path: out + 'pano.png' });
  } else {
    const dur = +a1, fps = +a2, n = Math.round(dur * fps);
    require('fs').mkdirSync(out + 'frames', { recursive: true });
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => window.setT(t), i / fps);
      await p.screenshot({ path: out + 'frames/f' + String(i).padStart(4, '0') + '.jpg', type: 'jpeg', quality: 95 });
    }
  }
  await b.close();
})();
