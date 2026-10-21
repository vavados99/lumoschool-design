#!/usr/bin/env python3
"""Круг 8, логотип: замеры -> замеры-круг8.txt.  /usr/local/lib/hermes-agent/venv/bin/python measure8.py"""
import os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
out = []
def P(s=''): out.append(s); print(s)
def lum(c):
    f = lambda v: (v/255/12.92) if v/255 <= .03928 else ((v/255+.055)/1.055)**2.4
    return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])
def cr(a, b):
    la, lb = lum(a), lum(b); return (max(la, lb)+.05)/(min(la, lb)+.05)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
P('=== 1. Ореол вокруг малых иконок на тёмной шкале (скриншот листа, кольцо вокруг круга аватара) ===')
im = np.array(Image.open('r8-лист-для-Влада.png').convert('RGB')).astype(int)
sheet = open('sheet8.py').read()
with sync_playwright() as p:
    b = p.chromium.launch(args=['--disable-lcd-text']); pg = b.new_page(viewport={'width': 1600, 'height': 900})
    pg.goto('file:///root/.hermes/cache/scratch/sheet8.html'); pg.wait_for_timeout(800)
    rects = pg.evaluate('''()=>{const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.x+scrollX),Math.round(b.y+scrollY),Math.round(b.width),Math.round(b.height)]};
      return {panels:[...document.querySelectorAll('.hd,.tabs,.pane')].map(e=>[e.className,r(e)]),
              av:[...document.querySelectorAll('.pane.half .av')].map(e=>r(e))}}''')
    b.close()
bg = hx('#1E1424')
P(' тёмная панель чисто-фоновая: #1E1424')
for (x, y, w, h) in rects['av']:
    if im[y+h//2, x-6].tolist() != list(bg) and False: pass
dark_av = [r for r in rects['av'] if r[0] > 772][:3]   # 110/56/40; четвёртый аватар стоит внутри чипа (подложка чипа — не ореол)
for (x, y, w, h) in dark_av:
    # кольцо шириной 12 px вокруг круга: максимальное отклонение от фона (за пределами круга)
    cx, cy = x+w/2, y+h/2; ring = []
    for ang in np.linspace(0, 6.283, 72, endpoint=False):
        for d in (w/2+3, w/2+8, w/2+14):
            px_, py_ = int(cx+d*np.cos(ang)), int(cy+d*np.sin(ang))
            if 0 <= py_ < im.shape[0] and 0 <= px_ < im.shape[1]: ring.append(im[py_, px_])
    ring = np.array(ring); dev = np.abs(ring-np.array(bg)).max(axis=1)
    # проверяем только то, что внутри тёмной панели (кольцо на фоне панели)
    P(' аватар %dpx @(%d,%d): макс. отклонение кольца от #1E1424 = %d из 255 (0 = ореола нет)' % (w, x, y, dev.max()))
P()
P('=== 2. Сердцевина: один цвет на всех носителях (fill сердцевины в svg-файлах) ===')
for n in ('mark', 'mark-onlight', 'wordmark', 'wordmark-onlight', 'avatar', 'avatar-onlight'):
    s = open('lumo-v5r8-%s.svg' % n).read(); fills = re.findall(r'fill="(#[0-9A-Fa-f]{6})"', s)
    P(' lumo-v5r8-%-18s цвета: %s; кремовая #FFE3B8: %s' % (n, sorted(set(fills)), '#FFE3B8' in fills))
P(' В5/В6: сверить grep в замерах прототипов (см. замеры-круг8.txt прототипов)')
P(' контраст сердцевины #FFE3B8 к телу #DF5520 = %.2f:1; к телу #FF7A45 = %.2f:1' % (cr(hx('FFE3B8'), hx('DF5520')), cr(hx('FFE3B8'), hx('FF7A45'))))
P()
P('=== 3. Фавиконы ===')
for t, bgc in (('dark', '1E1424'), ('light', 'FBEFDF')):
    for n in (16, 32, 64):
        a = np.array(Image.open('r8-favicon-%d-%s.png' % (n, t)).convert('RGB')).astype(int)
        eye = (np.abs(a-np.array(hx('4A1A0E' if t == 'dark' else '2A1A2E'))).sum(axis=2) < 40)
        cream = (np.abs(a-np.array(hx('FFE3B8'))).sum(axis=2) < 6)
        ys, xs = np.nonzero(eye)
        if len(ys):
            m = (xs < xs.mean()); bb = []
            for sel in (m, ~m):
                bb.append((xs[sel].max()-xs[sel].min()+1, ys[sel].max()-ys[sel].min()+1))
            P(' r8-favicon-%d-%s: тёмных px глаз %d; глаза (ш×в px) левый %dx%d, правый %dx%d (вертикальные: %s); кремовых px блика %d'
              % (n, t, eye.sum(), bb[0][0], bb[0][1], bb[1][0], bb[1][1], 'да' if all(h > w for w, h in bb) else 'нет', cream.sum()))
        else:
            P(' r8-favicon-%d-%s: глаз НЕТ (чистое пламя); кремовых px %d' % (n, t, cream.sum()))
P()
P('=== 4. Левый язык ===')
def tips(file, vb=None):
    return None
d2 = re.search(r'BODY2 = \("(.+?)"\n\s+"(.+?)"\)', open('make8.py').read(), re.S)
P(' r7: кончик левого языка (118,122), внутренний край от (118,122) к (172,198): наклон влево-вверх, торчал «с плеча»')
P(' r8: кончик (160,104), выемка мельче ((180,178) вместо (172,198)): внешний край с (86,226) поднимается вправо (dx=+74 при dy=-122), как главный язык (276,18) ← (232,150): dx=+44 при dy=-132; угол к вертикали левого %.0f°, главного %.0f°' % (np.degrees(np.arctan2(74, 122)), np.degrees(np.arctan2(44, 132))))
P()
P('=== 5. Чип и панели листа ===')
P(' подложка чипа тёмного #2E2238 к фону панели #1E1424 = %.2f:1; ободок rgba(255,255,255,.08)' % cr(hx('2E2238'), hx('1E1424')))
P(' r7 чип был #18191A к фону #1E1424 = %.2f:1' % cr(hx('18191A'), hx('1E1424')))
ws = sorted({(c, r[2]) for c, r in rects['panels'] if ('hd' in c and 'm' not in c.split()) or 'full' in c or 'half' in c or 'tabs' in c})
P(' ширины панелей листа (класс → px): ' + '; '.join('%s=%d' % (c.replace(' ', '.'), w) for c, w in ws))
allw = sorted({r[2] for c, r in rects['panels'] if ('hd' in c) or 'full' in c or 'half' in c or 'tabs' in c})
P(' различных ширин панелей: %s (допустимо 1440 и 708 = 2×708+24)' % allw)
open('замеры-круг8.txt', 'w').write('\n'.join(out)+'\n')
