#!/usr/bin/env python3
import os, re, io, json, base64
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
DARK, LIGHT = '#1E1424', '#FBEFDF'
def rd(n, kind, suf): return open('%s/lumo-v%d-%s%s.svg' % (D, n, kind, suf)).read()
def uri(s): return 'data:image/svg+xml;base64,' + base64.b64encode(s.encode()).decode()
NAMES = {1: 'Капля-L (негатив)', 2: 'L + огонёк', 3: 'Монограмма в ореоле', 4: 'Типографика L.', 5: 'Силуэт Люмо'}

def sheet_html():
    h = ['<html><body style="margin:0;width:1600px;background:#140D18;font-family:Golos Text,sans-serif;color:#FBEFDF">'
         '<div style="padding:32px 48px 8px;font:600 34px sans-serif">LUMOSCHOOL · логотип · 5 вариантов — контрольный лист</div>']
    for n in range(1, 6):
        h.append('<div style="padding:18px 48px;border-top:2px solid #FF7A45;margin-top:18px">'
                 '<div style="font:700 40px sans-serif;margin-bottom:12px"><span style="color:#FF7A45">v%d</span> · %s</div>' % (n, NAMES[n]))
        h.append('<div style="display:flex;gap:24px">')
        for bg, suf in ((DARK, ''), (LIGHT, '-onlight')):
            h.append('<div style="background:%s;padding:20px 24px;border-radius:12px;width:680px">' % bg)
            h.append('<div style="display:flex;align-items:flex-end;gap:28px">')
            for px in (32, 64, 128):
                h.append('<img src="%s" width="%d" height="%d">' % (uri(rd(n, 'mark', suf)), px, px))
            h.append('<div style="width:1px"></div>')
            h.append('</div><div style="margin-top:18px"><img src="%s" width="320" style="display:block"></div>'
                     '<div style="margin-top:12px"><img src="%s" width="160" style="display:block"></div></div>' % (uri(rd(n, 'wordmark', suf)), uri(rd(n, 'wordmark', suf))))
        h.append('</div></div>')
    h.append('<div style="height:30px"></div></body></html>')
    return ''.join(h)

def zoom_html():
    h = ['<html><body style="margin:0;width:1600px;background:#140D18;color:#FBEFDF;font-family:sans-serif;padding:32px 0">'
         '<div style="padding:0 48px;font:600 30px sans-serif">Читаемость: 32 px и 16 px, увеличено ×6 (pixelated), без сглаживания при увеличении</div>']
    for bg, suf, lab in ((DARK, '', 'тёмный фон'), (LIGHT, '-onlight', 'светлый фон')):
        h.append('<div style="padding:16px 48px"><div style="font:600 24px sans-serif;margin-bottom:8px">%s</div><div style="display:flex;gap:16px">' % lab)
        for n in range(1, 6):
            h.append('<div style="background:%s;padding:10px;border-radius:8px;width:262px;color:%s;font:700 24px sans-serif">v%d<br>' % (bg, '#2A1A2E' if suf else '#FBEFDF', n))
            for px in (32, 16):
                h.append('<img data-px="%d" data-n="%d" data-suf="%s" src="%s" width="%d" height="%d" style="image-rendering:pixelated;margin-right:8px">' % (px, n, suf, uri(rd(n, 'mark', suf)), px, px))
            h.append('</div>')
        h.append('</div></div>')
    return ''.join(h)

def raster(page, n, suf, px, bg):
    """растр знака на px с фоном — реальный рендер Chromium в 1x"""
    page.set_viewport_size({'width': 200, 'height': 200})
    page.set_content('<body style="margin:0;background:%s"><img id=i src="%s" width=%d height=%d style="display:block"></body>' % (bg, uri(rd(n, 'mark', suf)), px, px))
    page.wait_for_selector('#i')
    return Image.open(io.BytesIO(page.screenshot(clip={'x': 0, 'y': 0, 'width': px, 'height': px}))).convert('RGB')

def lum(c):
    c = np.array(c, float) / 255; c = np.where(c <= .03928, c / 12.92, ((c + .055) / 1.055) ** 2.4)
    return .2126 * c[..., 0] + .7152 * c[..., 1] + .0722 * c[..., 2]

def cc(mask):
    """число связных компонент (4-связность) без scipy"""
    m = mask.copy(); H, W = m.shape; n = 0
    for y in range(H):
        for x in range(W):
            if m[y, x]:
                n += 1; st = [(y, x)]; m[y, x] = False
                while st:
                    a, b = st.pop()
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        i, j = a + da, b + db
                        if 0 <= i < H and 0 <= j < W and m[i, j]: m[i, j] = False; st.append((i, j))
    return n

