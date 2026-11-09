// «Домашка» — Paper Pop-up Book. 1080×1920, 24 fps; timings follow the user's original voice-over.
import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clamp, lerp, seg, ss, eio, eo, ei, back, spring, TAU, mulberry, track, hash } from './lib.js';
import * as A from './art.js';
import { cv } from './paper.js';
import { makeBook, texOf, BW, BD, PG } from './book.js';
import { cutMesh, blobShadow, thread } from './cutmesh.js';
import { makePost } from './post.js';

await document.fonts.load('80px Neucha');
const W = innerWidth, H = innerHeight, DUR = 60.8;
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('stage').appendChild(renderer.domElement);
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(40, W / H, .004, 30);
const post = makePost(renderer, scene, cam, W, H);
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const q = t => Math.floor(t * 12 + 1e-6) / 12;

// ---------- the real room ----------
const PH = '/core/assets/polyhaven/';
const hdr = await new RGBELoader().loadAsync(PH + 'lythwood_lounge_2k.hdr'); hdr.mapping = THREE.EquirectangularReflectionMapping;
scene.environment = hdr; scene.background = hdr; scene.backgroundBlurriness = .22;
scene.backgroundRotation.set(0, 2.3, 0); scene.environmentRotation.set(0, 2.3, 0); scene.environmentIntensity = .38; scene.backgroundIntensity = .7;
const tl = new THREE.TextureLoader();
const wt = n => { const t = tl.load(`${PH}walnut_${n}.jpg`); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2.2, 1.4); t.anisotropy = 12; return t; };
const wdiff = wt('diff'); wdiff.colorSpace = THREE.SRGBColorSpace;
const desk = new THREE.Mesh(new THREE.BoxGeometry(2.6, .04, 1.7), new THREE.MeshStandardMaterial({ map: wdiff, normalMap: wt('nor'), roughnessMap: wt('rough'), color: '#c9a88a', envMapIntensity: .8 }));
desk.position.set(0, -.02, .25); desk.receiveShadow = true; scene.add(desk);
const lamp = (await new GLTFLoader().loadAsync(`${PH}desk_lamp_arm_01/desk_lamp_arm_01.gltf`)).scene;
lamp.position.set(-.36, 0, .02); lamp.scale.setScalar(.55); lamp.rotation.y = -.2; lamp.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; }); scene.add(lamp);
// a real pencil lying on the desk (it plays a part when the boy steps off the page)
const pencil = new THREE.Group();
{ const body = new THREE.Mesh(new THREE.CylinderGeometry(.0038, .0038, .15, 6), new THREE.MeshStandardMaterial({ color: '#f2b632', roughness: .5 }));
  const wood = new THREE.Mesh(new THREE.CylinderGeometry(.0038, .0008, .018, 6), new THREE.MeshStandardMaterial({ color: '#e8c79a', roughness: .8 }));
  const lead = new THREE.Mesh(new THREE.CylinderGeometry(.0008, .0001, .004, 6), new THREE.MeshStandardMaterial({ color: '#333', roughness: .4 }));
  const ferr = new THREE.Mesh(new THREE.CylinderGeometry(.004, .004, .012, 12), new THREE.MeshStandardMaterial({ color: '#c9c2b0', metalness: 1, roughness: .3 }));
  const eras = new THREE.Mesh(new THREE.CylinderGeometry(.0039, .0039, .01, 12), new THREE.MeshStandardMaterial({ color: '#e88a8a', roughness: .9 }));
  wood.position.y = .084; lead.position.y = .095; ferr.position.y = -.081; eras.position.y = -.092;
  pencil.add(body, wood, lead, ferr, eras); pencil.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; });
  pencil.rotation.set(0, -.35, Math.PI / 2); pencil.position.set(.37, .0038, .41); scene.add(pencil); }

