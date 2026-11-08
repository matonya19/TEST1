// chars.js — the family: Boy (deadpan), Dad, Mom, Grandma. Origin at the feet, y down.
// Common pose params P: {x,y,s,face,lean,bob,sq, lid,look,brow,mouth:{o,w,sm,skew},blink, armR:{h:[dx,dy],bend,fist}, armL, holdR, holdL, t, nerv, sweat, turn}
import { clamp, lerp, hash, TAU } from '/core/lib.js';
import { INK, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, spline, rr, rect, noodle, quad, dot, text } from './toon.js';

export const C = {
  white: '#ffffff', mouthIn: '#4a1a2a', tongue: '#e8637a', sweat: '#bfe9ff',
  skin: '#f4c7a1', skinS: '#dca37c', skinB: '#e9b48c',
  hoodie: '#2fb7a8', hoodieS: '#1e8579', boyHair: '#5a3524', jeans: '#3e4a6b',
  dadTop: '#e3a72f', dadTopS: '#b77f17', dadHair: '#3b2a22', pants: '#6b5a4a', pantsS: '#4f4236', stub: '#e2b590',
  momTop: '#ff7a6b', momTopS: '#d9564a', momHair: '#7a3e2a', skirt: '#2d3a6e', skirtS: '#1f2a52',
  granTop: '#8e4a8a', granTopS: '#6a3266', granHair: '#d9d4de', granHairS: '#b2abba', granSkirt: '#5b4a6a',
  shoe: '#2a2230', glass: '#2a2230',
};

// —— face parts ——
export function eye(cx, cy, rx, ry, { lid = 0, look = [0, 0], pupil = 4.5, skin = C.skin, closed = false, lw = 6, jitter = 0, lower = 0 } = {}) {
  if (closed) { stroke(arc(cx, cy + ry * .15, rx * .8, ry * .45, Math.PI * .1, Math.PI * .9, 14), lw); return; }
  shape(ell(cx, cy, rx, ry, 36), {
    fill: C.white, lw, shade: () => {
      dot(cx + look[0] * rx * .55 + jitter, cy + look[1] * ry * .5, pupil);
      if (lid > 0) {
        const yl = cy - ry + lid * 2 * ry;
        fillOnly([[cx - rx * 1.3, cy - ry * 1.4], [cx + rx * 1.3, cy - ry * 1.4], [cx + rx * 1.3, yl], [cx - rx * 1.3, yl + ry * .08]], skin, { boil: .5 });
        stroke([[cx - rx * 1.2, yl + ry * .08], [cx + rx * 1.2, yl]], lw);
      }
      if (lower > 0) { const yb = cy + ry - lower * 2 * ry; fillOnly([[cx - rx * 1.3, yb], [cx + rx * 1.3, yb], [cx + rx * 1.3, cy + ry * 1.4], [cx - rx * 1.3, cy + ry * 1.4]], skin, { boil: .5 }); stroke([[cx - rx * 1.2, yb], [cx + rx * 1.2, yb]], lw * .8); }
    }
  });
}
export function mouth(cx, cy, mw, { o = 0, w = 1, sm = 0, skew = 0, lw = 6, teeth = true } = {}) {
  const hw = mw * w / 2, k = mw * .22, lc = [cx - hw, cy - sm * k + skew * k], rc = [cx + hw, cy - sm * k - skew * k];
  if (o < .07) { stroke(quad(lc, [cx, cy + sm * k * 1.2], rc, 12), lw); return; }
  const h = o * mw * .62;
  const up = quad(lc, [cx, cy - h * .25 + sm * k * .4], rc, 12), dn = quad(rc, [cx, cy + h + sm * k * .6], lc, 14);
  shape([...up, ...dn], {
    fill: C.mouthIn, lw, shade: () => {
      if (teeth && o > .22) fillOnly(rect(cx - hw * 1.2, cy - h, hw * 2.4, h * .32 + 6), C.white, { boil: .3 });
      fillOnly(ell(cx + hw * .15, cy + h * .95, hw * .6, h * .45, 20), C.tongue, { boil: .3 });
    }
  });
}
// brow: b>0 worried/surprised (inner end up), b<0 angry (inner end down)
function brows(ex1, ex2, y, w, b, lw = 8, col = INK) {
  for (const [ex, side] of [[ex1, -1], [ex2, 1]]) {
    const inner = [ex - side * w * .9, y - b * 14], outer = [ex + side * w * .9, y + b * 4 - 4];
    stroke(quad(outer, [ex, y - 8 - Math.abs(b) * 4], inner, 8), lw, { line: col });
  }
}
export function hand(x, y, ang, r = 21, col = C.skin, { fist = false, lw = 6, point = false } = {}) {
  push(); translate(x, y); rotate(ang);
  let pts;
  if (point) pts = spline([[-r * .6, -r * .8], [r * .5, -r * .9], [r * 1.9, -r * .55], [r * 1.95, -r * .15], [r * .9, -r * .05], [r * .8, r * .8], [-r * .5, r * .9], [-r * .9, 0]]);
  else if (fist) pts = spline([[-r * .6, -r * .8], [r * .7, -r * .9], [r * 1.1, -r * .1], [r * .8, r * .8], [-r * .5, r * .9], [-r * .9, 0]]);
  else pts = spline([[-r * .5, -r * .85], [r * .5, -r * 1.05], [r * 1.35, -r * .75], [r * 1.05, -r * .3], [r * 1.5, -r * .1], [r * 1.1, r * .3], [r * 1.35, r * .7], [r * .6, r * .95], [-r * .6, r * .8], [-r * .95, 0]]);
  shape(pts, { fill: col, lw });
  pop();
}
export const sweat = (x, y, s = 1) => shape(spline([[x, y - 16 * s], [x + 9 * s, y + 4 * s], [x, y + 12 * s], [x - 9 * s, y + 4 * s]]), { fill: C.sweat, lw: 5 });

