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

def sweep(page, label):
    """прокрутка страницы шагами: каждый текст берём в лучшем (неперекрытом) положении"""
    page.evaluate("document.documentElement.style.scrollBehavior='auto'")
    H = page.evaluate("document.documentElement.scrollHeight"); vh = page.evaluate("innerHeight")
    best = {}; y = 0
    while True:
        page.evaluate(f"scrollTo(0,{y})"); page.wait_for_timeout(250)
        sy = page.evaluate("scrollY")
        for it in vp_contrast(page):
            k = (it['t'], round(it['x']), round(it['y'] + sy))
            if k not in best or (best[k]['over'] and not it['over']): best[k] = it
        if sy + vh >= H - 2: break
        y = sy + int(vh * .6)
    page.evaluate("scrollTo(0,0)"); page.wait_for_timeout(200)
    its = list(best.values()); never = [i for i in its if i['over']]
    act = [i for i in its if i['cr'] is not None and not i['off']]
    mn = min(act, key=lambda i: i['cr'])
    P(f"  [{label}: вся страница прокруткой] текстов {len(its)}; ни разу не видны без перекрытия {len(never)}; контраст мин {mn['cr']:.2f} ({mn['t']!r}); ниже 4.5: {sum(1 for i in act if i['cr'] < 4.5)} из {len(act)}")

