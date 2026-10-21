"""Круг 10: кадры r10-* и замеры В6-преподаватель -> shots/r10-metrics.txt.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run_r9.py
ВЕСЬ замер идёт с chromium args ['--disable-lcd-text'] (серое сглаживание; иначе «тёплые точки» ловят цветную кайму LCD на цифрах).
Каждый экран меряется ОТДЕЛЬНО своими числами (viewport на момент кадра):
  - ширина страницы = окну; мин. шрифт среди видимых текстов;
  - контраст: для каждого видимого текста document.elementFromPoint в центре видимой части; если вернулся не сам элемент/потомок -> «перекрыт», в контраст не входит (1.00 не считается);
    остальные: пиксели viewport при прозрачном тексте, сравнение с цветом текста; неактивные (disabled/aria-disabled) считаются отдельно;
  - тёплые точки: HSV тон ≤52°/≥345°, насыщ ≥0,45, яркость ≥0,6, слияние ≤12 px, области ≥40 px.
"""
import sys, os, io, re, colorsys, itertools, json
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html')
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
ARGS = ['--disable-lcd-text']
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def Lm(rgb): return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
def cr(a, b):
    la, lb = Lm(a), Lm(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def parse(c): return [float(x) for x in re.findall(r'[\d.]+', c)[:4]]

INIT = """window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) {window.__cls += e.value; (window.__src=window.__src||[]).push([+e.value.toFixed(4), Math.round(e.startTime), e.hadRecentInput, (e.sources||[]).map(s=>{const n=s.node; return n?(n.nodeName+(n.id?'#'+n.id:'')+(n.className&&n.className.baseVal===undefined?'.'+String(n.className).split(' ')[0]:'')):'?'}).join(',')]);} }).observe({type:'layout-shift', buffered:true});"""

# видимые тексты в окне + проверка перекрытия через elementFromPoint
VP_JS = """() => {
  const res = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); const vw = innerWidth, vh = innerHeight;
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg') || el.closest('details:not([open])')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    const x0 = Math.max(0, b.left), y0 = Math.max(0, b.top), x1 = Math.min(vw, b.right), y1 = Math.min(vh, b.bottom);
    if (x1 - x0 < 1 || y1 - y0 < 1) continue;
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2; const top = document.elementFromPoint(cx, cy);
    const over = !(top && (top === el || el.contains(top) || top.contains(el)));
    let cov = 0; if (over) for (const [px, py] of [[x0 + 1, y0 + 1], [x1 - 1, y0 + 1], [x0 + 1, y1 - 1], [x1 - 1, y1 - 1], [cx, cy]]) { const e2 = document.elementFromPoint(px, py); if (!(e2 && (e2 === el || el.contains(e2) || e2.contains(el)))) cov++; }
    res.push({t: n.textContent.trim().slice(0, 28), fs: parseFloat(cs.fontSize), color: cs.color, x: b.left, y: b.top, w: b.width, h: b.height, cx, cy, x0, y0, x1, y1, tag: el.tagName.toLowerCase(),
      over, cut: over && cov < 5, by: over && top ? (top.tagName.toLowerCase() + (top.id ? '#' + top.id : '') + (top.className && top.className.baseVal === undefined ? '.' + String(top.className).split(' ')[0] : '')) : null,
      off: !!el.closest('[disabled],[aria-disabled=true]'), clipped: (b.left < 0 || b.right > vw || b.top < 0 || b.bottom > vh)});
  }
  return res; }"""

DOM_WARM_JS = """() => {
 const res=[]; const vw=innerWidth, vh=innerHeight;
 const parse=c=>{const m=c.match(/[\\d.]+/g); if(!m)return null; const a=m.length>3?parseFloat(m[3]):1; return {r:+m[0],g:+m[1],b:+m[2],a}};
 for(const el of document.querySelectorAll('body *')){
  if(el.closest('svg')&&!el.matches('svg'))continue;
  const r=el.getBoundingClientRect(); if(r.width<2||r.height<2||r.bottom<0||r.top>vh||r.right<0||r.left>vw)continue;
  const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden')continue;
  const props=[['color',cs.color,[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())],['bg',cs.backgroundColor,true],['border',cs.borderTopColor,parseFloat(cs.borderTopWidth)>0&&cs.borderTopStyle!=='none']];
  for(const [k,c,use] of props){ if(!use)continue; const p=parse(c); if(p&&p.a>=.3) res.push({k,tag:el.tagName.toLowerCase(),cls:String(el.className&&el.className.baseVal===undefined?el.className:'').slice(0,24),c:[p.r,p.g,p.b],txt:(el.textContent||'').trim().slice(0,16)});}
 }
 return res;}"""

def warm_hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255); h *= 360
    return (h <= 52 or h >= 345) and s >= .45 and v >= .6

