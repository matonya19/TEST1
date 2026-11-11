const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
(async () => {
  const [date = '', out = 'out.mp4', mode = 'video'] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: Number(process.env.H || 1080) } });
  await pg.goto('file://' + path.resolve(process.env.SCENE || 'scene.html') + '?date=' + encodeURIComponent(date) + '&h=' + (process.env.H || 1080));
  await pg.evaluate(() => window.ready);
  const FPS = 30, DUR = await pg.evaluate(() => window.DUR);
  if (mode === 'stills') {
    for (const t of (process.env.STILLS ? process.env.STILLS.split(',').map(Number) : [0.6, 1.5, 2.5, 4, 6, 8.9])) { await pg.evaluate(t => drawAt(t), t);
      const d = await pg.evaluate(() => document.getElementById('c').toDataURL('image/png'));
      fs.writeFileSync(`still_${t}.png`, Buffer.from(d.split(',')[1], 'base64')); }
    await b.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'slow', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < FPS * DUR; i++) {
    const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/jpeg', .95); }, i / FPS);
    ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
