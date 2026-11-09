// «Домашка» — Brick Toy. 1080×1920, 24 fps; timings follow the user's original voice-over.
import * as THREE from 'three';
import { makePost } from '/core/three/post.js';
import { clamp, seg, eio, eo, ei, ss, lerp, hash, mulberry } from '/core/lib.js';
import { COL, BRICK, PLATE, brick, plate, mesh, roundGeo, plastic } from './bricks.js';
import { buildSet, PT } from './set.js';
import { makeFig, walkPose, FC } from './figs.js';

await document.fonts.load('80px Neucha');
const W = innerWidth, H = innerHeight, DUR = 60.8;
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById('stage').appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(36, W / H, .5, 3000);
const post = makePost(renderer, scene, camera, W, H, { ssaa: 1, ao: true, aoRadius: 3.0, aoThickness: 3, aoAmt: .9 });
post.bloom.strength = .12; post.bloom.threshold = 1.3;
post.vig.uniforms.amt.value = .3; post.vig.uniforms.warm.value = -.35; post.vig.uniforms.contrast.value = .24; post.vig.uniforms.sat.value = 1.1;
const set = await buildSet(scene);
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const q = t => Math.floor(t * 12 + 1e-6) / 12;     // characters and bricks on twos

// —— printed tiles (signs, answers) ——
function label(txt, { w = 4, h = 2, bg = '#f4f4f1', fg = '#1f3a6e', size = 150, circle = false } = {}) {
  const c = document.createElement('canvas'); c.width = 256 * w; c.height = 256 * h; const x = c.getContext('2d');
  x.fillStyle = bg; x.fillRect(0, 0, c.width, c.height); x.fillStyle = fg; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.font = `${size}px Neucha`; x.fillText(txt, c.width / 2, c.height / 2 + size * .05);
  if (circle) { x.strokeStyle = fg; x.lineWidth = 22; x.beginPath(); x.arc(c.width / 2, c.height / 2, Math.min(c.width, c.height) * .4, 0, 7); x.stroke(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return new THREE.MeshPhysicalMaterial({ map: t, roughness: .3, clearcoat: .8, clearcoatRoughness: .1 });
}
function tile(w, d, mat) {   // a flat printed tile (no studs); the print faces +y
  const g = new THREE.Group();
  const b = brick(w, d, '#f4f4f1', { h: PLATE, tile: true }); g.add(b);
  const p = new THREE.Mesh(new THREE.PlaneGeometry(w - .12, d - .12), mat); p.rotation.x = -Math.PI / 2; p.position.y = PLATE + .005; g.add(p);
  g.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; }); return g;
}

// —— the boy's desk ——
const DESK = V(-12, PT, 2);
const deskG = new THREE.Group(); deskG.position.copy(DESK); scene.add(deskG);
for (const [x, z] of [[-2.5, -1], [2.5, -1], [-2.5, 1], [2.5, 1]]) for (let i = 0; i < 2; i++) { const b = brick(1, 1, COL.tan); b.position.set(x, i * BRICK, z); deskG.add(b); }
const deskTop = plate(6, 3, COL.white); deskTop.position.y = 2 * BRICK; deskG.add(deskTop);
const deskBook = tile(2, 2, label('7×8', { w: 2, h: 2, size: 150 })); deskBook.position.set(-.5, 2 * BRICK + PLATE, .2); deskG.add(deskBook);
const DESK_TOP_Y = PT + 2 * BRICK + PLATE;

// —— family ——
const boy = makeFig('boy'), dad = makeFig('dad'), mom = makeFig('mom'), gran = makeFig('gran');
dad.root.scale.setScalar(1.15); mom.root.scale.setScalar(1.12); gran.root.scale.setScalar(1.3);
[boy, dad, mom, gran].forEach(f => scene.add(f.root));

// —— props ——
const signMats = ['+5 мин', '+10 мин', '+5 мин'].map(s => label(s, { w: 4, h: 2, size: 190, fg: '#c91a09' }));
const sign = new THREE.Group(); scene.add(sign); sign.position.set(-1.5, PT, 7);
for (let i = 0; i < 3; i++) { const b = brick(1, 1, COL.lgray); b.position.y = i * BRICK; sign.add(b); }
const signBoard = tile(4, 2, signMats[0]); signBoard.rotation.x = Math.PI / 2; signBoard.position.set(0, 3 * BRICK + 1.2, .6); sign.add(signBoard);
const signPrint = signBoard.children[1];

