#!/usr/bin/env python3
"""Design Snippet: one HTML page at /design-snippet/ that is also, printed, the 12-page A4 pamphlet (the downloadable PDF).
The opening pages are the same for everyone; only the exercises are in three levels (Interns, Junior Architects, Advanced).
Usage: build_tiers.py <out.html>"""
import sys, math

CAREERS = 'studio@collaborativearchitecture.com'
SITE = 'https://collaborativearchitecture.com/'
PDF = '/design-snippet/Collaborative-Architecture-Design-Snippet.pdf'

# ============================== drawings (all generated, in millimetres) ==============================
def rods_svg(rows, plates=0):
    s, y, out = .2, 30, []
    for n, L in rows:
        out.append(f'<text class="k-n" x="0" y="{y+7}">{n}&#215;</text><rect class="k-rod" x="44" y="{y-5}" width="{L*s}" height="{50*s}" rx="{25*s}"/>'
                   f'<text class="k-l" x="{44+L*s+10}" y="{y+5}">&#216;50 &#183; {L}</text>')
        y += 34
    if plates:
        py = y + 6
        out.append(f'<text class="k-n" x="0" y="{py+64}">{plates}&#215;</text>')
        for i in range(3): out.append(f'<rect class="k-pl" x="{44+i*14}" y="{py+i*6}" width="{600*s}" height="{600*s}"/>')
        out.append(f'<text class="k-l" x="{44+600*s+40}" y="{py+50}">600 &#215; 600</text><text class="k-l" x="{44+600*s+40}" y="{py+66}">12 thick</text>')
        y = py + 600 * s + 24
    else: y += 4
    out.append(f'<line class="k-sc" x1="44" y1="{y}" x2="{44+1000*s}" y2="{y}"/><line class="k-sc" x1="44" y1="{y-4}" x2="44" y2="{y+4}"/>'
               f'<line class="k-sc" x1="{44+1000*s}" y1="{y-4}" x2="{44+1000*s}" y2="{y+4}"/><text class="k-l" x="{44+500*s}" y="{y+16}" text-anchor="middle">1000 mm</text>')
    desc = ', '.join(f'{n} rods {L} mm long' for n, L in rows) + ', all 50 mm in diameter' + (f', and {plates} plates of 600 by 600 mm' if plates else '')
    return f'<svg class="dg kit" viewBox="0 0 360 {y+22}" role="img" aria-label="The kit drawn to scale: {desc}.">{"".join(out)}</svg>'

