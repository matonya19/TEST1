// Cut-paper art for «Домашка»: the family (redrawn per pose), the room, props. Canvas2D → finishCut → cut-out item.
import { mulberry, TAU, clamp } from './lib.js';
import { cv, finishCut, sh, blob, crescent, paperFill, INK, rr } from './paper.js';

export const PPM = 5200;
const LW = 9, LW2 = 5;
export function cut(wm, hm, draw, o = {}) {
  const pad = o.pad ?? 30, w = Math.ceil(wm * PPM) + pad * 2, h = Math.ceil(hm * PPM) + pad * 2;
  const c = cv(w, h), x = c.getContext('2d'); x.translate(pad, pad);
  draw(x, w - pad * 2, h - pad * 2);
  const out = o.raw ? c : finishCut(c, o.border ?? 14, o);
  return { c: out, w: w / PPM, h: h / PPM, ax: o.ax ?? .5, ay: o.ay ?? 1 - pad / h };
}

// ===================== THE FAMILY =====================
// canvas 700 × 1100, feet at y = 1050, centre x = 350; each character has its own proportions
export const FW = 700, FH = 1100;
const SKIN = '#ffdcb8', SKIN_S = '#f0bc8e';
export const WHO = {
  boy:  { top: '#2bb3a6', topS: '#1c8a80', legs: '#2d4a86', hair: '#6b3f22', headR: 175, headY: 330, sh: 560, hip: 820, bw: 150, hipW: 175 },
  dad:  { top: '#e8a92c', topS: '#c48614', legs: '#6b4a32', hair: '#4a2e1c', headR: 135, headY: 210, sh: 380, hip: 700, bw: 150, hipW: 140, glasses: '#2a1f1a' },
  mom:  { top: '#f2705a', topS: '#cf5440', legs: SKIN, hair: '#7a3a22', skirt: '#2f3f7a', skirtS: '#22305f', headR: 135, headY: 230, sh: 400, hip: 680, bw: 120, hipW: 120 },
  gran: { top: '#8a4590', topS: '#6c3071', legs: '#c9b8a8', hair: '#d6d1da', headR: 140, headY: 250, sh: 420, hip: 760, bw: 190, hipW: 210, glasses: '#c79a2e' },
};

