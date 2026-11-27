"""The six sector pages under Expertise, as approved in Mujib's marked review (25-26 November 2026).
Writes the data both ways: readable JS for src/ca-website.html, and one minified statement for the live site-3 bundle."""
import re, json, html
LF = open('/home/claude/seo4/out/upload/llms-full.txt', encoding='utf-8').read()
SITE = 'https://collaborativearchitecture.com'
MON = {m: i for i, m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}
TITLE = {}
for line in [x for x in re.split(r'\n---\n', LF) if '<!-- https://collaborativearchitecture.com/work/ -->' in x][0].split('\n'):
    m = re.match(r'- \[(.+?)\]\(https://collaborativearchitecture\.com/work/([a-z0-9-]+)/\): (.*)$', line)
    if m: TITLE[m.group(2)] = m.group(1)
PRESS = {}
for sec in re.split(r'\n---\n', LF):
    m = re.search(r'<!-- https://collaborativearchitecture.com/work/([a-z0-9-]+)/ -->', sec)
    if not m: continue
    items = []
    for h in ('## In print', '## Online'):
        i = sec.find(h)
        if i < 0: continue
        for l in sec[i + len(h):].split('\n## ')[0].strip().split('\n'):
            mm = re.match(r'- (\d{4})(?: ([A-Za-z–\-]+))?: (.+?)(?: \((?:the feature on the project, PDF: )?(https?://[^)\s]+)\))?$', l.strip())
            if mm: items.append((mm.group(1), mm.group(2) or '', mm.group(3), mm.group(4) or ''))
    PRESS[m.group(1)] = items

def item(y, mo, src, u, slug, label=None):
    pdf = u.startswith(SITE + '/press/')
    return {'d': (y + ' ' + mo).strip(), 't': src.split(',')[0], 's': slug, **({'l': label} if label else {}),
            'u': u[len(SITE):] if pdf else u, **({'pdf': 1} if pdf else {})}
def pi(slug, sub, year=None, label=None):
    for y, mo, src, u in PRESS.get(slug, []):
        if sub.lower() in src.lower() and (year is None or y == year): return item(y, mo, src, u, slug, label)
    raise SystemExit(f'press item not found: {slug} {sub} {year}')
def pkey(r): return (r['d'][:4], MON.get((r['d'][5:8] or 'Jan'), 0))
def auto(slugs, must=(), n=10, per=4):
    rows = [(y, mo, src, u, s) for s in slugs for y, mo, src, u in PRESS.get(s, [])]
    out, seen, cnt = [], set(), {}
    def take(r):
        k = (r[2].split(',')[0], r[4])
        if k in seen: return
        seen.add(k); cnt[r[4]] = cnt.get(r[4], 0) + 1; out.append(item(*r))
    for slug, sub in must:
        for r in rows:
            if r[4] == slug and sub.lower() in r[2].lower(): take(r)
    for r in sorted(rows, key=lambda r: (r[0], MON.get((r[1] or 'Jan')[:3], 0)), reverse=True):
        if len(out) >= n: break
        if cnt.get(r[4], 0) >= per: continue
        take(r)
    return out
srt = lambda L: sorted(L, key=pkey, reverse=True)

S = []
S.append({'k': 'workplace-and-research', 'n': 'Workplace and Research', 'stmt': 'Workplaces that carry an organization’s culture', 'img': 'img/bgrt/p01',
  'lede': 'We design workplaces, research campuses and experience centers that carry an organization’s culture and keep their value at a time of unprecedented and hard-to-predict shifts in all these sectors.',
  'title': 'Workplace and research campus design', 'desc': 'Workplaces, research campuses and experience centers by Collaborative Architecture: The Barn, Reflected Topography, BGRT Mumbai and MillerKnoll.',
  'quote': ['There are levels at which design reaches spaces of ecstasy and yet allows human life to wind around it.', 'Domus, December 2015, on Reflected Topography'],
  'items': ['the-barn', 'reflected-topography', 'bgrt-mumbai', 'miller-knoll-experience-center', 'wedge-1'],
  'persp': [['An industrial shed can become a contemporary workplace.', 'The Barn in Navi Mumbai keeps parts of its workshop, paint shop and mechanical repair functions, and builds on the shed’s industrial character instead of erasing it. A modest budget made reuse the better design.'],
            ['The brief starts with how an organization works.', 'Before design begins, organizational mapping, participatory workshops and spatial audits show how teams collaborate and where a space fails them. The evidence shapes the brief.'],
            ['Performance is non-negotiable.', 'BGRT Mumbai targets LEED Platinum with a climate-responsive façade, Reflected Topography sits in a LEED Platinum campus, and the MillerKnoll Experience Center is India’s first Net Zero retail space.'],
            ['A lobby can be a public room.', 'Reflected Topography turns a 32 × 32-meter hall in Bengaluru into reception, waiting, meeting and circulation spaces under one waffle slab. It won OFFICE NEXT in 2016 and an IES Illumination Award of Merit in 2015.']],
  'press': srt([pi('reflected-topography', 'BluPrint'), pi('reflected-topography', 'Architecture + Design'), pi('reflected-topography', 'Domus'), pi('reflected-topography', 'Mondo*Arc International'),
                pi('reflected-topography', 'Mondo*Arc India'), pi('reflected-topography', 'LD+A'), pi('reflected-topography', 'Hinge'), pi('wedge-1', 'IA&B'), pi('wedge-1', 'ArchDaily')])})
