#!/usr/bin/env node
// Co.Tbilisi — карусель «лидер сообщества» (4 слайда 1080×1350) по брендбуку Co.
// Запуск: node carousel.js leaders/<папка>   → PNG в leaders/<папка>/out/
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname;
const C = { blue: '#5d77fb', sky: '#95bbf8', green: '#8cf8a7', mint: '#a6f5ae', lime: '#daff8b', white: '#ffffff', black: '#000000', red: '#ea475c' };
const DARK_BG = new Set(['blue', 'red', 'black']);           // на них текст и звёзды белые
const W = 1080, H = 1350;
const LOGO_AR = { tbilisi: 690 / 153, batumi: 776 / 153 };

// ---------- helpers
const b64 = (p, mime) => `data:${mime || (p.endsWith('.png') ? 'image/png' : 'image/jpeg')};base64,${fs.readFileSync(p).toString('base64')}`;
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

// 4-лучевая звезда бренда (вогнутые стороны)
function star(x, y, size, color, rot = 0) {
  const r = size / 2, k = 0.13 * size;
  const d = `M0,${-r} C${k * 0.35},${-k} ${k},${-k * 0.35} ${r},0 C${k},${k * 0.35} ${k * 0.35},${k} 0,${r} C${-k * 0.35},${k} ${-k},${k * 0.35} ${-r},0 C${-k},${-k * 0.35} ${-k * 0.35},${-k} 0,${-r}Z`;
  return `<svg class="abs" style="left:${x - r}px;top:${y - r}px;width:${size}px;height:${size}px;overflow:visible" viewBox="${-r} ${-r} ${size} ${size}"><path d="${d}" fill="${color}" transform="rotate(${rot})"/></svg>`;
}

// «Капля из плиток»: объединение скруглённых плиток → выемки на стыках по краям
function tiles(box, split, r, jit, rnd) {
  const [x, y, w, h] = box, o = r * 0.42, out = [];
  const xs = [0, ...(split.x || []), 1], ys = [0, ...(split.y || []), 1];
  for (let i = 0; i < xs.length - 1; i++) for (let j = 0; j < ys.length - 1; j++) {
    const j1 = () => (rnd() - 0.5) * 2 * jit;
    const x0 = x + xs[i] * w - (i ? o : 0) + (i ? 0 : j1()), x1 = x + xs[i + 1] * w + (i < xs.length - 2 ? o : 0) + (i < xs.length - 2 ? 0 : j1());
    const y0 = y + ys[j] * h - (j ? o : 0) + (j ? 0 : j1()), y1 = y + ys[j + 1] * h + (j < ys.length - 2 ? o : 0) + (j < ys.length - 2 ? 0 : j1());
    out.push(`<rect x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}" rx="${r}"/>`);
  }
  return out.join('');
}
let clipN = 0;
function photoBlob(img, box, opt, rnd) {
  const id = 'c' + (clipN++);
  const [x, y, w, h] = box;
  const pos = opt.pos || 'xMidYMid';
  return `<svg class="abs" style="left:0;top:0" width="${W}" height="${H}"><defs><clipPath id="${id}">${tiles(box, opt.split, opt.r || 70, opt.jit ?? 10, rnd)}</clipPath></defs>
    ${opt.fill ? `<rect x="${x - 20}" y="${y - 20}" width="${w + 40}" height="${h + 40}" fill="${opt.fill}" clip-path="url(#${id})"/>` : ''}
    <image href="${img}" x="${x + (opt.ix || 0)}" y="${y + (opt.iy || 0)}" width="${w - (opt.ix || 0) * 2}" height="${h - (opt.iy || 0)}" preserveAspectRatio="${pos} slice" clip-path="url(#${id})"/></svg>`;
}

// скруглённый неровный четырёхугольник (карточки)
function roundPoly(pts, r) {
  const n = pts.length; let d = '';
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n];
    const v1 = [p0[0] - p1[0], p0[1] - p1[1]], v2 = [p2[0] - p1[0], p2[1] - p1[1]];
    const l1 = Math.hypot(...v1), l2 = Math.hypot(...v2), rr = Math.min(r, l1 / 2, l2 / 2);
    const a = [p1[0] + v1[0] / l1 * rr, p1[1] + v1[1] / l1 * rr], b = [p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr];
    d += (i ? 'L' : 'M') + a.join(',') + 'Q' + p1.join(',') + ' ' + b.join(',');
  }
  return d + 'Z';
}
function card(pts, fill, stroke, r = 46) {
  return `<svg class="abs" style="left:0;top:0" width="${W}" height="${H}"><path d="${roundPoly(pts, r)}" fill="${fill}" ${stroke ? `stroke="${stroke}" stroke-width="3"` : ''}/></svg>`;
}

