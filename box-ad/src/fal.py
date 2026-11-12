"""Tiny fal.ai queue client. The API key is injected by the network proxy.
usage: python fal.py <model> <args.json> <out_prefix>
Writes <out_prefix>.json and downloads every media URL found in the result.
"""
import json, sys, time, urllib.request

model, args_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
BASE = 'https://queue.fal.run/'
HDR = {'Content-Type': 'application/json', 'Authorization': 'Key proxy-injected'}


def call(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, headers=HDR,
                                 method='POST' if data is not None else 'GET')
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


sub = call(BASE + model, json.load(open(args_path)))
status_url, resp_url = sub['status_url'], sub['response_url']
t0 = time.time()
while True:
    st = call(status_url)
    if st['status'] == 'COMPLETED':
        break
    if time.time() - t0 > 900:
        sys.exit('timeout ' + json.dumps(st))
    time.sleep(4)
res = call(resp_url)
json.dump(res, open(out + '.json', 'w'), ensure_ascii=False, indent=1)
urls = []


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'url' and isinstance(v, str) and v.startswith('http'):
                urls.append(v)
            else:
                walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(res)
for i, u in enumerate(urls):
    ext = u.split('?')[0].rsplit('.', 1)[-1][:4]
    fn = f'{out}_{i}.{ext}' if len(urls) > 1 else f'{out}.{ext}'
    urllib.request.urlretrieve(u, fn)
    print(fn, u)
print('done', round(time.time() - t0, 1), 's')