const book = new THREE.Group(); scene.add(book);
{ const b = brick(3, 2, '#7a2a1e'); book.add(b); const tl = tile(3, 2, label('1974', { w: 3, h: 2, bg: '#e8d6a8', fg: '#5a2a1e', size: 170 })); tl.position.y = BRICK; book.add(tl); }

const laptop = new THREE.Group(); scene.add(laptop);
{ const base = plate(3, 2, COL.dgray); laptop.add(base); const scr = new THREE.Mesh(new THREE.BoxGeometry(2.8, 1.9, .15), new THREE.MeshPhysicalMaterial({ color: '#7cc8ff', emissive: '#3a9bff', emissiveIntensity: .9, roughness: .1, clearcoat: 1 })); scr.position.set(0, PLATE + .95, -.95); scr.rotation.x = -.25; laptop.add(scr); }
const phone = new THREE.Group(); scene.add(phone);
{ const b = new THREE.Mesh(new THREE.BoxGeometry(1, 1.8, .25), new THREE.MeshPhysicalMaterial({ color: '#1b2a34', roughness: .2, clearcoat: 1 })); phone.add(b); const s = new THREE.Mesh(new THREE.PlaneGeometry(.85, 1.55), new THREE.MeshStandardMaterial({ color: '#8fd2ff', emissive: '#4aa8ff', emissiveIntensity: .9 })); s.position.z = .13; phone.add(s); }
const wheel = new THREE.Group(); scene.add(wheel);
{ const m = plastic(COL.black); const r = new THREE.Mesh(new THREE.TorusGeometry(2.2, .28, 12, 40), m); wheel.add(r); for (let k = 0; k < 3; k++) { const s = new THREE.Mesh(new THREE.CylinderGeometry(.18, .18, 2.2, 10), m); s.position.set(Math.cos(k * 2.09 + 1.57) * 1.1, Math.sin(k * 2.09 + 1.57) * 1.1, 0); s.rotation.z = k * 2.09; wheel.add(s); } const hub = mesh(roundGeo(.5, .6), COL.red); hub.rotation.x = Math.PI / 2; wheel.add(hub); }
wheel.traverse(o => { if (o.isMesh) o.castShadow = true; });
const pedsovet = tile(8, 2, label('ПЕДСОВЕТ', { w: 8, h: 2, size: 200, fg: '#c91a09' })); scene.add(pedsovet);
const answers = [['54', -15.5, 9, .2, '#e0a22a'], ['65', -11, 10.5, -.15, '#f06a55'], ['48', -6.5, 9, .3, '#7d3c86']].map(([s, x, z, r, c]) => { const t = tile(3, 3, label(s, { w: 3, h: 3, size: 330, fg: c })); t.userData = { x, z, r }; scene.add(t); return t; });
const balls = [[-17, 13], [-4, 12.5], [-13, 14], [-8.5, 13.5]].map(([x, z], i) => {
  const g = new THREE.IcosahedronGeometry(1.3, 2); const p = g.attributes.position; const R = mulberry(40 + i);
  for (let k = 0; k < p.count; k++) { const s = .75 + R() * .45; p.setXYZ(k, p.getX(k) * s, p.getY(k) * s, p.getZ(k) * s); } g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: '#f3f0e6', roughness: .95, flatShading: true })); m.castShadow = m.receiveShadow = true; m.userData = { x, z }; scene.add(m); return m;
});
const hint = brick(1, 2, COL.yellow); scene.add(hint);
const five = tile(3, 3, label('5', { w: 3, h: 3, size: 360, fg: '#d01a12', circle: true })); scene.add(five);