// ---------- lights ----------
const sun = new THREE.DirectionalLight('#fff3e0', 2.4); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -.00008; sun.shadow.normalBias = .0003; sun.shadow.radius = 4;
Object.assign(sun.shadow.camera, { left: -.4, right: .4, top: .4, bottom: -.4, near: .1, far: 3 }); sun.position.set(-.35, .55, .75); sun.target.position.set(0, .05, .15); scene.add(sun, sun.target);
const hemi = new THREE.HemisphereLight('#cfe6ff', '#caa27a', .5); scene.add(hemi);
const bulb = new THREE.PointLight('#ffcf94', .35, .8, 2); bulb.position.set(-.3, .36, .1); scene.add(bulb);

// ---------- the book ----------
const cw = 2048, chh = Math.round(2048 * BD / BW), cc = cv(cw, chh), cm = cv(cw, chh); A.coverArt(cc, cm);
const book = makeBook({ c: cc, m: cm }); scene.add(book.root);
book.groundMat.map = texOf(A.floorPage()); book.backMat.map = texOf(A.wallPage());
book.root.position.set(0, 0, 0);
const S = book.stage, SKY = book.sky;

// pop-up helper: a card lying flat that springs up around its bottom edge
const pops = [];
function pop(parent, item, x, y, z, { t0, d = .5, fold = null, s = 1, flatSide = 1 } = {}) {
  const g = new THREE.Group(), m = cutMesh(item, { s }); g.add(m); g.position.set(x, y, z); parent.add(g);
  const P = { g, t0, d, fold, flatSide }; pops.push(P); return P;
}
function updatePops(t) {
  for (const P of pops) {
    let k = back(seg(t, P.t0, P.t0 + P.d), 1.6);
    if (P.fold) k = Math.min(k, 1 - eio(seg(t, P.fold, P.fold + .45)));
    P.g.visible = k > .003; P.g.rotation.x = -P.flatSide * (Math.PI / 2) * (1 - k);
  }
}

// backdrop pieces (on the standing page)
pop(SKY, A.shelf(), -.12, .2, .004, { t0: 1.9, d: .5, flatSide: -1 });
pop(SKY, A.window_(), .13, .17, .004, { t0: 2.0, d: .5, flatSide: -1 });
const clock = pop(SKY, A.clockCard(), 0, .23, .005, { t0: 2.1, d: .5, flatSide: -1 });
const handMat = it => cutMesh(it);
const hHr = handMat(A.hand(.016, .0028)), hMin = handMat(A.hand(.021, .002));
clock.g.add(hHr, hMin); hHr.position.set(0, .025 + .0003, .001); hMin.position.set(0, .025 + .0003, .0015);
const tags = ['+5 мин', '+10 мин', '+5 мин'].map((s, i) => pop(SKY, A.tag(s), 0, .17 - i * .022, .006, { t0: [5.4, 8.6, 12.4][i], d: .4, flatSide: -1, fold: 55.2 }));
// «ПЕДСОВЕТ» on strings
const ban = new THREE.Group(); SKY.add(ban); ban.add(cutMesh(A.banner('ПЕДСОВЕТ')));
const strings = [-.07, .07].map(x => { const th = thread(.2); th.position.set(x, .04, 0); ban.add(th); return th; });

// floor pieces
const deskCard = pop(S, A.desk(), -.03, 0, .15, { t0: 2.2, d: .5 });
const ansCards = [['54', '#e8a92c', -.1, .225, -.25], ['65', '#f2705a', -.035, .245, .1], ['48', '#8a4590', .035, .225, .3]].map(([s, c, x, z, r], i) => {
  const g = new THREE.Group(); g.add(cutMesh(A.sheet(s, c))); g.rotation.set(-Math.PI / 2, 0, r); g.position.set(x, .0006, z); S.add(g); g.userData = { t0: [31.7, 32.2, 32.7][i], x, z }; return g; });
