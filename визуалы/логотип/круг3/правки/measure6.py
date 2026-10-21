#!/usr/bin/env python3
"""Замеры круга 6 -> замеры-круг6.txt (WCAG)."""
import os, io, numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); out = []
def P(s=''): print(s); out.append(s)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def lum(c):
    v = [x/255 for x in c[:3]]; v = [x/12.92 if x <= .03928 else ((x+.055)/1.055)**2.4 for x in v]; return .2126*v[0]+.7152*v[1]+.0722*v[2]
def cr(a, b): a, b = lum(a), lum(b); return (max(a, b)+.05)/(min(a, b)+.05)
BG = {'light': '#FBEFDF', 'dark': '#1E1424'}
def render(pg, fn, px, bg):
    pg.set_viewport_size({'width': px, 'height': px})
    open('/root/.hermes/cache/scratch/m6.html','w').write('<body style="margin:0;background:%s"><img src="file://%s" style="width:%dpx;height:%dpx;display:block"></body>' % (bg, os.path.join(D, fn), px, px)); pg.goto('file:///root/.hermes/cache/scratch/m6.html'); pg.wait_for_timeout(200)
    return np.array(Image.open(io.BytesIO(pg.screenshot())).convert('RGB')).astype(int)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    P('=== 1. Сердцевина (WCAG 2.x), цвет %s ===' % '#F6B85F')
    for nm, c in (('r4 #FFE3B8', '#FFE3B8'), ('r6 #F6B85F', '#F6B85F')):
        P(' %s: к фону #FBEFDF %.2f:1 | к телу #DF5520 %.2f:1 | к глазам #2A1030 %.2f:1' % (nm, cr(hx(c), hx('#FBEFDF')), cr(hx(c), hx('#DF5520')), cr(hx(c), hx('#2A1030'))))
    P(' цель ≥1.5:1 к фону: %s' % ('ВЫПОЛНЕНА' if cr(hx('#F6B85F'), hx('#FBEFDF')) >= 1.5 else 'НЕ выполнена'))
    P(' пиксельный замер (рендер lumo-v5r6-mark-onlight.svg 400 px на #FBEFDF; точка в сердцевине (51,50) в viewBox -6..106):')
    im = render(pg, 'lumo-v5r6-mark-onlight.svg', 400, BG['light']); k = 400/112
    core = tuple(int(v) for v in im[int((50+6)*k), int((51+6)*k)]); body = tuple(int(v) for v in im[int((80+6)*k), int((50+6)*k)])
    P('   сердцевина %s к фону %.2f:1; тело %s к фону %.2f:1; сердцевина к телу %.2f:1' % (core, cr(core, hx(BG['light'])), body, cr(body, hx(BG['light'])), cr(core, body)))
    P(' тёмная версия: сердцевина #FBEFDF на тёле #DF5520 = %.2f:1; тело к фону #1E1424 = %.2f:1' % (cr(hx('#FBEFDF'), hx('#DF5520')), cr(hx('#DF5520'), hx('#1E1424'))))
    P('')
    P('=== 2. Глаза: цвет и контраст к телу (16 px фавикон) ===')
    P(' r4 тёмная: #5B3351 к телу #FF7A45 = %.2f:1 (было) → r6 тёмная: #2A1A2E к телу #FF7A45 = %.2f:1; светлая: #2A1A2E к телу #D24C16 = %.2f:1' % (cr(hx('#5B3351'), hx('#FF7A45')), cr(hx('#2A1A2E'), hx('#FF7A45')), cr(hx('#2A1A2E'), hx('#D24C16'))))
    P(' цвет глаз теперь одинаковый в обеих версиях: #2A1A2E (в полном знаке тёмной темы был #2A1030 — как и в светлой)')
    for th in ('dark', 'light'):
        for s in (16, 32, 64):
            a = np.array(Image.open(os.path.join(D, 'r6-favicon-%d-%s.png' % (s, th))).convert('RGB')).astype(int); kk = s//16
            eye = a[9*kk+kk//2, 4*kk+kk//2]; body = a[12*kk, 8*kk]
            # размер глаза в px: связная область цвета глаза
            m = (np.abs(a-eye).sum(2) < 6); ys, xs = np.where(m[:, :s//2])
            P(' r6-favicon-%d-%s.png: глаз %s; к телу %.2f:1; к фону %.2f:1; пятно глаза %d×%d px (клеток 2×2)' % (s, th, tuple(int(v) for v in eye), cr(eye, body), cr(eye, hx(BG[th])), xs.max()-xs.min()+1, ys.max()-ys.min()+1))
    P(' глаза: 2×2 клетки в сетке 16×16 = 2×2 px при 16 px, 4×4 при 32, 8×8 при 64; между глазами 4 клетки; x 4,5 | 10,11; y 9,10')
    P(' к тёмной вкладке Chrome #35363A глаза в теле, не на краю: пара, которая важна — глаз/тело (выше), не глаз/вкладка')
    P('')
    P('=== 3. Safe area в SVG (viewBox знака) ===')
    for fn in ('lumo-v5r6-mark.svg', 'lumo-v5r6-mark-onlight.svg', 'lumo-v5r6-mark-simple.svg'):
        im = render(pg, fn, 560, '#FF00FF'); m = (np.abs(im-np.array(hx('#FF00FF'))).sum(2) > 40); ys, xs = np.where(m)
        P(' %s: viewBox -6 -6 112 112; отступ слева %.1f %% / справа %.1f %% / сверху %.1f %% / снизу %.1f %% от стороны (пусто вокруг чернил)' % (fn, 100*xs.min()/560, 100*(559-xs.max())/560, 100*ys.min()/560, 100*(559-ys.max())/560))
    P(' примечание: у знака отступ у файла = 6 % + собственное поле вокруг контура; у lockup-файлов (wordmark*) отступ 0.2 cap слева/сверху/снизу, 0.4 cap справа — как в r4, не менялся')
    b.close()
open(os.path.join(D, 'замеры-круг6.txt'), 'w').write('\n'.join(out)+'\n')
