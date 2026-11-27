#!/usr/bin/env python3
"""Live patch 2026-11-26-sectors1, on top of 2026-11-25-seo4 (which carries seo3 and bing1; none of them uploaded yet).

From Mujib's marked review of 25 November 2026 (approved draft of 26 November):
  1. Six sector pages under Expertise (/expertise/<sector>/): Workplace and Research, Residential, Civic and Cultural,
     Hospitality, Educational, Real Estate and Developers. Listed below the six disciplines, under "Sectoral expertise",
     on the Expertise page and in the Expertise block on Home. The disciplines and their wording are unchanged.
  2. Studio: the practice in figures and selected honors, a section above Key facts.
  3. Awards: 2026, The Iconic Gateway shortlisted and Project Alpha longlisted, UltraTech IndiaNext Innovation Awards
     (also on the two project pages).
  4. The Barn: area, scope and its sector in the fact panel.
  5. 50th Cross Road: the studio's enhanced films (Cleaned folder, 3 November 2026) replace the 1 November encodes, under new
     names (…-r2), since films are cached for 30 days.
  6. The Measured City: a new picture (View 2) for its card on the Civic and Cultural page.

Nothing else changes: every other page differs only in the address of the loader script and the stylesheet.

Stage 1 (this script) edits the shared scripts and the stylesheet with exact substitutions, adds the media, and writes the full
site to <out>/full. Stage 2 (pages_sectors1.py) renders the new and changed pages and assembles the upload folder.

Usage: make_patch_sectors1.py <seo4 full site> <Measured City View 2 master .jpg> <50th Cross Road -r2 folder> <out dir>"""
import sys, os, re, json, hashlib, shutil, io
from PIL import Image, ImageCms, ImageFilter
base, mc_master, vid_dir, out = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
full = os.path.join(out, 'full'); shutil.rmtree(out, ignore_errors=True); shutil.copytree(base, full)
rd = lambda p: open(os.path.join(full, p), encoding='utf-8', newline='').read()
def wr(p, t):
    q = os.path.join(full, p); os.makedirs(os.path.dirname(q), exist_ok=True); open(q, 'w', encoding='utf-8', newline='').write(t)
h12 = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:12]
def sub(t, a, b, n=1, what=''):
    c = t.count(a)
    if c != n: raise SystemExit(f'{what}: expected {n} of {a[:100]!r}, found {c}')
    return t.replace(a, b)
def asset(prefix, ext):
    f = [x for x in os.listdir(os.path.join(full, 'assets')) if x.startswith(prefix) and x.endswith(ext)]
    assert len(f) == 1, (prefix, f); return 'assets/' + f[0]
OLD = {k: asset(k + '.', e) for k, e in [('site-1', '.css'), ('site-3', '.js'), ('site-6', '.js'), ('site-7', '.js'), ('data-ca-data-j', '.js'), ('sizes', '.js'), ('load', '.js')]}
NEW = {}

