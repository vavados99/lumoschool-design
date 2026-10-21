#!/usr/bin/env python3
"""Круг 3, ВОРДМАРК: Golos Text 600, кернинг GPOS (Chromium/HarfBuzz) + ручная доводка L–u, c–h; контуры в SVG.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python wordmark3.py"""
import os, json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(D + '/../../../../прототипы-люмо/B5-тьма/fonts')
TEXT = 'Lumoschool'
TRACK = -0.02          # em, как в круге 2
SCR = '/root/.hermes/cache/scratch'

def fmt(v): return ('%.2f' % v).rstrip('0').rstrip('.')
def font():
    f = TTFont(FONTS + '/golos-text-latin-wght-normal.woff2')
    f = instancer.instantiateVariableFont(f, {'wght': 600}); return f
F = font(); UPM = F['head'].unitsPerEm; CMAP = F.getBestCmap(); GS = F.getGlyphSet(); HMTX = F['hmtx']
def adv(ch): return HMTX[CMAP[ord(ch)]][0]

def browser_kern():
    """x-позиции букв в Chromium (HarfBuzz, GPOS kern включён) при 1000 px без трекинга -> кернинг в em-единицах шрифта"""
    html = ("<style>@font-face{font-family:G;src:url('file://%s/golos-text-latin-wght-normal.woff2');font-weight 600}"
            ".t{font:600 %dpx G;font-kerning:%s;letter-spacing:0;white-space:nowrap;position:absolute;left:0;top:0}</style>"
            "<span class=t id=a>%s</span>") % (FONTS, UPM, 'normal', TEXT)
    html = html.replace('font-weight 600', 'font-weight:600')
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.goto('file://' + FONTS + '/LICENSE') if False else None
        open(SCR + '/k.html', 'w').write(html)
        for mode in ('normal', 'none'):
            pg.goto('file://' + SCR + '/k.html'); pg.evaluate("document.fonts.ready")
            pg.evaluate("m => { const e=document.getElementById('a'); e.style.fontKerning=m; }", mode)
            pg.evaluate("document.fonts.load('600 %dpx G')" % UPM); pg.wait_for_timeout(300)
            xs = pg.evaluate("""() => { const t=document.getElementById('a').firstChild; const r=document.createRange(); const o=[];
              for(let i=0;i<t.length;i++){ r.setStart(t,i); r.setEnd(t,i+1); o.push(r.getBoundingClientRect().left);} 
              const w=document.getElementById('a').getBoundingClientRect().width; o.push(w); return o; }""")
            res[mode] = xs
        b.close()
    return res

def kern_pairs():
    r = browser_kern(); k = []
    for i in range(len(TEXT) - 1):
        a = TEXT[i]
        dn = r['normal'][i + 1] - r['normal'][i] - adv(a)
        d0 = r['none'][i + 1] - r['none'][i] - adv(a)
        k.append((TEXT[i:i+2], round(dn, 1), round(d0, 1)))
    return k, r

# ручная доводка (em-единицы шрифта, 1000/em), подобрана по оптическим зазорам (см. optical_gaps)
MANUAL = {'Lu': -32, 'ch': -12, 'sc': -8}   # правки: c–h было -26 (Опус: «sch» темнее слова)   # поджать L–u и c–h до мин. зазора >=30/45 ед.; s–c чуть (131 против медианы 107)

def positions(kern, manual):
    xs = []; x = 0
    for i, ch in enumerate(TEXT):
        xs.append(x)
        x += adv(ch) + TRACK * UPM
        if i < len(TEXT) - 1:
            pair = TEXT[i:i+2]; x += kern[i][1] + manual.get(pair, 0)
    return xs, x - TRACK * UPM

# оптические зазоры между соседними буквами (в x-высоте полосе), px при размере 1000
def glyph_arr(ch, size=1000):
    path = SCR + '/golos600.ttf'
    if not os.path.exists(path): F.save(path)
    fnt = ImageFont.truetype(path, size)
    W = H = int(size * 1.6); im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    ox = 300; base = int(size * 1.15); d.text((ox, base), ch, font=fnt, fill=255, anchor='ls')
    return np.array(im) > 127, ox, base

def optical_gaps(xs, size=1000):
    sc = size / UPM; xh = None
    bp = BoundsPen(GS); GS[CMAP[ord('x')]].draw(bp); xh = bp.bounds[3] * sc
    out = []
    arrs = [glyph_arr(c, size) for c in TEXT]
    for i in range(len(TEXT) - 1):
        a, oxa, base = arrs[i]; b, oxb, _ = arrs[i + 1]
        rows = range(int(base - xh * 0.95), int(base - xh * 0.05))
        gaps = []
        for y in rows:
            ra = np.where(a[y])[0]; rb = np.where(b[y])[0]
            if len(ra) == 0 or len(rb) == 0: gaps.append(np.nan); continue
            right_a = ra.max() - oxa + xs[i] * sc; left_b = rb.min() - oxb + xs[i + 1] * sc
            gaps.append(left_b - right_a)
        g = np.array(gaps); mn = np.nanmin(g); cap = mn + 0.3 * xh
        opt = np.nanmean(np.where(np.isnan(g), cap, np.minimum(g, cap)))
        out.append((TEXT[i:i+2], round(float(mn), 1), round(float(opt), 1)))
    return out

def path_d(xs, size, x0, baseline):
    sc = size / UPM; d = []
    for ch, x in zip(TEXT, xs):
        g = GS[CMAP[ord(ch)]]; sp = SVGPathPen(GS, ntos=fmt)
        g.draw(TransformPen(sp, (sc, 0, 0, -sc, x0 + x * sc, baseline))); d.append(sp.getCommands())
    return ''.join(d)

def capheight():
    bp = BoundsPen(GS); GS[CMAP[ord('H')]].draw(bp); return bp.bounds[3]

if __name__ == '__main__':
    kp, raw = kern_pairs()
    print('кернинг GPOS (Chromium) пары: (пара, с кернингом, без) :', kp)
    xs0 = positions(kp, {})[0]; g0 = optical_gaps(xs0)
    print('оптич. зазоры БЕЗ ручной доводки:', g0)
    # подбор доводки: тянем L–u и c–h к медиане зазоров «нормальных» пар
    med = float(np.median([o for p, m, o in g0 if p not in ('Lu', 'ch', 'sc')]))
    print('медиана оптич. зазора нормальных пар', round(med, 1))