// —— the tower: the boy's desk overbuilt by the grown-ups ——
const TW = { x: -12, z: -1 };
const TCOL = [FC.mustard, FC.coral, FC.plum, COL.red, COL.blue, COL.yellow];
const towerBricks = [];
function ring(layer, t0, step) {
  const y = PT + layer * BRICK, out = [];
  const spots = [];
  for (let x = -4; x < 4; x += 2) { spots.push([x + 1, -3 + .5, 2, 1]); spots.push([x + 1, 3 - .5, 2, 1]); }
  for (let z = -2; z < 2; z += 2) { spots.push([-3.5, z + 1, 1, 2]); spots.push([3.5, z + 1, 1, 2]); }
  spots.forEach(([x, z, w, d], i) => { const off = layer % 2 ? 1 : 0; const b = brick(w === 2 ? 2 : 1, d === 2 ? 2 : 1, TCOL[(layer + i) % TCOL.length]); scene.add(b); out.push({ m: b, to: V(TW.x + x + (w === 2 ? off * 0 : 0), y, TW.z + z), t: t0 + i * step, layer }); });
  return out;
}
// first build (18.6–23.0): 6 layers; second growth (45.6–49.0): layers 6–9 + a top deck
for (let L = 0; L < 6; L++) towerBricks.push(...ring(L, 18.6 + L * .7, .05));
for (let L = 4; L < 10; L++) towerBricks.push(...ring(L, 45.6 + (L - 4) * .55, .04));
const deck = plate(8, 6, COL.lgray); scene.add(deck); towerBricks.push({ m: deck, to: V(TW.x, PT + 10 * BRICK, TW.z), t: 48.9, layer: 10 });
const DECK_Y = PT + 10 * BRICK + PLATE;
// Grandma's "start over": layers 4–5 are knocked off at KNOCK and scattered (pre-simulated)
const KNOCK = 30.45;
towerBricks.forEach((b, i) => {
  if (b.layer < 4 || b.layer > 5 || b.t > 40) return;
  const R = mulberry(500 + i), v = V((R() - .5) * 14, 6 + R() * 6, 6 + R() * 10), w = V((R() - .5) * 9, (R() - .5) * 9, (R() - .5) * 9);
  const path = []; let p = b.to.clone(), vel = v.clone(), rot = V(0, 0, 0), rest = false;
  for (let f = 0; f <= 3 * 240; f++) {
    if (f % 10 === 0) path.push([p.clone(), rot.clone()]);
    if (rest) continue;
    vel.y -= 60 / 240; p.addScaledVector(vel, 1 / 240); rot.addScaledVector(w, 1 / 240);
    if (p.y < PT) { p.y = PT; vel.y *= -.3; vel.x *= .6; vel.z *= .6; w.multiplyScalar(.5); if (Math.abs(vel.y) < 1) { rest = true; rot.x = Math.round(rot.x / (Math.PI / 2)) * Math.PI / 2; rot.z = Math.round(rot.z / (Math.PI / 2)) * Math.PI / 2; } }
  }
  b.fall = path;
});
// the answer the boy builds from 1×1 plates in the corner: «56 ✓»
const GLY = { '5': ['111', '100', '111', '001', '111'], '6': ['111', '100', '111', '101', '111'], 'v': ['000', '001', '001', '110', '100'] };
const pix = [];
{ let gx = 8.5; ['5', '6', 'v'].forEach((ch, gi) => { GLY[ch].forEach((row, r) => [...row].forEach((c, k) => { if (c === '1') { const m = plate(1, 1, ch === 'v' ? COL.green : COL.blue); scene.add(m); pix.push({ m, to: V(gx + k, PT, 9.5 + r), t: 38.0 + pix.length * .055 }); } })); gx += gi === 1 ? 5 : 4; }); }
const CORNER = V(21.5, PT, 12);

// —— brick motion: fly in on an arc and snap with a small overshoot ——
function flyPos(to, t, t0, d = .45, from = null) {
  const u = (t - t0) / d;
  if (u >= 1) { const k = t - t0 - d; const os = k < .17 ? .35 * (1 - k / .17) * Math.sin(k * 40) : 0; return to.clone().add(V(0, Math.max(0, os), 0)); }
  const src = from || to.clone().add(V(-6 + 12 * hash(to.x * 3 + to.z), 14, 10));
  const p = src.clone().lerp(to, eio(u)); p.y += Math.sin(u * Math.PI) * 4; return p;
}

// ===================== PERFORMANCE =====================
const walkTo = (t, t0, t1, A, B, stride = 2.2) => { const u = seg(t, t0, t1), p = A.clone().lerp(B, ss(u)), d = A.distanceTo(B) * ss(u); return { p, moving: t > t0 && t < t1, phi: d / stride * Math.PI * 2 }; };
const ryTo = (a, b) => Math.atan2(b.x - a.x, b.z - a.z);
const blinkAt = (t, k) => Math.floor(t * 12 + k * 7) % 41 === 0;