# ---------------------------------------------------------------- the stylesheet ----------------------------------------------------
CSS = ('.sx-i{max-width:52ch;margin-top:26px}.sx-j{margin:22px 0 0;display:flex;gap:6px;flex-wrap:wrap}'
       '.sx-j a{color:inherit;text-decoration:underline;text-underline-offset:3px}.xh .sx-q{max-width:62ch}'
       '.sx{padding-top:clamp(40px,5vw,72px)}.sx-l{color:var(--ink);border-top:1px solid var(--line);padding-top:14px;margin:0 0 20px}'
       '.sx-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}'
       '.sx-qa{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:34px clamp(28px,5vw,80px)}'
       '.sx-qa h3{margin:0 0 10px;font-size:clamp(19px,1.7vw,24px);line-height:1.25}.sx-qa p{margin:0;max-width:56ch}'
       '.sx-pr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 clamp(28px,5vw,80px)}'
       '.sx-pi{display:grid;grid-template-columns:92px minmax(0,1fr);gap:2px 14px;padding:12px 0;border-bottom:1px solid var(--line);text-decoration:none;color:inherit}'
       '.sx-pi .mono{grid-row:span 2;color:var(--concrete);font-size:12px;padding-top:3px}.sx-pi b{font-weight:600}'
       '.sx-pi span:last-child{color:var(--concrete);font-size:14px}a.sx-pi:hover b,a.sx-pi:focus-visible b{color:var(--crimson)}'
       '.sfig{padding-top:clamp(40px,5vw,80px);padding-bottom:clamp(20px,3vw,40px)}.sfig h2{margin:0 0 28px}.sfig h3{margin:48px 0 14px}'
       '.sf-n{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:34px clamp(28px,5vw,80px)}'
       '.sf-n b{display:block;font-size:clamp(54px,7vw,110px);line-height:.95;color:var(--crimson);font-stretch:70%;font-weight:750}'
       '.sf-n span{display:block;margin-top:8px;max-width:26ch}'
       '@media (max-width:760px){.sx-g,.sx-qa,.sx-pr{grid-template-columns:1fr}.sf-n{grid-template-columns:repeat(2,minmax(0,1fr))}}\n')
css = rd(OLD['site-1']); assert '.sx-g' not in css and '.sf-n' not in css
css = css.rstrip('\n') + '\n' + CSS if css.endswith('\n') else css + CSS
NEW['site-1'] = f'assets/site-1.{h12(css)}.css'; wr(NEW['site-1'], css)

# ---------------------------------------------------------------- content (site-3) ---------------------------------------------------
SECTORS = open(os.path.join(HERE, 'sectors1', 'sectors.min.js'), encoding='utf-8').read().strip()
assert SECTORS.startswith('C.sectors=[') and SECTORS.endswith('];')
FIGURES = [['2004', 'Founded in Mumbai by Lalita Tharani and Mujib Ahmed'], ['2', 'Studios, in Mumbai and Riyadh'], ['6', 'Disciplines, from urban design to objects'],
           ['60', 'Awards, honors and international shortlists'], ['30', 'Of them international'], ['150+', 'Publications featuring the work']]
HONORS = [['2026', 'The Iconic Gateway, shortlisted, UltraTech IndiaNext Innovation Awards'], ['2026', 'Project Alpha, longlisted, UltraTech IndiaNext Innovation Awards'],
          ['2022–23', 'Peace Pavilion, exhibited at the Cooper Hewitt, Smithsonian Design Museum, New York, and the Museum of Craft and Design, San Francisco'],
          ['2021', 'National Unity Pavilion, one of the three winning entries, Notions of India'], ['2019', 'The Souk, winner of the Dubai Design Week installation program'],
          ['2017', 'Finalist, Indian National War Museum, Government of India'], ['2017', 'Cascadia, with J. MAYER H., finalist for the BCDA Iconic Tower, Manila'],
          ['2016', 'Reflected Topography, winner of OFFICE NEXT, international workspace category'], ['2015', 'Reflected Topography, IES Illumination Awards, Merit Award']]
J = lambda x: json.dumps(x, ensure_ascii=False, separators=(',', ':'))
s3 = rd(OLD['site-3'])
s3 = sub(s3, '["Status","Completed",!1],["Year","2026",!0]],metrics:[["Reuse"',
         '["Status","Completed",!1],["Year","2026",!0],["Area","510 m²",!1],["Scope","Architecture and interior architecture",!1]],sector:"workplace-and-research",metrics:[["Reuse"', 1, 'barn facts')
s3 = sub(s3, 'cit:[["Writing",[{d:"2026 Jan",t:"The Collaborative Logs: Reflections 2026, are we serving right?"',
         'cit:[["Awards and shortlists",[{d:"2026",t:"UltraTech IndiaNext Innovation Awards, Longlisted",u:"",scan:"",cov:"",note:""}]],["Writing",[{d:"2026 Jan",t:"The Collaborative Logs: Reflections 2026, are we serving right?"', 1, 'alpha awards')
