// chars.js — the family as a child would draw them: round heads, tube limbs, mitten hands, dot eyes, pink cheeks.
// person(C, o): C = rig group; o = {x, y (feet), s, who, armL, armR (lists of local points from the shoulder), expr, look, dr (outline 0..1), cf (colour 0..1), seed, hold}
import { line, fill, dab, ellipse, handCircle, xf, smooth, text, sx, sy, CAM } from './crayon.js';
import { part, tube, curve } from './rig.js';
import { clamp, hash } from '/core/lib.js';

export const K = {
  ink: '#2b2f5c', teal: '#2aa198', mustard: '#e2a62a', coral: '#f0705a', plum: '#8a4a8c', peach: '#f4c3a0', pink: '#ee8ea4',
  brown: '#7a4b31', grey: '#b9b3bf', red: '#d93a33', green: '#4a9a3c', blue: '#6fa8dc', navy: '#33427a', white: '#fbfaf4',
};
const LW = 7;
const lo = (seed, x = {}) => ({ w: LW, seed, col: K.ink, ...x });
const SPEC = {
  boy:  { headR: 66, headY: -300, sh: -228, hip: -92, bodyW: [58, 74], top: K.teal, legs: K.navy, hair: K.brown, skin: K.peach },
  dad:  { headR: 64, headY: -470, sh: -394, hip: -170, bodyW: [62, 70], top: K.mustard, legs: K.brown, hair: K.brown, skin: K.peach },
  mom:  { headR: 62, headY: -446, sh: -372, hip: -190, bodyW: [52, 60], top: K.coral, legs: K.peach, hair: K.brown, skin: K.peach, skirt: K.navy },
  gran: { headR: 66, headY: -420, sh: -344, hip: -130, bodyW: [72, 104], top: K.plum, legs: K.peach, hair: K.grey, skin: K.peach },
};

