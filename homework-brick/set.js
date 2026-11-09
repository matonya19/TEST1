// Set: a real walnut desk, an open squared exercise book (the brick world's ground), a desk lamp, a pencil and an eraser.
import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

const PH = '/core/assets/polyhaven/';
export const M = 125;          // 1 m = 125 studs
export const PT = .6;          // page top
export const PAGE = { w: 26, d: 37 };   // one A4 page in studs

function pageTex(side) {
  const c = document.createElement('canvas'); c.width = 1040; c.height = 1480; const x = c.getContext('2d');
  x.fillStyle = '#f6f3ea'; x.fillRect(0, 0, c.width, c.height);
  // faint paper mottling
  for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(120,110,90,${Math.random() * .03})`; x.fillRect(Math.random() * 1040, Math.random() * 1480, 3, 3); }
  x.strokeStyle = 'rgba(90,140,200,.45)'; x.lineWidth = 2;
  const g = 20;   // 5 mm squares: 1 stud = 40 px → square = 20 px
  for (let i = 0; i <= c.width; i += g) { x.beginPath(); x.moveTo(i, 0); x.lineTo(i, c.height); x.stroke(); }
  for (let j = 0; j <= c.height; j += g) { x.beginPath(); x.moveTo(0, j); x.lineTo(c.width, j); x.stroke(); }
  if (side === 'L') {
    x.strokeStyle = 'rgba(210,60,60,.7)'; x.lineWidth = 4; x.beginPath(); x.moveTo(980, 0); x.lineTo(980, c.height); x.stroke();
    x.fillStyle = '#23317a'; x.textAlign = 'center';
    x.font = '84px Neucha'; x.fillText('Домашняя работа', 500, 150);
    x.font = '70px Neucha'; x.fillText('Задача 3:  7 × 8 = ?', 470, 260);
  } else {
    x.strokeStyle = 'rgba(210,60,60,.7)'; x.lineWidth = 4; x.beginPath(); x.moveTo(60, 0); x.lineTo(60, c.height); x.stroke();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}

export async function buildSet(scene) {
  const hdr = await new RGBELoader().loadAsync(PH + 'photo_studio_loft_hall_2k.hdr');
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = hdr; scene.background = hdr;
  scene.backgroundBlurriness = .5; scene.backgroundIntensity = .22; scene.environmentIntensity = .45;
  scene.environmentRotation.y = scene.backgroundRotation.y = 1.2;

  const tl = new THREE.TextureLoader(), tex = (f, srgb) => { const t = tl.load(PH + f); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(3.5, 3.5); t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  const desk = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), new THREE.MeshStandardMaterial({ map: tex('walnut_diff.jpg', true), normalMap: tex('walnut_nor.jpg'), roughnessMap: tex('walnut_rough.jpg'), roughness: 1 }));
  desk.rotation.x = -Math.PI / 2; desk.receiveShadow = true; scene.add(desk);

  // the open exercise book: two pages, a cover edge, a slight dip at the spine
  const book = new THREE.Group(); scene.add(book);
  const cover = new THREE.Mesh(new THREE.BoxGeometry(PAGE.w * 2 + 1.2, .25, PAGE.d + 1.2), new THREE.MeshStandardMaterial({ color: '#2f6fb0', roughness: .7 }));
  cover.position.y = .125; book.add(cover);
  for (const [s, side] of [[-1, 'L'], [1, 'R']]) {
    const pg = new THREE.Mesh(new THREE.BoxGeometry(PAGE.w, PT - .25, PAGE.d), [
      new THREE.MeshStandardMaterial({ color: '#efeadf', roughness: .95 }), new THREE.MeshStandardMaterial({ color: '#efeadf', roughness: .95 }),
      new THREE.MeshStandardMaterial({ map: pageTex(side), roughness: .92 }), new THREE.MeshStandardMaterial({ color: '#efeadf' }),
      new THREE.MeshStandardMaterial({ color: '#efeadf', roughness: .95 }), new THREE.MeshStandardMaterial({ color: '#efeadf', roughness: .95 })]);
    pg.position.set(s * PAGE.w / 2, .25 + (PT - .25) / 2, 0); book.add(pg);
  }
  book.traverse(m => { if (m.isMesh) { m.castShadow = m.receiveShadow = true; } });

  // lights: key with shadows, cool fill, softboxes for the plastic highlights
  const key = new THREE.DirectionalLight('#fff4e8', 3.0); key.position.set(-60, 110, 50); key.target.position.set(0, 0, 0);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -.0004; key.shadow.normalBias = .03; key.shadow.radius = 4;
  Object.assign(key.shadow.camera, { left: -40, right: 40, top: 40, bottom: -40, near: 10, far: 400 }); scene.add(key, key.target);
  const fill = new THREE.DirectionalLight('#cfe0ff', .45); fill.position.set(60, 40, -50); scene.add(fill);
  RectAreaLightUniformsLib.init();
  const box = (col, I, w, h, p, at) => { const l = new THREE.RectAreaLight(col, I, w, h); l.position.set(...p); l.lookAt(...at); scene.add(l); return l; };
  box('#fff6ee', 6, 70, 45, [-45, 60, 65], [0, 4, 0]);
  box('#e4eeff', 9, 60, 30, [45, 45, -75], [0, 6, 0]);

  // real props: desk lamp, pencil, eraser
  const gl = new GLTFLoader();
  const lamp = (await gl.loadAsync(`${PH}desk_lamp_arm_01/desk_lamp_arm_01.gltf`)).scene;
  lamp.scale.setScalar(M); lamp.position.set(-55, 0, -45); lamp.rotation.y = 1.2; scene.add(lamp);
  lamp.traverse(m => { if (m.isMesh) m.castShadow = m.receiveShadow = true; });
  const bulb = new THREE.PointLight('#ffe2b8', 500, 120, 2); bulb.position.set(-25, 40, -40); scene.add(bulb);

  const pencil = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(.95, .95, 22, 6), new THREE.MeshStandardMaterial({ color: '#f3b61f', roughness: .45 }));
  const wood = new THREE.Mesh(new THREE.ConeGeometry(.95, 2.6, 6), new THREE.MeshStandardMaterial({ color: '#e9c89a', roughness: .8 })); wood.position.y = 12.3;
  const lead = new THREE.Mesh(new THREE.ConeGeometry(.3, .8, 12), new THREE.MeshStandardMaterial({ color: '#2b2b2b', roughness: .4 })); lead.position.y = 14;
  const fer = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 1.4, 16), new THREE.MeshStandardMaterial({ color: '#b9bcc0', metalness: 1, roughness: .3 })); fer.position.y = -11.7;
  const eras = new THREE.Mesh(new THREE.CylinderGeometry(.95, .95, 1.6, 16), new THREE.MeshStandardMaterial({ color: '#e88a8a', roughness: .8 })); eras.position.y = -13.2;
  pencil.add(body, wood, lead, fer, eras); pencil.rotation.set(Math.PI / 2, 0, -.5); pencil.position.set(-4, PT + .95, -24);
  pencil.traverse(m => { if (m.isMesh) m.castShadow = m.receiveShadow = true; }); scene.add(pencil);
  const rubber = new THREE.Mesh(new THREE.BoxGeometry(6, 1.6, 3.4), [0, 1, 2, 3, 4, 5].map(i => new THREE.MeshStandardMaterial({ color: i === 2 ? '#e98aa0' : '#5b8fd6', roughness: .85 })));
  rubber.position.set(34, .8, 10); rubber.rotation.y = .4; rubber.castShadow = rubber.receiveShadow = true; scene.add(rubber);

  return { key, bulb };
}