function arm(sh, a, sleeve, sleeveS, skin, wSleeve = 40, wEnd = 34, r = 20, hold = null) {
  const hp = [sh[0] + a.h[0], sh[1] + a.h[1]];
  shape(noodle(sh, hp, a.bend ?? 0, wSleeve, wEnd), { fill: sleeve, lw: 7 });
  const ang = Math.atan2(hp[1] - sh[1], hp[0] - sh[0]);
  shape(ell(hp[0] - Math.cos(ang) * 4, hp[1] - Math.sin(ang) * 4, wEnd * .55, wEnd * .55, 18), { fill: sleeveS, lw: 6 });
  if (hold) hold(hp, ang);
  hand(hp[0], hp[1], ang, r, skin, { fist: a.fist, point: a.point });
  return hp;
}
const jit = (P, amt) => P.nerv ? (hash(Math.floor((P.t || 0) * 12) * 3.3 + amt) - .5) * 8 * P.nerv : 0;

// ===================== BOY =====================
export function boy(P) {
  const f = P.face ?? 1;
  push(); translate(P.x + jit(P, 1), P.y + (P.bob || 0)); scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  if (!P.noLegs) for (const sx of [-1, 1]) {
    const lg = (sx < 0 ? P.legL : P.legR) || [0, 0];
    shape(noodle([sx * 24, -110], [sx * 26 + lg[0], -20 + lg[1]], 0, 30, 28), { fill: C.jeans, lw: 6 });
    shape(spline([[sx * 26 - 26 + lg[0], 2 + lg[1]], [sx * 26 - 20 + lg[0], -26 + lg[1]], [sx * 26 + 16 + lg[0], -26 + lg[1]], [sx * 26 + 34 + lg[0], -4 + lg[1]], [sx * 26 + 30 + lg[0], 6 + lg[1]]]), { fill: C.shoe, lw: 6 });
  }
  push(); rotate(P.lean ?? 0);
  const shB = [-62, -258], shF = [62, -258];
  arm(shB, P.armL || { h: [-22, 110], bend: -14 }, C.hoodie, C.hoodieS, C.skin, 36, 34, 17, P.holdL);
  // oversized hoodie, down to the knees
  shape(spline([[0, -296], [70, -270], [92, -170], [100, -84], [0, -74], [-100, -84], [-92, -170], [-70, -270]]), {
    fill: C.hoodie, lw: 7, shade: () => {
      fillOnly(spline([[30, -300], [110, -260], [120, -80], [60, -70], [70, -180]]), C.hoodieS, { boil: .4 });
      fillOnly(rr(-46, -170, 92, 44, 14), C.hoodieS, { boil: .3 });   // kangaroo pocket
    }
  });
  stroke(rr(-46, -170, 92, 44, 14).slice(0, 15), 5);
  // drawstrings
  stroke([[-16, -280], [-20, -226]], 5); stroke([[16, -280], [20, -230]], 5);
  push(); translate(4, -384); rotate(P.headTilt ?? 0);
  // hood behind head
  shape(spline([[-110, 30], [-104, -60], [0, -118], [104, -60], [110, 30], [60, 90], [-60, 90]]), { fill: C.hoodie, lw: 7, shade: () => fillOnly(ell(60, 0, 70, 120, 20), C.hoodieS, { boil: .3 }) });
  const tr = (P.turn ?? .15) * 18;
  shape(ell(0, 0, 92, 88, 60), { fill: C.skin, lw: 7, shade: () => fillOnly(ell(70, 30, 50, 80, 24), C.skinB, { boil: .3 }) });
  // hair: flat cap of hair + one tall tuft "antenna"
  shape(spline([[-90, -10], [-84, -62], [-30, -96], [40, -96], [88, -58], [92, -10], [60, -40], [10, -52], [-40, -40]]), { fill: C.boyHair, lw: 6 });
  stroke(spline([[10, -94], [4, -140], [26, -168], [44, -150], [30, -138]], false), 6);
  const lid = P.blink ? 1 : (P.lid ?? .42), look = P.look || [0, 0];
  eye(-30 + tr, 4, 30, 32, { lid, look, pupil: 4.5, lower: P.lower || 0 });
  eye(30 + tr, 4, 30, 32, { lid, look, pupil: 4.5, lower: P.lower || 0 });
  brows(-30 + tr, 30 + tr, -40 - (P.brow ?? 0) * 4, 22, P.brow ?? 0, 6);
  shape(ell(4 + tr * 1.4, 40, 10, 8, 12), { fill: C.skinS, lw: 5 });
  const m = P.mouth || {};
  mouth(4 + tr, 66, 40, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? -.1, skew: m.skew || 0, lw: 5 });
  for (let i = 0; i < 5; i++) dot(-58 + tr + hash(i) * 18, 34 + hash(i + 9) * 12, 2, '#d08a6a');
  pop();
  arm(shF, P.armR || { h: [22, 110], bend: 14 }, C.hoodie, C.hoodieS, C.skin, 36, 34, 17, P.holdR);
  pop();
  if (P.sweat != null) sweat(110, -460 + (P.sweat % 1) * 30, 1);
  pop();
}

