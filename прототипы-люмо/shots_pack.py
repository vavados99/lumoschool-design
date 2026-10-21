"""Пакет «ВКУС» В3+В4: кадры и замеры. Запуск:
PYTHONDONTWRITEBYTECODE=1 /usr/local/lib/hermes-agent/venv/bin/python shots_pack.py <tag>   (tag = before | after)
Кадры -> <папка>/shots/pack-<tag>-*.png, числа -> <папка>/shots/pack-<tag>.txt"""
import os, io, re, sys, json, math, colorsys
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
TAG = sys.argv[1] if len(sys.argv) > 1 else 'after'
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
INIT = "window.__cls=0;window.__ls=[];new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput){window.__cls+=e.value;if(e.value>.002)window.__ls.push([+e.value.toFixed(4),performance.now()|0,(e.sources||[]).slice(0,3).map(s=>(s.node&&(s.node.className||s.node.id||s.node.tagName))+':'+(s.previousRect.y|0)+'->'+(s.currentRect.y|0))])}}).observe({type:'layout-shift',buffered:true});"

def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def L(r): return 0.2126 * lin(r[0]) + 0.7152 * lin(r[1]) + 0.0722 * lin(r[2])
def cr(a, b):
    la, lb = sorted([L(a), L(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
def nums(s): return [float(x) for x in re.findall(r'[\d.]+', s)]

TEXT_JS = """() => { const res = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg,[hidden]')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (el.closest('.sr') ) continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    if (b.bottom < 0 || b.top > innerHeight) continue;
    const cx = b.left + b.width / 2, cy = b.top + b.height / 2; const top = document.elementFromPoint(cx, cy);
    if (top && !el.contains(top) && !top.contains(el)) continue;
    res.push({t: n.textContent.trim().slice(0, 26), fs: parseFloat(cs.fontSize), color: cs.color, x: b.left, y: b.top, w: b.width, h: b.height, dis: !!el.closest('button:disabled,[aria-disabled=true]')}); }
  return res; }"""

# заливки: считаем элементы с непрозрачной (alpha>.5) заливкой
FILLS_JS = """() => { const out = []; for (const e of document.querySelectorAll('body *')) {
  const r = e.getBoundingClientRect(); if (r.width < 8 || r.height < 8) continue;
  if (r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) continue;
  if (e.closest('svg') || e.closest('[hidden]') || e.tagName === 'I') continue;
  const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
  if (e.closest('dialog') && !e.closest('dialog[open]')) continue;
  const c = cs.backgroundColor; if (!c || c === 'rgba(0, 0, 0, 0)') continue;
  out.push([(e.id ? '#' + e.id : '') + '.' + (typeof e.className === 'string' ? e.className.split(' ')[0] : '') + ':' + e.tagName.toLowerCase() + ':' + e.textContent.trim().slice(0, 14), c, Math.round(r.width) + 'x' + Math.round(r.height)]); }
  return out; }"""

def hue_info(rgb):
    h, l, s = colorsys.rgb_to_hls(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    return h * 360, s, l

def classify(c):
    v = nums(c)
    if len(v) >= 4 and v[3] < .5: return None
    h, s, l = hue_info(v[:3])
    if s < .45 or l < .3 or l > .92: return None
    if 8 <= h <= 60: return 'warm'   # оранжевый, янтарь, золото
    return None
def is_orange(c):
    v = nums(c)
    if len(v) >= 4 and v[3] < .5: return False
    h, s, l = hue_info(v[:3])
    return 8 <= h <= 28 and s > .8 and .5 < l < .72   # #FF7A45-ряд

def contrast_pixels(pg):
    items = pg.evaluate(TEXT_JS)
    pg.add_style_tag(content='.gap{border-color:transparent !important} *{color:transparent !important;text-shadow:none !important;-webkit-text-fill-color:transparent !important} svg{opacity:1} .chip svg,.btn-sm svg,.sos svg{opacity:0}')
    pg.wait_for_timeout(120)
    im = np.array(Image.open(io.BytesIO(pg.screenshot())).convert('RGB')).astype(float)
    pg.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    worst = []
    for it in items:
        x0, y0 = max(0, int(it['x'])), max(0, int(it['y'])); x1, y1 = int(it['x'] + it['w']) + 1, int(it['y'] + it['h']) + 1
        reg = im[y0:y1, x0:x1]
        if reg.size == 0: continue
        lum = 0.2126 * (reg[..., 0] / 255) ** 2.2 + 0.7152 * (reg[..., 1] / 255) ** 2.2 + 0.0722 * (reg[..., 2] / 255) ** 2.2
        yy, xx = np.unravel_index(np.argmax(lum), lum.shape)
        col = nums(it['color'])[:3]
        worst.append((cr(col, reg[yy, xx]), it['t'], it['dis'], tuple(int(v) for v in reg[yy, xx])))
    worst.sort(); return worst

def disc(im, cx, cy, r):
    H, W = im.shape[:2]
    y0, y1, x0, x1 = max(0, int(cy - r)), min(H, int(cy + r)), max(0, int(cx - r)), min(W, int(cx + r))
    if y1 <= y0 or x1 <= x0: return None
    yy, xx = np.mgrid[y0:y1, x0:x1]
    m = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
    return im[y0:y1, x0:x1][m].mean(axis=0)
def lum_of(rgb): return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

GEOM_JS = """() => { const q = s => document.querySelector(s); const R = e => { const b = e.getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; };
  const lumo = q('#lumo'), core = q('#lumo .core'); const cr_ = core.getBoundingClientRect();
  const el = q('#lumo .eye-l ellipse'), pu = q('#lumo .eye-l .pupil');
  const er = el.getBoundingClientRect(), pr = pu.getBoundingClientRect();
  const root = q('#room') || q('#page'); const cs = getComputedStyle(root);
  return {lumo: R(lumo), btn: R(q('.lumo-btn')), core: [cr_.x + cr_.width / 2, cr_.y + cr_.height / 2],
    light: [parseFloat(cs.getPropertyValue('--lx')), parseFloat(cs.getPropertyValue('--ly'))], emo: root.dataset.emo,
    eye: [er.x + er.width / 2, er.y + er.height / 2], pupil: [pr.x + pr.width / 2, pr.y + pr.height / 2],
    scroll: [scrollX, scrollY], vw: innerWidth, vh: innerHeight, sw: document.documentElement.scrollWidth}; }"""

def frame(pg, folder, name, key_sel, spill_sel, out, fullpage=False):
    """снять кадр и вывести числа"""
    pg.wait_for_timeout(1100)
    png = pg.screenshot(path=os.path.join(folder, 'shots', f'pack-{TAG}-{name}.png'), full_page=fullpage)
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    pg.add_style_tag(content='.lumo{animation:none!important}'); pg.wait_for_timeout(80)
    g = pg.evaluate(GEOM_JS)
    pg.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    fills = pg.evaluate(FILLS_JS)
    orange = [f for f in fills if is_orange(f[1])]
    warm = [f for f in fills if classify(f[1]) == 'warm']
    # свет: центр света vs ядро (в координатах viewport: light даётся относительно комнаты, у В3 комната = окно; у В4 + scrollY)
    lx, ly = g['light'][0], g['light'][1] - (g['scroll'][1] if 'page' in folder.lower() or True else 0)
    page_off = pg.evaluate("() => { const r = (document.querySelector('#room')||document.querySelector('#page')).getBoundingClientRect(); return [r.left, r.top]; }")
    lx += page_off[0]; ly = g['light'][1] + page_off[1]
    dl = math.hypot(lx - g['core'][0], ly - g['core'][1])
    # яркость: ядро против кончика
    cx, cy = g['core']; lb = g['lumo']; tip = (lb[0] + lb[2] * .55, lb[1] + lb[3] * .06)
    c = disc(im, cx, cy, 12); t = disc(im, tip[0], tip[1], 8)
    ratio = (lum_of(c) / max(1, lum_of(t))) if c is not None and t is not None else float('nan')
    # ореол: яркость кольца вокруг Люмо (радиус 0.62..0.9 ширины) — среднее по 16 точкам
    ring = []
    for k in range(16):
        a = k * math.pi / 8; rr = lb[2] * 0.85
        d = disc(im, cx + rr * math.cos(a), cy + rr * math.sin(a) + lb[3] * .12, 6)
        if d is not None: ring.append(lum_of(d))
    halo = float(np.mean(ring)) if ring else float('nan')
    # соседний блок: левая/правая полоса
    sp = ''
    if spill_sel:
        bb = pg.evaluate("(s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; }", spill_sel)
        if bb and bb[2] > 100 and bb[1] < im.shape[0]:
            ya, yb = int(max(0, bb[1] + 20)), int(min(im.shape[0], bb[1] + bb[3] - 20))
            def strip(x0, x1):
                x0, x1 = int(max(0, x0)), int(min(im.shape[1], x1))
                return im[ya:yb, x0:x1].reshape(-1, 3) if yb > ya and x1 > x0 else None
            a_ = strip(bb[0] + 4, bb[0] + 84); b_ = strip(bb[0] + bb[2] - 84, bb[0] + bb[2] - 4)
            if a_ is not None and b_ is not None:
                # какая сторона ближе к Люмо
                near, far = (a_, b_) if abs(bb[0] - cx) < abs(bb[0] + bb[2] - cx) else (b_, a_)
                nm, fm = near.mean(axis=0), far.mean(axis=0); nd, fd = np.median(near, axis=0), np.median(far, axis=0)
                sp = f'отсвет {spill_sel}: край у Люмо − дальний край: среднее {lum_of(nm) - lum_of(fm):+.1f}, медиана (без текста) {lum_of(nd) - lum_of(fd):+.1f}; розовая доля (R−G) у Люмо {nd[0] - nd[1]:.0f} / дальн. {fd[0] - fd[1]:.0f}'
    # взгляд: угол между сдвигом зрачка и направлением на главную кнопку
    gz = ''
    if key_sel:
        kb = pg.evaluate("(s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [b.x + b.width / 2, b.y + b.height / 2]; }", key_sel)
        dx, dy = g['pupil'][0] - g['eye'][0], g['pupil'][1] - g['eye'][1]
        if kb and (abs(dx) + abs(dy)) > .3:
            want = math.atan2(kb[1] - g['eye'][1], kb[0] - g['eye'][0]); got = math.atan2(dy, dx)
            diff = abs((math.degrees(want - got) + 180) % 360 - 180)
            gz = f'взгляд: сдвиг зрачка ({dx:.1f},{dy:.1f}) px, угол до кнопки {key_sel}: {diff:.0f}°'
        else:
            gz = f'взгляд: зрачок почти по центру ({dx:.1f},{dy:.1f}) px, на кнопку {key_sel} не направлен'
    cw = contrast_pixels(pg)
    en = [x for x in cw if not x[2]]
    cmin = en[0] if en else (None, '', 0)
    sw_ok = g['sw'] == g['vw']
    out(f'  [{name}] эмоция {g["emo"]}: оранж. заливок {len(orange)} {[o[0] for o in orange][:4]}; тёплых заливок (оранж/янтарь/золото) {len(warm)}; '
        f'центр света↔ядро {dl:.1f} px; яркость ядро/кончик {ratio:.2f}; кольцо-ореол {halo:.1f}; шир. стр. {g["sw"]} vs окно {g["vw"]} ({"ок" if sw_ok else "СКРОЛЛ"}); контраст мин {cmin[0]:.2f}:1 «{cmin[1]}» фон {cmin[3] if len(cmin) > 3 else ""}' + (f'; <4.5: {[(round(x[0], 2), x[1]) for x in en if x[0] < 4.5]}' if cmin[0] and cmin[0] < 4.5 else ''))
    if sp: out('      ' + sp)
    if gz: out('      ' + gz)
    mf = pg.evaluate("(" + TEXT_JS + ")()")
    mn = min(mf, key=lambda i: i['fs']); out(f'      мин. шрифт {mn["fs"]} px «{mn["t"]}»')
    return g

def JC(pg, s): pg.evaluate('(s) => document.querySelector(s).click()', s)
def EMO_NOW(pg): return pg.evaluate("() => document.querySelector('#room').dataset.emo")
def H2_NOW(pg): return pg.evaluate("() => parseFloat(getComputedStyle(document.querySelector('.board h2')).fontSize)")
def run(pw, folder, dev, out):
    w, h = DEV[dev]
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone'))
    ctx.add_init_script(INIT); pg = ctx.new_page(); con = []; reqs = []
    pg.on('console', lambda m: con.append(m.text) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: con.append(str(e)))
    pg.on('request', lambda r: reqs.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    is3 = 'комната' in folder
    pg.goto('file://' + os.path.join(ROOT, folder, 'index.html') + ('?still=1' if is3 else '')); pg.wait_for_timeout(800)
    out(f'== {folder} · {dev} {w}x{h} ==')
    key = '#check' if is3 else '#enter'
    spill = '.board' if is3 else '#next'
    if is3:
        # телефон: Люмо смотрит на «Перевірити» (ниже в доске)
        rects = {}
        for emo in ['listen', 'think', 'joy', 'rest']:
            JC(pg, '#lumoBtn'); JC(pg, f'#demo [data-emo={emo}]'); pg.wait_for_timeout(100)
            rects[emo] = pg.evaluate("() => { const b = document.querySelector('.lumo-btn').getBoundingClientRect(); const s = document.querySelector('.lamp-say').getBoundingClientRect(); return [b.x, b.y, b.width, b.height, s.x, s.y, s.width, s.height]; }")
            frame(pg, folder, f'{dev}-{emo}', key if pg.evaluate("(s)=>!!document.querySelector(s)&&document.querySelector(s).offsetParent!==null", key) else None, spill, out)
        base = rects['listen']
        out(f'  сдвиг Люмо при смене эмоции: {max(max(abs(rects[e][i] - base[i]) for i in range(8)) for e in rects):.2f} px (бокс кнопки и подписи)')
    else:
        rects = {}
        for emo in ['rest', 'wait', 'think', 'joy']:
            pg.evaluate("() => { const d = document.querySelector('#demo'); if (d) d.hidden = true; }")
            JC(pg, '#lumoBtn'); JC(pg, f'#demo [data-emo={emo}]'); pg.wait_for_timeout(100)
            pg.evaluate("() => scrollTo(0, 0)")
            rects[emo] = pg.evaluate("() => { const q = s => { const b = document.querySelector(s).getBoundingClientRect(); return [b.x, b.y + scrollY, b.width, b.height]; }; return [...q('.lumo-btn'), ...q('.lamp-say'), ...q('#next')]; }")
            frame(pg, folder, f'{dev}-{emo}', key, spill, out)
        base = rects['rest']
        out(f'  сдвиг Люмо при смене эмоции: {max(max(abs(rects[e][i] - base[i]) for i in range(12)) for e in rects):.2f} px (бокс кнопки, подписи, карточки урока)')
        # урок скоро: кнопка входа
        JC(pg, '#lumoBtn'); JC(pg, '#demo [data-day=near]'); pg.wait_for_timeout(1300)
        pg.evaluate("() => scrollTo(0, 0)")
        frame(pg, folder, f'{dev}-near', key, spill, out)
        eb = pg.evaluate("() => { const b = document.querySelector('#enter').getBoundingClientRect(); const c = document.querySelector('.count').getBoundingClientRect(); return {enter: [Math.round(b.width), Math.round(b.height)], gapToTimer: Math.round(Math.hypot(b.x + b.width/2 - (c.x + c.width/2), b.y + b.height/2 - (c.y + c.height/2)))}; }")
        out(f'  кнопка «Увійти»: {eb["enter"][0]}×{eb["enter"][1]} px; расстояние центр кнопки↔центр таймера {eb["gapToTimer"]} px')
        JC(pg, '#lumoBtn'); JC(pg, '#demo [data-day=far]'); pg.wait_for_timeout(600)
        pg.evaluate("() => scrollTo(0, 0)")
        # слоты и бронь: вся страница
        pg.screenshot(path=os.path.join(ROOT, folder, 'shots', f'pack-{TAG}-{dev}-full-far.png'), full_page=True)
        pg.evaluate("() => scrollTo(0, 560)"); pg.wait_for_timeout(300)
        fl = pg.evaluate(FILLS_JS)
        out(f'  [слоты в экране, scroll 560] оранж. заливок {len([f for f in fl if is_orange(f[1])])}; тёплых {len([f for f in fl if classify(f[1]) == "warm"])}')
        pg.screenshot(path=os.path.join(ROOT, folder, 'shots', f'pack-{TAG}-{dev}-slots.png'))
        pg.evaluate("() => scrollTo(0, 0)")
        pg.click('[data-book=s3]'); pg.wait_for_timeout(900)
        pg.evaluate("() => scrollTo(0, 0)")
        frame(pg, folder, f'{dev}-booked', key, spill, out)
        pg.wait_for_timeout(3800)
        pg.click('[data-cancel=s3]'); pg.wait_for_timeout(600)
        pg.screenshot(path=os.path.join(ROOT, folder, 'shots', f'pack-{TAG}-{dev}-cancel.png'))
        fl = pg.evaluate(FILLS_JS)
        out(f'  [диалог отмены] оранж. заливок {len([f for f in fl if is_orange(f[1])])} (в т.ч. {[f[0] for f in fl if is_orange(f[1])][:3]}); фокус: {pg.evaluate("() => document.activeElement.textContent.trim()")}')
        pg.click('[data-keep]')
    if is3:
        # дополнительно: ответ неверный/верный — цвета
        pg.evaluate("() => scrollTo(0,0)")
        pg.click('#opts1 [data-v=go]'); pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(ROOT, folder, 'shots', f'pack-{TAG}-{dev}-wrong.png'))
        pg.click('#opts1 [data-v=goes]'); pg.wait_for_timeout(900)
        pg.screenshot(path=os.path.join(ROOT, folder, 'shots', f'pack-{TAG}-{dev}-solved.png'))
        fl = pg.evaluate(FILLS_JS)
        out(f'  [после верного ответа] оранж. заливок {len([f for f in fl if is_orange(f[1])])}; тёплых {len([f for f in fl if classify(f[1]) == "warm"])}: {[f[0] for f in fl if classify(f[1]) == "warm"][:5]}')
        # SOS экран
        pg.click('#sos'); pg.wait_for_timeout(600)
        pg.screenshot(path=os.path.join(ROOT, folder, 'shots', f'pack-{TAG}-{dev}-sos.png'))
        fl = pg.evaluate(FILLS_JS)
        out(f'  [SOS-выбор] оранж. заливок {len([f for f in fl if is_orange(f[1])])}; эмоция {EMO_NOW(pg)}')
        sb = pg.evaluate("() => { const b = document.querySelector('#sos').getBoundingClientRect(); const cs = getComputedStyle(document.querySelector('#sos')); return [Math.round(b.width), Math.round(b.height), cs.backgroundColor, cs.borderTopWidth]; }")
        out(f'  кнопка «Вийти/покликати» (#sos): {sb[0]}×{sb[1]} фон {sb[2]} рамка {sb[3]}')
        mono = pg.evaluate("() => [...document.querySelectorAll('.ini')].map(e => parseFloat(getComputedStyle(e).fontSize))")
        out(f'  размеры монограмм: {mono} px; заголовок «Дошка» {H2_NOW(pg)} px')
    out(f'  CLS за сессию: {pg.evaluate("() => window.__cls"):.4f}; ошибок консоли {len(con)} {con[:2]}; внешних запросов {len(reqs)}')
    out('  крупные сдвиги (>0.002): ' + str(pg.evaluate('window.__ls'))[:400])
    br.close()

lines = []
for folder in ['В3-комната', 'В4-кабинет']:
    out = []
    def P(s): print(s); out.append(s)
    with sync_playwright() as pw:
        for dev in DEV: run(pw, folder, dev, P)
    with open(os.path.join(ROOT, folder, 'shots', f'pack-{TAG}.txt'), 'w') as f: f.write('\n'.join(out) + '\n')
