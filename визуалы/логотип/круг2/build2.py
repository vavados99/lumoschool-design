#!/usr/bin/env python3
"""Круг 2: логотип LUMOSCHOOL. Всё кодом: SVG руками, шрифт сайта (Golos Text 600) -> контуры через fontTools."""
import os, re, math, json, io, base64
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
D = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(D + '/../../../прототипы-люмо/B5-тьма/fonts')
ORANGE, ORANGE_L, CREAM, INK, DARKBG = '#FF7A45', '#DF5520', '#FBEFDF', '#2A1A2E', '#1E1424'
BEND = 44          # сдвиг кончика вправо в единицах 480-сетки (угол см. ниже)

# ---------- геометрия капли ----------
DROP = [('M', [(222,22)]),
 ('C', [(238,42),(262,98),(296,150)]), ('C', [(338,218),(358,292),(346,360)]),
 ('C', [(334,430),(282,478),(200,478)]), ('C', [(118,478),(66,430),(54,360)]),
 ('C', [(42,292),(62,218),(104,154)]), ('C', [(140,100),(184,66),(204,38)]),
 ('C', [(210,28),(216,20),(222,22)]), ('Z', [])]
def bend(x, y, k=BEND):
    t = max(0.0, (330 - y) / 308.0)
    return x + k * t ** 1.6, y
def fire_path(y0, y1, w):       # огонёк-капля, остриём вверх (480-сетка)
    h = y1 - y0; cx = 200; r = w / 2; yb = y1 - r
    return [('M', [(cx, y0)]), ('C', [(cx+r*.45, y0+h*.22),(cx+r, yb-h*.28),(cx+r, yb)]),
            ('C', [(cx+r, yb+r*.55),(cx+r*.55, y1),(cx, y1)]), ('C', [(cx-r*.55, y1),(cx-r, yb+r*.55),(cx-r, yb)]),
            ('C', [(cx-r, yb-h*.28),(cx-r*.45, y0+h*.22),(cx, y0)]), ('Z', [])]
def ell(cx, cy, rx, ry):
    return [('M', [(cx-rx, cy)]), ('A', [(rx, ry, cx+rx, cy)]), ('A', [(rx, ry, cx-rx, cy)]), ('Z', [])]
def xf_path(segs, f):
    out = []
    for c, pts in segs:
        if c == 'A': out.append((c, pts))   # эллипс не гнём — переносим центр отдельно
        else: out.append((c, [f(*p) for p in pts]))
    return out
def sample(segs, n=40):
    pts = []; cur = None
    for c, p in segs:
        if c == 'M': cur = p[0]; pts.append(cur)
        elif c == 'C':
            for i in range(1, n+1):
                t = i/n; a = (1-t)**3; b = 3*t*(1-t)**2; cc = 3*t*t*(1-t); d = t**3
                pts.append((a*cur[0]+b*p[0][0]+cc*p[1][0]+d*p[2][0], a*cur[1]+b*p[0][1]+cc*p[1][1]+d*p[2][1]))
            cur = p[2]
    return pts
def fmt(v): return ('%.2f' % v).rstrip('0').rstrip('.')
def to_d(segs, f):
    s = []
    for c, p in segs:
        if c == 'Z': s.append('Z')
        elif c == 'A': s.append('A%s %s 0 1 0 %s %s' % (fmt(p[0][0]*f[0]), fmt(p[0][1]*f[0]), *map(fmt, f[1](p[0][2], p[0][3]))))
        else: s.append(c + ' '.join('%s %s' % tuple(map(fmt, f[1](*q))) for q in p))
    return ''.join(s)

