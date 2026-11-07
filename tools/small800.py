#!/usr/bin/env python3
"""Collaborative Architecture · make the small copies (-800) of the pictures the review copy shows at full size.

The review copy on claude.ai is held to 511 files, so the small copies of some pictures were retired there and the pictures are listed in
C.smallSame in src/ca-website.html (cards and the Work tiles then load the full picture, up to 780 KB). The published site has no file
limit: for every picture in that list this writes public/img/<path>-800.webp from public/img/<path>.webp, 800 px wide (at most 1,200 px
high), WebP quality 80, lightly sharpened, so it matches the picture as it is now. tools/build.js then gives cards and tiles the small copy
wherever it is at least as new as its picture. Run it after the pictures are updated, before the build (7 November 2026).

Usage:  python3 tools/small800.py [--public public] [--check]
Needs Python 3 with Pillow (pip install pillow)."""
import argparse, os, re, sys
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = argparse.ArgumentParser(description='Make the small copies (-800) of the pictures listed in C.smallSame.')
a.add_argument('--public', default=os.path.join(ROOT, 'public')); a.add_argument('--src', default=os.path.join(ROOT, 'src', 'ca-website.html'))
a.add_argument('--check', action='store_true', help='only list the copies that are missing or older than their picture')
o = a.parse_args()

s = open(o.src, encoding='utf-8').read()
m = re.search(r'C\.smallSame = \[([\s\S]*?)\];', s)
if not m: sys.exit('C.smallSame not found in ' + o.src)
items = re.findall(r"'(img/[^']+)'", m.group(1))
made = stale = missing = 0
for f in items:
    full, small = os.path.join(o.public, f + '.webp'), os.path.join(o.public, f + '-800.webp')
    if not os.path.exists(full): print('no picture:', f + '.webp'); missing += 1; continue
    if os.path.exists(small) and os.path.getmtime(small) >= os.path.getmtime(full): continue
    stale += 1
    if o.check: print('to make:', f + '-800.webp'); continue
    im = Image.open(full); im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') and 'A' in im.getbands() else 'RGB')
    im.thumbnail((800, 1200), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=0.6, percent=40, threshold=2))
    tmp = small + '.tmp'; im.save(tmp, 'WEBP', quality=80, method=6); os.replace(tmp, small); made += 1   # a new file, never written through a link
    print(f'{f}-800.webp  {im.size[0]} x {im.size[1]}  {os.path.getsize(small) // 1024} KB')
print(f'{len(items)} pictures in the list: {made} small copies made, {stale - made if o.check else 0} to make, {missing} pictures missing')