s3 = sub(s3, 'teaser:{src:"vid/cross50-teaser-1080.mp4",m:"vid/cross50-teaser-720.mp4",loop:10},gvid:[{src:"vid/cross50-teaser-720.mp4",full:"vid/cross50-film.mp4",poster:"vid/cross50-film.webp",',
         'teaser:{src:"vid/cross50-teaser-r2-1080.mp4",m:"vid/cross50-teaser-r2-720.mp4",loop:10},gvid:[{src:"vid/cross50-teaser-r2-720.mp4",full:"vid/cross50-film-r2.mp4",poster:"vid/cross50-film-r2.webp",', 1, 'cross50 films')
s3 = s3.rstrip('\n') + SECTORS + 'C.studioFigures=' + J(FIGURES) + ';C.studioHonors=' + J(HONORS) + ';\n'
NEW['site-3'] = f'assets/site-3.{h12(s3)}.js'; wr(NEW['site-3'], s3)

# ---------------------------------------------------------------- the data (awards register, The Iconic Gateway) ----------------------
dj = rd(OLD['data-ca-data-j'])
E = lambda o: json.dumps(J(o), ensure_ascii=False)[1:-1]     # a JSON fragment as it reads inside the loader's string
GW = {"d": "2026", "t": "UltraTech IndiaNext Innovation Awards, Shortlisted", "u": "", "scan": "", "cov": "", "note": ""}
A0 = '\\"cit\\":[[\\"Awards and shortlists\\",[{\\"d\\":\\"2023 ⚑\\",\\"t\\":\\"Competition proposal, Diyar Al Muharraq\\"'
dj = sub(dj, A0, '\\"cit\\":[[\\"Awards and shortlists\\",[' + E(GW) + ',{\\"d\\":\\"2023 ⚑\\",\\"t\\":\\"Competition proposal, Diyar Al Muharraq\\"', 1, 'gateway awards')
AW = [{"year": "2026", "org": "UltraTech IndiaNext Innovation Awards", "distinction": "Shortlisted", "project": "The Iconic Gateway", "type": "Award", "scope": "National", "s": "iconic-gateway"},
      {"year": "2026", "org": "UltraTech IndiaNext Innovation Awards", "distinction": "Longlisted", "project": "Project Alpha", "type": "Award", "scope": "National", "s": "project-alpha"}]
A1 = '\\"awards\\":[{\\"year\\":\\"2023\\",\\"org\\":\\"Museum of Craft and Design, San Francisco\\"'
dj = sub(dj, A1, '\\"awards\\":[' + ','.join(E(a) for a in AW) + ',{\\"year\\":\\"2023\\",\\"org\\":\\"Museum of Craft and Design, San Francisco\\"', 1, 'awards register')
m = re.search(r's\.text="(.*)";document', dj, re.S); D = json.loads(json.loads('"' + m.group(1) + '"'))   # still valid JSON
assert D['awards'][:2] == AW and len(D['awards']) == 47
assert next(p for p in D['projects'] if p['slug'] == 'iconic-gateway')['cit'][0][1][0] == GW
NEW['data-ca-data-j'] = f'assets/data-ca-data-j.{h12(dj)}.js'; wr(NEW['data-ca-data-j'], dj)

