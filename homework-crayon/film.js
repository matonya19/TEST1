// film.js — «Домашка»: one page of the boy's exercise book, drawn while we watch. Timings follow the user's voice-over.
import { layer, clear, line, fill, dab, text, handCircle, ellipse, xf, smooth, CAM, BOIL, W, H, sx, sy } from './crayon.js';
import { group, clearGroup, part, erase } from './rig.js';
import { person, K, deskDraw, notebookDraw, laptop, phoneDraw, bookDraw, eraserDraw } from './chars.js';
import { clamp, lerp, hash, track, ss, eio, eo, ei, mulberry } from '/core/lib.js';

export const DUR = 60.8;
const pr = (t, a, b) => clamp((t - a) / (b - a));
const FONT = 'Neucha';

// —— camera keys: [t, [x, y, zoom]] ——
const camT = track([
  [0, [560, 240, 1.6]], [2.3, [560, 300, 1.45]], [3.0, [540, 1020, 1.45]], [5.2, [540, 1020, 1.45]],
  [5.8, [450, 980, 1.2]], [8.3, [450, 980, 1.2]], [8.9, [560, 960, 1.1]], [12.2, [560, 960, 1.1]],
  [12.8, [540, 900, 1.05]], [18.4, [540, 900, 1.05]], [19.4, [540, 960, 1.0]], [23.3, [540, 960, 1.0]],
  [24.1, [300, 900, 1.55]], [25.7, [300, 900, 1.55]], [26.3, [820, 900, 1.55]], [28.5, [820, 900, 1.55]], [29.1, [540, 820, 1.4]], [31.0, [540, 960, 1.3]],
  [31.6, [540, 960, 1.0]], [37.3, [540, 960, 1.0]], [38.2, [840, 1690, 2.2]], [40.9, [840, 1690, 2.2]],
  [41.8, [540, 960, 1.0]], [50.0, [540, 960, 1.0]], [50.6, [840, 1660, 1.9]], [55.0, [840, 1660, 1.9]],
  [55.9, [540, 960, 1.0]], [60.8, [540, 960, 1.0]],
]);

// —— layers ——
const PAP = { f: layer(), l: layer() }, GRID = layer(), WAX = layer(), PAGE = layer(), ADF = { f: layer(), l: layer() }, WASH = layer(), FX = layer();
const DAD = group(), MOM = group(), GRAN = group(), BOY = group(), DESK = group(), ERA = group();

// —— events for foley ——
export const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: +t.toFixed(3), type, ...o });
ev(0.2, 'write', { dur: 2.3 }); ev(2.6, 'draw', { dur: 1.0 }); ev(3.4, 'scribble', { dur: 1.0 }); ev(4.2, 'write', { dur: .7 });
ev(5.3, 'draw', { dur: 1.0 }); ev(6.2, 'scribble', { dur: 1.0 }); ev(8.6, 'draw', { dur: 1.0 }); ev(9.4, 'scribble', { dur: 1.0 }); ev(10.6, 'zigzag', { dur: 1.2 });
ev(12.4, 'draw', { dur: 1.2 }); ev(13.4, 'scribble', { dur: 1.2 }); ev(17.3, 'thud'); ev(19.5, 'zigzag', { dur: .8 }); ev(21.0, 'write', { dur: 1.6 });
ev(23.8, 'draw', { dur: .6 }); ev(26.1, 'draw', { dur: .6 }); ev(29.4, 'erase', { dur: 1.6 });
[31.7, 32.2, 32.7].forEach(t => ev(t, 'paper')); [33.4, 33.8, 34.2, 34.6].forEach(t => ev(t, 'crumple')); ev(35.8, 'pop');
ev(38.0, 'brush', { dur: 1.8 }); ev(41.2, 'zigzag', { dur: 4 }); ev(45.6, 'scribble', { dur: 5.2 }); ev(52.6, 'draw', { dur: .8 });
ev(55.2, 'erase', { dur: 2.6 }); ev(58.0, 'pop'); ev(58.6, 'write', { dur: 1.0 });

