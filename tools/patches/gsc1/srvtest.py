import sys, re, os, json, http.client, urllib.parse
O = 'https://collaborativearchitecture.com'
def req(port, path, method='GET'):
    c = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
    c.request(method, path, headers={'Host': 'collaborativearchitecture.com', 'X-Forwarded-Proto': 'https', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0 Safari/537.36'})
    r = c.getresponse(); r.read(); h = {k.lower(): v for k, v in r.getheaders()}; c.close(); return r.status, h
def chain(port, path):
    hops = []; p = path
    for _ in range(6):
        s, h = req(port, p); loc = h.get('location', '')
        hops.append((s, loc))
        if s in (301, 302, 307, 308) and loc.startswith(O):
            p = loc[len(O):] or '/'; continue
        return hops, s, h
    return hops, 'LOOP', {}
def summary(port, path):
    hops, final, h = chain(port, path)
    first = hops[0]
    return {'first': first[0], 'loc': first[1].replace(O, ''), 'final': final, 'hops': len(hops) - 1,
            'xrt': h.get('x-robots-tag', ''), 'csp': h.get('content-security-policy', '')[:60], 'link': h.get('link', ''),
            'cc': h.get('cache-control', ''), 'ct': h.get('content-type', '').split(';')[0]}
paths = [l.rstrip('\n') for l in open(sys.argv[1]) if l.strip()]
res = {p: {'old': summary(int(os.environ.get('PO',8081)), p), 'new': summary(int(os.environ.get('PN',8082)), p)} for p in paths}
json.dump(res, open(sys.argv[2], 'w'), indent=1)
diff = {p: v for p, v in res.items() if v['old'] != v['new']}
print(len(paths), 'paths;', len(diff), 'differ')
for p, v in diff.items():
    o, n = v['old'], v['new']
    print(f"{p}\n   old {o['first']} {o['loc']} -> {o['final']} xrt={o['xrt']!r}\n   new {n['first']} {n['loc']} -> {n['final']} xrt={n['xrt']!r} hops={n['hops']}")