# ---------------------------------------------------------------- the search module (site-6) ------------------------------------------
s6 = rd(OLD['site-6'])
SXI = ',...(C.sectors||[]).map(o=>"x-"+o.k)'
s6 = sub(s6, 't[1]==="x"?C.expertise.some(a=>a.k===t[2]):', 't[1]==="x"?C.expertise.some(a=>a.k===t[2])||(C.sectors||[]).some(a=>a.k===t[2]):', 1, 'isRoute')
s6 = sub(s6, '}else if(v&&v[1]==="x"){const b=C.expertise.find(y=>y.k===v[2]);',
         '}else if(v&&v[1]==="x"&&(C.sectors||[]).some(y=>y.k===v[2])){const b=C.sectors.find(y=>y.k===v[2]),L=b.items.map(y=>I[y]).filter(Boolean);'
         'n=b.title,i=b.desc,r="CollectionPage",s=L[0]?Ge(L[0]):s,f=b.n,h.push(["Expertise","/expertise/"],[b.n,t]),'
         'p.push({"@type":"Service","@id":a+"#service",name:b.n,serviceType:b.title,description:R(b.lede,300),provider:j(E),areaServed:(C.markets||[]).filter(y=>y.code).map(y=>({"@type":"Country",name:y.n}))},'
         '{"@type":"ItemList","@id":a+"#projects",name:`${b.n}: projects`,itemListElement:L.map((y,x)=>({"@type":"ListItem",position:x+1,name:y.title,url:c(k("p-"+y.slug))}))})'
         '}else if(v&&v[1]==="x"){const b=C.expertise.find(y=>y.k===v[2]);', 1, 'meta')
s6 = sub(s6, 'const wt=()=>["home","studio","approach","expertise",...C.expertise.filter(e=>!e.hidden).map(e=>"x-"+e.k),',
         'const wt=()=>["home","studio","approach","expertise",...C.expertise.filter(e=>!e.hidden).map(e=>"x-"+e.k),...(C.sectors||[]).map(e=>"x-"+e.k),', 1, 'MDIDS')
s6 = sub(s6, '...C.expertise.filter(o=>!o.hidden).map(o=>"x-"+o.k),...Ze().map(o=>"lab-"+o)',
         '...C.expertise.filter(o=>!o.hidden).map(o=>"x-"+o.k)' + SXI + ',...Ze().map(o=>"lab-"+o)', 1, 'sitemap ids')
s6 = sub(s6, 'if(o.startsWith("x-")){const d=C.expertise.find(A=>"x-"+A.k===o)',
         '{const d=(C.sectors||[]).find(A=>"x-"+A.k===o);if(d){const w=d.items.map(A=>I[A]).filter(Boolean);return w.length?h(w):We}}if(o.startsWith("x-")){const d=C.expertise.find(A=>"x-"+A.k===o)', 1, 'sitemap lastmod')
s6 = sub(s6, '- Disciplines: ${C.expertise.filter(o=>!o.hidden).map(o=>o.n).join("; ")}\n',
         '- Disciplines: ${C.expertise.filter(o=>!o.hidden).map(o=>o.n).join("; ")}\n- Sectors: ${(C.sectors||[]).map(o=>o.n).join("; ")}\n', 1, 'llms sectors line')
s6 = sub(s6, '## Expertise\n${C.expertise.filter(o=>!o.hidden).map(o=>`- [${o.n}](${c(k("x-"+o.k))}): ${O(o.stmt||o.lede,140)}`).join(`\n`)}\n',
         '## Expertise\n${C.expertise.filter(o=>!o.hidden).map(o=>`- [${o.n}](${c(k("x-"+o.k))}): ${O(o.stmt||o.lede,140)}`).join(`\n`)}\n\n'
         '## Sectoral expertise\n${(C.sectors||[]).map(o=>`- [${o.n}](${c(k("x-"+o.k))}): ${O(o.lede,140)}`).join(`\n`)}\n', 1, 'llms sectors list')
SXMD = (r'const sxMd=e=>{const t=e.items.map(a=>I[a]).filter(Boolean);return[`# ${e.n}`,`${g(e.stmt)}. A sector of ${l.name}.`,g(e.lede),e.quote?`> ${g(e.quote[0])} (${g(e.quote[1])})`:"",'
        r'`## Projects\n\n`+t.map(a=>`- [${a.title}](${c(k("p-"+a.slug))}): ${Ae(a.sub,a.year)}`).join(`\n`),'
        r'`## Perspectives\n\n`+e.persp.map(([a,n])=>`### ${g(a)}\n\n${g(n)}`).join(`\n\n`),'
        r'`## In the press\n\n`+e.press.map(a=>`- ${a.d}: ${g(a.t)}, on ${g(a.l||(I[a.s]||{}).title||"")}${a.u?` (${a.u.startsWith("/")?c(a.u):a.u})`:""}`).join(`\n`),'
        r'`Page: ${c(k("x-"+e.k))}`].filter(Boolean).join(`\n\n`)};')