// —— the scene ——
const DESK_Y = 1180;
function gridDraw() {
  const g = GRID.g; clear(GRID); g.save();
  g.setTransform(CAM.s, 0, 0, CAM.s, W / 2 - CAM.x * CAM.s, H / 2 - CAM.y * CAM.s);
  g.strokeStyle = 'rgba(110,150,205,.35)'; g.lineWidth = 1.6 / CAM.s;
  for (let x = 0; x <= 1080; x += 54) { g.beginPath(); g.moveTo(x, -400); g.lineTo(x, 2400); g.stroke(); }
  for (let y = 0; y <= 1920; y += 54) { g.beginPath(); g.moveTo(-400, y); g.lineTo(1500, y); g.stroke(); }
  g.strokeStyle = 'rgba(220,70,70,.55)'; g.lineWidth = 3 / CAM.s; g.beginPath(); g.moveTo(96, -400); g.lineTo(96, 2400); g.stroke();
  g.restore();
}
const T = (s, x, y, o = {}) => text(o.L || PAGE, s, sx(x), sy(y), { size: (o.size || 70) * CAM.s, font: FONT, col: o.col || K.ink, seed: o.seed || 7, reveal: o.reveal ?? 1, p: o.p ?? .95, stroke: 1.5, align: o.align || 'center' });

// boy position: at the desk → squeezed → in the corner → back at the desk
function boyState(t) {
  const base = { who: 'boy', s: 1.0, seed: 1000, dr: pr(t, 2.6, 3.5), cf: pr(t, 3.3, 4.3), expr: 'calm', look: [0, .4] };
  const desk = { x: 540, y: 1330, armL: [[-30, 70], [10, 110]], armR: [[30, 70], [-6, 116]] };
  if (t < 4.2) return { ...base, ...desk };
  if (t < 5.3) return { ...base, ...desk, look: [-.6, -.6], armR: [[40, -40], [60, -120]], mouth: 'smile' };            // asks
  if (t < 35.8) {
    const sq = t > 34.6 ? eo(pr(t, 34.6, 35.6)) * 60 : 0;
    const look = t < 8.5 ? [-1, 0] : t < 12.3 ? [1, -.3] : t < 18.5 ? [0, -1] : [0, -1];
    const ex = t > 17.3 && t < 18.6 ? 'surprised' : 'calm';
    return { ...base, ...desk, x: 540 + (t > 6.4 ? 70 : 0) + sq, look, expr: ex, mouth: 'flat' };
  }
  if (t < 58.0) {
    const smile = t > 39.6 && t < 45.5 || t > 52.8;
    return { ...base, x: 985, y: 1860, s: .7, expr: t > 50.2 && t < 52.4 ? 'worried' : 'calm', mouth: smile ? 'smile' : 'flat', look: t > 52.6 ? [-.6, .4] : [-.4, .8],
      armL: [[-30, 70], [10, 120]], armR: [[30, 60], [-20, 110]], legs: [[[-22, -80], [-70, -10]], [[22, -80], [70, -10]]] };
  }
  return { ...base, ...desk, look: [0, .8], expr: t > 59.4 ? 'happyclosed' : 'calm', mouth: t > 59.4 ? 'big' : 'smile' };
}

function adultsVisible(t) { return t < 58.2; }
function eraseLine(t) { return t < 55.2 ? -9999 : lerp(-100, 2000, eio(pr(t, 55.2, 57.9))); }
function eraseBelow(L, ye) {
  if (ye < -50) return;
  const poly = [[-400, -400], [1500, -400], [1500, ye]];
  for (let x = 1500; x >= -400; x -= 60) poly.push([x, ye + 20 * Math.sin(x * .05)]);
  const sp = poly.map(([x, y]) => [x, y]);
  erase(L, sp);
}

