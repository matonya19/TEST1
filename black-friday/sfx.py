"""Synthesised sound design for the SHKOLA Black Friday video (11.5 s timeline).
Usage: python sfx.py out.wav [--no-music]
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
DUR = 11.5
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)


def t_(d):
    return np.arange(int(SR * d)) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)


def hp(x, f):
    return sosfilt(butter(2, f, btype='high', fs=SR, output='sos'), x)


def lp(x, f):
    return sosfilt(butter(2, f, btype='low', fs=SR, output='sos'), x)


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414
    R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414


def env(n, a, d_total):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.clip(1 - (t - a) / max(d_total - a, 1e-4), 0, 1)
    return e


# ---------- elements ----------
def whoosh(d=0.6, up=True):
    n = int(SR * d); x = rng.standard_normal(n)
    # sweep by crossfading bands
    lo = bp(x, 300, 1200); hi = bp(x, 1800, 6000)
    k = np.linspace(0, 1, n) if up else np.linspace(1, 0, n)
    y = lo * (1 - k) + hi * k
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return y * e * 0.5


def pop(f0=900, f1=260, d=0.12):
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t * 45)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 32) * 0.8


def chime(f, d=0.9, bright=1.0):
    t = t_(d)
    y = (np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * f * 2.01 * t) * bright
         + .2 * np.sin(2 * np.pi * f * 3.02 * t) * bright) * np.exp(-t * 5)
    return y * np.minimum(1, t / 0.004) * 0.35


def tick(f=2400):
    t = t_(0.05)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 120) * .5 + hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * .3)


def marker(d=0.4):
    n = int(SR * d); t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 1500, 5500)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 22 * t + 3 * np.sin(2 * np.pi * 3 * t))  # scratchy strokes
    e = np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.06)
    squeak = np.sin(2 * np.pi * (2600 + 400 * t / d) * t) * 0.06
    return (x * am * 0.32 + squeak) * e


def buzz():
    out = np.zeros(int(SR * 0.42))
    for k, f in enumerate([196, 165]):
        t = t_(0.14); s = np.sign(np.sin(2 * np.pi * f * t)) * 0.18
        s = lp(s, 1800) * env(len(t), 0.005, 0.14)
        i = int(k * 0.17 * SR); out[i:i + len(s)] += s
    return out


def sparkle(d=0.8, count=9, seed=3):
    r = np.random.default_rng(seed); out = np.zeros(int(SR * d))
    for _ in range(count):
        f = r.uniform(2500, 6000); at = r.uniform(0, d * 0.6); t = t_(0.25)
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 18) * r.uniform(.05, .12)
        i = int(at * SR); j = min(len(out), i + len(s)); out[i:j] += s[: j - i]
    return out


def riser(d=0.5):
    t = t_(d); f = 300 * (6 ** (t / d))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.08
    noise = hp(rng.standard_normal(len(t)), 2500) * 0.12
    return (tone + noise) * (t / d) ** 2


# ---------- music bed: 120 bpm, Am-F-C-G ----------
def music():
    bpm = 120; beat = 60 / bpm
    out_l = np.zeros(N); out_r = np.zeros(N)
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]]  # Am F C G
    bass = [110.0, 87.31, 130.81, 98.0]
    nb = int(DUR / beat) + 1
    for b in range(nb):
        at = b * beat; bar = (b // 4) % 4
        # kick
        t = t_(0.3); f = 45 + 90 * np.exp(-t * 30)
        k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.55
        i = int(at * SR); j = min(N, i + len(k)); out_l[i:j] += k[: j - i]; out_r[i:j] += k[: j - i]
        # offbeat hat
        t = t_(0.05); h = hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 90) * 0.12
        i = int((at + beat / 2) * SR); j = min(N, i + len(h))
        if j > i: out_l[i:j] += h[: j - i] * .7; out_r[i:j] += h[: j - i]
        # plucked chord stab on offbeat
        t = t_(0.35); st = sum(np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t) for f in chords[bar])
        st = st * np.exp(-t * 11) * 0.07
        if j > i:
            j2 = min(N, i + len(st)); out_l[i:j2] += st[: j2 - i] * 1.0; out_r[i:j2] += st[: j2 - i] * .8
        # bass on beat
        t = t_(beat * .9); bs = np.sin(2 * np.pi * bass[bar] * t) * np.exp(-t * 4) * 0.25
        i = int(at * SR); j = min(N, i + len(bs)); out_l[i:j] += bs[: j - i]; out_r[i:j] += bs[: j - i]
    # soft pad
    t = np.arange(N) / SR; pad = np.zeros(N)
    for bar in range(int(DUR / (4 * beat)) + 1):
        s0 = int(bar * 4 * beat * SR); s1 = min(N, int((bar + 1) * 4 * beat * SR))
        tt = t[s0:s1] - t[s0]
        pad[s0:s1] = sum(np.sin(2 * np.pi * f * tt) for f in chords[bar % 4]) * np.minimum(1, tt / .3) * np.minimum(1, (tt[-1] - tt + 1e-3) / .3) * 0.025
    out_l += pad; out_r += pad
    fade = np.minimum(1, np.minimum(t / 0.4, (DUR - t) / 0.8))
    return out_l * fade, out_r * fade


# ---------- timeline (matches scene timings) ----------
add(pop(700, 300), 0.15, .5)                       # title pop
add(whoosh(0.8, up=True), 0.25, .9)                # diary slides in
add(tick(), 1.0, .5, .2)                           # caption 1
add(buzz(), 1.32, .9)                              # bad grades shake
for k, s in enumerate([2.0, 2.5, 3.0, 3.5]):       # marker swipes + check dings
    add(marker(0.4), s, .9, .3)
    add(chime([784, 880, 988, 1175][k], .6), s + .33, .55, .1)
add(tick(2000), 2.3, .45, -.2)                     # caption 2
add(whoosh(0.7, up=False), 4.25, .9)               # diary slides away
for at, f in [(4.6, 1046.5), (5.3, 1318.5)]:       # offer cards
    add(pop(900, 240), at, .9)
    add(chime(f, 1.2), at + .35, .8)
    add(sparkle(seed=int(at * 10)), at + .35, 1.0, .4 if f > 1100 else -.4)
add(tick(), 6.2, .5, .2); add(tick(2100), 7.6, .5, -.2)   # benefit captions
add(riser(0.5), 8.5, 1.0)                          # build to CTA
add(pop(1000, 300), 9.0, .9); add(chime(1568, 1.2), 9.05, .7)
add(sparkle(1.0, 12, seed=9), 9.8, 1.2)            # button shine

if '--no-music' not in sys.argv:
    ml, mr = music(); L += ml * .28; R += mr * .28

mix = np.stack([L, R], 1)
mix = mix / max(1e-9, np.abs(mix).max()) * 0.89
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print('ok', mix.shape)
