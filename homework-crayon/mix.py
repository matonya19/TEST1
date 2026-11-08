"""mix.py — the user's original soundtrack (voice + music) untouched, plus quiet crayon/paper foley from events.json → out/mix.wav"""
import json, os, sys
import numpy as np, soundfile as sf
LIB = os.environ.get('LIB', '/root/lemo-opuscar')
sys.path.insert(0, os.path.join(LIB, 'core', 'audio'))
from sfx import SR, noise, bp, lp, hp, t_, env_exp, norm, thump, pop, add, limit

HERE = os.path.dirname(os.path.abspath(__file__))
orig, sr = sf.read(os.path.join(HERE, 'audio', 'original.wav'), always_2d=True)
assert sr == SR, sr
EV = json.load(open(os.path.join(HERE, 'events.json')))
dur = max(EV['dur'], len(orig) / SR)
fol = np.zeros((int(dur * SR) + SR, 2))
rng = np.random.default_rng(3)

def crayon(d, rate=7.0, bright=1.0):
    """wax stick-slip on paper: band-passed noise, grain modulated by back-and-forth strokes"""
    n = bp(noise(d), 1800 * bright, 6500 * bright)
    tt = t_(d); m = .55 + .45 * np.abs(np.sin(np.pi * rate * tt + rng.random() * 3))
    grain = (rng.random(len(n)) < .02) * rng.standard_normal(len(n)) * 3
    e = np.minimum(1, np.minimum(tt / .04, (d - tt) / .08).clip(0))
    return norm((n * m + bp(grain, 2500, 7000)) * e)

def paper(v=1.0):
    d = .35; tt = t_(d)
    return norm(bp(noise(d), 1200, 7000) * np.exp(-tt / .09) * (1 + .5 * np.sin(tt * 90))) * v

def crumple(v=1.0):
    d = .45; x = np.zeros(int(d * SR))
    for k in range(40):
        at = int(rng.random() * (len(x) - 900)); x[at:at + 900] += bp(noise(900 / SR), 1500, 8000) * np.exp(-np.arange(900) / 180) * rng.random()
    return norm(x) * v

def rub(d, v=1.0):
    tt = t_(d); m = .4 + .6 * np.abs(np.sin(np.pi * 5 * tt))
    return norm(bp(noise(d), 300, 2200) * m * np.minimum(1, np.minimum(tt / .05, (d - tt) / .1).clip(0))) * v

def brush(d, v=1.0):
    tt = t_(d); e = np.sin(np.pi * tt / d) ** .7
    return norm(lp(noise(d), 1500) * e + bp(noise(d), 3000, 6000) * e * .2) * v

for e in EV['ev']:
    ty, t, d = e['type'], e['t'], e.get('dur', .6)
    if ty in ('write',): add(fol, crayon(d, 9, 1.15), t, .22, -.2)
    elif ty in ('draw',): add(fol, crayon(d, 4, .9), t, .25, .1)
    elif ty in ('scribble',): add(fol, crayon(d, 12, 1.0), t, .2, -.1)
    elif ty == 'zigzag': add(fol, crayon(d, 14, 1.1), t, .2, .2)
    elif ty == 'thud': add(fol, thump(1.0, 90), t, .5, 0)
    elif ty == 'paper': add(fol, paper(), t, .3, rng.uniform(-.4, .4))
    elif ty == 'crumple': add(fol, crumple(), t, .28, rng.uniform(-.4, .4))
    elif ty == 'erase': add(fol, rub(d), t, .3, 0)
    elif ty == 'brush': add(fol, brush(d), t, .3, .3)
    elif ty == 'pop': add(fol, pop(.8), t, .25, 0)

n = len(orig)
fol = fol[:max(n, int(EV['dur'] * SR))]
mix = np.zeros_like(fol); mix[:n] += orig
# foley sits well under the voice: −20 dB relative to the original's RMS
r0 = np.sqrt(np.mean(orig ** 2)); rf = np.sqrt(np.mean(fol[fol != 0] ** 2)) if np.any(fol) else 1
mix += fol * (r0 / rf) * 10 ** (-17 / 20)
mix = limit(mix, .95) if mix.ndim == 1 else np.stack([limit(mix[:, 0], .95), limit(mix[:, 1], .95)], 1)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), mix.astype(np.float32), SR)
print('mix', mix.shape, 'peak', float(np.abs(mix).max()))
