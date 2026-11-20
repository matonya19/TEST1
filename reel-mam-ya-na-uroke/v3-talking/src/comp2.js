// Renders the transparent overlay layer (bubbles, drawn laptop screens, CTA) over base.mp4 and muxes audio.
const { chromium } = require('playwright'); const path = require('path'); const { spawn } = require('child_process');
(async () => { const [base, audio, out, dur = '26.6'] = process.argv.slice(2); const FPS = 30, N = Math.round(Number(dur) * FPS);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve('reel.html')); await pg.evaluate(() => window.ready);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-i', base, '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', audio,
    '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]', '-map', '[v]', '-map', '2:a', '-c:a', 'aac', '-b:a', '192k',
    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-t', dur, '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) { const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/png'); }, i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); })();
