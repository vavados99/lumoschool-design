#!/usr/bin/env python3
"""Круг 2: листы и замеры. Запуск: /usr/local/lib/hermes-agent/venv/bin/python render2.py"""
import os, io, json, base64, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
import build2 as B
D = B.D
DARK, LIGHT = B.DARKBG, B.CREAM
NAMES = {5: 'Силуэт Люмо (главный)', 1: 'Капля-L', 2: 'L + огонёк (запас, фавикон)'}
def U(f): return 'data:image/svg+xml;base64,' + base64.b64encode(open('%s/%s' % (D, f), 'rb').read()).decode()
def SU(s): return 'data:image/svg+xml;base64,' + base64.b64encode(s.encode()).decode()
def suf(th): return {'dark': '', 'light': '-onlight', 'mono': '-mono'}[th]

# ---------- WCAG ----------
def lin(c): c = c / 255; return c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
def L(h): r, g, b = (int(h[i:i+2], 16) for i in (1, 3, 5)); return .2126 * lin(r) + .7152 * lin(g) + .0722 * lin(b)
def cr(a, b): la, lb = L(a), L(b); return round((max(la, lb) + .05) / (min(la, lb) + .05), 2)

FONT = lambda s, bold=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), s)

def sheet(theme):
    bg = DARK if theme == 'dark' else LIGHT; fg = B.CREAM if theme == 'dark' else B.INK
    acc = B.ORANGE if theme == 'dark' else B.ORANGE_L
    h = ['<body style="margin:0;width:1600px;background:%s;color:%s;font-family:\'Golos Text\',DejaVu Sans,sans-serif">' % (bg, fg),
         '<div style="padding:34px 56px 6px;font:700 32px DejaVu Sans">LUMOSCHOOL · логотип · круг 2 · %s фон</div>' % ('тёмный #1E1424' if theme == 'dark' else 'светлый #FBEFDF')]
    for v in (5, 1, 2):
        h.append('<div style="margin:26px 56px 0;padding-top:16px;border-top:2px solid %s"><div style="font:700 30px DejaVu Sans;margin-bottom:14px"><span style="color:%s">v%d</span> · %s</div>' % (acc, acc, v, NAMES[v]))
        h.append('<div style="display:flex;align-items:flex-end;gap:34px">')
        for px in (128, 64, 32):
            h.append('<img src="%s" width="%d" height="%d">' % (U('lumo-v%d-mark%s.svg' % (v, suf(theme))), px, px))
        h.append('<img src="%s" width="16" height="16" style="margin-left:4px">' % U('lumo-v%d-mark16%s.svg' % (v, suf(theme))))
        h.append('<div style="width:30px"></div><img src="%s" height="84"><img src="%s" height="40">' % (U('lumo-v%d-wordmark%s.svg' % (v, suf(theme))), U('lumo-v%d-wordmark%s.svg' % (v, suf(theme)))))
        if v == 5:   # круглый аватар: знак ~60 % диаметра, поднят на 4 %
            h.append(avatar(theme))
        h.append('</div><div style="font:18px DejaVu Sans;opacity:.7;margin-top:8px">128 · 64 · 32 · 16 (мастер 16 px) · вордмарк высотой 84 / 40 px</div></div>')
    h.append('<div style="height:34px"></div></body>')
    return ''.join(h)

def avatar(theme):
    s = B.mark(5, 'dark')
    inner = s[s.index('</title>') + 8:-6]
    k = 0.60 * 160 / 88.0
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160"><defs><radialGradient id="g"><stop offset="0" stop-color="#FF7A45" stop-opacity=".28"/><stop offset="1" stop-color="#FF7A45" stop-opacity="0"/></radialGradient></defs>'
           '<circle cx="80" cy="80" r="80" fill="#2A1A2E"/><circle cx="80" cy="76" r="62" fill="url(#g)"/>'
           '<g transform="translate(%s %s) scale(%s)">%s</g></svg>' % (B.fmt(80 - 50 * k), B.fmt(80 - 50 * k - 0.04 * 160), B.fmt(k), inner))
    open(D + '/lumo-v5-avatar.svg', 'w').write(svg)
    return '<img src="%s" width="160" height="160" style="margin-left:20px;border-radius:80px">' % SU(svg)

def raster(page, f, px, bg, scale_to=None):
    page.set_viewport_size({'width': 200, 'height': 200})
    page.set_content('<body style="margin:0;background:%s"><img id=i src="%s" width=%d height=%d style="display:block"></body>' % (bg, U(f), px, px))
    page.wait_for_selector('#i'); page.wait_for_timeout(30)
    return Image.open(io.BytesIO(page.screenshot(clip={'x': 0, 'y': 0, 'width': px, 'height': px}))).convert('RGB')