const crumps = [[-.13, .265], [.07, .26], [-.06, .275], [.01, .28]].map(([x, z], i) => pop(S, A.crumple(10 + i), x, 0, z, { t0: [33.4, 33.8, 34.2, 34.6][i], d: .3, fold: 55.3 }));
const deskSheets = [0, 1, 2].map(i => { const g = new THREE.Group(); g.add(cutMesh(A.sheet(['?', '…', '×'][i], '#23317a'), { s: .5 })); g.rotation.set(-1.1, 0, (i - 1) * .4); S.add(g); return g; });
const consoleP = pop(S, A.consoleCard(), -.03, 0, .03, { t0: 45.6, d: .8, fold: 55.4 });
const fiveP = pop(S, A.five(), .1, 0, .21, { t0: 58.6, d: .45 });
const bubHelp = pop(S, A.bubble('help'), .02, .068, .13, { t0: 3.4, d: .35, fold: 5.1 });
const bubZig = pop(S, A.bubble('zig'), -.02, .1, .17, { t0: 10.6, d: .35, fold: 12.3 });
// the boy's own answer, on the real desk
const ansReal = new THREE.Group(); ansReal.add(cutMesh(A.answerCard())); scene.add(ansReal); ansReal.position.set(.272, 0, .345); ansReal.rotation.y = -.25;
const hint = new THREE.Group(); hint.add(cutMesh(A.cut(.02, .012, (x) => { x.translate(70, 40); A.HOLD.arrow(x); }, { ay: .5 }))); scene.add(hint);

// ---------- the family: flat cards redrawn per pose ----------
function makeChar(who, Hm) {
  const c = cv(A.FW, A.FH); A.drawPerson(c.getContext('2d'), who, {});
  const t = texOf(c), w = Hm * A.FW / A.FH, ay = 1050 / A.FH;
  const geo = new THREE.PlaneGeometry(w, Hm); geo.translate(0, ay * Hm - Hm / 2, 0);
  const front = new THREE.MeshStandardMaterial({ map: t, alphaTest: .5, alphaToCoverage: true, roughness: .85, side: THREE.FrontSide });
  const backM = new THREE.MeshStandardMaterial({ map: t, alphaTest: .5, alphaToCoverage: true, roughness: .9, side: THREE.BackSide });
  backM.onBeforeCompile = s => { s.fragmentShader = s.fragmentShader.replace('#include <map_fragment>', '#include <map_fragment>\n diffuseColor.rgb = vec3(.94,.91,.85);'); };
  const f = new THREE.Mesh(geo, front), b = new THREE.Mesh(geo, backM);
  f.castShadow = true; f.receiveShadow = true; f.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: t, alphaTest: .5, side: THREE.DoubleSide });
  const root = new THREE.Group(), flip = new THREE.Group(), fold = new THREE.Group(); root.add(fold); fold.add(flip); flip.add(f, b);
  const sh = blobShadow(Hm * .22, .4); root.add(sh); sh.position.y = .0004;
  let key = '';
  return { root, flip, fold, Hm, pose(p) { const k = JSON.stringify(p, (kk, v) => typeof v === 'number' ? Math.round(v * 30) / 30 : typeof v === 'function' ? v.name : v); if (k === key) return; key = k; A.drawPerson(c.getContext('2d'), who, p); t.needsUpdate = true; } };
}
const boy = makeChar('boy', .068), dad = makeChar('dad', .1), mom = makeChar('mom', .094), gran = makeChar('gran', .122);
for (const c of [boy, dad, mom, gran]) S.add(c.root);
const pd = { laptop: function laptop(x) { A.HOLD.laptop(x); }, phone: function phone(x) { A.HOLD.phone(x); }, book: function book(x) { A.HOLD.book(x); } };

const blink = (t, k) => Math.floor(t * 12 + k * 7) % 43 === 0;
const talk = (t, ph = 0) => Math.floor(q(t) * 6 + ph) % 2 ? 'open' : 'smile';
const popK = (t, t0, f = 99) => Math.min(back(seg(t, t0, t0 + .5), 1.6), 1 - eio(seg(t, f, f + .45)));

