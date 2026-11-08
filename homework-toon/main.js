// main.js — «Домашка», Sci-Fi Sitcom Toon. 1080×1920, 24 fps. Timings follow the user's original voice-over.
import { clamp, lerp, seg, ss, eio, eo, ei, back, hash, TAU } from '/core/lib.js';
import { W, H, INK, init, g, frame, push, pop, translate, rotate, scale, reset, shape, fillOnly, stroke, ell, arc, spline, rr, rect, noodle, quad, dot, text, bands, S } from './toon.js';
import { C, boy, dad, mom, gran, notebook, pencil, calculator, phone, bigBook, paper, hand, sweat } from './chars.js';

const cv = document.getElementById('c');
init(cv);
window.DUR = 60.8;

// —— palettes ——
const HOME = { wall: ['#a9cfa8', '#9cc5a1', '#93bd98'], wallS: '#7fa886', floor: '#c98b55', floorS: '#a96d3c', desk: '#b0773f', deskS: '#8a5a2c', deskTop: '#c88a4c', trim: '#f1e6cc' };
const BRIDGE = { bg: ['#2a1660', '#341b72', '#3f2286'], floor: '#1d1248', gold: '#f2b630', goldS: '#c48a12', ink: '#141a4a', screen: '#ffd86b' };
const BEIGE = { wall: ['#eadfc8', '#e5d8be', '#dfd1b5'], wallS: '#cbb995', floor: '#b89b72', floorS: '#9a7f58', desk: '#8a6a4a', deskS: '#6e5238', deskTop: '#9c7a56', trim: '#f4ecdc' };
const MINT = '#7dffc4';

// —— camera ——
function cam(cx, cy, z, { rot = 0, shake = 0, t = 0 } = {}) {
  reset();
  const sx = shake ? (hash(Math.floor(t * 24) * 1.7) - .5) * 2 * shake : 0, sy = shake ? (hash(Math.floor(t * 24) * 3.1 + 5) - .5) * 2 * shake : 0;
  translate(W / 2 + sx, H / 2 + sy); scale(z); rotate(rot); translate(-cx, -cy);
}
const q12 = t => Math.floor(t * 12) / 12;
const shakeAt = (t, t0, amp = 26, d = .5) => (t >= t0 && t < t0 + d) ? amp * Math.cos((t - t0) * 30) * (1 - (t - t0) / d) : 0;

// —— terminal tag (screen space) ——
function tag(str, t0, t, { col = '#ffd86b', bg = 'rgba(20,26,74,.92)', y = 150, size = 46, hold = 99 } = {}) {
  if (t < t0 || t > t0 + hold) return;
  const n = Math.min(str.length, Math.floor((t - t0) * 18) + 1);
  const sub = str.slice(0, n) + ((Math.floor(t * 4) % 2 && n < str.length + 1) ? '_' : '');
  reset();
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.font = `${size}px PS2P`;
  const w = g.measureText(str + '_').width + 60;
  shape(rr(W / 2 - w / 2, y - size, w, size * 2, 14), { fill: bg, lw: 7 });
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.font = `${size}px PS2P`; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillStyle = col;
  g.fillText(sub, W / 2 - w / 2 + 30, y + 4);
}