def run(pw, dev, lang):
    w, h = DEV[dev]; ph = dev == 'phone'
    br = pw.chromium.launch(args=ARGS)
    ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=ph)
    ctx.add_init_script(INIT)
    page = ctx.new_page(); console = []; ext = []
    page.on('console', lambda m: console.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append(('pageerror', str(e))))
    page.on('requestfailed', lambda r: console.append(('reqfail', r.url)))
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    sfx = '?lang=en' if lang == 'en' else ''
    def go(extra=''):
        q = (sfx + ('&' if sfx else '?') + extra) if extra else sfx
        page.goto(URL + q); page.evaluate("document.documentElement.style.scrollBehavior='auto'"); page.wait_for_timeout(900)
    def settle(): page.mouse.move(0, 0); page.wait_for_timeout(200)
    def frame(n, name, full=False, ctr=True):
        P(f'   [t] кадр {n} t={page.evaluate("Math.round(performance.now())")} cls={page.evaluate("window.__cls"):.4f}')
        settle()
        png = page.screenshot()
        if lang == 'uk':
            open(os.path.join(SH, f'r10-{dev}-uk-{n}-{name}-view.png'), 'wb').write(png)
            if full: page.screenshot(path=os.path.join(SH, f'r10-{dev}-uk-{n}-{name}-full.png'), full_page=True)
        comps = pixel_points(png)
        s = page.evaluate("() => [document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight, Math.round(scrollY)]")
        items = vp_contrast(page)
        mf = min(items, key=lambda i: i['fs'])
        cs, nov, cmin, ncut = summarize(items)
        P(f'  [{n}-{name}] scrollWidth {s[0]}/body {s[1]} vs окно {s[2]} {"OK" if s[0] == s[2] and s[1] <= s[2] else "ПЛОХО"}; scrollY {s[4]}; '
          f'мин.шрифт {mf["fs"]}px {"OK" if mf["fs"] >= 16 else "ПЛОХО"} ({mf["t"]!r}); {cs}; '
          f'тёплые точки {len(comps)} {"OK(≤4)" if len(comps) <= 4 else "ПЛОХО(>4)"}: ' + '; '.join(f'{c[0]}px x{c[1]}–{c[3]} y{c[2]}–{c[4]}' for c in comps))
        return nov, ncut
    def anchor(sec):
        page.evaluate("document.documentElement.style.scrollBehavior='auto'")
        page.click(f'#nav a[data-sec={sec}]'); page.wait_for_timeout(900)
    def gap(sec):
        return page.evaluate("""(id) => { const nb = document.getElementById('nav').getBoundingClientRect().bottom;
          const hd = document.querySelector('#' + id + ' h1, #' + id + ' h2'); return Math.round(hd.getBoundingClientRect().top - nb); }""", sec)
    def errcheck(label, sel):
        page.wait_for_timeout(900)   # плавная прокрутка закончилась
        r = page.evaluate("""(sel) => { const nav = document.getElementById('nav').getBoundingClientRect(); const eb = document.querySelector(sel).getBoundingClientRect();
          const tx = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          while (w.nextNode()) { const n = w.currentNode; if (!n.textContent.trim()) continue; const el = n.parentElement; if (!el || el.closest('script,style,svg,nav,header,.grain') || getComputedStyle(el).visibility === 'hidden' || el.closest('details:not([open])')) continue;
            const rg = document.createRange(); rg.selectNodeContents(n); const b = rg.getBoundingClientRect(); if (b.width < 1 || b.height < 1 || b.bottom < 0 || b.top > innerHeight) continue;
            if (b.top < nav.bottom && b.bottom > nav.top) tx.push([n.textContent.trim().slice(0, 22), Math.round(b.top), Math.round(b.bottom)]); }
          const own = [...document.querySelectorAll(sel + ' *')].filter(e => e.children.length === 0 && e.textContent.trim()).map(e => { const b = e.getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom)]; });
          return {nav: [Math.round(nav.top), Math.round(nav.bottom)], err: [Math.round(eb.top), Math.round(eb.bottom)], H: innerHeight, scrollY: Math.round(scrollY), under: tx, errTexts: own, fixedBar: (() => { const l = document.querySelector('.lesson-card .lc-row'); const c = getComputedStyle(l); return c.position === 'fixed' ? Math.round(l.getBoundingClientRect().top) : null; })()}; }""", sel)
        ok = not r['under'] and r['err'][0] >= r['nav'][1] and r['err'][1] <= (r['fixedBar'] or r['H'])
        P(f"  [{label}: ошибка vs шапка] шапка y {r['nav'][0]}–{r['nav'][1]}; блок ошибки y {r['err'][0]}–{r['err'][1]} (окно {r['H']}, липкая кнопка с y {r['fixedBar']}); тексты ошибки y {r['errTexts']}; текстов, пересекающих шапку (полностью или частично): {len(r['under'])} {r['under'][:3]}; ошибка не под шапкой и не под кнопкой: {r['err'][0] >= r['nav'][1] and r['err'][1] <= (r['fixedBar'] or r['H'])} -> {'OK' if ok else 'ПЛОХО'}")
    P(f'== {dev} {w}x{h} {lang} (весь замер с --disable-lcd-text) ==')

    # ---------- 1 покой ----------
    go('demo=early'); frame(1, 'rest')
    rest_txt = page.inner_text('body')
    card = page.inner_text('#lessonCard')
    P(f'  [логика, рано 16:20] кнопка disabled: {page.evaluate("document.querySelector(`#enter`).disabled")}; aria-disabled: {page.evaluate("document.querySelector(`#enter`).getAttribute(`aria-disabled`)")}; подпись: {page.inner_text("#enter")!r}; emo {page.evaluate("document.querySelector(`#page`).dataset.emo")}')
    P(f'  [покой, п.3] «Далі/Next» на странице: {len(re.findall(r"Далі|Next(?! lesson)", rest_txt))}; «Іде зараз/In progress»: {len(re.findall(r"Іде зараз|In progress", rest_txt))}; «кімната відкриється/room opens» (все вхождения): {len(re.findall(r"[Кк]імната відкриється|room opens", rest_txt))}; «вхід відкриється/entry opens»: {len(re.findall(r"вхід відкриється|entry opens", rest_txt))}')
    btn = page.evaluate("""() => { const b = document.querySelector('#enter'); const cs = getComputedStyle(b); return {bg: cs.backgroundColor, bs: cs.borderTopStyle, bw: cs.borderTopWidth, col: cs.color}; }""")
    cbtn = cr(parse(btn['col'])[:3], parse(btn['bg'])[:3])
    P(f'  [неактивный вход, п.5] фон {btn["bg"]}, граница {btn["bs"]} {btn["bw"]} (не dashed: {btn["bs"] != "dashed"}), контраст подписи {cbtn:.2f}')
    if ph:
        P('  [phone, rest] ' + page.evaluate("""() => { const hd = document.querySelector('#day h2').getBoundingClientRect(); const bar = document.querySelector('.lc-row').getBoundingClientRect(); return `заголовок «Ваш день» y ${Math.round(hd.top)}–${Math.round(hd.bottom)}, панель с y ${Math.round(bar.top)}: ` + (hd.bottom <= bar.top - 32 ? 'целиком над затуханием' : hd.bottom <= bar.top ? 'над панелью (в зоне затухания)' : hd.top >= bar.top ? 'целиком под панелью' : 'СРЕЗАН'); }"""))

    # ---------- 2 вход открыт ----------
    go(); frame(2, 'open', full=True)
    sweep(page, 'open'); P(f'   [t] после sweep open t={page.evaluate("Math.round(performance.now())")} cls={page.evaluate("window.__cls"):.4f}')
    g = page.evaluate("""() => { const q = s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
      return {card: q('#lessonCard'), lumo: q('.lumo-wrap'), btn: q('#enter'), nav: q('#nav'), say: q('#say'), meta: q('.lc-meta'), when: q('#enterNote'), H: innerHeight}; }""")
    P(f'  [open] карточка {g["card"]}; Люмо {g["lumo"]}; кнопка {g["btn"]}; реплика {g["say"]}; нав {g["nav"]}; время {g["meta"]}')
    if not ph:
        P(f'  [open, п.3 карман] время x{g["meta"][0]}–{g["meta"][2]}, кнопка x{g["btn"][0]}–{g["btn"][2]} на одной строке (y {g["meta"][1]}–{g["meta"][3]} / {g["btn"][1]}–{g["btn"][3]}): зазор время→кнопка {g["btn"][0] - g["meta"][2]} px; кнопка → Люмо {g["lumo"][0] - g["btn"][2]} px')
    sm = page.evaluate("() => ['today','week','groups','plan','notes','swap'].map(i => getComputedStyle(document.getElementById(i)).scrollMarginTop)")
    P(f'  scroll-margin-top разделов: {sm}; форм/ошибок: {page.evaluate("[getComputedStyle(document.querySelector(`#noteForm`)).scrollMarginTop, getComputedStyle(document.querySelector(`#noteErr`)).scrollMarginTop]")}')
    kn = page.evaluate("() => { const t = document.body.innerText; return [(t.match(/Київ|Kyiv/g) || []).length, (document.getElementById('week').innerText.match(/Київ|Kyiv/g) || []).length]; }")
    P(f'  повторы «Київ/Kyiv» (вся страница / неделя): {kn[0]} / {kn[1]}')
    # --- п.5: шапка, пилюли, dev ---
    if not ph:
        hd = page.evaluate("""() => { const b = document.querySelector('.seg button[aria-pressed=true]'); const cs = getComputedStyle(b); const sg = getComputedStyle(b.parentElement);
          const inf = document.querySelector('.lc-foot .info'); const ic = getComputedStyle(inf);
          const dv = document.querySelector('.dev summary').getBoundingClientRect(); const rs = [...document.querySelectorAll('.today, .sec, .day, #nav a, .dl, .lesson-card, .foot')].map(e => e.getBoundingClientRect());
          const hit = rs.filter(r => !(dv.right < r.left || dv.left > r.right || dv.bottom < r.top || dv.top > r.bottom)).length;
          const t = document.querySelector('#nav a[data-sec=today]').getBoundingClientRect();
          return {selBg: cs.backgroundColor, selBorder: cs.borderTopWidth + ' ' + cs.boxShadow, segBorder: sg.borderTopWidth, infBorder: ic.borderTopWidth, infBg: ic.backgroundColor, infH: Math.round(inf.getBoundingClientRect().height),
            dev: [Math.round(dv.left), Math.round(dv.top), Math.round(dv.right), Math.round(dv.bottom)], hit, devTxt: document.querySelector('.devtxt').textContent, contentRight: Math.round(Math.max(...[...document.querySelectorAll('.lesson-card, .day')].map(e => e.getBoundingClientRect().right))), todayTab: [Math.round(t.left), Math.round(t.top), Math.round(t.right), Math.round(t.bottom)]}; }""")
        P(f'  [шапка, п.5] выбранный: фон {hd["selBg"]}, рамка/тень «{hd["selBorder"]}»; рамка контейнера {hd["segBorder"]} (пилюли в пилюле нет)')
        P(f'  [инфо-пилюли, п.5] «.info»: рамка {hd["infBorder"]}, фон {hd["infBg"]}')
        P(f'  [кнопка прототипа, п.5] подпись {hd["devTxt"]!r}; прямоугольник {hd["dev"]}; правый край контента {hd["contentRight"]}; пересечений с блоками контента: {hd["hit"]}; вкладка «Сьогодні» {hd["todayTab"]}')
    if ph:
        pb = page.evaluate("""() => { const r = document.querySelector('.lesson-card .lc-row'); const cs = getComputedStyle(r); const b = document.querySelector('#enter').getBoundingClientRect();
          let rule = ''; try { rule = [...document.styleSheets].flatMap(s => { try { return [...s.cssRules]; } catch (e) { return []; } }).flatMap(r => r.cssRules ? [...r.cssRules] : [r]).map(r => r.cssText).find(t => t.includes('.lc-row') && t.includes('safe-area')) || ''; } catch (e) {}
          const bf = getComputedStyle(r, '::before');
          return {pad: cs.paddingBottom, pos: cs.position, btnBottom: Math.round(b.bottom), H: innerHeight, barTop: Math.round(r.getBoundingClientRect().top), src: (rule.match(/padding: [^;]*;/) || [''])[0], bf: bf.backgroundImage, bfh: bf.height, bg: cs.backgroundColor}; }""")
        P(f'  [липкая панель, п.4] position {pb["pos"]}, padding-bottom {pb["pad"]} (css: {pb["src"]}); низ кнопки y {pb["btnBottom"]} при окне {pb["H"]} -> отступ {pb["H"] - pb["btnBottom"]}; панель с y {pb["barTop"]}; фон {pb["bg"]}')
        css = open(os.path.join(HERE, 'style.css'), encoding='utf-8').read()
        P(f'  [css] отступ панели: ' + ('max(24px, calc(12px + env(safe-area-inset-bottom, 0px)))' if 'max(24px, calc(12px + env(safe-area-inset-bottom, 0px)))' in css else 'НЕТ формулы'))
        P(f'  [затухание над панелью] ::before высота {pb["bfh"]}, градиент {pb["bf"]} (в цвет фона rgb(30,20,36), а не в чёрный: {"rgba(0, 0, 0" not in pb["bf"] and "rgba(30, 20, 36, 0)" in pb["bf"]})')
        nv = page.evaluate("""() => { const n = document.getElementById('navIn'); const a = [...n.querySelectorAll('a')]; const tops = new Set(a.map(x => Math.round(x.getBoundingClientRect().top))); const cs = getComputedStyle(n);
          const nb = getComputedStyle(document.getElementById('nav'), '::after');
          return {rows: tops.size, sw: n.scrollWidth, cw: n.clientWidth, snap: cs.scrollSnapType, sbw: cs.scrollbarWidth, sbH: n.offsetHeight - n.clientHeight, fr: document.getElementById('nav').hasAttribute('data-fr'), fl: document.getElementById('nav').hasAttribute('data-fl'), fade: nb.backgroundImage, fo: nb.opacity, lefts: a.map(x => Math.round(x.getBoundingClientRect().left)), navH: Math.round(document.getElementById('nav').getBoundingClientRect().height), align: cs.overflowX}; }""")
        P(f'  [вкладки, п.4] строк: {nv["rows"]}; scrollWidth {nv["sw"]} > clientWidth {nv["cw"]}; overflow-x {nv["align"]}; scroll-snap-type {nv["snap"]}; scrollbar-width {nv["sbw"]}, высота полосы {nv["sbH"]}px; fade справа включён {nv["fr"]} (opacity {nv["fo"]}), слева {nv["fl"]}; высота нав {nv["navH"]}px')
        P(f'  [вкладки] fade-градиент: {nv["fade"]}')
        page.evaluate("document.getElementById('navIn').scrollLeft = 9999"); page.wait_for_timeout(400)
        P(f'  [вкладки] после прокрутки в конец: fade слева {page.evaluate("document.getElementById(`nav`).hasAttribute(`data-fl`)")}, справа {page.evaluate("document.getElementById(`nav`).hasAttribute(`data-fr`)")}')
        page.evaluate("document.getElementById('navIn').scrollLeft = 0"); page.wait_for_timeout(200)
        P('  [phone, open] ' + page.evaluate("""() => { const hd = document.querySelector('#day h2').getBoundingClientRect(); const bar = document.querySelector('.lc-row').getBoundingClientRect(); return `заголовок «Ваш день» y ${Math.round(hd.top)}–${Math.round(hd.bottom)}, панель с y ${Math.round(bar.top)}: ` + (hd.bottom <= bar.top - 32 ? 'целиком над затуханием' : hd.bottom <= bar.top ? 'над панелью (в зоне затухания)' : hd.top >= bar.top ? 'целиком под панелью' : 'СРЕЗАН'); }"""))
    # --- Люмо: ядро, форма, размер, наклон, взгляд, отсвет ---
    mark = open(os.path.join(HERE, 'assets', 'lumo-v5r8-mark.svg'), encoding='utf-8').read()
    ref_body = re.findall(r' d="([^"]+)"', mark)[0]; ref_inner = re.findall(r' d="([^"]+)"', mark)[1]
    lm = page.evaluate("""() => { const s = document.querySelector('.lumo'); const ps = [...s.querySelectorAll('path')].filter(p => !p.closest('.sparks'));
      const wr = document.querySelector('.lumo-wrap').getBoundingClientRect(); const m = new DOMMatrix(getComputedStyle(s).transform);
      const say = document.querySelector('#say'); const sc = getComputedStyle(say);
      const card = getComputedStyle(document.querySelector('#lessonCard'));
      return {body: ps[0].getAttribute('d'), bodyFill: ps[0].getAttribute('fill'), inner: ps[1].getAttribute('d'), innerFill: ps[1].getAttribute('fill'), eyeFill: ps[2].getAttribute('fill'), glint: [...s.querySelectorAll('.glint')].map(c => c.getAttribute('fill')),
        gaze: s.querySelector('.gaze').getAttribute('transform'), eyes: s.querySelector('.eyes > g').getAttribute('transform'), w: Math.round(wr.width), h: Math.round(wr.height), ang: Math.round(Math.atan2(m.b, m.a) * 180 / Math.PI * 10) / 10,
        edge: sc.borderTopColor, shadow: sc.boxShadow, cardBg: card.backgroundImage.slice(0, 300), filter: getComputedStyle(s).filter, FB: (document.documentElement.outerHTML.match(/FBEFDF/gi) || []).length}; }""")
    P(f'  [Люмо, п.6] тело = путь r8-mark.svg: {lm["body"] == ref_body}; сердцевина = r8: {lm["inner"] == ref_inner}; заливки: тело {lm["bodyFill"]}, сердцевина {lm["innerFill"]}, глаза {lm["eyeFill"]}, блики {lm["glint"]}')
    P(f'  [Люмо, п.3] размер {lm["w"]}×{lm["h"]} px; наклон {lm["ang"]}°; сдвиг глаз {lm["eyes"]}, сдвиг бликов {lm["gaze"]} (влево-вниз = минус по x, плюс по y); отсвет: рамка пузыря сверху {lm["edge"]}; тень пузыря {lm["shadow"]}')
    P(f'  [Люмо] фон карточки (градиент в цвет пламени с нулевой прозрачностью, не в чёрный): {"rgba(255, 154, 92, 0)" in lm["cardBg"] and "rgba(0, 0, 0, 0)" not in lm["cardBg"]} :: {lm["cardBg"][:130]}')
    page.add_style_tag(content='*{animation:none!important}'); page.wait_for_timeout(150)
    gp = page.evaluate("""() => { const wr = document.querySelector('.lumo-wrap').getBoundingClientRect(); const sy = document.querySelector('#say').getBoundingClientRect();
      const flameBottom = wr.bottom - wr.height * (12 / 112); const tip = sy.top - 12.3; return {gap: Math.round((tip - flameBottom) * 10) / 10, tailX: Math.round(sy.right - 44 - 8), lumoCx: Math.round((wr.left + wr.right) / 2)}; }""")
    P(f'  [пузырь↔Люмо] зазор «кончик хвостика — нижний край пламени» в покое анимации: {gp["gap"]} px (+до 8 px при float-анимации -> макс {gp["gap"] + 8}); ' + ('ТРЕБОВАНИЕ ≤16 ' + ('OK' if gp['gap'] + 8 <= 16 else 'ПЛОХО') if ph else '(десктоп, требование ≤16 только для телефона)'))
    page.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    # пиксели верхней кромки пузыря vs нижней
    settle(); png = page.screenshot(); im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    sb = page.evaluate("() => { const r = document.querySelector('#say').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }")
    xa, xb = int(sb[0] + 40), int(sb[2] - 40)
    topc = im[int(sb[1]) - 6:int(sb[1]) - 2, xa:xb].reshape(-1, 3).mean(0); botc = im[int(sb[3]) + 3:int(sb[3]) + 7, xa:xb].reshape(-1, 3).mean(0)
    P(f'  [отсвет на кромке] средний цвет полосы НАД верхней кромкой пузыря rgb{tuple(int(v) for v in topc)} vs полоса ПОД нижней rgb{tuple(int(v) for v in botc)} (теплее сверху: {topc[0] - topc[2] > botc[0] - botc[2] + 6})')

    # меню на телефоне
    if ph:
        page.focus('#avatarBtn'); page.keyboard.press('Enter'); page.wait_for_timeout(300)
        ex = page.evaluate("[document.getElementById('avatarBtn').getAttribute('aria-expanded'), document.getElementById('menu').getBoundingClientRect().width > 0]")
        P(f'  меню с клавиатуры: aria-expanded {ex[0]}, видно {ex[1]}; подпись dev-кнопки в меню: {page.inner_text("#devSum")!r}')
        frame(10, 'menu')
        page.click('[data-tz=kyiv]'); page.wait_for_timeout(300)
        P(f'  после «Київ» время в карточке: {page.evaluate("document.querySelector(`#lessonCard .lc-time b`).textContent")}; подпись неактивного входа: n/a (open)')
        page.click('[data-tz=both]'); page.wait_for_timeout(200)
        page.keyboard.press('Escape'); page.wait_for_timeout(200)
        P(f'  Esc закрывает меню: {page.evaluate("document.getElementById(`avatarBtn`).getAttribute(`aria-expanded`)") == "false"}; фокус на аватаре: {page.evaluate("document.activeElement.id") == "avatarBtn"}')
    # --- 3 вход нажат ---
    page.click('#enter'); page.wait_for_timeout(500)
    frame(3, 'entered')
    P(f'  [вход нажат] emo {page.evaluate("document.querySelector(`#page`).dataset.emo")}; заметка: {page.inner_text("#enterNote")!r}')
    if ph:
        P('  [phone, entered] ' + page.evaluate("""() => { const hd = document.querySelector('#day h2').getBoundingClientRect(); const bar = document.querySelector('.lc-row').getBoundingClientRect(); return `заголовок «Ваш день» y ${Math.round(hd.top)}–${Math.round(hd.bottom)}, панель с y ${Math.round(bar.top)}: ` + (hd.bottom <= bar.top - 32 ? 'целиком над затуханием' : hd.bottom <= bar.top ? 'над панелью (в зоне затухания)' : hd.top >= bar.top ? 'целиком под панелью' : 'СРЕЗАН'); }"""))
    # --- 4 live ---
    go('demo=live'); frame(4, 'live', full=True)
    sweep(page, 'live')
    txt = page.inner_text('#lessonCard')
    P(f'  [live, логика] «Зараз · лишилось 33 хв»: {bool(re.search(r"Зараз · лишилось 33 хв|Now · 33 min left", txt))}; «Іде зараз/In progress» в карточке: {len(re.findall(r"Іде зараз|In progress", txt))} (должно 0); «Найближчий» нет: {not re.search(r"Найближчий|Next lesson", txt)}; «Вхід відкрито» нет: {not re.search(r"Вхід відкрито|Entry is open|open from", txt)}')
    P(f'  [live] реплика: {page.inner_text("#say")!r}; emo {page.evaluate("document.querySelector(`#page`).dataset.emo")}; рот видим: {page.evaluate("getComputedStyle(document.querySelector(`.lumo .mouth`)).opacity")}; искры: {page.evaluate("getComputedStyle(document.querySelector(`.lumo .sparks`)).opacity")}')
    dm = page.evaluate(DOM_WARM_JS)
    wl = [d for d in dm if warm_hsv(*d['c']) and not d['cls'].startswith('lumo')]
    P(f'  [live] тёплые элементы по CSS (вне SVG): {[(d["tag"], d["k"], d["cls"], d["txt"]) for d in wl]}; заливок оранжевым фоном: {sum(1 for d in wl if d["k"] == "bg")}')
    if ph:
        P('  [phone, live] ' + page.evaluate("""() => { const hd = document.querySelector('#day h2').getBoundingClientRect(); const bar = document.querySelector('.lc-row').getBoundingClientRect(); return `заголовок «Ваш день» y ${Math.round(hd.top)}–${Math.round(hd.bottom)}, панель с y ${Math.round(bar.top)}: ` + (hd.bottom <= bar.top - 32 ? 'целиком над затуханием' : hd.bottom <= bar.top ? 'над панелью (в зоне затухания)' : hd.top >= bar.top ? 'целиком под панелью' : 'СРЕЗАН'); }"""))
        for s_ in ('week', 'notes'):
            anchor(s_); P(f'  [якорь {s_} на телефоне] зазор заголовок−низ вкладок: {gap(s_)} px (≥0 = не прячется)')
        P(f'  [вкладки следуют за разделом] aria-current={page.evaluate("document.querySelector(`#nav a[aria-current=true]`).dataset.sec")}; активная вкладка в окне: {page.evaluate("(() => { const a = document.querySelector(`#nav a[aria-current=true]`).getBoundingClientRect(); return a.left >= 0 && a.right <= innerWidth; })()")}')
    # --- 5 неделя ---
    go(); anchor('week'); frame(5, 'week')
    P(f'  [якорь week] зазор: {gap("week")} px')
    go('tz=kyiv'); P(f'  [пояс Киев] время в карточке: {page.evaluate("document.querySelector(`#lessonCard .lc-time b`).textContent")}'); go()
    anchor('groups'); frame(7, 'groups'); P(f'  [якорь groups] зазор: {gap("groups")} px')
    page.click('[data-grp=owls]'); page.wait_for_timeout(200)
    anchor('plan'); P(f'  [якорь plan] зазор: {gap("plan")} px'); page.click('[data-chk="0"]'); page.wait_for_timeout(200); frame(8, 'plan')
    # --- заметки: ошибка ---
    anchor('notes'); P(f'  [якорь notes] зазор: {gap("notes")} px')
    saved0 = page.evaluate("document.querySelectorAll('.saved li').length")
    page.fill('#noteText', 'Call parent +48 600 100 200')
    page.evaluate("document.documentElement.style.scrollBehavior='auto'")
    page.click('#noteForm button[type=submit]', force=True); page.wait_for_timeout(1500)
    ev = page.evaluate("""() => { const e = document.querySelector('#noteErr .err'); const m = e && e.querySelector('mark'); const b = document.querySelector('#noteForm button[type=submit]'); const bs = getComputedStyle(b); const er = document.getElementById('noteErr').getBoundingClientRect();
      const nb = document.getElementById('nav').getBoundingClientRect().bottom;
      return {err: !!e, mark: m ? m.textContent : null, why: e ? e.querySelector('b').textContent : null, border: e ? getComputedStyle(e).borderTopColor : null, aria: b.getAttribute('aria-disabled'), op: bs.opacity, cls: b.className, saved: document.querySelectorAll('.saved li').length,
        errMid: Math.round((er.top + er.bottom) / 2), H: innerHeight, nb: Math.round(nb), formTop: Math.round(document.getElementById('noteForm').getBoundingClientRect().top), ta: document.activeElement.id, ariaInvalid: document.getElementById('noteText').hasAttribute('aria-invalid')}; }""")
    P(f'  [ошибка, п.2] показана: {ev["err"]}; подсвечено: {ev["mark"]!r}; «чому»: {ev["why"]!r}; рамка {ev["border"]}; «Зберегти»: aria-disabled={ev["aria"]!r}, opacity {ev["op"]}, class {ev["cls"]!r}; записей {saved0} -> {ev["saved"]} (не должно прибавиться); фокус на {ev["ta"]!r}')
    P(f'  [ошибка] scrollIntoView(center): середина блока ошибки y {ev["errMid"]} при окне {ev["H"]} (центр {ev["H"] // 2}); верх формы y {ev["formTop"]} (низ шапки/вкладок {ev["nb"]}) -> форма под шапкой: {ev["formTop"] < ev["nb"]}')
    errcheck('notes', '#noteErr'); nov, ncut = frame(6, 'notes-error')
    P(f'  [ошибка] ПЕРЕКРЫТЫХ текстов в кадре ошибки: {nov}, из них частично срезано {ncut} (требование 0)')
    page.click('#noteForm button[type=submit]', force=True); page.wait_for_timeout(500)
    P(f'  [ошибка, клик по «Зберегти» при ошибке] записей {page.evaluate("document.querySelectorAll(`.saved li`).length")} (без роста: {page.evaluate("document.querySelectorAll(`.saved li`).length") == saved0}); ошибка осталась: {page.evaluate("!!document.querySelector(`#noteErr .err`)")}; фокус на: {page.evaluate("document.activeElement.id")!r}')
    page.fill('#noteText', 'Topic understood. Review apple, bread.'); page.wait_for_timeout(200)
    P(f'  [исправление текста] ошибка скрыта: {page.evaluate("!document.querySelector(`#noteErr .err`)")}; aria-disabled снят: {page.evaluate("!document.querySelector(`#noteForm button[type=submit]`).hasAttribute(`aria-disabled`)")}; opacity {page.evaluate("getComputedStyle(document.querySelector(`#noteForm button[type=submit]`)).opacity")}')
    page.click('#noteForm button[type=submit]', force=True); page.wait_for_timeout(300)
    P(f'  [заметки] нормальная заметка сохранена: записей {page.evaluate("document.querySelectorAll(`.saved li`).length")}')
    for bad in ('mail me a@b.co', 'https://example.org/x', 'мій телеграм'):
        page.fill('#noteText', bad); page.click('#noteForm button[type=submit]', force=True); page.wait_for_timeout(120)
        P(f'  [заметки] {bad!r} отклонено: {page.evaluate("!!document.querySelector(`#noteErr .err`)")}')
    page.fill('#noteText', '')
    # --- замена ---
    anchor('swap'); P(f'  [якорь swap] зазор: {gap("swap")} px')
    # радиокнопки: клавиатурный фокус
    page.focus('input[value=l6]'); page.keyboard.press('ArrowDown'); page.wait_for_timeout(200)
    frame(9, 'swap')
    rd = page.evaluate("""() => { const all = [...document.querySelectorAll('.opt input')]; const f = document.activeElement; const cs = el => getComputedStyle(el);
      return {n: all.length, app: cs(all[0]).appearance, w: cs(all[0]).width, unchecked: all.filter(i => !i.checked).map(i => [cs(i).borderTopColor, cs(i).backgroundImage.slice(0, 20)]).slice(0, 1), checked: all.filter(i => i.checked).map(i => [cs(i).borderTopColor, cs(i).backgroundImage.slice(0, 60)]),
        focus: f.matches(':focus-visible'), ol: cs(f).outlineStyle + ' ' + cs(f).outlineWidth + ' ' + cs(f).outlineColor, br: cs(f).borderRadius}; }""")
    P(f'  [радиокнопки, п.1] всего {rd["n"]}; appearance {rd["app"]}, размер {rd["w"]}; не выбрана: рамка/фон {rd["unchecked"]}; выбрана: {rd["checked"]}; фокус-кольцо (с клавиатуры): focus-visible {rd["focus"]}, outline {rd["ol"]}, radius {rd["br"]}')
    # размер точки по пикселям @4x
    ctx4 = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=4)
    p4 = ctx4.new_page(); p4.goto(URL + sfx); p4.wait_for_timeout(600)
    p4.evaluate("document.documentElement.style.scrollBehavior='auto'; document.querySelector('#swap').scrollIntoView()"); p4.wait_for_timeout(500)
    p4.focus('input[value=l6]'); p4.keyboard.press('ArrowDown'); p4.wait_for_timeout(300)
    bb = p4.evaluate("(() => { const r = document.querySelector('.opt input:checked').getBoundingClientRect(); const u = document.querySelector('.opt input:not(:checked)').getBoundingClientRect(); return [r.left, r.top, r.width, u.left, u.top]; })()")
    def dot(x, y, wd):
        png = p4.screenshot(clip={'x': x - 2, 'y': y - 2, 'width': wd + 4, 'height': wd + 4}); a = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
        hh, ww = a.shape[:2]; yy, xx = np.mgrid[:hh, :ww]; rr = np.hypot(xx - ww / 2, yy - hh / 2)
        cream = np.linalg.norm(a - np.array([255, 227, 184]), axis=2) < 40
        return cream, rr
    cream, rr = dot(bb[0], bb[1], bb[2]); inner = cream & (rr < 9 * 4)
    d_px = 2 * np.sqrt(inner.sum() / np.pi) / 4
    cream_u, rr_u = dot(bb[3], bb[4], bb[2]); inner_u = cream_u & (rr_u < 9 * 4)
    P(f'  [радиокнопки] кремовая точка выбранной ≈{d_px:.1f} px при внешнем диаметре {bb[2]:.0f} px = {d_px / bb[2] * 100:.0f}% (цель ≈50%); у невыбранной кремовых пикселей внутри: {int(inner_u.sum())} (должно ~0)')
    if lang == 'uk' and not ph:
        p4.screenshot(path=os.path.join(SH, 'r10-desktop-uk-9b-swap-radio-zoom-view.png'), clip={'x': 60, 'y': max(0, bb[1] - 90), 'width': 700, 'height': 330})
    ctx4.close()
    page.click('input[value=l7]'); page.click('#swapForm button[type=submit]'); page.wait_for_timeout(400)
    P(f'  [замена] статус после отправки: {page.inner_text("#swap .st")!r}')
    frame(11, 'swap-sent')
    cur = []
    for s_ in ('today', 'week', 'groups', 'plan', 'notes', 'swap'):
        anchor(s_); cur.append(page.evaluate("document.querySelector('#nav a[aria-current=true]')?.dataset.sec"))
    P(f'  активный пункт навигации по якорям: {cur}')
    hits = re.findall(r'@|\+\d{2,}|https?:|\b\d{3}[ -]\d{3}[ -]\d{3}\b', page.evaluate("document.body.innerText"))
    P(f'  контакты в видимом тексте страницы: {hits}')
    # swap: ошибка комментария -> aria-disabled
    go(); P('   [t] go t=' + str(page.evaluate('Math.round(performance.now())'))); anchor('swap'); P('   [t] anchor t=' + str(page.evaluate('Math.round(performance.now())') ) + ' cls=' + str(page.evaluate('window.__cls'))); page.fill('#swapNote', 'write me t.me/abc'); P('   [t] fill t=' + str(page.evaluate('Math.round(performance.now())') ) + ' cls=' + str(page.evaluate('window.__cls'))); page.click('#swapForm button[type=submit]', force=True); P('   [t] click t=' + str(page.evaluate('Math.round(performance.now())') ) + ' cls=' + str(page.evaluate('window.__cls'))); page.wait_for_timeout(1300)
    errcheck('swap', '#swapErr'); P(f'  [заміна, ошибка комментария] aria-disabled={page.evaluate("document.querySelector(`#swapForm button[type=submit]`).getAttribute(`aria-disabled`)")!r}; перекрытых текстов в кадре: {summarize(vp_contrast(page))[1]} (срезано частично {summarize(vp_contrast(page))[3]})')
    page.fill('#swapNote', 'ok'); page.wait_for_timeout(150)
    P(f'  [заміна, исправление] aria-disabled снят: {page.evaluate("!document.querySelector(`#swapForm button[type=submit]`).hasAttribute(`aria-disabled`)")}')
    P(f'  CLS за сценарий: {page.evaluate("window.__cls"):.4f}'); P('  CLS источники: ' + str(page.evaluate("window.__src||[]"))[:700])
    P(f'  ошибки/предупреждения консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    br.close()

DEVS = ('desktop', 'phone') if len(sys.argv) < 2 else (sys.argv[1],)
with sync_playwright() as pw:
    for dev in DEVS:
        for lang in (('uk', 'en') if len(sys.argv) < 3 else (sys.argv[2],)):
            run(pw, dev, lang)

P('== пары цветов (WCAG) ==')
pairs = [('ink on panel', '#FBEFDF', '#2A1A31', 4.5), ('ink2 on panel', '#D6C3CE', '#2A1A31', 4.5), ('ink2 on page bg', '#D6C3CE', '#1E1424', 4.5),
 ('кнопка: тёмный текст на #FF7A45', '#2A1A2E', '#FF7A45', 4.5), ('неактивный вход: #E8D9E2 на #45324D', '#E8D9E2', '#45324D', 4.5),
 ('выбранный сегмент: #2A1A2E на кремовом #FFE3B8', '#2A1A2E', '#FFE3B8', 4.5), ('ошибка: розовый #FF8FA3 на panel', '#FF8FA3', '#2A1A31', 4.5),
 ('[не текст] радио: рамка ink2 vs panel2', '#D6C3CE', '#35223C', 3.0), ('[не текст] радио выбранная: кремовая точка vs panel2', '#FFE3B8', '#35223C', 3.0)]
bad = 0
for n, a, b, need in pairs:
    c = cr(hx(a), hx(b)); ok = c >= need; bad += (not ok)
    P(f'  {c:5.2f}:1 {"OK " if ok else "ПЛОХО"} (нужно {need}) {n}')
P(f'  пар ниже порога: {bad}')
open(os.path.join(SH, 'r10-metrics.txt'), 'w').write('\n'.join(out) + '\n')