const DAD_SPOT = V(-19.5, PT, 1.5), MOM_SPOT = V(-4.5, PT, 1.5), GRAN_SPOT = V(-12, PT, -6.5);
const TOP_SPOTS = [V(-15, DECK_Y, -2), V(-12, DECK_Y, -2.8), V(-9, DECK_Y, -2)];

function boyAt(t) {
  const P = { x: -12, z: -.3, y: PT, ry: 0, expr: 'calm', blink: blinkAt(t, 0) };
  if (t < 2.6) return P;
  if (t < 5.3) { P.armR = t > 3.2 ? [-2.8, .15] : [0, .05]; P.expr = 'smile'; P.look = t > 3.6 ? -.4 : 0; return P; }
  if (t < 18.6) { P.x = -12 + (t > 6.2 ? 1.2 : 0); P.expr = t > 17.3 && t < 18.4 ? 'surprised' : 'flat'; P.look = t < 8.5 ? -.6 : t < 12.3 ? .6 : 0; P.nod = t > 12.3 ? -.25 : 0; return P; }
  if (t < 35.0) {   // pushed out in front of the tower
    const u = ss(seg(t, 18.8, 19.4)); P.x = lerp(-10.8, -12, u); P.z = lerp(-.3, 6.2, u); P.y = PT + Math.sin(u * Math.PI) * 1.2;
    P.expr = t > 30.4 && t < 31.4 ? 'surprised' : 'flat'; P.nod = -.35; P.look = Math.sin(t * .7) * .3;
    return P;
  }
  if (t < 37.2) {   // squeezed, then walks to the corner
    if (t < 35.8) { P.x = -12 + seg(t, 35.0, 35.8) * 2.5; P.z = 6.2 + seg(t, 35.0, 35.8) * 1.5; P.expr = 'worried'; P.lean = .1; return P; }
    const mv = walkTo(t, 35.8, 37.2, V(-9.5, PT, 7.7), CORNER); Object.assign(P, mv.p, walkPose(mv.phi)); P.ry = ryTo(V(-9.5, 0, 7.7), CORNER); P.expr = 'flat'; return P;
  }
  if (t < 58.0) {
    P.x = CORNER.x; P.z = CORNER.z; P.ry = -Math.PI / 2 - .35;
    if (t < 41) { P.armR = [-1.2 - .3 * Math.sin(q(t) * 14), .1]; P.expr = t > 40.2 ? 'happy' : 'calm'; P.nod = -.35; }
    else if (t < 50.2) { P.expr = 'smile'; P.look = .4; P.armL = [-.4, .1]; }
    else if (t < 52.2) { P.expr = 'worried'; P.look = .7; P.nod = .25; P.ry = -Math.PI / 2 + .3; }
    else { P.expr = t > 53.8 ? 'smile' : 'surprised'; P.look = .5; P.ry = -Math.PI / 2 + .1; P.armR = t > 54.0 ? [-1.1, .1] : [0, .05]; }
    return P;
  }
  P.expr = t > 59.2 ? 'happy' : 'smile'; P.nod = -.2; P.armR = [-.9, .05]; P.armL = [-.9, .05];
  return P;
}
function dadAt(t) {
  const P = { x: -40, z: 3, y: PT, ry: Math.PI / 2, expr: 'calm', blink: blinkAt(t, 1) };
  if (t < 5.3) return P;
  if (t < 6.5) { const mv = walkTo(t, 5.3, 6.5, V(-30, PT, 3), DAD_SPOT); Object.assign(P, mv.p, walkPose(mv.phi)); P.expr = 'smile'; return P; }
  Object.assign(P, DAD_SPOT); P.ry = 1.0;
  if (t < 18.6) { P.armR = [-1.4, -.1]; P.armL = [-.6 + .25 * Math.sin(q(t) * 8), 0]; P.expr = t < 8.5 ? 'smile' : 'worried'; P.lean = .15; P.look = t > 10 && t < 12.3 ? .6 : -.2; return P; }
  if (t < 45.5) {
    P.ry = .6; P.expr = t > 41 ? 'talk' : t > 23.6 && t < 26 ? 'surprised' : 'flat'; P.armL = [-1.2, .1]; P.armR = [-1.2, -.1];
    if (t > 41) { P.armR = [-2.6 - .3 * Math.sin(q(t) * 9), .2]; P.armL = [-.5, .4]; P.expr = Math.floor(q(t) * 6) % 2 ? 'talk' : 'angry'; }
    return P;
  }
  if (t < 55.0 && t > 49.0) {
    Object.assign(P, TOP_SPOTS[0]); P.ry = .3; P.armR = [-1.3, -.1]; P.armL = [-1.3, .1]; P.expr = 'angry'; P.lean = .1;
    if (t > 52.2) { P.armR = t < 52.8 ? [-2.9, .1] : [-1.0, .2]; P.expr = 'smile'; P.ry = .8; }
    return P;
  }
  const mv = walkTo(t, 55.6, 57.8, DAD_SPOT, V(-40, PT, 6)); Object.assign(P, mv.p, walkPose(mv.phi)); P.ry = -Math.PI / 2 - .3; P.expr = 'smile';
  if (t > 58) { P.x = -31; P.z = 10; P.ry = .9; P.legs = [0, 0]; P.armL = P.armR = [0, .05]; }
  return P;
}
function momAt(t) {
  const P = { x: 40, z: 3, y: PT, ry: -Math.PI / 2, expr: 'calm', blink: blinkAt(t, 2) };
  if (t < 8.5) return P;
  if (t < 9.4) { const mv = walkTo(t, 8.5, 9.4, V(14, PT, 3), MOM_SPOT); Object.assign(P, mv.p); P.bob = Math.abs(Math.sin(mv.phi)) * .15; return P; }
  Object.assign(P, MOM_SPOT); P.ry = -1.0;
  if (t < 18.6) { const k = Math.floor(q(t) * 4) % 2; P.armL = k ? [-2.6, .2] : [-1.6, .5]; P.armR = k ? [-1.6, .5] : [-2.6, .2]; P.expr = t < 12.3 ? 'talk' : 'angry'; P.look = .3; return P; }
  if (t < 45.5) {
    P.ry = -.6; P.expr = t > 41 ? 'talk' : 'worried'; P.armL = [-1.1, -.1]; P.armR = [-1.1, .1]; P.nod = .25;
    if (t > 41) { P.armL = [-2.6 - .3 * Math.cos(q(t) * 9), .2]; P.expr = Math.floor(q(t) * 6 + 1) % 2 ? 'talk' : 'angry'; P.nod = 0; }
    return P;
  }
  if (t < 55.0 && t > 49.0) { Object.assign(P, TOP_SPOTS[2]); P.ry = -.3; P.armR = [-1.3, -.1]; P.armL = [-1.3, .1]; P.expr = 'angry'; return P; }
  const mv = walkTo(t, 55.8, 58.0, MOM_SPOT, V(40, PT, 6)); Object.assign(P, mv.p); P.bob = Math.abs(Math.sin(mv.phi)) * .15; P.ry = Math.PI / 2 + .3; P.expr = 'smile';
  if (t > 58) { P.x = 31; P.z = 10; P.ry = -.9; }
  return P;
}
function granAt(t) {
  const P = { x: -12, z: -30, y: PT, ry: 0, expr: 'angry', blink: blinkAt(t, 3) };
  if (t < 12.3) return P;
  if (t < 13.6) { const mv = walkTo(t, 12.3, 13.6, V(-12, PT, -22), GRAN_SPOT); Object.assign(P, mv.p, walkPose(mv.phi, .35)); P.armL = P.armR = [-2.8, .1]; return P; }
  Object.assign(P, GRAN_SPOT);
  if (t < 17.3) { const up = t > 15.0; P.armL = P.armR = [up ? -3.0 : -2.8, .1]; P.expr = t > 15 ? 'talk' : 'angry'; P.nod = -.1; return P; }
  if (t < 18.6) { P.armL = P.armR = [-1.4, .1]; P.lean = .25; P.expr = 'angry'; return P; }
  if (t < 45.5) {
    P.expr = 'angry'; P.armL = [-.3, .1]; P.armR = [-.3, .1];
    if (t > 28.7 && t < KNOCK + .6) { const u = seg(t, 29.6, KNOCK); P.armR = [lerp(-1.2, -2.4, u), lerp(.3, -1.2, u)]; P.expr = 'talk'; P.lean = .1; }
    if (t > 41) { P.armR = [-2.9, .1]; P.expr = Math.floor(q(t) * 6 + 2) % 2 ? 'talk' : 'angry'; }
    return P;
  }
  if (t < 55.0 && t > 49.0) { Object.assign(P, TOP_SPOTS[1]); P.armL = P.armR = [-1.5, .1]; P.lean = .1; P.expr = 'angry'; return P; }
  const mv = walkTo(t, 55.4, 57.6, GRAN_SPOT, V(-12, PT, -40)); Object.assign(P, mv.p, walkPose(mv.phi, .35)); P.ry = Math.PI; P.expr = 'smile';
  return P;
}