def mark_geom():
    """возвращает пути (в viewBox 100) и параметры. Капля нормируется: высота 88, центр тела x=50, y 6..94"""
    drop = xf_path(DROP, bend)
    pts = sample(drop); ys = [p[1] for p in pts]; s = 88.0 / (max(ys) - min(ys))
    ty = 6 - min(ys) * s; tx = 50 - 200 * s
    T = lambda x, y: (x * s + tx, y * s + ty)
    g = {'s': s, 'T': T, 'bbox': (min(p[0] for p in pts)*s+tx, min(ys)*s+ty, max(p[0] for p in pts)*s+tx, max(ys)*s+ty)}
    g['drop'] = to_d(drop, (1, T))
    # глаза +15 % и шире (32 px и больше)
    ex = [(142, 322), (258, 322)]
    g['eyes'] = ''.join(to_d(ell(0, 0, 41, 53), (s, lambda x, y, cx=cx, cy=cy: T(cx + x*0 + x, cy + y)))
                        if False else to_d([('M', [(cx-41, cy)]), ('A', [(41, 53, cx+41, cy)]), ('A', [(41, 53, cx-41, cy)]), ('Z', [])], (s, T))
                        for cx, cy in ex)
    fire = xf_path([('M', [(216,98)]), ('C', [(208,142),(252,160),(252,198)]), ('C', [(252,224),(230,236),(202,236)]),
                    ('C', [(174,236),(152,218),(152,194)]), ('C', [(152,166),(178,152),(192,132)]), ('C', [(200,120),(212,114),(216,98)]), ('Z', [])], bend)
    g['fire'] = to_d(fire, (1, T))
    # угол кончика: ось от центра основания (200,330) к вершине
    tip = bend(222, 22); g['angle_before'] = math.degrees(math.atan2(222-200, 330-22)); g['angle_after'] = math.degrees(math.atan2(tip[0]-200, 330-tip[1]))
    return g
G = mark_geom()

# L-вырез для v1 (внутри капли, не гнётся; сдвиг вправо к наклонённому телу)
def v1_L():
    s, T = G['s'], G['T']; dx = 6
    pts = [(126+dx,176),(194+dx,176),(194+dx,346),(280+dx,346),(280+dx,414),(126+dx,414)]
    return 'M' + 'L'.join('%s %s' % tuple(map(fmt, T(*p))) for p in pts) + 'Z'

# ---------- v2 ----------
def v2_parts():
    L = 'M24 10H39V70H80V86H24Z'
    # огонёк (остриё вправо-вверх, как колышется), заменяет круглую точку
    f = [('M', [(68,18)]), ('C', [(64,32),(79,37),(79,50)]), ('C', [(79,59),(72,64),(62,64)]),
         ('C', [(53,64),(46,58),(46,50)]), ('C', [(46,42),(52,38),(57,32)]), ('C', [(62,27),(66,24),(68,18)]), ('Z', [])]
    return L, to_d(f, (1, lambda x, y: (x, y)))

# ---------- пиксельные мастера 16 px ----------
def bm(rows): return [[1 if ch == '#' else 0 for ch in r.ljust(16, '.')] for r in rows]
V5_16 = ['................','........##......','.......###......','......####......','.....#####......','....#######.....',
         '...########.....','...#########....','..##########....','..###########...','..###########...','..###########...',
         '...#########....','...########.....','....######......','................']
# выровняем: тело ровное, тупой кончик (2 px), ширина 12 по max, глаза 2x2 с зазором 2
V5_16 = ['................','........##......','.......####.....','......#####.....','.....######.....','....########....',
         '....########....','...##########...','..############..','..############..','..############..','..############..',
         '..############..','...##########...','....########....','................']
EYES16 = [(5,9),(6,9),(5,10),(6,10),(9,9),(10,9),(9,10),(10,10)]   # (x,y): 2x2 + 2x2, зазор 2 px (x=7,8)
V1_16_L = [(x,y) for x in (6,7) for y in range(5,12)] + [(x,y) for x in (8,9,10) for y in (10,11)]
V2_16_L = [(x,y) for x in (3,4,5) for y in range(1,15)] + [(x,y) for x in range(6,14) for y in (12,13,14)]
V2_16_F = [(11,3),(10,4),(11,4),(9,5),(10,5),(11,5),(8,6),(9,6),(10,6),(11,6),(8,7),(9,7),(10,7),(11,7),(8,8),(9,8),(10,8),(11,8),(9,9),(10,9)]
def pix_rects(cells, fill):
    rows = {}
    for x, y in cells: rows.setdefault(y, []).append(x)
    out = []
    for y, xs in sorted(rows.items()):
        xs.sort(); a = b = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == b + 1: b = x; continue
            out.append('<rect x="%d" y="%d" width="%d" height="1" fill="%s"/>' % (a, y, b-a+1, fill)); 
            if x is not None: a = b = x
    return ''.join(out)
def cells_of(b): return [(x, y) for y, r in enumerate(b) for x, v in enumerate(r) if v]
def drop16(): return set(cells_of(bm(V5_16)))

