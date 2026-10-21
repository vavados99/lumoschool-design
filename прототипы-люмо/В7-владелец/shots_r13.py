"""Круг 13. Кадры r13-* и замеры В7. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_r13.py"""
import os, io, re
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html')
SHOTS = os.path.join(HERE, 'shots'); os.makedirs(SHOTS, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def L_(rgb): return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
def cr(a, b):
    la, lb = L_(a), L_(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

INIT = """window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type:'layout-shift', buffered:true});"""

TEXT_JS = """() => {
  const res = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg')) continue;
    if (el.closest('[hidden]')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (el.closest('.vh') || el.closest('.skip')) continue;
    if (el.closest('.cmp') && getComputedStyle(el.closest('.cmp')).clipPath !== 'none') continue; /* визуально скрытый текст для скринридера (телефон) */
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    res.push({t: n.textContent.trim().slice(0, 30), fs: parseFloat(cs.fontSize), color: cs.color, x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, tag: el.tagName.toLowerCase()});
  }
  return res; }"""

def parse(c): return [float(x) for x in re.findall(r'[\d.]+', c)[:4]]

def contrast_pixels(page):
    items = page.evaluate(TEXT_JS)
    page.add_style_tag(content='*{color:transparent !important;-webkit-text-fill-color:transparent !important;text-shadow:none !important} svg{opacity:0 !important}')
    page.wait_for_timeout(200)
    png = page.screenshot(full_page=True)
    page.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    worst = []
    for it in items:
        x0, y0 = int(it['x']), int(it['y']); x1, y1 = int(it['x'] + it['w']) + 1, int(it['y'] + it['h']) + 1
        reg = im[max(0, y0):y1, max(0, x0):x1]
        if reg.size == 0: continue
        lum = 0.2126 * ((reg[..., 0] / 255) ** 2.2) + 0.7152 * ((reg[..., 1] / 255) ** 2.2) + 0.0722 * ((reg[..., 2] / 255) ** 2.2)
        col = parse(it['color'])[:3]
        c_min = 99
        for fn in (np.argmax, np.argmin):
            yy, xx = np.unravel_index(fn(lum), lum.shape)
            c_min = min(c_min, cr(col, reg[yy, xx]))
        worst.append((c_min, it['t'], it['tag'], tuple(int(v) for v in col)))
    worst.sort()
    return worst

def min_font(page):
    items = page.evaluate(TEXT_JS)
    m = min(items, key=lambda i: i['fs'])
    return m['fs'], m['t']

def shot(page, name, full=False):
    page.screenshot(path=os.path.join(SHOTS, 'r13-' + name + '.png'), full_page=full)

def goto_sec(page, sec):
    page.evaluate("(id) => { const el = document.getElementById(id); window.scrollTo({top: el.getBoundingClientRect().top + scrollY - 84, behavior: 'instant'}); }", sec)
    page.wait_for_timeout(400)

CLIP_JS = """() => { const bad = []; const vw = innerWidth;
  for (const el of document.querySelectorAll('main *, header *, .sbar *')) {
    if (el.closest('svg') || el.closest('[hidden]') || el.closest('.nav') || el.closest('.vh') || el.closest('.cmp') || (el.closest('.ribbon') && el !== el.closest('.ribbon'))) continue;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect(); if (r.width < 1) continue;
    if (r.right > vw + 1 || r.left < -1) bad.push('вне окна: ' + el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
    if (el.children.length === 0 && el.scrollWidth > el.clientWidth + 1 && cs.overflow !== 'visible') bad.push('обрезан текст: ' + el.tagName + '.' + el.className);
  } return bad.slice(0, 8); }"""
TARGET_JS = """() => [...document.querySelectorAll('button, a.btn, .nav a')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.display !== 'none' && !e.closest('[hidden]') && (r.height < 44 - .5) }).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().height) + 'px ' + e.textContent.trim().slice(0, 16))"""
WARM_JS = """() => { // тёплые точки в первом экране: элементы с заливкой/обводкой акцента + Люмо
  const vh = innerHeight, res = [];
  for (const el of document.querySelectorAll('#page *')) {
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect(); if (r.width < 1 || r.top > vh || r.bottom < 0) continue;
    const isAcc = c => /rgb\\(255, 122, 69\\)/.test(c);
    if (isAcc(cs.backgroundColor) || isAcc(cs.color) || isAcc(cs.borderTopColor) && parseFloat(cs.borderTopWidth) > 0 || (el.tagName === 'circle' && isAcc(cs.fill)) || (el.tagName === 'circle' && el.getAttribute('class') && el.getAttribute('class').includes('overlap'))) res.push(el.tagName + '.' + (el.getAttribute('class') || ''));
  }
  return res; }"""


OVERLAP_JS = """() => {
  const items = []; let nid = 0; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode; if (!n.textContent.trim()) continue; const el = n.parentElement;
    if (!el || el.closest('script,style,svg,[hidden],.vh,.skip,.grain,.toast')) continue;
    if (el.closest('.sbar') && scrollY > 0) continue; /* липкая шапка перекрывает контент при прокрутке по замыслу */
    const cc = el.closest('.cmp'); if (cc && getComputedStyle(cc).clipPath !== 'none') continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    nid++; for (const b of r.getClientRects()) { if (b.width < 1 || b.height < 1) continue;
    items.push({nid, t: n.textContent.trim().slice(0, 24), l: b.left + scrollX, r: b.right + scrollX, tp: b.top + scrollY, bt: b.bottom + scrollY}); } }
  const bad = [];
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) { const a = items[i], c = items[j];
    const ix = Math.min(a.r, c.r) - Math.max(a.l, c.l), iy = Math.min(a.bt, c.bt) - Math.max(a.tp, c.tp);
    if (a.nid !== c.nid && ix > 1.5 && iy > 3) bad.push(a.t + ' x ' + c.t + ' (' + Math.round(ix) + 'x' + Math.round(iy) + ')'); }
  // текст не должен выходить за свою ячейку ленты цифр (наезд на разделитель)
  const spill = [];
  for (const f of document.querySelectorAll('.fig')) { const fr = f.getBoundingClientRect(); if (fr.width < 1) continue;
    const ww = document.createTreeWalker(f, NodeFilter.SHOW_TEXT);
    while (ww.nextNode()) { const n = ww.currentNode; if (!n.textContent.trim() || n.parentElement.closest('.vh')) continue; const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
      if (b.width && (b.right > fr.right + 0.5 || b.left < fr.left - 0.5)) spill.push(n.textContent.trim().slice(0, 20) + ' за границу ячейки на ' + Math.round(Math.max(b.right - fr.right, fr.left - b.left)) + 'px'); } }
  return {n: items.length, bad: bad.slice(0, 6), nbad: bad.length, spill}; }"""
OVR = {'checks': 0, 'texts': 0, 'bad': 0, 'spill': 0}
def overlap(page, tag):
    r = page.evaluate(OVERLAP_JS); OVR['checks'] += 1; OVR['texts'] += r['n']; OVR['bad'] += r['nbad']; OVR['spill'] += len(r['spill'])
    P(f"  [{tag}] пересечения соседних текстов (bounding boxes): {r['nbad']} из {r['n']} текстов {r['bad']}; выход за ячейку ленты: {len(r['spill'])} {r['spill'][:3]}")


import math
PCT = {'checks': 0, 'bad': []}
def fh(x): return math.floor(x + .5)
def digits(t): return int(re.sub(r'\D', '', t))
def dec(t, lang):
    t = re.sub(r'[\s\u00a0\u202f]', '', t)
    m = re.search(r'\d+[.,]?\d*', t); return float(m.group(0).replace(',', '.'))
PCT_JS = """() => {
  const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
  return { cells: qa('.cell').map(c => c.getAttribute('aria-label')), read: q('#read').innerText, avg: q('.avgline b').innerText,
    fun: qa('.funnel li .ftxt').map(e => [e.querySelector('b').innerText, e.querySelector('em').innerText]),
    retH: q('#retention .sec-h p').innerText, figs: qa('.ribbon .fig').map(f => [f.querySelector('.fl').innerText, f.querySelector('b').innerText]),
    attH: q('#attendance .sec-h p').innerText, moneyH: q('#money .sec-h p').innerText,
    split: qa('.splitl b').map(b => b.innerText), splitw: qa('.split i').map(i => i.style.width), mini: qa('.mini dd').map(d => d.innerText),
    reasons: qa('.reasons b').map(b => b.innerText), dist: qa('.dist li').map(li => [li.querySelector('.st').innerText, li.querySelector('b').innerText]) }; }"""
def pct_check(page, tag, lang):
    d = page.evaluate(PCT_JS); bad = []; n = 0
    def chk(name, got, exp, tol=0):
        nonlocal n; n += 1
        if abs(got - exp) > tol + 1e-9: bad.append(f'{name}: на странице {got}, по данным {exp}')
    for c in d['cells']:
        m = re.search(r'(\d+)%, (\d+)/12', c); chk('ячейка ' + c[:12], int(m.group(1)), fh(int(m.group(2)) / 12 * 100))
    m1, m2 = re.search(r'(\d+)%', d['read']), re.search(r'(\d+)/12', d['read']); chk('readout %', int(m1.group(1)), fh(int(m2.group(1)) / 12 * 100))
    if len(d['cells']) == 98:
        tot = sum(int(re.search(r', (\d+)/12', c).group(1)) for c in d['cells']); chk('среднее по карте', int(d['avg'].rstrip('%')), fh(tot / (98 * 12) * 100))
    f = [digits(a) for a, b in d['fun']]
    for i in range(1, 4): chk(f'воронка шаг {i} «от предыдущего»', int(re.search(r'(\d+)%', d['fun'][i][1]).group(1)), fh(f[i] / f[i - 1] * 100))
    nums = [int(x) for x in re.findall(r'(\d+)%', d['retH'])]
    chk('заголовок удержания: пробный→платный', nums[0], fh(f[1] / f[0] * 100)); chk('заголовок удержания: до 3 мес.', nums[1], fh(f[3] / f[1] * 100))
    figs = {a: b for a, b in d['figs']}; retk = [k for k in figs if '3' in k][0]
    x = f[3] / f[1] * 100; chk('KPI «платні через 3 міс.»', dec(figs[retk], lang), math.floor(x * 10 + .5) / 10, .051)
    chk('KPI відвідуваність = заголовок секції', dec([v for k, v in figs.items() if k.startswith(('Відвід', 'Attend'))][0], lang), dec(re.search(r'\d+[.,]\d%', d['attH']).group(0), lang))
    inc = digits([v for k, v in figs.items() if k.startswith(('Дохід', 'Income'))][0]); chk('Дохід KPI = заголовок «Гроші»', inc, digits(re.match(r'[\d\s\u00a0\u202f,]+', d['moneyH']).group(0)))
    sp = [digits(v) for v in d['split']]; chk('Польща+Україна = дохід', sum(sp), inc, 2); chk('частка Польщі 61%', sp[0], fh(inc * .61), 1)
    chk('ширини смуги 61+39=100', sum(int(float(w.rstrip('%'))) for w in d['splitw']), 100); chk('«очікує оплати» 6,2%', digits(d['mini'][1]), fh(inc * .062), 1)
    chk('причини пропусків в сумі 100%', sum(int(r.rstrip('%')) for r in d['reasons']), 100)
    rate = sum(digits(c) * int(s[0]) for s, c in d['dist']) / sum(digits(c) for s, c in d['dist'])
    chk('KPI оцінка = з розподілу', dec([v for k, v in figs.items() if k.startswith(('Оцінка', 'Lesson rating'))][0], lang), math.floor(rate * 10 + .5) / 10, .051)
    PCT['checks'] += n; PCT['bad'] += [tag + ' ' + b for b in bad]
    P(f'  [округление %, {tag}] проверок {n}, расхождений {len(bad)} {bad[:3]}')

SIG_JS = """() => [...document.querySelectorAll('.sig')].map(s => ({id: s.dataset.sigid, st: s.querySelector('.urg') ? s.querySelector('.urg').dataset.st : 'done', badge: s.querySelector('.urg') ? s.querySelector('.urg').innerText : 'Виконано', meta: s.querySelector('.sig-m') ? s.querySelector('.sig-m').innerText : '', done: s.classList.contains('done')}))"""
CREAM_JS = """() => { const bad = [], ok = []; for (const el of document.querySelectorAll('body *')) { const cs = getComputedStyle(el); if (cs.backgroundColor !== 'rgb(251, 239, 223)') continue;
  const r = el.getBoundingClientRect(); if (r.width < 1 || el.closest('[hidden]') || cs.visibility === 'hidden' || el.closest('.skip')) continue; const d = el.tagName + '.' + (el.className && el.className.baseVal === undefined ? el.className : '');
  const ctl = el.closest('button, a, .toast, .nav, .seg, .dchip, .perm, .sig-c');
  if (el.matches('.btn') || el.matches('.cell.on')) ok.push(d); else if (ctl) bad.push(d); } return {ok, bad}; }"""
ORANGE_JS = """() => { const vh = innerHeight, res = []; for (const el of document.querySelectorAll('#page *, .topbar *')) { const cs = getComputedStyle(el), r = el.getBoundingClientRect();
  if (r.width < 1 || r.top > vh || r.bottom < 0 || el.closest('[hidden]') || cs.display === 'none') continue; const o = c => /rgb\\(255, 122, 69\\)/.test(c);
  const own = c => o(c.backgroundColor) || (o(c.color) && !(el.parentElement && o(getComputedStyle(el.parentElement).color) && !o(c.backgroundColor))) || (o(c.borderTopColor) && parseFloat(c.borderTopWidth) > 0);
  if (own(cs)) res.push(el.tagName + '.' + (el.getAttribute('class') || '')); } return res; }"""
STATE_JS = """() => { const on = document.querySelector('.cell.on'), so = document.querySelector('.cell.sigon'), bar = document.getElementById('bar').getBoundingClientRect();
  const rows = [...new Set([...document.querySelectorAll('.cell')].map(c => c.dataset.h))]; const r = on ? on.getBoundingClientRect() : null;
  return { sel: on ? [+on.dataset.d, +on.dataset.h] : null, sigon: so ? [+so.dataset.d, +so.dataset.h] : null, rows: rows.length, rowIdx: on ? rows.indexOf(on.dataset.h) : -1, hours: rows[0] + '–' + rows[rows.length - 1],
    top: r && Math.round(r.top), bottom: r && Math.round(r.bottom), barBottom: Math.round(bar.bottom), vh: innerHeight, nOn: document.querySelectorAll('.cell.on').length }; }"""

def selected_first_screen(page, tag):
    st = page.evaluate(STATE_JS)
    ok = st['top'] is not None and st['top'] >= st['barBottom'] and st['bottom'] <= st['vh']
    P(f"  [{tag}] выбранная ячейка {st['sel']}: y {st['top']}..{st['bottom']} при окне {st['vh']}, липкая шапка до {st['barBottom']} -> {'ВИДНА В ПЕРВОМ ЭКРАНЕ' if ok else 'НЕ ВИДНА'}; строк в сетке {st['rows']} ({st['hours']}), выбранная строка №{st['rowIdx'] + 1}")
    return ok, st

def orange(page, tag, limit=3):
    o = page.evaluate(ORANGE_JS); P(f"  [{tag}] оранжевых элементов в первом экране: {len(o)} (лимит {limit}) {'OK' if len(o) <= limit else 'ПЛОХО'} {o}"); return len(o)

def run(pw, dev, lang):
    w, h = DEV[dev]
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=(dev == 'phone'))
    ctx.add_init_script(INIT)
    page = ctx.new_page(); console = []; ext = []
    page.on('console', lambda m: console.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append(('pageerror', str(e))))
    page.on('requestfailed', lambda r: console.append(('reqfail', r.url)))
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    page.goto(URL + ('?lang=en' if lang == 'en' else '')); page.wait_for_timeout(900)
    P(f'== {dev} {w}x{h} {lang} ==')
    pre = f'{dev}-{lang}-'
    ph = dev == 'phone'
    RES = {}
    def sw(tag):
        s = page.evaluate("() => [document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
        mf = min_font(page); ok = 'OK' if s[0] == s[2] and s[1] <= s[2] else 'ПЛОХО'
        P(f'  [{tag}] scrollWidth {s[0]} / body {s[1]} vs окно {s[2]} {ok}; высота {s[3]}; мин.шрифт {mf[0]}px ({mf[1]!r})')
        cl = page.evaluate(CLIP_JS); P(f'  [{tag}] выход за окно / обрезанный текст: {len(cl)} {cl[:3]}')
        overlap(page, tag)
        RES.setdefault('sw', []).append(ok == 'OK'); RES.setdefault('mf', []).append(mf[0]); RES.setdefault('clip', []).append(len(cl))
    # ---- 1. первый экран
    shot(page, pre + '1-first'); shot(page, pre + '1-first-full', full=True)
    sw('first')
    ok, st = selected_first_screen(page, 'первый экран'); RES['selvis'] = ok
    P(f"  [сигнал раскрыт → ячейка] подсвеченная ячейка сигнала {st['sigon']} = выбранная {st['sel']}: {st['sigon'] == st['sel']}; выбранных ячеек: {st['nOn']}")
    if ph:
        win = page.evaluate("""() => { const f = [...document.querySelectorAll('.ribbon .fig')].map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.left)]; }); const rb = document.querySelector('.ribbon').getBoundingClientRect();
          const vis = e => { const el = document.querySelector(e); return el && el.getBoundingClientRect().width > 0 && getComputedStyle(el).display !== 'none'; };
          return { tops: [...new Set(f.map(x => x[0]))], n: f.length, rbRight: Math.round(rb.right), rbLeft: Math.round(rb.left), cur: vis('#curSeg'), lang: vis('[data-lang=en]'), menu: vis('#menuBtn'), sx: document.querySelector('.ribbon').scrollLeft, sw: document.querySelector('.ribbon').scrollWidth }; }""")
        P(f"  [телефон: KPI в одну полосу] карточек {win['n']}, различных y: {win['tops']} -> {'ОДНА ПОЛОСА' if len(win['tops']) == 1 else 'НЕСКОЛЬКО РЯДОВ'}; лента {win['rbLeft']}..{win['rbRight']} (окно {w}), прокрутка {win['sx']}/{win['sw']}")
        P(f"  [телефон: валюта и язык] видны в шапке: валюта {win['cur']}, язык {win['lang']}; кнопка «Меню» видна: {win['menu']} -> {'УБРАНЫ В МЕНЮ' if not win['cur'] and not win['lang'] and win['menu'] else 'ПЛОХО'}")
        RES['strip1'] = len(win['tops']) == 1; RES['menu_hidden'] = (not win['cur'] and not win['lang'] and win['menu'])
    o = orange(page, 'первый экран', 3); RES['orange'] = [o]
    cr_ = page.evaluate(CREAM_JS); P(f"  [кремовая заливка] допустимые (действие/выбранная ячейка): {cr_['ok']}; ПРОЧИЕ: {len(cr_['bad'])} {cr_['bad'][:4]}"); RES['cream_bad'] = len(cr_['bad'])
    steps = page.evaluate("[...document.querySelectorAll('.steps i')].map(i => getComputedStyle(i).backgroundColor)")
    cols = [tuple(int(x) for x in re.findall(r'\d+', c)) for c in steps]
    P(f"  [шкала карты] ступеней {len(steps)}; пол {steps[0]} = {cr(cols[0], hx('#1E1424')):.2f}:1 к фону страницы; верх {steps[-1]}; подпись: {page.inner_text('.lg-cap')!r}")
    P('  соседние ступени, контраст: ' + ', '.join(f'{cr(cols[i], cols[i + 1]):.2f}' for i in range(len(cols) - 1)))
    pct_check(page, 'неделя', lang)
    cp = contrast_pixels(page)
    P(f'  контраст текста (пиксели): мин {cp[0][0]:.2f} ({cp[0][1]!r}, {cp[0][2]}, {cp[0][3]}); ниже 4.5: {sum(1 for c in cp if c[0] < 4.5)} из {len(cp)}')
    for c in cp[:4]: P(f'    худшие: {c[0]:.2f} {c[1]!r} {c[2]} {c[3]}')
    RES['lowc'] = sum(1 for c in cp if c[0] < 4.5)
    tg = page.evaluate(TARGET_JS); P(f'  кнопки ниже 44 px по высоте: {len(tg)} {tg[:3]}')
    txt = page.evaluate("document.body.innerText"); hits = re.findall(r'@[a-z]|\+\d{2}[ \d]*\d{3}|\b\d{3}[ -]\d{3}[ -]\d{3}\b', txt)
    P(f'  открытые контакты в тексте: {hits}')
    # ---- 2. порядок сигналов
    sg = page.evaluate(SIG_JS)
    RK = {'over': 0, 'soon': 1, 'info': 2}
    days = {'consent': 6, 'overlap': 3, 'empty': 5, 'quality': 7}
    exp = sorted(sg, key=lambda s: RK[s['st']] * 100 + (-days[s['id']] if s['st'] == 'over' else days[s['id']]))
    P(f"  [порядок сигналов] на странице: {[(s['id'], s['badge'], s['meta'].split(' · ')[-1]) for s in sg]}")
    P(f"  [порядок сигналов] ожидаемый по риску (Прострочено → Скоро по сроку → Инфо): {[s['id'] for s in exp]} -> {'СОВПАДАЕТ' if [s['id'] for s in sg] == [s['id'] for s in exp] else 'НЕ СОВПАДАЕТ'}")
    RES['order'] = [s['id'] for s in sg] == [s['id'] for s in exp]
    words = all(re.search(r'(через|in) \d+ |\d+ (дн|d) |(звернення|complaints)', s['meta'] + ' ') for s in sg) and not any(re.fullmatch(r'\d+\s*(дн|d)', s['badge']) for s in sg)
    P(f"  [бейдж=статус, срок словами] бейджи {[s['badge'] for s in sg]}; срок словами в мета у всех: {words}")
    # ---- 3. каждый сигнал подсвечивает свою ячейку
    SL = {'overlap': (3, 17), 'empty': (5, 10), 'consent': (1, 16), 'quality': (2, 18)}
    for sid in ['consent', 'overlap', 'empty', 'quality']:
        if page.get_attribute(f'[data-sig={sid}]', 'aria-expanded') != 'true': page.click(f'[data-sig={sid}]')
        elif sid == 'consent': page.click('[data-sig=consent]'); page.wait_for_timeout(150); page.click('[data-sig=consent]')
        page.wait_for_timeout(250); st = page.evaluate(STATE_JS)
        okk = st['sigon'] == list(SL[sid]) and st['sel'] == list(SL[sid])
        extra = ''
        if ph:
            ok2, _ = selected_first_screen(page, f'сигнал {sid}') if False else (None, None)
            extra = f" (ячейка y {st['top']}..{st['bottom']} в окне {st['vh']}, окно часов {st['hours']})"
        P(f"  [раскрыт «{sid}»] подсвечена {st['sigon']}, выбрана {st['sel']}, ожидается {SL[sid]} -> {'OK' if okk else 'ПЛОХО'}{extra}")
        RES.setdefault('sigcell', []).append(okk)
        if sid == 'consent':
            if ph:
                page.evaluate("document.querySelector('[data-sigid=consent]').scrollIntoView({block:'start'}); window.scrollBy(0, -(document.getElementById('bar').offsetHeight + 8))")
                page.wait_for_timeout(300)
            shot(page, pre + '2-sig-consent'); overlap(page, 'consent-open')
            bw = page.evaluate("(() => { const b = document.querySelector('[data-act=\"consent:remind\"]'); const r = b.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), b.innerText]; })()")
            P(f"  [кнопка действия] «{bw[2]}» {bw[0]}×{bw[1]} px -> {'~300 OK' if 280 <= bw[0] <= 330 else 'ВНЕ 280–330'}; ширина окна {w}"); RES['btnw'] = bw[0]
            if ph:
                bb = page.evaluate("(() => { const b = document.querySelector('[data-act=\"consent:remind\"]').getBoundingClientRect(), f = document.querySelector('.fam').getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom), Math.round(f.top), innerHeight]; })()")
                P(f"  [кнопка над списком семей] кнопка y {bb[0]}..{bb[1]}, список с y {bb[2]}, окно {bb[3]} -> {'ВИДНА И ВЫШЕ СПИСКА' if bb[1] <= bb[2] and bb[1] <= bb[3] else 'ПЛОХО'}"); RES['btnabove'] = bb[1] <= bb[2] and bb[1] <= bb[3]
            cr2 = page.evaluate(CREAM_JS); P(f"  [кремовая заливка, сигнал раскрыт] допустимые {cr2['ok']}; прочие {len(cr2['bad'])} {cr2['bad'][:3]}"); RES['cream_bad'] += len(cr2['bad'])
            if ph:
                page.evaluate('window.scrollTo(0,0)'); page.wait_for_timeout(250); shot(page, pre + '2-sig-consent-top')
                RES['sel_consent'] = selected_first_screen(page, 'сигнал consent, верх страницы')[0]
    # конфликт: только точка (ячейка не выделена контуром, пока не выбрана)
    page.click('[data-sig=overlap]') if page.get_attribute('[data-sig=overlap]', 'aria-expanded') == 'true' else None
    page.evaluate('window.scrollTo(0,0)')
    if ph: page.click('.dchip[data-day="3"]'); page.wait_for_timeout(200)
    page.click('.cell[data-d="3"][data-h="16"]'); page.wait_for_timeout(200)
    cf = page.evaluate("(() => { const c = document.querySelector('.cell[data-d=\"3\"][data-h=\"17\"]'); const cs = getComputedStyle(c); return {shadow: cs.boxShadow, bg: cs.backgroundColor, dot: !!c.querySelector('.mk.overlap'), on: c.classList.contains('on'), sigon: c.classList.contains('sigon')}; })()")
    P(f"  [конфликт без выбора] точка есть: {cf['dot']}, обводка/тень: {cf['shadow']}, выбрана: {cf['on']}, подсветка сигнала: {cf['sigon']} (сигнал overlap закрыт) -> {'ТОЛЬКО ТОЧКА' if cf['dot'] and cf['shadow'] == 'none' and not cf['on'] else 'ПЛОХО'}"); RES['dotonly'] = cf['dot'] and cf['shadow'] == 'none'
    ok, st = selected_first_screen(page, 'обычная ячейка Чт 16'); RES['selvis2'] = ok
    on_bg = page.evaluate("getComputedStyle(document.querySelector('.cell.on')).backgroundColor"); exp_bg = page.evaluate("document.querySelector('.cell.on').style.backgroundColor"); P(f'  [выбранная ячейка = цвет своего процента, не крем] фон {on_bg}, ожидаемый по шкале {exp_bg} -> {"OK" if on_bg == exp_bg and on_bg != "rgb(251, 239, 223)" else "ПЛОХО"}'); RES['selfill'] = on_bg == exp_bg and on_bg != 'rgb(251, 239, 223)'
    ring = page.evaluate("getComputedStyle(document.querySelector('.cell.on')).boxShadow"); P(f'  [контур выбора] box-shadow: {ring}'); RES['ring'] = '3px' in ring
    rd_ = page.evaluate("(() => { const v = document.querySelector('.rd-v'), k = document.querySelector('.ribbon .fig b'); return [getComputedStyle(v).fontSize, getComputedStyle(k).fontSize, getComputedStyle(v).color]; })()")
    P(f'  [значение выбора] размер {rd_[0]} vs KPI {rd_[1]}, цвет {rd_[2]} -> {"герой: >= KPI+4" if ph and float(rd_[0][:-2]) >= float(rd_[1][:-2]) + 4 else ("не крупнее KPI" if not ph and float(rd_[0][:-2]) <= float(rd_[1][:-2]) else "ПЛОХО")}'); RES['rdsize'] = (float(rd_[0][:-2]) >= float(rd_[1][:-2]) + 4) if ph else (float(rd_[0][:-2]) <= float(rd_[1][:-2]))
    page.click('[data-sig=consent]') if False else None
    shot(page, pre + '3-cell-plain'); overlap(page, 'cell-plain'); o = orange(page, 'обычная ячейка', 3); RES['orange'].append(o)
    pct_check(page, 'ячейка Чт 16', lang)
    if ph:
        # окно по часам
        page.evaluate('window.scrollTo(0,0)'); page.click('[data-win="-1"]'); page.wait_for_timeout(200); st = page.evaluate(STATE_JS); P(f"  [окно «Раніше»] часы {st['hours']}, строк {st['rows']}"); shot(page, pre + '6-window-earlier')
        for _ in range(3): page.click('[data-win="-1"]') if page.is_enabled('[data-win="-1"]') else None
        dis = not page.is_enabled('[data-win="-1"]'); st = page.evaluate(STATE_JS); P(f"  [окно у верхней границы] часы {st['hours']}; «Раніше» отключена: {dis}")
        page.click('.dchip[data-day="2"]'); page.wait_for_timeout(200); st = page.evaluate(STATE_JS); P(f"  [чип дня Ср → окно по выбранному часу] выбрана {st['sel']}, часы {st['hours']}, строка №{st['rowIdx'] + 1} из {st['rows']}")
        RES['recenter'] = st['rows'] == 7 and abs(st['rowIdx'] - 3) <= 3
        page.focus('.cell.on'); h0 = page.evaluate("+document.querySelector('.cell.on').dataset.h")
        for _ in range(5): page.keyboard.press('ArrowDown')
        st = page.evaluate(STATE_JS); P(f"  [клавиатура ↓×5 из {h0}:00] выбрана {st['sel']}, окно {st['hours']}, ячейка в DOM: {st['sel'] is not None}")
        RES['kb'] = st['sel'] is not None and st['nOn'] == 1
        day0 = page.evaluate("document.querySelector('.cell.on').dataset.d")
        P(f"  [клавиатура: ось] ↓×5 меняет час, день остался {day0} (ожидался 2 = Ср) -> {'OK' if day0 == '2' else 'ПЛОХО'}"); RES['kbaxis'] = day0 == '2'
        page.keyboard.press('ArrowRight'); st = page.evaluate(STATE_JS); P(f"  [клавиатура →] выбрана {st['sel']} (день +1)"); page.keyboard.press('ArrowLeft')
        # липкие заголовки дней
        page.evaluate("window.scrollTo(0, document.querySelector('.hgrid').getBoundingClientRect().top + scrollY + 120)"); page.wait_for_timeout(300)
        sk = page.evaluate("(() => { const c = document.querySelector('.hgrid .dchip').getBoundingClientRect(), b = document.getElementById('bar').getBoundingClientRect(), g = document.querySelector('.hgrid').getBoundingClientRect(); return [Math.round(c.top), Math.round(b.bottom), Math.round(g.top), scrollY]; })()")
        ch = page.evaluate("""[...document.querySelectorAll('.hgrid .dchip')].map(c => { const s = getComputedStyle(c); return {t: c.textContent, pr: c.getAttribute('aria-pressed') === 'true', on: c.classList.contains('on'), ring: /inset/.test(s.boxShadow) || s.outlineStyle !== 'none' || s.borderColor === 'rgb(251, 239, 223)' && c.getAttribute('aria-pressed') === 'true', fv: c.matches(':focus-visible')}; })""")
        selday = page.evaluate("+document.querySelector('.cell.on').dataset.d")
        rings = [i for i, c in enumerate(ch) if c['ring']]
        P(f"  [контур на чипах дней] чипы с контуром: {[ch[i]['t'] for i in rings]}; выбран день №{selday} ({ch[selday]['t']}); устаревших .on: {[c['t'] for c in ch if c['on'] != c['pr']]}; фокус-контур: {[c['t'] for c in ch if c['fv']]} -> {'ТОЛЬКО ВЫБРАННЫЙ' if rings == [selday] else 'ПЛОХО'}"); RES['chipring'] = rings == [selday]
        P(f'  [липкие заголовки дней] после прокрутки на {sk[3]}px: верх чипа {sk[0]}, низ шапки {sk[1]}, верх сетки {sk[2]} -> {"ЛИПНУТ" if abs(sk[0] - sk[1]) <= 2 and sk[2] < sk[1] else "НЕ ЛИПНУТ"}'); RES['sticky'] = abs(sk[0] - sk[1]) <= 2 and sk[2] < sk[1]
        shot(page, pre + '5-sticky-days')
        page.evaluate('window.scrollTo(0,0)')
        # меню
        page.click('#menuBtn'); page.wait_for_timeout(250); shot(page, pre + '2-menu')
        mv = page.evaluate("(() => { const r = document.getElementById('tools').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.bottom), document.getElementById('menuBtn').getAttribute('aria-expanded')]; })()"); P(f'  [меню] панель {mv[0]}..{mv[1]} x, y {mv[2]}..{mv[3]}, aria-expanded={mv[4]}; внутри окна: {mv[1] <= w and mv[0] >= 0}')
        page.evaluate("document.getElementById('bar').style.visibility = 'hidden'; document.getElementById('main').style.visibility = 'hidden'"); overlap(page, 'menu-open (само меню + шапка; контент под всплывающим меню скрыт — оно его перекрывает по замыслу)'); page.evaluate("document.getElementById('bar').style.visibility = ''; document.getElementById('main').style.visibility = ''"); RES['menu_in'] = mv[1] <= w and mv[0] >= 0
        page.click('[data-cur=UAH]'); page.wait_for_timeout(300); closed = not page.evaluate("document.getElementById('tools').classList.contains('open')"); P(f'  [меню → UAH] меню закрылось: {closed}; доход в ленте: {page.inner_text(".ribbon .fig:nth-child(4) b")!r}')
        page.click('#menuBtn'); page.click('[data-cur=PLN]'); page.wait_for_timeout(200)
    # ---- периоды и проценты
    page.evaluate('window.scrollTo(0,0)')
    for per, nm in (('month', 'месяц'), ('quarter', 'квартал')):
        page.click(f'[data-per={per}]'); page.wait_for_timeout(500)
        pct_check(page, nm, lang); o = orange(page, nm, 3); RES['orange'].append(o)
        selected_first_screen(page, nm) if ph else None
        if per == 'quarter': shot(page, pre + '4-quarter'); sw('quarter')
    page.click('[data-per=quarter]')
    if not ph:
        page.click('[data-cur=UAH]'); page.wait_for_timeout(400); shot(page, pre + '4-quarter-uah'); overlap(page, 'quarter-uah'); pct_check(page, 'квартал UAH', lang)
        page.click('[data-cur=PLN]')
    else:
        page.click('#menuBtn'); page.click('[data-cur=UAH]'); page.wait_for_timeout(400); pct_check(page, 'квартал UAH', lang); overlap(page, 'quarter-uah'); shot(page, pre + '4-quarter-uah'); page.click('#menuBtn'); page.click('[data-cur=PLN]')
    page.click('[data-per=week]'); page.wait_for_timeout(300)
    # ---- действие, сортировка после выполнения
    page.evaluate('window.scrollTo(0,0)'); page.click('[data-sig=consent]') if page.get_attribute('[data-sig=consent]', 'aria-expanded') != 'true' else None
    page.click('[data-act="consent:remind"]'); page.wait_for_timeout(400)
    sg2 = page.evaluate(SIG_JS); P(f"  [после действия] порядок {[(s['id'], s['badge']) for s in sg2]}; счётчик: {page.inner_text('.badge')!r}; первая запись журнала: {page.inner_text('.jrow:first-child')[:60]!r}")
    RES['doneLast'] = sg2[-1]['id'] == 'consent' and sg2[-1]['done']
    P(f"  [сделанный сигнал уходит вниз] {RES['doneLast']}")
    # ---- язык
    page.evaluate('window.scrollTo(0,0)'); h_a = page.evaluate('document.documentElement.scrollHeight')
    if ph: page.click('#menuBtn')
    page.click('[data-lang=en]' if lang == 'uk' else '[data-lang=uk]'); page.wait_for_timeout(400); h_b = page.evaluate('document.documentElement.scrollHeight')
    P(f'  [смена языка] высота {h_a} → {h_b}; scrollWidth {page.evaluate("document.documentElement.scrollWidth")} vs {w}')
    sw('final')
    cls = page.evaluate('window.__cls'); P(f'  CLS за сценарий: {cls:.4f}')
    P(f'  ошибки консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    RES['cls'] = cls; RES['console'] = len(console); RES['ext'] = len(ext)
    br.close()
    return RES

ALL = {}
with sync_playwright() as pw:
    for dev in ('desktop', 'phone'):
        for lang in ('uk', 'en'):
            ALL[(dev, lang)] = run(pw, dev, lang)

P(f"== ИТОГ пересечений: проверок {OVR['checks']}, текстов {OVR['texts']}, пересечений {OVR['bad']}, выходов за ячейку {OVR['spill']} ==")
P(f"== ИТОГ округления процентов: проверок {PCT['checks']}, расхождений {len(PCT['bad'])} {PCT['bad'][:5]} ==")
P('== СВОДКА по прогонам ==')
for k, r in ALL.items():
    P(f"  {k}: ширина OK {sum(r['sw'])}/{len(r['sw'])}; мин.шрифт {min(r['mf'])}px; обрезов {sum(r['clip'])}; текстов <4.5:1 {r['lowc']}; CLS {r['cls']:.4f}; консоль {r['console']}; внеш.запросы {r['ext']}; оранж. по состояниям {r['orange']}; порядок {r['order']}; сигнал→ячейка {r['sigcell']}; кремовых лишних {r['cream_bad']}; кнопка {r.get('btnw')}px; точка-только {r['dotonly']}; заливка выбранной = цвет её процента (выбор контуром, не заливкой) {r['selfill']}; значение выбора (тел.: герой ≥KPI+4; ноут.: ≤KPI) {r['rdsize']}")
    if k[0] == 'phone': P(f"     телефон: выбранная в первом экране {r['selvis']} / после выбора Чт16 {r['selvis2']} / consent {r.get('sel_consent')}; KPI в одну полосу {r['strip1']}; меню убрало валюту/язык {r['menu_hidden']}; липкие дни {r['sticky']}; окно центрируется {r['recenter']}; клавиатура {r['kb']}; меню в окне {r['menu_in']}")
P('== пары цветов (WCAG) ==')
pairs = [('ink on page bg', '#FBEFDF', '#1E1424', 4.5), ('ink2 on page bg', '#D6C3CE', '#1E1424', 4.5), ('ink2 on panel', '#D6C3CE', '#2A1A31', 4.5), ('ink on panel2 (выбранное)', '#FBEFDF', '#35223C', 4.5), ('текст кнопки на креме', '#2A1A2E', '#FBEFDF', 4.5), ('текст бейджа «Прострочено» на оранжевом', '#2A1A2E', '#FF7A45', 4.5), ('дельта-падение (оранж) на фоне', '#FF7A45', '#1E1424', 4.5), ('[не текст] точка перетина vs кремовая ячейка (обводка тёмная)', '#1E1424', '#FBEFDF', 3.0), ('[не текст] кремовый контур выбора vs фон страницы (между контуром и ячейкой 1 px тёмного зазора)', '#FBEFDF', '#1E1424', 3.0), ('[не текст] пол шкалы vs фон', '#5A4270', '#1E1424', 1.5)]
bad = 0
for n, a, b, need in pairs:
    c = cr(hx(a), hx(b)); ok = c >= need; bad += (not ok); P(f'  {c:5.2f}:1 {"OK " if ok else "ПЛОХО"} (нужно {need}) {n}')
P(f'  пар ниже порога: {bad}')
open(os.path.join(SHOTS, 'metrics-r13.txt'), 'w').write('\n'.join(out) + '\n')