// ===================== SETS =====================
function room(P, { night = true } = {}) {
  bands(P.wall, -600, 1500, -1400, 2600);
  fillOnly(rect(-1400, 1500, 4000, 1400), P.floor, { boil: 0 });
  for (let i = 0; i < 9; i++) stroke([[-400 + i * 200, 1500], [-700 + i * 260, 2400]], 4, { line: P.floorS, boil: .5 });
  stroke([[-1400, 1500], [2600, 1500]], 7);
  // door (left)
  shape(rect(20, 560, 320, 940), { fill: P.trim, lw: 7 });
  shape(rect(52, 600, 256, 900), { fill: '#4a5a52', lw: 6, shade: () => fillOnly(rect(52, 600, 256, 120), '#3a4842', { boil: .3 }) });
  // planet poster
  shape(rect(410, 470, 220, 290), { fill: '#24305e', lw: 6, shade: () => { fillOnly(ell(520, 620, 70, 70, 30), '#ff9e5e', { boil: .3 }); fillOnly(ell(545, 600, 26, 20, 16), '#ffc48a', { boil: .3 }); } });
  stroke(ell(520, 620, 110, 26, 40).slice(20, 40), 5, { line: '#ffd86b' });
  // window (right)
  shape(rect(700, 420, 300, 380), { fill: P.trim, lw: 7 });
  shape(rect(726, 446, 248, 328), { fill: night ? '#2b2f6b' : '#bcd9e6', lw: 6, shade: () => { if (night) { for (let i = 0; i < 14; i++) dot(740 + hash(i) * 220, 460 + hash(i + 3) * 300, 3, '#ffe9a8'); fillOnly(ell(930, 500, 26, 26, 18), '#ffe9a8', { boil: .3 }); } } });
  stroke([[850, 446], [850, 774]], 6); stroke([[726, 610], [974, 610]], 6);
  // shelf
  shape(rect(380, 330, 360, 26), { fill: P.trim, lw: 6 });
  const bk = ['#e8392b', '#3a7bd5', '#ffcf3f', '#2fb7a8', '#8e4a8a'];
  for (let i = 0; i < 7; i++) shape(rect(400 + i * 44, 330 - 70 - hash(i) * 30, 36, 70 + hash(i) * 30), { fill: bk[i % 5], lw: 5 });
}
function desk(P, { y = 1170, x0 = 70, x1 = 1010 } = {}) {
  shape([[x0 + 40, y], [x1 - 40, y], [x1, y + 90], [x0, y + 90]], { fill: P.deskTop, lw: 7 });
  shape(rect(x0, y + 90, x1 - x0, 60), { fill: P.desk, lw: 7 });
  shape(rect(x0 + 30, y + 150, 60, 360), { fill: P.deskS, lw: 6 });
  shape(rect(x1 - 90, y + 150, 60, 360), { fill: P.deskS, lw: 6 });
  shape(rect(x0 + 220, y + 150, x1 - x0 - 440, 140), { fill: P.desk, lw: 6, shade: () => fillOnly(rect(x0 + 220, y + 250, x1 - x0 - 440, 60), P.deskS, { boil: .3 }) });
  shape(rr((x0 + x1) / 2 - 40, y + 200, 80, 22, 10), { fill: P.trim, lw: 5 });
}
function lamp(x, y) {
  shape(ell(x, y, 60, 16, 20), { fill: '#2a2230', lw: 6 });
  stroke([[x, y], [x + 30, y - 160], [x - 50, y - 250]], 10);
  shape([[x - 110, y - 230], [x - 10, y - 290], [x + 20, y - 230], [x - 60, y - 190]], { fill: '#2fb7a8', lw: 6 });
}
// notebook lying on the desk (squashed by perspective)
function deskBook(x, y, s, o = {}) { push(); translate(x, y); scale(1, .5); notebook(0, 0, s, o); pop(); }