// ===================== CAMERA =====================
function shot(t) {
  const S = (pos, look, fov, focus, aper = 700) => ({ pos, look, fov, focus, aper });
  let c;
  if (t < 2.6) { const u = eio(seg(t, .9, 2.4)); c = S(V(-13, 15, -1).lerp(V(-12, 8, 24), u), V(-13, 0, -12.5).lerp(V(-12, 5, 0), u), 34, V(-13, PT, -12.5).lerp(V(-12, 6, 0), u), 700); }
  else if (t < 5.3) c = S(V(-12, 6, 27).lerp(V(-12, 6.3, 23), seg(t, 2.6, 5.3)), V(-12, 5.2, 0), 32, V(-12, 7.5, -.3), 650);
  else if (t < 8.5) c = S(V(-14, 9, 44), V(lerp(-20, -15, eio(seg(t, 5.3, 6.6))), 6, 0), 32, V(-16, 7, 1), 750);
  else if (t < 12.3) { const w = eio(seg(t, 10.2, 10.55)); c = S(V(-12, 9, 34), V(lerp(-5, -19, w), 7, 1), 28, lerp(0, 1, w) > .5 ? V(-19.5, 9, 1.5) : V(-4.5, 8.5, 1.5), 700); }
  else if (t < 18.5) { const sh = t > 17.3 && t < 17.8 ? (1 - (t - 17.3) / .5) * .8 : 0; const fr = Math.floor(t * 24); c = S(V(-12, 3, 32).add(V((hash(fr) - .5) * sh, (hash(fr + 9) - .5) * sh, 0)), V(-12, 8, -3), 38, V(-12, 9, -5), 650); }
  else if (t < 23.6) { const a = lerp(.55, -.45, eio(seg(t, 18.5, 23.6))); c = S(V(TW.x + Math.sin(a) * 30, 13, TW.z + Math.cos(a) * 30), V(TW.x, 5, TW.z), 40, V(TW.x, 5, TW.z), 450); }
  else if (t < 31.3) {
    const k = t < 25.9 ? 0 : t < 28.7 ? 1 : 2;
    const sh = t > KNOCK && t < KNOCK + .5 ? (1 - (t - KNOCK) / .5) * .9 : 0, fr = Math.floor(t * 24), j = V((hash(fr) - .5) * sh, (hash(fr + 9) - .5) * sh, 0);
    if (k === 0) c = S(V(-30, 11, 22), V(-19, 8, 1.5), 34, V(-19.5, 9.5, 1.5), 600);
    else if (k === 1) c = S(V(6, 11, 22), V(-5, 8, 1.5), 34, V(-4.5, 9.5, 1.5), 600);
    else c = S(V(-12, 11, 32).add(j), V(-12, 7.5, -3), 38, V(-12, 10, -6.5), 600);
  }
  else if (t < 37.2) { const px = lerp(-10, 2, eio(seg(t, 35.6, 37.2))); c = S(V(px, 48, 14), V(px, 0, 4), 34, V(px, PT, 6), 250); }
  else if (t < 41.0) { const u = eio(seg(t, 37.2, 41)); c = S(V(16, 26, 60).lerp(V(17, 21, 52), u), V(16, 2.5, 12), 34, V(17, 2, 11.5), 650); }
  else if (t < 45.5) c = S(V(-12, 3, 34), V(-12, 8, -2), 40, V(-12, 9, 0), 550);
  else if (t < 52.2) { const rf = ss(seg(t, 50.0, 50.6)); c = S(V(42, 6, 20), V(-12, 9, -1), 34, V(-12, 12, -1).lerp(V(21.5, 6, 12), rf), 650); }
  else if (t < 55.0) c = S(V(34, 10, 34), V(20, 5.5, 12.5), 32, V(21, 5, 12.5), 600);
  else { const u = eio(seg(t, 55.0, 60.5)); c = S(V(2, 26, 44).lerp(V(0, 78, 88), u), V(-2, 2, 0).lerp(V(-2, 0, -2), u), 38, V(-8, PT, 2), lerp(500, 300, u)); }
  return c;
}

