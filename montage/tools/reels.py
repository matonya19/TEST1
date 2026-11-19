# wrapper: engine bytecode (source lost in container reset) + brand2 patches, then CLI
import marshal as _m, os as _os, sys as _s
_main = __name__ == '__main__'
__name__ = 'reels_engine'
exec(_m.loads(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'engine.pyc'), 'rb').read()[16:]))
_s.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import brand2 as _b2; _b2.install(globals()); _b2.install2(globals())
__name__ = '__main__' if _main else 'reels'
if _main:
    a = _s.argv[1:]; script = _os.path.abspath(__file__)
    if a[0] == 'setup': setup()
    elif a[0] == 'probe': probe(a[1], a[2])
    elif a[0] == 'asr': asr(a[1], json.loads(open(a[2]).read()) if _os.path.exists(a[2]) else json.loads(a[2]))
    else:
        plan = load_plan(a[1]); plan['_path'] = _os.path.abspath(a[1])
        if a[0] == 'words':
            tl = build_timeline(plan); seen = {}; out = []
            for w in tl['words']:
                k = norm(w['w']); n = seen.get(k, 0); seen[k] = n + 1
                out.append(f"{w['s']:.2f} {w['w']}" + (f'#{n}' if n else ''))
            print(' | '.join(out)); print('segments at:', [round(s['o'], 2) for s in tl['segs']], 'total', round(tl['total'], 2))
        elif a[0] == 'cues': cues(plan)
        elif a[0] == 'preview': preview(plan, [float(x) for x in a[2:]])
        elif a[0] == 'audio': audio(plan)
        elif a[0] == 'video': [_os.remove(p) for p in glob.glob(plan['work'] + '/part*.mp4')]; render_video(plan, script)
        elif a[0] == '_worker': Renderer(plan).run(int(a[2]), int(a[3]))
        elif a[0] == 'final': final(plan, script)