s6 = sub(s6, 'const cn=/\\bto be (supplied|added|confirmed|photographed|assembled|entered)\\b/i,', SXMD + 'const cn=/\\bto be (supplied|added|confirmed|photographed|assembled|entered)\\b/i,', 1, 'sector md')
s6 = sub(s6, '"## Expertise",a.map(n=>`- [${n.n}](${c(k("x-"+n.k))}): ${g(n.stmt)}`).join(`\n`),"## Projects",',
         '"## Expertise",a.map(n=>`- [${n.n}](${c(k("x-"+n.k))}): ${g(n.stmt)}`).join(`\n`),"## Sectoral expertise",(C.sectors||[]).map(n=>`- [${n.n}](${c(k("x-"+n.k))}): ${g(n.stmt)}`).join(`\n`),"## Projects",', 1, 'home md')
s6 = sub(s6, '"## Selected honors",C.honors.filter(n=>!/⚑/.test(n.t)).map(n=>`- ${n.y}: ${g(n.t)}`).join(`\n`),',
         '"## The practice in figures",(C.studioFigures||[]).map(([n,i])=>`- ${n}: ${i}`).join(`\n`),'
         '"## Selected honors",(C.studioHonors||C.honors.filter(n=>!/⚑/.test(n.t)).map(n=>[n.y,n.t])).map(([n,i])=>`- ${n}: ${g(i)}`).join(`\n`),', 1, 'studio md')
s6 = sub(s6, 'a.map(n=>`## [${n.n}](${c(k("x-"+n.k))})\n\n${g(n.stmt)}. ${g(R(n.lede,260))}`).join(`\n\n`)].join(`\n\n`)),a.forEach(n=>t("x-"+n.k,ln(n))),',
         'a.map(n=>`## [${n.n}](${c(k("x-"+n.k))})\n\n${g(n.stmt)}. ${g(R(n.lede,260))}`).join(`\n\n`),'
         '(C.sectors||[]).length?"# Sectoral expertise\\n\\n"+C.sectors.map(n=>`## [${n.n}](${c(k("x-"+n.k))})\n\n${g(n.stmt)}. ${g(n.lede)}`).join(`\n\n`):""].filter(Boolean).join(`\n\n`)),'
         'a.forEach(n=>t("x-"+n.k,ln(n))),(C.sectors||[]).forEach(n=>t("x-"+n.k,sxMd(n))),', 1, 'expertise md')
NEW['site-6'] = f'assets/site-6.{h12(s6)}.js'; wr(NEW['site-6'], s6)