// ===================== RENDER =====================
function render(t0) {
  const t = q(t0);
  boy.pose(boyAt(t)); dad.pose(dadAt(t)); mom.pose(momAt(t)); gran.pose(granAt(t));
  // sign
  sign.visible = t > 5.3 && t < 18.6; const si = t < 8.5 ? 0 : t < 12.3 ? 1 : 2; signPrint.material = signMats[si];
  const pop = [5.4, 8.6, 12.4][si]; sign.position.y = PT + Math.max(0, (pop + .2 - t) * 6) * (t < pop + .2 ? 1 : 0);
  // book: in Grandma's raised hands → slammed on the desk
  book.visible = t > 12.3 && t < 55;
  if (t < 17.3) { const hp = gran.arms[1].hand.getWorldPosition(V()); const hl = gran.arms[0].hand.getWorldPosition(V()); book.position.copy(hp.add(hl).multiplyScalar(.5)).add(V(0, .3, 0)); book.rotation.set(0, 0, 0); }
  else if (t < 18.6) { book.position.set(DESK.x + 1.2, DESK_TOP_Y + (t < 17.45 ? 1 : 0), DESK.z); book.rotation.set(0, .2, 0); }
  else book.visible = false;
  deskBook.position.y = 2 * BRICK + PLATE + (t > 17.3 && t < 17.55 ? .6 : 0);
  // laptop + phone
  laptop.visible = t > 23.6 && t < 45.5; laptop.position.copy(dad.arms[1].hand.getWorldPosition(V())).lerp(dad.arms[0].hand.getWorldPosition(V()), .5).add(V(0, .2, 0)); laptop.rotation.y = .6;
  phone.visible = t > 25.9 && t < 45.5; phone.position.copy(mom.arms[0].hand.getWorldPosition(V())).add(V(.4, .9, .3)); phone.rotation.set(-.4, -.6, 0);
  // tower bricks
  for (const b of towerBricks) {
    if (t < b.t) { b.m.visible = false; continue; }
    b.m.visible = true;
    if (b.fall && t >= KNOCK) { const f = Math.min(b.fall.length - 1, Math.floor((t - KNOCK) * 24)); b.m.position.copy(b.fall[f][0]); b.m.rotation.set(b.fall[f][1].x, b.fall[f][1].y, b.fall[f][1].z); }
    else { b.m.position.copy(flyPos(b.to, t, b.t)); b.m.rotation.set(0, 0, 0); }
    if (t > 55.4) {   // taken apart: flies up and away, top first
      const k = 55.4 + (10 - b.layer) * .2; if (t > k) { const u = ei(seg(t, k, k + .6)); b.m.position.add(V(0, u * 60, -u * 30)); if (u >= 1) b.m.visible = false; }
      if (b.fall) b.m.visible = t < 56.6;
    }
  }
  deskG.visible = !(t > 21.2 && t < 57.6);
  pedsovet.visible = t > 22.0 && t < 55.4; pedsovet.position.copy(flyPos(V(TW.x, PT + 3.4, TW.z + 3.05), t, 22.0, .45)); pedsovet.rotation.set(Math.PI / 2, 0, 0);
  wheel.visible = t > 49.3 && t < 55.4; wheel.position.copy(flyPos(V(TW.x, DECK_Y + 2.6, TW.z + 1.2), t, 49.3, .5)); wheel.rotation.set(-.4, 0, Math.sin(q(t) * 4) * .5 * seg(t, 49.8, 50.2));
  // answers + paper balls
  answers.forEach((a, i) => { const t0 = [31.7, 32.2, 32.7][i]; a.visible = t > t0 && t < 55.6; a.position.copy(flyPos(V(a.userData.x, PT, a.userData.z), t, t0, .4)); a.rotation.y = a.userData.r; });
  balls.forEach((b, i) => { const t0 = [33.4, 33.8, 34.2, 34.6][i]; b.visible = t > t0 && t < 55.8; const u = seg(t, t0, t0 + .35); b.position.set(b.userData.x, lerp(25, PT + 1.1, ei(u)) + (u >= 1 ? Math.max(0, .6 * Math.sin((t - t0 - .35) * 18) * (1 - (t - t0 - .35) / .4)) : 0), b.userData.z); b.rotation.set(t0, i, 0); });
  // the boy's answer plates
  pix.forEach(p => { p.m.visible = t > p.t; p.m.position.copy(flyPos(p.to, t, p.t, .3, p.to.clone().add(V(4, 6, 1)))); });
  // Dad's hint brick
  hint.visible = t > 52.6; if (hint.visible) { const A = V(-14, DECK_Y + 4, -1), B = CORNER.clone().add(V(-1.5, 0, 2.2)), u = seg(t, 52.6, 53.8); const p = A.clone().lerp(B, u); p.y += Math.sin(u * Math.PI) * 16; hint.position.copy(u >= 1 ? flyPos(B, t, 52.6, 1.2) : p); hint.rotation.set(0, u * 6, 0); }
  five.visible = t > 58.6; five.position.copy(flyPos(V(-3.5, PT, -12.2), t, 58.6, .45)); five.rotation.y = -.1;

  // camera
  const c = shot(t0);
  camera.position.copy(c.pos); camera.fov = c.fov; camera.updateProjectionMatrix(); camera.lookAt(c.look);
  const k = set.key, fc = c.focus, span = t > 55 ? 60 : t > 31.3 && t < 37.2 ? 34 : 26;
  k.target.position.copy(fc); k.position.copy(fc).add(V(-60, 110, 50)); k.target.updateMatrixWorld();
  Object.assign(k.shadow.camera, { left: -span, right: span, top: span, bottom: -span }); k.shadow.camera.updateProjectionMatrix();
  post.dof.focus = camera.position.distanceTo(fc); post.dof.aper = c.aper; post.dof.maxCoc = 14;
  post.composer.render();
}