S.append({'k': 'residential', 'n': 'Residential', 'stmt': 'Homes shaped around the people who live in them', 'img': 'img/cantilevers/p01',
  'lede': 'We conceive and create distinctive residences across India and the Middle East, shaped by the people who inhabit those spaces. These are often borne out of detailed spatial mapping strategies, to make each home personal, relatable and co-authored.',
  'title': 'Luxury residential architecture and interiors', 'desc': 'Distinctive residences across India and the Middle East by Collaborative Architecture: House of Cantilevers, Apartment by the Bay and Bearys Wafira.',
  'items': ['house-of-cantilevers', 'apartment-by-the-bay', 'parallel-house', 'the-legend', '50th-cross-road', 'bearys-wafira'], 'jump': ['projects', 'press'],
  'persp': [['A house can accommodate the familiar and the evolving.', 'The House of Cantilevers in Kerala preserves the rituals of the family while embracing the rhythms of contemporary life.'],
            ['The building and its interiors are designed as one.', 'We conceive interiors as an extension of the architecture: materiality, light, acoustics and detail converge to create a seamless spatial experience.'],
            ['Homes are designed for a long life.', 'Through spatial mapping and predictive planning, we anticipate changing needs and patterns of occupancy, shaping adaptable spaces that sustain relevance, functionality and design longevity across generations.'],
            ['Our clients are co-authors in the design journey.', 'Each home starts with how its owners live and what they value; Apartment by the Bay, a 180-square-meter home at Cuffe Parade, was shaped around its young teenage occupants’ outgoing lives.']],
  'press': srt([pi('apartment-by-the-bay', 'Indian Furniture Journal'), pi('the-legend', 'Livingetc'), pi('the-legend', 'Interiors & Décor'), pi('the-legend', 'Society Interiors'),
                pi('house-of-cantilevers', 'Society Interiors'), pi('house-of-cantilevers', 'Inside Outside'), pi('house-of-cantilevers', 'Trends')])})
S.append({'k': 'civic-and-cultural', 'n': 'Civic and Cultural', 'stmt': 'Architecture for public life', 'img': 'img/peace/p01',
  'lede': 'We design pavilions, memorials, museums, places of worship and civic landmarks for governments, public authorities and cultural institutions.',
  'title': 'Civic and cultural architecture', 'desc': 'Pavilions, memorials, museums and civic landmarks by Collaborative Architecture, from the Peace Pavilion and National Unity Pavilion to The Iconic Gateway.',
  'quote': ['Mumbai-based architects challenged a national war museum competition with a design proposal for a “Peace Museum”, aiming to shape a new narrative and alter India’s discourse on war and nationalism.',
            'Curatorial note, Designing Peace, Cooper Hewitt, Smithsonian Design Museum'],
  'items': ['peace-pavilion', 'national-unity-pavilion', 'iconic-gateway', 'tree-of-life', 'urnes-stave-heritage-center', 'sandy-hook-memorial', 'iconic-mosque', 'the-souk', 'the-measured-city'],
  'cards': {'the-measured-city': 'img/uae/p06', 'sandy-hook-memorial': 'img/sandyhook/p01r2'},
  'persp': [['A war museum can put peace at the center.', 'Our finalist entry for the Indian National War Museum proposed the Peace Pavilion, one of seven practices in the final stage from 268 entries. It was later shown at the Cooper Hewitt, Smithsonian Design Museum, New York, and the Museum of Craft and Design, San Francisco.'],
            ['Architecture can reinforce pluralistic ideas.', 'The National Unity Pavilion, one of the three winning entries from 575 submissions to Notions of India, asks how a building can hold many histories, cultures, beliefs and languages.'],
            ['Civic infrastructure can be a national landmark.', 'The Iconic Gateway for Diyar Al Muharraq, Bahrain, is a cable-suspended footbridge with a 165-meter clear span between two 65-meter pylons, drawn from Bahrain’s vernacular and maritime heritage.'],
            ['International work is shaped with international partners.', 'Partners on recent work include Arup, BDP, Buro Happold, Henning Larsen, J. MAYER H. and Web Structures (Ramboll).']],
  'press': srt([pi('the-measured-city', 'Indian Furniture Journal'), pi('iconic-gateway', 'Insite'), pi('national-unity-pavilion', 'Insite'), pi('national-unity-pavilion', 'Notions of India'),
                pi('peace-pavilion', 'BluPrint'), pi('peace-pavilion', 'e-architect', '2020'),
                {'d': '2022 Jun', 't': 'Cooper Hewitt, Smithsonian Design Museum', 's': 'peace-pavilion', 'l': 'Peace Pavilion · Designing Peace, exhibition', 'u': 'https://exhibitions.cooperhewitt.org/designing-peace/peace-pavilion/'},
                pi('peace-pavilion', 'ArchitectureLive', label='Indian National War (Peace) Museum')])})