export function person(C, o) {
  const S = SPEC[o.who], sd = o.seed || 100, s = o.s || 1;
  const T = pts => xf(pts, { x: o.x, y: o.y, s, r: o.r || 0, sx: o.flip ? -1 : 1 });
  const dr = o.dr ?? 1, cf = o.cf ?? 1;
  const D = (i, n = 8) => clamp(dr * n - i);          // staged draw-on: parts appear one after another
  const F = (i, n = 8) => clamp(cf * n - i);
  const P = (poly, fo, l, i, extra = {}) => { if (D(i) <= 0) return; part(C, T(poly), fo && F(i) > 0 ? { ...fo, draw: F(i) } : null, l ? { ...l, draw: D(i) } : null, extra); };
  const fl = (col, k, x = {}) => ({ col, p: .78, gap: 9, w: 11, ang: .6 + (k % 3) * .25, seed: sd + k, over: 5, ...x });

  // legs
  const legW = o.who === 'gran' ? 26 : 24;
  for (const [i, sx] of [[0, -1], [1, 1]]) {
    const L = o.legs?.[i] || [[sx * 22, S.hip + 10], [sx * 26, -16]];
    P(tube(L, legW, legW - 2), fl(S.legs, 1 + i), lo(sd + 1 + i), 0);
    P(smooth([[L[1][0] - 22, -10], [L[1][0] + 24 * (sx), -14], [L[1][0] + 30 * sx, 2], [L[1][0] - 18, 6]], 4), fl(K.ink, 3 + i, { p: .9 }), lo(sd + 3 + i, { w: 5 }), 0);
  }
  // body
  const [w0, w1] = S.bodyW;
  let body;
  if (o.who === 'mom') {
    body = smooth([[-w0, S.sh + 8], [0, S.sh - 6], [w0, S.sh + 8], [w1, S.hip], [-w1, S.hip]], 4);
    P(smooth([[-w1 + 6, S.hip - 6], [w1 - 6, S.hip - 6], [w1 + 50, S.hip + 110], [-w1 - 50, S.hip + 110]], 3), fl(S.skirt, 5), lo(sd + 5), 1);
  } else if (o.who === 'boy') {
    body = smooth([[-w0, S.sh + 10], [0, S.sh - 4], [w0, S.sh + 10], [w1 + 6, S.hip + 30], [0, S.hip + 40], [-w1 - 6, S.hip + 30]], 4);   // long hoodie
  } else body = smooth([[-w0, S.sh + 10], [0, S.sh - 4], [w0, S.sh + 10], [w1, S.hip + 10], [-w1, S.hip + 10]], 4);
  P(body, fl(S.top, 6, { cross: o.who !== 'boy' }), lo(sd + 6), 1);
  if (o.who === 'boy') { if (D(2) > 0) line(C.l, T(smooth([[-34, S.hip - 30], [34, S.hip - 30], [26, S.hip + 4], [-26, S.hip + 4]], 3)), lo(sd + 61, { w: 4, draw: D(2) })); }
  if (o.who === 'dad') for (let k = 0; k < 2; k++) if (F(2) > 0) line(C.f, T([[-w0 + 4, S.sh + 70 + k * 60], [w0 + 4, S.sh + 70 + k * 60]]), { col: '#b97d12', w: 8, p: .8, seed: sd + 70 + k });
  if (o.who === 'gran') for (let k = 0; k < 9; k++) if (F(2) > 0) dab(C.f, ...T([[-60 + hash(k + sd) * 120, S.sh + 40 + hash(k * 3 + sd) * 150]])[0], 7 * s, { col: K.pink, seed: sd + 80 + k });
  // arms
  const arm = (pts, i) => {
    const sh = [i ? w0 - 10 : -w0 + 10, S.sh + 20];
    const A = (pts || [[i ? 40 : -40, 90], [i ? 54 : -54, 180]]).map(([x, y]) => [sh[0] + x, sh[1] + y]);
    P(tube(curve([sh, ...A], 4), 26, 22), fl(S.top, 10 + i), lo(sd + 10 + i), 2, {});
    const hd = A[A.length - 1];
    if (o.hold && o.hold[i] && D(3) > 0) o.hold[i](T([hd])[0], s);
    P(handCircle(hd[0], hd[1], 17, sd + 12 + i, 0, 18), fl(S.skin, 12 + i), lo(sd + 12 + i, { w: 5 }), 3);
  };
  arm(o.armL, 0); arm(o.armR, 1);
  // head
  const hy = S.headY, R = S.headR;
  if (o.who === 'mom') P(handCircle(30, hy - R - 10, 34, sd + 20, 0, 24), fl(S.hair, 20), lo(sd + 20), 4);   // bun
  if (o.who === 'mom' && D(4) > 0) line(C.l, T([[4, hy - R - 54], [62, hy - R + 26]]), { col: '#e8a020', w: 9, seed: sd + 21, draw: D(4) });   // pencil in the bun
  if (o.who === 'gran') for (let k = 0; k < 7; k++) { const a = Math.PI * (1.05 + k * .15); P(handCircle(Math.cos(a) * R * 1.02, hy + Math.sin(a) * R * 1.02 - 6, 24, sd + 22 + k, 0, 18), fl(S.hair, 22 + k, { p: .7 }), lo(sd + 22 + k, { w: 5 }), 4); }
  P(handCircle(0, hy, R, sd + 30, 0, 44), fl(S.skin, 30, { p: .55 }), lo(sd + 30), 4);
  // hair
  if (o.who === 'boy') {
    P(smooth([[-R, hy - 4], [-R + 6, hy - 46], [-20, hy - R - 6], [24, hy - R - 8], [R - 4, hy - 44], [R, hy - 6], [36, hy - 34], [0, hy - 26], [-38, hy - 34]], 4), fl(S.hair, 32, { p: .85 }), lo(sd + 32), 5);
    if (D(5) > 0) line(C.l, T(curve([[4, hy - R], [-6, hy - R - 46], [20, hy - R - 70], [34, hy - R - 50]])), lo(sd + 33, { draw: D(5) }));
  } else if (o.who === 'dad') {
    P(smooth([[-R, hy + 4], [-R - 6, hy - 40], [-30, hy - R - 12], [30, hy - R - 14], [R + 6, hy - 40], [R, hy + 4], [40, hy - 30], [-40, hy - 30]], 4), fl(S.hair, 32, { p: .85 }), lo(sd + 32), 5);
  } else if (o.who === 'mom') {
    P(smooth([[-R - 8, hy + 50], [-R - 10, hy - 30], [-24, hy - R - 8], [30, hy - R - 8], [R + 10, hy - 30], [R + 8, hy + 50], [R - 10, hy + 10], [30, hy - 36], [-30, hy - 36], [-R + 10, hy + 10]], 4), fl(S.hair, 32, { p: .85 }), lo(sd + 32), 5);
  }
  // face
  if (D(6) > 0) face(C, T, o, hy, R, sd, s, D(6));
  pop();
  function pop() {}
}

