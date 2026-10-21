#!/usr/bin/env python3
"""Круг 6, логотип: сердцевина #F2A444 (≥1.5:1 к #FBEFDF), глаза тёмной версии как в светлой (#2A1A2E), глаза фавикона 2×2, safe area в SVG знака.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python make6.py  (файлы lumo-v5r6-*, favicon-v5r6.svg, r6-favicon-*.png)"""
import os, re
from PIL import Image
import build3 as B, make3 as M, make4 as M4
D = B.D
def W(n, s): open(os.path.join(D, n), 'w').write(s)
CORE6 = '#F6B85F'
M4.CORE_LIGHT = CORE6
SAFE = 6   # safe area: 6 % с каждой стороны (viewBox -6 -6 112 112)
def safe(s): return s.replace('viewBox="0 0 100 100"', 'viewBox="-%d -%d %d %d"' % (SAFE, SAFE, 100+2*SAFE, 100+2*SAFE), 1)
# глаза 2×2: x 4,5 | 10,11; y 9,10
EYES = {(x, y) for x in (4, 5, 10, 11) for y in (9, 10)}
CELLS = M.CELLS16
EYE_C = B.INK   # одинаковый тёмный глаз в обеих темах
def col(theme): return B.ORANGE_D if theme == 'dark' else M.FAV_L
def mark16(theme):
    if theme == 'mono': return B.svg(M.rects(CELLS-EYES, '#000'), '0 0 16 16', 'Люмо 16px (моно)', ' shape-rendering="crispEdges"')
    return B.svg(M.rects(CELLS-EYES, col(theme))+M.rects(EYES, EYE_C), '0 0 16 16', 'Люмо 16px', ' shape-rendering="crispEdges"')
def fav_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><style>.o{fill:%s}.e{fill:%s}@media (prefers-color-scheme:light){.o{fill:%s}}</style>%s%s</svg>'
            % (B.ORANGE_D, EYE_C, M.FAV_L, M.rects(CELLS-EYES, cls='o'), M.rects(EYES, cls='e')))
def px16(theme, bg):
    im = Image.new('RGBA', (16, 16), M.rgb(bg)); p = im.load()
    for x, y in CELLS: p[x, y] = M.rgb(EYE_C) if (x, y) in EYES else M.rgb(col(theme))
    return im
def build():
    for th, suf in (('dark', ''), ('light', '-onlight'), ('mono', '-mono')):
        W('lumo-v5r6-mark%s.svg' % suf, safe(M4.mark_full(th)))
        W('lumo-v5r6-mark-simple%s.svg' % suf, safe(M.mark_simple(th)))
        W('lumo-v5r6-mark16%s.svg' % suf, mark16(th))
        W('lumo-v5r6-wordmark%s.svg' % suf, M4.lockup('full', th)[0])
        W('lumo-v5r6-wordmark-small%s.svg' % suf, M4.lockup('simple', th)[0])
    for a in ('avatar', 'avatar-small'):   # аватары: берём r4 как есть, меняем цвет сердцевины
        s = open(os.path.join(D, 'lumo-v5r4-%s.svg' % a)).read()
        W('lumo-v5r6-%s.svg' % a, s.replace('#FFE3B8', CORE6))
    W('favicon-v5r6.svg', fav_svg())
    for th, bg in (('dark', '#1E1424'), ('light', '#FBEFDF')):
        for s in (16, 32, 64): px16(th, bg).resize((s, s), Image.NEAREST).save(D+'/r6-favicon-%d-%s.png' % (s, th))
if __name__ == '__main__': build(); print('ok')
