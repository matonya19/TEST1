const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 9720, height: 1350 } });
  await p.goto('file://' + __dirname + '/panorama.html');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  const r = await p.evaluate(() => { const s=[...document.querySelectorAll('.slide')][1].querySelectorAll('.pill'); const l=s[s.length-1].getBoundingClientRect(); return [l.right,l.top+l.height/2]; });
  console.log('last pill S2', r);
  const rows = await p.evaluate(() => { const e=document.getElementById('rows').children[2].getBoundingClientRect(); return [e.right,e.top+e.height/2]; });
  console.log('row3', rows);
  await p.screenshot({ path: __dirname + '/../build/pano.png' });
  await b.close();
})();