S.append({'k': 'hospitality', 'n': 'Hospitality', 'stmt': 'Places to dine, gather and stay', 'img': 'img/mezban/p01',
  'lede': 'We design restaurants, clubs and guest facilities in which light, material and cultural reference shape the experience of dining, gathering and staying.',
  'title': 'Hospitality architecture and restaurant design', 'desc': 'Restaurants, clubs and guest facilities by Collaborative Architecture: Mezban (Inverted Topography) in Kozhikode, Spicy Route in Doha and The Vessel in Kerala.',
  'items': ['inverted-topography', 'spicy-route', 'the-vessel'],
  'persp': [['Design can change how a business performs.', 'After Mezban’s relaunch, Hotel Asma Tower was rated the No. 1 hotel in Kozhikode, and the restaurant was a finalist for the Restaurant & Bar Design Awards and the SBID Awards in 2012.'],
            ['Light as the principal material.', 'An undulating canopy of custom luminaires turns Mezban’s ceiling into an inverted topography of light. At Spicy Route in Doha, custom copper light fittings fill the ceiling.'],
            ['Culture can be read without kitsch.', 'Spicy Route reinterprets the Indian restaurant through a sophisticated interpretation of materiality, in place of decorative clichés.'],
            ['Adaptive reuse as a path toward a sustainable future.', 'The Vessel turns a single-story house on a Kerala river into guest facilities for the Jellyfish Water Sports Club: dining and lounges below, guest rooms above, and a pool along its perimeter.']],
  'press': srt(auto(['inverted-topography', 'spicy-route', 'the-vessel'], must=[('inverted-topography', 'ArchDaily'), ('inverted-topography', 'ArchitectureLive'), ('spicy-route', 'GID')], n=10, per=8))})
S.append({'k': 'educational', 'n': 'Educational', 'stmt': 'Learning environments that invite discovery', 'img': 'img/jdt/p01',
  'lede': 'We design schools and learning centers that start from how children perceive space, with daylight, color and informal places to meet.',
  'title': 'School and educational architecture', 'desc': 'Schools and learning centers by Collaborative Architecture: Stacked Tectonics, a primary school in Kozhikode, and Wrap-3, a computer learning center.',
  'quote': ['…breaks away from conventional bias toward symmetrical planning.', 'Domus, June 2013, on Stacked Tectonics'],
  'items': ['stacked-tectonics', 'wrap-3'],
  'persp': [['A school can start from a child’s point of view.', 'Wrap-3, a computer learning center for an orphanage in Kozhikode, takes the child’s perception as its point of departure: layered wraps of color, doodle-like cut-outs and daylight make an informal room for discovery.'],
            ['Every classroom can have its own identity.', 'At Stacked Tectonics each classroom has a large window with its own shape and color, bringing daylight in for much of the school day and helping children find their way.'],
            ['A corridor can be a place to meet.', 'A single-loaded corridor organizes the school, and its widened stretches become informal meeting places between classes.'],
            ['One project leads to the next.', 'The ideas of Wrap-3, completed in 2006, informed Stacked Tectonics, a 2,100-square-meter primary school on the same JDT Islam campus, completed in 2012.']],
  'press': srt(auto(['stacked-tectonics', 'wrap-3'], must=[('stacked-tectonics', 'Domus')], n=10, per=6))})