const pill = (txt, cls, style) => `<div class="pill ${cls || ''}" style="${style || ''}">${esc(txt)}</div>`;
const logo = (color, style) => `<div class="logo" style="background:${color};${style}"></div>`;
const TOTAL = [4], CITY = ['tbilisi'];
const footer = (n, ink) => `<div class="foot" style="color:${ink}"><span>@co.${CITY[0]}</span><span>${n}/${TOTAL[0]}</span></div>`;

function css(ink) {
  const f = p => `url(${b64(path.join(HERE, 'assets/fonts', p), 'font/woff')})`;
  return `<style>
  @font-face{font-family:Mabry;src:${f('MabryPro-Regular.woff')};font-weight:400}
  @font-face{font-family:Mabry;src:${f('MabryPro-Medium.woff')};font-weight:500}
  @font-face{font-family:Mabry;src:${f('MabryPro-Bold.woff')};font-weight:700}
  @font-face{font-family:Oswald;src:url(${b64(path.join(HERE, 'assets/fonts/Oswald.ttf'), 'font/ttf')});font-weight:200 700}
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:${W}px;height:${H}px;position:relative;overflow:hidden;font-family:Mabry;color:${ink};-webkit-font-smoothing:antialiased}
  .abs{position:absolute}
  .logo{position:absolute;width:${CITY[0] === 'tbilisi' ? 228 : Math.round(51 * LOGO_AR[CITY[0]])}px;height:51px;-webkit-mask:url(${b64(path.join(HERE, `assets/co-${CITY[0]}-mask.png`))}) left center/contain no-repeat}
  .pill{position:absolute;display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;border:3px solid #000;border-radius:999px;background:#fff;color:#000;line-height:1}
  .foot{position:absolute;left:160px;right:160px;bottom:38px;display:flex;justify-content:space-between;font-size:23px}
  .h{position:absolute;line-height:1.03;letter-spacing:-0.01em}
  </style>`;
}

// ---------- slides
function slide1(L, v, rnd) {         // обложка
  const bg = C[v.colors[0]], dark = DARK_BG.has(v.colors[0]), ink = dark ? '#fff' : '#000';
  const sc = dark ? '#fff' : '#000';
  const stars = v.cover.stars.map(([x, y, s, r]) => star(x, y, s, sc, r)).join('');
  const title = L.cover_title || `27 ноября выступит основатель сообщества`;
  const frameY = 465, frameH = 765;
  return `<body style="background:${bg}">${css(ink)}
  ${stars}
  ${logo(ink, 'left:50%;transform:translateX(-50%);top:68px')}
  <div class="h" style="left:90px;right:90px;top:165px;text-align:center;font-size:${L.cover_title_size || 66}px;font-weight:700;color:${ink}">${esc(title).replace(/\n/g, '<br>')}</div>
  ${pill(L.community, '', `left:50%;transform:translateX(-50%) rotate(${v.cover.pillRot}deg);top:342px;height:88px;padding:0 44px;font-size:50px;font-weight:500;background:${C[v.cover.pill]}`)}
  ${photoBlob(b64(L.photos.cover), [45, frameY, 990, frameH], { split: L.cover_split || v.cover.split, r: 64, pos: L.cover_pos || 'xMidYMin' }, rnd)}
  ${pill(L.cover_name || L.leader, '', `left:50%;transform:translateX(-50%);top:1185px;height:104px;padding:0 ${L.cover_name_size ? 36 : 46}px;font-size:${L.cover_name_size || 56}px;font-weight:500;border-radius:24px`)}
  </body>`;
}