def components(mask):
    m = mask.copy(); H, W = m.shape; out = []
    for y in range(H):
        for x in range(W):
            if m[y, x]:
                st = [(y, x)]; m[y, x] = False; comp = []
                while st:
                    a, b = st.pop(); comp.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        i, j = a + da, b + db
                        if 0 <= i < H and 0 <= j < W and m[i, j]: m[i, j] = False; st.append((i, j))
                out.append(comp)
    return out

def measure(im, bg):
    a = np.array(im).astype(int); bgc = np.array([int(bg[i:i+2], 16) for i in (1, 3, 5)])
    diff = np.abs(a - bgc).sum(2); H, W = diff.shape
    ink = diff > 60
    # внешний фон: связан с рамкой через пиксели, близкие к фону
    near = ~ink; ext = np.zeros_like(near); st = [(y, x) for y in range(H) for x in (0, W-1)] + [(y, x) for x in range(W) for y in (0, H-1)]
    for y, x in st:
        if near[y, x] and not ext[y, x]:
            s = [(y, x)]; ext[y, x] = True
            while s:
                p, q = s.pop()
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    i, j = p + da, q + db
                    if 0 <= i < H and 0 <= j < W and near[i, j] and not ext[i, j]: ext[i, j] = True; s.append((i, j))
    inside = ~ext
    # основной цвет знака = самый частый цвет внутри
    cols, cnt = np.unique(a[inside].reshape(-1, 3), axis=0, return_counts=True); main = cols[cnt.argmax()]
    far = inside & (np.abs(a - main).sum(2) > 60)           # детали, отличные от основного цвета
    det = components(far)
    hexs = lambda c: '#%02X%02X%02X' % tuple(int(v) for v in c)
    det_info = []
    for c in sorted(det, key=len, reverse=True):
        if len(c) < 4: continue
        col = np.mean([a[y, x] for y, x in c], axis=0); det_info.append(dict(px=len(c), contrast_vs_main=cr(hexs(col), hexs(main))))
    anti = ((diff > 15) & (diff < 200)).sum() / max(1, ink.sum())
    return dict(ink_px=int(ink.sum()), parts=len(components(ink)), main_color=hexs(main), details=det_info, antialias_share=round(float(anti), 2))

def sheet_px(pg, px, fname, title):
    canvas = Image.new('RGB', (1600, 1000), '#140D18'); d = ImageDraw.Draw(canvas)
    d.text((40, 24), title, fill=B.CREAM, font=FONT(26, True))
    y = 80; Z = 6 if px == 32 else 10
    for theme in ('dark', 'light'):
        bg = DARK if theme == 'dark' else LIGHT
        d.rectangle([20, y, 1580, y + 40 + px * Z + 72], fill=bg)
        d.text((40, y + 8), '%s фон' % ('тёмный' if theme == 'dark' else 'светлый'), fill=B.ORANGE_L if theme == 'light' else B.ORANGE, font=FONT(20, True))
        for i, v in enumerate((5, 1, 2)):
            x = 60 + i * 500
            f = 'lumo-v%d-mark%s.svg' % (v, suf(theme)) if px == 32 else 'lumo-v%d-mark16%s.svg' % (v, suf(theme))
            im = raster(pg, f, px, bg)
            canvas.paste(im.resize((px * Z, px * Z), Image.NEAREST), (x, y + 44))
            canvas.paste(im, (x + px * Z + 24, y + 44))
            d.text((x + px * Z + 24, y + 44 + px + 6), '1×', fill='#888', font=FONT(16))
            if px == 16:   # для сравнения: 32-px версия, ужатая до 16
                big = raster(pg, 'lumo-v%d-mark%s.svg' % (v, suf(theme)), 16, bg)
                canvas.paste(big.resize((16 * 4, 16 * 4), Image.NEAREST), (x + px * Z + 24, y + 44 + 60))
                canvas.paste(big, (x + px * Z + 24 + 70, y + 44 + 60)); d.text((x + px * Z + 24, y + 44 + 128), 'ужатая 32px-версия', fill='#888', font=FONT(14))
            d.text((x, y + 40 + px * Z + 6), 'v%d' % v, fill=B.INK if theme == 'light' else B.CREAM, font=FONT(22, True))
        y += 40 + px * Z + 80
    canvas.crop((0, 0, 1600, y)).save(D + '/' + fname)

