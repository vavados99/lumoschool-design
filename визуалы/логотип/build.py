#!/usr/bin/env python3
"""Генератор логотипов LUMOSCHOOL v1..v5. Запуск: /usr/local/lib/hermes-agent/venv/bin/python build.py
Текст переводится в контуры из локальных шрифтов проекта (Playfair Display / Golos Text), SVG автономны."""
import os, io
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = os.path.dirname(os.path.abspath(__file__))
FD = '/root/projects/english-school/прототипы-люмо/B5-тьма/fonts/'
CREAM, ORANGE, PLUM = '#FBEFDF', '#FF7A45', '#2A1A2E'   # палитра B5-тьма
# схемы: dark = для тёмной сцены (#1E1424), light = для светлого фона
SCHEMES = {'': (CREAM, ORANGE), '-onlight': (PLUM, ORANGE)}

_cache = {}
def font(fn, wght):
    k = (fn, wght)
    if k not in _cache:
        f = TTFont(FD + fn)
        _cache[k] = instancer.instantiateVariableFont(f, {'wght': wght})
    return _cache[k]

def fmt(v): return ('%.2f' % v).rstrip('0').rstrip('.')

def glyph_paths(fn, wght, text, size, track=0.0, x0=0.0):
    """-> (list of (d, char)), width, capheight(px). y вниз, базовая линия y=0."""
    f = font(fn, wght); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    s = size / upm; x = x0; res = []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=fmt)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        res.append((pen.getCommands(), ch))
        x += gs[g].width * s + track * size
    cap = getattr(f['OS/2'], 'sCapHeight', 0.7 * upm) * s
    return res, x - track * size, cap

def svg(vb, body, w=None, h=None, title=''):
    a = vb
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" %srole="img" aria-label="%s">'
            '<title>%s</title>%s</svg>\n') % (a, ('width="%s" height="%s" ' % (w, h)) if w else '', title, title, body)

LUMO = ("M222 22C238 42 262 98 296 150C338 218 358 292 346 360C334 430 282 478 200 478"
        "C118 478 66 430 54 360C42 292 62 218 104 154C140 100 184 66 204 38C210 28 216 20 222 22Z")
LUMO_T = 'transform="translate(21.5 4.5) scale(.2)"'   # тело Люмо (400x500) в рамку 100x100

def ell(cx, cy, rx, ry):
    return 'M%s %sa%s %s 0 1 0 %s 0a%s %s 0 1 0 %s 0Z' % (fmt(cx - rx), fmt(cy), rx, ry, fmt(2 * rx), rx, ry, fmt(-2 * rx))

# ---------- ЗНАКИ ----------
def mark1(c1, c2):   # капля Люмо с вырезом «L» (негатив), один цвет — оранж
    L = 'M126 166H200V336H284V410H126Z'
    return svg('0 0 100 100', '<path %s fill="%s" fill-rule="evenodd" d="%s%s"/>' % (LUMO_T, ORANGE, LUMO, L), title='LUMOSCHOOL v1')

def mark2(c1, c2):   # L-луч: «L» + огонёк, живущий в её углу
    return svg('0 0 100 100',
        '<path fill="%s" d="M22 10H40V70H80V88H22Z"/><circle cx="62" cy="46" r="14" fill="%s"/>' % (c1, c2), title='LUMOSCHOOL v2')

def mark3(c1, c2):   # монограмма «L» в ореоле-кольце с разрывом и искрой
    import math
    r = 42; a0, a1 = math.radians(-70), math.radians(-20)   # разрыв справа-сверху
    # дуга от a1 по часовой до a0+360
    def pt(a): return (50 + r * math.cos(a), 50 + r * math.sin(a))
    p1, p0 = pt(a1), pt(a0)
    arc = 'M%s %sA%d %d 0 1 1 %s %s' % (fmt(p1[0]), fmt(p1[1]), r, r, fmt(p0[0]), fmt(p0[1]))
    gl, w, cap = glyph_paths('playfair-display-latin-wght-normal.woff2', 800, 'L', 60)
    sx = 50 - w / 2 - 1; sy = 50 + cap / 2
    spark = pt(math.radians(-45))
    return svg('0 0 100 100',
        '<path d="%s" fill="none" stroke="%s" stroke-width="9" stroke-linecap="round"/>'
        '<circle cx="%s" cy="%s" r="5.5" fill="%s"/>'
        '<path transform="translate(%s %s)" fill="%s" d="%s"/>' % (arc, c1, fmt(spark[0]), fmt(spark[1]), c2, fmt(sx), fmt(sy), c1, gl[0][0]),
        title='LUMOSCHOOL v3')