export function frame(comp, t) {
  const cam = camT(t); [CAM.x, CAM.y, CAM.s] = cam;
  const tq = Math.floor(t * 12) / 12;
  gridDraw();
  [WAX, PAGE, ADF.f, ADF.l, PAP.f, PAP.l, WASH, FX].forEach(clear);
  [DAD, MOM, GRAN, BOY, DESK, ERA].forEach(clearGroup);

  // —— page lettering: header, problem ——
  T('Домашняя работа', 560, 170, { size: 84, reveal: pr(t, .2, 1.5), seed: 11 });
  const probRe = t > 30.4 && t < 55 ? 0 : 1;
  if (probRe) T('Задача 3:  7 × 8 = ?', 560, 300, { size: 62, reveal: pr(t, 1.3, 2.5), seed: 13 });
  // the answer in white wax, hidden from the first seconds
  T('56 ✓', 790, 1800, { L: WAX, size: 120, reveal: pr(t, 2.0, 2.6), seed: 15, col: K.white });
  if (t > 4.3 && t < 5.6) T('помоги?', 330, 820, { size: 56, reveal: pr(t, 4.3, 4.9), seed: 17 });

  // —— adults' things (all erased at the end) ——
  const AD = t >= 5.3 && adultsVisible(t);
  if (AD) {
    // the clock-sun in the corner of the page
    const cr = [920, 520];
    line(ADF.l, handCircle(cr[0], cr[1], 70, 31, .05, 40), { col: K.ink, w: 7, seed: 31, draw: pr(t, 5.3, 5.8) });
    fill(ADF.f, handCircle(cr[0], cr[1], 70, 31, 0, 30), { col: '#f6d24a', p: .7, seed: 32, draw: pr(t, 5.6, 6.2) });
    const hrs = t * .6;
    line(ADF.l, [cr, [cr[0] + Math.cos(hrs) * 40, cr[1] + Math.sin(hrs) * 40]], { col: K.ink, w: 6, seed: 33 });
    line(ADF.l, [cr, [cr[0] + Math.cos(hrs * 7) * 55, cr[1] + Math.sin(hrs * 7) * 55]], { col: K.ink, w: 5, seed: 34 });
    for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2; line(ADF.l, [[cr[0] + Math.cos(a) * 84, cr[1] + Math.sin(a) * 84], [cr[0] + Math.cos(a) * 108, cr[1] + Math.sin(a) * 108]], { col: '#e8a020', w: 6, seed: 35 + k, draw: pr(t, 5.6, 6.0) }); }
    T('+5', 900, 680, { L: ADF.l, size: 60, reveal: pr(t, 5.4, 5.7), seed: 41, col: K.red });
    if (t > 8.5) T('+10', 900, 750, { L: ADF.l, size: 60, reveal: pr(t, 8.5, 8.9), seed: 42, col: K.red });
    if (t > 12.3) T('+5', 900, 820, { L: ADF.l, size: 60, reveal: pr(t, 12.3, 12.6), seed: 43, col: K.red });
    // argument zigzag between Mom and Dad
    if (t > 10.6 && t < 18.5) { const z = []; for (let i = 0; i <= 14; i++) z.push([330 + i * 32, 600 + (i % 2 ? -30 : 30) + (hash(i + Math.floor(t * 12)) - .5) * 8]); line(ADF.l, z, { col: K.red, w: 7, seed: 50, draw: pr(t, 10.6, 11.6) }); }
    // the header crossed out → «ПЕДСОВЕТ»
    if (t > 19.5) { line(ADF.l, [[230, 180], [890, 150]], { col: K.red, w: 10, seed: 55, draw: pr(t, 19.5, 20.0) }); line(ADF.l, [[230, 150], [890, 186]], { col: K.red, w: 10, seed: 56, draw: pr(t, 19.8, 20.3) }); }
    if (t > 21.0) T('ПЕДСОВЕТ', 560, 75, { L: ADF.l, size: 96, reveal: pr(t, 21.0, 22.6), seed: 57, col: K.red });
    // grandma's re-written problem («всё сначала»)
    if (t > 30.4) T('Задача 3 (по-нашему!)', 560, 300, { L: ADF.l, size: 58, reveal: pr(t, 30.4, 31.2), seed: 58, col: K.plum });
    // papers: 3 answers and 4 drafts on the desk
    const ans = [['54', 31.7, 380, 1090, -.2, K.mustard], ['65', 32.2, 540, 1060, .1, K.coral], ['48', 32.7, 700, 1090, .25, K.plum]];
    ans.forEach(([v, t0, x, y, r, c], i) => { if (t < t0) return; const pts = xf([[-60, -75], [60, -75], [60, 75], [-60, 75]], { x, y, r }); fill(PAP.f, pts, { col: K.white, p: .9, gap: 7, w: 9, seed: 60 + i, draw: pr(t, t0, t0 + .3) }); line(PAP.l, [...pts, pts[1]], { col: K.ink, w: 6, seed: 60 + i, draw: pr(t, t0, t0 + .3) }); T(v, x, y + 22, { L: PAP.l, size: 76, seed: 63 + i, col: c, reveal: pr(t, t0 + .1, t0 + .4) }); });
    [[33.4, 420, 1150], [33.8, 620, 1140], [34.2, 480, 1110], [34.6, 700, 1110]].forEach(([t0, x, y], i) => { if (t < t0) return; const R = mulberry(70 + i); const sc = []; for (let k = 0; k < 18; k++) { const a = k * 1.9, r = 26 + R() * 22; sc.push([x + Math.cos(a) * r, y + Math.sin(a) * r * .8]); } line(PAP.l, sc, { col: K.ink, w: 5, seed: 70 + i, draw: pr(t, t0, t0 + .35) }); });
    // arguing scribble clouds over the heads
    if (t > 41.0) [[260, 560, K.mustard], [540, 330, K.plum], [850, 560, K.coral]].forEach(([x, y, c], i) => { const n = 30, sc = []; const R = mulberry(80 + i + Math.floor(t * 12) % 3); for (let k = 0; k < n; k++) { const a = k * 2.3, r = 40 + R() * 70 * Math.min(1, (t - 41) / 3); sc.push([x + Math.cos(a) * r * 1.4, y + Math.sin(a) * r]); } line(ADF.l, sc, { col: c, w: 6, seed: 80 + i, draw: pr(t, 41 + i * .4, 42.5 + i * .4) }); });
    // the takeover: their colours flood the page, down to the boy's corner
    if (t > 45.5) {
      const fy = lerp(-100, 1560, ss(pr(t, 45.6, 51.0)));
      [[K.mustard, 0, 380], [K.plum, 360, 720], [K.coral, 700, 1100]].forEach(([c, x0, x1], i) => {
        const poly = [[x0 - 20, -100], [x1 + 20, -100], [x1 + 20, fy + 30 * Math.sin(i * 3 + t)], [x0 - 20, fy - 30 * Math.cos(i * 2 + t)]];
        fill(ADF.f, poly, { col: c, p: .55, gap: 16, w: 13, seed: 90 + i, ang: .9 + i * .4 });
      });
    }
    // Dad's small hint arrow next to the boy
    if (t > 52.6) { line(ADF.l, smooth([[560, 1600], [620, 1660], [680, 1710]], 4, false), { col: K.mustard, w: 9, seed: 95, draw: pr(t, 52.6, 53.2) }); line(ADF.l, [[650, 1712], [684, 1714], [678, 1680]], { col: K.mustard, w: 9, seed: 96, draw: pr(t, 53.1, 53.4) }); }
  }

  // —— characters ——
  const ye = eraseLine(t);
  if (AD) {
    const grow = t > 20.6 ? ss(pr(t, 20.6, 21.4)) : 0;
    // Grandma (behind the desk, tallest)
    if (t > 12.4) {
      const bookUp = t < 17.3;
      const gs = 1.4 + grow * .15;
      let armR = [[50, 30], [90, -60]], armL = [[-40, 80], [-40, 160]], hold = null, expr = 'angry', mouth = (t > 15 && t < 17.2) || (t > 41 && t < 45) ? 'open' : 'frown';
      if (t < 17.3) { armL = [[-60, -40], [-50, -140]]; armR = [[60, -40], [50, -140]]; hold = [null, (p, s) => bookDraw(GRAN, [p[0] - 70 * s, p[1] - 30 * s], s * .9, 641)]; }
      if (t > 28.7 && t < 31.3) { armR = [[80, 90], [160 + 40 * Math.sin(tq * 14), 200]]; hold = [null, (p, s) => eraserDraw(GRAN, [p[0], p[1] + 30 * s], s * .8, 661, .3)]; }
      person(GRAN, { who: 'gran', x: 540, y: 1200, s: gs, seed: 3000, dr: pr(t, 12.4, 13.4), cf: pr(t, 13.3, 14.5), expr, mouth, armL, armR, hold, look: t < 17.3 ? [.2, -.3] : [0, .8] });
      if (!bookUp) bookDraw(GRAN, [430, 1150], .9, 642);
    }
    // Dad (left)
    {
      const ds = 1.15 + grow * .15;
      let armR = [[60, 70], [140, 110]], armL = [[-30, 90], [-40, 170]], hold = null, expr = t < 8.5 ? 'calm' : 'worried', mouth = t < 8.5 ? 'big' : 'wavy';
      if (t > 23.6 && t < 45.5) { armL = [[30, 70], [60, 120]]; armR = [[40, 80], [110, 120]]; hold = [(p, s) => laptop(DAD, [p[0] + 60 * s, p[1]], s * .9, 601), null]; expr = 'surprised'; mouth = 'open'; }
      if (t > 41) { expr = 'angry'; mouth = 'open'; }
      if (t > 52.2) { expr = 'calm'; mouth = 'smile'; armR = [[90, 60], [200, 70]]; hold = null; }
      person(DAD, { who: 'dad', x: 250, y: 1560, s: ds, seed: 2000, dr: pr(t, 5.3, 6.3), cf: pr(t, 6.1, 7.1), expr, mouth, armL, armR, hold, look: [1, .4] });
    }
    // Mom (right)
    if (t > 8.5) {
      const ms = 1.15 + grow * .15;
      let armL = [[-60, 0], [-150, -40]], armR = [[30, 90], [40, 170]], hold = null, expr = 'angry', mouth = (t > 8.6 && t < 12.2) || t > 41 ? 'open' : 'frown';
      if (t > 25.9 && t < 45.5) { armL = [[-30, 70], [-40, 110]]; armR = [[30, 70], [40, 110]]; hold = [(p, s) => phoneDraw(MOM, [p[0] + 30 * s, p[1] - 30 * s], s * 1.2, 621), null]; expr = 'worried'; mouth = 'flat'; }
      person(MOM, { who: 'mom', x: 850, y: 1560, s: ms, seed: 2500, dr: pr(t, 8.6, 9.6), cf: pr(t, 9.4, 10.4), expr, mouth, armL, armR, hold, look: [-1, .2] });
    }
  }
  // the desk and the boy's notebook
  if (t > 2.8) {
    const nbErased = t > 29.6 && t < 58;
    deskDraw(DESK.l, DESK.f, { y: DESK_Y, dr: pr(t, 2.8, 3.4), cf: pr(t, 3.2, 3.8), col: K.brown });
    if (!nbErased) notebookDraw(DESK.l, DESK.f, 540 + (t > 58 ? 0 : 0), DESK_Y + 22, 1.1);
    if (t > 58.6) T('5', 900, 330, { L: FX, size: 150, reveal: pr(t, 58.6, 59.2), seed: 99, col: K.red });
    if (t > 59.0) line(FX, handCircle(900, 290, 80, 98, .1, 40), { col: K.red, w: 8, seed: 98, draw: pr(t, 59.0, 59.6) });
  }
  if (t > 2.6) person(BOY, boyState(t));

  // the eraser sweeps the grown-ups off the page
  if (ye > -50) {
    for (const L of [ADF.f, ADF.l, PAP.f, PAP.l, DAD.k, DAD.f, DAD.l, MOM.k, MOM.f, MOM.l, GRAN.k, GRAN.f, GRAN.l]) eraseBelow(L, ye);
    if (t < 58) eraserDraw(ERA, [540 + 300 * Math.sin(t * 9), ye + 20], 2.2, 670, .15 * Math.sin(t * 9));
  }

  // —— watercolour: reveals the white-wax answer in the corner ——
  if (t > 38.0) {
    const g = WASH.g; g.save(); g.setTransform(CAM.s, 0, 0, CAM.s, W / 2 - CAM.x * CAM.s, H / 2 - CAM.y * CAM.s);
    const front = lerp(520, 1100, eio(pr(t, 38.0, 39.8)));
    g.beginPath(); g.moveTo(500, 1600); for (let y = 1600; y <= 1960; y += 20) g.lineTo(front + 50 * Math.sin((y - 1600) / 360 * Math.PI) + 8 * Math.sin(y * .07), y); g.lineTo(500, 1960); g.closePath(); g.clip();
    const sh = new Path2D(); const blob = []; for (let k = 0; k < 28; k++) { const a = k / 28 * Math.PI * 2; const r = 1 + .08 * Math.sin(a * 5 + 1) + .05 * Math.sin(a * 11); blob.push([800 + Math.cos(a) * 230 * r, 1790 + Math.sin(a) * 120 * r]); }
    smooth(blob, 5).forEach(([x, y], i) => i ? sh.lineTo(x, y) : sh.moveTo(x, y)); sh.closePath();
    g.fillStyle = '#000'; g.globalAlpha = .75; g.fill(sh);
    g.restore();
  }

  // —— composite ——
  comp.paperCam(CAM.x, CAM.y, CAM.s);
  comp.begin();
  comp.image(GRID.c);
  comp.crayon(WAX.c, { gain: 1.1 });
  comp.crayon(PAGE.c);
  comp.crayon(ADF.f.c); comp.crayon(ADF.l.c);
  comp.group(GRAN); comp.group(DAD); comp.group(MOM);
  comp.group(DESK); comp.crayon(PAP.f.c); comp.crayon(PAP.l.c); comp.group(BOY);
  if (t > 38.0) comp.wash(WASH.c, { color: [0.42, 0.6, 0.9], resist: .95 });
  comp.crayon(FX.c);
  comp.group(ERA);
  comp.finish({ vig: .22, emb: .5 });
}
