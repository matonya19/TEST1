const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
(async () => { const [base, audio, out, dur = '10', still = ''] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('ov.html')); await pg.evaluate(() => window.ready);
  if (still) { const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/png'); }, Number(still)); fs.writeFileSync('ov_still.png', Buffer.from(d.split(',')[1], 'base64')); await b.close(); return; }
  const FPS = 30, N = Math.round(Number(dur) * FPS);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-i', base, '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', audio,
    '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]', '-map', '[v]', '-map', '2:a', '-c:a', 'aac', '-b:a', '192k',
    '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-t', dur, '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) { const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/png'); }, i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); })();
