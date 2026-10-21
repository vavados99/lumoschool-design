"""Круг 8: кадры r8-* и замеры В5-родитель -> shots/r8-metrics.txt.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run_r8.py"""
import os, io, re, colorsys
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html')
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
LCD = ['--disable-lcd-text']
INIT = "window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"
out = []
def P(s=''): print(s); out.append(s)

TEXT_JS = """(scope) => {
  const root = scope ? document.querySelector(scope) : document.body;
  const res = []; const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg')) continue;
    if (el.closest('[hidden]')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    const cx = b.left + b.width / 2, cy = b.top + b.height / 2; const sy0 = scrollY;
    window.scrollTo({top: Math.max(0, b.top + sy0 - innerHeight / 2), behavior: 'instant'}); const nb = r.getBoundingClientRect();
    const hit = document.elementFromPoint(nb.left + nb.width / 2, nb.top + nb.height / 2);
    const cov = !hit || !(hit === el || el.contains(hit) || hit.contains(el)) ; window.scrollTo({top: sy0, behavior: 'instant'});
    res.push({cov, t: n.textContent.trim().slice(0, 30), fs: parseFloat(cs.fontSize), color: cs.color, x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, tag: el.tagName.toLowerCase()});
  }
  return res; }"""
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def Lm(rgb): return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
def cr(a, b):
    la, lb = Lm(a), Lm(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)
def parse(c): return [float(x) for x in re.findall(r'[\d.]+', c)[:4]]

def contrast_pixels(page, scope=None):
    items = page.evaluate(TEXT_JS, scope)
    page.add_style_tag(content='*{color:transparent !important;-webkit-text-fill-color:transparent !important;text-shadow:none !important;animation:none !important} svg{opacity:0 !important}')
    page.wait_for_timeout(250)
    png = page.screenshot(full_page=(scope is None))
    page.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    sy = page.evaluate('scrollY') if scope else 0
    worst = []
    for it in items:
        x0, y0 = int(it['x']), int(it['y']) - int(sy); x1, y1 = int(it['x'] + it['w']) + 1, int(it['y'] + it['h']) + 1 - int(sy)
        reg = im[max(0, y0):y1, max(0, x0):x1]
        if reg.size == 0: continue
        lum = 0.2126 * ((reg[..., 0] / 255) ** 2.2) + 0.7152 * ((reg[..., 1] / 255) ** 2.2) + 0.0722 * ((reg[..., 2] / 255) ** 2.2)
        col = parse(it['color'])[:3]; c_min = 99
        for fn in (np.argmax, np.argmin):
            yy, xx = np.unravel_index(fn(lum), lum.shape); c_min = min(c_min, cr(col, reg[yy, xx]))
        worst.append((c_min, it['t'], it['tag'], it.get('cov', False)))
    worst.sort(); return worst

