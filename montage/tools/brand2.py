# extra brand kit v2: rounded window card, more animated scenes. Imported via reels.py wrapper.
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter


def install(G):
    Renderer = G['Renderer']; prog = G['prog']; ease_out = G['ease_out']; ease_in = G['ease_in']; back = G['back']
    ease_io = G['ease_io']; font = G['font']; SCENES = G['SCENES']; FW, FH = G['FW'], G['FH']
    B = (36, 87, 237); WH = (255, 255, 255); K = (17, 17, 20); LB = (220, 229, 252); GR = (140, 146, 160)
    F = lambda s, w='ExtraBold': font('Montserrat.ttf', s, w)
    _mask = {}

    def rmask(w, h, r):
        k = (w, h, r)
        if k not in _mask:
            m = Image.new('L', (w * 2, h * 2), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), r * 2, fill=255)
            m = np.asarray(m.resize((w, h), Image.LANCZOS), np.float32)[..., None] / 255
            sh = Image.new('L', (w + 120, h + 120), 0); ImageDraw.Draw(sh).rounded_rectangle((60, 76, 60 + w, 76 + h), r, fill=70)
            sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(22)), np.float32)[..., None] / 255
            _mask[k] = (m, sh)
        return _mask[k]

    def card_scene(self, base, t, c):
        cv2 = self.cv2
        kin = 1.0 if c.get('instant_in') else ease_out(prog(t, c['t0'], 0.3))
        kout = 0.0 if c.get('instant_out') else ease_in(prog(t, c['t1'] - 0.2, 0.2))
        w = int(FW * c.get('size', 0.86)); h = int(w * c.get('aspect', 1.0)); cy = int(FH * c.get('y', 0.5))
        sz = int(FW * c.get('crop', 1.0)); ch = int(sz * h / w); sy = int(FH * c.get('crop_y', 0.5))
        x0 = (FW - sz) // 2; y0 = max(0, sy - ch // 2)
        win = cv2.resize(base[y0:y0 + ch, x0:x0 + sz], (w, h), interpolation=cv2.INTER_AREA)
        bg = np.zeros_like(base) + np.array(c.get('bg', [255, 255, 255]), np.float32)
        m, sh = rmask(w, h, c.get('radius', 56))
        sc = 0.9 + 0.1 * kin; a = kin * (1 - kout)
        if sc < 0.999:
            w2, h2 = max(2, int(w * sc)), max(2, int(h * sc))
            win = cv2.resize(win, (w2, h2)); m = cv2.resize(m[..., 0], (w2, h2))[..., None]; sh = cv2.resize(sh[..., 0], (w2 + 120, h2 + 120))[..., None]
        else: w2, h2 = w, h
        X = (FW - w2) // 2; Y = cy - h2 // 2 + int(40 * (1 - kin))
        out = bg
        ys, xs = Y - 60, X - 60
        sy0, sx0 = max(0, ys), max(0, xs); sy1, sx1 = min(FH, ys + sh.shape[0]), min(FW, xs + sh.shape[1])
        out[sy0:sy1, sx0:sx1] *= 1 - sh[sy0 - ys:sy1 - ys, sx0 - xs:sx1 - xs] * a
        reg = out[Y:Y + h2, X:X + w2]
        out[Y:Y + h2, X:X + w2] = reg * (1 - m * a) + win * m * a
        return out
    Renderer.card_scene = card_scene

    # ---------------- scenes
    def topics(d, img, u, o, fg):  # many topics piling up vs a little clock
        rs = np.random.default_rng(2); names = ['дроби', 'падежи', 'уравнения', 'словарные слова', 'таблица умножения', 'части речи',
                                                 'периметр', 'деление столбиком', 'суффиксы', 'площадь', 'корни', 'задачи']
        y = FH * 0.23; x = 80
        for k, nm in enumerate(names):
            p = back(prog(u, 0.1 + k * 0.16, 0.25), 2.2)
            f = F(44, 'Bold'); w = f.getlength(nm) + 70
            if x + w > FW - 70: x = 80; y += 124
            if p > 0:
                cx, cy = x + w / 2, y + 48; ww, hh = w * p / 2, 48 * p
                fill = B if k % 3 == 0 else LB; ink = WH if k % 3 == 0 else B
                d.rounded_rectangle((cx - ww, cy - hh, cx + ww, cy + hh), int(hh), fill=fill)
                if p > 0.7: d.text((cx, cy), nm, font=f, fill=ink, anchor='mm')
            x += w + 22

    def test(d, img, u, o, fg):  # diagnostic sheet: rows checked, two gaps highlighted
        x0, y0, x1 = 110, FH * 0.27, FW - 110; rows = 6
        p = ease_out(prog(u, 0, 0.3))
        d.rounded_rectangle((x0, y0 + 50 * (1 - p), x1, y0 + 140 + rows * 120 + 50 * (1 - p)), 48, fill=WH, outline=LB, width=6)
        if p < 0.9: return
        d.text((x0 + 60, y0 + 50), 'Диагностика', font=F(48), fill=K)
        gaps = (2, 4)
        for i in range(rows):
            yy = y0 + 150 + i * 120; q = prog(u, 0.35 + i * 0.28, 0.25)
            d.rounded_rectangle((x0 + 150, yy + 22, x1 - 80 - (i % 3) * 90, yy + 52), 15, fill=LB)
            if q <= 0: d.ellipse((x0 + 60, yy + 12, x0 + 110, yy + 62), outline=LB, width=5); continue
            if i in gaps:
                d.ellipse((x0 + 60, yy + 12, x0 + 110, yy + 62), outline=B, width=6)
                d.text((x0 + 85, yy + 37), '!', font=F(36), fill=B, anchor='mm')
                r = back(q, 2.2); d.rounded_rectangle((x0 + 140, yy + 6, x1 - 60, yy + 70), 32, outline=B, width=int(5 * min(1, r)))
            else:
                d.ellipse((x0 + 60, yy + 12, x0 + 110, yy + 62), fill=B)
                d.line([(x0 + 72, yy + 37), (x0 + 82, yy + 48), (x0 + 99, yy + 26)], fill=WH, width=6)

    def calendar(d, img, u, o, fg):  # plan of N lessons filling toward a goal flag
        x0, y0 = 120, FH * 0.30; cs, gap = 108, 18; n = 20
        f = F(36, 'Bold')
        for i in range(n):
            r, c = divmod(i, 5); x, y = x0 + c * (cs + gap) + 30, y0 + r * (cs + gap)
            q = prog(u, 0.2 + i * 0.09, 0.2)
            d.rounded_rectangle((x, y, x + cs, y + cs), 26, fill=B if q > 0 else LB)
            d.text((x + cs / 2, y + cs / 2), str(i + 1), font=f, fill=WH if q > 0 else B, anchor='mm')
        q = back(prog(u, 0.2 + n * 0.09, 0.4), 2)
        if q > 0:  # goal flag
            fx, fy = x0 + 4 * (cs + gap) + 30 + cs + 20, y0 + 3 * (cs + gap)
            d.line([(fx, fy + cs), (fx, fy + cs - 150 * q)], fill=B, width=10)
            d.polygon([(fx, fy + cs - 150 * q), (fx + 80 * q, fy + cs - 120 * q), (fx, fy + cs - 90 * q)], fill=B)

    def chat(d, img, u, o, fg):  # parents' messages arriving
        msgs = o.get('msgs', [])
        y = FH * 0.30
        for k, (who, txt) in enumerate(msgs):
            p = back(prog(u, 0.2 + k * 0.9, 0.3), 1.8)
            if p <= 0: break
            f = F(44, 'SemiBold'); fw = F(32, 'Bold')
            w = max(f.getlength(txt), fw.getlength(who)) + 90; h = 150
            x = 80 if k % 2 == 0 else FW - 80 - w
            cx, cy = x + w / 2, y + h / 2
            ww, hh = w / 2 * p, h / 2 * p
            d.rounded_rectangle((cx - ww, cy - hh, cx + ww, cy + hh), int(40 * p), fill=(238, 242, 252) if tuple(o['bg']) == WH else WH)
            if p > 0.8:
                d.text((x + 45, y + 28), who, font=fw, fill=B); d.text((x + 45, y + 74), txt, font=f, fill=K)
            y += h + 50

    def jump(d, img, u, o, fg):  # bouncing ball + stretching hand lines = physical break
        cx = FW / 2; ground = FH * 0.62
        for k in range(3):
            ph = (u * 2.2 + k * 0.33) % 1; hgt = 380 * 4 * ph * (1 - ph)
            x = cx + (k - 1) * 260; y = ground - hgt; sq = 1 - 0.25 * max(0, 1 - hgt / 60)
            r = 95; d.ellipse((x - r / sq, y - r * 2 * sq, x + r / sq, y), fill=fg if k != 1 else LB)
            sw = 60 * (1 - hgt / 380) + 20; d.ellipse((x - sw, ground + 14, x + sw, ground + 30), fill=(26, 70, 200) if o['bg'] == list(B) else LB)

    SCENES.update(topics=topics, test=test, calendar=calendar, chat=chat, jump=jump)


