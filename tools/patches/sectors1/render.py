"""Rendering helpers for patch sectors1: serve a copy of the site locally, render pages as the prerender did, bring a render to the
form the live static pages have, and carry the differences between two renders onto a live page.

The live pages went through a step after the prerender that is not in the repository. Its rules, read off the live pages and
checked by reproducing the six discipline pages byte for byte (all but the per-render seed):
  - the font block (<style id="ca-fonts">) closes the head;
  - a lazy picture (img.bgi, loading=lazy) whose container is laid out sits in <noscript>, with the full-size file and without the
    loader's data-sz, data-px and data-fb; its width and height, when the render loaded it, are the live file's (size list);
  - thumbnail spans (span.th) are left as the template writes them, for the scripts to fill."""
import asyncio, difflib, http.server, io, json, os, re, threading
from urllib.parse import urlparse, unquote

TYPES = {'.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2',
         '.mp4': 'video/mp4', '.json': 'application/json', '.xml': 'application/xml', '.txt': 'text/plain', '.md': 'text/markdown', '.pdf': 'application/pdf'}

def _stand_in():
    from PIL import Image
    b = io.BytesIO(); Image.new('RGB', (16, 9), (200, 200, 200)).save(b, 'WEBP'); return b.getvalue()
STAND_IN = _stand_in()

def serve(root, extra_roots=(), port=0):
    """A static server for a site folder. Unknown addresses get the Expertise page as a shell (the scripts route by address).
    A picture that is not in the local copy is answered with a small stand-in, so a render never records a loading error; the
    final markup takes file names and sizes from the live size list, never from the stand-in."""
    roots = [root, *extra_roots]
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _send(self, b, ctype):
            self.send_response(200); self.send_header('content-type', ctype); self.send_header('content-length', str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            u = unquote(urlparse(self.path).path); ext = os.path.splitext(u)[1].lower()
            if ext and ext != '.html':
                for r in roots:
                    f = os.path.join(r, u.lstrip('/'))
                    if os.path.isfile(f): return self._send(open(f, 'rb').read(), TYPES.get(ext, 'application/octet-stream'))
                if u.startswith('/img/') and ext in ('.webp', '.jpg', '.png'): return self._send(STAND_IN, 'image/webp')
                self.send_response(404); self.end_headers(); return
            p = u if u.endswith('/') or u.endswith('.html') else u + '/'
            f = os.path.join(root, p.lstrip('/'), 'index.html') if p.endswith('/') else os.path.join(root, p.lstrip('/'))
            if not os.path.isfile(f): f = os.path.join(root, 'expertise', 'index.html')
            self._send(open(f, 'rb').read(), 'text/html; charset=utf-8')
    s = http.server.ThreadingHTTPServer(('127.0.0.1', port), H); threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, s.server_address[1]

INIT = ("Object.defineProperty(navigator,'webdriver',{get:()=>false});window.__PRERENDER=true;try{sessionStorage.setItem('ca-pl','1')}catch(e){}"
        # a fixed random source, so two renders of a page (old and new scripts) draw the same seed and the same picture order
        "(function(){let s=20261126;Math.random=function(){s=(Math.imul(s,1664525)+1013904223)>>>0;return s/4294967296}})();")
SNAP = r"""() => {
  const pl = document.getElementById('pl'); if (pl) pl.setAttribute('hidden', '');
  document.querySelectorAll('[data-lq]').forEach(el => el.removeAttribute('data-lq'));
  document.querySelectorAll('img.bgi').forEach(i => { if (!i.parentElement || !i.parentElement.getClientRects().length) i.setAttribute('data-nw', '1'); });
  return '<!doctype html>\n' + document.documentElement.outerHTML;
}"""

async def _render(port, paths, extract, waits):
    from playwright.async_api import async_playwright
    out, errors = {}, []
    async with async_playwright() as p:
        exe = '/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None
        b = await p.chromium.launch(executable_path=exe, args=['--no-sandbox', '--no-proxy-server'])
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')
        await ctx.add_init_script(INIT)
        await ctx.route('**/*', lambda r: r.continue_() if '127.0.0.1' in r.request.url else r.abort())
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: errors.append(str(e)))
        for path in paths:
            await pg.goto(f'http://127.0.0.1:{port}' + path, wait_until='load')
            await pg.wait_for_function("window.CA_SEO && document.querySelector('#app').children.length && document.querySelector('script#ca-ld')", timeout=30000)
            await pg.wait_for_timeout((waits or {}).get(path, 250))
            out[path] = await pg.evaluate(SNAP)
        if extract:
            out['__feeds__'] = await pg.evaluate("(()=>({files: CA_SEO.feeds(), md: CA_SEO.pagesMd()}))()")
        await b.close()
    return out, errors

def render(root, paths, extra_roots=(), feeds=False, waits=None):
    s, port = serve(root, extra_roots)
    try: return asyncio.run(_render(port, paths, feeds, waits))
    finally: s.shutdown()

# ---------------------------------------------------------------- live form ----------------------------------------------------------
def clean(h):   # what the loader adds to a page at run time
    h = re.sub(r'<script src="/assets/(?:sizes|data-ca-[a-z]+-j|site-\d)\.[0-9a-f]{12}\.js"></script>', '', h)
    h = re.sub(r'<script type="application/json" id="ca-(?:data|land|kw)-j">.*?</script>', '', h, flags=re.S)
    h = re.sub(r'<link rel="preload" as="script" href="/assets/[^"]+">', '', h)
    return h