def pixel_points(png, blk=6):   # тот же замер, что в круге 6
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float) / 255
    mx, mn = im.max(2), im.min(2); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    d = np.maximum(mx - mn, 1e-9); r, g, b = im[..., 0], im[..., 1], im[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    m = ((h <= 52) | (h >= 345)) & (s >= .45) & (v >= .6) & (mx - mn > 0)
    H, W = m.shape; hb, wb = H // blk, W // blk
    cnt = m[:hb * blk, :wb * blk].reshape(hb, blk, wb, blk).sum((1, 3)); grid = cnt >= 6
    from itertools import product
    g2 = grid.copy()
    for dy, dx in product(range(-2, 3), repeat=2): g2 |= np.roll(np.roll(grid, dy, 0), dx, 1)
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

SAY_JS = """() => { const s = document.querySelector('#say'), t = document.querySelector('#sayT'), h = document.querySelector('#sayH'); const r = s.getBoundingClientRect();
  const lh = parseFloat(getComputedStyle(t).lineHeight); const tr = t.getBoundingClientRect(); const hv = getComputedStyle(h).display !== 'none';
  return {txt: t.textContent, sh: s.scrollHeight, ch: s.clientHeight, h: r.height, lines: Math.round(tr.height / lh), th: tr.height, fs: getComputedStyle(t).fontSize, top: r.top, emo: document.querySelector('#page').dataset.emo}; }"""

BORDER_JS = """() => { const vis = []; const sel = '.tz,.seg,.kid,.nav a,.cons,.lesson,.msg,.law,.banner,.compose,.dcard,.say,.pill,.next,.t-av,.d-node,.btn-eq,.btn-main,.btn-line,.btn-danger,textarea,.bars i,.track i,.dlg';
  const cards = new Set(['tz','seg','kid','cons','lesson','msg','law','banner','compose','dcard','say','next']);
  const rows = []; for (const el of document.querySelectorAll('body *')) { if (el.closest('svg') && !el.matches('svg')) continue;
    const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const sides = ['Top','Right','Bottom','Left'].filter(s => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none' && parseFloat((cs['border' + s + 'Color'].match(/[\\d.]+/g) || [0,0,0,1])[3] ?? 1) > 0);
    rows.push({cls: (typeof el.className === 'string' ? el.className : '').split(' ')[0] || el.tagName.toLowerCase(), tag: el.tagName.toLowerCase(), b: sides.length > 0, w: sides.length ? parseFloat(cs['border' + sides[0] + 'Width']) : 0}); }
  return rows; }"""

def g_lumo_size(pg): return pg.evaluate("(()=>{const r=document.querySelector('#lumo').getBoundingClientRect(); return Math.round(r.width)+'x'+Math.round(r.height)})()")

def run_main(pw, dev):
    w, h = DEV[dev]
    br = pw.chromium.launch(args=LCD); ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=(dev == 'phone')); ctx.add_init_script(INIT)
    pg = ctx.new_page(); cons = []; ext = []
    pg.on('console', lambda m: cons.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: cons.append(('pageerror', str(e))))
    pg.on('requestfailed', lambda r: cons.append(('reqfail', r.url)))
    pg.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    pg.goto(URL); pg.wait_for_timeout(1500)
    snap = lambda name, full=False: pg.screenshot(path=os.path.join(SH, f'r8-{dev}-uk-{name}.png'), full_page=full)
    P(f'== В5 {dev} {w}x{h} UK ==')
    pg.add_style_tag(content='.lumo,.lumo *{animation-play-state:paused !important}')   # кадр без моргания
    snap('1-rest'); snap('1-rest-full', True)
    png = pg.screenshot()
    sw = pg.evaluate("[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
    P(f'  ширина страницы: html {sw[0]} / body {sw[1]} против окна {sw[2]} -> {"OK" if sw[0] == sw[2] and sw[1] <= sw[2] else "ПЛОХО"}; высота {sw[3]}')
    items = pg.evaluate(TEXT_JS, None); mf = sorted(items, key=lambda i: i['fs'])[:3]
    P(f'  мин. шрифт: {mf[0]["fs"]} px ({mf[0]["t"]!r}) -> {"OK" if mf[0]["fs"] >= 16 else "ПЛОХО <16"}')
    cp = contrast_pixels(pg)
    cov = [c for c in cp if c[3]]; cpv = [c for c in cp if not c[3]]
    P(f'  контраст текста (пиксели, вся страница; elementFromPoint в центре текста): проверено {len(cpv)}, перекрыт (не считаю) {len(cov)} {[c[1] for c in cov[:6]]}; мин {cpv[0][0]:.2f} ({cpv[0][1]!r}, {cpv[0][2]}); ниже 4.5: {sum(1 for c in cpv if c[0] < 4.5)}; худшие: {[(round(c[0], 2), c[1]) for c in cpv[:4]]}')
    comps = pixel_points(png)
    P(f'  ТЁПЛЫЕ ТОЧКИ (HSV: тон ≤52°/≥345°, насыщ ≥0,45, яркость ≥0,6; слияние ≤12 px; ≥40 px), первый экран: {len(comps)} -> {"OK (≤4)" if len(comps) <= 4 else "ПЛОХО (>4)"}')
    for c in comps: P(f'     {c[0]:6d} px  область x {c[1]}–{c[3]}, y {c[2]}–{c[4]}')
    g = pg.evaluate("""()=>{const q=s=>{const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom,r.width,r.height]};
      return {lumo:q('#lumoBox'), say:q('#say'), card:q('#nextCard'), ph:q('.t-av'), kids:q('.kids'), nav:q('#nav')}}""")
    nc = g['card']; ph = g['ph']
    P(f'  Люмо {g["lumo"][4]:.0f}x{g["lumo"][5]:.0f} x {g["lumo"][0]:.0f}–{g["lumo"][2]:.0f}, y {g["lumo"][1]:.0f}–{g["lumo"][3]:.0f}; главная карточка y {nc[1]:.0f}–{nc[3]:.0f} (x {nc[0]:.0f}–{nc[2]:.0f})')
    tb_ = pg.evaluate("document.querySelector('.teacher').getBoundingClientRect().bottom"); nimg = pg.evaluate("document.querySelectorAll('#nextCard img').length")
    P(f'  РАССТОЯНИЕ до карточки урока (верх карточки от верха страницы): {nc[1]:.0f} px из {h}; низ карточки {nc[3]:.0f}; учитель до y {tb_:.0f}')
    P(f'  фото учителя: {ph[4]:.0f}x{ph[5]:.0f} px (нужно 72–96); внутри — inline SVG, тегов img в карточке: {nimg}')
    sy = g['say']; P(f'  пузырь: y {sy[1]:.0f}–{sy[3]:.0f}, высота {sy[5]:.0f} при Люмо {g["lumo"][5]:.0f}')
    sd = pg.evaluate(SAY_JS)
    P(f'  пузырь (покой): текст {sd["lines"]} стр., высота текста {sd["th"]:.0f}, scrollHeight {sd["sh"]} <= clientHeight {sd["ch"]}: {sd["sh"] <= sd["ch"]}')
    # рамки
    rows = pg.evaluate(BORDER_JS)
    nb = [r for r in rows if r['b']]
    from collections import Counter
    cc = Counter(r['cls'] for r in nb)
    cards = {'tz', 'seg', 'kid', 'cons', 'lesson', 'msg', 'law', 'banner', 'compose', 'dcard', 'say', 'next', 'dlg'}
    card_rows = [r for r in rows if r['cls'] in cards]; card_b = [r for r in card_rows if r['b']]
    P(f'  РАМКИ (первая загрузка, вся страница): элементов с border: {len(nb)} из {len(rows)} видимых ({100 * len(nb) / len(rows):.1f}%); по классам: {dict(cc)}')
    P(f'  карточки (tz, seg, kid, cons, lesson, msg, law, banner, compose, dcard, say, next): {len(card_rows)}, из них с рамкой {len(card_b)}: {Counter(r["cls"] for r in card_b)}')
    # текст/структура
    nm = pg.evaluate("document.querySelector('#nextCard .next-meta').textContent"); P(f'  в карточке урока: «{nm}»')
    # UK без заливки
    uk = pg.evaluate("(()=>{const b=document.querySelector('.seg button[aria-pressed=true]'); const c=getComputedStyle(b); const s=getComputedStyle(b.parentElement); return {txt:b.textContent, bg:c.backgroundColor, bd:c.borderTopWidth, ul:c.textDecorationLine}})()")
    P(f'  «UK» (выбранный язык): текст {uk["txt"]}, фон {uk["bg"]}, border {uk["bd"]}, подчёркивание {uk["ul"]} -> без заливки: {uk["bg"] in ("rgba(0, 0, 0, 0)", "transparent")}')
    # согласия
    nv = pg.evaluate("""()=>{const n=document.querySelector('#nav'); const a=[...n.querySelectorAll('a')]; const tops=new Set(a.map(e=>Math.round(e.getBoundingClientRect().top))); const cur=n.querySelector('[aria-current=true]'); const bd=n.querySelector('.n-badge'); const bs=bd?getComputedStyle(bd):null; const pb=getComputedStyle(cur,'::before');
      const ink=getComputedStyle(document.body).color; return {rows:tops.size, sw:n.scrollWidth, cw:n.clientWidth, snap:getComputedStyle(n).scrollSnapType, mask:(getComputedStyle(n).maskImage||getComputedStyle(n).webkitMaskImage||'').slice(0,40), sb:getComputedStyle(n).scrollbarWidth, bad: bs&&bs.color, badbg: bs&&bs.backgroundColor, before: pb.display, left: Math.round(cur.getBoundingClientRect().left), rect: Math.round(n.getBoundingClientRect().left)}}""")
    P(f'  меню: строк вкладок {nv["rows"]}; scrollWidth {nv["sw"]} / clientWidth {nv["cw"]}; scroll-snap {nv["snap"]}; scrollbar {nv["sb"]}; mask {nv["mask"]}; бейдж: цвет {nv["bad"]} на фоне {nv["badbg"]}; полоска ::before активного: display {nv["before"]}')
    ca = pg.evaluate("[...document.querySelectorAll('.lumo .core')].map(e=>e.getAttribute('fill')).concat([...document.querySelectorAll('.lumo .pupil-hi')].map(e=>e.getAttribute('fill')))")
    fd = pg.evaluate("getComputedStyle(document.querySelector('.lumo .f-full')).display")
    P(f'  Люмо: fill сердцевины/бликов {ca}; f-full display {fd}; размер {g_lumo_size(pg)}')
    pg.evaluate("window.scrollTo({top: document.getElementById('consents').getBoundingClientRect().top + scrollY - (innerWidth<=820?200:90), behavior:'instant'})"); pg.wait_for_timeout(900)
    snap('2-consents')
    c = pg.evaluate("""()=>{const q=s=>document.querySelector(s); const g=[...document.querySelectorAll('.cgrp')];
      const tit=g.map(e=>e.querySelector('.grp-t').textContent);
      const lastYes=g[0].querySelector('.cons:last-child').getBoundingClientRect(); const conT=g[1].getBoundingClientRect(); const lab2=g[1].querySelector('.grp-t').getBoundingClientRect();
      const lnk=q('.lnk'); const ls=getComputedStyle(lnk); const st=q('.stl.con'); const btn=[...document.querySelectorAll('.cons .btn-eq')].map(b=>Math.round(b.getBoundingClientRect().width));
      return {tit, gap: Math.round(lab2.top - lastYes.bottom), grpGapBox: Math.round(conT.top-g[0].getBoundingClientRect().bottom), inYes:[...g[0].querySelectorAll('.c-t')].map(e=>e.textContent), inCon:[...g[1].querySelectorAll('.c-t')].map(e=>e.textContent), svg: !!st.querySelector('svg'), stt: st.textContent, lbg: ls.backgroundColor, lbd: ls.borderTopWidth, lul: ls.textDecorationLine, btn, lead: q('#consents .sec-lead').textContent, say: q('#sayT').textContent}}""")
    P(f'  согласия: группы {c["tit"]}; в «Ваша згода»: {c["inYes"]}; в «за договором»: {c["inCon"]}')
    P(f'  отступ между группами (низ последней карточки переключателей -> заголовок группы договора): {c["gap"]} px (нужно 32); значок документа (inline SVG): {c["svg"]}; статус: «{c["stt"]}»')
    P(f'  ссылка «Розділ «Дані» →»: фон {c["lbg"]}, border {c["lbd"]}, подчёркивание {c["lul"]}; ширины кнопок Надати/Відкликати: {c["btn"]}')
    P(f'  подзаголовок раздела: «{c["lead"]}»')
    if dev == 'phone':
        sdc = pg.evaluate(SAY_JS); P('  реплика в разделе согласий: «%s»; %s стр.' % (c['say'], sdc['lines']))
    pg.click('[data-revoke=part]'); pg.wait_for_timeout(900); snap('3-revoke-dialog')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    esc_ = pg.evaluate("document.getElementById('scrim').hidden")
    P(f'  Esc закрывает диалог: {esc_}')
    pg.click('[data-revoke=part]'); pg.wait_for_timeout(300); pg.click('#dlgGo'); pg.wait_for_timeout(900); snap('4-after-revoke')
    sdr = pg.evaluate(SAY_JS); P(f'  пузырь после отзыва: «{sdr["txt"]}» {sdr["lines"]} стр., scrollHeight {sdr["sh"]} <= {sdr["ch"]}: {sdr["sh"] <= sdr["ch"]}')
    pg.wait_for_timeout(4200)
    # данные
    pg.evaluate("window.scrollTo({top: document.getElementById('data').getBoundingClientRect().top + scrollY - (innerWidth<=820?200:90), behavior:'instant'})"); pg.wait_for_timeout(700)
    pg.click('[data-stub=de]'); pg.wait_for_timeout(500); snap('5-data')
    # второй ребёнок, расписание
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
    pg.click('[data-kid=max]'); pg.wait_for_timeout(700); snap('6-kid2-rest')
    pg.evaluate("window.scrollTo({top: document.getElementById('schedule').getBoundingClientRect().top + scrollY - (innerWidth<=820?200:90), behavior:'instant'})"); pg.wait_for_timeout(700)
    snap('7-kid2-schedule')
    # все реплики: влезает ли текст (scrollHeight<=clientHeight), по разделам и детям
    allok = []
    for kid in ('olya', 'max'):
        pg.evaluate("window.scrollTo(0,0)"); pg.click(f'[data-kid={kid}]'); pg.wait_for_timeout(600)
        for sec in ('schedule', 'consents', 'progress', 'messages', 'data'):
            pg.evaluate("(id)=>{const el=document.getElementById(id); window.scrollTo({top: el.getBoundingClientRect().top + scrollY - (innerWidth<=820?200:90), behavior:'instant'})}", sec); pg.wait_for_timeout(700)
            d = pg.evaluate(SAY_JS); allok.append((kid, sec, d['emo'], d['lines'], round(d['h']), d['sh'] <= d['ch']))
    P(f'  пузырь по всем разделам и обоим детям (kid, раздел, эмоция, строк, высота, влезает): {allok}')
    P(f'  пузырь влезает везде: {all(a[5] for a in allok)}; макс. строк {max(a[3] for a in allok)}; высоты пузыря: {sorted(set(a[4] for a in allok))}')
    cls = pg.evaluate('window.__cls'); P(f'  CLS сценария: {cls:.4f}; ошибки/предупреждения консоли: {len(cons)} {cons[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    br.close()

def emo_frames(pw):
    # кадры эмоций Люмо: крупно (desktop и phone), для проверки сердцевины/наклона/глаз
    for dev in ('desktop', 'phone'):
        w, h = DEV[dev]; br = pw.chromium.launch(args=LCD); ctx = br.new_context(viewport={'width': w, 'height': h}); pg = ctx.new_page()
        pg.goto(URL); pg.wait_for_timeout(900); pg.add_style_tag(content='.lumo,.lumo *{animation:none !important}')
        for emo in ('rest', 'wait', 'think', 'joy'):
            pg.evaluate("(e)=>{document.querySelector('#page').dataset.emo=e}", emo); pg.wait_for_timeout(1000)
            b = pg.evaluate("(()=>{const r=document.querySelector('#lumoBox').getBoundingClientRect(); return [r.left,r.top,r.width,r.height]})()")
            pg.screenshot(path=os.path.join(SH, f'r8-{dev}-lumo-{emo}.png'), clip={'x': max(0, b[0] - 20), 'y': max(0, b[1] - 20), 'width': b[2] + 60, 'height': b[3] + 40})
        br.close()

with sync_playwright() as pw:
    for dev in DEV: run_main(pw, dev)
    emo_frames(pw)
    for dev, (w, h) in DEV.items():   # EN
        br = pw.chromium.launch(args=LCD); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone')); ctx.add_init_script(INIT); pg = ctx.new_page(); cons = []
        pg.on('console', lambda m: cons.append(m.text) if m.type in ('error', 'warning') else None); pg.on('pageerror', lambda e: cons.append(str(e)))
        pg.goto(URL + '?lang=en'); pg.wait_for_timeout(1000)
        pg.screenshot(path=os.path.join(SH, f'r8-{dev}-en-1-rest.png'))
        sw = pg.evaluate("[document.documentElement.scrollWidth, innerWidth]"); sd = pg.evaluate(SAY_JS)
        els = []
        for sec in ('schedule', 'consents', 'progress', 'messages', 'data'):
            pg.evaluate("(id)=>{const el=document.getElementById(id); window.scrollTo({top: el.getBoundingClientRect().top + scrollY - (innerWidth<=820?200:90), behavior:'instant'})}", sec); pg.wait_for_timeout(600)
            d = pg.evaluate(SAY_JS); els.append((sec, d['lines'], d['sh'] <= d['ch']))
        mf = min(pg.evaluate(TEXT_JS, None), key=lambda i: i['fs'])['fs']
        clsx = pg.evaluate('window.__cls')
        P(f'== EN {dev}: ширина {sw[0]} = окно {sw[1]}: {sw[0] == sw[1]}; мин. шрифт {mf}; пузырь (раздел, строк, влезает) {els}; CLS {clsx:.4f}; консоль {len(cons)} {cons[:2]}')
        br.close()
    for dev, (w, h) in DEV.items():   # CLS при загрузке
        vals = []
        for _ in range(10):
            br = pw.chromium.launch(args=LCD); ctx = br.new_context(viewport={'width': w, 'height': h}); ctx.add_init_script(INIT)
            pg = ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(1500); vals.append(pg.evaluate('window.__cls')); br.close()
        P(f'== CLS при загрузке {dev}: 10 прогонов, макс {max(vals):.4f}, среднее {sum(vals) / len(vals):.5f}')
open(os.path.join(SH, 'r8-metrics.txt'), 'w').write('\n'.join(out) + '\n')
