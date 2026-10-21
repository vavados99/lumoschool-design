#!/usr/bin/env python3
"""Круг 7, логотип: глаза тёмной версии #4A1A0E; левый язык ниже на ~18 % высоты знака; ≤56 px — один язык; глаза фавикона на 1 клетку выше.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python make7.py  (файлы lumo-v5r7-*, favicon-v5r7.svg, r7-favicon-*.png; r6 не трогаем)"""
import os, re
from PIL import Image
import build3 as B, wordmark3 as WM, make3 as M, make4 as M4
D = B.D
def W(n, s): open(os.path.join(D, n), 'w').write(s)
CORE7 = '#F6B85F'; EYE_DK7 = '#4A1A0E'; EYE_LT7 = B.INK
SAFE = 6
def safe(s): return s.replace('viewBox="0 0 100 100"', 'viewBox="-%d -%d %d %d"' % (SAFE, SAFE, 100+2*SAFE, 100+2*SAFE), 1)
# геометрия 400x500. Левый язык: кончик был y=42, стал y=122 (80 ед. из 460 высоты знака = 17 %).
BODY2 = ("M276 18C256 60 226 96 232 150C238 200 316 240 328 350C336 436 290 478 200 478C110 478 64 436 72 350"
         "C76 300 82 262 86 226C90 202 82 170 118 122C122 164 142 186 172 198"
         "C164 136 214 84 250 50C260 40 270 30 276 18Z")
# один язык (≤56 px): левый плечо плавно уходит в внутренний край правого языка
BODY1 = ("M276 18C256 60 226 96 232 150C238 200 316 240 328 350C336 436 290 478 200 478C110 478 64 436 72 350"
         "C76 300 82 262 86 226C92 176 140 150 190 112C214 92 236 70 250 50C260 40 270 30 276 18Z")
def d(body): return B.to_d(B.tf(B.parse(body), B.T))
B2, B1 = d(BODY2), d(BODY1)
def eye(theme): return EYE_DK7 if theme == 'dark' else EYE_LT7
def body_col(theme): return B.ORANGE_D if theme == 'dark' else B.ORANGE_L
def core(theme): return B.CREAM if theme == 'dark' else CORE7
def full(theme):
    if theme == 'mono': return B.svg('<path fill="#000" fill-rule="evenodd" d="%s%s%s"/>' % (B2, B.CORE_D, B.EYES_D), title='Люмо (моно)')
    return B.svg('<path fill="%s" d="%s"/><path fill="%s" d="%s"/><path fill="%s" d="%s"/>%s' % (
        B.ORANGE_L if theme == 'light' else B.ORANGE_L, B2, core(theme), B.CORE_D, eye(theme), B.EYES_D, B.hl_circles(core(theme))))
def simple(theme):
    if theme == 'mono': return B.svg('<path fill="#000" fill-rule="evenodd" d="%s%s"/>' % (B1, B.EYES_D), title='Люмо (моно)')
    return B.svg('<path fill="%s" d="%s"/><path fill="%s" d="%s"/>' % (body_col(theme), B1, eye(theme), B.EYES_D), title='Люмо ≤56px')
def lockup(kind, theme):
    size = 100; cap = WM.capheight()*size/WM.UPM; mh = (1.5 if kind == 'full' else M4.MH_K)*cap
    gap = M.GAP_K*cap; pad = .2*cap; padR = .4*cap
    bp = WM.BoundsPen(WM.GS); WM.GS[WM.CMAP[ord('L')]].draw(bp); lsb = bp.bounds[0]*size/WM.UPM
    H = mh+2*pad; baseline = pad+mh-M4.OVERSHOOT*cap
    ink = {'dark': B.CREAM, 'light': B.INK, 'mono': '#000'}[theme]
    m = simple(theme) if kind == 'simple' else full(theme)
    inner = re.search(r'</title>(.*)</svg>', m).group(1)
    ms = mh/88.0; l = B.T(min(p[0] for p in B.flat(B.BODY_S)), 0)[0]; r = B.T(max(p[0] for p in B.flat(B.BODY_S)), 0)[0]
    x = pad; parts = ['<g transform="translate(%s %s) scale(%s)">%s</g>' % (B.fmt(x-l*ms), B.fmt(pad-6*ms), B.fmt(ms), inner)]
    x += (r-l)*ms+gap-lsb
    parts.append('<path fill="%s" d="%s"/>' % (ink, WM.path_d(M.XS, size, x, baseline)))
    Wd = x+M.TOTAL*size/WM.UPM+padR
    return B.svg(''.join(parts), '0 0 %s %s' % (B.fmt(Wd), B.fmt(H)), 'LUMOSCHOOL')
