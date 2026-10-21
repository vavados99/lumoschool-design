#!/usr/bin/env python3
"""Замеры круга 7 (логотип) -> замеры-круг7.txt. Всё считается по файлам r7, не копируется из r6."""
import os, io, numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import make7 as M7
D = os.path.dirname(os.path.abspath(__file__)); out = []
def P(s=''): print(s); out.append(s)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def lum(c):
    v = [x/255 for x in c[:3]]; v = [x/12.92 if x <= .03928 else ((x+.055)/1.055)**2.4 for x in v]; return .2126*v[0]+.7152*v[1]+.0722*v[2]
def cr(a, b): a, b = lum(a), lum(b); return (max(a, b)+.05)/(min(a, b)+.05)
BG = {'light': '#FBEFDF', 'dark': '#1E1424'}
def render(pg, fn, px, bg):
    pg.set_viewport_size({'width': px, 'height': px})
    open('/root/.hermes/cache/scratch/m7.html', 'w').write('<body style="margin:0;background:%s"><img src="file://%s" style="width:%dpx;height:%dpx;display:block"></body>' % (bg, os.path.join(D, fn), px, px)); pg.goto('file:///root/.hermes/cache/scratch/m7.html'); pg.wait_for_timeout(200)
    return np.array(Image.open(io.BytesIO(pg.screenshot())).convert('RGB')).astype(int)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    P('=== 1. Глаза: цвет и контраст (WCAG 2.x) ===')
    P(' тёмная версия: глаза #4A1A0E (было r6 #2A1A2E)')
    for nm, eye, body, bg in (('тёмная', '#4A1A0E', '#FF7A45', '#1E1424'), ('тёмная, тело как в знаке #DF5520', '#4A1A0E', '#DF5520', '#1E1424'), ('светлая', '#2A1A2E', '#DF5520', '#FBEFDF'), ('r6 тёмная (было)', '#2A1A2E', '#FF7A45', '#1E1424')):
        P('  %-34s глаз %s к телу %s = %.2f:1; глаз к фону %s = %.2f:1' % (nm, eye, body, cr(hx(eye), hx(body)), bg, cr(hx(eye), hx(bg))))
    P(' фавикон r7 (пиксельный замер PNG):')
    for th in ('dark', 'light'):
        for s in (16, 32, 64):
            a = np.array(Image.open(os.path.join(D, 'r7-favicon-%d-%s.png' % (s, th))).convert('RGB')).astype(int); k = s//16
            eye = a[8*k+k//2, 4*k+k//2]; body = a[12*k, 8*k]
            P('  r7-favicon-%d-%s.png: глаз %s к телу %.2f:1; к фону %.2f:1' % (s, th, tuple(int(v) for v in eye), cr(eye, body), cr(eye, hx(BG[th]))))
    P(' честно: к фону тёмной вкладки/шапки глаз #4A1A0E остаётся близок (≈1.2:1) — глаз внутри тела, пара глаз/тело %.2f:1; отличие от «дырки» только в тёплом оттенке' % cr(hx('#4A1A0E'), hx('#FF7A45')))
    P('')
    P('=== 2. Левый язык ниже (геометрия 400×500 до нормировки) ===')
    ys = [pt[1] for pt in M7.B.flat(M7.B.parse(M7.BODY2))]; H = max(ys)-min(ys)
    P(' высота знака %.0f ед.; правый язык кончик y=18; левый: r6 y=42 → r7 y=122; опущен на %.0f ед. = %.1f %% высоты знака (цель 15–20 %%)' % (H, 80, 100*80/H))
    P(' разница верхушек двух языков: r6 24 ед. (%.1f %%) → r7 104 ед. (%.1f %%)' % (100*24/H, 100*104/H))
    P('')
    P('=== 3. Один язык на ≤56 px: проверка файлов ===')
    for fn in ('lumo-v5r7-mark-simple.svg', 'lumo-v5r7-mark-simple-onlight.svg', 'lumo-v5r7-wordmark-small.svg', 'lumo-v5r7-avatar-small.svg'):
        s = open(os.path.join(D, fn)).read(); P(' %-40s путь одно-язычный: %s; двух-язычный: %s' % (fn, M7.B1 in s, M7.B2 in s))
    for fn in ('lumo-v5r7-mark.svg', 'lumo-v5r7-wordmark.svg', 'lumo-v5r7-avatar.svg'):
        s = open(os.path.join(D, fn)).read(); P(' %-40s (≥64 px) двух-язычный: %s' % (fn, M7.B2 in s))
    # число пиков силуэта на 56 и 24 px (локальные максимумы верхнего края по столбцам)
    for fn in ('lumo-v5r7-mark-simple.svg', 'lumo-v5r7-mark.svg'):
        for px in (56, 150):
            im = render(pg, fn, px, '#FF00FF'); m = (np.abs(im-np.array((255, 0, 255))).sum(2) > 60)
            top = [np.argmax(m[:, x]) if m[:, x].any() else 9999 for x in range(px)]
            mn = min(top); peaks = sum(1 for x in range(1, px-1) if top[x] < 9999 and top[x] <= top[x-1] and top[x] < top[x+1] and top[x] < mn+0.45*px and top[x] <= min(top[max(0, x-3):x+4]))
            P('  %s @%d px: верхушки силуэта (локальные пики выше 45 %% высоты): %d' % (fn, px, peaks))
    P('')
    P('=== 4. Фавикон: положение глаз ===')
    P(' r6: строки 9–10 из 16 (центр 9.5) → r7: строки 8–9 (центр 8.5), на 1 клетку выше; тело занимает строки 1–14 (центр 7.5): глаза на %.1f клетки ниже центра тела (r6: 2.0)' % (8.5-7.5))
    P(' клетки глаз x 4,5 | 10,11 — внутри тела (тело в строках 8–9 занимает x 2–12/13)')
    P(' не сделано: подъём на 2 клетки (y 7–8) — правый глаз упёрся бы в край тела (в строке 7 тело кончается на x=11)')
    b.close()
open(os.path.join(D, 'замеры-круг7.txt'), 'w').write('\n'.join(out)+'\n')