# ---------- SVG сборка знаков ----------
def svg(body, vb='0 0 100 100', title='LUMOSCHOOL', extra=''):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" role="img" aria-label="%s"%s><title>%s</title>%s</svg>' % (vb, title, extra, title, body)
def theme_cols(theme):
    return {'dark': dict(main=ORANGE, cut=CREAM, eye=INK, ink=CREAM, bg=DARKBG, l2=CREAM, fl=ORANGE),
            'light': dict(main=ORANGE_L, cut=CREAM, eye=INK, ink=INK, bg=CREAM, l2=INK, fl=ORANGE_L),
            'mono': dict(main='#000000', cut=None, eye=None, ink='#000000', bg=None, l2='#000000', fl='#000000')}[theme]
def mark(v, theme):
    c = theme_cols(theme); t = 'LUMOSCHOOL v%d' % v
    if v == 5:
        if theme == 'mono':   # вырезы глаз и огонька — дырами (evenodd)
            return svg('<path fill="#000" fill-rule="evenodd" d="%s%s%s"/>' % (G['drop'], G['eyes'], G['fire']), title=t)
        return svg('<path fill="%s" d="%s"/><path fill="%s" d="%s"/><path fill="%s" d="%s"/>' % (c['main'], G['drop'], c['eye'], G['eyes'], c['cut'], G['fire']), title=t)
    if v == 1:
        return svg('<path fill="%s" fill-rule="evenodd" d="%s%s"/>' % (c['main'], G['drop'], v1_L()), title=t)
    L, F = v2_parts(); s2 = '<g transform="translate(50 50) scale(1.158) translate(-52 -50)">%s</g>'
    return svg(s2 % ('<path fill="%s" d="%s"/><path fill="%s" d="%s"/>' % (c['l2'], L, c['fl'], F)), title=t)
def mark16(v, theme):
    c = theme_cols(theme); t = 'LUMOSCHOOL v%d 16px' % v; ex = ' shape-rendering="crispEdges"'
    dr = drop16()
    if v == 5:
        if theme == 'mono': return svg(pix_rects(sorted(dr - set(EYES16), key=lambda p: (p[1], p[0])), '#000'), '0 0 16 16', t, ex)
        return svg(pix_rects(sorted(dr, key=lambda p: (p[1], p[0])), c['main']) + pix_rects(sorted(EYES16, key=lambda p: (p[1], p[0])), c['eye']), '0 0 16 16', t, ex)
    if v == 1:
        return svg(pix_rects(sorted(dr - set(V1_16_L), key=lambda p: (p[1], p[0])), c['main']), '0 0 16 16', t, ex)
    return svg(pix_rects(sorted(V2_16_L, key=lambda p: (p[1], p[0])), c['l2']) + pix_rects(sorted(V2_16_F, key=lambda p: (p[1], p[0])), c['fl']), '0 0 16 16', t, ex)

# ---------- вордмарк: Golos Text 600 в контурах ----------
class Face:
    def __init__(self, wght=600):
        self.fonts = []
        for n in ('latin', 'latin-ext', 'cyrillic', 'cyrillic-ext'):
            f = TTFont('%s/golos-text-%s-wght-normal.woff2' % (FONTS, n)); f = instancer.instantiateVariableFont(f, {'wght': wght}); self.fonts.append(f)
        self.upm = self.fonts[0]['head'].unitsPerEm
    def find(self, ch):
        for f in self.fonts:
            g = f.getBestCmap().get(ord(ch))
            if g and g != '.notdef': return f, g
        return None, None
    def has(self, ch): return self.find(ch)[0] is not None
    def capheight(self):
        f, g = self.find('H'); bp = BoundsPen(f.getGlyphSet()); f.getGlyphSet()[g].draw(bp); return bp.bounds[3]
    def text_path(self, text, size, track=-0.02, x0=0, baseline=0):
        sc = size / self.upm; x = x0; d = []
        for ch in text:
            f, g = self.find(ch)
            if f is None: raise ValueError('нет глифа %r' % ch)
            gs = f.getGlyphSet(); sp = SVGPathPen(gs, ntos=fmt)
            gs[g].draw(TransformPen(sp, (sc, 0, 0, -sc, x, baseline))); d.append(sp.getCommands())
            x += gs[g].width * sc + track * size
        return ''.join(d), x - track * size - x0
