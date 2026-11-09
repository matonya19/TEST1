// Brick-built family. Origin at the feet, facing +z. Limbs rotate at hips/shoulders; nothing bends.
import * as THREE from 'three';
import { COL, BRICK, PLATE, brick, plate, mesh, roundGeo, coneGeo, plastic } from './bricks.js';

export const FC = {
  teal: '#1aa39a', navy: '#1f3a6e', mustard: '#e0a22a', brown: '#6b4226', coral: '#f06a55', plum: '#7d3c86',
  grey: '#b8b8be', skin: '#f3cfa6', hair: '#5a3418', dark: '#1b2a34',
};
const SPEC = {
  boy:  { legs: 2, legCol: FC.navy, torso: [2, 2], tH: 2, top: FC.teal, armN: 2, hair: 'boy' },
  dad:  { legs: 3, legCol: FC.brown, torso: [2, 2], tH: 2, top: FC.mustard, armN: 3, hair: 'dad', glasses: true },
  mom:  { legs: 0, skirt: FC.navy, torso: [2, 2], tH: 2, top: FC.coral, armN: 3, hair: 'mom' },
  gran: { legs: 2, legCol: FC.grey, torso: [3, 2], tH: 2, top: FC.plum, armN: 2, hair: 'gran', glasses: true, wide: true },
};

const darkMat = new THREE.MeshPhysicalMaterial({ color: FC.dark, roughness: .25, clearcoat: .8 });
function face(head, R) {
  // eyes, brows and a few interchangeable mouths on the front of a round head
  const f = new THREE.Group(); f.position.set(0, BRICK * .95, 0); head.add(f);
  const eyes = [-.38, .38].map(x => { const e = new THREE.Mesh(new THREE.CylinderGeometry(.16, .16, .08, 20), darkMat); e.rotation.x = Math.PI / 2; e.position.set(x, .2, R + .02); f.add(e); return e; });
  const brows = [-.38, .38].map(x => { const b = new THREE.Mesh(new THREE.BoxGeometry(.42, .09, .06), darkMat); b.position.set(x, .55, R + .02); f.add(b); return b; });
  const arc = (a0, len, r = .32) => { const m = new THREE.Mesh(new THREE.TorusGeometry(r, .055, 8, 24, len), darkMat); m.rotation.z = a0; m.position.set(0, -.2, R + .02); f.add(m); return m; };
  const mouths = {
    smile: arc(Math.PI + .5, Math.PI - 1), frown: (() => { const m = arc(.5, Math.PI - 1); m.position.y = -.55; return m; })(),
    flat: (() => { const m = new THREE.Mesh(new THREE.BoxGeometry(.5, .08, .06), darkMat); m.position.set(0, -.35, R + .02); f.add(m); return m; })(),
    open: (() => { const m = new THREE.Mesh(new THREE.CylinderGeometry(.2, .2, .08, 20), new THREE.MeshPhysicalMaterial({ color: '#5a1622', roughness: .3, clearcoat: .8 })); m.rotation.x = Math.PI / 2; m.position.set(0, -.38, R + .02); f.add(m); return m; })(),
    big: arc(Math.PI + .25, Math.PI - .5, .4),
  };
  function set(expr = 'calm', blink = false) {
    const mo = { calm: 'smile', smile: 'smile', happy: 'big', frown: 'frown', angry: 'frown', open: 'open', talk: 'open', surprised: 'open', worried: 'flat', flat: 'flat' }[expr] || 'smile';
    for (const k in mouths) mouths[k].visible = k === mo;
    eyes.forEach(e => e.scale.set(1, 1, blink ? .2 : 1));
    eyes.forEach(e => e.scale.x = expr === 'surprised' ? 1.3 : 1);
    const b = { angry: [.35, .12], worried: [-.3, .1], surprised: [0, .2] }[expr] || [0, 0];
    brows[0].rotation.z = -b[0]; brows[1].rotation.z = b[0]; brows.forEach(x => x.position.y = .55 + b[1]);
  }
  set(); return set;
}