function slide2(L, v, rnd) {         // о сообществе
  const key = v.colors[1], bg = C[key], dark = DARK_BG.has(key), ink = dark ? '#fff' : '#000';
  const m = v.comm.mirror;           // зеркалим плашки/логотип
  const px = m ? null : 65;
  const name = L.community.toUpperCase();
  const pills = m
    ? pill(name, '', `right:65px;top:630px;height:96px;padding:0 36px;font-size:${L.comm_pill_size || 68}px;border-radius:30px`) +
      pill(L.about_label || 'О СЕБЕ', '', `right:235px;top:728px;height:72px;padding:0 30px;font-size:46px;border-radius:30px`)
    : pill(name, '', `left:65px;top:630px;height:96px;padding:0 36px;font-size:${L.comm_pill_size || 68}px;border-radius:30px`) +
      pill(L.about_label || 'О СЕБЕ', '', `left:235px;top:728px;height:72px;padding:0 30px;font-size:46px;border-radius:30px`);
  const wide = L.logo_wide;
  const lg = L.photos.logo ? `<div class="abs" style="${m ? 'left:60px' : 'right:60px'};top:${wide ? 640 : 585}px;width:${wide ? 340 : 218}px;height:${wide ? 150 : 218}px;border:3px solid #000;border-radius:34px;background:#fff;transform:rotate(${m ? -3 : 3}deg);overflow:hidden;display:flex;align-items:center;justify-content:center">
      <img src="${b64(L.photos.logo)}" style="width:86%;height:86%;object-fit:contain"></div>` : '';
  const stars = v.comm.stars.map(([x, y, s, r]) => star(x, y, s, dark ? '#fff' : '#000', r)).join('');
  return `<body style="background:${bg}">${css(ink)}
  ${stars}
  ${logo(ink, 'left:65px;top:52px')}
  ${photoBlob(b64(L.photos.community), [40, 135, 1000, 590], { split: v.comm.split, r: 62, pos: L.community_pos || 'xMidYMid' }, rnd)}
  ${pills}${lg}
  <div class="abs" style="left:65px;right:110px;top:${L.community_title.length > 60 ? 850 : 880}px"><div style="margin-right:40px;font-size:46px;font-weight:700;line-height:1.12">${esc(L.community_title).replace(/(^|\s)(о|в|и|на|с|к|у|по|для|из|от|об) /gi, '$1$2\u00a0').replace(/(\S+-\S+)/g, '<span style="white-space:nowrap">$1</span>')}</div>
  <div style="margin-top:22px;font-size:31px;line-height:1.36">${esc(L.community_text)}</div></div>
  ${pill(L.cta || '27 ноября их основатель выступит у нас →', '', `left:65px;top:1170px;height:68px;padding:0 30px;font-size:29px;font-weight:500;background:${dark ? '#fff' : '#111'};color:${dark ? '#000' : '#fff'};border-color:${dark ? '#fff' : '#111'};border-radius:22px`)}
  ${footer(2, ink)}</body>`;
}

function slide3(L, v, rnd, page = 3, ckey) {         // лидер
  const key = ckey || v.colors[2], bg = C[key], dark = DARK_BG.has(key), ink = dark ? '#fff' : '#000';
  const m = v.lead.mirror;
  const [first, ...rest] = L.leader.toUpperCase().split(' ');
  const last = rest.join(' ');
  const sx = m ? 45 : 355;
  const nameL = m ? null : 65;
  const pills = m
    ? pill(first, '', `right:65px;top:560px;height:118px;padding:0 36px;font-size:84px;border-radius:30px`) +
      pill(last, '', `right:${v.lead.step + 65}px;top:675px;height:118px;padding:0 36px;font-size:84px;border-radius:30px`)
    : pill(first, '', `left:65px;top:560px;height:118px;padding:0 36px;font-size:84px;border-radius:30px`) +
      pill(last, '', `left:${v.lead.step + 65}px;top:675px;height:118px;padding:0 36px;font-size:84px;border-radius:30px`);
  const cx0 = m ? 50 : 295, cx1 = m ? 785 : 1030;
  const cpts = m ? [[cx0, 905], [cx1, 840], [cx1, 1255], [cx0 + 6, 1250]] : [[cx0, 840], [cx1, 905], [cx1 - 6, 1250], [cx0, 1255]];
  const tx = cx0 + 58;
  const accent = dark ? '#fff' : (key === 'white' ? C.blue : '#000');
  return `<body style="background:${bg}">${css(ink)}
  ${logo(ink, 'left:65px;top:52px')}
  ${star(m ? 990 : 125, 300, 104, dark ? '#fff' : '#000', 0)}
  ${star(m ? 860 : 215, 1150, 62, accent, 8)}
  ${photoBlob(b64(L.photos.leader), [sx, m ? 135 : 112, 680, m ? 729 : 752], { split: v.lead.split, r: 74, fill: '#000', pos: L.leader_pos || 'xMidYMin' }, rnd)}
  ${pills}
  ${card(cpts, '#fff', '#000')}
  <div class="h" style="left:${tx}px;width:${cx1 - cx0 - 110}px;top:${948}px;font-size:36px;font-weight:500;color:#000">${esc(L.role)}</div>
  ${pill(L.community, '', `left:${tx}px;top:1003px;height:60px;padding:0 24px;font-size:31px;font-weight:500;background:${C[v.lead.pill]}`)}
  <div class="h" style="left:${tx}px;width:${cx1 - cx0 - 105}px;top:1083px;font-size:28px;line-height:1.36;color:#222">${esc(L.bio)}</div>
  ${footer(page, ink)}</body>`;
}