function eye(x, ex, ey, p, s = 1) {
  const { blink = false, eyes = 'open', look = [0, 0] } = p;
  if (eyes === 'happy') { x.beginPath(); x.moveTo(ex - 26 * s, ey + 8); x.quadraticCurveTo(ex, ey - 36 * s, ex + 26 * s, ey + 8); x.lineWidth = 11; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke(); return; }
  if (blink) { x.beginPath(); x.moveTo(ex - 24 * s, ey + 2); x.quadraticCurveTo(ex, ey + 16, ex + 24 * s, ey + 2); x.lineWidth = 10; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke(); return; }
  const big = eyes === 'wide' ? 1.22 : 1, ry = 40 * s * big * (eyes === 'sleepy' ? .55 : 1), rx = 22 * s * big;
  x.beginPath(); x.ellipse(ex + look[0] * 8, ey + look[1] * 9, rx, ry, 0, 0, TAU); x.fillStyle = INK; x.fill();
  x.beginPath(); x.ellipse(ex + look[0] * 8 - 7 * s, ey + look[1] * 9 - ry * .4, 8 * s, 12 * s, -.2, 0, TAU); x.fillStyle = '#fff'; x.fill();
  if (eyes === 'sleepy') { x.beginPath(); x.moveTo(ex - 28 * s, ey - ry); x.lineTo(ex + 28 * s, ey - ry); x.lineWidth = 9; x.strokeStyle = INK; x.stroke(); }
}
function brows(x, cx, y, d, kind, s = 1) {
  const k = { angry: [16, -10], worried: [-14, 8], up: [0, -14] }[kind] || [0, 0];
  x.lineWidth = 11 * s; x.strokeStyle = INK; x.lineCap = 'round';
  x.beginPath(); x.moveTo(cx - d - 28 * s, y + k[1] - k[0] * .2); x.lineTo(cx - d + 22 * s, y + k[1] + k[0]); x.stroke();
  x.beginPath(); x.moveTo(cx + d + 28 * s, y + k[1] - k[0] * .2); x.lineTo(cx + d - 22 * s, y + k[1] + k[0]); x.stroke();
}
function mouthD(x, cx, my, kind, s = 1) {
  x.lineCap = 'round'; x.strokeStyle = INK; x.lineWidth = 10 * s;
  if (kind === 'smile') { x.beginPath(); x.moveTo(cx - 34 * s, my - 6); x.quadraticCurveTo(cx, my + 30 * s, cx + 34 * s, my - 6); x.stroke(); }
  else if (kind === 'big') { x.beginPath(); x.moveTo(cx - 44 * s, my - 10); x.quadraticCurveTo(cx, my + 60 * s, cx + 44 * s, my - 10); x.closePath(); sh(x, '#9a2f3a', 9 * s); }
  else if (kind === 'open') { x.beginPath(); x.ellipse(cx, my + 10 * s, 24 * s, 30 * s, 0, 0, TAU); sh(x, '#9a2f3a', 9 * s); }
  else if (kind === 'frown') { x.beginPath(); x.moveTo(cx - 30 * s, my + 18 * s); x.quadraticCurveTo(cx, my - 12 * s, cx + 30 * s, my + 18 * s); x.stroke(); }
  else if (kind === 'wavy') { x.beginPath(); x.moveTo(cx - 32 * s, my + 6); for (let i = 1; i <= 4; i++) x.lineTo(cx - 32 * s + i * 16 * s, my + (i % 2 ? -6 : 6)); x.stroke(); }
  else { x.beginPath(); x.moveTo(cx - 24 * s, my + 4); x.lineTo(cx + 24 * s, my + 4); x.stroke(); }
}
function arm(x, S, side, ang, held) {
  const shx = 350 + side * (S.bw - 18), shy = S.sh + 30;
  x.save(); x.translate(shx, shy); x.rotate(-ang * side);
  const L = (S.hip - S.sh) * .82;
  rr(x, -26, -14, 52, L, 26); sh(x, S.top, LW2 + 1);
  x.beginPath(); x.arc(0, L, 34, 0, TAU); sh(x, SKIN, LW2 + 1);
  if (held) { x.translate(0, L); x.rotate(ang * side); held(x); }
  x.restore();
}
export function drawPerson(x, who, p = {}) {
  const S = WHO[who];
  x.clearRect(0, 0, FW, FH);
  const W = cv(FW, FH), a = W.getContext('2d');
  a.save(); a.translate(350, 1050); a.rotate(p.lean || 0); a.translate(-350, -1050);
  // legs
  const st = p.walk ? Math.sin(p.walk) * (p.stride ?? 1) : 0;
  if (who !== 'mom') for (const [sx, k] of [[-1, st], [1, -st]]) {
    a.save(); a.translate(350 + sx * S.hipW * .45, S.hip); a.rotate(k * .35);
    rr(a, -34, -20, 68, 1000 - S.hip, 30); sh(a, S.legs, LW2 + 1);
    blob(a, 14, 1000 - S.hip + 8, 58, 30, .04, 3 + sx); sh(a, '#3a2a24', LW2 + 1);
    a.restore();
  } else {
    for (const [sx, k] of [[-1, st], [1, -st]]) { a.save(); a.translate(350 + sx * 40, S.hip + 150); a.rotate(k * .3); rr(a, -22, -20, 44, 1000 - S.hip - 150, 22); sh(a, SKIN, LW2); blob(a, 12, 1000 - S.hip - 140, 44, 24, .04, 5 + sx); sh(a, '#a33a2a', LW2); a.restore(); }
    const sk = () => { a.beginPath(); a.moveTo(350 - S.hipW, S.hip - 30); a.lineTo(350 + S.hipW, S.hip - 30); a.lineTo(350 + S.hipW + 90, S.hip + 190); a.quadraticCurveTo(350, S.hip + 230, 350 - S.hipW - 90, S.hip + 190); a.closePath(); };
    crescent(a, sk, S.skirtS, 26, 0, S.skirt); sk(); sh(a, null, LW);
  }
  // back arm
  arm(a, S, -1, p.armL ?? .15, p.holdL);
  // body
  const body = () => { a.beginPath(); a.moveTo(350 - S.bw, S.sh + 20); a.quadraticCurveTo(350, S.sh - 30, 350 + S.bw, S.sh + 20); a.lineTo(350 + S.hipW + (who === 'boy' ? 20 : 0), S.hip + (who === 'boy' ? 40 : 0)); a.quadraticCurveTo(350, S.hip + 30, 350 - S.hipW - (who === 'boy' ? 20 : 0), S.hip + (who === 'boy' ? 40 : 0)); a.closePath(); };
  crescent(a, body, S.topS, 30, 0, S.top); body(); sh(a, null, LW);
  if (who === 'boy') { rr(a, 270, S.hip - 120, 160, 80, 30); sh(a, S.topS, LW2); a.beginPath(); a.moveTo(330, S.sh); a.lineTo(326, S.sh + 90); a.moveTo(370, S.sh); a.lineTo(374, S.sh + 90); a.lineWidth = LW2; a.strokeStyle = INK; a.stroke(); }
  if (who === 'dad') { a.save(); a.beginPath(); body(); a.clip(); a.strokeStyle = S.topS; a.lineWidth = 14; for (let k = 0; k < 3; k++) { a.beginPath(); a.moveTo(150, S.sh + 110 + k * 90); a.lineTo(560, S.sh + 110 + k * 90); a.stroke(); } a.restore(); }
  if (who === 'gran') { a.save(); a.beginPath(); body(); a.clip(); const R = mulberry(4); for (let k = 0; k < 14; k++) { a.beginPath(); a.arc(180 + R() * 340, S.sh + 60 + R() * 300, 14, 0, TAU); a.fillStyle = '#f5b9de'; a.fill(); } a.restore(); }
  if (who === 'mom') { a.beginPath(); a.moveTo(310, S.sh - 8); a.lineTo(350, S.sh + 60); a.lineTo(390, S.sh - 8); a.fillStyle = SKIN; a.fill(); a.lineWidth = LW2; a.strokeStyle = INK; a.stroke(); }
  // head
  const hx = 350, hy = S.headY, R = S.headR;
  if (who === 'mom') { blob(a, hx + 20, hy - R - 30, 60, 52, .05, 6); sh(a, S.hair, LW); a.save(); a.translate(hx + 30, hy - R - 40); a.rotate(-.6); rr(a, -10, -90, 20, 180, 6); sh(a, '#ffcf3f', LW2); a.restore(); blob(a, hx, hy + 20, R + 22, R + 34, .03, 7); sh(a, S.hair, LW); }
  if (who === 'gran') { for (let k = 0; k < 9; k++) { const an = Math.PI * (1.0 + k / 8); blob(a, hx + Math.cos(an) * R * 1.02, hy + Math.sin(an) * R * .95, 48, 44, .06, 20 + k); sh(a, S.hair, LW2 + 1); } blob(a, hx, hy - R - 34, 56, 46, .05, 31); sh(a, S.hair, LW2 + 1); }
  const head = () => blob(a, hx, hy, R, R * .96, .025, 11);
  crescent(a, head, SKIN_S, 22, 0, SKIN); head(); sh(a, null, LW);
  if (who === 'boy') { a.beginPath(); a.moveTo(hx - R - 4, hy - 10); a.bezierCurveTo(hx - R, hy - R * 1.2, hx + R, hy - R * 1.25, hx + R + 4, hy - 10); a.quadraticCurveTo(hx + R * .5, hy - R * .55, hx, hy - R * .6); a.quadraticCurveTo(hx - R * .6, hy - R * .55, hx - R - 4, hy - 10); sh(a, S.hair, LW);
    a.beginPath(); a.moveTo(hx + 10, hy - R * .98); a.bezierCurveTo(hx - 10, hy - R * 1.5, hx + 60, hy - R * 1.6, hx + 70, hy - R * 1.3); a.lineWidth = 16; a.strokeStyle = S.hair; a.lineCap = 'round'; a.stroke(); a.lineWidth = LW2; a.strokeStyle = INK; a.stroke(); }
  if (who === 'dad') { a.beginPath(); a.moveTo(hx - R - 6, hy); a.bezierCurveTo(hx - R - 20, hy - R * 1.3, hx + R + 20, hy - R * 1.35, hx + R + 6, hy); a.quadraticCurveTo(hx + R * .6, hy - R * .55, hx, hy - R * .5); a.quadraticCurveTo(hx - R * .6, hy - R * .6, hx - R - 6, hy); sh(a, S.hair, LW); const R2 = mulberry(3); for (let k = 0; k < 16; k++) { a.beginPath(); a.arc(hx - 60 + R2() * 120, hy + 70 + R2() * 40, 4, 0, TAU); a.fillStyle = '#9a6a4a'; a.fill(); } }
  if (who === 'mom') { a.beginPath(); a.moveTo(hx - R - 4, hy + 10); a.bezierCurveTo(hx - R, hy - R * 1.25, hx + R, hy - R * 1.25, hx + R + 4, hy + 10); a.quadraticCurveTo(hx + R * .3, hy - R * .7, hx - R - 4, hy + 10); sh(a, S.hair, LW); }
  if (who === 'gran') { a.beginPath(); a.moveTo(hx - R, hy - 20); a.bezierCurveTo(hx - R, hy - R * 1.2, hx + R, hy - R * 1.2, hx + R, hy - 20); a.quadraticCurveTo(hx, hy - R * .55, hx - R, hy - 20); sh(a, S.hair, LW); }
  const es = who === 'boy' ? 1.15 : 1, ed = who === 'boy' ? 62 : 52, ey = hy + (who === 'boy' ? 10 : 0);
  eye(a, hx - ed, ey, p, es); eye(a, hx + ed, ey, p, es);
  if (S.glasses) { a.lineWidth = 9; a.strokeStyle = S.glasses; for (const sx of [-1, 1]) { a.beginPath(); if (who === 'dad') a.roundRect(hx + sx * ed - 44, ey - 40, 88, 76, 14); else a.arc(hx + sx * ed, ey, 46, 0, TAU); a.stroke(); } a.beginPath(); a.moveTo(hx - ed + 44, ey - 6); a.lineTo(hx + ed - 44, ey - 6); a.stroke(); }
  if (p.brows) brows(a, hx, ey - 70 * es, ed, p.brows, es);
  for (const sx of [-1, 1]) { a.beginPath(); a.ellipse(hx + sx * (ed + 40), ey + 60, 30, 16, 0, 0, TAU); a.fillStyle = 'rgba(255,120,130,.45)'; a.fill(); }
  mouthD(a, hx, hy + R * .52, p.mouth || 'smile', es);
  // front arm
  arm(a, S, 1, p.armR ?? .15, p.holdR);
  a.restore();
  x.drawImage(finishCut(W, 16), 0, 0);
}

