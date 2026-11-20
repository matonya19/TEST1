const { chromium } = require('playwright'); const path = require('path'); const { spawn } = require('child_process');
(async () => { const [out, audio] = process.argv.slice(2); const FPS = 30, DUR = 24.5;
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('reel.html')); await pg.evaluate(() => window.ready);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', audio, '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', String(DUR), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < Math.round(DUR * FPS); i++) { const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/jpeg', .92); }, i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); })();