// ===================== DAD =====================
export function dad(P) {
  const f = P.face ?? 1;
  push(); translate(P.x + jit(P, 2), P.y + (P.bob || 0)); scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  if (!P.noLegs) for (const sx of [-1, 1]) {
    const lg = (sx < 0 ? P.legL : P.legR) || [0, 0];
    shape(noodle([sx * 34, -380], [sx * 34 + lg[0], -24 + lg[1]], 0, 52, 44), { fill: C.pants, lw: 7, shade: () => fillOnly(rect(sx > 0 ? 20 : -200, -400, 200, 400), C.pantsS, { boil: .3 }) });
    shape(spline([[sx * 34 - 34 + lg[0], 2 + lg[1]], [sx * 34 - 28 + lg[0], -30 + lg[1]], [sx * 34 + 20 + lg[0], -30 + lg[1]], [sx * 34 + 54 + lg[0], -6 + lg[1]], [sx * 34 + 48 + lg[0], 6 + lg[1]]]), { fill: C.shoe, lw: 7 });
  }
  push(); rotate(P.lean ?? 0);
  const shB = [-74, -600], shF = [74, -600];
  arm(shB, P.armL || { h: [-20, 190], bend: -16 }, C.dadTop, C.dadTopS, C.skin, 42, 36, 21, P.holdL);
  shape(spline([[0, -640], [80, -616], [98, -500], [92, -390], [0, -370], [-92, -390], [-98, -500], [-80, -616]]), {
    fill: C.dadTop, lw: 7, shade: () => {
      fillOnly(spline([[30, -650], [120, -600], [120, -360], [50, -360], [70, -500]]), C.dadTopS, { boil: .4 });
      for (let k = 0; k < 3; k++) stroke([[-90, -560 + k * 60], [92, -560 + k * 60]], 4, { line: C.dadTopS });
    }
  });
  stroke(arc(0, -632, 36, 22, .1, Math.PI - .1, 12), 6);   // collar
  shape(noodle([0, -636], [0, -672], 0, 34, 34), { fill: C.skin, lw: 6 });
  push(); translate(6, -768); rotate(P.headTilt ?? 0);
  const tr = (P.turn ?? .15) * 18;
  // long face
  shape(spline([[0, -112], [62, -96], [76, -20], [72, 60], [44, 112], [0, 124], [-44, 112], [-72, 60], [-76, -20], [-62, -96]]), {
    fill: C.skin, lw: 7, shade: () => {
      fillOnly(spline([[-80, 40], [0, 70], [80, 40], [80, 140], [-80, 140]]), C.stub, { boil: .3 });
      fillOnly(ell(64, 10, 30, 110, 20), C.skinB, { boil: .3 });
    }
  });
  for (const sx of [-1, 1]) shape(ell(sx * 78, 0, 14, 22, 14), { fill: C.skin, lw: 6 });
  // messy hair
  shape(spline([[-78, -20], [-86, -90], [-40, -140], [20, -150], [70, -128], [90, -70], [80, -24], [56, -84], [0, -96], [-50, -80]]), { fill: C.dadHair, lw: 6 });
  const lid = P.blink ? 1 : (P.lid ?? .1), look = P.look || [0, 0];
  eye(-28 + tr, -6, 26, 30, { lid, look, pupil: 4, jitter: jit(P, 7) * .4 });
  eye(28 + tr, -6, 26, 30, { lid, look, pupil: 4, jitter: jit(P, 7) * .4 });
  // rectangular glasses
  for (const ex of [-28 + tr, 28 + tr]) shape(rr(ex - 32, -38, 64, 58, 8), { line: C.glass, lw: 7, stroke: true });
  stroke([[-2 + tr, -18], [2 + tr, -18]], 7);
  brows(-28 + tr, 28 + tr, -54, 24, P.brow ?? .4, 8);
  shape(spline([[tr, 10], [14 + tr, 40], [6 + tr, 52], [-8 + tr, 48]]), { fill: C.skinS, lw: 5 });
  const m = P.mouth || {};
  mouth(4 + tr, 84, 50, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? 0, skew: m.skew || 0, lw: 6 });
  pop();
  arm(shF, P.armR || { h: [20, 190], bend: 16 }, C.dadTop, C.dadTopS, C.skin, 42, 36, 21, P.holdR);
  pop();
  if (P.sweat != null) { const u = P.sweat % 1; sweat(-100, -900 + u * 40, 1.2); sweat(110, -880 + ((u + .5) % 1) * 40, 1); }
  pop();
}