// held props (drawn in hand space; hand at 0,0)
export const HOLD = {
  laptop: x => { x.save(); x.rotate(.1); rr(x, -110, -150, 220, 140, 14); sh(x, '#5f6b7a', LW2 + 1); rr(x, -95, -138, 190, 116, 8); sh(x, '#8fd2ff', LW2); rr(x, -130, -12, 260, 30, 10); sh(x, '#8b95a3', LW2 + 1); x.restore(); },
  phone: x => { x.save(); x.rotate(-.2); rr(x, -40, -120, 80, 150, 14); sh(x, '#2a2230', LW2 + 1); rr(x, -30, -108, 60, 120, 6); sh(x, '#9fd8ff', 0); x.restore(); },
  book: x => { x.save(); x.rotate(-.1); rr(x, -120, -180, 240, 160, 10); sh(x, '#8a3a2a', LW2 + 1); rr(x, -80, -150, 160, 70, 6); sh(x, '#e8d6a8', LW2); x.font = '64px Neucha'; x.fillStyle = '#5a2a1e'; x.textAlign = 'center'; x.fillText('1974', 0, -96); x.restore(); },
  arrow: x => { x.save(); x.rotate(-.3); x.beginPath(); x.moveTo(-60, 0); x.lineTo(30, 0); x.lineTo(30, -30); x.lineTo(80, 10); x.lineTo(30, 50); x.lineTo(30, 20); x.lineTo(-60, 20); x.closePath(); sh(x, '#ffd84a', LW2 + 1); x.restore(); },
};

