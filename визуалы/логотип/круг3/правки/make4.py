#!/usr/bin/env python3
"""Круг 4, логотип (правки по разбору Опуса): знак на базовой линии, сердцевина #FFE3B8 на светлом, глаза фавикона выше и шире.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python make4.py  (файлы lumo-v5r4-*, r4-*.png)"""
import os, re
from PIL import Image
import build3 as B, wordmark3 as WM, make3 as M
D = B.D
def W(n, s): open(os.path.join(D, n), 'w').write(s)
CORE_LIGHT = '#FFE3B8'
OVERSHOOT = 0.02      # низ знака ниже базовой линии, доли заглавной (лимит 0.03)
MH_K = 1.35           # высота знака в заглавных

def core_for(theme): return CORE_LIGHT if theme == 'light' else B.CREAM
def mark_full(theme):
    if theme == 'mono': return B.mark_full('mono')
    return B.svg('<path fill="%s" d="%s"/><path fill="%s" d="%s"/><path fill="%s" d="%s"/>%s' % (
        B.ORANGE_L if theme == 'light' else B.ORANGE_L, B.BODY_D, core_for(theme), B.CORE_D, B.HEROINK, B.EYES_D, B.hl_circles(core_for(theme))))
def lockup(kind, theme, text_only=False):
    size = 100; cap = WM.capheight()*size/WM.UPM; mh = (1.5 if kind == 'full' else MH_K)*cap if kind != 'x' else 0
    gap = M.GAP_K*cap; pad = .2*cap; padR = .4*cap
    bp = WM.BoundsPen(WM.GS); WM.GS[WM.CMAP[ord('L')]].draw(bp); lsb = bp.bounds[0]*size/WM.UPM
    H = mh+2*pad; baseline = pad+mh-OVERSHOOT*cap     # низ знака = базовая линия + 2 % cap
    if text_only: H = cap+2*pad; baseline = pad+cap
    ink = {'dark': B.CREAM, 'light': B.INK, 'mono': '#000'}[theme]
    parts = []; x = pad
    if not text_only:
        m = (M.mark_simple(theme) if kind == 'simple' else mark_full(theme))
        inner = re.search(r'</title>(.*)</svg>', m).group(1)
        ms = mh/88.0; l = B.T(min(p[0] for p in B.flat(B.BODY_S)), 0)[0]; r = B.T(max(p[0] for p in B.flat(B.BODY_S)), 0)[0]
        parts.append('<g transform="translate(%s %s) scale(%s)">%s</g>' % (B.fmt(x-l*ms), B.fmt(pad-6*ms), B.fmt(ms), inner)); x += (r-l)*ms+gap-lsb
    parts.append('<path fill="%s" d="%s"/>' % (ink, WM.path_d(M.XS, size, x, baseline)))
    Wd = x+M.TOTAL*size/WM.UPM+padR
    return B.svg(''.join(parts), '0 0 %s %s' % (B.fmt(Wd), B.fmt(H)), 'LUMOSCHOOL'), (Wd, H)

# фавикон 16: глаза на 1 px выше и шире (были x 5,6,9,10 / y 9–11 → x 4,5,10,11 / y 8–10)
EYES16 = {(x, y) for x in (4, 5, 10, 11) for y in (8, 9, 10)}
M16 = M.M16
CELLS = M.CELLS16
EYE_DK, EYE_LT = M.EYE16_DK, B.INK
def mark16(theme):
    if theme == 'mono': return B.svg(M.rects(CELLS-EYES16, '#000'), '0 0 16 16', 'Люмо 16px (моно)', ' shape-rendering="crispEdges"')
    col = B.ORANGE_D if theme == 'dark' else M.FAV_L
    return B.svg(M.rects(CELLS-EYES16, col)+M.rects(EYES16, EYE_DK if theme == 'dark' else EYE_LT), '0 0 16 16', 'Люмо 16px', ' shape-rendering="crispEdges"')
def fav_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><style>.o{fill:%s}.e{fill:%s}@media (prefers-color-scheme:light){.o{fill:%s}.e{fill:%s}}</style>%s%s</svg>'
            % (B.ORANGE_D, EYE_DK, M.FAV_L, B.INK, M.rects(CELLS-EYES16, cls='o'), M.rects(EYES16, cls='e')))
def px16(theme, bg):
    col = B.ORANGE_D if theme == 'dark' else M.FAV_L; eye = EYE_DK if theme == 'dark' else EYE_LT
    im = Image.new('RGBA', (16, 16), M.rgb(bg)); p = im.load()
    for x, y in CELLS: p[x, y] = M.rgb(eye) if (x, y) in EYES16 else M.rgb(col)
    return im
BGS = {'dark': '#1E1424', 'light': '#FBEFDF'}
def build():
    for th, suf in (('dark', ''), ('light', '-onlight'), ('mono', '-mono')):
        W('lumo-v5r4-mark%s.svg' % suf, mark_full(th))
        W('lumo-v5r4-mark-simple%s.svg' % suf, M.mark_simple(th))
        W('lumo-v5r4-mark16%s.svg' % suf, mark16(th))
        W('lumo-v5r4-wordmark%s.svg' % suf, lockup('full', th)[0])
        W('lumo-v5r4-wordmark-small%s.svg' % suf, lockup('simple', th)[0])
    W('favicon-v5r4.svg', fav_svg())
    for th in ('dark', 'light'):
        for s in (16, 32, 64):
            px16(th, BGS[th]).resize((s, s), Image.NEAREST).save(D+'/r4-favicon-%d-%s.png' % (s, th))
if __name__ == '__main__': build(); print('ok')
