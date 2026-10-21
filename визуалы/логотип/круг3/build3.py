#!/usr/bin/env python3
"""Круг 3, ТОЛЬКО v5 (Люмо). Знак-огонь: S-силуэт, левый язычок, сердцевина от линии глаз вверх, глаза с зазором 9.4 ед.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python build3.py   (всё кодом: SVG руками + Pillow/numpy + fontTools)"""
import os, re, json, math
import numpy as np
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__))
import wordmark3 as WM

ORANGE_D, ORANGE_L, CREAM, INK, DARKBG, HEROINK = '#FF7A45', '#DF5520', '#FBEFDF', '#2A1A2E', '#1E1424', '#2A1030'
BODY_C = ORANGE_L          # один цвет тела на обеих темах: сердцевина кремовая даёт 3.39 (на #FF7A45 было 2.28)

# ---- геометрия (сетка 400x500) ----
BODY = ("M276 18C256 60 226 96 232 150C238 200 316 240 328 350C336 436 290 478 200 478C110 478 64 436 72 350"
        "C76 300 82 262 86 226C92 190 74 120 118 42C122 120 142 168 172 198"
        "C164 136 214 84 250 50C260 40 270 30 276 18Z")
CORE_BASE = ("M226 150C214 186 258 206 260 258C262 294 238 316 206 316C174 316 154 296 154 266"
             "C154 240 178 232 188 214C198 196 190 182 204 168C210 160 222 158 226 150Z")
EYE = dict(cx=(137, 263), cy=346, rx=38, ry=49)
TARGET_CORE = 0.11         # 10–12 % площади знака

def parse(d):
    toks = re.findall(r'[MCZ]|-?\d+\.?\d*', d); i = 0; segs = []
    while i < len(toks):
        t = toks[i]
        if t == 'M': segs.append(('M', [(float(toks[i+1]), float(toks[i+2]))])); i += 3
        elif t == 'C':
            n = [float(x) for x in toks[i+1:i+7]]; segs.append(('C', [(n[0], n[1]), (n[2], n[3]), (n[4], n[5])])); i += 7
        elif t == 'Z': segs.append(('Z', [])); i += 1
        else: i += 1   # неявные повторы C не используются
    return segs
def flat(segs, n=32):
    pts = []; cur = None
    for c, p in segs:
        if c == 'M': cur = p[0]; pts.append(cur)
        elif c == 'C':
            for k in range(1, n+1):
                t = k/n; a=(1-t)**3; b=3*t*(1-t)**2; cc=3*t*t*(1-t); dd=t**3
                pts.append((a*cur[0]+b*p[0][0]+cc*p[1][0]+dd*p[2][0], a*cur[1]+b*p[0][1]+cc*p[1][1]+dd*p[2][1]))
            cur = p[2]
    return pts
def area(pts): return abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts))))/2
def tf(segs, f): return [(c, [f(*q) for q in p]) for c, p in segs]
def scale_about(segs, k, cx, cy): return tf(segs, lambda x, y: (cx+(x-cx)*k, cy+(y-cy)*k))
def fmt(v): return ('%.2f' % v).rstrip('0').rstrip('.')
def to_d(segs): return ''.join(c if c=='Z' else c+' '.join('%s %s' % (fmt(x), fmt(y)) for x, y in p) for c, p in segs)

BODY_S = parse(BODY); CORE_S0 = parse(CORE_BASE)
A_BODY = area(flat(BODY_S)); 
def eye_area(): return 2*math.pi*EYE['rx']*EYE['ry']
# сердцевину масштабируем вокруг основания (205,316), пока доля = цель; низ остаётся на линии глаз
def fit_core():
    lo, hi = 0.5, 1.6
    for _ in range(40):
        k = (lo+hi)/2; a = area(flat(scale_about(CORE_S0, k, 206, 316)))/A_BODY
        if a < TARGET_CORE: lo = k
        else: hi = k
    return k
K_CORE = fit_core(); CORE_S = scale_about(CORE_S0, K_CORE, 206, 316)
A_CORE = area(flat(CORE_S))