function slide4(L, v, ev) {          // вечер
  const key = v.colors[v.colors.length - 1], bg = C[key], dark = DARK_BG.has(key), ink = dark ? '#fff' : '#000';
  const sc = dark ? '#fff' : '#000';
  const stars = v.ev.stars.map(([x, y, s, r]) => star(x, y, s, sc, r)).join('');
  return `<body style="background:${bg}">${css(ink)}
  ${stars}
  ${logo(ink, 'left:50%;transform:translateX(-50%);top:78px')}
  ${pill(ev.label, '', `left:50%;transform:translateX(-50%);top:184px;height:64px;padding:0 30px;font-size:34px;background:transparent;border-color:${ink};color:${ink}`)}
  <div class="h" style="left:0;right:0;top:268px;text-align:center;font-size:150px;font-weight:700;letter-spacing:-0.04em;line-height:1">${esc(ev.date)}</div>
  <div class="h" style="left:0;right:0;top:440px;text-align:center;font-size:38px;font-weight:500">${esc(ev.time)}</div>
  <div class="h" style="left:120px;right:120px;top:505px;text-align:center;font-size:30px;line-height:1.32;opacity:.85">${esc(L.speakers || ev.speakers)}</div>
  ${card([[108, 668], [972, 652], [980, 858], [102, 873]], '#fff', key === 'white' ? '#000' : null, 40)}
  <div class="h" style="left:0;right:0;top:700px;text-align:center;font-size:52px;font-weight:700;color:#000">
    <svg width="40" height="48" viewBox="0 0 24 30" style="vertical-align:-6px;margin-right:12px"><path d="M12 0C5.4 0 0 5.2 0 11.7 0 20.5 12 30 12 30s12-9.5 12-18.3C24 5.2 18.6 0 12 0zm0 16.2a4.6 4.6 0 110-9.2 4.6 4.6 0 010 9.2z" fill="#000"/></svg>${esc(ev.place)}</div>
  <div class="h" style="left:0;right:0;top:775px;text-align:center;font-size:30px;color:#000">${esc(ev.address)}</div>
  ${pill(ev.entry, '', `left:50%;transform:translateX(-50%);top:918px;height:112px;padding:0 48px;font-size:56px;font-weight:700;background:#111;border-color:#111;color:#fff`)}
  <div class="h" style="left:0;right:0;top:1048px;text-align:center;font-size:30px">${esc(ev.entry_note)}</div>
  ${pill(ev.button, '', `left:50%;transform:translateX(-50%);top:1112px;height:72px;padding:0 28px;font-family:Oswald;font-weight:300;font-size:36px;border:none;border-radius:12px;background:${key === 'white' ? '#f1f1f1' : 'rgba(255,255,255,.55)'};color:#000`)}
  ${footer(TOTAL[0], ink)}</body>`;
}

// ---------- variants: цвета и раскладка свои для каждого лидера
const PALETTES = [
  ['blue', 'green', 'white', 'lime'], ['lime', 'white', 'blue', 'green'], ['green', 'blue', 'white', 'lime'],
  ['white', 'lime', 'blue', 'green'], ['sky', 'lime', 'white', 'green'], ['blue', 'lime', 'white', 'sky'],
  ['green', 'white', 'blue', 'lime'], ['lime', 'sky', 'white', 'blue'], ['sky', 'white', 'blue', 'lime'],
  ['white', 'green', 'blue', 'lime'],
];
const SPLITS = [{ x: [0.33], y: [0.45] }, { x: [0.5], y: [0.45] }, { x: [0.62], y: [0.6] }, { x: [0.5] }, { y: [0.42] }, { x: [0.4], y: [0.3] }];
function variant(n, over = {}) {
  const r = rng(n * 7919 + 13), pick = a => a[Math.floor(r() * a.length)];
  const cornerStars = () => {
    const c = [[125, 110], [960, 105], [70, 1270], [1015, 1240], [1010, 470], [70, 470]];
    const k = 3 + Math.floor(r() * 2);
    return c.sort(() => r() - 0.5).slice(0, k).map(([x, y]) => [x + (r() - 0.5) * 30, y + (r() - 0.5) * 30, 80 + r() * 70, (r() - 0.5) * 30]);
  };
  const colors = over.colors || PALETTES[(n - 1) % PALETTES.length];
  const pillColors = ['lime', 'green', 'sky', 'white'].filter(c => c !== colors[0] && c !== colors[2]);
  const v = {
    colors,
    cover: { split: pick(SPLITS), stars: cornerStars().filter(([x, y]) => y < 200 || y > 1150), pill: pickPill(colors[0]), pillRot: (r() - 0.5) * 4 },
    comm: { split: pick(SPLITS), mirror: r() < 0.5, stars: [[985, 95, 100, 0]] },
    lead: { split: pick(SPLITS), mirror: r() < 0.5, step: 120 + Math.floor(r() * 60), pill: pickPill(colors[2]) },
    ev: { stars: cornerStars() },
  };
  function pickPill(bgc) { const opts = ['lime', 'green', 'sky'].filter(c => c !== bgc); return opts[Math.floor(r() * opts.length)]; }
  return Object.assign(v, over);
}

(async () => {
  const dir = path.resolve(process.argv[2]);
  const L = JSON.parse(fs.readFileSync(path.join(dir, 'leader.json'), 'utf8'));
  for (const k in L.photos) L.photos[k] = path.join(dir, L.photos[k]);
  CITY[0] = L.city || 'tbilisi';
  const ev = JSON.parse(fs.readFileSync(path.join(HERE, CITY[0] === 'tbilisi' ? 'event.json' : `event-${CITY[0]}.json`), 'utf8'));
  const v = variant(L.n || 1, L.variant || {});
  const rnd = rng((L.n || 1) * 31 + 7);
  const out = path.join(dir, 'out'); fs.mkdirSync(out, { recursive: true });
  const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  // несколько основателей: L.more = [{leader, role, bio, photo}] → по слайду на каждого
  const extra = (L.more || []).map(x => ({ ...L, ...x, photos: { ...L.photos, leader: path.join(dir, x.photo) } }));
  TOTAL[0] = 4 + extra.length;
  const slides = [slide1(L, v, rnd), slide2(L, v, rnd), slide3(L, v, rnd)];
  extra.forEach((X, i) => {
    const vi = { ...v, lead: { ...v.lead, mirror: (i % 2 === 0) ? !v.lead.mirror : v.lead.mirror, split: SPLITS[(SPLITS.indexOf(v.lead.split) + 2 + i) % SPLITS.length] } };
    slides.push(slide3(X, vi, rnd, 4 + i, v.colors[3 + i] && 3 + i < v.colors.length - 1 ? v.colors[3 + i] : v.colors[2]));
  });
  slides.push(slide4(L, v, ev));
  for (let i = 0; i < slides.length; i++) {
    await pg.setContent('<!doctype html><html><head><meta charset="utf-8"></head>' + slides[i] + '</html>');
    await pg.evaluate(() => document.fonts.ready);
    await pg.screenshot({ path: path.join(out, `${i + 1}.png`) });
  }
  await br.close();
  fs.writeFileSync(path.join(out, 'variant.json'), JSON.stringify(v, null, 1));
  console.log('ok', out, v.colors.join(' / '));
})();