def sizes_of(site):
    f = [x for x in os.listdir(os.path.join(site, 'assets')) if x.startswith('sizes.')][0]
    t = open(os.path.join(site, 'assets', f), encoding='utf-8').read()
    return {k: v[:2] for k, v in json.loads(t[t.find('{'):t.rfind('}') + 1]).items()}

IMG = re.compile(r'<img class="bgi"[^>]*>')
def normalize(h, sizes):
    h = clean(h)
    m = re.search(r'<style id="ca-fonts">.*?</style>', h, re.S)
    if m: h = h.replace(m.group(0), '', 1); h = h.replace('</head>', m.group(0) + '</head>', 1)
    def fix(t, bg):
        if 'loading="lazy"' not in t: return t.replace(' data-nw="1"', '')
        nw = ' data-nw="1"' in t
        t = re.sub(r' data-sz="[^"]*"| data-px="[^"]*"| data-fb="1"| data-nw="1"', '', t)
        if bg: t = re.sub(r' src="[^"]*"', f' src="{bg}"', t, 1)
        if ' width="' in t and bg and sizes.get(bg.lstrip('/')):
            w, hh = sizes[bg.lstrip('/')]; t = re.sub(r' width="\d+" height="\d+"', f' width="{w}" height="{hh}"', t)
        return t if nw else '<noscript>' + t + '</noscript>'
    out, pos = [], 0
    for m in IMG.finditer(h):
        if h[max(0, m.start() - 10):m.start()] == '<noscript>': continue
        k = h.rfind('<', 0, m.start()); pm = re.search(r'data-bg="([^"]+)"', h[k:m.start()])
        out += [h[pos:m.start()], fix(m.group(0), pm.group(1) if pm else None)]; pos = m.end()
    h = ''.join(out + [h[pos:]])
    def th(m):
        t = m.group(0).replace(' data-shown="1" data-done="1"', '')
        return re.sub(r' ?background-image: url\(&quot;[^&]*&quot;\);', '', t).replace(' style=""', '')
    return re.sub(r'<span class="th" [^>]*>', th, h)

# ---------------------------------------------------------------- carrying changes -----------------------------------------------------
TOK = re.compile(r'(?=<)')                       # one token per tag, with the text that follows it
toks = lambda h: [t for t in TOK.split(h) if t]
# the seed differs per render, and the hero gains "settled" when its opening animation ends (timing, not content)
key = lambda t: re.sub(r' data-seed="\d+"', '', t).replace('<section class="hero settled"', '<section class="hero"')

def hunks(a, b):
    A, B = toks(a), toks(b); sm = difflib.SequenceMatcher(None, [key(x) for x in A], [key(x) for x in B], autojunk=False)
    return [(op, i1, i2, j1, j2) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal'], A, B

def carry(live, old, new, skip=lambda a, b: False, ctx=3):
    """Apply the differences old -> new (two renders) to the live page. Each change is placed by the old text it replaces with up
    to ctx tokens on either side, matched exactly and once in the live page. Returns the page and a report; raises if a change
    cannot be placed."""
    hs, A, B = hunks(old, new); L = toks(live); KL = [key(x) for x in L]; report = []
    for op, i1, i2, j1, j2 in reversed(hs):
        a, b = A[i1:i2], B[j1:j2]
        if skip(''.join(a), ''.join(b)): report.append(('skipped', op, ''.join(b)[:120])); continue
        placed = None
        for before in range(ctx, -1, -1):
            for after in range(ctx, -1, -1):
                if before + after + len(a) == 0 or i1 - before < 0 or i2 + after > len(A): continue
                pat = [key(x) for x in A[i1 - before:i1]] + [key(x) for x in a] + [key(x) for x in A[i2:i2 + after]]
                hits = [s for s in range(len(KL) - len(pat) + 1) if KL[s:s + len(pat)] == pat]
                if len(hits) == 1: placed = (hits[0] + before, len(a)); break
            if placed: break
        if not placed: raise SystemExit(f'cannot place a change ({op}): {"".join(a)[:200]!r} -> {"".join(b)[:200]!r}')
        s, n = placed; L[s:s + n] = b; KL[s:s + n] = [key(x) for x in b]
        report.append(('applied', op, (''.join(b) or ''.join(a))[:120]))
    return ''.join(L), list(reversed(report))

def carry_lines(live, old, new):
    """The same for text files (Markdown, llms, sitemap), line by line."""
    L, A, B = live.split('\n'), old.split('\n'), new.split('\n')
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    for op, i1, i2, j1, j2 in reversed([o for o in sm.get_opcodes() if o[0] != 'equal']):
        placed = None
        for before in range(3, -1, -1):
            for after in range(3, -1, -1):
                if i1 - before < 0 or i2 + after > len(A) or before + after + (i2 - i1) == 0: continue
                pat = A[i1 - before:i2 + after]
                hits = [s for s in range(len(L) - len(pat) + 1) if L[s:s + len(pat)] == pat]
                if len(hits) == 1: placed = hits[0] + before; break
            if placed is not None: break
        if placed is None: raise SystemExit(f'cannot place a text change: {A[i1:i2][:3]} -> {B[j1:j2][:3]}')
        L[placed:placed + (i2 - i1)] = B[j1:j2]
    return '\n'.join(L)