# нормировка в viewBox 100: высота знака 88 (y 6..94), центр оси глаз x=50
_ys = [p[1] for p in flat(BODY_S)]; _xs = [p[0] for p in flat(BODY_S)]
SC = 88.0/(max(_ys)-min(_ys)); TX = 50-200*SC; TY = 6-min(_ys)*SC
def T(x, y): return (x*SC+TX, y*SC+TY)
BODY_D = to_d(tf(BODY_S, T)); CORE_D = to_d(tf(CORE_S, T))
def ell_d(cx, cy, rx, ry):
    (x1, y1), (x2, y2) = T(cx-rx, cy), T(cx+rx, cy); r1, r2 = rx*SC, ry*SC
    return 'M%s %sA%s %s 0 1 0 %s %sA%s %s 0 1 0 %s %sZ' % (fmt(x1), fmt(y1), fmt(r1), fmt(r2), fmt(x2), fmt(y2), fmt(r1), fmt(r2), fmt(x1), fmt(y1))
EYES_D = ''.join(ell_d(cx, EYE['cy'], EYE['rx'], EYE['ry']) for cx in EYE['cx'])
def hl_circles(c=CREAM):   # блик героя: круглый, ~20 % ширины глаза, вверх-вправо
    out = ''
    for cx in EYE['cx']:
        x, y = T(cx+0.32*EYE['rx'], EYE['cy']-0.36*EYE['ry']); out += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fmt(x), fmt(y), fmt(0.2*EYE['rx']*SC), c)
    return out

def svg(body, vb='0 0 100 100', title='LUMOSCHOOL Люмо', extra=''):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" role="img" aria-label="%s"%s><title>%s</title>%s</svg>' % (vb, title, extra, title, body)

# ---- знаки ----
def mark_full(theme='color', hl=True):
    if theme == 'mono':
        return svg('<path fill="#000" fill-rule="evenodd" d="%s%s%s"/>' % (BODY_D, CORE_D, EYES_D), title='Люмо (моно)')
    return svg('<path fill="%s" d="%s"/><path fill="%s" d="%s"/><path fill="%s" d="%s"/>%s' % (BODY_C, BODY_D, CREAM, CORE_D, HEROINK, EYES_D, hl_circles() if hl else ''))
def mark_simple(theme='color'):   # <=40 px: без сердцевины и бликов, тот же силуэт и глаза
    if theme == 'mono':
        return svg('<path fill="#000" fill-rule="evenodd" d="%s%s"/>' % (BODY_D, EYES_D), title='Люмо ≤40px (моно)')
    return svg('<path fill="%s" d="%s"/><path fill="%s" d="%s"/>' % (BODY_C, BODY_D, INK, EYES_D), title='Люмо ≤40px')

# ---- растр ----
def raster(segs_list, W, H, ss=8, fn=T, evenodd=True):
    """segs_list: [(segs, in_grid_coords?)] — маска оранжевого тела (в сетке 400x500 -> viewBox100 -> W,H)"""
    im = Image.new('L', (W*ss, H*ss), 0); d = ImageDraw.Draw(im)
    return im
def mask_poly(segs, W, H, ss=8, grid=True):
    im = Image.new('L', (W*ss, H*ss), 0); d = ImageDraw.Draw(im)
    pts = flat(segs); 
    pp = [((T(*p)[0])/100*W*ss, (T(*p)[1])/100*H*ss) for p in pts] if grid else pts
    d.polygon(pp, fill=255); return im
def ellipse_mask(cx, cy, rx, ry, W, H, ss=8):
    im = Image.new('L', (W*ss, H*ss), 0); d = ImageDraw.Draw(im)
    x0, y0 = T(cx-rx, cy-ry); x1, y1 = T(cx+rx, cy+ry)
    d.ellipse([x0/100*W*ss, y0/100*H*ss, x1/100*W*ss, y1/100*H*ss], fill=255); return im

def ascii16():
    """растр силуэта на сетке 16x16 (по порогу 50 %)"""
    W = H = 16; ss = 16
    m = np.array(mask_poly(BODY_S, W, H, ss)).reshape(H, ss, W, ss).mean(axis=(1, 3))/255
    return m

if __name__ == '__main__':
    m = ascii16()
    for r in m: print(''.join('#' if v > .5 else '.' for v in r))
    print('K_CORE', K_CORE, 'core/body', A_CORE/A_BODY, 'SC', SC)
