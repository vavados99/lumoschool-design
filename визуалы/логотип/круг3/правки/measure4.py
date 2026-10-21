#!/usr/bin/env python3
"""Замеры круга 4 -> замеры-круг4.txt. Запуск: /usr/local/lib/hermes-agent/venv/bin/python measure4.py"""
import os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'measure_pravki.py')).read().split('with sync_playwright() as p:')[0]
exec(src)
import re
def px_at(im, x, y): return tuple(int(v) for v in im[y, x])
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 600})
    P('=== 1. Низ знака относительно базовой линии (лимит ≤ 3 % высоты заглавной) ===')
    P('круг3-правки (было, замер до исправления) → круг4 (стало); px при device scale 1')
    rows = [('wordmark-small', 'wordmark-small.svg', 'dark', [61, 43, 40, 150]), ('wordmark-small-onlight', 'wordmark-small-onlight.svg', 'light', [61, 43]), ('wordmark полный знак', 'wordmark.svg', 'dark', [150, 96]), ('wordmark полный знак onlight', 'wordmark-onlight.svg', 'light', [150])]
    worst = 0
    for name, fn, th, hs in rows:
        for h in hs:
            for tag, fname in (('r3p', 'lumo-v5r3-'+fn), ('r4 ', 'lumo-v5r4-'+fn)):
                m = lockup_metrics(pg, os.path.join(D, fname), h, th)
                pct = 100*m['below_base']/m['cap']
                if tag == 'r4 ': worst = max(worst, m['below_base']/m['cap'])
                P(f' {name:30s} {tag} lock_h={h:3d}: cap {m["cap"]:3d}px; знак {m["mark_h"]}px; низ знака vs базовая {m["below_base"]:+d}px = {pct:+.1f} % cap; верх знака vs верх заглавной {m["top_vs_cap"]:+d}px; зазор {m["gap"]}px = {m["gap"]/m["cap"]:.2f} cap')
    P(f' ИТОГ r4 (целые px, грубо): макс. {100*worst:.1f} % cap')
    # точный (вектор): вынос = OVERSHOOT
    P(' точный замер (рендер крупно, lock_h=800, квантование <0.3 %):')
    for fn, th in (('wordmark-small', 'dark'), ('wordmark-small-onlight', 'light'), ('wordmark', 'dark'), ('wordmark-onlight', 'light')):
        m = lockup_metrics(pg, os.path.join(D, 'lumo-v5r4-'+fn+'.svg'), 800, th)
        P(f'   {fn:24s} cap {m["cap"]}px; низ знака vs базовая {m["below_base"]:+d}px = {100*m["below_base"]/m["cap"]:+.1f} % cap')
    P(' в построении SVG: вынос = 2.0 % cap (OVERSHOOT=0.02 в make4.py). На мелких px сглаживание края даёт +1 px.')
    P('')
    P('=== 2. Сердцевина на светлом #FBEFDF ===')
    for tag, fn in (('r3 #FBEFDF (=фон)', 'lumo-v5r3-mark-onlight.svg'), ('r4 #FFE3B8', 'lumo-v5r4-mark-onlight.svg')):
        im = render(pg, os.path.join(D, fn), 110, BG['light']); H, Wd, _ = im.shape
        cx, cy = int(Wd*.5), int(H*.5)   # центр сердцевины ≈ (51,50) в viewBox 100
        core = im[int(H*.50), int(Wd*.51)]; body = im[int(H*.80), int(Wd*.50)] ; 
        P(f' {tag}: цвет сердцевины (пиксель) {tuple(int(v) for v in core)}; к фону {cr(core, hx(BG["light"])):.2f}:1; к телу {cr(core, hx("#DF5520")):.2f}:1')
    P(f' пары: #FFE3B8 к #FBEFDF = {cr(hx("#FFE3B8"), hx("#FBEFDF")):.3f}:1 (почти равны по яркости, отличается оттенком — тёплый/золотой; отличить от «дырки» помогает то, что внутри контура тела и граничит с оранжевым); #FFE3B8 к телу #DF5520 = {cr(hx("#FFE3B8"), hx("#DF5520")):.2f}:1')
    P(f' {"" }на тёмном (#1E1424) сердцевина осталась кремовой #FBEFDF; к телу {cr(hx("#FBEFDF"), hx("#DF5520")):.2f}:1')
    P('')
    P('=== 3. Фавикон: глаза (16 px) ===')
    for th in ('dark', 'light'):
        for s in (16, 32, 64):
            im = Image.open(os.path.join(D, f'r4-favicon-{s}-{th}.png')).convert('RGB'); a = np.array(im).astype(int); k = s//16
            e1 = tuple(int(v) for v in a[9*k+k//2, 4*k+k//2]); e2 = tuple(int(v) for v in a[9*k+k//2, 11*k+k//2]); bgc = hx(BG[th]); body = tuple(int(v) for v in a[12*k, 8*k])
            P(f' r4-favicon-{s}-{th}.png {im.size}: глаза L,R центры {e1}/{e2}; к фону {cr(e1, bgc):.2f}:1; к телу {cr(e1, body):.2f}:1; тело {body}')
    P(' положение глаз (клетки 16×16): было x 5,6 | 9,10; y 9–11 (зазор 2 клетки, низ глаз ряд 11). Стало x 4,5 | 10,11; y 8–10 (зазор 4 клетки, низ ряд 10). Сдвиг: +1 px вверх, зазор 2→4.')
    P(' контраст глаза к фону шапки/тёмной вкладки (фон — холст #1E1424, не #35363A, глаза внутри тела):')
    for nm, e, bg in (('тёмный глаз #5B3351 / фон #1E1424', '#5B3351', '#1E1424'), ('#5B3351 / вкладка #35363A', '#5B3351', '#35363A'), ('светлый: #2A1A2E / фон #FBEFDF', '#2A1A2E', '#FBEFDF')):
        P(f'   {nm}: {cr(hx(e), hx(bg)):.2f}:1')
    P('')
    P('=== 4. Растр знака ≤40 (vector mark-simple, Chromium) на 32 и 64 px: глаза против фона и тела ===')
    for th, fn in (('dark', 'lumo-v5r4-mark-simple.svg'), ('light', 'lumo-v5r4-mark-simple-onlight.svg')):
        for px in (32, 64):
            c, c_bg, c_body = eyes_check(pg, os.path.join(D, fn), px, th, None)
            P(f' {th:5s} {px}px: цвет глаза {c}; к фону {c_bg:.2f}:1; к телу {c_body:.2f}:1')
    b.close()
open(os.path.join(D, 'замеры-круг4.txt'), 'w').write('\n'.join(out) + '\n')
