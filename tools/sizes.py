#!/usr/bin/env python3
"""Collaborative Architecture · the lighter copies of the pictures for phones and smaller boxes (9 November 2026, approved by Mujib:
benchmark audit P1, phone speed before launch). Run by tools/build.js; it can also be run by hand.

tools/build.js visits every page at phone size and writes what each picture is used for (plan JSON):
  {"widths": ["img/souk/p02.webp", ...],                 pictures drawn smaller than a screen somewhere (galleries, drawings, cards)
   "crops":  [["img/souk/p01.webp", 50], ...]}           pictures that fill a box taller than it is wide, with the box's focal point (%)
For each, this makes, from the picture in public/ and into the cache folder (kept between builds; a copy is remade only when its picture
changes):
  - name-w800.webp and name-w1280.webp: the picture 800 and 1,280 px wide (only where the picture is at least 1,100 and 1,600 px wide);
  - name-m50.webp: the picture's full height, at least three quarters as wide as it is high (widened by up to 99 px so its left edge
    falls on a whole pixel), cut at the focal point (here 50%) exactly as the browser places a cover picture (left edge = focal point x
    (picture width - crop width)), so a screen whose box is no wider than the crop draws exactly the same pixels from it.
WebP quality 90, Lanczos resampling, no sharpening, the picture's colour profile kept. Then it writes the list the page reads
(window.CA_SIZES): {"img/souk/p01.webp": [1500, 1000, [800], {"50": 750}], ...}.

Usage:  python3 tools/sizes.py --public public --cache .cache/sizes --plan plan.json --out sizes.json
Needs Python 3 with Pillow."""
import argparse, hashlib, json, math, os, sys
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

Q = 90                      # WebP quality of the copies (the masters are high-quality WebP; 90 keeps them indistinguishable)
WIDTHS = ((800, 1100), (1280, 1600))   # (copy width, smallest picture width that gets it)
CROP = 0.75                 # crop width / height
VERSION = 'sizes-2'         # part of every copy's fingerprint: changing the method remakes the copies

def fingerprint(src):
    st = os.stat(src); return f'{VERSION}|q{Q}|{st.st_size}|{int(st.st_mtime)}'

def save(im, path, icc):
    tmp = path + '.tmp'
    kw = dict(quality=Q, method=6)
    if icc: kw['icc_profile'] = icc
    im.save(tmp, 'WEBP', **kw); os.replace(tmp, path)

def make(job):
    key, src, cache, widths, xs = job
    out = {'key': key, 'files': [], 'w': None, 'h': None, 'ws': [], 'crops': {}, 'made': 0}
    try:
        im = Image.open(src); im.load()
    except Exception as e:
        return dict(out, error=f'{key}: {e}')
    W, H = im.size; out['w'], out['h'] = W, H
    icc = im.info.get('icc_profile')
    if im.mode not in ('RGB', 'RGBA'): im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
    base = os.path.join(cache, key[:-5])          # without .webp
    os.makedirs(os.path.dirname(base), exist_ok=True)
    fp = fingerprint(src)
    def fresh(path):
        meta = path + '.fp'
        return os.path.exists(path) and os.path.exists(meta) and open(meta).read() == fp
    def mark(path): open(path + '.fp', 'w').write(fp)
    if widths:
        for w, minW in WIDTHS:
            if W < minW: continue
            path = f'{base}-w{w}.webp'
            if not fresh(path):
                h = max(1, round(H * w / W)); save(im.resize((w, h), Image.LANCZOS), path, icc); mark(path); out['made'] += 1
            out['ws'].append(w); out['files'].append(key[:-5] + f'-w{w}.webp')
    c0 = math.ceil(H * CROP)
    for x in sorted(set(xs or [])):
        # the crop's width is widened (by at most 99 px) until its left edge, focal point x (picture width - crop width), falls on a whole
        # pixel: the crop then lies exactly where the browser places the picture, so the screen draws the very same pixels
        cw = next((c for c in range(c0, min(W, c0 + 100)) if (x * (W - c)) % 100 == 0), c0)
        if cw > W * 0.85: continue                # a crop that saves less than 15% is not worth a file
        path = f'{base}-m{x}.webp'
        if not fresh(path):
            left = (x * (W - cw)) // 100 if (x * (W - cw)) % 100 == 0 else round(x / 100 * (W - cw))
            save(im.crop((left, 0, left + cw, H)), path, icc); mark(path); out['made'] += 1
        out['crops'][str(x)] = cw; out['files'].append(key[:-5] + f'-m{x}.webp')
    return out

def main():
    a = argparse.ArgumentParser(description='Make the lighter copies of the pictures and the list the page reads.')
    a.add_argument('--public', required=True); a.add_argument('--cache', required=True); a.add_argument('--plan', required=True); a.add_argument('--out', required=True)
    a.add_argument('--jobs', type=int, default=max(1, min(6, (os.cpu_count() or 2))))
    o = a.parse_args()
    plan = json.load(open(o.plan))
    widths = set(k for k in plan.get('widths', []) if k.endswith('.webp'))
    crops = {}
    for k, x in plan.get('crops', []):
        if k.endswith('.webp') and isinstance(x, (int, float)) and 0 <= x <= 100: crops.setdefault(k, set()).add(int(round(x)))
    keys = sorted(widths | set(crops))
    jobs = []
    for k in keys:
        src = os.path.join(o.public, k)
        if not os.path.isfile(src): print('no picture:', k, file=sys.stderr); continue
        jobs.append((k, src, o.cache, k in widths, sorted(crops.get(k, []))))
    manifest, files, made, errors = {}, [], 0, []
    with ProcessPoolExecutor(o.jobs) as ex:
        for r in ex.map(make, jobs, chunksize=4):
            if r.get('error'): errors.append(r['error']); continue
            made += r['made']
            if r['ws'] or r['crops']:
                manifest[r['key']] = [r['w'], r['h'], r['ws'], r['crops']]; files += r['files']
    json.dump({'sizes': manifest, 'files': files}, open(o.out, 'w'), separators=(',', ':'), sort_keys=True)
    print(f'sizes: {len(manifest)} pictures, {len(files)} copies ({made} made now, the rest from the cache){", " + str(len(errors)) + " unreadable" if errors else ""}')
    for e in errors[:10]: print('  could not read', e, file=sys.stderr)

if __name__ == '__main__':
    main()
