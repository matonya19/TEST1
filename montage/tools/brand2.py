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
