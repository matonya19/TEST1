#!/usr/bin/env python3
"""
reels_ref.py — "iOS sheet" style on top of reels.py (reference: video card + white bottom sheet
with live phrase and chapter progress bar, glass pills, hook title, photo cards).

Extra overlay types (plan['overlays']):
  {"type":"sheet","at":..,"until":..,"chapter":"01/03","label":"ПРАКТИКА","photo":"path.jpg"|null}
  {"type":"pill","text":"Процесс","at":..,"dur":1.6,"x":0.5,"y":0.3}
  {"type":"hook","lines":["ВЫ ИМЕЕТЕ","ПРАВО ЗНАТЬ"],"at":0,"until":..,"pill":"процесс"}
  {"type":"photo","src":"path.jpg","at":..,"until":..}   full-screen photo with the speaker card on top
Subtitles: plan['subs']['mode']='phrase' -> white phrase at bottom; inside sheet: black phrase on panel.
Usage: same commands as reels.py, but run this file.
"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reels as R
from reels import *  # noqa
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

AMBER = (242, 183, 107)
INKC = (20, 18, 16)
PILL_DOT = (255, 255, 255)
ORANGE = (236, 118, 40)
CARD = dict(x=60, y=150, w=960, h=560, r=44)        # speaker card in sheet scene
PANEL_Y = 1250                                       # top of the white sheet


def rr_mask(w, h, r, S=3):
    def dr(d, s): d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=(255, 255, 255, 255))
    return R.ss(dr, w, h, S).getchannel('A')


@lru_cache(8)
def photo_spr(path, w, h, r=36):
    im = Image.open(path).convert('RGB')
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * 0.35); im = im.crop((x, y, x + w, y + h)).convert('RGBA')
    im.putalpha(rr_mask(w, h, r))
    out = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0))
    sh_ = Image.new('L', out.size, 0); ImageDraw.Draw(sh_).rounded_rectangle((30, 40, 30 + w, 40 + h), r, fill=150)
    lay = Image.new('RGBA', out.size, (0, 0, 0, 255)); lay.putalpha(sh_.filter(ImageFilter.GaussianBlur(18)))
    out = Image.alpha_composite(out, lay)
    border = Image.new('L', (w, h), 0); ImageDraw.Draw(border).rounded_rectangle((0, 0, w - 1, h - 1), r, outline=255, width=3)
    bl = Image.new('RGBA', (w, h), (255, 255, 255, 120)); bl.putalpha(border.point(lambda v: v // 2))
    out.alpha_composite(im, (30, 30)); out.alpha_composite(bl, (30, 30))
    return out


@lru_cache(64)
def pill_spr(text, dark=True, size=30):
    f = font('InterTight.ttf', size, 'Medium')
    tw = int(f.getlength(text)); h = int(size * 2.0); w = tw + int(size * 2.6)
    def dr(d, s):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), h * s // 2, fill=ORANGE + (245,))
        cx, cy, rr_ = int(size * 0.95) * s, h * s // 2, int(size * 0.22) * s
        d.ellipse((cx - rr_, cy - rr_, cx + rr_, cy + rr_), fill=PILL_DOT + (255,))
    img = R.ss(dr, w, h); d = ImageDraw.Draw(img)
    d.text((int(size * 1.65), h // 2), text, font=f, fill=(255, 255, 255), anchor='lm')
    return img


def wrap(text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        tr = (cur + ' ' + w).strip()
        if cur and f.getlength(tr) > maxw: lines.append(cur); cur = w
        else: cur = tr
    if cur: lines.append(cur)
    return lines


class Ref(R.Renderer):
    def __init__(self, plan):
        super().__init__(plan)
        self.sheets = [o for o in self.ov if o['type'] == 'sheet']
        self.photos = [o for o in self.ov if o['type'] == 'photo']
        self.cmask = rr_mask(CARD['w'], CARD['h'], CARD['r'])
        self.groups = self.make_groups()

    def resolve(self, o):
        if o['type'] in ('sheet', 'photo', 'hook', 'pill', 'pic', 'wave', 'img'):
            o = dict(o); c = self.cue
            o['t0'] = c(o.get('at', 0)); o['t1'] = c(o['until']) if 'until' in o else o['t0'] + o.get('dur', 1.5)
            return o
        return super().resolve(o)

    # phrase groups for subtitles (3-5 words, break on punctuation / segment)
    def make_groups(self):
        gs, cur = [], []
        for i, w in enumerate(self.W):
            cur.append(w); nxt = self.W[i + 1] if i + 1 < len(self.W) else None
            ch = sum(len(x['w']) + 1 for x in cur)
            if nxt is None or nxt['seg'] != w['seg'] or len(cur) >= 5 or ch >= 26 or w['w'][-1] in ',.:!?—' \
                    or (nxt and nxt['s'] - w['e'] > 0.25):
                gs.append(cur); cur = []
        return gs

    def group_at(self, t):
        for g in self.groups:
            if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15: return g
        return None

    def active(self, lst, t, pad=0.0):
        for o in lst:
            if o['t0'] <= t < o['t1'] + pad: return o
        return None

    # ---------------- scene compose
    def compose(self, frame, t):
        base = self.camera(frame, t)                       # graded full frame float
        sh_ = self.active(self.sheets, t, 0.3); ph = self.active(self.photos, t, 0.25)
        cv = Image.fromarray(base.astype(np.uint8)).convert('RGBA')
        if sh_ or ph:
            if sh_:
                kin = ease_out(prog(t, sh_['t0'], 0.38)); kout = ease_in(prog(t, sh_['t1'], 0.3)); k = kin * (1 - kout)
            else:
                kin = ease_out(prog(t, ph['t0'], 0.3)); kout = ease_in(prog(t, ph['t1'], 0.25)); k = kin * (1 - kout)
            cv = self.card_scene_ref(base, t, k, sh_, ph)
        self.draw_ref(cv, t, sh_)
        return np.asarray(cv.convert('RGB'))

    def card_scene_ref(self, base, t, k, sh_, ph):
        cv2 = self.cv2
        # background: photo (if any) or blurred warm video
        if ph:
            bgp = Image.open(ph['src']).convert('RGB'); s = max(FW / bgp.width, FH / bgp.height)
            bgp = bgp.resize((int(bgp.width * s) + 1, int(bgp.height * s) + 1), Image.LANCZOS)
            x = (bgp.width - FW) // 2; y = (bgp.height - FH) // 2; bg = np.asarray(bgp.crop((x, y, x + FW, y + FH)), np.float32)
            z = 1 + 0.04 * prog(t, ph['t0'], ph['t1'] - ph['t0'])
            bg = cv2.warpAffine(bg, np.float32([[z, 0, FW / 2 * (1 - z)], [0, z, FH / 2 * (1 - z)]]), (FW, FH))
            bg = bg * 0.82
        else:
            small = cv2.resize(base, (FW // 8, FH // 8), interpolation=cv2.INTER_AREA)
            bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (FW, FH)) * np.array([1.0, 0.82, 0.68]) * 0.62
        full = base
        # card target rect & crop of the speaker
        cx, cy = self.plan.get('card_focus', [540, 760]); cw = 1080; chh = int(cw * CARD['h'] / CARD['w'])
        y0 = int(np.clip(cy - chh * 0.42, 0, FH - chh)); crop = full[y0:y0 + chh, :]
        # interpolate rect from full screen to card
        X = 0 + (CARD['x'] - 0) * k; Y = 0 + (CARD['y'] - 0) * k
        W_ = FW + (CARD['w'] - FW) * k; H_ = FH + (CARD['h'] - FH) * k
        src = full if k < 0.5 else crop
        if k < 0.5:   # still mostly full-screen: blend full frame toward bg
            out = full * (1 - k * 2) + bg * (k * 2)
            img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
            win = Image.fromarray(np.clip(crop, 0, 255).astype(np.uint8)).resize((max(2, int(W_)), max(2, int(H_))))
            m = rr_mask(win.width, win.height, int(CARD['r'] * k * 2) + 1, 1)
            win.putalpha(m.point(lambda v: int(v * k * 2)))
            img.alpha_composite(win, (int(X), int(Y)))
            return img
        img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA')
        win = Image.fromarray(np.clip(src, 0, 255).astype(np.uint8)).resize((int(W_), int(H_)), Image.BILINEAR).convert('RGBA')
        win.putalpha(rr_mask(int(W_), int(H_), CARD['r'], 1))
        # soft shadow + border
        shd = Image.new('L', (FW, FH), 0); ImageDraw.Draw(shd).rounded_rectangle((X, Y + 18, X + W_, Y + H_ + 18), CARD['r'], fill=140)
        lay = Image.new('RGBA', (FW, FH), (0, 0, 0, 255)); lay.putalpha(shd.filter(ImageFilter.GaussianBlur(24)))
        img = Image.alpha_composite(img, lay); img.alpha_composite(win, (int(X), int(Y)))
        bd = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
        ImageDraw.Draw(bd).rounded_rectangle((X, Y, X + W_ - 1, Y + H_ - 1), CARD['r'], outline=(255, 255, 255, 70), width=2)
        img.alpha_composite(bd)
        return img

    # ---------------- overlays
    def draw_ref(self, cv, t, sh_):
        for o in self.ov:
            if not (o['t0'] - 0.01 <= t < o['t1'] + 0.35): continue
            ty = o['type']
            if ty in ('sheet', 'photo', 'card'): continue
            if ty == 'wave' or o.get('top'): continue
            elif ty == 'img': self.ov_img(cv, t, o)
            elif ty == 'pic': self.ov_pic(cv, t, o)
            elif ty == 'pill': self.ov_pill(cv, t, o)
            elif ty == 'hook': self.ov_hook(cv, t, o)
            elif hasattr(self, 'ov_' + ty): getattr(self, 'ov_' + ty)(cv, t, o)
        if sh_: self.ov_sheet(cv, t, sh_)
        for o in self.ov:
            if o['t0'] - 0.01 <= t < o['t1'] + 0.35 and (o['type'] == 'wave' or o.get('top')):
                (self.ov_wave if o['type'] == 'wave' else self.ov_img if o['type'] == 'img' else getattr(self, 'ov_' + o['type']))(cv, t, o)
        if t < self.BODY + 0.3 and not self.in_sheet(t): self.subs_phrase(cv, t)

    def in_sheet(self, t):
        o = self.active(self.sheets, t, 0.35)
        return o is not None and t >= o['t0'] + 0.25

    def ov_wave(self, cv, t, o):
        if not hasattr(self, '_env'): self._env = R.env_db(self.plan['work'])
        if t >= self.BODY: return
        sg = self.seg_at(t); st = sg['a'] + (t - sg['o'])
        n = o.get('bars', 36); w = o.get('w', 640); bw = w / n; h = o.get('h', 120); cy = FH * o.get('y', 0.86)
        img = Image.new('RGBA', (FW, int(h) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        x0 = FW / 2 - w / 2; mid = (h + 20) / 2
        for k in range(n):
            # mirror around centre: centre bars = now, edges = slightly earlier
            off = abs(k - (n - 1) / 2) / ((n - 1) / 2)
            i = int((st - off * 0.35) * 100)
            v = self._env[max(0, min(i, len(self._env) - 1))]
            a = clamp((v + 50) / 32) * (1 - 0.45 * off) * (0.75 + 0.25 * math.sin(k * 1.7 + t * 9))
            bh = max(6, a * h)
            col = tuple(o.get('color', AMBER)) + (255,)
            xx = x0 + k * bw + bw * 0.2
            d.rounded_rectangle((xx, mid - bh / 2, xx + bw * 0.6, mid + bh / 2), int(bw * 0.3), fill=col)
        cv.alpha_composite(img, (0, int(cy - mid)))

    def ov_img(self, cv, t, o):
        if not hasattr(self, '_imgs'): self._imgs = {}
        if o['src'] not in self._imgs: self._imgs[o['src']] = Image.open(o['src']).convert('RGBA').resize((FW, FH))
        a = ease_out(prog(t, o['t0'], o.get('fade', 0.5)))
        if a <= 0: return
        z = 1.0 + 0.03 * prog(t, o['t0'], max(0.1, o['t1'] - o['t0']))
        paste(cv, self._imgs[o['src']], FW / 2, FH / 2, z, a)

    def ov_pic(self, cv, t, o):
        p = prog(t, o['t0'], 0.35); a = clamp(p * 3) * (1 - ease_in(prog(t, o['t1'], 0.22)))
        if a <= 0: return
        spr = photo_spr(o['src'], o.get('w', 340), o.get('h', 604), o.get('r', 30))
        paste(cv, spr, o.get('x', 220), o.get('y', 430) + 40 * (1 - ease_out(p)), 0.85 + 0.15 * back(p), a, rot=o.get('rot', -3))

    def ov_pill(self, cv, t, o):
        p = prog(t, o['t0'], 0.3); a = clamp(p * 3) * (1 - ease_in(prog(t, o['t1'], 0.2)))
        if a <= 0: return
        spr = pill_spr(o['text'], o.get('dark', True), o.get('size', 30))
        paste(cv, spr, FW * o.get('x', 0.5), FH * o.get('y', 0.3) + 24 * (1 - ease_out(p)), 0.9 + 0.1 * back(p), a)

    def ov_hook(self, cv, t, o):
        a = 1 - ease_in(prog(t, o['t1'], 0.25))
        if a <= 0: return
        size = o.get('size', 112); y = FH * o.get('y', 0.6); lh = size * 0.9
        for i, ln in enumerate(o['lines']):
            p = prog(t, o['t0'] + i * 0.18, 0.35)
            if p <= 0: continue
            col = tuple(o.get('accent_color', AMBER)) if i == len(o['lines']) - 1 and o.get('accent_last', True) else WHITE
            spr = text_spr(ln, 'sans_semi', size, col, -0.035, 0.8)
            paste(cv, spr, 70 + 40 * (1 - ease_out(p)), y + i * lh, 1, clamp(p * 2) * a, anchor='l')
        if o.get('pill'):
            p = prog(t, o['t0'] + 0.5, 0.3)
            if p > 0: paste(cv, pill_spr(o['pill']), 70, y + len(o['lines']) * lh + 10, 1, clamp(p * 3) * a, anchor='l')

    def ov_sheet(self, cv, t, o):
        kin = ease_out(prog(t, o['t0'] + 0.08, 0.38)); kout = ease_in(prog(t, o['t1'], 0.28)); k = kin * (1 - kout)
        if k <= 0: return
        top = PANEL_Y + (FH - PANEL_Y + 40) * (1 - k)
        panel = Image.new('RGBA', (FW, FH), (0, 0, 0, 0)); d = ImageDraw.Draw(panel)
        d.rounded_rectangle((0, top, FW, FH + 60), 56, fill=(14, 13, 12, 248), outline=(255, 255, 255, 40), width=2)
        d.rounded_rectangle((FW / 2 - 40, top + 18, FW / 2 + 40, top + 26), 4, fill=(90, 86, 82, 255))
        cv.alpha_composite(panel)
        # middle zone photo card
        if o.get('video'):
            p = prog(t, o['t0'] + 0.3, 0.4); a = clamp(p * 2) * k
            n = len(os.listdir(o['video'])); i = int(clamp((t - o['t0']) * 30, 0, n - 1)) + 1
            spr = photo_spr(os.path.join(o['video'], f'{i:04d}.jpg'), o.get('pw', 600), o.get('ph', 430))
            mid = (CARD['y'] + CARD['h'] + PANEL_Y) / 2 + 10
            paste(cv, spr, FW / 2, mid + 40 * (1 - ease_out(p)), 0.9 + 0.1 * back(p), a, rot=o.get('rot', -1.5))
        elif o.get('photo'):
            p = prog(t, o['t0'] + 0.3, 0.4); a = clamp(p * 2) * k
            spr = photo_spr(o['photo'], o.get('pw', 520), o.get('ph', 400))
            mid = (CARD['y'] + CARD['h'] + PANEL_Y) / 2 + 10
            paste(cv, spr, FW / 2, mid + 40 * (1 - ease_out(p)), 0.9 + 0.1 * back(p), a, rot=o.get('rot', -2))
        # live phrase (black) on the sheet
        g = self.group_at(t)
        if g and t < self.BODY:
            txt = ' '.join(w['w'] for w in g).strip(' ,—')
            f = font('InterTight.ttf', 60, 'Medium'); lines = wrap(txt, f, 860)[:2]
            for i, ln in enumerate(lines):
                spr = text_spr(ln, 'sans', 60, WHITE, -0.02, 0)
                paste(cv, spr, FW / 2, top + 120 + i * 66 - (len(lines) - 1) * 10, 1, k)
        # chapter progress bar
        fsm = font('InterTight.ttf', 22, 'Medium'); bar = Image.new('RGBA', (FW, 60), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
        lab = f"{o.get('chapter', '')}   {o.get('label', '').upper()}"
        bd.text((250, 30), lab, font=fsm, fill=(170, 165, 160), anchor='lm')
        lx0 = 250 + fsm.getlength(lab) + 24; lx1 = 830
        bd.line((lx0, 30, lx1, 30), fill=(70, 66, 62), width=3)
        pr = clamp((t - o['t0']) / max(0.1, o['t1'] - o['t0']))
        st, en = o.get('bar', [0, 1]); px = lx0 + (lx1 - lx0) * (st + (en - st) * pr)
        bd.line((lx0, 30, px, 30), fill=WHITE, width=3); bd.ellipse((px - 8, 22, px + 8, 38), fill=WHITE)
        paste(cv, bar, FW / 2, top + 290, 1, k)

    def subs_phrase(self, cv, t):
        S = self.plan['subs']
        if S.get('mode') == 'none': return
        hide = [(o['t0'], o['t1']) for o in self.ov if o['type'] in ('hook',)]
        if any(a <= t < b for a, b in hide): return
        g = self.group_at(t)
        if not g: return
        txt = ' '.join(w['w'] for w in g).strip(' ,—')
        f = font('InterTight.ttf', S.get('size', 56), 'Medium'); lines = wrap(txt, f, 820)[:2]
        y = FH * S.get('y', 0.76)
        for i, ln in enumerate(lines):
            spr = text_spr(ln, 'sans', S.get('size', 56), WHITE, -0.02, 0.9)
            paste(cv, spr, FW / 2, y + i * S.get('size', 56) * 1.08, 1, 1)


R.Renderer = Ref   # so preview / worker / cues use the extended renderer

if __name__ == '__main__':
    sys.argv[0] = os.path.abspath(__file__)
    a = sys.argv[1:]; script = os.path.abspath(__file__)
    plan = R.load_plan(a[1]) if len(a) > 1 and a[0] not in ('setup', 'probe', 'asr') else None
    if plan: plan['_path'] = os.path.abspath(a[1])
    if a[0] == '_worker': Ref(plan).run(int(a[2]), int(a[3]))
    elif a[0] == 'preview': R.preview(plan, [float(x) for x in a[2:]])
    elif a[0] == 'cues':
        r = Ref(plan)
        for o in r.ov: print(f"{o['t0']:6.2f}-{o['t1']:6.2f}  {o['type']:7s} {o.get('text', o.get('label', o.get('lines', '')))}")
    elif a[0] == 'video':
        import glob
        [os.remove(p) for p in glob.glob(plan['work'] + '/part*.mp4')]; R.render_video(plan, script)
    elif a[0] == 'final': R.final(plan, script)
    else:
        sys.argv = [os.path.join(os.path.dirname(script), 'reels.py')] + a
        exec(open(sys.argv[0]).read(), {'__name__': '__main__', '__file__': sys.argv[0]})