function charsAt(t) {
  const tq = q(t);
  // —— boy ——
  let B = { x: -.03, y: 0, z: .135, face: 1, k: popK(t, 2.3), p: { eyes: 'open', mouth: 'smile', blink: blink(t, 0) } };
  if (t > 3.2 && t < 5.3) B.p = { ...B.p, armR: 2.6, mouth: 'smile' };
  if (t >= 5.3 && t < 35.8) { B.x = -.03 + (t > 6.2 ? .022 : 0) + (t > 34.8 ? .05 * eo(seg(t, 34.8, 35.6)) : 0); B.p = { ...B.p, mouth: t > 17.3 && t < 18.4 ? 'open' : 'flat', eyes: t > 17.3 && t < 18.4 ? 'wide' : 'open', look: t < 8.5 ? [-1, 0] : t < 12.3 ? [1, 0] : [0, -1], brows: t > 18.6 ? 'worried' : null }; }
  if (t >= 35.8 && t < 37.6) {   // walks to the page edge and hops down onto the real desk
    const u = seg(t, 35.8, 37.0), w = eio(u), A0 = V(.05, 0, .135), A1 = V(.2, 0, .29);
    const p = A0.clone().lerp(A1, w); B.x = p.x; B.z = p.z; B.y = 0;
    if (t > 37.0) { const h = seg(t, 37.0, 37.5); B.x = lerp(.2, .245, h); B.z = lerp(.29, .345, h); B.y = lerp(0, -PG, h) + Math.sin(h * Math.PI) * .012; }
    B.p = { walk: u * 26, stride: u > 0 && u < 1 ? 1 : 0, mouth: 'flat', look: [1, 0], armL: .25 + Math.sin(u * 26) * .4, armR: .25 - Math.sin(u * 26) * .4 };
  }
  if (t >= 37.6 && t < 57.8) { B.x = .245; B.y = -PG; B.z = .348; B.face = 1;
    B.p = { mouth: (t > 39.8 && t < 50) || t > 53.9 ? 'big' : 'flat', eyes: t > 39.8 && t < 41 ? 'happy' : t > 50.2 && t < 52.4 ? 'wide' : 'open', look: t > 45 && t < 53.6 ? [-1, -1] : [1, .5], armR: t < 39.8 ? .5 + .3 * Math.sin(tq * 14) : t < 41 ? 2.6 : .2, blink: blink(t, 0) };
    if (t > 53.8) B.p.armR = 1.6;
  }
  if (t >= 57.8) { B.p = { mouth: t > 59.4 ? 'big' : 'smile', eyes: t > 59.4 ? 'happy' : 'open', look: [0, 1], armR: .5 }; }
  // —— dad ——
  const D = { x: -.11, y: 0, z: .162, face: 1, k: popK(t, 5.4, 55.6), p: { mouth: t < 8.5 ? 'big' : 'wavy', brows: t < 8.5 ? null : 'worried', armR: 1.2, armL: .3 + .2 * Math.sin(tq * 8), look: [1, .6], blink: blink(t, 1) } };
  if (t > 10.2 && t < 12.3) D.p.look = [1, -.4];
  if (t > 23.6 && t < 45.5) { D.p = { mouth: 'open', eyes: 'wide', brows: 'up', armR: .9, armL: .9, holdR: pd.laptop, look: [0, .6] }; }
  if (t > 41 && t < 45.5) { D.p = { mouth: talk(t), brows: 'angry', armR: 2.5 + .3 * Math.sin(tq * 9), armL: .4, look: [1, 0] }; }
  if (t > 45.5 && t < 52.2) { D.p = { mouth: 'open', brows: 'angry', armR: 2.7, armL: 2.7, look: [0, -1] }; }
  if (t > 52.2 && t < 55.6) { D.p = { mouth: 'smile', brows: null, armR: t < 52.8 ? 2.4 : 1.4, armL: .3, look: [1, .4] }; }
  // —— mom ——
  const M = { x: .065, y: 0, z: .166, face: -1, k: popK(t, 8.6, 55.8), p: { mouth: t < 12.3 ? talk(t) : 'frown', brows: 'angry', armR: Math.floor(tq * 4) % 2 ? 1.6 : 2.5, armL: .3, look: [1, 0], blink: blink(t, 2) } };
  if (t > 25.9 && t < 45.5) M.p = { mouth: 'wavy', brows: 'worried', armR: 1.0, armL: .4, holdR: pd.phone, look: [0, .8] };
  if (t > 41 && t < 45.5) M.p = { mouth: talk(t, 1), brows: 'angry', armR: 2.5 + .3 * Math.cos(tq * 9), armL: .4, look: [1, 0] };
  if (t > 45.5 && t < 55.8) M.p = { mouth: 'open', brows: 'angry', armR: 2.7, armL: 2.7, look: [0, -1] };
  // —— grandma ——
  const G = { x: -.03, y: 0, z: .075, face: 1, k: popK(t, 12.4, 55.4), p: { mouth: 'frown', brows: 'angry', armR: 2.9, armL: 2.9, holdR: pd.book, look: [0, .4], blink: blink(t, 3) } };
  if (t > 15 && t < 17.3) G.p = { ...G.p, mouth: talk(t, 2), armR: 3.0, armL: 3.0 };
  if (t >= 17.3 && t < 45.5) { G.p = { mouth: 'frown', brows: 'angry', armR: .6, armL: .3, look: [0, .8] };
    if (t > 28.7 && t < 31.3) G.p = { mouth: t > 30.3 ? 'open' : 'frown', brows: 'angry', armR: t < 30.3 ? 2.2 : .8, armL: .3, look: [1, .8] };
    if (t > 41) G.p = { mouth: talk(t, 3), brows: 'angry', armR: 2.8, armL: .3, look: [1, 0] }; }
  if (t > 45.5) G.p = { mouth: 'open', brows: 'angry', armR: 2.7, armL: 2.7, look: [0, -1] };
  return { B, D, M, G };
}