// ===================== MOM =====================
export function mom(P) {
  const f = P.face ?? 1;
  push(); translate(P.x + jit(P, 3), P.y + (P.bob || 0)); scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  if (!P.noLegs) for (const sx of [-1, 1]) {
    shape(noodle([sx * 26, -200], [sx * 28, -20], 0, 30, 26), { fill: C.skin, lw: 6 });
    shape(spline([[sx * 28 - 24, 2], [sx * 28 - 18, -24], [sx * 28 + 16, -24], [sx * 28 + 40, -4], [sx * 28 + 34, 6]]), { fill: C.momTopS, lw: 6 });
  }
  // A-line skirt
  shape([[-60, -380], [60, -380], [120, -180], [-120, -180]], { fill: C.skirt, lw: 7, shade: () => fillOnly([[20, -390], [70, -390], [140, -170], [60, -170]], C.skirtS, { boil: .3 }) });
  push(); rotate(P.lean ?? 0);
  const shB = [-64, -560], shF = [64, -560];
  arm(shB, P.armL || { h: [-18, 170], bend: -14 }, C.momTop, C.momTopS, C.skin, 36, 30, 18, P.holdL);
  shape(spline([[0, -592], [70, -572], [84, -470], [70, -376], [0, -366], [-70, -376], [-84, -470], [-70, -572]]), {
    fill: C.momTop, lw: 7, shade: () => {
      fillOnly(spline([[30, -600], [100, -560], [100, -360], [44, -360], [60, -470]]), C.momTopS, { boil: .4 });
      fillOnly([[-24, -596], [24, -596], [0, -520]], C.skin, { boil: .3 });
    }
  });
  stroke([[0, -520], [0, -372]], 5);
  for (let k = 0; k < 3; k++) dot(10, -500 + k * 40, 5);
  push(); translate(4, -680); rotate(P.headTilt ?? 0);
  const tr = (P.turn ?? .15) * 18;
  // bun with a pencil stuck in it
  push(); translate(20, -110); rotate(-.5);
  shape(rr(-8, -70, 16, 140, 4), { fill: '#ffcf3f', lw: 5 }); shape([[-8, 70], [8, 70], [0, 92]], { fill: C.skin, lw: 5 });
  pop();
  shape(ell(10, -104, 54, 46, 30), { fill: C.momHair, lw: 7 });
  shape(spline([[-84, 50], [-90, -40], [-40, -96], [40, -96], [90, -40], [84, 50], [60, 10], [0, -40], [-60, 10]]), { fill: C.momHair, lw: 7 });
  shape(ell(0, 0, 80, 86, 50), { fill: C.skin, lw: 7, shade: () => fillOnly(ell(62, 20, 40, 90, 20), C.skinB, { boil: .3 }) });
  shape(spline([[-80, -10], [-60, -78], [0, -96], [64, -76], [84, -14], [40, -54], [-20, -56]]), { fill: C.momHair, lw: 6 });
  const lid = P.blink ? 1 : (P.lid ?? .15), look = P.look || [0, 0];
  eye(-26 + tr, 6, 26, 30, { lid, look, pupil: 4 });
  eye(26 + tr, 6, 26, 30, { lid, look, pupil: 4 });
  for (const [ex, s] of [[-26 + tr, -1], [26 + tr, 1]]) stroke([[ex + s * 22, -18], [ex + s * 34, -30]], 5);   // lashes
  brows(-26 + tr, 26 + tr, -38, 22, P.brow ?? 0, 7);
  shape(ell(2 + tr * 1.3, 42, 8, 7, 10), { fill: C.skinS, lw: 5 });
  const m = P.mouth || {};
  mouth(2 + tr, 64, 42, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? .1, skew: m.skew || 0, lw: 6 });
  pop();
  arm(shF, P.armR || { h: [18, 170], bend: 14 }, C.momTop, C.momTopS, C.skin, 36, 30, 18, P.holdR);
  pop();
  if (P.sweat != null) sweat(100, -780 + (P.sweat % 1) * 30, 1);
  pop();
}

