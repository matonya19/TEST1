// Renders scene with a time warp (holds for voiceover) and muxes the voice track.
const { chromium } = require('playwright');
const path = require('path'); const { spawn, execFileSync } = require('child_process');
const WARP = [[0, 0], [1.35, 1.35], [3.0, 1.35], [5.55, 3.9], [6.9, 5.25], [9.2, 5.25], [10.05, 6.1], [11.9, 6.1],
  [12.8, 7.0], [13.9, 7.0], [15.2, 8.9], [17.8, 11.5], [19.6, 11.5]];
const VO = [[1.1, 1], [3.75, 2], [6.3, 3], [9.65, 4], [12.2, 5], [15.35, 6]];   // [start sec, segment #]
const sceneT = r => { for (let i = 0; i < WARP.length - 1; i++) { const [r0, s0] = WARP[i], [r1, s1] = WARP[i + 1];
  if (r <= r1) return s0 + (s1 - s0) * (r - r0) / (r1 - r0); } return WARP[WARP.length - 1][1]; };
(async () => {
  const [date = '20', out = 'vo.mp4', H = '1080', segDir = '../tts'] = process.argv.slice(2);
  const REAL = WARP[WARP.length - 1][0], FPS = 30;
  // voice track
  const inputs = [], filt = [];
  VO.forEach(([st, n], i) => { inputs.push('-i', path.join(segDir, `seg${n}.wav`)); filt.push(`[${i}]adelay=${Math.round(st * 1000)}:all=1[a${i}]`); });
  execFileSync('ffmpeg', ['-nostdin', '-v', 'error', '-y', ...inputs, '-filter_complex',
    filt.join(';') + ';' + VO.map((_, i) => `[a${i}]`).join('') + `amix=inputs=${VO.length}:normalize=0,apad,atrim=0:${REAL},highpass=f=80,acompressor=threshold=-18dB:ratio=3,loudnorm=I=-16:TP=-1.5[out]`,
    '-map', '[out]', '-ar', '48000', 'voice.wav']);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: Number(H) } });
  await pg.goto('file://' + path.resolve(process.env.SCENE || 'scene6.html') + `?date=${date}&h=${H}`);
  await pg.evaluate(() => window.ready);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', 'voice.wav',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'slow', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < Math.round(REAL * FPS); i++) {
    const r = i / FPS;
    const d = await pg.evaluate(([s, a]) => { drawAt(s, a); return document.getElementById('c').toDataURL('image/jpeg', .95); }, [sceneT(r), r]);
    ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
