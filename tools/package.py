#!/usr/bin/env python3
"""Collaborative Architecture · deployment packages for a host the build cannot reach (9 November 2026).

The server is isolated, so GitHub cannot upload to it. After the first full package, each update is a small zip that holds only the files
that are new or changed since the version the host last applied, with a list of files to delete and the host's instructions.

  python3 tools/package.py full   --dist dist --out packages            # the whole site, and its fingerprint (the baseline)
  python3 tools/package.py update --dist dist --out packages            # only what changed since the last package the host applied
  python3 tools/package.py applied <version>                            # record that the host has applied that package

Each package writes version.txt into the site (so anyone can check which version is live at /version.txt) and keeps a fingerprint of
every file (path, size, SHA-256) in deploy/manifests/<version>.json. deploy/manifests/live.txt names the version the host has applied:
an update is always made against that one, so packages must be applied in order. Never packaged: build-report.json, api/config.php
(the server's own mail password) and _private/ (the copies of messages on the server)."""
import argparse, datetime, hashlib, json, os, sys, zipfile
from zoneinfo import ZoneInfo
IST = ZoneInfo('Asia/Kolkata')   # the studio's time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, 'deploy', 'manifests')
ORIGIN = 'https://collaborativearchitecture.com'
SKIP = ('build-report.json', 'api/config.php')
SKIP_DIRS = ('_private/',)

def files(dist):
    out = {}
    for dp, dn, fn in os.walk(dist):
        for f in fn:
            p = os.path.join(dp, f); r = os.path.relpath(p, dist).replace(os.sep, '/')
            if r in SKIP or r.startswith(SKIP_DIRS): continue
            h = hashlib.sha256()
            with open(p, 'rb') as fh:
                for b in iter(lambda: fh.read(1 << 20), b''): h.update(b)
            out[r] = [os.path.getsize(p), h.hexdigest()]
    return out

def live():
    p = os.path.join(MAN, 'live.txt')
    return open(p).read().strip() if os.path.exists(p) else ''

def write_version(dist, version, base):
    with open(os.path.join(dist, 'version.txt'), 'w') as f:
        f.write(f'Collaborative Architecture website\nversion {version}\nbuilt {datetime.datetime.now(IST).isoformat(timespec="minutes")}\n'
                + (f'update from {base}\n' if base else 'full package\n'))

def page_url(r):
    if r.endswith('index.html'): return ORIGIN + '/' + r[:-len('index.html')]
    return None

def zip_files(dist, names, out, extra):
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for r in sorted(names):
            # already-compressed media are stored as they are
            z.write(os.path.join(dist, r), r, compress_type=zipfile.ZIP_STORED if r.endswith(('.webp', '.mp4', '.pdf', '.png', '.jpg', '.woff2', '.zip')) else zipfile.ZIP_DEFLATED)
        for name, text in extra.items(): z.writestr(name, text)

README_FULL = """Collaborative Architecture website, full package {v}

1. Upload the CONTENTS of this zip (not the zip itself) to the site's web folder (for example public_html/), keeping the folders.
   This file and DELETE.txt need not be uploaded.
2. Keep the server's own api/config.php (the mail settings) and the _private/ folder: this package never contains them.
3. Check https://collaborativearchitecture.com/version.txt shows: version {v}
4. Reply to the studio that version {v} is live.
"""
README_UPDATE = """Collaborative Architecture website, update {v} (to be applied on top of version {b})

1. Check that the site is at version {b}: https://collaborativearchitecture.com/version.txt
   If it is not, stop and tell the studio: updates must be applied in order.
2. Upload the CONTENTS of this zip over the site's web folder, keeping the folders and replacing the files already there,
   all in one go (the pages name new script files that come in the same package). This file, DELETE.txt and CHANGED-URLS.txt need not be uploaded.
3. Delete from the web folder the files listed in DELETE.txt ({nd} file(s)), if any.
4. Never replace api/config.php or the _private/ folder: this package never contains them.
5. Check https://collaborativearchitecture.com/version.txt shows: version {v}
6. Reply to the studio that version {v} is live.

{nn} new and {nc} changed files, {mb} MB.
"""

def main():
    a = argparse.ArgumentParser(description='Full and update packages for the isolated server.')
    a.add_argument('mode', choices=['full', 'update', 'applied'])
    a.add_argument('version', nargs='?', help='applied: the version the host has applied')
    a.add_argument('--dist', default=os.path.join(ROOT, 'dist')); a.add_argument('--out', default=os.path.join(ROOT, 'packages'))
    a.add_argument('--name', default='', help='a label for this version, e.g. v488 (default: date and time)')
    o = a.parse_args(); os.makedirs(MAN, exist_ok=True)
    if o.mode == 'applied':
        if not o.version or not os.path.exists(os.path.join(MAN, o.version + '.json')): sys.exit('no package of that version: ' + str(o.version))
        open(os.path.join(MAN, 'live.txt'), 'w').write(o.version + '\n'); print('live version:', o.version); return
    if not os.path.isdir(o.dist): sys.exit('no build at ' + o.dist + ': run node tools/build.js first')
    os.makedirs(o.out, exist_ok=True)
    version = datetime.datetime.now(IST).strftime('%Y-%m-%d-%H%M') + (('-' + o.name) if o.name else '')
    base = live() if o.mode == 'update' else ''
    if o.mode == 'update' and not base: sys.exit('no version is recorded as live yet: make the full package first, then record it with "applied"')
    write_version(o.dist, version, base)
    now = files(o.dist)
    json.dump(now, open(os.path.join(MAN, version + '.json'), 'w'), indent=0, sort_keys=True)
    if o.mode == 'full':
        out = os.path.join(o.out, f'CA-website-{version}-full.zip')
        zip_files(o.dist, now.keys(), out, {'README-HOST.txt': README_FULL.format(v=version)})
        print(f'full package: {out}  ({len(now)} files, {sum(v[0] for v in now.values()) / 1e6:.1f} MB of site)')
    else:
        old = json.load(open(os.path.join(MAN, base + '.json')))
        new = [r for r in now if r not in old]; chg = [r for r in now if r in old and old[r][1] != now[r][1]]; gone = sorted(r for r in old if r not in now)
        mb = sum(now[r][0] for r in new + chg) / 1e6
        urls = sorted(u for u in (page_url(r) for r in new + chg) if u)
        out = os.path.join(o.out, f'CA-website-{version}-update-from-{base}.zip')
        zip_files(o.dist, new + chg, out, {'README-HOST.txt': README_UPDATE.format(v=version, b=base, nd=len(gone), nn=len(new), nc=len(chg), mb=f'{mb:.1f}'),
                                           'DELETE.txt': ''.join(r + '\n' for r in gone), 'CHANGED-URLS.txt': ''.join(u + '\n' for u in urls)})
        print(f'update package: {out}  ({len(new)} new, {len(chg)} changed, {len(gone)} to delete, {mb:.1f} MB)')
    print('when the host confirms it is live: python3 tools/package.py applied', version)

if __name__ == '__main__':
    main()