// ---------- camera ----------
const SH = [
  [[0, 0, .8, .62, 0, .0, .14, 40, 1.6], [1.6, 0, .45, .62, 0, .03, .12, 40, 2.0], [2.6, -.02, .2, .52, -.03, .05, .12, 38, 2.2]],
  [[2.6, -.03, .07, .4, -.03, .045, .13, 34, 2.6], [5.3, -.03, .068, .36, -.03, .045, .13, 34, 2.6]],
  [[5.3, -.06, .08, .5, -.075, .055, .14, 38, 2.6], [8.5, -.065, .078, .46, -.07, .055, .14, 38, 2.6]],
  [[8.5, -.02, .08, .46, .065, .06, .16, 36, 2.6], [10.15, -.02, .08, .46, .06, .06, .16, 36, 2.6], [10.5, -.02, .08, .46, -.11, .06, .16, 36, 2.6], [12.3, -.02, .08, .45, -.11, .06, .16, 36, 2.6]],
  [[12.3, -.03, .03, .48, -.03, .095, .07, 44, 2.4], [18.5, -.03, .035, .44, -.03, .095, .07, 44, 2.4]],
  [[18.5, .2, .22, .58, -.02, .08, .1, 40, 1.8], [23.6, .12, .28, .6, -.02, .09, .1, 40, 1.8]],
  [[23.6, -.16, .09, .44, -.11, .06, .16, 36, 2.6], [25.9, -.16, .09, .43, -.11, .06, .16, 36, 2.6]],
  [[25.9, .11, .09, .44, .065, .06, .166, 36, 2.6], [28.7, .11, .09, .43, .065, .06, .166, 36, 2.6]],
  [[28.7, -.03, .11, .48, -.03, .08, .09, 42, 2.4], [31.3, -.03, .11, .46, -.03, .08, .09, 42, 2.4]],
  [[31.3, 0, .62, .3, 0, 0, .19, 38, 1.2], [35.6, 0, .62, .3, 0, 0, .19, 38, 1.2], [37.2, .12, .6, .45, .14, 0, .27, 38, 1.2]],
  [[37.2, .37, .04, .58, .265, .02, .345, 34, 3.2], [41.0, .35, .04, .53, .26, .02, .345, 34, 3.2]],
  [[41.0, -.2, .2, .5, -.02, .06, .12, 40, 1.8], [45.5, -.17, .18, .46, -.02, .06, .12, 40, 1.8]],
  [[45.5, -.03, .014, .36, -.03, .085, .05, 46, 2.0], [50.2, -.03, .012, .33, -.03, .09, .05, 46, 2.0]],
  [[50.2, .34, .02, .5, .245, .03, .348, 32, 3.0], [52.2, .33, .02, .48, .245, .03, .348, 32, 3.0]],
  [[52.2, .35, .04, .52, .255, .022, .35, 36, 3.0], [55.0, .34, .04, .51, .255, .022, .35, 36, 3.0]],
  [[55.0, .05, .2, .62, 0, .03, .14, 40, 1.8], [60.8, .05, .4, .76, 0, .02, .15, 40, 1.4]],
];
const SHOTS = SH.map(keys => ({ t0: keys[0][0], f: track(keys.map(k => [k[0], k.slice(1)])) }));
const focusOf = t => {   // focus target per shot (world)
  if (t < 2.6) return V(0, PG + .02, .14);
  if (t < 5.3) return V(-.03, PG + .05, .135);
  if (t < 8.5) return V(-.08, PG + .05, .16);
  if (t < 12.3) return t < 10.3 ? V(.065, PG + .05, .166) : V(-.11, PG + .05, .162);
  if (t < 18.5) return V(-.03, PG + .085, .075);
  if (t < 23.6) return V(-.03, PG + .06, .12);
  if (t < 25.9) return V(-.11, PG + .05, .162);
  if (t < 28.7) return V(.065, PG + .05, .166);
  if (t < 31.3) return V(-.03, PG + .07, .075);
  if (t < 37.2) return V(.02, PG, .2);
  if (t < 41.0) return t < 38.2 ? V(.34, .004, .42) : V(.255, .03, .345);
  if (t < 45.5) return V(-.03, PG + .06, .12);
  if (t < 50.2) return V(-.03, PG + .08, .05);
  if (t < 55.0) return V(.248, .03, .348);
  return V(-.02, PG + .02, .14);
};