FACE = Face()
TEXT = 'Lumoschool'
def wordmark(v, theme, with_mark=True):
    c = theme_cols(theme); size = 100; cap = FACE.capheight() * size / FACE.upm
    mh = 1.3 * cap                           # высота знака = 1.3 высоты заглавных
    if v == 2: mh = 1.3 * cap
    gap = (0.38 if v != 2 else 0.6) * cap; pad = 0.2 * cap
    ms = mh / 88.0                           # масштаб: знак занимает y 6..94 внутри viewBox 100
    base = pad + (mh + cap) / 2 if False else None
    # оптический центр: середина знака на середине заглавных (с подъёмом 3 % — тяжёлый низ)
    H = mh + 2 * pad; baseline = H / 2 + cap / 2 - 0.03 * cap
    mark_cy = baseline - cap / 2 + 0.0
    mw = 100 * ms if False else 56 * ms
    x = pad; parts = []
    if with_mark:
        left, right = (G['bbox'][0], G['bbox'][2]) if v != 2 else (17.6, 82.4); tx = x - left * ms; ty = mark_cy - 50 * ms - ( (G['bbox'][1] + G['bbox'][3]) / 2 - 50) * ms
        if v == 2: ty = mark_cy - 50 * ms - 0 * ms
        m = mark(v, theme)
        inner = re.search(r'</title>(.*)</svg>', m).group(1)
        parts.append('<g transform="translate(%s %s) scale(%s)">%s</g>' % (fmt(tx), fmt(ty), fmt(ms), inner))
        x += (right - left) * ms + gap
    dpath, w = FACE.text_path(TEXT, size, -0.02, x, baseline)
    parts.append('<path fill="%s" d="%s"/>' % (c['ink'], dpath))
    W = x + w + pad
    return svg(''.join(parts), '0 0 %s %s' % (fmt(W), fmt(H)), 'LUMOSCHOOL', ''), (W, H)
def text_only(theme):
    c = theme_cols(theme); size = 100; cap = FACE.capheight() * size / FACE.upm
    dpath, w = FACE.text_path(TEXT, size, -0.02, 10, 10 + cap)
    return svg('<path fill="%s" d="%s"/>' % (c['ink'], dpath), '0 0 %s %s' % (fmt(w+20), fmt(cap+20+size*0.22)), 'LUMOSCHOOL')

def write(name, s): open('%s/%s' % (D, name), 'w').write(s)
if __name__ == '__main__':
    for v in (5, 1, 2):
        for th, suf in (('dark', ''), ('light', '-onlight'), ('mono', '-mono')):
            write('lumo-v%d-mark%s.svg' % (v, suf), mark(v, th))
            write('lumo-v%d-mark16%s.svg' % (v, suf), mark16(v, th))
            write('lumo-v%d-wordmark%s.svg' % (v, suf), wordmark(v, th)[0])
    for th, suf in (('dark', ''), ('light', '-onlight'), ('mono', '-mono')):
        write('lumoschool-wordmark-text%s.svg' % suf, text_only(th))
    json.dump({k: G[k] for k in ('angle_before', 'angle_after', 'bbox')}, open(D + '/.geom.json', 'w'))
    # фавикон: мастер 16 px, цвет по теме браузера
    pix = pix_rects(sorted(drop16(), key=lambda p: (p[1], p[0])), 'ORANGE').replace('fill="ORANGE"', 'class="o"')
    eyes = pix_rects(sorted(EYES16, key=lambda p: (p[1], p[0])), 'x').replace('fill="x"', 'class="e"')
    write('favicon-v5.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><style>.o{fill:%s}.e{fill:%s}@media (prefers-color-scheme:light){.o{fill:%s}.e{fill:%s}}</style>%s%s</svg>' % (ORANGE, INK, ORANGE_L, INK, pix, eyes))
    write('favicon-v5-plate.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect width="16" height="16" rx="3" fill="%s"/><g transform="translate(0 0)">%s%s</g></svg>' % (INK, pix_rects(sorted(drop16(), key=lambda p: (p[1], p[0])), ORANGE), pix_rects(sorted(EYES16, key=lambda p: (p[1], p[0])), INK)))
    v2a = pix_rects(sorted(V2_16_L, key=lambda p: (p[1], p[0])), 'x').replace('fill="x"', 'class="l"'); v2b = pix_rects(sorted(V2_16_F, key=lambda p: (p[1], p[0])), 'x').replace('fill="x"', 'class="o"')
    write('favicon-v2.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><style>.l{fill:%s}.o{fill:%s}@media (prefers-color-scheme:light){.l{fill:%s}.o{fill:%s}}</style>%s%s</svg>' % (CREAM, ORANGE, INK, ORANGE_L, v2a, v2b))
    print('ok', G['angle_before'], G['angle_after'], G['bbox'], FACE.capheight(), FACE.upm)