# ---------------------------------------------------------------- the site (site-7) ---------------------------------------------------
s7 = rd(OLD['site-7'])
for n in ['sxR', 'sxC', 'sxP', 'sxJ', 'sxIx', 'sxPg']: assert not re.search(r'\b' + n + r'\b', s7), n
APP = (
 'const sxR=(x,c)=>`<a class="xi dsp${c?" "+c:""}" href="#x-${x.k}" data-img="${p(x.img)}"><span>${p(x.n)}</span>${Es(x)}</a>`,'
 'sxC=(t,x)=>{const a=String(t.sub||"").split(",")[0].trim(),s=String(t.status||"").trim();return`<a class="card" href="#p-${p(t.slug)}"><div class="im" ${ie((x.cards||{})[t.slug]||t.card,!0,`${t.title}, ${t.city||t.country}`)}></div><b>${p(t.title)}</b><span>${p(a)}${s&&!a.toLowerCase().includes(s.toLowerCase())?" · "+de(s):""}</span></a>`},'
 'sxP=r=>{const t=Re[r.s],w=r.l||(t?t.title:""),b=`<span class="mono">${p(r.d)}</span><b>${p(r.t)}</b><span>${p(w)}</span>`;'
 'if(r.u)return`<a class="sx-pi" href="${p(r.pdf?J(r.u.replace(/^\\//,"")):He(r.u))}" target="_blank" rel="noopener"${r.pdf?` type="application/pdf" data-pdf data-pdf-t="${p(r.t+", "+r.d)}"`:""}>${b}</a>`;'
 'return t?`<a class="sx-pi" href="#p-${p(t.slug)}">${b}</a>`:`<div class="sx-pi">${b}</div>`},'
 'sxJ={projects:"Projects",perspectives:"Perspectives",press:"In the press"},'
 'sxIx=()=>(C.sectors||[]).length?`<section class="xs" data-tone="light" style="padding-top:0"><p class="mono" style="margin-bottom:14px">Sectoral expertise</p>${C.sectors.map(x=>`${sxR(x)}<p class="hd xs-st">${p(x.stmt)}</p><p class="xs-d" style="max-width:62ch;color:var(--concrete)">${p(qo(x.lede,1))}</p>`).join("")}</section>`:"";'
 'function sxPg(x){const L=x.items.map(k=>Re[k]).filter(Boolean);return{html:`\n'
 '  <section class="xh" data-tone="light"><p class="mono crumb"><a href="#expertise">Expertise</a> / ${p(x.n)}</p><h1 class="dsp d-l" style="margin-top:14px">${p(x.n)}</h1><p class="hd stmt">${p(x.stmt)}</p><p class="lede sx-i">${de(x.lede)}</p>\n'
 '    <p class="mono sx-j">${(x.jump||Object.keys(sxJ)).map(j=>`<a href="#sx-${j}">${sxJ[j]}</a>`).join(\'<span aria-hidden="true">·</span>\')}</p>\n'
 '    ${x.quote?`<div class="qt sx-q"><q>${p(x.quote[0])}</q><cite class="mono">${de(x.quote[1])}</cite></div>`:""}</section>\n'
 '  <section class="wrap sx" id="sx-projects" data-tone="light"><h2 class="mono sx-l">Projects</h2><div class="sx-g">${L.map(t=>sxC(t,x)).join("")}</div></section>\n'
 '  <section class="wrap sx" id="sx-perspectives" data-tone="light"><h2 class="mono sx-l">Perspectives</h2><div class="sx-qa">${x.persp.map(([h,t])=>`<div><h3 class="hd">${p(h)}</h3><p>${de(t)}</p></div>`).join("")}</div></section>\n'
 '  <section class="wrap sx" id="sx-press" data-tone="light"><h2 class="mono sx-l">In the press</h2><div class="sx-pr">${x.press.map(sxP).join("")}</div></section>\n'
 '  <section class="wrap" data-tone="light" style="padding-top:clamp(60px,7vw,100px);padding-bottom:80px"><p class="mono" style="margin-bottom:14px">Other sectors</p>${C.sectors.filter(o=>o!==x).map(o=>sxR(o,"xo")).join("")}</section>`,title:x.n,nav:"expertise",init:()=>Ta()}}')
s7 = sub(s7, 'function rr(){return{html:`<section class="ph" data-tone="light"><h1>', APP + 'function rr(){return{html:`<section class="ph" data-tone="light"><h1>', 1, 'sector functions')
s7 = sub(s7, '(or(t))}`).join("")}</section>`,title:"Expertise",nav:"expertise",init:()=>Ta()}}', '(or(t))}`).join("")}</section>${sxIx()}`,title:"Expertise",nav:"expertise",init:()=>Ta()}}', 1, 'expertise index')
s7 = sub(s7, 'function _n(e){const t=C.expertise.find(n=>n.k===e);if(!t)return Wt();', 'function _n(e){{const x=(C.sectors||[]).find(n=>n.k===e);if(x)return sxPg(x)}const t=C.expertise.find(n=>n.k===e);if(!t)return Wt();', 1, 'expertise page')
s7 = sub(s7, 'integrated approach to the built environment.</p>\n  </section>\n  ${Yo()}',
         'integrated approach to the built environment.</p>\n    ${(C.sectors||[]).length?`<p class="mono" style="color:var(--crimson);margin:clamp(56px,6vw,88px) 0 18px">Sectoral expertise</p>${C.sectors.map(x=>sxR(x)).join("")}`:""}\n  </section>\n  ${Yo()}', 1, 'home')