def mark4(c1, c2):   # типографика: курсивная Playfair «L» + оранжевая точка-свет
    from fontTools.pens.boundsPen import BoundsPen
    f = font(PFI, 800); gs = f.getGlyphSet(); k = 108 / f['head'].unitsPerEm
    g = f.getBestCmap()[ord('L')]; bp = BoundsPen(gs); gs[g].draw(bp); x0, y0, x1, y1 = bp.bounds
    r = 10; gap = 5
    total = (x1 - x0) * k + gap + 2 * r
    ox = 50 - total / 2 - x0 * k; base = 50 + (y1 + y0) * k / 2
    gl, w, cap = glyph_paths(PFI, 800, 'L', 108)
    dot = '<circle cx="%s" cy="%s" r="%d" fill="%s"/>' % (fmt(ox + x1 * k + gap + r), fmt(base - r - 1), r, c2)
    return svg('0 0 100 100', '<path transform="translate(%s %s)" fill="%s" d="%s"/>%s' % (fmt(ox), fmt(base), c1, gl[0][0], dot), title='LUMOSCHOOL v4')

def mark5(c1, c2):   # силуэт Люмо: оранжевое тело + два крупных глаза
    eyes = '<path %s fill="%s" d="%s%s"/>' % (LUMO_T, c1, ell(148, 312, 36, 46), ell(252, 312, 36, 46))
    return svg('0 0 100 100', '<path %s fill="%s" d="%s"/>%s' % (LUMO_T, ORANGE, LUMO, eyes), title='LUMOSCHOOL v5')

# ---------- ВОРДМАРКИ ----------
PF = 'playfair-display-latin-wght-normal.woff2'
PFI = 'playfair-display-latin-wght-italic.woff2'
GOLOS = 'golos-text-latin-wght-normal.woff2'
PF = 'playfair-display-latin-wght-normal.woff2'
PFI = 'playfair-display-latin-wght-italic.woff2'

def wordmark(fn, wght, text, size, track, c1, c2, accent=None, title=''):
    gl, w, cap = glyph_paths(fn, wght, text, size, track)
    pad = size * .15
    body = ''
    for i, (d, ch) in enumerate(gl):
        col = c2 if accent and accent(i, ch) else c1
        body += '<path fill="%s" d="%s"/>' % (col, d)
    # снизу запас под нижние выносы/округления
    top = -cap - pad; hh = cap + 2 * pad + size * .02
    return svg('%s %s %s %s' % (fmt(-pad), fmt(top), fmt(w + 2 * pad), fmt(hh)), '<g>%s</g>' % body, title=title), (w + 2 * pad, hh)

def word1(c1, c2): return wordmark(GOLOS, 600, 'LUMOSCHOOL', 100, .16, c1, c2, lambda i, ch: i == 3, 'LUMOSCHOOL')   # O оранжевая
def word2(c1, c2): return wordmark(PF, 600, 'Lumoschool', 100, .005, c1, c2, lambda i, ch: i == 0, 'Lumoschool')
def word3(c1, c2): return wordmark(PF, 500, 'LUMOSCHOOL', 100, .12, c1, c2, None, 'LUMOSCHOOL')
def word4(c1, c2): return wordmark(PFI, 700, 'Lumoschool', 100, .0, c1, c2, lambda i, ch: i == 0, 'Lumoschool')
def word5(c1, c2): return wordmark(GOLOS, 700, 'Lumoschool', 100, .01, c1, c2, lambda i, ch: i == 0, 'Lumoschool')

MARKS = {1: mark1, 2: mark2, 3: mark3, 4: mark4, 5: mark5}
WORDS = {1: word1, 2: word2, 3: word3, 4: word4, 5: word5}

if __name__ == '__main__':
    for n in range(1, 6):
        for suf, (c1, c2) in SCHEMES.items():
            open('%s/lumo-v%d-mark%s.svg' % (OUT, n, suf), 'w').write(MARKS[n](c1, c2))
            s, _ = WORDS[n](c1, c2)
            open('%s/lumo-v%d-wordmark%s.svg' % (OUT, n, suf), 'w').write(s)
    print('ok')