// ===================== EVENTS (foley) =====================
const EV = [], ev = (type, t, o = {}) => EV.push({ type, t: +t.toFixed(3), ...o });
[5.4, 8.6, 12.4].forEach(t => ev('click', t + .2, { v: 1 }));
ev('thump', 17.3, { v: 1 }); ev('clack', 17.35, { v: .7 });
towerBricks.forEach(b => ev('click', b.t + .45, { v: .45, pitch: .9 + hash(b.t) * .3 }));
ev('click', 22.45, { v: .9 }); ev('click', 49.8, { v: 1 });
ev('crash', KNOCK, { v: 1 }); for (let k = 0; k < 18; k++) ev('clack', KNOCK + .3 + Math.pow(k / 18, 1.5) * 1.6 + hash(k) * .08, { v: 1 - k / 22 });
[31.7, 32.2, 32.7].forEach(t => ev('click', t + .4, { v: .9 })); [33.4, 33.8, 34.2, 34.6].forEach(t => ev('paper', t + .35, { v: .8 }));
pix.forEach((p, i) => { if (i % 2 === 0) ev('click', p.t + .3, { v: .5, pitch: 1.3 }); }); ev('ding', 40.3, { v: .8 });
ev('whoosh', 52.7, { v: .5 }); ev('click', 53.8, { v: 1.1 });
for (let k = 0; k < 11; k++) ev('whoosh', 55.4 + (10 - k) * .2, { v: .25 });
ev('click', 59.05, { v: 1.2 });
for (const [f, a, b] of [[dadAt, 5.3, 6.5], [momAt, 8.5, 9.4], [granAt, 12.3, 13.6], [boyAt, 35.8, 37.2], [dadAt, 55.6, 57.8], [granAt, 55.4, 57.6]]) { let last = null; for (let x = a; x < b; x += 1 / 12) { const l = f(x).legs?.[0] ?? Math.sin(x * 9); const s = Math.sign(l); if (last !== null && s !== last) ev('step', x, { v: .45 }); last = s; } }
EV.sort((a, b) => a.t - b.t);

window.render = render; window.DUR = DUR; window.EV = EV;
render(0);
window.READY = true;