# фавикон: глаза на 1 клетку выше (y 8,9 вместо 9,10)
EYES = {(x, y) for x in (4, 5, 10, 11) for y in (8, 9)}
CELLS = M.CELLS16
def col16(theme): return B.ORANGE_D if theme == 'dark' else M.FAV_L
def mark16(theme):
    if theme == 'mono': return B.svg(M.rects(CELLS-EYES, '#000'), '0 0 16 16', 'Люмо 16px (моно)', ' shape-rendering="crispEdges"')
    return B.svg(M.rects(CELLS-EYES, col16(theme))+M.rects(EYES, eye(theme)), '0 0 16 16', 'Люмо 16px', ' shape-rendering="crispEdges"')
def fav_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges"><style>.o{fill:%s}.e{fill:%s}@media (prefers-color-scheme:light){.o{fill:%s}.e{fill:%s}}</style>%s%s</svg>'
            % (B.ORANGE_D, EYE_DK7, M.FAV_L, EYE_LT7, M.rects(CELLS-EYES, cls='o'), M.rects(EYES, cls='e')))
def px16(theme, bg):
    im = Image.new('RGBA', (16, 16), M.rgb(bg)); p = im.load()
    for x, y in CELLS: p[x, y] = M.rgb(eye(theme)) if (x, y) in EYES else M.rgb(col16(theme))
    return im
def avatar(small):
    s = open(os.path.join(D, 'lumo-v5r3-avatar%s.svg' % ('-small' if small else ''))).read()
    inner = re.search(r'</title>(.*)</svg>', simple('dark') if small else full('dark')).group(1)
    glow = '<defs><radialGradient id="g" cx="50%" cy="60%" r="48%"><stop offset="0" stop-color="#FF7A45" stop-opacity=".2"/><stop offset="1" stop-color="#FF7A45" stop-opacity="0"/></radialGradient></defs>'
    return B.svg('%s<rect width="100" height="100" fill="%s"/><rect width="100" height="100" fill="url(#g)"/><g transform="translate(11 12) scale(.78)">%s</g>' % (glow, B.DARKBG, inner), title='Люмо аватар')
def avatar_light(small):
    inner = re.search(r'</title>(.*)</svg>', simple('light') if small else full('light')).group(1)
    return B.svg('<rect width="100" height="100" fill="%s"/><g transform="translate(11 12) scale(.78)">%s</g>' % (B.CREAM, inner), title='Люмо аватар (светлый)')
def build():
    for th, suf in (('dark', ''), ('light', '-onlight'), ('mono', '-mono')):
        W('lumo-v5r7-mark%s.svg' % suf, safe(full(th)))
        W('lumo-v5r7-mark-simple%s.svg' % suf, safe(simple(th)))
        W('lumo-v5r7-mark16%s.svg' % suf, mark16(th))
        W('lumo-v5r7-wordmark%s.svg' % suf, lockup('full', th))
        W('lumo-v5r7-wordmark-small%s.svg' % suf, lockup('simple', th))
    W('lumo-v5r7-avatar.svg', avatar(False)); W('lumo-v5r7-avatar-small.svg', avatar(True))
    W('lumo-v5r7-avatar-onlight.svg', avatar_light(False)); W('lumo-v5r7-avatar-small-onlight.svg', avatar_light(True))
    W('favicon-v5r7.svg', fav_svg())
    for th, bg in (('dark', '#1E1424'), ('light', '#FBEFDF')):
        for s in (16, 32, 64): px16(th, bg).resize((s, s), Image.NEAREST).save(D+'/r7-favicon-%d-%s.png' % (s, th))
if __name__ == '__main__': build(); print('ok')