// ===================== GRANDMA =====================
export function gran(P) {
  const f = P.face ?? 1;
  push(); translate(P.x + jit(P, 4), P.y + (P.bob || 0)); scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  if (!P.noLegs) for (const sx of [-1, 1]) {
    shape(noodle([sx * 34, -120], [sx * 36, -20], 0, 34, 30), { fill: '#c9b8a8', lw: 6 });
    shape(spline([[sx * 36 - 28, 2], [sx * 36 - 22, -24], [sx * 36 + 16, -24], [sx * 36 + 42, -4], [sx * 36 + 36, 6]]), { fill: C.shoe, lw: 6 });
  }
  shape(spline([[-110, -300], [110, -300], [130, -110], [0, -96], [-130, -110]]), { fill: C.granSkirt, lw: 7 });
  push(); rotate(P.lean ?? 0);
  const shB = [-92, -420], shF = [92, -420];
  arm(shB, P.armL || { h: [-20, 150], bend: -14 }, C.granTop, C.granTopS, C.skin, 44, 38, 20, P.holdL);
  // short, wide body
  shape(spline([[0, -456], [96, -440], [124, -340], [118, -250], [0, -236], [-118, -250], [-124, -340], [-96, -440]]), {
    fill: C.granTop, lw: 7, shade: () => {
      fillOnly(spline([[40, -470], [150, -420], [150, -230], [70, -230], [90, -340]]), C.granTopS, { boil: .4 });
      for (let i = 0; i < 12; i++) dot(-90 + hash(i * 2.1) * 170, -420 + hash(i * 5.3) * 170, 5, '#f2c3e6');   // little flowers
    }
  });
  // glasses chain
  stroke(spline([[-62, -500], [-50, -440], [0, -420], [50, -440], [62, -500]], false), 3, { line: '#c99a2e' });
  push(); translate(4, -540); rotate(P.headTilt ?? 0);
  const tr = (P.turn ?? .15) * 18;
  // grey "cabbage" hair
  shape(spline([[-96, 20], [-110, -50], [-70, -110], [0, -130], [70, -110], [110, -50], [96, 20], [70, -20], [-70, -20]]), { fill: C.granHair, lw: 7, shade: () => fillOnly(ell(60, -60, 50, 60, 20), C.granHairS, { boil: .3 }) });
  shape(ell(0, -132, 46, 34, 24), { fill: C.granHair, lw: 7 });
  shape(ell(0, 6, 82, 84, 50), { fill: C.skin, lw: 7, shade: () => fillOnly(ell(64, 30, 40, 80, 20), C.skinB, { boil: .3 }) });
  shape(spline([[-84, -6], [-60, -70], [0, -90], [60, -70], [84, -6], [40, -46], [-40, -46]]), { fill: C.granHair, lw: 6 });
  const lid = P.blink ? 1 : (P.lid ?? .3), look = P.look || [0, 0];
  eye(-28 + tr, 8, 22, 24, { lid, look, pupil: 4 });
  eye(28 + tr, 8, 22, 24, { lid, look, pupil: 4 });
  for (const ex of [-28 + tr, 28 + tr]) shape(ell(ex, 8, 34, 32, 30), { line: '#c99a2e', lw: 7, stroke: true });
  stroke([[-2 + tr, 4], [2 + tr, 4]], 6, { line: '#c99a2e' });
  brows(-28 + tr, 28 + tr, -34, 22, P.brow ?? -.6, 8, '#8f8798');
  for (const sx of [-1, 1]) stroke(arc(sx * 50 + tr, 52, 12, 8, Math.PI * .2, Math.PI * .8, 6), 3.5);   // wrinkles
  shape(spline([[tr, 20], [12 + tr, 48], [2 + tr, 58], [-10 + tr, 52]]), { fill: C.skinS, lw: 5 });
  const m = P.mouth || {};
  mouth(2 + tr, 78, 42, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? -.5, skew: m.skew || 0, lw: 6 });
  pop();
  arm(shF, P.armR || { h: [20, 150], bend: 14 }, C.granTop, C.granTopS, C.skin, 44, 38, 20, P.holdR);
  pop();
  if (P.sweat != null) sweat(100, -640 + (P.sweat % 1) * 30, 1);
  pop();
}