S.append({'k': 'real-estate-and-developers', 'n': 'Real Estate and Developers', 'stmt': 'Design that strengthens a development’s brand', 'img': 'img/legend/p01',
  'lede': 'We design show apartments, experience centers, lobbies, residences and campuses for design-discerning clients and developers.',
  'title': 'Design for real estate developers', 'desc': 'Show apartments, lobbies, residences and campuses for developers, by Collaborative Architecture: Bearys Wafira, The Legend, 50th Cross Road and BGRT.',
  'items': ['bearys-wafira', 'the-legend', '50th-cross-road', 'bgrt-mumbai', 'reflected-topography', 'miller-knoll-experience-center'],
  'persp': [['Good design can strengthen brand value.', 'The Legend, a 353-square-meter show condominium for Skyline Builders in Kochi, developed the layout, materials, furniture and kitchen as one proposition for an enhanced brand value.'],
            ['A show apartment sets the standard for a whole development.', 'At 50th Cross Road in Kozhikode our scope went beyond the apartment to the material palette, tonal direction and specification framework of the project, supporting PVS Developers’ move into luxury condominiums.'],
            ['The interiors carry the address.', 'At Bearys Wafira, Dubai Healthcare City, Dubai, we design the grand lobby, club floors, four condominiums and the penthouse for Bearys Global, as one of the best uber-luxury projects due in 2029.'],
            ['A campus is planned for the tenants it must attract.', 'For the Bearys Group we designed the public lobby of its Bengaluru research campus and BGRT Mumbai, a campus of about 40,000 square meters targeting companies that have pledged a substantial commitment to sustainability and are serious about meeting those targets.']],
  'press': srt([pi('50th-cross-road', 'MGS Architecture'), pi('reflected-topography', 'BluPrint'), pi('reflected-topography', 'Architecture + Design'), pi('reflected-topography', 'Indian Furniture Journal', '2019'),
                pi('the-legend', 'Livingetc'), pi('the-legend', 'Interiors & Décor'), pi('the-legend', 'Society Interiors')])})

for s in S:
    assert len(s['title']) <= 60 and 70 <= len(s['desc']) <= 160, (s['k'], len(s['title']), len(s['desc']))
    for k in s['items']: assert k in TITLE, k
    s.setdefault('jump', ['projects', 'perspectives', 'press']); s.setdefault('quote', None); s.setdefault('cards', {})

def minified():
    return 'C.sectors=' + json.dumps(S, ensure_ascii=False, separators=(',', ':')) + ';'

def readable():
    def v(x): return json.dumps(x, ensure_ascii=False)
    L = ['/* 26 November 2026 (Mujib, marked review of 25 November): "These pages come after the Expertise as sectoral expertise, hyperlinked to the',
         '   titles." Six sector pages at /expertise/<k>/, listed below the disciplines on the Expertise page and on Home. Each has its introduction, a',
         '   quote where there is one, every project in the sector (cards: a picture of its own where one was chosen), four perspectives, the press on',
         '   those projects as he marked it, and the other sectors. jump: the links under the introduction (Residential: Projects and In the press). */',
         'C.sectors = [']
    for s in S:
        L.append('  {')
        for key in ['k', 'n', 'stmt', 'img', 'title', 'desc', 'lede', 'quote', 'items', 'cards', 'jump']:
            L.append(f'    {key}: {v(s[key])},')
        L.append('    persp: [')
        for h, t in s['persp']: L.append(f'      [{v(h)}, {v(t)}],')
        L.append('    ],')
        L.append('    press: [')
        for r in s['press']: L.append(f'      {v(r)},')
        L.append('    ] },')
    L.append('];')
    return '\n'.join(L)

if __name__ == '__main__':
    open('/home/claude/p5/sectors.min.js', 'w', encoding='utf-8').write(minified())
    open('/home/claude/p5/sectors.src.js', 'w', encoding='utf-8').write(readable())
    for s in S: print(s['k'], len(s['items']), 'projects,', len(s['press']), 'press;', s['title'], len(s['title']), '|', len(s['desc']))
    for s in S[3:5]:
        for r in s['press']: print('  ', s['k'], r)