def metrics(page, n):
    out = {}
    for suf, bg in (('', DARK), ('-onlight', LIGHT)):
        im = np.array(raster(page, n, suf, 32, bg)); bgc = np.array([int(bg[i:i + 2], 16) for i in (1, 3, 5)])
        diff = np.abs(im.astype(int) - bgc).sum(2)
        ink = diff > 60                      # заметно отличается от фона
        solid = diff > 200                   # почти полный цвет
        L_ink = lum(im[ink]).mean() if ink.any() else 0; L_bg = lum(bgc)
        cr = (max(L_ink, L_bg) + .05) / (min(L_ink, L_bg) + .05)
        # «дыры»: компоненты фона внутри знака (не касающиеся рамки) = различимые детали-вырезы
        bgm = ~ink; H, W = bgm.shape
        lab = bgm.copy(); holes = 0
        # флуд от края
        edge = np.zeros_like(bgm); st = [(y, x) for y in range(H) for x in (0, W - 1)] + [(y, x) for x in range(W) for y in (0, H - 1)]
        for y, x in st:
            if lab[y, x]:
                s = [(y, x)]; lab[y, x] = False
                while s:
                    a, b = s.pop()
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        i, j = a + da, b + db
                        if 0 <= i < H and 0 <= j < W and lab[i, j]: lab[i, j] = False; s.append((i, j))
        holes = cc(lab)
        # минимальная толщина: макс. эрозия — оценим по доле solid к ink
        out[suf or 'dark'] = dict(coverage=round(ink.mean() * 100, 1), solid_share=round(solid.sum() / max(1, ink.sum()) * 100), parts=cc(ink), holes=holes, contrast=round(cr, 1))
    return out

def colors(n):
    s = rd(n, 'mark', '')
    return sorted(set(re.findall(r'(?:fill|stroke)="(#[0-9A-Fa-f]{6})"', s)))

if __name__ == '__main__':
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 800})
        pg.set_content(sheet_html()); pg.wait_for_timeout(500)
        pg.screenshot(path=D + '/лист.png', full_page=True)
        pg.set_content(zoom_html()); pg.wait_for_timeout(500)
        # увеличить: делаем рендер 32/16 как растр и масштабируем ×6 в отдельной картинке
        b.close()
    # лист-32px: растр в реальных 32/16 px → ×6 nearest
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        W = 1600; canvas = Image.new('RGB', (W, 1000), '#14132000'[:7])
        from PIL import ImageDraw, ImageFont
        d = ImageDraw.Draw(canvas)
        try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30); fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
        except Exception: f = fs = ImageFont.load_default()
        d.text((40, 20), 'v1..v5 в реальных 32 px и 16 px, увеличено x6 (пиксели без сглаживания)', fill='#FBEFDF', font=f)
        y = 80
        for bg in (DARK, LIGHT):
            suf = '' if bg == DARK else '-onlight'
            d.rectangle([20, y, W - 20, y + 360], fill=bg)
            for n in range(1, 6):
                x = 40 + (n - 1) * 310
                d.text((x, y + 10), 'v%d' % n, fill='#FF7A45', font=f)
                a = raster(pg, n, suf, 32, bg).resize((192, 192), Image.NEAREST)
                c16 = raster(pg, n, suf, 16, bg).resize((96, 96), Image.NEAREST)
                canvas.paste(a, (x, y + 55)); canvas.paste(c16, (x + 196, y + 151))
                # реальный размер 1x
                canvas.paste(raster(pg, n, suf, 32, bg), (x, y + 270)); canvas.paste(raster(pg, n, suf, 16, bg), (x + 50, y + 286))
                d.text((x + 90, y + 280), '← 1x', fill='#888', font=fs)
            y += 380
        canvas.crop((0, 0, W, y)).save(D + '/лист-32px.png')
        for n in range(1, 6):
            res[n] = metrics(pg, n); res[n]['colors'] = colors(n)
            res[n]['kb'] = round(os.path.getsize('%s/lumo-v%d-mark.svg' % (D, n)) / 1024, 2)
            res[n]['kb_word'] = round(os.path.getsize('%s/lumo-v%d-wordmark.svg' % (D, n)) / 1024, 2)
        b.close()
    json.dump(res, open(D + '/замеры.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False))