function face(C, T, o, hy, R, sd, s, d) {
  const ex = o.expr || 'calm', look = o.look || [0, 0];
  const eyes = [[-24, hy - 2], [24, hy - 2]];
  eyes.forEach(([x, y], i) => {
    const px = x + look[0] * 6, py = y + look[1] * 5;
    if (ex === 'happyclosed' || o.blink) line(C.l, T([[x - 10, y], [x, y - 7], [x + 10, y]]), lo(sd + 40 + i, { w: 5, draw: d }));
    else {
      dab(C.l, ...T([[px, py]])[0], (ex === 'surprised' ? 9 : 7.5) * s, { col: K.ink, p: 1, seed: sd + 40 + i, gap: 3, w: 5 });
      if (ex === 'sleepy') line(C.l, T([[x - 13, y - 6], [x + 13, y - 6]]), lo(sd + 44 + i, { w: 5, draw: d }));
    }
    // brows
    const b = ex === 'angry' ? (i ? -1 : 1) : ex === 'worried' ? (i ? 1 : -1) : 0;
    if (b) line(C.l, T([[x - 13, y - 22 - b * 5], [x + 13, y - 22 + b * 5]]), lo(sd + 46 + i, { w: 5, draw: d }));
  });
  if (o.who === 'dad' || o.who === 'gran') for (const [x, y] of eyes) line(C.l, T(handCircle(x, y, 20, sd + 48 + x, .05, 24)), lo(sd + 48 + x, { w: 4.5, draw: d }));
  if (o.who === 'dad' || o.who === 'gran') line(C.l, T([[-4, hy - 4], [4, hy - 4]]), lo(sd + 50, { w: 4.5, draw: d }));
  if (o.who === 'dad') for (let k = 0; k < 10; k++) dab(C.f, ...T([[-34 + hash(k) * 68, hy + 34 + hash(k + 4) * 22]])[0], 2.5 * s, { col: K.brown, seed: sd + 90 + k, gap: 2, w: 3 });
  // cheeks
  for (const sx of [-1, 1]) dab(C.f, ...T([[sx * 40, hy + 22]])[0], 11 * s, { col: K.pink, p: .75, seed: sd + 52 + sx, sq: .7 });
  // mouth
  const m = o.mouth ?? (ex === 'angry' ? 'frown' : ex === 'worried' ? 'wavy' : ex === 'talk' ? 'open' : 'smile');
  const my = hy + 32;
  if (m === 'smile') line(C.l, T(curve([[-16, my - 3], [0, my + 8], [16, my - 3]])), lo(sd + 55, { w: 5, draw: d }));
  else if (m === 'big') line(C.l, T(curve([[-22, my - 6], [0, my + 14], [22, my - 6]])), lo(sd + 55, { w: 6, draw: d }));
  else if (m === 'frown') line(C.l, T(curve([[-15, my + 6], [0, my - 4], [15, my + 6]])), lo(sd + 55, { w: 5, draw: d }));
  else if (m === 'flat') line(C.l, T([[-12, my + 2], [12, my + 2]]), lo(sd + 55, { w: 5, draw: d }));
  else if (m === 'wavy') line(C.l, T([[-16, my + 2], [-8, my - 3], [0, my + 2], [8, my - 3], [16, my + 2]]), lo(sd + 55, { w: 4.5, draw: d }));
  else if (m === 'open') { const T2 = T(handCircle(0, my + 4, 11, sd + 56, 0, 16).map(([x, y]) => [x, my + 4 + (y - my - 4) * (o.mo ?? 1)])); fill(C.f, T2, { col: '#8a2a3a', p: .9, gap: 3, w: 5, seed: sd + 57 }); line(C.l, [...T2, T2[1]], lo(sd + 56, { w: 4.5 })); }
}