// ===================== PROPS =====================
export function notebook(x, y, s = 1, { open = 1, glow = 0, t = 0, lines = 1, solved = 0 } = {}) {
  push(); translate(x, y); scale(s);
  if (glow > 0) {
    for (const [r, a] of [[1.5, .18], [1.25, .3]]) shape(ell(0, 0, 230 * r * glow, 120 * r * glow, 40), { fill: `rgba(125,255,196,${a})`, line: null, stroke: false, boil: .6 });
  }
  if (open > .5) {
    shape([[-220, -110], [0, -96], [0, 110], [-220, 96]], { fill: '#fbf7ec', lw: 6 });
    shape([[220, -110], [0, -96], [0, 110], [220, 96]], { fill: '#fbf7ec', lw: 6 });
    for (let k = 0; k < 6; k++) { stroke([[-200, -70 + k * 30], [-16, -60 + k * 30]], 2.5, { line: '#9ec3e6', boil: .3 }); stroke([[16, -60 + k * 30], [200, -70 + k * 30]], 2.5, { line: '#9ec3e6', boil: .3 }); }
    if (lines > 0) {
      text('Задача 3', -110, -72, { font: '900 26px "Nunito"', fill: '#33427a' });
      text('7 × 8 = ?', -110, -12, { font: '900 40px "Nunito"', fill: '#33427a' });
    }
    if (solved > 0) text('56', 110, -12, { font: '900 56px "Nunito"', fill: '#33427a' });
    stroke([[0, -96], [0, 110]], 6);
  } else {
    shape(rr(-150, -110, 300, 220, 10), { fill: '#3a7bd5', lw: 7, shade: () => fillOnly(rect(-150, -110, 40, 220), '#2a5ca8', { boil: .3 }) });
    shape(rr(-60, -40, 140, 60, 6), { fill: '#fbf7ec', lw: 5 });
  }
  pop();
}
export function pencil(x, y, a, s = 1) {
  push(); translate(x, y); rotate(a); scale(s);
  shape(rect(-90, -9, 150, 18), { fill: '#ffcf3f', lw: 5 });
  shape([[60, -9], [92, 0], [60, 9]], { fill: '#f1d2a6', lw: 5 }); dot(88, 0, 4);
  shape(rect(-108, -9, 18, 18), { fill: '#ff8fa3', lw: 5 });
  pop();
}
export function calculator(x, y, a = 0, ant = 0) {
  push(); translate(x, y); rotate(a);
  if (ant > 0) { stroke([[30, -40], [30 + ant * 20, -40 - ant * 120]], 5); dot(30 + ant * 20, -40 - ant * 120, 9, '#ff4a3a'); }
  shape(rr(-40, -50, 80, 100, 10), { fill: '#8d96a3', lw: 6, shade: () => fillOnly(rect(16, -52, 30, 104), '#6c7482', { boil: .3 }) });
  shape(rr(-28, -38, 56, 24, 4), { fill: '#bfe3a8', lw: 4 });
  for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) shape(rr(-26 + i * 19, -4 + j * 20, 14, 14, 3), { fill: '#e8e4dc', lw: 3 });
  pop();
}
export function phone(x, y, a = 0, s = 1, txt = '') {
  push(); translate(x, y); rotate(a); scale(s);
  shape(rr(-60, -100, 120, 200, 16), { fill: '#2a2230', lw: 6 });
  shape(rr(-50, -86, 100, 172, 8), { fill: '#9fd8ff', lw: 4 });
  if (txt) text(txt, 0, -40, { font: '900 18px "Nunito"', fill: '#2a2230' });
  pop();
}
export function bigBook(x, y, a = 0, s = 1) {
  push(); translate(x, y); rotate(a); scale(s);
  shape(rr(-120, -80, 240, 160, 10), { fill: '#7a3b2a', lw: 7, shade: () => { fillOnly(rect(-120, 50, 240, 40), '#5a2a1e', { boil: .3 }); fillOnly(rect(-120, -80, 34, 160), '#5a2a1e', { boil: .3 }); } });
  shape(rr(-70, -48, 160, 50, 6), { fill: '#e8d6a8', lw: 5 });
  text('ЗАДАЧНИК', 10, -32, { font: '900 22px "Nunito"', fill: '#5a2a1e' });
  text('1974', 10, -8, { font: '900 22px "Nunito"', fill: '#5a2a1e' });
  stroke([[-118, 56], [118, 56]], 4);
  pop();
}
export function paper(x, y, a = 0, s = 1, { txt = '', col = '#fbf7ec', crumpled = false, ink = '#33427a', cross = false, tick = false } = {}) {
  push(); translate(x, y); rotate(a); scale(s);
  if (crumpled) {
    shape(spline([[-60, -40], [-10, -58], [50, -46], [64, 6], [40, 52], [-20, 58], [-62, 20]]), { fill: col, lw: 6 });
    stroke([[-40, -20], [0, 0], [30, -30]], 3); stroke([[-20, 30], [10, 10], [40, 30]], 3);
  } else {
    shape(rect(-80, -105, 160, 210), { fill: col, lw: 6 });
    for (let k = 0; k < 6; k++) stroke([[-60, -70 + k * 26], [40 - hash(k + a) * 40, -70 + k * 26]], 3, { line: '#9aa4c4', boil: .4 });
    if (txt) text(txt, 0, 30, { font: '900 72px "Nunito"', fill: ink });
    if (cross) { stroke([[-50, -10], [50, 80]], 9, { line: '#e8392b' }); stroke([[50, -10], [-50, 80]], 9, { line: '#e8392b' }); }
    if (tick) stroke([[-40, 50], [-10, 80], [50, 0]], 11, { line: '#1e9e5a' });
  }
  pop();
}