def pixel_points(png, blk=6):
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float) / 255
    mx, mn = im.max(2), im.min(2); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    d = np.maximum(mx - mn, 1e-9); r, g, b = im[..., 0], im[..., 1], im[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    m = ((h <= 52) | (h >= 345)) & (s >= .45) & (v >= .6) & (mx - mn > 0)
    H, W = m.shape; hb, wb = H // blk, W // blk
    cnt = m[:hb * blk, :wb * blk].reshape(hb, blk, wb, blk).sum((1, 3))
    grid = cnt >= 6
    g2 = grid.copy()
    for dy, dx in itertools.product(range(-2, 3), repeat=2):
        g2 |= np.roll(np.roll(grid, dy, 0), dx, 1)
    lab = np.zeros(g2.shape, int); n = 0; comps = []
    for y, x in zip(*np.where(g2)):
        if lab[y, x]: continue
        n += 1; st = [(y, x)]; lab[y, x] = n; cells = []
        while st:
            cy, cx = st.pop(); cells.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < g2.shape[0] and 0 <= nx < g2.shape[1] and g2[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n; st.append((ny, nx))
        ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
        px = int(sum(cnt[c] for c in cells if grid[c]))
        comps.append((px, min(xs) * blk, min(ys) * blk, (max(xs) + 1) * blk, (max(ys) + 1) * blk))
    return sorted([c for c in comps if c[0] >= 40], reverse=True)

def vp_contrast(page):
    """контраст видимых текстов в окне; перекрытые помечаются и не считаются"""
    page.mouse.move(0, 0)
    items = page.evaluate(VP_JS)
    page.add_style_tag(content='*{color:transparent !important;-webkit-text-fill-color:transparent !important;text-shadow:none !important; transition:none !important; animation:none !important} svg{opacity:0 !important}')
    page.wait_for_timeout(300)
    png = page.screenshot()
    page.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    for it in items:
        it['cr'] = None
        if it['over']: continue
        x0, y0, x1, y1 = int(it['x0']), int(it['y0']), int(it['x1']) + 1, int(it['y1']) + 1
        reg = im[y0:y1, x0:x1]
        if reg.size == 0: continue
        lum = 0.2126 * ((reg[..., 0] / 255) ** 2.2) + 0.7152 * ((reg[..., 1] / 255) ** 2.2) + 0.0722 * ((reg[..., 2] / 255) ** 2.2)
        col = parse(it['color'])[:3]; c_min = 99
        for fn in (np.argmax, np.argmin):
            yy, xx = np.unravel_index(fn(lum), lum.shape)
            c_min = min(c_min, cr(col, reg[yy, xx]))
        it['cr'] = c_min
    return items

def summarize(items):
    act = [i for i in items if i['cr'] is not None and not i['off']]
    off = [i for i in items if i['cr'] is not None and i['off']]
    ov = [i for i in items if i['over']]; cut = [i for i in ov if i['cut']]
    mn = min(act, key=lambda i: i['cr']) if act else None
    s = f"текстов в окне {len(items)}; перекрыто {len(ov)} (из них частично срезано {len(cut)}, полностью скрыто {len(ov) - len(cut)}); контраст мин {mn['cr']:.2f} ({mn['t']!r}) ниже 4.5: {sum(1 for i in act if i['cr'] < 4.5)} из {len(act)}" if mn else f"текстов {len(items)}; перекрыто {len(ov)}; активных без перекрытия 0"
    if off: s += f"; неактивных (отдельно) {len(off)}, мин {min(i['cr'] for i in off):.2f}"
    if ov: s += '; перекрыты: ' + ', '.join(f"{i['t']!r} под {i['by']}" for i in ov[:4])
    return s, len(ov), (mn['cr'] if mn else None), len(cut)