// —— props ——
export function deskDraw(L, LF, { x = 540, y = 1180, w = 420, dr = 1, cf = 1, seed = 500, col = K.brown } = {}) {
  const top = [[x - w / 2, y], [x + w / 2, y], [x + w / 2 + 30, y + 46], [x - w / 2 - 30, y + 46]];
  fill(LF, top, { col, p: .7, gap: 10, w: 12, seed, draw: cf, ang: .2 });
  line(L, [...top, top[1]], { col: K.ink, w: 7, seed, draw: dr });
  for (const sx of [-1, 1]) line(L, [[x + sx * (w / 2 + 6), y + 46], [x + sx * (w / 2 - 4), y + 300]], { col: K.ink, w: 8, seed: seed + 3 + sx, draw: dr });
}
export function notebookDraw(L, LF, x, y, s = 1, { seed = 520, dr = 1 } = {}) {
  const p = [[x - 60 * s, y - 14 * s], [x + 60 * s, y - 14 * s], [x + 70 * s, y + 14 * s], [x - 70 * s, y + 14 * s]];
  fill(LF, p, { col: K.white, p: .9, gap: 6, w: 8, seed });
  line(L, [...p, p[1]], { col: K.ink, w: 5, seed, draw: dr });
  line(L, [[x, y - 14 * s], [x, y + 14 * s]], { col: K.ink, w: 4, seed: seed + 1, draw: dr });
}
export function laptop(C, [x, y], s = 1, sd = 600) {
  const scr = [[x - 70 * s, y - 120 * s], [x + 70 * s, y - 120 * s], [x + 70 * s, y - 10 * s], [x - 70 * s, y - 10 * s]];
  part(C, scr, { col: K.blue, p: .8, gap: 7, w: 9, seed: sd }, lo(sd));
  part(C, [[x - 90 * s, y - 10 * s], [x + 90 * s, y - 10 * s], [x + 100 * s, y + 10 * s], [x - 100 * s, y + 10 * s]], { col: K.grey, p: .8, gap: 6, w: 8, seed: sd + 1 }, lo(sd + 1));
}
export function phoneDraw(C, [x, y], s = 1, sd = 620) {
  part(C, [[x - 26 * s, y - 50 * s], [x + 26 * s, y - 50 * s], [x + 26 * s, y + 46 * s], [x - 26 * s, y + 46 * s]], { col: K.blue, p: .85, gap: 6, w: 8, seed: sd }, lo(sd, { w: 6 }));
}
export function bookDraw(C, [x, y], s = 1, sd = 640) {
  part(C, [[x - 70 * s, y - 46 * s], [x + 70 * s, y - 46 * s], [x + 70 * s, y + 46 * s], [x - 70 * s, y + 46 * s]], { col: '#8a3a2a', p: .85, gap: 7, w: 9, seed: sd, cross: true }, lo(sd));
  text(C.l, '1974', sx(x), sy(y + 12 * s), { size: 36 * s * CAM.s, font: 'Neucha', col: K.white, seed: sd });
}
export function eraserDraw(C, [x, y], s = 1, sd = 660, r = 0) {
  const p = xf([[-60, -34], [60, -34], [60, 34], [-60, 34]], { x, y, s, r });
  part(C, p, { col: K.pink, p: .85, gap: 6, w: 9, seed: sd }, lo(sd));
  part(C, xf([[-60, -34], [-10, -34], [-10, 34], [-60, 34]], { x, y, s, r }), { col: K.blue, p: .85, gap: 6, w: 9, seed: sd + 1 }, lo(sd + 1));
}