// ===================== THE ROOM (pages) =====================
export const PW = 2048, PH = 1396;    // page canvases (book BW × BD)
export function wallPage() {
  const c = cv(PW, PH), x = c.getContext('2d');
  paperFill(x, PW, PH, '#a9dcc0', 4, .05);
  // wallpaper dots
  const R = mulberry(9); x.fillStyle = 'rgba(255,255,255,.35)'; for (let i = 0; i < 220; i++) { x.beginPath(); x.arc(R() * PW, R() * PH * .8 + PH * .2, 10 + R() * 6, 0, TAU); x.fill(); }
  // skirting board (at the bottom = page floor edge)
  x.fillStyle = '#f2e6cf'; x.fillRect(0, 0, PW, 70); x.strokeStyle = INK; x.lineWidth = 8; x.beginPath(); x.moveTo(0, 70); x.lineTo(PW, 70); x.stroke();
  return c;
}
export function floorPage() {
  const c = cv(PW, PH), x = c.getContext('2d');
  paperFill(x, PW, PH, '#e7b56e', 6, .05);
  x.strokeStyle = 'rgba(150,90,40,.35)'; x.lineWidth = 6; for (let i = 0; i < PW; i += 170) { x.beginPath(); x.moveTo(i, 0); x.lineTo(i, PH); x.stroke(); }
  // rug
  x.save(); x.translate(PW * .55, PH * .55); blob(x, 0, 0, 620, 300, .03, 12); sh(x, '#e5786a', 10); blob(x, 0, 0, 520, 230, .03, 13); sh(x, '#f6b9a3', 0); x.restore();
  return c;
}
// cover: an exercise book
export function coverArt(c, m) {
  const x = c.getContext('2d'), y = m.getContext('2d'), w = c.width, h = c.height;
  x.fillStyle = '#3f86c8'; x.fillRect(0, 0, w, h);
  const R = mulberry(3); for (let i = 0; i < h; i += 3) { x.fillStyle = `rgba(0,0,0,${.03 + R() * .05})`; x.fillRect(0, i, w, 1.2); }
  y.fillStyle = 'rgb(0,235,0)'; y.fillRect(0, 0, w, h);
  // white label
  x.fillStyle = '#fbf8ee'; x.fillRect(w * .28, h * .26, w * .44, h * .44); x.strokeStyle = '#23317a'; x.lineWidth = 8; x.strokeRect(w * .28 + 20, h * .26 + 20, w * .44 - 40, h * .44 - 40);
  x.fillStyle = '#23317a'; x.textAlign = 'center'; x.font = '150px Neucha'; x.fillText('Домашняя', w / 2, h * .42); x.fillText('работа', w / 2, h * .55);
  x.font = '80px Neucha'; x.fillText('ТЕТРАДЬ', w / 2, h * .64);
}