s7 = sub(s7, '<div><dt>Expertise</dt><dd>${G}</dd></div>',
         '<div><dt>Expertise</dt><dd>${G}</dd></div>${(x=>x?`<div><dt>Sector</dt><dd><a href="#x-${p(x.k)}">${p(x.n)}</a></dd></div>`:"")((C.sectors||[]).find(x=>x.k===t.sector))}', 1, 'facts sector')
s7 = sub(s7, '  <section class="cols2 kf" id="facts" data-tone="light"><div><h2 class="hd">Key facts</h2></div>',
         '  ${(C.studioFigures||[]).length?`<section class="wrap sfig" id="figures" data-tone="light"><h2 class="dsp d-m">The practice in figures</h2><div class="sf-n">${C.studioFigures.map(([n,t])=>`<div><b class="dsp">${p(n)}</b><span>${p(t)}</span></div>`).join("")}</div>'
         '<h3 class="hd">Selected honors</h3><dl class="facts">${(C.studioHonors||[]).map(([y,t])=>`<div><dt>${p(y)}</dt><dd>${Dt(de(t))}</dd></div>`).join("")}</dl></section>`:""}\n'
         '  <section class="cols2 kf" id="facts" data-tone="light"><div><h2 class="hd">Key facts</h2></div>', 1, 'studio')
s7 = sub(s7, '"vid/cross50-teaser.mp4":"vid/cross50-teaser",', '"vid/cross50-teaser.mp4":"vid/cross50-teaser","vid/cross50-teaser-r2.mp4":"vid/cross50-teaser-r2",', 1, 'cross50 first frame')
s7 = sub(s7, '...C.expertise.filter(s=>s.n.toLowerCase().includes(e)).map(s=>({h:"#x-"+s.k,t:s.n,s:"Expertise",img:s.img+".webp"})),',
         '...C.expertise.filter(s=>s.n.toLowerCase().includes(e)).map(s=>({h:"#x-"+s.k,t:s.n,s:"Expertise",img:s.img+".webp"})),...(C.sectors||[]).filter(s=>s.n.toLowerCase().includes(e)).map(s=>({h:"#x-"+s.k,t:s.n,s:"Sectoral expertise",img:s.img+".webp"})),', 1, 'search')
s7 = sub(s7, 'C.expertise.filter(c=>!c.hidden).forEach(c=>{n["expertise/"+c.k]="x-"+c.k});',
         'C.expertise.filter(c=>!c.hidden).forEach(c=>{n["expertise/"+c.k]="x-"+c.k});(C.sectors||[]).forEach(c=>{n["expertise/"+c.k]="x-"+c.k});', 1, 'agent pages')
s7 = sub(s7, '...C.expertise.filter(e=>!e.hidden).map(e=>"x-"+e.k),...(C.lab&&C.lab.strands||[]).map(e=>"lab-"+e.k)',
         '...C.expertise.filter(e=>!e.hidden).map(e=>"x-"+e.k),...(C.sectors||[]).map(e=>"x-"+e.k),...(C.lab&&C.lab.strands||[]).map(e=>"lab-"+e.k)', 1, 'crawl ids')
s7 = sub(s7, '...C.expertise.filter(l=>!l.hidden).map(l=>"x-"+l.k)].map(l=>{const c=O.meta(l)',
         '...C.expertise.filter(l=>!l.hidden).map(l=>"x-"+l.k),...(C.sectors||[]).map(l=>"x-"+l.k)].map(l=>{const c=O.meta(l)', 1, 'seo tab ids')
