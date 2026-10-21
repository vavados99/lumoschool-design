#!/usr/bin/env python3
"""Круг 3: сборка файлов, замеры, листы. /usr/local/lib/hermes-agent/venv/bin/python make3.py"""
import os, json, math, re
import numpy as np
from PIL import Image, ImageDraw
import build3 as B
import wordmark3 as WM
D = B.D
def W(name, s): open(os.path.join(D, name), 'w').write(s)

def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    c = [x/12.92 if x <= .03928 else ((x+.055)/1.055)**2.4 for x in c]; return .2126*c[0]+.7152*c[1]+.0722*c[2]
def cr(a, b):
    la, lb = lum(a), lum(b); return round((max(la, lb)+.05)/(min(la, lb)+.05), 2)

def mark_simple(theme):
    if theme == 'mono': return B.mark_simple('mono')
    col = B.ORANGE_D if theme == 'dark' else B.ORANGE_L
    return B.svg('<path fill="%s" d="%s"/><path fill="%s" d="%s"/>' % (col, B.BODY_D, B.INK, B.EYES_D), title='Люмо ≤40px')

FAV_L = '#D24C16'   # светлая вкладка Chrome #DEE1E6: #DF5520 давал 2.93, этот >=3
M16 = ['................',
       '.........##.....',
       '........###.....',
       '.......####.....',
       '....#.#####.....',
       '...########.....',
       '..#########.....',
       '..##########....',
       '..###########...',
       '..############..',
       '..############..',
       '..############..',
       '..############..',
       '...##########...',
       '....########....',
       '................']
EYES16 = {(x, y) for x in (5, 6, 9, 10) for y in (9, 10, 11)}
assert len(M16) == 16 and all(len(r) == 16 for r in M16)
CELLS16 = {(x, y) for y, r in enumerate(M16) for x, ch in enumerate(r) if ch == '#'}
def rects(cells, fill=None, cls=None):
    rows = {}
    for x, y in cells: rows.setdefault(y, []).append(x)
    out = []
    for y, xs in sorted(rows.items()):
        xs.sort(); a = b = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == b+1: b = x; continue
            attr = ('fill="%s"' % fill) if fill else ('class="%s"' % cls)
            out.append('<rect x="%d" y="%d" width="%d" height="1" %s/>' % (a, y, b-a+1, attr))
            if x is not None: a = b = x
    return ''.join(out)
def mark16(theme):
    if theme == 'mono': return B.svg(rects(CELLS16-EYES16, '#000'), '0 0 16 16', 'Люмо 16px (моно)', ' shape-rendering="crispEdges"')
    col = B.ORANGE_D if theme == 'dark' else FAV_L
    return B.svg(rects(CELLS16-EYES16, col)+rects(EYES16, B.INK), '0 0 16 16', 'Люмо 16px', ' shape-rendering="crispEdges"')
def favicon_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><style>.o{fill:%s}.e{fill:%s}@media (prefers-color-scheme:light){.o{fill:%s}}</style>%s%s</svg>'
            % (B.ORANGE_D, B.INK, FAV_L, rects(CELLS16-EYES16, cls='o'), rects(EYES16, cls='e')))
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))+(255,)
def png16(theme, scale=1):
    col = B.ORANGE_D if theme == 'dark' else FAV_L
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); px = im.load()
    for x, y in CELLS16: px[x, y] = rgb(B.INK) if (x, y) in EYES16 else rgb(col)
    return im.resize((16*scale, 16*scale), Image.NEAREST) if scale > 1 else im

KP, RAW = WM.kern_pairs()
XS, TOTAL = WM.positions(KP, WM.MANUAL)
def lockup(mark_kind, theme, mh_k=1.3, text_only=False):
    size = 100; cap = WM.capheight()*size/WM.UPM; mh = (1.5 if mark_kind == 'full' else mh_k)*cap; gap = .38*cap; pad = .2*cap; padR = .4*cap
    H = mh+2*pad; baseline = pad+mh-.06*cap          # знак «стоит» на строке: низ брюшка на 0.06 cap ниже базовой линии
    if text_only: H = cap+2*pad; baseline = pad+cap
    cy = baseline-cap/2
    ink = {'dark': B.CREAM, 'light': B.INK, 'mono': '#000'}[theme]
    parts = []; x = pad
    if not text_only:
        m = mark_simple(theme) if mark_kind == 'simple' else (B.mark_full('mono') if theme == 'mono' else B.mark_full())
        inner = re.search(r'</title>(.*)</svg>', m).group(1)
        ms = mh/88.0; l = B.T(min(p[0] for p in B.flat(B.BODY_S)), 0)[0]; r = B.T(max(p[0] for p in B.flat(B.BODY_S)), 0)[0]
        tx = x-l*ms; ty = pad-6*ms
        parts.append('<g transform="translate(%s %s) scale(%s)">%s</g>' % (B.fmt(tx), B.fmt(ty), B.fmt(ms), inner)); x += (r-l)*ms+gap
    parts.append('<path fill="%s" d="%s"/>' % (ink, WM.path_d(XS, size, x, baseline)))
    Wd = x+TOTAL*size/WM.UPM+padR
    return B.svg(''.join(parts), '0 0 %s %s' % (B.fmt(Wd), B.fmt(H)), 'LUMOSCHOOL'), (Wd, H)

def avatar_svg(small=False):
    glow = '<defs><radialGradient id="g" cx="50%" cy="60%" r="48%"><stop offset="0" stop-color="#FF7A45" stop-opacity=".2"/><stop offset="1" stop-color="#FF7A45" stop-opacity="0"/></radialGradient></defs>'
    inner = re.search(r'</title>(.*)</svg>', mark_simple('dark') if small else B.mark_full()).group(1)
    return B.svg('%s<rect width="100" height="100" fill="%s"/><rect width="100" height="100" fill="url(#g)"/><g transform="translate(11 12) scale(.78)">%s</g>' % (glow, B.DARKBG, inner), title='Люмо аватар')

def build_files():
    for th, suf in (('dark', ''), ('light', '-onlight'), ('mono', '-mono')):
        W('lumo-v5r3-mark%s.svg' % suf, B.mark_full('mono') if th == 'mono' else B.mark_full())
        W('lumo-v5r3-mark-simple%s.svg' % suf, mark_simple(th))
        W('lumo-v5r3-mark16%s.svg' % suf, mark16(th))
        W('lumo-v5r3-wordmark%s.svg' % suf, lockup('full', th)[0])
        W('lumo-v5r3-wordmark-small%s.svg' % suf, lockup('simple', th)[0])
        W('lumoschool-r3-wordmark-text%s.svg' % suf, lockup('x', th, text_only=True)[0])
    W('favicon-v5r3.svg', favicon_svg())
    for th in ('dark', 'light'):
        png16(th).save(D+'/favicon-v5r3-16-%s.png' % th); png16(th, 2).save(D+'/favicon-v5r3-32px-%s.png' % th)
    W('lumo-v5r3-avatar.svg', avatar_svg()); W('lumo-v5r3-avatar-small.svg', avatar_svg(True))

if __name__ == '__main__':
    print('kern', KP); build_files(); print('files ok')
