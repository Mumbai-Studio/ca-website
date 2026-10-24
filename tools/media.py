#!/usr/bin/env python3
"""Collaborative Architecture · put a new picture on the site, in place of an old one.

The site's pictures are WebP files in public/img/<project>/ (p01 = photographs, d01 = drawings, s01 = sketches, c01-t = press covers).
This replaces one of them from a studio original (JPEG, PNG or TIFF, any size), the way the site expects it:
  - public/img/<path>.webp        the picture, at most 3,000 px on the long edge, WebP quality 80
  - public/img/<path>-800.webp    its small copy for cards and lists, when the site already has one
  - public/img/share/<slug>.jpg   the 1,200 × 630 share card, when --share <slug> is given (for a page's hero picture)
  - the picture's placeholder color in src/ca-website.html (the color painted before the photograph arrives)

Usage:  python3 tools/media.py <original> img/bgrt/p01 [--share reflected-topography] [--max 3000]
Then:   npm run build   (and check the page), then commit and push: the site updates itself.
The audit of which pictures to replace, and at what size, is "image-media-audit-2.5.csv" in the WEBSITE project.
Needs Python 3 with Pillow (pip install pillow)."""
import argparse, io, json, os, re, sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB, SRC = os.path.join(ROOT, 'public'), os.path.join(ROOT, 'src', 'ca-website.html')

a = argparse.ArgumentParser(description='Replace a picture of the site from a studio original.')
a.add_argument('original'); a.add_argument('web', help='the picture on the site, e.g. img/bgrt/p01 (no extension)')
a.add_argument('--share', help='also make the share card for this page slug, e.g. reflected-topography')
a.add_argument('--max', type=int, default=3000, help='longest edge in pixels (default 3000)')
o = a.parse_args()
web = re.sub(r'\.(webp|jpe?g|png)$', '', o.web.strip('/'))
if not web.startswith('img/'): sys.exit('the web path starts with img/, e.g. img/bgrt/p01')

im = Image.open(o.original); im = ImageOps.exif_transpose(im); icc = im.info.get('icc_profile')
if im.mode == 'CMYK': im = im.convert('RGB')
alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
im = im.convert('RGBA' if alpha else 'RGB')
if icc:   # to sRGB, the color space of the web
    try:
        from PIL import ImageCms
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc)); dst = ImageCms.createProfile('sRGB')
        im = ImageCms.profileToProfile(im, src, dst, outputMode=im.mode); icc = None
    except Exception: pass
if max(im.size) > o.max: im.thumbnail((o.max, o.max), Image.LANCZOS)

def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    kw = dict(quality=80, method=6)
    if alpha: kw['alpha_quality'] = 90
    img.save(path, 'WEBP', **kw); return os.path.getsize(path)

full = os.path.join(PUB, web + '.webp'); n = save(im, full)
print(f'{web}.webp  {im.size[0]} × {im.size[1]}  {n / 1024:.0f} KB')
small = os.path.join(PUB, web + '-800.webp')
if os.path.exists(small):
    s = im.copy(); s.thumbnail((800, 800), Image.LANCZOS); n = save(s, small); print(f'{web}-800.webp  {s.size[0]} × {s.size[1]}  {n / 1024:.0f} KB')
if o.share:
    logo = Image.open(os.path.join(PUB, 'img', 'logo-224.png')).convert('RGBA').resize((94, 94), Image.LANCZOS)
    card = ImageOps.fit(im.convert('RGB'), (1200, 630), Image.LANCZOS, centering=(0.5, 0.5)); card.paste(logo, (1069, 502), logo)
    p = os.path.join(PUB, 'img', 'share', o.share + '.jpg'); card.save(p, 'JPEG', quality=85, progressive=True, optimize=True)
    print(f'img/share/{o.share}.jpg  1200 × 630')

# the placeholder color, painted before the picture arrives
avg = im.convert('RGB').resize((1, 1), Image.LANCZOS).getpixel((0, 0)); hexc = '#%02x%02x%02x' % avg
s = open(SRC, encoding='utf-8').read(); i = s.find('window.CA_LQ=')
if i >= 0:
    j = s.index('\n', i); lq, end = json.JSONDecoder().raw_decode(s[i + len('window.CA_LQ='):j])
    for k in (web + '.webp', web + '-800.webp'):
        if k in lq.get('avg', {}) or k == web + '.webp': lq.setdefault('avg', {})[k] = hexc
    s = s[:i] + 'window.CA_LQ=' + json.dumps(lq, ensure_ascii=False, separators=(',', ':')) + s[i + len('window.CA_LQ=') + end:]
    open(SRC, 'w', encoding='utf-8').write(s); print('placeholder color', hexc)
print('done: now run  npm run build  and look at the page')