def install2(G):
    Renderer = G['Renderer']; prog = G['prog']; ease_out = G['ease_out']; ease_in = G['ease_in']; back = G['back']; clamp = G['clamp']
    font = G['font']; SCENES = G['SCENES']; FW, FH = G['FW'], G['FH']; paste = G['paste']; text_spr = G['text_spr']
    B = (36, 87, 237); WH = (255, 255, 255); K = (17, 17, 20); LB = (220, 229, 252); YEL = (253, 203, 10)
    F = lambda s, w='ExtraBold': font('Montserrat.ttf', s, w)

    # topics chips readable on any bg
    old_topics = SCENES['topics']
    def topics(d, img, u, o, fg):
        rs_names = ['дроби', 'падежи', 'уравнения', 'словарные слова', 'таблица умножения', 'части речи', 'периметр', 'деление столбиком', 'суффиксы', 'площадь', 'корни', 'задачи']
        soft = WH if tuple(o['bg']) != WH else LB
        y = FH * 0.23; x = 80
        for k, nm in enumerate(rs_names):
            p = back(prog(u, 0.1 + k * 0.16, 0.25), 2.2); f = F(44, 'Bold'); w = f.getlength(nm) + 70
            if x + w > FW - 70: x = 80; y += 114
            if p > 0:
                cx, cy = x + w / 2, y + 44; ww, hh = w * p / 2, 44 * p
                fill = B if k % 3 == 0 else soft; ink = WH if k % 3 == 0 else B
                d.rounded_rectangle((cx - ww, cy - hh, cx + ww, cy + hh), int(hh), fill=fill)
                if p > 0.7: d.text((cx, cy), nm, font=f, fill=ink, anchor='mm')
            x += w + 22
    SCENES['topics'] = topics

    # ---- panel: a scene squeezed into a box (top half layout)
    def ov_panel(self, cv, t, o):
        if not (o['t0'] <= t < o['t1']): return
        p = ease_out(prog(t, o['t0'], 0.3)); q = ease_in(prog(t, o['t1'] - 0.2, 0.2)); a = p * (1 - q)
        if a <= 0.01: return
        bg = tuple(o.get('bg', WH)); fg = tuple(o.get('fg', B if bg != B else WH))
        img = Image.new('RGBA', (FW, FH), bg + (255,)); d = ImageDraw.Draw(img)
        SCENES[o['kind']](d, img, t - o['t0'], o, fg)
        sx0, sx1 = o.get('sx', [60, 1020]); sy0, sy1 = o['sy']; dy0, dy1 = o.get('dy', [330, 830])
        crop = img.crop((sx0, sy0, sx1, sy1))
        sc = min((dy1 - dy0) / (sy1 - sy0), 1060 / (sx1 - sx0), o.get('max_scale', 1.0)) * (0.92 + 0.08 * p)
        crop = crop.resize((max(1, int(crop.width * sc)), max(1, int(crop.height * sc))), Image.LANCZOS)
        paste(cv, crop, FW / 2, (dy0 + dy1) / 2 + 30 * (1 - p), 1, a)
    Renderer.ov_panel = ov_panel

    # ---- pill subtitles between halves
    orig_subs = Renderer.subs
    def subs(self, cv, t):
        S = self.plan['subs']
        if S.get('mode') != 'pill': return orig_subs(self, cv, t)
        if t >= self.BODY: return
        if any(o['t0'] <= t < o['t1'] for o in self.ov if o['type'] in S.get('hide_under', [])): return
        if not hasattr(self, '_groups'):
            gs, cur = [], []
            for i, w in enumerate(self.W):
                cur.append(w); nxt = self.W[i + 1] if i + 1 < len(self.W) else None
                ch = sum(len(x['w']) for x in cur)
                if nxt is None or nxt['seg'] != w['seg'] or len(cur) >= 4 or ch >= 20 or w['w'][-1] in ',.:!?—': gs.append(cur); cur = []
            self._groups = gs
        g = next((g for g in self._groups if g[0]['s'] <= t < g[-1]['e'] + 0.15), None)
        if not g: return
        size = S.get('size', 44); f = F(size, 'Bold'); gap = int(size * 0.32)
        words = [w['w'].lower().strip('…,.:;—?!«»') for w in g]
        ws = [f.getlength(x) for x in words]; tw = sum(ws) + gap * (len(ws) - 1)
        W_, H_ = int(tw + size * 1.2), int(size * 1.75)
        key = ('subpill', tuple(words), tuple(int(t >= w['s']) + int(w['s'] <= t < w['e']) for w in g))
        img = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, W_ - 1, H_ - 1), H_ // 2, fill=K + (235,))
        x = size * 0.6
        for w, s_, wd in zip(g, ws, words):
            act = w['s'] <= t < w['e']; seen = t >= w['s']
            if act: d.rounded_rectangle((x - 8, H_ * 0.16, x + s_ + 8, H_ * 0.84), 14, fill=YEL + (255,))
            d.text((x, H_ / 2), wd, font=f, fill=K if act else (WH if seen else (150, 150, 160)), anchor='lm'); x += s_ + gap
        sc = 0.9 + 0.1 * back(prog(t, g[0]['s'], 0.15))
        paste(cv, img, FW / 2, FH * S.get('y', 0.455), sc, 1)
    Renderer.subs = subs

    # ---- strong CTA: "3 дня бесплатно" + Direct mock with typed message being sent
    def cta2(d, img, u, o, fg):
        lg = Image.open(o['logo']).convert('RGBA'); lg = lg.resize((int(lg.width * 1.6), int(lg.height * 1.6)), Image.LANCZOS)
        img.alpha_composite(lg, ((FW - lg.width) // 2, 90))
        p = back(prog(u, 0.05, 0.35), 2.0)
        if p > 0:
            s1 = text_spr('3 дня', 'mont_xb', 260, YEL, -0.04, 0.0); s1 = s1.resize((max(1, int(s1.width * p)), max(1, int(s1.height * p))))
            img.alpha_composite(s1, ((FW - s1.width) // 2, int(330 + (1 - p) * 60)))
        q = ease_out(prog(u, 0.35, 0.3))
        if q > 0:
            s2 = text_spr('бесплатно', 'mont_xb', 120, WH, -0.03, 0.0); s2.putalpha(s2.getchannel('A').point(lambda v: int(v * q)))
            img.alpha_composite(s2, ((FW - s2.width) // 2, 610))
        # direct mock
        r = ease_out(prog(u, 0.7, 0.35))
        if r <= 0: return
        X0, Y0, X1, Y1 = 90, int(820 + 80 * (1 - r)), FW - 90, int(1460 + 80 * (1 - r))
        d.rounded_rectangle((X0, Y0, X1, Y1), 56, fill=WH)
        d.ellipse((X0 + 40, Y0 + 34, X0 + 120, Y0 + 114), fill=B); d.text((X0 + 80, Y0 + 74), 'S', font=F(40), fill=WH, anchor='mm')
        d.text((X0 + 145, Y0 + 40), 'SHKOLA', font=F(40), fill=K); d.text((X0 + 145, Y0 + 88), 'Директ', font=F(28, 'Medium'), fill=(140, 146, 160))
        d.line([(X0, Y0 + 150), (X1, Y0 + 150)], fill=(232, 235, 242), width=3)
        msg = 'Хочу 3 бесплатных дня'
        t_type0, t_send = 1.1, 1.1 + 0.055 * len(msg) + 0.25
        n = int(clamp((u - t_type0) / 0.055, 0, len(msg)))
        sent = u >= t_send
        iy = Y1 - 130
        d.rounded_rectangle((X0 + 36, iy, X1 - 150, iy + 92), 46, outline=(220, 224, 234), width=4, fill=(246, 247, 251))
        if not sent:
            txt = msg[:n] + ('|' if int(u * 3) % 2 == 0 else '')
            d.text((X0 + 76, iy + 46), txt if n else 'Сообщение…', font=F(38, 'SemiBold'), fill=K if n else (160, 166, 180), anchor='lm')
        bx, by = X1 - 90, iy + 46; pr = 1 - 0.15 * (1 - abs(prog(u, t_send - 0.1, 0.2) * 2 - 1)) if u > t_send - 0.1 else 1
        d.ellipse((bx - 46 * pr, by - 46 * pr, bx + 46 * pr, by + 46 * pr), fill=B)
        d.polygon([(bx - 20, by - 18), (bx + 24, by), (bx - 20, by + 18), (bx - 10, by)], fill=WH)
        if sent:
            k = back(prog(u, t_send, 0.35), 1.6); f = F(40, 'SemiBold'); w = f.getlength(msg) + 80
            my = Y0 + 200 + 40 * (1 - k)
            d.rounded_rectangle((X1 - 40 - w * k, my, X1 - 40, my + 92 * max(k, 0.05)), 46, fill=B)
            if k > 0.8:
                d.text((X1 - 40 - w + 40, my + 46), msg, font=f, fill=WH, anchor='lm')
                d.text((X1 - 44, my + 130), 'отправлено', font=F(26, 'Medium'), fill=(160, 166, 180), anchor='rm')
            z = ease_out(prog(u, t_send + 0.5, 0.4))
            if z > 0:
                rep = 'Здравствуйте! Дарим 3 дня ✨'.replace(' ✨', '')
                f2 = F(38, 'SemiBold'); w2 = f2.getlength(rep) + 80; ry = my + 170
                d.rounded_rectangle((X0 + 40, ry, X0 + 40 + w2 * z, ry + 90), 45, fill=(238, 242, 252))
                if z > 0.8: d.text((X0 + 80, ry + 45), rep, font=f2, fill=K, anchor='lm')
        # bottom call
        c = ease_out(prog(u, 0.9, 0.3))
        if c > 0:
            bounce = 14 * math.sin(u * 6)
            s3 = text_spr('Напишите нам в Директ', 'mont_xb', 70, WH, -0.02, 0.0)
            img.alpha_composite(s3, ((FW - s3.width) // 2, 1530))
            ax, ay = FW // 2, int(1650 + bounce)
            d.line([(ax, ay), (ax, ay + 70)], fill=YEL, width=14)
            d.polygon([(ax - 34, ay + 50), (ax + 34, ay + 50), (ax, ay + 96)], fill=YEL)
    SCENES['cta2'] = cta2