// ---------- render ----------
function render(t0) {
  const t = t0, tq = q(t);
  // book opens
  book.setOpen(Math.PI / 2 * eio(seg(t, .3, 2.0)));
  updatePops(t);
  // clock hands race forward on each jump of time
  const jumps = [5.4, 8.6, 12.4].reduce((a, j, i) => a + eio(seg(t, j, j + .5)) * [5, 10, 5][i], 0);
  hMin.rotation.z = -(jumps / 60) * TAU - .3; hHr.rotation.z = -(jumps / 720) * TAU - 1.6;
  // banner drops on strings, swinging; leaves at the end
  const drop = spring(t - 19.4, 6, .3), up = eio(seg(t, 55.2, 55.9));
  ban.position.set(-.03, lerp(.42, .25, clamp(drop, 0, 1.2)) + up * .25, .02); ban.rotation.z = Math.sin((t - 19.4) * 6) * .08 * Math.exp(-(t - 19.4) * .8) * (t > 19.4 ? 1 : 0);
  ban.visible = t > 19.3 && t < 56;
  // characters
  const C = charsAt(t);
  for (const [ch, s] of [[boy, C.B], [dad, C.D], [mom, C.M], [gran, C.G]]) {
    ch.root.visible = s.k > .003; ch.root.position.set(s.x, s.y, s.z); ch.fold.rotation.x = -(Math.PI / 2) * (1 - clamp(s.k, 0, 1.2)); ch.flip.scale.x = s.face; ch.pose(s.p);
  }
  // Grandma's slam: everything on the floor jumps
  const jolt = t > 17.3 && t < 17.7 ? Math.sin((t - 17.3) * 40) * .002 * (1 - (t - 17.3) / .4) : 0;
  deskCard.g.position.y = Math.abs(jolt); boy.root.position.y += Math.abs(jolt);
  // drafts on the desk, swept away by «start over»
  deskSheets.forEach((g, i) => { const t0s = 24 + i * .6; g.visible = t > t0s && t < 31.5; const sw = ei(seg(t, 30.35, 31.1)); g.position.set(-.05 + i * .02 + sw * (.1 + i * .05), .036 + sw * .05, .148 + sw * .12); g.rotation.z = (i - 1) * .4 + sw * 6; });
  // answer sheets drop flat; crumples pop
  ansCards.forEach(g => { const u = seg(t, g.userData.t0, g.userData.t0 + .35); g.visible = t > g.userData.t0 && t < 55.6; g.position.y = .0006 + (1 - eo(u)) * .08; });
  // the boy's own answer on the real desk unfolds
  const ak = popK(t, 38.3, 99); ansReal.visible = ak > .003; ansReal.rotation.set(-(Math.PI / 2) * (1 - ak), -.25, 0);
  // Dad's hint
  { const u = seg(t, 52.7, 53.8); hint.visible = t > 52.7; const A0 = V(-.09, PG + .07, .17), A1 = V(.258, .004, .36); const p = A0.clone().lerp(A1, eo(u)); p.y += Math.sin(u * Math.PI) * .06; hint.position.copy(p); hint.rotation.set(u >= 1 ? -Math.PI / 2 : u * 8, .3, 0); }
  // camera
  let s = SHOTS[0]; for (const X of SHOTS) if (t >= X.t0) s = X;
  const v = s.f(t);
  let shake = 0; if (t > 17.3 && t < 17.7) shake = .002 * (1 - (t - 17.3) / .4);
  cam.position.set(v[0] + (hash(Math.floor(t * 24)) - .5) * shake, v[1] + (hash(Math.floor(t * 24) + 7) - .5) * shake, v[2]); cam.fov = v[6]; cam.lookAt(v[3], v[4], v[5]); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  post.dof.focus = cam.position.distanceTo(focusOf(t)); post.dof.aper = v[7]; post.dof.maxCoc = 14;
  post.vig.uniforms.warm.value = .12;
  scene.updateMatrixWorld(true);
  post.composer.render();
}