function bridgeSet(t, { alarm = 0 } = {}) {
  bands(BRIDGE.bg, -600, 1450, -1400, 2600);
  // viewport with stars
  shape(ell(540, 640, 400, 400, 80), { fill: '#7a62c9', lw: 8 });
  shape(ell(540, 640, 350, 350, 80), {
    fill: BRIDGE.ink, lw: 7, shade: () => {
      for (let i = 0; i < 60; i++) { const sx = 190 + hash(i * 1.3) * 700, sy = 290 + hash(i * 2.7) * 700, tw = Math.floor(t * 6 + i) % 5 === 0; dot(sx, sy, tw ? 4 : 2.5, '#ffe9a8'); }
      fillOnly(ell(700, 760, 120, 120, 40), BRIDGE.gold, { boil: .4 });
      fillOnly(ell(740, 730, 60, 50, 20), '#ffd86b', { boil: .3 });
      fillOnly(ell(700, 760, 200, 34, 40), 'rgba(255,216,107,.35)', { boil: .4 });
    }
  });
  for (let k = 0; k < 8; k++) { const a = k / 8 * TAU; dot(540 + Math.cos(a) * 375, 640 + Math.sin(a) * 375, 9, '#2a1660'); }
  // side panels
  for (const sx of [-1, 1]) {
    const x = sx < 0 ? -40 : 900;
    shape(rect(x, 300, 220, 1150), { fill: '#4b2a95', lw: 7, shade: () => fillOnly(rect(x, 300, 60, 1150), '#2a1660', { boil: .3 }) });
    for (let i = 0; i < 5; i++) { const on = (Math.floor(t * 3 + i + sx) % 3) === 0; shape(ell(x + 120, 420 + i * 150, 24, 24, 16), { fill: alarm && i % 2 ? (Math.floor(t * 6) % 2 ? '#ff4a5a' : '#7a1a2a') : (on ? BRIDGE.gold : '#6a4aa8'), lw: 5 }); }
  }
  fillOnly(rect(-1400, 1450, 4000, 1400), BRIDGE.floor, { boil: 0 });
  stroke([[-1400, 1450], [2600, 1450]], 7);
  for (let i = 0; i < 7; i++) stroke([[-200 + i * 240, 1450], [-900 + i * 480, 2500]], 4, { line: '#2e1f6a', boil: .4 });
  if (alarm) { reset(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = .18 * (Math.floor(t * 4) % 2); g.fillStyle = '#ff2a4a'; g.fillRect(0, 0, W, H); g.globalAlpha = 1; }
}
// the command console = the desk transformed
function console_(x, y, w = 820, { nb = true, nbGlow = .6, t = 0, open = 1 } = {}) {
  shape([[x - w / 2 + 40, y], [x + w / 2 - 40, y], [x + w / 2, y + 100], [x - w / 2, y + 100]], { fill: BRIDGE.gold, lw: 7, shade: () => fillOnly(rect(x - w / 2, y + 60, w, 50), BRIDGE.goldS, { boil: .3 }) });
  shape(rect(x - w / 2, y + 100, w, 320), { fill: '#5a36a8', lw: 7, shade: () => fillOnly(rect(x - w / 2, y + 300, w, 120), '#3f2286', { boil: .3 }) });
  for (let i = 0; i < 6; i++) { const on = (Math.floor(t * 4) + i) % 3 === 0; shape(rr(x - w / 2 + 50 + i * (w - 100) / 6, y + 150, 70, 40, 8), { fill: on ? '#ff7a6b' : BRIDGE.gold, lw: 5 }); }
  if (nb) { push(); translate(x, y + 48); scale(1, .5); notebook(0, 0, .8, { glow: nbGlow, t, open }); pop(); }
}
function holoScreen(x, y, w, h, lines, t, col = MINT) {
  shape(rr(x - w / 2, y - h / 2, w, h, 16), { fill: 'rgba(20,26,74,.9)', lw: 7 });
  g.setTransform(1, 0, 0, 1, 0, 0);
  lines.forEach((ln, i) => text(ln, x - w / 2 + 34, y - h / 2 + 60 + i * 56, { font: '28px PS2P', fill: col, align: 'left' }));
}

// ===================== SHOTS =====================
const SHOTS = [];
const shot = (t0, t1, fn) => SHOTS.push({ t0, t1, fn });

// 1 — insert: the problem
shot(0, 2.6, (t) => {
  const u = seg(t, 0, 2.6), tq = q12(t);
  cam(520, 1215, lerp(2.7, 2.1, eio(u)));
  room(HOME); desk(HOME);
  deskBook(540, 1215, 1.2, { t });
  const tap = Math.floor(tq * 4) % 2;
  push(); translate(700, 1150 - tap * 8); pencil(0, 0, -1.0 + tap * .08, .9); pop();
  hand(660, 1210, -.4, 22, C.skin, { fist: true });
});
// 2 — the request
shot(2.6, 5.3, (t) => {
  const u = seg(t, 2.6, 5.3), tq = q12(t);
  cam(540, 1000, lerp(1.0, 1.08, eio(u)));
  room(HOME);
  // dad peeks in at the door
  const peek = eo(seg(t, 3.0, 3.6));
  dad({ x: lerp(-60, 190, peek), y: 1500, s: 1, face: 1, t: tq, lean: -.12 * peek, look: [1, .3], brow: .5, mouth: { sm: .5 }, armR: { h: [60, 100], bend: 30 } });
  shape(rect(20, 560, 32, 940), { fill: HOME.trim, lw: 7 });       // door frame in front of him
  const look = t > 3.7 ? [-1, -.4] : [0, .6];
  boy({ x: 600, y: 1340, s: 1.4, t: tq, look, lid: t > 3.7 ? .35 : .45, brow: t > 3.7 ? .6 : 0, mouth: { o: (t > 4.1 && t < 4.8) ? .25 + .2 * Math.abs(Math.sin(t * 12)) : 0, sm: .1 }, armR: { h: [60, 150], bend: 10 }, armL: { h: [-40, 150], bend: -10 } });
  desk(HOME); lamp(900, 1200);
  deskBook(560, 1215, .9, { t });
});
// 3 — +5 min: Dad has taken over
shot(5.3, 8.5, (t) => {
  const u = seg(t, 5.3, 8.5), tq = q12(t);
  cam(540, 1020, 1.05);
  room(HOME);
  boy({ x: 930, y: 1500, s: 1.25, t: tq, face: -1, look: [1, .2], lid: .55, mouth: { sm: -.3 }, armR: { h: [10, 120], bend: 10 }, armL: { h: [-10, 120], bend: -10 } });
  const ant = eo(seg(t, 6.6, 7.2));
  dad({ x: 470, y: 1570, s: 1, t: tq, nerv: .35, look: [0, .8], brow: .7, lid: 0, mouth: { o: .25 + .2 * Math.abs(Math.sin(tq * 9)), sm: .3 },
    armR: { h: [110, 220], bend: 30 }, armL: { h: [-30, -110], bend: -50 }, holdL: (hp) => calculator(hp[0], hp[1] - 60, -.2, ant) });
  desk(HOME); lamp(130, 1200);
  deskBook(560, 1215, .9, { t });
  pencil(620, 1180, -.9 + Math.sin(tq * 20) * .15, .8);
  tag('+5 МИН', 5.3, t, { y: 150 });
});
// 4 — +10 min: Mom explains why Dad is wrong (whip pan between faces)
shot(8.5, 12.3, (t) => {
  const tq = q12(t);
  const whip = eio(seg(t, 10.1, 10.45));
  const cx = lerp(720, 330, whip);
  cam(cx, 900, 1.45);
  room(HOME);
  const talk = (a, b) => (t > a && t < b) ? .25 + .3 * Math.abs(Math.sin(tq * 10)) : 0;
  dad({ x: 330, y: 1570, s: 1, t: tq, nerv: t > 10.4 ? .6 : .2, look: [1, -.2], brow: .9, mouth: { o: 0, sm: -.6, w: .8 }, sweat: t > 10.4 ? t * 1.3 : null, armR: { h: [80, 220], bend: 20 }, armL: { h: [-40, 220], bend: -20 } });
  mom({ x: 760, y: 1560, s: 1, face: -1, t: tq, look: [1, .1], brow: -.5, mouth: { o: talk(8.6, 12.0), sm: -.2 }, armR: { h: [200, -10], bend: -30, point: true }, armL: { h: [40, 150], bend: 20 } });
  desk(HOME, { y: 1190 });
  deskBook(420, 1235, .9, { t });
  if (whip > 0 && whip < 1) { reset(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = .55; g.fillStyle = '#e8f0e0'; for (let i = 0; i < 26; i++) g.fillRect(0, hash(i) * H, W, 6 + hash(i + 7) * 18); g.globalAlpha = 1; }
  tag('+10 МИН', 8.5, t, { y: 150 });
});
// 5 — +5 min: Grandma at the door
shot(12.3, 15.0, (t) => {
  const tq = q12(t), u = seg(t, 12.3, 15.0);
  const push_ = eo(seg(t, 13.2, 13.6));
  cam(lerp(420, 260, push_), lerp(1000, 960, push_), lerp(1.0, 1.5, push_));
  room(HOME);
  const enter = eo(seg(t, 12.5, 13.1));
  gran({ x: 180, y: 1500, s: lerp(.95, 1.15, enter), t: tq, look: [1, 0], brow: -.8, lid: .35, mouth: { sm: -.6 }, armR: { h: [20, -30], bend: -40, point: t > 14 }, armL: { h: [-60, 120], bend: -30 }, holdL: (hp) => bigBook(hp[0] - 30, hp[1] - 10, -.2, .7) });
  // backs of mom & dad in the foreground
  mom({ x: 900, y: 1900, s: 1.3, face: -1, t: tq, look: [-1, -.2], brow: .6, lid: 0, mouth: { o: .3, sm: 0 } });
  dad({ x: 640, y: 2050, s: 1.35, face: -1, t: tq, look: [-1, -.3], brow: .8, lid: 0, mouth: { o: .35 } });
  tag('+5 МИН', 12.3, t, { y: 150 });
});
// 6 — "in a normal school…" — the book slams
shot(15.0, 18.5, (t) => {
  const tq = q12(t);
  const SLAM = 17.3;
  if (t < 17.8) {
    const sh = shakeAt(t, SLAM, 30);
    cam(520, 1000, 1.55, { shake: Math.abs(sh), t });
    room(HOME);
    const lift = t < SLAM ? eo(seg(t, 15.4, 16.6)) : 0;
    const bookY = t < SLAM ? lerp(1110, 1060, lift) : 1205;
    gran({ x: 560, y: 1540, s: 1.15, t: tq, look: [0, t < SLAM ? -.4 : .6], brow: -1, lid: .25, mouth: { o: (t > 15.1 && t < 17.2) ? .2 + .3 * Math.abs(Math.sin(tq * 9)) : 0, sm: -.7 },
      armR: { h: [60, lerp(140, -10, lift)], bend: -40 }, armL: { h: [-60, lerp(140, -10, lift)], bend: 40 } });
    desk(HOME, { y: 1190 });
    deskBook(400, 1235, .9, { t });
    bigBook(560, bookY, t < SLAM ? .05 : 0, 1.0);
    if (t >= SLAM && t < SLAM + .3) for (let k = 0; k < 6; k++) { const a = -Math.PI + k / 5 * Math.PI; stroke([[560 + Math.cos(a) * 150, 1200 + Math.sin(a) * 60], [560 + Math.cos(a) * 230, 1200 + Math.sin(a) * 110]], 7); }
  } else {
    // reaction close-up: the boy
    cam(560, 820, 2.2);
    room(HOME);
    boy({ x: 560, y: 1340, s: 1.4, t: tq, look: [-.6, 0], lid: .5, blink: t > 18.0 && t < 18.12, mouth: { sm: -.2, skew: .3 } });
  }
});
// 7 — the family council: notebook → portal → bridge
shot(18.5, 23.6, (t) => {
  const tq = q12(t);
  if (t < 21.3) {
    const zin = ei(seg(t, 20.2, 21.3));
    cam(540, lerp(1060, 1238, zin), lerp(.95, 9, zin), { rot: zin * .6 });
    room(HOME);
    const glow = seg(t, 19.0, 20.2);
    gran({ x: 170, y: 1560, s: 1.0, t: tq, look: [1, .5], brow: -.8, mouth: { o: .2 } });
    mom({ x: 900, y: 1540, s: .98, face: -1, t: tq, look: [1, .6], brow: .2, mouth: { o: .2 } });
    dad({ x: 360, y: 1580, s: .95, t: tq, look: [1, .7], brow: .7, lid: 0, mouth: { o: .3 } });
    boy({ x: 700, y: 1360, s: 1.2, t: tq, look: [0, -.5], lid: .5, mouth: { sm: -.2 } });
    desk(HOME, { y: 1190 });
    deskBook(540, 1238, .95, { glow: glow * (1 + .06 * Math.sin(t * 20)), t });
    if (zin > .5) { reset(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = (zin - .5) * 2; g.fillStyle = MINT; g.fillRect(0, 0, W, H); g.globalAlpha = 1; }
  } else {
    const o = eo(seg(t, 21.3, 22.0));
    cam(540, 1000, lerp(1.15, 1.0, eo(seg(t, 21.3, 23.6))));
    bridgeSet(t);
    gran({ x: 150, y: 1650, s: .95, t: tq, look: [1, -.2], brow: -.6, lid: .3, mouth: { sm: -.3 } });
    dad({ x: 360, y: 1700, s: .95, t: tq, look: [.5, -.6], brow: .8, lid: 0, mouth: { o: .4, sm: .4 } });
    mom({ x: 900, y: 1660, s: .95, face: -1, t: tq, look: [1, -.4], brow: .3, mouth: { o: .3, sm: .3 } });
    boy({ x: 640, y: 1460, s: 1.0, t: tq, look: [0, 0], lid: .55, mouth: { sm: -.2 } });
    console_(540, 1290, 900, { t, nbGlow: .7 });
    tag('ПЕДСОВЕТ', 22.1, t, { y: 160, size: 54 });
    // swirl wipe opening into the bridge
    if (o < 1) swirlOverlay(o, t);
  }
});
function swirlOverlay(o, t) {
  const r = o * 1400;
  reset(); g.setTransform(1, 0, 0, 1, 0, 0);
  g.save();
  const P = new Path2D(); P.rect(0, 0, W, H); P.arc(W / 2, H / 2, Math.max(1, r), 0, TAU); g.clip(P, 'evenodd');
  g.fillStyle = MINT; g.fillRect(0, 0, W, H);
  g.fillStyle = '#3fd6a0';
  for (let k = 0; k < 6; k++) {
    g.beginPath();
    for (let i = 0; i <= 40; i++) { const rr_ = i * 40, a = k / 6 * TAU + i * .16 + t * 6; g.lineTo(W / 2 + Math.cos(a) * rr_, H / 2 + Math.sin(a) * rr_); }
    for (let i = 40; i >= 0; i--) { const rr_ = i * 40, a = k / 6 * TAU + i * .16 + t * 6 + .35; g.lineTo(W / 2 + Math.cos(a) * rr_, H / 2 + Math.sin(a) * rr_); }
    g.fill();
  }
  g.restore();
  g.lineWidth = 9; g.strokeStyle = INK; g.beginPath(); g.arc(W / 2, H / 2, Math.max(1, r), 0, TAU); g.stroke();
}
// 8 — three stations, same framing: search / message / START OVER
shot(23.6, 31.3, (t) => {
  const tq = q12(t);
  const k = t < 25.9 ? 0 : t < 28.7 ? 1 : 2;
  const t0 = [23.6, 25.9, 28.7][k];
  const pushIn = eio(seg(t, t0, t0 + 2.6));
  cam(540, 1050, lerp(1.0, 1.08, pushIn));
  bridgeSet(t);
  if (k === 0) {
    holoScreen(540, 760, 720, 330, ['ПОИСК:', '«как решать', ' 7×8 по-новому»', 'НАЙДЕНО: 4 812 000'].slice(0, 1 + Math.floor((t - t0) * 2.2)), t);
    dad({ x: 540, y: 1700, s: 1.05, t: tq, nerv: .3, look: [0, -.8], brow: .8, lid: 0, mouth: { o: .2 + .15 * Math.abs(Math.sin(tq * 8)) },
      armR: { h: [110, -60 - 30 * Math.abs(Math.sin(tq * 14))], bend: -40 }, armL: { h: [-110, -60 - 30 * Math.abs(Math.cos(tq * 14))], bend: 40 } });
  } else if (k === 1) {
    const msg = 'УЧИТЕЛЬНИЦЕ: Здравствуйте! У нас вопрос по задаче…';
    const n = Math.floor((t - t0) * 16);
    holoScreen(540, 760, 760, 330, ['СООБЩЕНИЕ', msg.slice(0, Math.min(n, 18)), msg.slice(18, Math.max(18, Math.min(n, 36))), msg.slice(36, Math.max(36, n))], t, '#ff9e8e');
    mom({ x: 540, y: 1660, s: 1.05, t: tq, look: [0, .7], brow: -.3, mouth: { sm: -.2, skew: .3 },
      armR: { h: [40, 60], bend: 30 }, armL: { h: [-40, 60], bend: -30 }, holdR: (hp) => phone(hp[0] - 40, hp[1] - 20, .1, 1.2) });
  } else {
    const PRESS = 30.5;
    const pressed = t >= PRESS;
    holoScreen(540, 760, 700, 300, pressed ? ['', '   ВСЁ', '   СНАЧАЛА!'] : ['ПРОГРЕСС:', '██████░░ 80%'], t, pressed ? '#ff6a7a' : MINT);
    const sh = shakeAt(t, PRESS, 22);
    if (sh) { reset(); cam(540, 1050, 1.08, { shake: Math.abs(sh), t }); }
    gran({ x: 540, y: 1700, s: 1.2, t: tq, look: [0, .6], brow: -1, lid: .2, mouth: { o: pressed && t < 31 ? .6 : 0, sm: -.6 },
      armR: { h: [90, pressed ? 120 : lerp(100, -200, eo(seg(t, 29.2, 30.2)))], bend: -40, fist: true } });
    // the big red button
    shape(ell(640, 1330 + (pressed ? 10 : 0), 90, pressed ? 22 : 34, 30), { fill: '#e8392b', lw: 7 });
    shape(rect(550, 1335, 180, 50), { fill: '#7a1a2a', lw: 6 });
  }
  console_(540, 1360, 980, { t, nb: false });
  if (k === 2 && t >= 30.5) for (let i = 0; i < 8; i++) { const a = hash(i) * TAU, d = (t - 30.5) * 1400; paper(540 + Math.cos(a) * d, 1300 + Math.sin(a) * d * .6 - (t - 30.5) * 300, a + (t - 30.5) * 6, .7); }
});
// 9 — top-down: 3 answers, 4 drafts, no room for the child
shot(31.3, 37.2, (t) => {
  const tq = q12(t);
  cam(540, 960, 1.0);
  fillOnly(rect(-200, -200, 1500, 2400), BRIDGE.gold, { boil: 0 });
  for (let i = 0; i < 12; i++) stroke([[-100, i * 180], [1200, i * 180 + 40]], 4, { line: BRIDGE.goldS, boil: .5 });
  // the child's notebook, being squeezed
  const squeeze = eio(seg(t, 35.6, 36.9));
  notebook(lerp(540, 1060, squeeze), lerp(1500, 1560, squeeze), 1.1, { t });
  const drop = (i, ti) => { const p = eo(seg(t, ti, ti + .25)); return p; };
  const ANS = [['56', 31.7], ['54', 32.2], ['65', 32.7]];
  ANS.forEach(([v, ti], i) => { const p = drop(i, ti); if (p > 0) paper(220 + i * 320, lerp(-200, 520 + (i % 2) * 60, p), (i - 1) * .18, 1.15, { txt: v, ink: i === 0 ? '#1e9e5a' : '#e8392b' }); });
  const DR = [33.4, 33.75, 34.1, 34.45];
  DR.forEach((ti, i) => { const p = drop(i, ti); if (p > 0) paper(180 + i * 240, lerp(-200, 980 + hash(i) * 120, p), hash(i + 2) * 2, 1.6, { crumpled: true }); });
  // the clutter keeps coming: phone, the big book, the calculator
  const p1 = eo(seg(t, 34.7, 35.0)), p2 = eo(seg(t, 35.0, 35.3)), p3 = eo(seg(t, 35.3, 35.6));
  if (p1 > 0) phone(lerp(-200, 230, p1), 1300, .3, 1.4);
  if (p2 > 0) bigBook(lerp(1300, 760, p2), 1260, -.2, 1.4);
  if (p3 > 0) calculator(lerp(540, 520, p3), lerp(-200, 1250, p3), .4, .6);
  // the boy's hand slides off the edge
  hand(lerp(560, 1120, squeeze), lerp(1600, 1700, squeeze), -1.2, 30, C.skin, {});
  const cnt = t < 33.3 ? `ВАРИАНТЫ: ${ANS.filter(a => t > a[1]).length}` : t < 34.6 ? `ЧЕРНОВИКИ: ${DR.filter(d => t > d).length}` : t < 35.7 ? 'СВОБОДНОЕ МЕСТО: …' : 'СВОБОДНОЕ МЕСТО: 0';
  tag(cnt, 31.6, t, { y: 150, size: 34, hold: 6 });
});
// 10 — meanwhile the child has figured it out
shot(37.2, 41.0, (t) => {
  const tq = q12(t);
  cam(520, 1250, lerp(1.25, 1.45, seg(t, 37.2, 41.0)));
  bridgeSet(t);
  // legs of the adults on the left, just out of focus
  dad({ x: 140, y: 1720, s: 1.0, t: tq, noLegs: false, look: [-1, -.5], lid: 0, brow: .7, mouth: { o: .3 + .2 * Math.abs(Math.sin(tq * 8)) } });
  boy({ x: 640, y: 1560, s: 1.0, t: tq, look: [0, .8], lid: .55, legL: [-30, -20], legR: [40, -20], mouth: { sm: t > 39.8 ? .4 : -.1 },
    armR: { h: [30, 110], bend: 20 }, armL: { h: [-20, 110], bend: -20 } });
  const done = t > 39.8;
  paper(660, 1460, -.1, .9, { txt: done ? '56' : '', tick: done && t > 40.1, ink: '#33427a' });
  pencil(700 + Math.sin(tq * 18) * (done ? 0 : 10), 1420, -.8, .7);
});
// 11 — but the adults haven't finished helping
shot(41.0, 45.5, (t) => {
  const tq = q12(t);
  cam(540, 1050, lerp(1.1, 1.0, eio(seg(t, 41.0, 45.5))));
  bridgeSet(t, { alarm: 1 });
  const talk = (ph) => .25 + .35 * Math.abs(Math.sin(tq * 9 + ph));
  gran({ x: 170, y: 1650, s: .95, t: tq, nerv: .3, look: [1, 0], brow: -1, mouth: { o: talk(0), sm: -.5 }, armR: { h: [90, -60], bend: -40, point: true } });
  dad({ x: 420, y: 1720, s: .95, t: tq, nerv: .5, look: [-1, 0], brow: .9, lid: 0, mouth: { o: talk(1), sm: -.4 }, sweat: t * 1.4, armR: { h: [40, -150], bend: -30 }, armL: { h: [-60, -120], bend: 30 } });
  mom({ x: 680, y: 1680, s: .95, face: -1, t: tq, nerv: .3, look: [1, 0], brow: -.6, mouth: { o: talk(2), sm: -.3 }, armR: { h: [180, -20], point: true, bend: -30 } });
  console_(470, 1330, 780, { t, nbGlow: .8 });
  const up = eo(seg(t, 42.0, 42.6));
  boy({ x: 930, y: 1500, s: 1.0, t: tq, face: -1, look: [1, -.3], lid: .55, mouth: { sm: -.2 }, armR: { h: [40, lerp(110, -150, up)], bend: -20 }, holdR: (hp) => paper(hp[0], hp[1] - 80, .1, .6, { txt: '56', tick: true }) });
});
// 12 — help is useful… unless it becomes a full takeover
shot(45.5, 52.2, (t) => {
  const tq = q12(t);
  if (t < 50.2) {
    cam(540, 1000, lerp(1.0, 1.15, eio(seg(t, 45.5, 50.2))));
    bridgeSet(t, { alarm: t > 48.2 ? 1 : 0 });
    // the steering wheel, three pairs of hands on it
    const turn = Math.sin(tq * 3) * .4 * seg(t, 48.2, 49);
    gran({ x: 220, y: 1700, s: 1.0, t: tq, nerv: .4, look: [1, .3], brow: -1, mouth: { o: .3, sm: -.5 }, armR: { h: [200, -40], bend: -30, fist: true } });
    mom({ x: 860, y: 1700, s: 1.0, face: -1, t: tq, nerv: .4, look: [1, .3], brow: -.6, mouth: { o: .3 }, armR: { h: [200, -10], bend: -30, fist: true } });
    dad({ x: 540, y: 1780, s: 1.0, t: tq, nerv: .5, look: [0, .3], lid: 0, brow: .9, mouth: { o: .5 }, sweat: t * 1.3, armR: { h: [150, 120], bend: -30, fist: true }, armL: { h: [-150, 120], bend: 30, fist: true } });
    push(); translate(540, 1330); rotate(turn); scale(.85);
    shape(ell(0, 0, 230, 230, 60), { fill: null, lw: 26, line: INK });
    shape(ell(0, 0, 230, 230, 60), { fill: null, lw: 14, line: BRIDGE.gold });
    for (let k = 0; k < 3; k++) { const a = k / 3 * TAU + Math.PI / 2; stroke([[0, 0], [Math.cos(a) * 220, Math.sin(a) * 220]], 18); }
    shape(ell(0, 0, 50, 50, 24), { fill: BRIDGE.gold, lw: 7 });
    pop();
    console_(540, 1500, 980, { t, nb: false });
    if (t > 48.2) {
      const p = clamp(seg(t, 48.4, 50.0));
      tag(`ЗАХВАТ УПРАВЛЕНИЯ ${Math.round(p * 100)}%`, 48.2, t, { y: 160, size: 32, col: '#ff6a7a' });
    }
  } else {
    const sh = shakeAt(t, 50.55, 22, .6);
    cam(560, 760, 2.6, { shake: Math.abs(sh), t });
    bridgeSet(t, { alarm: 1 });
    boy({ x: 560, y: 1300, s: 1.4, t: tq, look: [0, 0], lid: .6, mouth: { sm: -.3 }, brow: -.2 });
    tag('ЗАХВАТ УПРАВЛЕНИЯ 100%', 0, t, { y: 160, size: 32, col: '#ff6a7a' });
  }
});
// 13 — the boy closes the notebook: the portal collapses
shot(52.2, 55.0, (t) => {
  const tq = q12(t);
  const CLOSE = 53.6;
  const suck = ei(seg(t, CLOSE, 54.5));
  reset();
  cam(540 , 1150 , lerp(1.25, 1.25, 0));
  if (suck > 0) { reset(); translate(W / 2, H / 2 + 200); scale(1 - suck * .98); rotate(suck * 5); translate(-W / 2, -H / 2 - 200); translate(W / 2, H / 2); scale(1.25); translate(-540, -1150); }
  bridgeSet(t);
  gran({ x: 140, y: 1680, s: 1.0, t: tq, look: [1, .3], brow: t > CLOSE ? .9 : -.8, lid: t > CLOSE ? 0 : .3, mouth: { o: t > CLOSE ? .6 : .2 } });
  mom({ x: 940, y: 1680, s: 1.0, face: -1, t: tq, look: [1, .3], brow: t > CLOSE ? .9 : -.4, lid: 0, mouth: { o: t > CLOSE ? .6 : .2 } });
  dad({ x: 300, y: 1760, s: 1.0, t: tq, look: [1, .2], brow: .9, lid: 0, mouth: { o: t > CLOSE ? .7 : .3 } });
  const reach = eo(seg(t, 52.4, 53.4));
  boy({ x: 680, y: 1560, s: 1.15, t: tq, face: -1, look: [1, .6], lid: .5, mouth: { sm: .1 }, armR: { h: [lerp(40, 170, reach), lerp(110, 40, reach)], bend: -10 } });
  console_(540, 1330, 900, { t, nbGlow: t < CLOSE ? .8 : 0, open: t < CLOSE ? 1 : 0 });
  if (t >= CLOSE && t < CLOSE + .2) { reset(); g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = 'rgba(125,255,196,.6)'; g.fillRect(0, 0, W, H); }
  if (suck > 0) { reset(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'destination-over'; g.fillStyle = MINT; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'source-over'; }
  if (t > 54.4) swirlOverlay(eo(seg(t, 54.4, 55.0)) * .0001, t);
});
// 14 — and sometimes just step back from his notebook
shot(55.0, 60.81, (t) => {
  const tq = q12(t);
  cam(540, lerp(1040, 900, eio(seg(t, 55.0, 60.8))), lerp(1.0, 1.35, eio(seg(t, 55.5, 60.8))));
  room(BEIGE, { night: false });
  const back1 = eio(seg(t, 55.7, 56.4)), back2 = eio(seg(t, 56.5, 57.2)), back3 = eio(seg(t, 57.3, 58.0));
  gran({ x: lerp(330, 60, back1), y: 1500, s: lerp(.95, .85, back1), t: tq, look: [1, .5], brow: .3, lid: .4, mouth: { sm: .2 } });
  mom({ x: lerp(760, 1030, back2), y: 1500, s: lerp(.95, .85, back2), face: -1, t: tq, look: [1, .5], brow: .3, mouth: { sm: .3 } });
  dad({ x: lerp(560, 240, back3), y: 1520, s: lerp(1.0, .88, back3), t: tq, look: [1, .5], brow: .4, mouth: { sm: .2 }, armR: { h: [0, 120], bend: 10 }, armL: { h: [-40, 160], bend: -10 } });
  const smile = eo(seg(t, 59.3, 59.9));
  boy({ x: 560, y: 1340, s: 1.4, t: tq, look: [0, .8], lid: lerp(.5, .35, smile), mouth: { sm: lerp(-.1, .7, smile) }, armR: { h: [50, 150], bend: 10 }, armL: { h: [-40, 150], bend: -10 } });
  desk(BEIGE); lamp(900, 1200);
  deskBook(560, 1215, .9, { t, solved: t > 58.6 ? 1 : 0 });
  pencil(650 + Math.sin(tq * 14) * 8, 1180, -.9, .8);
});

// ===================== EVENTS (foley) =====================
window.EV = [
  ...[0.3, 0.63, 0.97, 1.3, 1.63, 1.97, 2.3].map(t => ({ t, type: 'tap' })),
  { t: 5.3, type: 'blip' }, { t: 6.6, type: 'antenna' }, { t: 8.5, type: 'blip' }, { t: 10.1, type: 'whip' },
  { t: 12.3, type: 'blip' }, { t: 12.5, type: 'door' }, { t: 17.3, type: 'slam' }, { t: 18.0, type: 'blink' },
  { t: 19.0, type: 'hum' }, { t: 20.2, type: 'portal' }, { t: 21.3, type: 'swirl' }, { t: 22.1, type: 'type', d: .6 },
  { t: 23.6, type: 'type', d: 1.5 }, { t: 25.9, type: 'type', d: 2.4 }, { t: 30.5, type: 'button' }, { t: 30.55, type: 'papers' },
  ...[31.7, 32.2, 32.7].map(t => ({ t, type: 'paper' })), ...[33.4, 33.75, 34.1, 34.45].map(t => ({ t, type: 'crumple' })),
  { t: 34.7, type: 'thud' }, { t: 35.0, type: 'thud' }, { t: 35.3, type: 'thud' }, { t: 35.6, type: 'slide' },
  { t: 40.1, type: 'ding' }, { t: 41.0, type: 'alarm', d: 4.4 }, { t: 48.2, type: 'alarm', d: 2.0 }, { t: 50.55, type: 'sting' },
  { t: 53.6, type: 'close' }, { t: 53.7, type: 'suck' }, { t: 54.4, type: 'swirl' },
  { t: 55.7, type: 'step' }, { t: 56.5, type: 'step' }, { t: 57.3, type: 'step' },
];

window.render = (t) => {
  frame(t);
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  const s = SHOTS.find(s => t >= s.t0 && t < s.t1) || SHOTS[SHOTS.length - 1];
  s.fn(t);
};
document.fonts.load('900 40px "Nunito"').then(() => document.fonts.load('40px PS2P')).then(() => { window.render(0); window.READY = true; });