NEW['site-7'] = f'assets/site-7.{h12(s7)}.js'; wr(NEW['site-7'], s7)

# ---------------------------------------------------------------- media -----------------------------------------------------------------
im = Image.open(mc_master); icc = im.info.get('icc_profile')
if icc:
    src_p = ImageCms.ImageCmsProfile(io.BytesIO(icc))
    if 'srgb' not in ImageCms.getProfileDescription(src_p).lower().replace(' ', ''):
        im = ImageCms.profileToProfile(im, src_p, ImageCms.createProfile('sRGB'), outputMode='RGB')
im = im.convert('RGB'); assert im.size == (3840, 2160), im.size
def save(w, q, p):
    x = im.resize((w, w * 9 // 16), Image.LANCZOS)
    if w < 3840: x = x.filter(ImageFilter.UnsharpMask(radius=0.8, percent=40, threshold=2))
    q_ = os.path.join(full, p); os.makedirs(os.path.dirname(q_), exist_ok=True); x.save(q_, 'WEBP', quality=q, method=6)   # no EXIF, XMP or ICC written
for w, q, p in [(2880, 82, 'img/uae/p06.webp'), (1280, 82, 'img/uae/p06-1280.webp'), (800, 80, 'img/uae/p06-800.webp')]: save(w, q, p)
sz = rd(OLD['sizes']); assert '"img/uae/p06.webp"' not in sz
sz = sub(sz, '"img/uae/p05.webp":[2880,1620,[800,1280],{}],', '"img/uae/p05.webp":[2880,1620,[800,1280],{}],"img/uae/p06.webp":[2880,1620,[800,1280],{}],', 1, 'sizes')
NEW['sizes'] = f'assets/sizes.{h12(sz)}.js'; wr(NEW['sizes'], sz)
FILMS = ['cross50-film-r2.mp4', 'cross50-film-r2.webp', 'cross50-teaser-r2-1080.mp4', 'cross50-teaser-r2-720.mp4', 'cross50-teaser-r2.webp']
for f in FILMS:
    os.makedirs(os.path.join(full, 'vid'), exist_ok=True); shutil.copyfile(os.path.join(vid_dir, f), os.path.join(full, 'vid', f))

# ---------------------------------------------------------------- the loader --------------------------------------------------------------
load = rd(OLD['load'])
for k in ['site-3', 'site-6', 'site-7', 'data-ca-data-j', 'sizes']: load = sub(load, '"/' + OLD[k] + '"', '"/' + NEW[k] + '"', 1, 'load ' + k)
NEW['load'] = f'assets/load.{h12(load)}.js'; wr(NEW['load'], load)
for k in OLD: os.remove(os.path.join(full, OLD[k]))

# every page: the new loader and stylesheet (the pages that change otherwise are rendered in stage 2)
n = 0
for d, _, fs in os.walk(full):
    for f in fs:
        if not f.endswith('.html'): continue
        p = os.path.relpath(os.path.join(d, f), full).replace(os.sep, '/'); t = rd(p); t0 = t
        if '/' + OLD['load'] in t: t = sub(t, '/' + OLD['load'], '/' + NEW['load'], 1, p)
        if '/' + OLD['site-1'] in t: t = sub(t, '/' + OLD['site-1'], '/' + NEW['site-1'], 1, p)
        if t != t0: wr(p, t); n += 1
json.dump({'old': OLD, 'new': NEW, 'films': FILMS, 'pictures': ['img/uae/p06.webp', 'img/uae/p06-1280.webp', 'img/uae/p06-800.webp'], 'pages_swapped': n},
          open(os.path.join(out, 'stage1.json'), 'w'), indent=1)
print('stage 1:', n, 'pages point at the new loader and stylesheet'); [print('  ', OLD[k], '->', NEW[k]) for k in OLD]