// ---------- sound events ----------
const EV = [];
EV.push({ t: .3, type: 'creak' }, { t: 2.0, type: 'thump' });
for (const P of pops) EV.push({ t: P.t0 + .1, type: 'pop' }), P.fold && P.fold < 60 && EV.push({ t: P.fold + .1, type: 'fold' });
[2.3, 5.4, 8.6, 12.4].forEach(x => EV.push({ t: x + .1, type: 'pop', v: 1.2 }));
[55.4, 55.6, 55.8].forEach(x => EV.push({ t: x + .1, type: 'fold' }));
EV.push({ t: 17.3, type: 'thump', v: 1.2 }, { t: 19.4, type: 'drop' }, { t: 30.35, type: 'swish' }, { t: 37.0, type: 'hop' }, { t: 37.5, type: 'land' }, { t: 38.3, type: 'pop' }, { t: 40.0, type: 'ding' }, { t: 52.7, type: 'swish' }, { t: 53.8, type: 'land' });
[31.7, 32.2, 32.7].forEach(x => EV.push({ t: x + .3, type: 'paper' }));
for (let x = 35.8; x < 37; x += .2) EV.push({ t: +x.toFixed(2), type: 'tap' });
EV.sort((a, b) => a.t - b.t);

window.render = render; window.DUR = DUR; window.EV = EV;
render(0);
window.READY = true;
