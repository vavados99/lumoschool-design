#!/usr/bin/env python3
"""Замеры правок круга 3. Запуск: /usr/local/lib/hermes-agent/venv/bin/python measure_pravki.py  -> замеры-правки.txt
Рендер SVG в Chromium (1:1), анализ пикселей numpy. Старое (../) и новое (./) сравниваются на одной и той же процедуре."""
import os, io, sys
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); OLD = os.path.dirname(D)
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)
def lin(c):
    c = c / 255.0; return c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
def L(rgb): return .2126 * lin(rgb[0]) + .7152 * lin(rgb[1]) + .0722 * lin(rgb[2])
def cr(a, b):
    la, lb = sorted([L(a), L(b)], reverse=True); return (la + .05) / (lb + .05)
def hx(h): h = h.lstrip('#'); return [int(h[i:i+2], 16) for i in (0, 2, 4)]
BG = {'dark': '#1E1424', 'light': '#FBEFDF'}

def render(pg, path, h, bg, w=None):
    open('/root/.hermes/cache/scratch/r.html', 'w').write('<body style="margin:0;background:%s"><img id=i src="file://%s" style="height:%dpx;display:block;image-rendering:pixelated"></body>' % (bg, path, h))
    pg.goto('file:///root/.hermes/cache/scratch/r.html')
    pg.wait_for_function("document.getElementById('i').complete"); pg.wait_for_timeout(100)
    el = pg.query_selector('#i'); png = el.screenshot()
    return np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(int)

def classify(im, bgc):
    bgc = np.array(hx(bgc)); d = np.abs(im - bgc).sum(-1)
    return d > 40
def orange_mask(im):  # оранжевое тело (включая сглаженные края кончика): красный заметно выше зелёного и синего
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    return (r > 110) & (r - g > 45) & (r - b > 70)
def cream_mask(im):
    return (im[..., 0] > 200) & (im[..., 1] > 190) & (im[..., 2] > 170) | (im[..., 0] < 80) & (im[..., 1] < 70) & (im[..., 2] < 80) & False

def lockup_metrics(pg, path, h, theme):
    im = render(pg, path, h, BG[theme]); H, W, _ = im.shape
    om = orange_mask(im)
    # текст: светлый на тёмном / тёмный на светлом, исключая оранжевое
    bgc = np.array(hx(BG[theme]))
    if theme == 'dark': tm = (im[..., 0] > 150) & (im[..., 1] > 140) & (im[..., 2] > 120) & ~om   # кремовый текст
    else: tm = (im[..., 0] < 120) & (im[..., 1] < 100) & (im[..., 2] < 120) & ~om                   # тёмный текст
    # колонки оранжевого знака
    ys, xs = np.where(om); mx0, mx1, my0, my1 = xs.min(), xs.max(), ys.min(), ys.max()
    # текст правее знака (глаза знака тёмные — отсекаем колонками)
    tmr = tm.copy(); tmr[:, :mx1 + 2] = False
    ty, tx = np.where(tmr); tx0 = tx.min()
    # «L»: колонки сразу от tx0, ширина ~ 0.5 cap: берём 6 первых колонок текста
    Lcols = tmr[:, tx0:tx0 + 6]; ly, _ = np.where(Lcols); cap_top, base = ly.min(), ly.max() + 1
    cap = base - cap_top
    return dict(H=H, mark_h=my1 - my0 + 1, mark_top=my0, mark_bottom=my1 + 1, cap_top=int(cap_top), baseline=int(base), cap=int(cap),
                gap=int(tx0 - (mx1 + 1)), top_vs_cap=int(my0 - cap_top), below_base=int(my1 + 1 - base))