export function makeFig(who) {
  const S = SPEC[who];
  const root = new THREE.Group(), body = new THREE.Group(); root.add(body);
  let hip = 0;
  const legs = [];
  if (S.legs) {
    hip = PLATE + S.legs * BRICK;
    for (const x of [-.5, .5]) {
      const g = new THREE.Group(); g.position.set(x * (S.wide ? 1.4 : 1), hip, 0); body.add(g);
      for (let i = 0; i < S.legs; i++) { const b = brick(1, 1, S.legCol); b.position.y = -hip + PLATE + i * BRICK; g.add(b); }
      const f = plate(1, 2, FC.dark); f.position.set(0, -hip, .3); g.add(f);
      legs.push(g);
    }
    const hp = plate(S.torso[0], 2, S.legCol); hp.position.y = hip; body.add(hp); hip += PLATE;
  } else {   // skirt: a cone
    const sk = mesh(coneGeo(2.1, 3.4), S.skirt); sk.scale.set(1, 1, .8); body.add(sk); hip = 3.4;
  }
  for (let i = 0; i < S.tH; i++) { const b = brick(S.torso[0], S.torso[1], S.top); b.position.y = hip + i * BRICK; body.add(b); }
  const sh = hip + S.tH * BRICK;
  const ax = S.torso[0] / 2 + .5;
  const arms = [-ax, ax].map(x => {
    const g = new THREE.Group(); g.position.set(x, sh - .1, 0); body.add(g);
    for (let i = 0; i < S.armN; i++) { const b = mesh(roundGeo(.5), S.top); b.position.y = -S.armN * BRICK + i * BRICK; g.add(b); }
    const h = mesh(roundGeo(.5, PLATE * 1.5), FC.skin); h.position.y = -S.armN * BRICK - PLATE * 1.5; g.add(h);
    const hand = new THREE.Group(); hand.position.y = -S.armN * BRICK - .4; g.add(hand);
    return { g, hand };
  });
  const collar = plate(2, 2, S.top); collar.position.y = sh; body.add(collar);
  const head = new THREE.Group(); head.position.set(0, sh + PLATE, 0); body.add(head);
  const R = 1;
  const hd = mesh(roundGeo(R, BRICK * 2), FC.skin); head.add(hd);
  const setFace = face(head, R);
  const top = BRICK * 2;
  if (S.hair === 'boy') { const p = mesh(roundGeo(1.05, PLATE), FC.hair); p.position.y = top; head.add(p); const tuft = mesh(roundGeo(.5, BRICK * .8), FC.hair); tuft.position.set(.3, top + PLATE, -.2); tuft.rotation.z = -.3; head.add(tuft); }
  if (S.hair === 'dad') { const p = mesh(roundGeo(1.08, PLATE * 2), FC.hair); p.position.y = top - .3; head.add(p); }
  if (S.hair === 'mom') { const p = mesh(roundGeo(1.08, PLATE * 2), FC.brown); p.position.y = top - .3; head.add(p); const bun = mesh(roundGeo(.5, BRICK), FC.brown); bun.position.set(0, top + .5, -.3); head.add(bun);
    for (const s of [-1, 1]) { const side = brick(1, 2, FC.brown, { h: BRICK * 1.5 }); side.position.set(s * 1.05, .6, -.2); head.add(side); } }
  if (S.hair === 'gran') { for (let k = 0; k < 7; k++) { const a = Math.PI * (k / 6); const c = mesh(roundGeo(.5, BRICK), FC.grey); c.position.set(Math.cos(a) * .95, top - .5 + Math.sin(a) * .4, -Math.sin(a) * .3 - .2); head.add(c); } const bun = mesh(roundGeo(.5, BRICK), FC.grey); bun.position.set(0, top + .3, -.2); head.add(bun); }
  if (S.glasses) {
    const gm = new THREE.MeshPhysicalMaterial({ color: who === 'gran' ? '#c9952e' : '#1b2a34', roughness: .3, metalness: who === 'gran' ? .6 : 0, clearcoat: 1 });
    for (const x of [-.4, .4]) { const r = new THREE.Mesh(new THREE.TorusGeometry(.3, .045, 8, 24), gm); r.position.set(x, BRICK * .95 + .2, R + .06); head.add(r); }
    const br = new THREE.Mesh(new THREE.BoxGeometry(.2, .05, .05), gm); br.position.set(0, BRICK * .95 + .22, R + .06); head.add(br);
  }
  root.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; });
  const height = sh + PLATE + top;

  // p: {x,z,y,ry, armL:[fwd, side], armR, legs:[l,r], look, nod, tilt, expr, blink, bob, lean}
  function pose(p) {
    root.position.set(p.x, p.y ?? 0, p.z); root.rotation.y = p.ry ?? 0;
    body.position.y = p.bob ?? 0; body.rotation.x = p.lean ?? 0;
    if (legs.length) { legs[0].rotation.x = p.legs?.[0] ?? 0; legs[1].rotation.x = p.legs?.[1] ?? 0; }
    const aL = p.armL ?? [0, .05], aR = p.armR ?? [0, .05];
    arms[0].g.rotation.set(aL[0], 0, -aL[1]); arms[1].g.rotation.set(aR[0], 0, aR[1]);
    head.rotation.set(p.nod ?? 0, p.look ?? 0, p.tilt ?? 0);
    setFace(p.expr, p.blink);
  }
  return { root, arms, head, pose, height, sh };
}
export function walkPose(phi, amp = .5) {
  const s = Math.sin(phi);
  return { legs: [s * amp, -s * amp], armL: [-s * amp * .6, .06], armR: [s * amp * .6, .06], bob: Math.abs(Math.cos(phi)) * .15 };
}