def diacritics(pg):
    chars = 'ŁąężäöüßčřšžЇєіїЄІ'
    missing = [c for c in 'ŁłąęćńóśźżÄÖÜäöüßČčŘřŠšŽžЇїЄєІіҐґ' if not B.FACE.has(c)]
    samples = ['Lumoschool', 'ŁĄĘŻ łąęż', 'ÄÖÜ äöü ß', 'ČŘŠŽ čřšž', 'Ї Є І ї є і', 'Люмо школа']
    h = ['<body style="margin:0;width:1500px;background:%s;color:%s;padding:30px 50px;font-family:DejaVu Sans">' % (DARK, B.CREAM),
         '<div style="font:600 24px DejaVu Sans;margin-bottom:12px">Golos Text 600 (шрифт сайта), контуры fontTools. Нет глифов: %s</div>' % (', '.join(missing) if missing else 'нет — все 38 проверенных символов есть')]
    for s in samples:
        d, w = B.FACE.text_path(s, 100, -0.02, 10, 120)
        h.append('<img src="%s" width="%d" style="display:block;margin:8px 0">' % (SU('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s 160"><path fill="#FBEFDF" d="%s"/></svg>' % (B.fmt(w + 20), d)), int((w + 20) * 1.1)))
    h.append('</body>')
    pg.set_viewport_size({'width': 1600, 'height': 900}); pg.set_content(''.join(h)); pg.wait_for_timeout(300)
    pg.screenshot(path=D + '/диакритика.png', full_page=True)
    return missing

if __name__ == '__main__':
    B_main = __import__('subprocess').run(['/usr/local/lib/hermes-agent/venv/bin/python', D + '/build2.py'], capture_output=True)
    res = {'шрифт': 'Golos Text, wght 600 (шрифт сайта, прототипы-люмо/B5-тьма/fonts), трекинг -0.02em, без кернинга GPOS',
           'цвета': {'тёмный_фон': DARK, 'светлый_фон': LIGHT, 'оранж_тёмный': B.ORANGE, 'оранж_светлый': B.ORANGE_L, 'чернила': B.INK}}
    res['контраст_WCAG'] = {
        'оранж #FF7A45 на тёмном #1E1424': cr(B.ORANGE, DARK), 'оранж #FF7A45 на белом #FFFFFF (вкладка)': cr(B.ORANGE, '#FFFFFF'),
        'оранж #FF7A45 на светлом #FBEFDF (старый)': cr(B.ORANGE, LIGHT),
        'оранж #DF5520 на светлом #FBEFDF': cr(B.ORANGE_L, LIGHT), 'оранж #DF5520 на белом #FFFFFF': cr(B.ORANGE_L, '#FFFFFF'),
        'оранж #DF5520 на тёмном #1E1424': cr(B.ORANGE_L, DARK),
        'вырез кремовый на #DF5520 (огонёк на светлом)': cr(B.CREAM, B.ORANGE_L), 'вырез кремовый на #FF7A45 (огонёк на тёмном)': cr(B.CREAM, B.ORANGE),
        'глаза #2A1A2E на #FF7A45 (тёмный)': cr(B.INK, B.ORANGE), 'глаза #2A1A2E на #DF5520 (светлый)': cr(B.INK, B.ORANGE_L),
        'вордмарк #FBEFDF на тёмном': cr(B.CREAM, DARK), 'вордмарк #2A1A2E на светлом': cr(B.INK, LIGHT),
        'v2 L #FBEFDF на тёмном': cr(B.CREAM, DARK), 'v2 L #2A1A2E на светлом': cr(B.INK, LIGHT), 'v2 огонёк #DF5520 на светлом': cr(B.ORANGE_L, LIGHT)}
    res['угол_кончика_градусы'] = {'было (круг 1)': round(B.G['angle_before'], 1), 'стало': round(B.G['angle_after'], 1), 'прибавка': round(B.G['angle_after'] - B.G['angle_before'], 1)}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 900})
        # шрифт сайта не нужен для листа (вордмарк — контуры); подписи листа — DejaVu
        for th in ('dark', 'light'):
            pg.set_content(sheet(th)); pg.wait_for_timeout(500)
            pg.screenshot(path=D + '/лист-сравнение-%s.png' % ('тёмный' if th == 'dark' else 'светлый'), full_page=True)
        sheet_px(pg, 32, 'лист-32px.png', 'Знаки в реальных 32 px (×6 слева, 1× справа), тёмный и светлый фон')
        sheet_px(pg, 16, 'лист-16px.png', 'Мастера 16 px (×10 слева, 1× справа) и ужатая 32px-версия для сравнения')
        res['диакритика_нет_глифов'] = diacritics(pg)
        res['читаемость'] = {}
        for v in (5, 1, 2):
            r = {}
            for th, bg in (('dark', DARK), ('light', LIGHT)):
                r[th] = {'32px': measure(raster(pg, 'lumo-v%d-mark%s.svg' % (v, suf(th)), 32, bg), bg),
                         '16px_мастер': measure(raster(pg, 'lumo-v%d-mark16%s.svg' % (v, suf(th)), 16, bg), bg),
                         '16px_ужатая_32': measure(raster(pg, 'lumo-v%d-mark%s.svg' % (v, suf(th)), 16, bg), bg)}
            res['читаемость'][NAMES[v]] = r
        # пиксельный контраст знака (средний цвет «чернил» против фона) на 32 px
        res['kb'] = {f: round(os.path.getsize(D + '/' + f) / 1024, 2) for f in sorted(os.listdir(D)) if f.endswith('.svg')}
        b.close()
    json.dump(res, open(D + '/замеры.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))
