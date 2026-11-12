// Renders transparent overlay frames (bubbles + end card) and composites them on base.mp4.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
(async () => {
  const [base = 'base.mp4', audio = '', out = 'final.mp4', date = '20', stills = ''] = process.argv.slice(2);
  const plan = JSON.parse(fs.readFileSync('plan.json', 'utf8'));
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.addInitScript(p => { window.BUBBLES = p.bubbles; window.END = p.end; window.DUR = p.dur; }, plan);
  await pg.goto('file://' + path.resolve('overlay_built.html') + '?date=' + date);
  await pg.evaluate(() => window.ready);
  const FPS = 30, N = Math.round(plan.dur * FPS);
  if (stills) { // debug: composite single frames
    for (const t of stills.split(',').map(Number)) {
      const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/png'); }, t);
      fs.writeFileSync(`ov_${t}.png`, Buffer.from(d.split(',')[1], 'base64'));
    }
    await b.close(); return;
  }
  const args = ['-y', '-v', 'error', '-i', base, '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
  if (audio) args.push('-i', audio);
  args.push('-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]', '-map', '[v]');
  if (audio) args.push('-map', '2:a', '-c:a', 'aac', '-b:a', '192k');
  args.push('-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-t', String(plan.dur), '-movflags', '+faststart', out);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    const d = await pg.evaluate(t => { drawAt(t); return document.getElementById('c').toDataURL('image/png'); }, i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