def stand_svg(rows, plates=0):
    """the whole kit laid out: every rod standing side by side, longest in the middle; lengths to scale, thickness not"""
    s, p = .1, 2.1
    half = []
    for n, L in sorted(rows, key=lambda r: r[1]): half += [L] * (n // 2)
    order = half + half[::-1]
    base = 1000 * s
    rods = ''.join(f'<line x1="{i*p+1:.2f}" y1="{base:.2f}" x2="{i*p+1:.2f}" y2="{base-L*s:.2f}"/>' for i, L in enumerate(order))
    rw = len(order) * p
    x0, side, off = rw + 10, 600 * s, 1.6
    pl = ''.join(f'<rect x="{x0+k*off:.2f}" y="{base-side-(plates-1-k)*off:.2f}" width="{side:.2f}" height="{side:.2f}"/>' for k in range(plates)) if plates else ''
    lx = (x0 + side + plates * off + 8) if plates else rw + 10
    lines = [f'{n} &#215; {L}' for n, L in rows] + ([f'{plates} &#215; 600 &#215; 600'] if plates else [])
    leg = ''.join(f'<text x="{lx:.1f}" y="{base - (len(lines)-1-i)*9 - 2:.1f}">{l}</text>' for i, l in enumerate(lines))
    leg += f'<text class="mu" x="{lx:.1f}" y="{base - len(lines)*9 - 4:.1f}">mm, rods &#216; 50</text>'
    W = lx + 62
    sb = (f'<g class="dm"><line x1="0" y1="{base+7}" x2="{1000*s:.1f}" y2="{base+7}"/><line x1="0" y1="{base+4.5}" x2="0" y2="{base+9.5}"/>'
          f'<line x1="{1000*s:.1f}" y1="{base+4.5}" x2="{1000*s:.1f}" y2="{base+9.5}"/><text x="{1000*s:.1f}" y="{base+17}" text-anchor="end">1000 mm</text></g>')
    desc = ', '.join(f'{n} rods {L} mm long' for n, L in rows) + ', all 50 mm in diameter' + (f', and {plates} plates of 600 by 600 mm' if plates else '')
    return (f'<svg class="dg kit stand" viewBox="-2 -4 {W:.0f} {base+22:.0f}" role="img" aria-label="The whole kit laid out, every rod standing side by side: {desc}.">'
            f'<g class="sr">{rods}</g><g class="sp">{pl}</g><line class="sb" x1="-1" y1="{base:.1f}" x2="{(x0+side+plates*off+2) if plates else rw+2:.1f}" y2="{base:.1f}"/><g class="sl">{leg}</g>{sb}</svg>')

def screen_svg():
    """01-B: one 1220 x 2440 sheet perforated around one point; holes 20-120 mm, 25 mm between, 60 mm to the edge"""
    W, H, s, p = 1220, 2440, .125, 145
    ax, ay = 430, 1580
    holes, area = [], 0
    j = 0; y = 120
    while y <= H - 120:
        x = 120 + (p / 2 if j % 2 else 0)
        while x <= W - 120:
            d = 20 + 100 * max(0, 1 - math.hypot(x - ax, y - ay) / 1250) ** 1.5
            holes.append((x, y, d)); area += math.pi * d * d / 4; x += p
        y += p * .866; j += 1
    opn = area / (W * H) * 100
    c = ''.join(f'<circle cx="{x*s:.2f}" cy="{(H-y)*s:.2f}" r="{d*s/2:.2f}"/>' for x, y, d in holes)
    Ws, Hs = W * s, H * s
    dm = (f'<g class="dm"><line x1="0" y1="{Hs+8}" x2="{Ws}" y2="{Hs+8}"/><text x="{Ws/2}" y="{Hs+20}" text-anchor="middle">1220</text>'
          f'<line x1="{Ws+8}" y1="0" x2="{Ws+8}" y2="{Hs}"/><text x="{Ws+12}" y="{Hs/2}">2440</text></g>')
    note = (f'<g class="nt"><text x="{Ws+22}" y="{(H-ay)*s-4:.1f}">the point</text><line x1="{Ws+20}" y1="{(H-ay)*s-8:.1f}" x2="{ax*s+5:.1f}" y2="{(H-ay)*s:.1f}"/>'
            f'<text x="{Ws+22}" y="{Hs-40}">{len(holes)} holes</text><text x="{Ws+22}" y="{Hs-26}">{opn:.0f}% open</text>'
            f'<text x="{Ws+22}" y="{Hs-12}">one way of many</text></g>')
    return (f'<svg class="dg screen" viewBox="-2 -2 {Ws+122} {Hs+26}" role="img" aria-label="A plywood sheet 1220 by 2440 mm perforated with {len(holes)} round holes, '
            f'largest around one point and shrinking away from it; {opn:.0f}% of the sheet is open.">'
            f'<rect class="sh" x="0" y="0" width="{Ws}" height="{Hs}"/><g class="ho">{c}</g><circle class="pt" cx="{ax*s}" cy="{(H-ay)*s}" r="4"/>{dm}{note}</svg>')

def field_svg():
    W, H, n, m = 6000, 3000, 30, 15
    c = W / n; s = .1
    px, py = 1900, 1500
    curve = lambda x: 2300 - 900 * math.sin((x / W) * math.pi * 1.25 + .4)
    pts = ' '.join(f'{x*s:.1f},{(H-curve(x))*s:.1f}' for x in range(0, W + 1, 100))
    cells = []
    for i in range(n):
        for j in range(m):
            cx, cy = (i + .5) * c, (j + .5) * c
            o = max(math.exp(-(math.hypot(cx - px, cy - py) / 1250) ** 2) * .74, math.exp(-(abs(cy - curve(cx)) / 260) ** 2) * .42)
            o = 0 if o < .05 else o
            cells.append(f'<rect class="f-t" x="{i*c*s+.6:.1f}" y="{(H-(j+1)*c)*s+.6:.1f}" width="{c*s-1.2:.1f}" height="{c*s-1.2:.1f}"/>')
            if o: cells.append(f'<circle class="f-o" cx="{cx*s:.1f}" cy="{(H-cy)*s:.1f}" r="{math.sqrt(o*c*c/math.pi)*s:.2f}"/>')
    dims = (f'<line class="f-d" x1="0" y1="{H*s+14}" x2="{W*s}" y2="{H*s+14}"/><text class="f-l" x="{W*s/2}" y="{H*s+28}" text-anchor="middle">6000</text>'
            f'<line class="f-d" x1="{W*s+14}" y1="0" x2="{W*s+14}" y2="{H*s}"/><text class="f-l" x="{W*s+20}" y="{H*s/2+4}">3000</text>')
    return (f'<svg class="dg field" viewBox="-2 -2 {W*s+64} {H*s+36}" role="img" aria-label="A wall 6000 by 3000 mm of 450 square pieces: '
            f'closed where nothing acts on it, opening up to about 70% near a person walking past and along a curve.">'
            f'{"".join(cells)}<polyline class="f-c" points="{pts}"/><circle class="f-p" cx="{px*s}" cy="{(H-py)*s}" r="6"/>{dims}</svg>')

def canopy_svg():
    """03-A: a waffle canopy 8 x 8 m on three supports (plan), and one of its cutting sheets, nested and labeled"""
    # plan
    ps, P = .022, 8000
    plan = [f'<rect class="cp-o" x="0" y="0" width="{P*ps}" height="{P*ps}"/>']
    for k in range(1, 8):
        plan.append(f'<line class="cp-r" x1="{k*1000*ps}" y1="0" x2="{k*1000*ps}" y2="{P*ps}"/><line class="cp-r" x1="0" y1="{k*1000*ps}" x2="{P*ps}" y2="{k*1000*ps}"/>')
    plan.append(f'<line class="cp-k" x1="0" y1="{3000*ps}" x2="{P*ps}" y2="{3000*ps}"/>')
    for x, y in [(1600, 1700), (6400, 2300), (3800, 6600)]: plan.append(f'<circle class="cp-s" cx="{x*ps}" cy="{y*ps}" r="4.2"/>')
    pw = P * ps
    plan.append(f'<text class="cp-t" x="0" y="{pw+12}">Plan, 8 &#215; 8 m &#183; 3 supports</text><text class="cp-t k" x="{pw+4}" y="{3000*ps+3}">R03</text>')
    # one sheet, nested: rib segments between two curves, with half-depth slots
    SW, SH, ss, gap = 2440, 1220, .142, 6
    ox = pw + 34
    parts, used = [], 0
    rows = [(0, ['R03-1', 'R03-2', 'R03-3']), (1, ['R04-1', 'R04-2']), (2, ['C02-3', 'C02-4', 'C05-1']), (3, ['C05-2', 'C06-1'])]
    lens = {'R03-1': 860, 'R03-2': 760, 'R03-3': 780, 'R04-1': 1240, 'R04-2': 1150, 'C02-3': 700, 'C02-4': 880, 'C05-1': 820, 'C05-2': 1300, 'C06-1': 1090}
    y0 = gap
    for r, ids in rows:
        x0, depth, amp = gap, 196, 36
        for n, pid in enumerate(ids):
            L = lens[pid]; ph = r * 1.7 + n * 2.3
            bot = [(x0 + t, y0 + amp + amp * math.sin(t / L * math.pi * 1.1 + ph) * .8) for t in range(0, L + 1, 20)]
            top = [(x, y + depth) for x, y in bot]
            poly = bot + top[::-1]
            a = 0
            for i in range(len(poly)):
                x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]; a += x1 * y2 - x2 * y1
            used += abs(a) / 2
            path = 'M' + ' L'.join(f'{(ox + x*ss):.1f},{(SH - y)*ss:.1f}' for x, y in poly) + 'Z'
            slots = ''
            for k in range(1, int(L // 330) + 1):
                sx = x0 + k * L / (int(L // 330) + 1)
                sy = bot[min(len(bot) - 1, int((sx - x0) / 20))][1]
                up = k % 2
                yb = sy + (depth / 2 if up else 0)
                slots += f'<rect class="ns-s" x="{(ox+(sx-9)*ss):.1f}" y="{(SH-(yb+depth/2))*ss:.1f}" width="{18*ss:.1f}" height="{depth/2*ss:.1f}"/>'
            cx, cy = x0 + L / 2, bot[len(bot) // 2][1] + depth / 2
            parts.append(f'<path class="ns-p" d="{path}"/>{slots}<text class="ns-t" x="{(ox+cx*ss):.1f}" y="{(SH-cy)*ss+2.6:.1f}" text-anchor="middle">{pid}</text>'
                         f'<circle class="ns-d" cx="{(ox+(x0+40)*ss):.1f}" cy="{(SH-(bot[2][1]+depth/2))*ss:.1f}" r="1.1"/>')
            x0 += L + gap + 30
        y0 += depth + 2 * amp + gap + 10
    yld = used / (SW * SH) * 100
    sw, sh = SW * ss, SH * ss
    sheet = (f'<rect class="ns-b" x="{ox}" y="0" width="{sw:.1f}" height="{sh:.1f}"/>{"".join(parts)}'
             f'<g class="dm"><line x1="{ox}" y1="{sh+8:.1f}" x2="{ox+sw:.1f}" y2="{sh+8:.1f}"/><text x="{ox+sw/2:.1f}" y="{sh+20:.1f}" text-anchor="middle">2440</text>'
             f'<line x1="{ox+sw+8:.1f}" y1="0" x2="{ox+sw+8:.1f}" y2="{sh:.1f}"/><text x="{ox+sw+12:.1f}" y="{sh/2:.1f}">1220</text></g>'
             f'<text class="cp-t" x="{ox}" y="{sh+34:.1f}">Sheet 07 &#183; 10 parts &#183; IDs engraved &#183; one way of many</text>')
    W = ox + sw + 44
    return (f'<svg class="dg canopy" viewBox="-2 -6 {W:.0f} {max(pw, sh)+44:.0f}" role="img" aria-label="On the left, the plan of a canopy 8 by 8 metres: a grid of plywood ribs '
            f'one metre apart on three supports. On the right, one of its cutting sheets, 2440 by 1220 mm, with ten curved rib parts nested on it, each with slots, a drill mark and its ID, such as R03-1.">'
            f'{"".join(plan)}{sheet}</svg>')

def facade_svg():
    """03-B: a west facade 30 x 12 m of 600 panels (50 bays x 12 floors), each opening set by the sun, rationalized to 12 types"""
    nb, nf, PW, PH, s = 50, 12, 600, 1000, .0118
    val = lambda b, f: min(1, max(0, .5 + .34 * math.sin(b / nb * math.pi * 1.35 + f / nf * 1.1) + .22 * (f / (nf - 1) - .5)))
    cells, count = [], [0] * 12
    for f in range(nf):
        for b in range(nb):
            t = round(val(b, f) * 11); count[t] += 1
            x, y = b * PW * s, (nf - 1 - f) * PH * s
            w = (1 - t / 11) * .78 * PW * s + .5
            cells.append(f'<rect class="fa-p" x="{x+.35:.2f}" y="{y+.35:.2f}" width="{PW*s-.7:.2f}" height="{PH*s-.7:.2f}"/>'
                         f'<rect class="fa-o" x="{x+(PW*s-w)/2:.2f}" y="{y+1.1:.2f}" width="{w:.2f}" height="{PH*s-2.2:.2f}"/>')
    Ws, Hs = nb * PW * s, nf * PH * s
    fy = (nf - 1 - 7) * PH * s
    hi = (f'<rect class="fa-h" x="0" y="{fy:.2f}" width="{Ws:.2f}" height="{PH*s:.2f}"/>'
          f'<rect class="fa-c" x="{23*PW*s:.2f}" y="{fy:.2f}" width="{PW*s:.2f}" height="{PH*s:.2f}"/>'
          f'<text class="fa-t" x="{Ws+6:.1f}" y="{fy+8:.1f}">{{7;0}} to {{7;49}}</text>'
          f'<line class="fa-l" x1="{23.5*PW*s:.2f}" y1="{fy:.2f}" x2="{23.5*PW*s:.2f}" y2="-10"/>'
          f'<text class="fa-t" x="{23.5*PW*s+4:.2f}" y="-12">P-07-23 &#183; type 09 &#183; deviation 3.2 mm</text>')
    dm = (f'<g class="dm"><line x1="0" y1="{Hs+8:.1f}" x2="{Ws:.1f}" y2="{Hs+8:.1f}"/><text x="{Ws/2:.1f}" y="{Hs+20:.1f}" text-anchor="middle">30 000</text>'
          f'<line x1="{Ws+8:.1f}" y1="{Hs-PH*s*4:.1f}" x2="{Ws+8:.1f}" y2="{Hs:.1f}"/><text x="{Ws+12:.1f}" y="{Hs-PH*s*1.6:.1f}">12 000</text></g>')
    lg, gx = [], 0
    for t in range(12):
        w = (1 - t / 11) * .78 * 14 + .6
        lg.append(f'<rect class="fa-p" x="{gx:.1f}" y="{Hs+30:.1f}" width="14" height="22"/><rect class="fa-o" x="{gx+(14-w)/2:.1f}" y="{Hs+32:.1f}" width="{w:.1f}" height="18"/>'
                  f'<text class="fa-n" x="{gx+7:.1f}" y="{Hs+62:.1f}" text-anchor="middle">{t+1:02d}</text><text class="fa-m" x="{gx+7:.1f}" y="{Hs+72:.1f}" text-anchor="middle">{count[t]}</text>')
        gx += 29.5
    lg.append(f'<text class="fa-m" x="{gx+2:.1f}" y="{Hs+62:.1f}">type</text><text class="fa-m" x="{gx+2:.1f}" y="{Hs+72:.1f}">panels</text>')
    return (f'<svg class="dg facade" viewBox="-2 -24 {Ws+108:.0f} {Hs+102:.0f}" role="img" aria-label="Elevation of a west facade 30 by 12 metres of 600 panels in 50 bays and 12 floors. '
            f'Each panel has a vertical opening that narrows where the sun is strongest; the openings are grouped into 12 panel types, shown below with how many of each. '
            f'Floor 7 is outlined as one branch of the data tree, from 7;0 to 7;49, and panel P-07-23 is marked as type 09 with a deviation of 3.2 mm.">'
            f'{"".join(cells)}{hi}{dm}{"".join(lg)}</svg>')

# ============================== the three levels ==============================
AI_NOTE = 'Kindly do not send AI-generated scripts. The studio uses AI-detection tools, and any submission found to be assisted by AI generative tools shall be disqualified.'
DIVS = [
 dict(k='interns', no='01', file='Interns', name='Interns', sub='Foundation', tone='y', lvl=1,
      who='Students applying for an internship.', tools='Rhino. Grasshopper is a plus, not a must.', time='Most people take about three days.',
      ask='Try both.',
      snips=[
        dict(code='A', name='The Rods', brief='Fifty rods. Create anything with them.', dg=lambda: stand_svg([(20, 1000), (20, 750), (10, 500)]),
             have=None,
             b1=('Create anything with it, but', ['Use every rod. Cut none.', 'It stands on its own.', 'Someone can sit on it, in it or under it.']),
             b2=('The model', ['Model it in Rhino.', 'If you can, build it in Grasshopper, with one slider that changes the design.', 'Show it from eye level, the way someone would first meet it.'])),
        dict(code='B', name='The Screen', brief='One sheet of plywood, perforated.', dg=screen_svg,
             have='One sheet, 1220 &#215; 2440 mm, 12 mm thick.',
             b1=('The screen', ['Holes from 20 to 120 mm across.', 'At least 25 mm of material between holes, and 60 mm at the edges.', 'The pattern responds to one thing you choose: a point, a line or a photograph.']),
             b2=('The script', ['A Grasshopper definition draws the pattern. Move your point, or change your photograph, and it updates.', 'It reports the number of holes and how much of the sheet is open.', 'Draw the sheet flat, ready to cut.']))],
      send=['Two or three images: renders, or photographs of a model you made.', 'The Rhino file (.3dm), and the .gh file if you made one.', 'A hand sketch, if you have one. We like sketches.', '100 words on the idea.'],
      read='We look at the idea, the eye and how clearly you show it. A simple model with a clear idea beats a complicated one with none.'),
 dict(k='junior', no='02', file='Junior-Architects', name='Junior Architects', sub='Systems', tone='r', lvl=2,
      who='Architects with up to three years of practice.', tools='Rhino and Grasshopper.', time='Most people take about a week.',
      ask='Try both.',
      snips=[
        dict(code='A', name='The Kit', brief='Create anything with it. Use every piece.', dg=lambda: stand_svg([(30, 1000), (30, 750), (20, 500)], 12),
             have=None,
             b1=('Create anything with it, but', ['Use every piece. Cut none.', 'It touches the ground at no more than three points.', 'One person can stand upright inside or under it (2100 mm clear).', 'Every rod meets at least two other pieces.']),
             b2=('The script', ['One Grasshopper definition builds the whole thing.', 'A single slider must give at least three different versions that still obey all four rules.', 'A panel shows the live count of each piece used.'])),
        dict(code='B', name='The Field', brief='A wall 6000&#160;mm long and 3000&#160;mm high.', dg=field_svg,
             have=None, legend=True,
             b1=('The wall', ['Build it from one repeated component no bigger than 300 &#215; 300 &#215; 300 mm. Minimum 400 pieces.', 'The component changes (turn, opening, depth, your call) in response to two things: a point, which is a person walking past, and a curve, which is anything you want it to be.', 'Somewhere the wall is fully closed. Somewhere it is at least 70% open.']),
             b2=('The script', ['Move the point or redraw the curve and the wall updates.', 'Every component is numbered.', 'All pieces are laid flat for cutting from 1220 &#215; 2440 mm sheets, and the script reports how many sheets you need.']))],
      send=['Three 3D images.', 'The .gh file with all geometry internalized, and your Rhino version.', 'Native components preferred. If you use plug-ins, list them.', '100 words on the idea.'],
      read='We will be evaluating both the 3D and the script. A beautiful model with a messy script loses to a good model with a script we can read.'),
 dict(k='advanced', no='03', file='Advanced', name='Advanced', sub='Fabrication and data', tone='g', lvl=3,
      who='Architects and computational designers with three years or more, or anyone ready to show it.', tools='Rhino, Grasshopper and the plug-ins you trust.', time='Most people take about two weeks.',
      ask='Try both, or go deep on one and tell us why.',
      snips=[
        dict(code='A', name='The Canopy', brief='A canopy 8&#160;&#215;&#160;8&#160;m, cut from flat sheets.', dg=canopy_svg,
             have='18 mm birch plywood in 1220 &#215; 2440 mm sheets, a CNC router with a 6 mm cutter, and M8 bolts, as many as you need.',
             b1=('The canopy', ['It covers 8 &#215; 8 m on plan, with at least 2400 mm clear below, on no more than three supports.', 'Every part is cut flat from one sheet. At least 150 parts.', 'Parts join by slots, notches or bolts. No glue, no nails.', 'The nest uses at least 70% of each sheet.']),
             b2=('The script', ['Every part carries an ID that says where it sits. The script engraves it on the part and prints it on the drawings.', 'It nests all parts 6 mm apart and reports the sheets used and the yield.', 'Change the canopy&#8217;s form and the parts, IDs, nest and drawings all update.'])),
        dict(code='B', name='The Facade', brief='A west facade in Riyadh, 30&#160;m long and 12&#160;m high.', dg=facade_svg,
             have='A wall 30 &#215; 12 m facing west in Riyadh (24.7&#176; N), a panel module of your choice, and at least 600 panels.',
             b1=('The facade', ['Each panel opens or closes in response to the sun on that wall (Ladybug, or your own calculation).', 'No more than 12 panel types. Every panel within 5 mm of its ideal shape, or a tolerance you justify.', 'The data tree has one branch per floor and one item per panel: {floor;bay}.']),
             b2=('The script', ['It writes a panel schedule (CSV): ID, type, position, rotation and deviation.', 'It rebuilds the whole facade from that CSV alone.', 'It reports how many panels of each type, and what a thirteenth type would save.']))],
      send=['Three 3D images.', 'The fabrication set. The Canopy: one DXF per sheet (cut, engrave and drill layers), the assembly sequence in 6 to 10 steps, and the parts schedule (CSV). The Facade: every panel type at 1:20 with dimensions, and the panel schedule (CSV).',
            'The .gh file with all geometry internalized and its groups named, and your Rhino version.', 'A diagram of your data tree: what each path holds.', 'Plug-ins are welcome (Karamba3D, Ladybug, OpenNest, your own). List them.', '150 words on the idea.'],
      read=''),
]

# ============================== page ==============================
looks = [
    ('Digital fluency', 'A good command of Rhino and Grasshopper is a definite advantage. Grasshopper ninjas are particularly welcome! If your skills are still developing but you are willing to learn, we are happy to take a chance.'),
    ('Intellectual curiosity', 'We expect you to read, explore, question, and engage with ideas beyond architecture.'),
    ('A sense of humor', 'Being a real joker helps. A stand-up comedian would fit right in.'),
    ('Independent thinking', 'We value lateral thinkers, humanists, interdisciplinary minds, and people with an unusually broad spectrum of interests.'),
    ('Architectural awareness', 'Familiarity with significant architects, designers, thinkers, and their work will certainly help during the interview.'),
]
li = lambda xs: ''.join(f'<li>{x}</li>' for x in xs)
lvl = lambda n: '<span class="lvl" role="img" aria-label="Level ' + str(n) + ' of 3">' + ''.join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(3)) + '</span>'
looks_html = ''.join(f'<li><span class="n">0{i+1}</span><h4>{t}</h4><p>{d}</p></li>' for i, (t, d) in enumerate(looks))
end_block = lambda cls, subj='Design%20Snippet': (f'<div class="{cls}"><p class="to">Send your submission to</p><a class="addr" href="mailto:{CAREERS}?subject={subj}">{CAREERS}</a>'
    f'<p class="reg">Please write your level in the subject line. We regret that we may not be able to respond individually to every submission. However, if your interpretation makes us wish we had thought of it ourselves, you can expect to hear from us!</p>'
    f'<p class="gl dsp">Good luck.<br><span>Surprise us.</span></p></div>')

def snippet(d, s, first):
    have = f'<p class="have"><span class="mono">You have</span>{s["have"]}</p>' if s.get('have') else ''
    leg = ('<p class="lgd"><span><i class="lp"></i>The point: a person walking past</span><span><i class="lc"></i>The curve: anything you want it to be</span>'
           '<span>450 pieces of 200 mm, one way of many</span></p>') if s.get('legend') else ''
    wide = d['k'] != 'interns'
    return f'''<section class="sn{' wide' if wide else ''}" id="{d["k"]}-{s["code"].lower()}"><div class="w">
  <div class="snh"><span class="chip">{d["no"]}&#183;{s["code"]}</span><h3 class="dsp">{s["name"]}</h3><p class="brief">{s["brief"]}</p></div>
  {have}
  <div class="snb{' tall' if not wide else ''}">
   <div class="blk dgw">{'' if s.get('have') or d['k'] == 'advanced' else '<p class="mono">You have</p>' if s['code'] == 'A' else ''}{s["dg"]()}{leg}</div>
   <div class="blk"><p class="mono">{s["b1"][0]}</p><ul>{li(s["b1"][1])}</ul></div>
   <div class="blk"><p class="mono">{s["b2"][0]}</p><ul>{li(s["b2"][1])}</ul></div>
  </div>
 </div></section>'''

def division(d):
    a, b = d['snips']
    return f'''<div class="dv t-{d["tone"]}" id="{d["k"]}">
<div class="pg">
 <section class="dvh"><div class="w">
  <div class="dvt"><p class="mono">Level {d["no"]}</p>{lvl(d["lvl"])}</div>
  <h2 class="dsp">{d["name"]}</h2>
  <div class="dvf"><p class="sub">{d["sub"]}</p>
   <dl><div><dt class="mono">For</dt><dd>{d["who"]}</dd></div><div><dt class="mono">Tools</dt><dd>{d["tools"]}</dd></div><div><dt class="mono">Time</dt><dd>{d["time"]}</dd></div></dl>
   <p class="ask">{d["ask"]}</p></div>
 </div></section>
 {snippet(d, a, True)}
</div>
<div class="pg">
 {snippet(d, b, False)}
</div>
</div>'''

cards = ''.join(f'''<div class="card t-{d["tone"]}"><span class="mono">Level {d["no"]}</span>{lvl(d["lvl"])}
 <a class="dsp nm" href="#{d["k"]}">{d["name"]}</a><span class="sb">{d["sub"]}</span><span class="wh">{d["who"]}</span>
 <span class="sn2 mono"><a href="#{d["k"]}-a">{d["no"]}&#183;A {d["snips"][0]["name"]}</a><a href="#{d["k"]}-b">{d["no"]}&#183;B {d["snips"][1]["name"]}</a></span><a class="go mono" href="#{d["k"]}">Read the brief <span aria-hidden="true">&#8595;</span></a></div>''' for d in DIVS)

CSS = r'''
:root{--crimson:#A7182C;--crimson-deep:#7C1222;--marigold:#F2B705;--graphite:#2B2B30;--ink:#16161A;--concrete:#66666C;--grey:#E9E9E6;--fog:#EFEFEC;--line:#DADAD6;
--display:"Archivo","Arial Narrow","Helvetica Neue",Arial,sans-serif;--body:"Instrument Sans","Helvetica Neue",Arial,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
--gut:clamp(20px,5vw,72px);--max:1240px}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#fff;color:var(--ink);font:400 17px/1.55 var(--body)}
a{color:inherit;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.18em}
h1,h2,h3,h4,p,ul,ol,dl,dd{margin:0}
.w{max-width:var(--max);margin:0 auto;padding:0 var(--gut)}
.mono{font:500 12px/1.45 var(--mono);letter-spacing:.08em;text-transform:uppercase}
.dsp{font-family:var(--display);font-stretch:62%;font-weight:800;text-transform:uppercase;line-height:.86;letter-spacing:-.005em}
.hd{font-family:var(--display);font-stretch:75%;font-weight:750;line-height:1.05;font-size:clamp(28px,3.2vw,44px)}
section{padding:clamp(56px,8vw,112px) 0}
.top{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line)}
.top .w{display:flex;align-items:center;gap:16px;height:68px}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;font:600 15px/1.1 var(--body)}
.brand img{width:44px;height:44px}
.top nav{margin-left:auto;display:flex;align-items:center;gap:22px}.top nav a{text-decoration:none}
.dl{display:inline-flex;align-items:center;gap:10px;background:var(--marigold);color:var(--ink);text-decoration:none;padding:12px 18px;font:600 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;border:0}
.dl:hover{background:var(--ink);color:#fff}
.lvl{display:inline-flex;gap:4px;vertical-align:middle}.lvl i{width:16px;height:8px;border:1.5px solid currentColor;display:block}.lvl i.on{background:currentColor}
/* cover */
.cover{background:var(--crimson);color:#fff;padding:0}
.cover .w{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);min-height:min(78vh,720px);max-width:none;padding-left:max(var(--gut),calc((100vw - var(--max)) / 2 + var(--gut)));padding-right:0}
.cover .l{padding:clamp(48px,7vw,96px) 0 clamp(40px,5vw,72px);display:flex;flex-direction:column;justify-content:space-between;gap:48px}
.cover h1{font-size:clamp(76px,13vw,190px)}
.cover .sub{font:500 clamp(19px,1.8vw,24px)/1.35 var(--body);max-width:30ch}
.cover .r{background:var(--marigold);color:var(--ink);padding:clamp(40px,5vw,72px) max(var(--gut),calc((100vw - var(--max)) / 2 + var(--gut))) clamp(40px,5vw,72px) var(--gut);display:flex;flex-direction:column;justify-content:flex-end;gap:22px}
.cover .r .big{font-family:var(--display);font-stretch:75%;font-weight:750;font-size:clamp(34px,4vw,56px);line-height:1}
.cover .r ol{list-style:none;padding:0;border-top:2px solid var(--ink)}.cover .r ol li{display:flex;gap:14px;align-items:baseline;padding:10px 0;border-bottom:1px solid #16161a40;font:600 17px/1.2 var(--body)}
.cover .r ol .mono{min-width:2.2em}.cover .r ol a{display:flex;gap:14px;align-items:baseline;text-decoration:none;width:100%}.cover .r ol a:hover{text-decoration:underline}
.cover .r .dl{background:var(--ink);color:#fff;align-self:flex-start}.cover .r .dl:hover{background:#fff;color:var(--ink)}

/* desk */
.desk{background:var(--grey);padding:clamp(40px,5vw,64px) 0}
.desk .w{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:14px 56px;align-items:baseline}.desk .mono{color:var(--crimson)}
.cd{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 28px}.cdm{font-family:var(--display);font-stretch:75%;font-weight:750;font-size:clamp(24px,2.6vw,36px);line-height:1.1;overflow-wrap:anywhere}
/* belong, looks, grades, more */
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);gap:32px 56px}
.two .txt p+p{margin-top:16px}
.lead{font:500 clamp(20px,1.9vw,26px)/1.4 var(--body)}
.looks{list-style:none;padding:0;margin-top:14px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));border-top:2px solid var(--ink)}
.looks li{padding:18px 18px 0;border-right:1px solid var(--line)}.looks li:first-child{padding-left:0}.looks li:last-child{border-right:0}
.looks .n{font:500 13px/1 var(--mono);color:var(--crimson)}.looks h4{font:700 18px/1.2 var(--body);margin:12px 0 10px}.looks p{font-size:15px;line-height:1.5;color:#3a3a40}
.grades{background:var(--marigold);padding:clamp(48px,6vw,88px) 0}
.grades p{font-family:var(--display);font-stretch:75%;font-weight:750;font-size:clamp(34px,5vw,72px);line-height:1}.grades .q{opacity:.55}
.more{background:var(--graphite);color:#fff}.more .txt p{color:#d6d6d2}.more .txt p+p{margin-top:16px}.more .last{color:var(--marigold)!important;font-weight:600}
/* choose */
.choose .lead{max-width:40ch}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:clamp(32px,4vw,56px)}
.card{display:flex;flex-direction:column;gap:12px;padding:clamp(24px,2.6vw,36px);min-height:clamp(380px,34vw,470px);text-decoration:none}
.card .nm{font-size:clamp(40px,3.8vw,56px);margin-top:auto}.card .sb{font:600 18px/1.2 var(--body)}.card .wh{font-size:15px;line-height:1.45;max-width:30ch;opacity:.85}
.card .sn2{opacity:.8;font-size:11px}.card .go{border-top:1px solid currentColor;padding-top:12px}
.card a{text-decoration:none}.card a:hover{text-decoration:underline}.card .sn2{display:flex;flex-wrap:wrap;gap:4px 18px}.card .nm{display:block}
.t-y.card{background:var(--marigold);color:var(--ink)}.t-r.card{background:var(--crimson);color:#fff}.t-g.card{background:var(--graphite);color:#fff}
/* division */
.dvh{padding:clamp(48px,6vw,96px) 0 clamp(36px,4.5vw,64px)}
.t-y .dvh{background:var(--marigold);color:var(--ink)}.t-r .dvh{background:var(--crimson);color:#fff}.t-g .dvh{background:var(--graphite);color:#fff}
.dvt{display:flex;justify-content:space-between;align-items:center;gap:16px;padding-bottom:14px;border-bottom:1px solid currentColor}
.dvh h2{font-size:clamp(76px,12vw,190px);margin:clamp(24px,3vw,40px) 0 clamp(20px,2.4vw,32px)}
.dvf{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,2.2fr) auto;gap:18px 40px;align-items:start}
.dvf .sub{font-family:var(--display);font-stretch:75%;font-weight:750;font-size:clamp(24px,2.4vw,34px);line-height:1.05}
.t-g .dvf .sub,.t-g .ask{color:var(--marigold)}.t-r .ask{color:var(--marigold)}
.dvf dl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px 28px}.dvf dt{margin-bottom:6px;opacity:.75}.dvf dd{font-size:15px;line-height:1.45}
.ask{font:600 16px/1.3 var(--body);max-width:16ch}
.sn{background:var(--fog);padding:clamp(40px,5vw,72px) 0}
.sn+.sn,.pg+.pg .sn{border-top:1px solid var(--line)}
.snh{display:flex;align-items:baseline;gap:14px 24px;flex-wrap:wrap;padding-bottom:16px;border-bottom:2px solid var(--ink)}
.chip{font:600 13px/1 var(--mono);letter-spacing:.08em;padding:8px 10px;align-self:center}
.t-y .chip{background:var(--marigold);color:var(--ink)}.t-r .chip{background:var(--crimson);color:#fff}.t-g .chip{background:var(--graphite);color:var(--marigold)}
.snh h3{font-size:clamp(54px,7.4vw,112px)}.snh .brief{margin-left:auto;font:500 18px/1.35 var(--body);max-width:30ch;text-align:right}
.have{display:flex;gap:16px;align-items:baseline;margin-top:18px;font-weight:500}.have .mono{color:var(--crimson);white-space:nowrap}
.snb{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr) minmax(0,1fr);gap:32px 48px;margin-top:clamp(28px,3.4vw,44px)}
.sn.wide .snb{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.sn.wide .dgw{grid-column:1 / -1}
.snb.tall{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);align-items:start}.snb.tall .dgw{grid-row:span 2}.snb.tall .kit{max-width:560px}.snb.tall .screen{max-width:420px}
.blk .mono{color:var(--crimson);margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #cfcfca}
.blk ul{padding:0;list-style:none}.blk li{padding:9px 0 9px 22px;border-bottom:1px solid var(--line);position:relative;font-size:16px;line-height:1.45}
.blk li:before{content:"";position:absolute;left:0;top:17px;width:10px;height:2px;background:var(--ink)}
.dg{width:100%;height:auto;display:block}.kit{max-width:380px}.screen{max-width:340px}
.sr line{stroke:var(--ink);stroke-width:1.05;stroke-linecap:round}.sp rect{fill:var(--marigold);stroke:var(--ink);stroke-width:.35}.sb{stroke:var(--ink);stroke-width:.5}.sl text{font:600 6.4px var(--mono);fill:var(--ink)}.sl .mu{font-weight:500;fill:var(--concrete)}.stand .dm text{font-size:5.6px}.sn.wide .kit{max-width:none}.stand .dm line{stroke-width:.4}
.k-rod{fill:var(--graphite)}.k-pl{fill:var(--marigold);stroke:var(--ink);stroke-width:1}.k-n{font:600 13px var(--mono);fill:var(--crimson)}.k-l{font:500 10.5px var(--mono);fill:var(--concrete)}.k-sc{stroke:var(--ink);stroke-width:1}
.sh{fill:var(--graphite)}.ho circle{fill:var(--fog)}.pt{fill:var(--crimson);stroke:#fff;stroke-width:1.5}
.dm line{stroke:var(--concrete);stroke-width:.8}.dm text,.nt text,.cp-t{font:500 10px var(--mono);fill:var(--concrete);letter-spacing:.04em}.nt line{stroke:var(--crimson);stroke-width:.8}
.f-t{fill:var(--graphite)}.f-o{fill:var(--fog)}.f-c{fill:none;stroke:var(--crimson);stroke-width:2.5}.f-p{fill:var(--crimson);stroke:#fff;stroke-width:2}.f-l{font:500 11px var(--mono);fill:var(--concrete)}.f-d{stroke:var(--concrete);stroke-width:1}
.lgd{display:flex;flex-wrap:wrap;gap:8px 22px;margin-top:14px;font:500 12px/1.4 var(--mono);color:var(--concrete)}.lgd span{display:inline-flex;align-items:center;gap:8px}.lgd i{display:inline-block}.lgd .lp{width:11px;height:11px;border-radius:50%;background:var(--crimson)}.lgd .lc{width:22px;height:2.5px;background:var(--crimson)}
.cp-o{fill:#fff;stroke:var(--ink);stroke-width:1}.cp-r{stroke:var(--graphite);stroke-width:1.2}.cp-k{stroke:var(--crimson);stroke-width:2.4}.cp-s{fill:var(--crimson);stroke:#fff;stroke-width:1.5}.cp-t.k{fill:var(--crimson);font-weight:600}
.ns-b{fill:#fff;stroke:var(--ink);stroke-width:1}.ns-p{fill:var(--marigold);stroke:var(--ink);stroke-width:.8}.ns-s{fill:#fff;stroke:var(--ink);stroke-width:.6}.ns-t{font:600 7.4px var(--mono);fill:var(--ink)}.ns-d{fill:var(--crimson)}
.fa-p{fill:var(--graphite)}.fa-o{fill:var(--fog)}.fa-h{fill:none;stroke:var(--crimson);stroke-width:1.6}.fa-c{fill:none;stroke:var(--marigold);stroke-width:2}.fa-l{stroke:var(--crimson);stroke-width:.8}
.fa-t{font:600 9.5px var(--mono);fill:var(--crimson)}.fa-n{font:600 8.5px var(--mono);fill:var(--ink)}.fa-m{font:500 8px var(--mono);fill:var(--concrete)}
/* send, end */
.send{background:var(--grey)}
.send ol{list-style:none;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;margin-top:28px;counter-reset:s}
.t-g .send ol{grid-template-columns:repeat(3,minmax(0,1fr))}
.send li{border-top:2px solid var(--ink);padding-top:14px;counter-increment:s;font-size:16px;line-height:1.45}
.send li:before{content:counter(s,decimal-leading-zero);display:block;font:500 13px/1 var(--mono);color:var(--crimson);margin-bottom:12px}
.send .note{margin-top:36px;max-width:60ch;font-weight:600}
.send .dl{margin-top:28px}
.end{background:var(--crimson);color:#fff}
.end .to{font:500 clamp(18px,1.6vw,22px)/1.4 var(--body)}
.end .addr{display:inline-block;margin-top:10px;font-family:var(--display);font-stretch:75%;font-weight:750;font-size:clamp(26px,4.2vw,58px);line-height:1.05;overflow-wrap:anywhere;text-decoration-thickness:2px}
.end .reg{margin-top:28px;max-width:56ch;color:#f3d6da}
.end .gl{margin-top:clamp(48px,6vw,88px);font-size:clamp(56px,9vw,140px)}.end .gl span{color:var(--marigold)}
.foot{background:var(--crimson-deep);color:#fff;padding:22px 0}
.foot .w{display:flex;gap:16px 32px;flex-wrap:wrap;align-items:center;padding-right:max(var(--gut),104px)}.foot .mono{opacity:.85}.foot a{text-decoration:none}.foot .sp{margin-left:auto}
.pr-only{display:none}
.hd em{font-style:italic}.hl-r{color:var(--crimson)}.hl-y{color:var(--marigold)}
/* the PDF mark: bottom right of the screen, on this page only */
.pdfb{position:fixed;z-index:20;right:max(18px,env(safe-area-inset-right));bottom:max(18px,env(safe-area-inset-bottom));width:70px;height:70px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:var(--crimson);color:#fff;text-decoration:none;box-shadow:0 0 0 2px #fff,0 8px 22px rgba(22,22,26,.28);transition:background-color .2s,transform .2s}
.pdfb svg{width:22px;height:27px;display:block}.pdfb span{font:700 11.5px/1 var(--mono);letter-spacing:.1em;color:var(--marigold)}
.pdfb:hover,.pdfb:focus-visible{background:var(--ink);transform:translateY(-2px)}.pdfb:focus-visible{outline:2px solid var(--marigold);outline-offset:3px}
/* index */
.idx .ih{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;border-bottom:2px solid var(--ink);padding-bottom:14px}
.idx h2{font-size:clamp(76px,12vw,190px)}
.ip{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:32px 56px;margin-top:clamp(28px,3.4vw,48px)}
.ipl{color:var(--crimson);padding-bottom:10px;border-bottom:1px solid #cfcfca}
.il{list-style:none;padding:0}.il a{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:14px;align-items:baseline;padding:11px 0;border-bottom:1px solid var(--line);text-decoration:none;font:600 17px/1.3 var(--body)}
.il a.nc{grid-template-columns:minmax(0,1fr) auto}.il .p1 a{font:700 18px/1.25 var(--body);padding:14px 0}.il .p1 .pgn{font-weight:500}.il a:hover .t{text-decoration:underline}
.il .c{font:600 12px/1 var(--mono);letter-spacing:.06em;color:var(--crimson);min-width:3.4em}
.il .pgn{font:500 13px/1 var(--mono);color:var(--concrete)}
.idv{margin-top:14px}.idv>a{grid-template-columns:auto minmax(0,1fr) auto;padding:14px 16px;border:0;row-gap:6px}.idv>a .dn{grid-column:2;grid-row:1}.idv>a .ds{grid-column:2;grid-row:2}.idv>a .pgn{grid-column:3;grid-row:1}.idv>a .mono{grid-column:1;grid-row:1}
.idv>a .dn{font-family:var(--display);font-stretch:62%;font-weight:800;text-transform:uppercase;font-size:clamp(28px,2.6vw,38px);line-height:.9}
.idv>a .ds{font:600 14px/1.2 var(--body);opacity:.85}
.t-y.idv>a{background:var(--marigold);color:var(--ink)}.t-r.idv>a{background:var(--crimson);color:#fff}.t-g.idv>a{background:var(--graphite);color:#fff}
.idv>a .pgn{color:inherit;opacity:.8}.idv ol{list-style:none;padding:0 0 0 16px}
.il2>li:not(.idv){margin-top:0}.il2>li.idv+li:not(.idv){margin-top:14px}
/* send, by division */
.sendall{background:var(--grey)}
.sa{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin-top:clamp(28px,3.4vw,48px);align-items:start}
.sa-h{display:flex;flex-direction:column;gap:10px;padding:18px}
.sa-h .dsp{font-size:clamp(34px,3.4vw,50px)}
.t-y .sa-h{background:var(--marigold);color:var(--ink)}.t-r .sa-h{background:var(--crimson);color:#fff}.t-g .sa-h{background:var(--graphite);color:#fff}
.sa ol{list-style:none;padding:0;counter-reset:s}.sa li{padding:12px 0 12px 34px;border-bottom:1px solid #cfcfca;position:relative;counter-increment:s;font-size:15.5px;line-height:1.45}
.sa li:before{content:counter(s,decimal-leading-zero);position:absolute;left:0;top:14px;font:500 12px/1 var(--mono);color:var(--crimson)}
.sa .note{margin-top:16px;font-weight:700;font-style:italic;font-size:15.5px;line-height:1.45}
.ai{margin-top:clamp(28px,3.4vw,44px);padding-top:14px;border-top:2px solid var(--ink);max-width:78ch}.ai .mono{font-weight:700;color:var(--crimson);margin-bottom:6px}.ai p:last-child{font-style:italic;font-size:14px;line-height:1.5}
@media screen and (max-width:900px){
 .cover .w,.desk .w,.two,.snb,.sn.wide .snb,.dvf{grid-template-columns:minmax(0,1fr)}
 .cover .w{padding-left:0}.cover .l{padding-left:var(--gut);padding-right:var(--gut)}.cover .r{padding-right:var(--gut)}
 .looks,.cards{grid-template-columns:minmax(0,1fr)}.looks li{border-right:0;border-bottom:1px solid var(--line);padding:16px 0}
 .card{min-height:0}.card .nm{margin-top:24px}
 .dvf dl{grid-template-columns:minmax(0,1fr)}
 .send ol,.t-g .send ol{grid-template-columns:repeat(2,minmax(0,1fr))}
 .snh .brief{margin-left:0;text-align:left}
 .ip,.sa{grid-template-columns:minmax(0,1fr)}.idv>a{grid-template-columns:minmax(0,1fr) auto}.idv>a .mono{grid-column:1;grid-row:1}.idv>a .dn{grid-column:1;grid-row:2}.idv>a .ds{grid-column:1;grid-row:3}.idv>a .pgn{grid-column:2;grid-row:1}
 .snb.tall{grid-template-columns:minmax(0,1fr)}.snb.tall .dgw{grid-row:auto}
 .cdm{font-size:21px}.end .addr{font-size:23px}
 .pdfb{width:60px;height:60px}.pdfb svg{width:19px;height:23px}
 .have{flex-direction:column;gap:6px}
 .top nav .bk,.brand span,.top nav .dl{display:none}
 .foot .sp{margin-left:0;flex-basis:100%}
}
@media screen and (max-width:520px){.send ol,.t-g .send ol{grid-template-columns:minmax(0,1fr)}.top .dl{padding:11px 12px}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
/* 26 November 2026 (Mujib): on phones the header logo takes the main site footer logo's size and proportions, with the name */
@media screen and (max-width:700px){.top .w{height:84px}.brand{gap:14px;font:600 17px/1.1 var(--body)}.brand img{width:64px;height:64px}.brand span{display:block}}

/* ===================== the pamphlets: A4, six pages per division ===================== */
@page{size:A4;margin:0}
@media print{
 html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
 body{font-size:10.2pt;line-height:1.48}
 .top,.noprint,.card .go{display:none!important}
 body{counter-reset:pg}.pg{position:relative;counter-increment:pg}
 .pg::after{content:"Design Snippet  " counter(pg,decimal-leading-zero);white-space:pre;position:absolute;right:16mm;bottom:6.5mm;font:500 6.6pt var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--concrete)}
 .pg::before{content:"";position:absolute;left:16mm;bottom:4.4mm;width:7.2mm;height:7.2mm;background:url(/img/logo-224.png) center/contain no-repeat}
 main>.pg:first-child::after,.pg-last::after,main>.pg:first-child::before,.pg-last::before{content:none}
 .pr-only{display:block}
 .cover .r .cv-logo{width:30mm;height:30mm;margin-bottom:auto}
 .foot .ft-logo{width:10mm;height:10mm}
 .foot .w{display:grid;grid-template-columns:auto auto 1fr;column-gap:7mm;row-gap:1.8mm;align-items:center}.foot .mono{white-space:nowrap}
 .foot .ft-logo{grid-row:1 / span 2}.foot .sp{grid-column:2 / span 2;grid-row:2;margin-left:0}
 :root{--gut:16mm}
 .w{max-width:none}
 section{padding:11mm 0}
 .pg{height:297mm;overflow:hidden;break-after:page;display:flex;flex-direction:column}
 /* page 1 */
 .cover{flex:1 1 auto}.cover .w{min-height:0;height:100%;grid-template-columns:1.45fr 1fr;padding-left:var(--gut)}
 .cover h1{font-size:84pt}.cover .sub{font-size:13pt}.cover .r{padding-right:var(--gut)}
 .cover .r .big{font-size:27pt}.cover .r ol li{font-size:11pt;padding:2.4mm 0}
 .desk{padding:10mm 0 12mm}.desk .w{grid-template-columns:1fr}.cdm{font-size:22pt}
 /* page 2 */
 .belong{padding-top:16mm;padding-bottom:12mm}.lead{font-size:13.5pt}
 .looks{margin-top:4mm}.looks li{padding:4mm 3.5mm 0}.looks h4{font-size:11pt}.looks p{font-size:9pt}
 .belong .mono.lk{margin-top:12mm!important}
 /* page 3 */
 .grades{flex:1 1 auto;display:flex;align-items:flex-end;padding:14mm 0 16mm}.grades .w{width:100%}.grades p{font-size:42pt}
 .more{padding:13mm 0 12mm}
 .choose{flex:1 1 auto;padding:11mm 0 14mm}.choose .lead{font-size:12pt}.cards{margin-top:7mm}.card{min-height:112mm;padding:6mm;gap:2.4mm}.card .nm{font-size:29pt}.card .sb{font-size:11pt}.card .wh{font-size:8.6pt}.card .sn2{font-size:6.6pt}.hd{font-size:24pt}
 /* division pages */
 .dvh{padding:13mm 0 9mm}.dvh h2{font-size:76pt;margin:7mm 0 6mm}.dvf .sub{font-size:17pt}.dvf dd{font-size:9.4pt}.ask{font-size:10pt}
 .dvf{grid-template-columns:.7fr 2.3fr .6fr;gap:4mm 7mm}.dvf dl{gap:3mm 6mm}
 .sn{flex:1 1 auto;padding:9mm 0 10mm}
 .snh{padding-bottom:3mm}.snh h3{font-size:50pt}.snh .brief{font-size:11pt}.chip{font-size:9pt;padding:2mm 2.6mm}
 .have{margin-top:4mm;font-size:10pt}
 .snb{margin-top:7mm;gap:6mm 8mm}.snb.tall{grid-template-columns:1.3fr 1fr}.sn.wide .snb{grid-template-columns:1fr 1fr}.snb.tall .kit,.snb.tall .screen{max-width:none}
 .blk li{font-size:9.4pt;padding:4px 0 4px 16px}.blk li:before{top:11px;width:8px}.blk .mono{margin-bottom:2mm;padding-bottom:2mm}
 .lgd{font-size:7.6pt;margin-top:3mm}
 .pg:not(.pg-end) .dvh+.sn .snh h3{font-size:44pt}
 .send{padding:12mm 0 9mm}.send ol{margin-top:5mm;gap:5mm}.send li{font-size:9.4pt;padding-top:3mm}.send li:before{margin-bottom:2mm}.send .note{margin-top:6mm;font-size:10.4pt}
 .end{flex:1 1 auto;padding:11mm 0}.end .addr{font-size:24pt}.end .gl{font-size:46pt;margin-top:8mm}.end .reg{margin-top:4mm;font-size:9.6pt}.end .to{font-size:11.5pt}
 .foot{padding:5mm 0}.foot .w{padding-right:var(--gut)}
 .idx{flex:1 1 auto;padding:18mm 0 14mm}.idx h2{font-size:120pt}.ip{margin-top:12mm;gap:8mm 10mm}
 .il a{padding:3.4mm 0;font-size:11pt}.il .p1 a{font-size:11pt;padding:3.4mm 0}.il .c{font-size:7.4pt}.il .pgn{font-size:8pt}
 .idv{margin-top:5mm}.idv>a{padding:4.4mm 4.6mm;row-gap:1.6mm}.idv>a .dn{font-size:21pt}.idv>a .ds{font-size:8.6pt}.idv ol{padding-left:4mm}.il2>li.idv+li:not(.idv){margin-top:4mm}
 .ai{margin-top:6mm;padding-top:3mm}.ai .mono{font-size:7pt}.ai p:last-child{font-size:8.6pt}.sendall .ai{margin-top:auto}.sendall .w{display:flex;flex-direction:column;height:100%}
 .sendall{flex:1 1 auto;padding:16mm 0 14mm}.sa{margin-top:8mm;gap:6mm}.sa-h{padding:4mm}.sa-h .dsp{font-size:26pt}.sa li{font-size:9pt;padding:2.4mm 0 2.4mm 8mm}.sa li:before{top:3mm;font-size:7pt}.sa .note{font-size:9.4pt;margin-top:4mm}
 .pg-last .end{flex:1 1 auto;display:flex;align-items:flex-end;padding:20mm 0 16mm}.pg-last .end .w{width:100%}.pg-last .end .addr{font-size:30pt}.pg-last .end .gl{font-size:82pt;margin-top:22mm}.pg-last .end .reg{font-size:10.4pt}.pg-last .end .to{font-size:13pt}
 a{text-decoration-thickness:.6pt}
}
'''

DV = '\n'.join(division(d) for d in DIVS)
# page numbers of the pamphlet (twelve A4 pages)
PG = dict(desk=1, index=2, belong=3, more=4, divisions=4, send=11, submit=12, interns=5, junior=7, advanced=9)
row = lambda href, title, pg, code='': f'<li><a href="#{href}"{"" if code else " class=nc"}>{f"<span class=c>{code}</span>" if code else ""}<span class="t">{title}</span><span class="pgn">{pg if isinstance(pg, str) else f"{pg:02d}"}</span></a></li>'
part1 = row('cover', 'More than a place to work', '01&#8211;04').replace('<li>', '<li class="p1">', 1)
part2 = ''.join(f'''<li class="idv t-{d["tone"]}"><a href="#{d["k"]}"><span class="mono">Level {d["no"]}</span><span class="dn">{d["name"]}</span><span class="ds">{d["sub"]}</span><span class="pgn">{PG[d["k"]]:02d}</span></a>
  <ol>{row(d["k"] + "-a", d["snips"][0]["name"], PG[d["k"]], d["no"] + "&#183;A")}{row(d["k"] + "-b", d["snips"][1]["name"], PG[d["k"]] + 1, d["no"] + "&#183;B")}</ol></li>''' for d in DIVS)
INDEX = f'''<div class="pg">
 <section class="idx" id="index"><div class="w">
  <div class="ih"><h2 class="dsp">Index</h2><p class="mono">Design Snippet</p></div>
  <div class="ip">
   <div><p class="mono ipl">Part one &#183; The studio</p><ol class="il">{part1}</ol></div>
   <div><p class="mono ipl">Part two &#183; The exercises</p><ol class="il il2">{part2}</ol></div>
  </div>
 </div></section>
</div>'''
SENDALL = f'''<div class="pg">
 <section class="sendall" id="send"><div class="w">
  <h2 class="hd">Send us, for each snippet</h2>
  <div class="sa">{''.join(f'<div class="sa-c t-{d["tone"]}"><div class="sa-h"><span class="mono">Level {d["no"]}</span><span class="dsp">{d["name"]}</span></div><ol>{li(d["send"])}</ol>{f'<p class="note">{d["read"]}</p>' if d["read"] else ''}</div>' for d in DIVS)}</div>
  <div class="ai ai-imp"><p class="mono">Important note</p><p>{AI_NOTE}</p></div>
 </div></section>
</div>'''
FOOT = f'<footer class="foot"><div class="w"><img class="pr-only ft-logo" src="/img/logo-224.png" alt="" width="224" height="224"><span class="mono">Collaborative Architecture</span><span class="mono">Mumbai | Riyadh</span><a class="mono sp" href="{SITE}">collaborativearchitecture.com</a></div></footer>'

HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="generator" content="Custom built and designed">
<title>Design Snippet: careers at Collaborative Architecture, Mumbai and Riyadh</title>
<meta name="description" content="The Design Snippet: design challenges in Rhino and Grasshopper, in three levels for interns, junior architects and advanced applicants who want to join Collaborative Architecture in Mumbai or Riyadh. Read them here or download them as PDFs.">
<meta name="author" content="Collaborative Architecture">
<link rel="canonical" href="{SITE}design-snippet/">
<meta name="theme-color" content="#A7182C">
<meta property="og:type" content="website"><meta property="og:site_name" content="Collaborative Architecture"><meta property="og:title" content="Design Snippet: careers at Collaborative Architecture">
<meta property="og:description" content="Design challenges in three levels, for interns, junior architects and advanced applicants, in Mumbai or Riyadh.">
<meta property="og:url" content="{SITE}design-snippet/"><meta property="og:image" content="{SITE}img/share/design-snippet-levels.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/fonts/ca-fonts.css">
<style>{CSS}</style>
</head><body>
<!--email_off-->
<header class="top"><div class="w">
 <a class="brand" href="/"><img src="/img/logo-224.png" alt="" width="44" height="44"><span>Collaborative<br>Architecture</span></a>
 <nav><a class="bk mono" href="/studio/#careers">Careers</a><a class="bk mono" href="#index">Index</a><a class="dl" href="{PDF}" download>Download PDF <span aria-hidden="true">&#8595;</span></a></nav>
</div></header>
<main>
<div class="pg">
 <section class="cover" id="cover"><div class="w">
  <div class="l">
   <p class="mono">Careers &#183; Mumbai | Riyadh</p>
   <h1 class="dsp">Design<br>Snippet</h1>
   <p class="sub">Before we take this further, here is an opportunity to introduce us to the way you think.</p>
  </div>
  <div class="r">
   <img class="pr-only cv-logo" src="/img/logo-640.png" alt="Collaborative Architecture" width="640" height="640">
   <div class="cvr"><p class="mono">Three levels</p><p class="big" style="margin:12px 0 18px">Choose yours.</p>
    <ol>{''.join(f'<li><a href="#{d["k"]}"><span class="mono">{d["no"]}</span>{d["name"]}</a></li>' for d in DIVS)}</ol><a class="dl noprint" href="{PDF}" download>Download PDF <span aria-hidden="true">&#8595;</span></a></div>
  </div>
 </div></section>
 <section class="desk" id="desk"><div class="w">
  <p class="mono">The Careers Desk &#183; Mumbai Studio</p>
  <div class="cd"><a class="cdm" href="mailto:{CAREERS}">{CAREERS}</a><p>Exclusively for career and internship applications.</p></div>
 </div></section>
</div>
{INDEX}
<div class="pg">
 <section class="belong" id="belong"><div class="w">
  <div class="two">
   <h2 class="hd"><em>Is this where you <span class="hl-r">belong?</span></em></h2>
   <div class="txt">
    <p class="lead">Thank you for your interest in joining Collaborative Architecture.</p>
    <p>Headquartered in Mumbai, with a studio in Riyadh, KSA, Collaborative Architecture is an international practice driven by the convergence of people, places, cultures, and interdisciplinary thinking.</p>
    <p>We are interested in individuals who are curious, intellectually adventurous, creatively restless, and willing to challenge conventions.</p>
   </div>
  </div>
  <p class="mono lk" id="looks" style="margin-top:clamp(40px,5vw,64px);color:var(--crimson)">A few things we look for</p>
  <ol class="looks">{looks_html}</ol>
 </div></section>
 <section class="grades" id="grades"><div class="w"><p><span class="q">Your university grades?</span><br>Not particularly interested.<br><span class="q">Your ideas?</span> Very much so.</p></div></section>
</div>
<div class="pg">
 <section class="more" id="more"><div class="w two">
  <h2 class="hd"><em>More than a place to <span class="hl-y">work</span></em></h2>
  <div class="txt">
   <p class="lead" style="color:#fff">Collaborative is a studio where you are expected to challenge yourself, challenge us, and explore possibilities beyond the obvious.</p>
   <p>We are not particularly interested in conventional job seekers. We look for people with the curiosity to question, the courage to experiment, and the imagination to make their own rules.</p>
   <p>Our work culture can be intense, unconventional, and occasionally intimidating. For some, it might seem demanding; for others, liberating.</p>
   <p class="last">We are actively looking for the latter.</p>
  </div>
 </div></section>
 <section class="choose" id="levels"><div class="w">
  <div class="two"><h2 class="hd">A small challenge, in three levels</h2><p class="lead">Choose the level for the role you are applying for. You may always try the one above it.</p></div>
  <div class="cards">{cards}</div>
  <div class="ai"><p class="mono">Note</p><p>{AI_NOTE}</p></div>
 </div></section>
</div>
{DV}
{SENDALL}
<div class="pg pg-last">
 <section class="end" id="submit"><div class="w">{end_block('eb')}</div></section>
 {FOOT}
</div>
</main>
<a class="pdfb noprint" href="{PDF}" download aria-label="Download the Design Snippet as a PDF" title="Download the Design Snippet (PDF)"><svg viewBox="0 0 22 27" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M1.5 1.5h12l7 7v17h-19z"/><path d="M13.5 1.5v7h7"/></svg><span>PDF</span></a>
<!--/email_off-->
</body></html>
'''
open(sys.argv[1], 'w', encoding='utf-8').write(HTML)