// ===================== PROPS =====================
export function desk() { return cut(.08, .026, (x, W, H) => {
  const top = () => { x.beginPath(); x.moveTo(0, 30); x.lineTo(W, 30); x.lineTo(W, 80); x.lineTo(0, 80); x.closePath(); };
  crescent(x, top, '#8a5530', 0, 14, '#b9763f'); top(); sh(x, null, LW);
  for (const lx of [30, W - 70]) { rr(x, lx, 80, 40, H - 80, 8); sh(x, '#8a5530', LW2 + 1); }
  rr(x, W * .3, 0, W * .3, 34, 6); sh(x, '#fbf8ee', LW2);       // notebook on the desk
  x.font = '30px Neucha'; x.fillStyle = '#23317a'; x.textAlign = 'center'; x.fillText('7×8=?', W * .45, 26);
}); }
export function clockCard() { return cut(.05, .05, (x, W, H) => {
  const f = () => { x.beginPath(); x.arc(W / 2, H / 2, W * .46, 0, TAU); };
  crescent(x, f, '#e8d9b8', 14, 14, '#fff8e6'); f(); sh(x, '#fff8e6', LW + 2, '#c93b2c'); f(); x.lineWidth = LW; x.strokeStyle = INK; x.stroke();
  for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; x.beginPath(); x.moveTo(W / 2 + Math.cos(a) * W * .36, H / 2 + Math.sin(a) * W * .36); x.lineTo(W / 2 + Math.cos(a) * W * .41, H / 2 + Math.sin(a) * W * .41); x.lineWidth = 6; x.stroke(); }
}, { ay: .5 }); }
export function hand(len, wid, col = INK) { return cut(wid, len, (x, W, H) => { rr(x, 0, 0, W, H, W / 2); sh(x, col, 0); }, { border: 0, ay: 1, grain: false }); }
export function tag(text, col = '#c93b2c', wm = .05) { return cut(wm, wm * .4, (x, W, H) => {
  rr(x, 0, 0, W, H, 18); sh(x, '#fff8e6', LW, col); x.font = `${H * .62}px Neucha`; x.fillStyle = col; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(text, W / 2, H * .54);
}, { ay: 1 }); }
export function banner(text) { return cut(.17, .045, (x, W, H) => {
  const b = () => { x.beginPath(); x.moveTo(0, 10); x.lineTo(W, 0); x.lineTo(W - 20, H); x.lineTo(20, H - 10); x.closePath(); };
  crescent(x, b, '#a8241a', 0, 18, '#d8392b'); b(); sh(x, null, LW);
  x.font = `${H * .62}px Neucha`; x.fillStyle = '#fff8e6'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(text, W / 2, H * .5);
  for (const hx of [W * .15, W * .85]) { x.beginPath(); x.arc(hx, 20, 9, 0, TAU); sh(x, '#fff', 4); }
}, { ay: 0 }); }
export function sheet(text, col) { return cut(.026, .032, (x, W, H) => {
  x.beginPath(); x.rect(0, 0, W, H); sh(x, '#fbf8ee', LW2 + 1);
  x.strokeStyle = 'rgba(80,130,200,.4)'; x.lineWidth = 3; for (let i = 30; i < H; i += 26) { x.beginPath(); x.moveTo(10, i); x.lineTo(W - 10, i); x.stroke(); }
  x.font = `${H * .5}px Neucha`; x.fillStyle = col; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(text, W / 2, H * .55);
}, { ay: .5 }); }
export function answerCard() { return cut(.03, .022, (x, W, H) => {
  rr(x, 0, 0, W, H * .78, 10); sh(x, '#fbf8ee', LW2 + 1);
  x.font = `${H * .5}px Neucha`; x.fillStyle = '#23317a'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('56', W * .4, H * .42);
  x.beginPath(); x.moveTo(W * .66, H * .42); x.lineTo(W * .74, H * .56); x.lineTo(W * .9, H * .2); x.lineWidth = 12; x.strokeStyle = '#2f9a4a'; x.lineCap = 'round'; x.stroke();
  rr(x, W * .45, H * .78, 14, H * .22, 4); sh(x, '#b98150', LW2);
}); }
export function five() { return cut(.05, .05, (x, W, H) => {
  const f = () => { x.beginPath(); x.arc(W / 2, H / 2, W * .46, 0, TAU); };
  f(); sh(x, '#fff8e6', LW + 4, '#d01a12');
  x.font = `${H * .78}px Neucha`; x.fillStyle = '#d01a12'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('5', W / 2, H * .55);
}, { ay: .5 }); }
export function consoleCard() { return cut(.2, .13, (x, W, H) => {
  const b = () => { x.beginPath(); x.moveTo(W * .08, H * .35); x.lineTo(W * .92, H * .35); x.lineTo(W, H); x.lineTo(0, H); x.closePath(); };
  crescent(x, b, '#5a3a8a', 0, 30, '#7a55b3'); b(); sh(x, null, LW);
  const R = mulberry(5); for (let i = 0; i < 14; i++) { x.beginPath(); x.arc(W * .14 + (i % 7) * W * .12, H * .55 + Math.floor(i / 7) * H * .2, 18, 0, TAU); sh(x, ['#ffd84a', '#ff6b5a', '#7fe0ff'][Math.floor(R() * 3)], LW2); }
  // steering wheel on a column
  rr(x, W / 2 - 16, H * .05, 32, H * .32, 8); sh(x, '#8b95a3', LW2);
  x.beginPath(); x.arc(W / 2, H * .12, H * .11, 0, TAU); x.lineWidth = 26; x.strokeStyle = INK; x.stroke(); x.lineWidth = 16; x.strokeStyle = '#d8392b'; x.stroke();
  for (const a of [0, 2.09, 4.19]) { x.beginPath(); x.moveTo(W / 2, H * .12); x.lineTo(W / 2 + Math.cos(a) * H * .11, H * .12 + Math.sin(a) * H * .11); x.lineWidth = 12; x.strokeStyle = INK; x.stroke(); }
}); }
export function bubble(kind) { return cut(.035, .026, (x, W, H) => {
  const b = () => { x.beginPath(); x.ellipse(W / 2, H * .42, W * .48, H * .38, 0, 0, TAU); x.moveTo(W * .35, H * .7); x.lineTo(W * .25, H); x.lineTo(W * .5, H * .76); };
  b(); sh(x, '#fffdf5', LW);
  x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillStyle = INK;
  if (kind === 'help') { x.font = `${H * .3}px Neucha`; x.fillText('помоги?', W / 2, H * .44); }
  else { x.lineWidth = 10; x.strokeStyle = '#d8392b'; x.beginPath(); for (let i = 0; i <= 8; i++) x.lineTo(W * .18 + i * W * .08, H * .42 + (i % 2 ? -H * .12 : H * .12)); x.stroke(); }
}); }
export function window_() { return cut(.07, .08, (x, W, H) => {
  x.beginPath(); x.rect(0, 0, W, H); sh(x, '#fff3dc', LW);
  x.beginPath(); x.rect(26, 26, W - 52, H - 52); sh(x, '#2b356f', LW2);
  const R = mulberry(2); for (let i = 0; i < 18; i++) { x.beginPath(); x.arc(40 + R() * (W - 80), 40 + R() * (H - 80), 4, 0, TAU); x.fillStyle = '#ffe9a8'; x.fill(); }
  x.beginPath(); x.arc(W * .72, H * .3, 30, 0, TAU); x.fillStyle = '#ffe9a8'; x.fill();
  x.beginPath(); x.moveTo(W / 2, 26); x.lineTo(W / 2, H - 26); x.moveTo(26, H / 2); x.lineTo(W - 26, H / 2); x.lineWidth = LW2 + 2; x.strokeStyle = '#fff3dc'; x.stroke();
}, { ay: .5 }); }
export function shelf() { return cut(.09, .05, (x, W, H) => {
  rr(x, 0, H - 30, W, 30, 6); sh(x, '#b9763f', LW2 + 1);
  const cols = ['#e8392b', '#3a7bd5', '#ffcf3f', '#2fb7a8', '#8e4a8a', '#f08a3c']; let px = 20;
  for (let i = 0; i < 8; i++) { const bw = 36 + (i * 13) % 20, bh = H - 60 - (i * 17) % 50; rr(x, px, H - 30 - bh, bw, bh, 4); sh(x, cols[i % 6], LW2); px += bw + 6; }
}, { ay: .5 }); }
export function crumple(seed) { return cut(.014, .012, (x, W, H) => {
  blob(x, W / 2, H / 2, W * .46, H * .44, .12, seed, 14); sh(x, '#f6f1e4', LW2 + 1);
  x.lineWidth = 4; x.strokeStyle = 'rgba(58,42,36,.6)'; const R = mulberry(seed); for (let i = 0; i < 5; i++) { x.beginPath(); x.moveTo(W * (.2 + R() * .6), H * (.2 + R() * .6)); x.lineTo(W * (.2 + R() * .6), H * (.2 + R() * .6)); x.stroke(); }
}, { ay: .9 }); }