def eyes_check(pg, path, px, theme, eye_hex, expect_eyes=True):
    """цвет центра глаза против цвета фона и цвета тела"""
    im = render(pg, path, px, BG[theme]); H, W, _ = im.shape
    om = orange_mask(im); ys, xs = np.where(om)
    # глаза: нетелесные пиксели внутри bbox тела, ниже середины
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    reg = ~om[by0:by1 + 1, bx0:bx1 + 1]; yy, xx = np.where(reg); sel = (yy > (by1 - by0) * 0.55) & (yy < (by1 - by0) * 0.85)
    # центр левого глаза ≈ x 0.38 ширины; берём пиксель по ожидаемой точке
    cx = bx0 + int((bx1 - bx0) * 0.36); cy = by0 + int((by1 - by0) * 0.78)
    pxl = im[cy, cx]
    body = im[om].mean(0)
    return tuple(int(v) for v in pxl), cr(pxl, hx(BG[theme])), cr(pxl, body)

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 600})
    P('=== 1. Шапка: знак, опускание, отступ до «L» (знак ≤40px упрощённый, svg wordmark-small) ===')
    P('lock_h = высота картинки лого. Было = ../, Стало = ./. px при device scale 1.')
    for name, fn in (('wordmark-small', 'lumo-v5r3-wordmark-small.svg'), ('wordmark-small-onlight', 'lumo-v5r3-wordmark-small-onlight.svg'), ('wordmark (полный знак)', 'lumo-v5r3-wordmark.svg')):
        theme = 'light' if 'onlight' in fn else 'dark'
        hs = [61, 43, 150] if 'small' in name else [150, 96]
        for h in hs:
            for tag, base in (('было ', OLD), ('стало', D)):
                if 'small' in name and h == 61 and tag == 'было ': hh = 56   # была шапка 56
                elif 'small' in name and h == 43 and tag == 'было ': hh = 40
                else: hh = h
                m = lockup_metrics(pg, os.path.join(base, fn), hh, theme)
                P(f' {name:24s} {tag} lock_h={hh:3d}: знак высота {m["mark_h"]:3d}px; cap {m["cap"]}px; зазор знак→L {m["gap"]}px = {m["gap"]/m["cap"]:.3f} cap; верх знака vs верх заглавной {m["top_vs_cap"]:+d}px; низ знака ниже базовой линии {m["below_base"]:+d}px')
    P('')
    P('=== 2. Глаза маленького знака на тёмном: цвет глаза против фона шапки #1E1424 / тела (контраст WCAG) ===')
    for px in (16, 32, 48, 64):
        for tag, base in (('было ', OLD), ('стало', D)):
            fn = 'lumo-v5r3-mark16.svg' if px == 16 else 'lumo-v5r3-mark-simple.svg'
            hpx = px
            try:
                c, c_bg, c_body = eyes_check(pg, os.path.join(base, fn), hpx, 'dark', None)
                P(f' знак {px:3d}px {tag}: цвет глаза {c}; к фону шапки {c_bg:.2f}:1; к телу {c_body:.2f}:1')
            except Exception as ex: P(' ошибка', px, tag, ex)
    P(' справка (расчёт): глаза #2A1A2E к #1E1424 = %.2f; #4A2A40 к #1E1424 = %.2f; #4A2A40 к #35363A (тёмная вкладка) = %.2f; #5B3351 к #35363A = %.2f; #5B3351 к #202124 = %.2f; #4A2A40 к телу #FF7A45 = %.2f; #5B3351 к телу = %.2f' % (
        cr(hx('#2A1A2E'), hx('#1E1424')), cr(hx('#4A2A40'), hx('#1E1424')), cr(hx('#4A2A40'), hx('#35363A')), cr(hx('#5B3351'), hx('#35363A')), cr(hx('#5B3351'), hx('#202124')), cr(hx('#4A2A40'), hx('#FF7A45')), cr(hx('#5B3351'), hx('#FF7A45'))))
    P('=== 3. Знак на светлом фоне #FBEFDF (глаза остаются #2A1A2E) ===')
    for px in (16, 32, 48, 64):
        fn = 'lumo-v5r3-mark16-onlight.svg' if px == 16 else 'lumo-v5r3-mark-simple-onlight.svg'
        c, c_bg, c_body = eyes_check(pg, os.path.join(D, fn), px, 'light', None)
        P(f' знак {px:3d}px: глаз {c}; к фону {c_bg:.2f}:1; к телу {c_body:.2f}:1')
    P('=== 4. Полный знак 64 и 110, аватар 110: рендер без ошибок, размеры ===')
    for fn, px in (('lumo-v5r3-mark.svg', 64), ('lumo-v5r3-mark.svg', 110), ('lumo-v5r3-avatar.svg', 110), ('lumo-v5r3-avatar-small.svg', 48)):
        im = render(pg, os.path.join(D, fn), px, BG['dark']); P(f' {fn} {px}px -> {im.shape[1]}x{im.shape[0]}')
    P('=== 5. Фавикон-PNG 16/32 (проверка пикселей глаз) ===')
    for fn in ('favicon-v5r3-16-dark.png', 'favicon-v5r3-16-light.png', 'favicon-v5r3-32px-dark.png', 'favicon-v5r3-32px-light.png'):
        im = Image.open(os.path.join(D, fn)); P(f' {fn}: {im.size}, цвет глаза-пикселя (центр {im.size[0]*5//16},{im.size[1]*10//16}): {im.convert("RGBA").getpixel((im.size[0]*5//16, im.size[1]*10//16))}')
    b.close()

import wordmark3 as WM
kp = WM.kern_pairs()[0]
xs_old = WM.positions(kp, {'Lu': -32, 'ch': -26, 'sc': -8})[0]; xs_new = WM.positions(kp, WM.MANUAL)[0]
go = WM.optical_gaps(xs_old); gn = WM.optical_gaps(xs_new)
P('=== 6. Кернинг c–h (ед. на 1000 em; оптические зазоры {пара, мин., оптич.} при размере 1000) ===')
P(' MANUAL было c–h -26, стало', WM.MANUAL['ch'])
P(' было :', go); P(' стало:', gn)
P(' c–h мин. зазор: было %s → стало %s; медиана остальных пар (мин.): %s' % ([m for p, m, o in go if p == 'ch'][0], [m for p, m, o in gn if p == 'ch'][0], round(float(np.median([m for p, m, o in gn if p not in ('ch',)])), 1)))
open(os.path.join(D, 'замеры-правки.txt'), 'w').write('\n'.join(out) + '\n')
